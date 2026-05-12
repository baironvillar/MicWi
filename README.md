# MicWi Studio

MicWi Studio es una aplicación para Linux que te permite utilizar tu teléfono móvil (iOS o Android) como un **micrófono inalámbrico para tu computadora** a través de tu red Wi-Fi, con una latencia extremadamente baja y calidad de estudio (48000Hz, 16-bit PCM).

Al utilizar tecnologías web (WebRTC/WebSockets) en el teléfono, **no requiere instalar ninguna aplicación nativa en tu celular**.

![MicWi Screenshot](https://via.placeholder.com/600x400?text=Sube+una+captura+de+pantalla+aqui) <!-- Reemplaza este enlace con una captura real de la app cuando la subas a GitHub -->

## Descarga Directa e Instalación (Recomendado) 🚀

Para instalar la aplicación sin usar la consola, dirígete a la pestaña de **Releases** de este repositorio de GitHub y descarga el instalador correspondiente a tu sistema:

- **Fedora / RHEL / openSUSE:** Descarga el archivo `.rpm` y haz **doble clic** para abrirlo con el instalador gráfico (ej. GNOME Software).
- **Ubuntu / Debian / Mint:** Descarga el archivo `.deb` y haz **doble clic** para instalarlo.

Una vez instalada, simplemente busca **"MicWi Studio"** en tu menú de aplicaciones de Linux y ábrela.

---

## Características 
- **Interfaz Moderna**: Construida con Flet (Flutter) para una experiencia de usuario premium en escritorio.
- **Zero-Install en el Teléfono**: Funciona a través del navegador web del celular (PWA compatible).
- **Control de Volumen Nativo**: Ajusta el volumen del micrófono directamente desde la app en Linux.
- **Integración con el Sistema**: Crea un micrófono virtual (`PhoneMic`) a nivel de sistema usando `pactl` (PulseAudio / PipeWire), seleccionable en Discord, OBS, Zoom, etc.

---

## Prerrequisitos 
Para que la aplicación funcione en tu distribución Linux, necesitas tener instaladas las utilidades de PulseAudio (que también son compatibles con PipeWire).

En distribuciones basadas en Debian/Ubuntu:
```bash
sudo apt update
sudo apt install pulseaudio-utils
```
En Fedora/RHEL:
```bash
sudo dnf install pulseaudio-utils
```
En Arch Linux:
```bash
sudo pacman -S libpulse
```

---

## Instalación desde el código fuente 

1. **Clona el repositorio:**
   ```bash
   git clone https://github.com/TU_USUARIO/micwi.git
   cd micwi
   ```

2. **Crea un entorno virtual y actívalo:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Instala las dependencias:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Genera los certificados SSL (Obligatorio para WebRTC):**
   Debido a las políticas de seguridad de los navegadores, el micrófono solo puede ser accedido bajo `https://`. Debes generar certificados autofirmados ejecutando:
   ```bash
   openssl req -x509 -newkey rsa:4096 -keyout key.pem -out cert.pem -sha256 -days 365 -nodes
   ```

5. **Ejecuta la aplicación:**
   ```bash
   python gui.py
   ```

---

## Compilar como Ejecutable (Standalone)
Si deseas crear un archivo ejecutable para no tener que usar la consola en el futuro, puedes empaquetarlo usando Flet Pack (que internamente usa PyInstaller).

Asegúrate de estar en tu entorno virtual y ejecuta:
```bash
flet pack gui.py --name "MicWi" --add-data "static:static" --add-data "cert.pem:." --add-data "key.pem:."
```
El archivo ejecutable compilado aparecerá en la carpeta `/dist/MicWi`. ¡Puedes moverlo a tu escritorio o a `/usr/local/bin` y ejecutarlo con doble clic!

---

## ¿Cómo usarlo?
1. Abre **MicWi Studio** en tu PC y haz clic en **"Iniciar Transmisión"**.
2. En tu teléfono, asegúrate de estar conectado a la **misma red Wi-Fi** que la PC.
3. Abre el navegador web de tu celular (Safari en iOS, Chrome en Android) e ingresa la URL mostrada en la aplicación (ej. `https://192.168.x.x:8000`).
4. Acepta la advertencia de certificado autofirmado (En Safari: *Mostrar detalles -> Visitar sitio web*).
5. Toca el botón **"Conectar Micrófono"** y concede los permisos.

### Tip: Instalar como PWA (Experiencia Nativa)
Para que actúe exactamente como una aplicación nativa (sin la barra del navegador y con un icono en tu pantalla de inicio):
- **iOS (Safari):** Toca el botón de *Compartir* -> *Agregar a Inicio*.
- **Android (Chrome):** Toca el menú de los 3 puntos -> *Instalar aplicación* o *Agregar a la pantalla principal*.
