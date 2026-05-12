import flet as ft
import threading
import uvicorn
import time
import subprocess

from main import app, get_local_ip, resource_path

def main(page: ft.Page):
    page.title = "MicWi Studio"
    page.window_width = 500
    page.window_height = 700
    page.window_resizable = False
    
    # Diseño vibrante y moderno
    page.theme_mode = ft.ThemeMode.DARK
    page.theme = ft.Theme(
        color_scheme_seed=ft.Colors.BLUE,
        font_family="Inter",
        use_material3=True
    )
    page.padding = 30
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER

    ip_address = get_local_ip()
    server_thread = None
    server_instance = None
    is_running = False

    def change_volume(e):
        volume_pct = int(e.control.value)
        vol_label.value = f"{volume_pct}%"
        page.update()
        try:
            # Usar Popen en lugar de run para no bloquear (elimina el delay)
            subprocess.Popen([
                "pactl", "set-source-volume", "PhoneMic", f"{volume_pct}%"
            ])
        except Exception:
            pass

    def run_uvicorn():
        nonlocal server_instance
        try:
            cert_path = resource_path("cert.pem")
            key_path = resource_path("key.pem")
            config = uvicorn.Config(
                app, host="0.0.0.0", port=8000,
                ssl_certfile=cert_path, ssl_keyfile=key_path, log_level="error"
            )
            server_instance = uvicorn.Server(config)
            server_instance.run()
        except Exception:
            stop_server_logic(error=True)

    def start_server_logic():
        nonlocal is_running, server_thread
        if not is_running:
            is_running = True
            update_ui_state(starting=True)
            server_thread = threading.Thread(target=run_uvicorn, daemon=True)
            server_thread.start()
            update_ui_state(running=True)

    def stop_server_logic(error=False):
        nonlocal is_running, server_instance
        if is_running or error:
            update_ui_state(stopping=True)
            if server_instance:
                server_instance.should_exit = True
                time.sleep(0.5)
            is_running = False
            update_ui_state(running=False, error=error)

    def on_start(e): start_server_logic()
    def on_stop(e): stop_server_logic()

    # Componentes de UI
    
    # Encabezado descriptivo
    header = ft.Column([
        ft.Text("MicWi Studio", size=32, weight=ft.FontWeight.W_900, color=ft.Colors.BLUE_400),
        ft.Text("Wireless Microphone to Computer", size=14, color=ft.Colors.WHITE70),
    ], spacing=5)

    # Estado Central
    status_icon = ft.Icon(ft.Icons.WIFI_OFF, color=ft.Colors.RED_400, size=50)
    status_text = ft.Text("Server Offline", size=20, weight=ft.FontWeight.BOLD, color=ft.Colors.RED_400)
    
    status_container = ft.Container(
        content=ft.Column([status_icon, status_text], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
        padding=25,
        bgcolor=ft.Colors.SURFACE_CONTAINER_HIGH,
        border_radius=20,
        width=float('inf')
    )

    # Controles (Botones Start/Stop)
    start_btn = ft.ElevatedButton(
        "Start Streaming", 
        icon=ft.Icons.PLAY_ARROW,
        on_click=on_start, 
        height=55, 
        style=ft.ButtonStyle(
            bgcolor=ft.Colors.BLUE_600,
            color=ft.Colors.WHITE,
            shape=ft.RoundedRectangleBorder(radius=12)
        ),
        expand=True
    )
    stop_btn = ft.ElevatedButton(
        "Stop", 
        icon=ft.Icons.STOP,
        on_click=on_stop, 
        disabled=True, 
        height=55, 
        style=ft.ButtonStyle(
            bgcolor=ft.Colors.RED_700,
            color=ft.Colors.WHITE,
            shape=ft.RoundedRectangleBorder(radius=12)
        ),
        expand=True
    )

    controls_row = ft.Row([start_btn, stop_btn], spacing=15)

    # Control de Volumen (Hasta 200%)
    vol_label = ft.Text("100%", size=16, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_400)
    volume_slider = ft.Slider(min=0, max=200, divisions=200, value=100, label="{value}%", on_change=change_volume, active_color=ft.Colors.BLUE_400)
    
    volume_section = ft.Column([
        ft.Row([ft.Icon(ft.Icons.MIC), ft.Text("Microphone Volume", size=16, weight=ft.FontWeight.W_600), ft.Container(expand=True), vol_label]),
        volume_slider
    ])

    # Información de Conexión (Oculta por defecto)
    web_url = f"https://{ip_address}:8000"
    ios_url = f"wss://{ip_address}:8000/ws/audio"

    conn_info = ft.Column([
        ft.Text("How to connect:", size=16, weight=ft.FontWeight.BOLD),
        ft.Text("1. Make sure you are on the same Wi-Fi.", size=13, color=ft.Colors.WHITE70),
        ft.Text("2. Use the following links according to your platform:", size=13, color=ft.Colors.WHITE70),
        ft.Container(height=10),
        ft.TextField(label="URL for Web Browser", value=web_url, read_only=True, border_radius=12, prefix_icon=ft.Icons.LANGUAGE),
    ], visible=False)

    def update_ui_state(starting=False, running=False, stopping=False, error=False):
        if starting:
            status_icon.name = ft.Icons.WIFI_FIND
            status_icon.color = ft.Colors.AMBER_500
            status_text.value = "Starting..."
            status_text.color = ft.Colors.AMBER_500
            start_btn.disabled = True
            
        elif running:
            status_icon.name = ft.Icons.WIFI
            status_icon.color = ft.Colors.GREEN_500
            status_text.value = "Streaming"
            status_text.color = ft.Colors.GREEN_500
            stop_btn.disabled = False
            conn_info.visible = True
            
        elif stopping:
            status_icon.name = ft.Icons.WIFI_FIND
            status_icon.color = ft.Colors.AMBER_500
            status_text.value = "Stopping..."
            status_text.color = ft.Colors.AMBER_500
            
        else: # stopped or error
            status_icon.name = ft.Icons.ERROR if error else ft.Icons.WIFI_OFF
            status_icon.color = ft.Colors.RED_500
            status_text.value = "Error to start" if error else "Server Offline"
            status_text.color = ft.Colors.RED_500
            start_btn.disabled = False
            stop_btn.disabled = True
            conn_info.visible = False
            
        page.update()

    # Layout Principal
    page.add(
        header,
        ft.Divider(height=25, color=ft.Colors.TRANSPARENT),
        status_container,
        ft.Divider(height=15, color=ft.Colors.TRANSPARENT),
        controls_row,
        ft.Divider(height=25, color=ft.Colors.TRANSPARENT),
        volume_section,
        ft.Divider(height=15, color=ft.Colors.TRANSPARENT),
        conn_info
    )

if __name__ == "__main__":
    ft.run(main)
