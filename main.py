from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
import subprocess
import os
import sys

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

app = FastAPI()

FIFO_PATH = "/tmp/phonemic.fifo"

def setup_pipewire():
    try:
        res = subprocess.run(["pactl", "list", "sources", "short"], capture_output=True, text=True)
        if "PhoneMic" in res.stdout:
            print("Virtual microphone 'PhoneMic' is already loaded.")
        else:
            print("Loading virtual microphone 'PhoneMic'...")
            subprocess.run([
                "pactl", "load-module", "module-pipe-source",
                "source_name=PhoneMic",
                f"file={FIFO_PATH}",
                "format=s16le",
                "rate=48000",
                "channels=1"
            ], check=True)
    except Exception as e:
        print(f"Failed to setup virtual microphone: {e}")

import socket

def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(('10.255.255.255', 1))
        IP = s.getsockname()[0]
    except Exception:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP

@app.on_event("startup")
async def startup_event():
    setup_pipewire()
    ip = get_local_ip()
    print("\n" + "="*60)
    print("SERVER STARTED AND READY")
    print("To connect from your device, open browser and enter:")
    print(f"https://{ip}:8000")
    print("="*60 + "\n")

# Ensure the static directory exists before mounting
static_path = resource_path("static")
if not os.path.exists(static_path):
    os.makedirs(static_path, exist_ok=True)

app.mount("/static", StaticFiles(directory=static_path), name="static")

@app.get("/")
async def get():
    with open(os.path.join(static_path, "index.html"), "r") as f:
        return HTMLResponse(f.read())

@app.websocket("/ws/audio")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    print("Client connected!")
    
    # Open the FIFO pipe for writing
    try:
        # Use O_NONBLOCK so it doesn't block if PipeWire isn't reading at the exact moment
        fifo_fd = os.open(FIFO_PATH, os.O_WRONLY | os.O_NONBLOCK)
    except OSError as e:
        print(f"Could not open FIFO: {e}")
        await websocket.close()
        return

    try:
        while True:
            # Receive binary data (Int16 PCM from browser)
            data = await websocket.receive_bytes()
            try:
                os.write(fifo_fd, data)
            except BlockingIOError:
                # If pipe is full, drop the frame to avoid latency buildup
                pass
    except WebSocketDisconnect:
        print("Client disconnected!")
    except Exception as e:
        print(f"WebSocket error: {e}")
    finally:
        try:
            os.close(fifo_fd)
        except:
            pass
