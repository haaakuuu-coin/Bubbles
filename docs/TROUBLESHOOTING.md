# Solución de problemas

## Validar la instalación (5 minutos)
1. `python -m unittest discover -s tests -t .` (todo debe pasar).
2. Descarga el modelo desde la app y vuelve a ejecutar: el test `test_real_engine` ya no se omite.
3. Genera un texto de 20.000 caracteres y mide tiempo y RAM; anótalo.

| Mensaje | Qué hacer |
|---|---|
| «Falta instalar kokoro-onnx» | `pip install -r requirements.txt` en el entorno de la app |
| «Falta el modelo de voz» | Pulsa **Descargar modelo** |
| «archivo dañado o incompleto» | Borra el archivo en `~/.tts-chatbot/models` y descarga de nuevo; si se repite, ver «Descarga y verificación» en `TTS.md` |
| «No se pudo descargar el modelo» | Revisa Internet/proxy; solo hace falta una vez |
| «memoria de la GPU no es suficiente» | Dispositivo: CPU, o perfil Bajo |
| «No hay memoria RAM suficiente» | Cierra programas, perfil Bajo, divide el texto |
| «Para exportar MP3 u OGG hace falta FFmpeg» | Instala FFmpeg (ver INSTALL.md) o descarga WAV |
| «La voz seleccionada no existe» | Elige otra voz; recarga la página |
| «No hay espacio suficiente en el disco» | Libera ~1 GB |
| GPU no se usa | Instala `onnxruntime-gpu`/`-directml` **en lugar de** `onnxruntime` (no ambos) |
| Puerto ocupado | `python run.py --port 8800` |
| Datos | Todo en `~/.tts-chatbot` (o `TTS_CHATBOT_HOME`); bórralo para reiniciar |
