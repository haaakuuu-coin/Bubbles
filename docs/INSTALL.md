# Instalación

## Windows
1. Instala Python 3.11 desde python.org (marca «Add to PATH»).
2. (Opcional, MP3/OGG) Instala FFmpeg: `winget install Gyan.FFmpeg`.
3. Doble clic en `start.bat`. La primera vez crea el entorno e instala dependencias.
4. En el navegador pulsa **Descargar modelo**.
5. GPU opcional: `.venv\Scripts\pip uninstall onnxruntime -y` y `pip install onnxruntime-directml` (cualquier GPU DX12) o `onnxruntime-gpu` (NVIDIA + CUDA/cuDNN compatibles).

## Linux
`sudo apt install python3-venv ffmpeg espeak-ng` (espeak-ng solo si kokoro-onnx no lo trae) y luego `./start.sh`.
GPU NVIDIA: `.venv/bin/pip uninstall onnxruntime -y && .venv/bin/pip install onnxruntime-gpu`.

## macOS
`brew install ffmpeg`, luego `./start.sh`. Se usa CPU (CoreML no se activa automáticamente porque puede no soportar todas las operaciones del modelo).

## Instalador de Windows (.exe)
Ver `packaging/`: PyInstaller + Inno Setup (ambos open source). **No probado**; requiere Windows. Pasos en `packaging/build_windows.bat`.

## Usar sin Internet
Tras descargar el modelo, `start.*` no necesita red. Para copiar a otro PC sin Internet, copia la carpeta `~/.tts-chatbot/models`.
