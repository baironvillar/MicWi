let audioContext;
let workletNode;
let mediaStream;
let socket;
let isConnected = false;
let analyzer;
let animationFrameId;

const connectBtn = document.getElementById('connect-btn');
const statusText = document.getElementById('status-text');
const statusIndicator = document.getElementById('status-indicator');
const volumeMeter = document.getElementById('volume-meter');
const volumeBar = document.getElementById('volume-bar');
const volumeControl = document.getElementById('volume-control');
const gainSlider = document.getElementById('gain-slider');
const gainValueDisplay = document.getElementById('gain-value');

let micGainNode;

gainSlider.addEventListener('input', (e) => {
    const value = e.target.value;
    gainValueDisplay.innerText = `${value}%`;
    if (micGainNode) {
        micGainNode.gain.value = value / 100;
    }
});

connectBtn.addEventListener('click', toggleConnection);

async function toggleConnection() {
    if (isConnected) {
        stopMicrophone();
    } else {
        await startMicrophone();
    }
}

async function startMicrophone() {
    try {
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const wsUrl = `${protocol}//${window.location.host}/ws/audio`;
        
        statusText.innerText = "Conectando al servidor...";
        socket = new WebSocket(wsUrl);
        socket.binaryType = 'arraybuffer';

        socket.onopen = async () => {
            statusText.innerText = "Solicitando permisos...";
            try {
                mediaStream = await navigator.mediaDevices.getUserMedia({
                    audio: {
                        echoCancellation: false,
                        noiseSuppression: false,
                        autoGainControl: false,
                        channelCount: 1,
                        sampleRate: 48000
                    }
                });

                audioContext = new (window.AudioContext || window.webkitAudioContext)({ sampleRate: 48000 });
                await audioContext.audioWorklet.addModule('/static/processor.js');

                const source = audioContext.createMediaStreamSource(mediaStream);
                
                micGainNode = audioContext.createGain();
                micGainNode.gain.value = gainSlider.value / 100;
                
                workletNode = new AudioWorkletNode(audioContext, 'mic-processor');

                analyzer = audioContext.createAnalyser();
                analyzer.fftSize = 256;
                
                source.connect(micGainNode);
                micGainNode.connect(analyzer);

                workletNode.port.onmessage = (e) => {
                    if (socket.readyState === WebSocket.OPEN) {
                        socket.send(e.data);
                    }
                };

                micGainNode.connect(workletNode);
                
                const gainNode = audioContext.createGain();
                gainNode.gain.value = 0;
                workletNode.connect(gainNode);
                gainNode.connect(audioContext.destination);

                updateUIConnected();
                updateVolume();

            } catch (err) {
                console.error("Error al acceder al micrófono:", err);
                statusText.innerText = "Error: Permiso denegado";
                socket.close();
            }
        };

        socket.onclose = () => {
            if (isConnected) stopMicrophone();
        };

        socket.onerror = (err) => {
            console.error("WebSocket error:", err);
            statusText.innerText = "Error de conexión";
            if (isConnected) stopMicrophone();
        };

    } catch (err) {
        console.error("Error general:", err);
        statusText.innerText = "Error al conectar";
    }
}

function stopMicrophone() {
    if (mediaStream) {
        mediaStream.getTracks().forEach(track => track.stop());
    }
    if (audioContext) {
        audioContext.close();
    }
    if (socket && socket.readyState === WebSocket.OPEN) {
        socket.close();
    }
    if (animationFrameId) {
        cancelAnimationFrame(animationFrameId);
    }
    updateUIDisconnected();
}

function updateUIConnected() {
    isConnected = true;
    connectBtn.innerText = "Desconectar Micrófono";
    connectBtn.classList.remove('btn-primary');
    connectBtn.classList.add('btn-danger');
    
    statusText.innerText = "Conectado y transmitiendo";
    statusText.classList.add('connected');
    
    statusIndicator.classList.add('active');
    volumeMeter.classList.add('visible');
    volumeControl.style.opacity = '1';
}

function updateUIDisconnected() {
    isConnected = false;
    connectBtn.innerText = "Conectar Micrófono";
    connectBtn.classList.remove('btn-danger');
    connectBtn.classList.add('btn-primary');
    
    statusText.innerText = "Desconectado";
    statusText.classList.remove('connected');
    
    statusIndicator.classList.remove('active');
    volumeMeter.classList.remove('visible');
    volumeControl.style.opacity = '0';
    volumeBar.style.width = '0%';
}

function updateVolume() {
    if (!isConnected || !analyzer) return;
    
    const dataArray = new Uint8Array(analyzer.frequencyBinCount);
    analyzer.getByteFrequencyData(dataArray);
    
    let sum = 0;
    for (let i = 0; i < dataArray.length; i++) {
        sum += dataArray[i];
    }
    const average = sum / dataArray.length;
    
    const percentage = Math.min(100, Math.max(0, (average / 128) * 100));
    volumeBar.style.width = `${percentage}%`;
    
    animationFrameId = requestAnimationFrame(updateVolume);
}
