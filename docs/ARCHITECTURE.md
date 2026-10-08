# Arquitectura

```
Navegador (static/) ──HTTP 127.0.0.1──► server.py (App)
                                         ├─ pipeline.py : validar → normalizar → chunker → TTS → audio.concat → WAV
                                         ├─ jobs.py     : cola de 1 trabajo, progreso, ETA, cancelar
                                         ├─ tts/        : base.py (interfaz) · kokoro_engine · chatterbox_engine · manager (carga única)
                                         ├─ hardware.py : detección y plan CPU/GPU/perfil
                                         ├─ models.py   : descarga, SHA-256, corrupción, disco
                                         ├─ audio.py    : WAV, FFmpeg (MP3/OGG)
                                         ├─ storage.py  : historial SQLite + ajustes JSON
                                         └─ llm/        : LLMProvider (echo, Ollama, OpenAI, Anthropic, Gemini)
```
- **Cambiar de motor**: implementar `TTSEngine` (ver `tts/base.py`) y registrarlo en `tts/manager.py`. La UI y el pipeline no cambian; la UI oculta lo que el motor no soporta (`supports_speed`).
- **Sin dependencias web**: servidor con `http.server`; menos piezas que instalar y que auditar. Compromiso: no es un servidor de producción multiusuario.
- **Un trabajo a la vez** (`ThreadPoolExecutor(1)`) para no agotar RAM.
- **Seguridad**: solo 127.0.0.1; se valida `Host` y `Origin` (anti DNS-rebinding/CSRF); CSP sin scripts externos; sin telemetría ni registros del texto del usuario. Las claves de LLM viajan solo en la petición y no se guardan.
- **Privacidad**: la única salida de red es (a) la descarga inicial del modelo y (b) el chat si eliges un proveedor externo.
- **Estructura**: se simplificó la propuesta original (sin carpetas `voices/`, `services/`, `utils/` vacías): las voces viven dentro del archivo del modelo.
