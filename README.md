# TTS Chatbot

Convierte texto en voz **en tu propio equipo**: gratis, sin cuentas, sin API keys y sin enviar tu texto a ningún servidor.

## Características
- Hasta **20.000 caracteres** por audio (límite de la app, con contador en vivo y aviso de cuántos sobran; nunca recorta en silencio).
- Texto largo dividido por párrafos → oraciones → comas → palabras, y unido en **un único archivo**.
- Idioma, voz y velocidad. Los controles que un motor no soporta se ocultan (p. ej. velocidad en Chatterbox).
- Reproducir / pausar / detener / descargar **WAV**, y **MP3/OGG** si hay FFmpeg instalado.
- Progreso real por fragmento («Procesando fragmento 3 de 8») y tiempo restante estimado (se calcula con el ritmo real; no es exacto).
- Rendimiento: Automático / CPU / GPU y perfil Bajo / Medio / Alto / Automático. Si la GPU falla, vuelve a CPU.
- Historial local (SQLite) y pestaña **Chat** con proveedores intercambiables (Ollama local, OpenAI, Anthropic, Gemini). El TTS funciona sin configurar ninguno.
- Español: voces `ef_dora` / `em_alex` de Kokoro (ver límites en `docs/TTS.md`), con normalización de abreviaturas, números, porcentajes y fechas.

## Requisitos
| | Mínimo | Recomendado |
|---|---|---|
| Python | 3.10+ | 3.11–3.12 |
| RAM | 4 GB (perfil Bajo) | 8 GB |
| Disco | ~1 GB | 2 GB |
| GPU | no necesaria | NVIDIA (CUDA) o DirectML en Windows |
Las cifras son estimaciones basadas en el tamaño del modelo (~337 MB); mídelas en tu equipo (ver `docs/TTS.md`).

## Instalación rápida
```
# Linux / macOS            # Windows
./start.sh                 start.bat
```
Se abre `http://127.0.0.1:8765`. La primera vez pulsa **Descargar modelo** (~337 MB, requiere Internet una sola vez). Después funciona sin conexión. Detalles: `docs/INSTALL.md`.

## Uso
1. Pega tu texto. 2. Elige idioma y voz. 3. **Generar audio**. 4. Reproduce o descarga.

## Tests
`python -m unittest discover -s tests -t .`

## Documentación
`docs/INSTALL.md` · `docs/ARCHITECTURE.md` · `docs/TTS.md` · `docs/TROUBLESHOOTING.md`

## Estado honesto de esta entrega
Probado: chunking, límites, unión de audio, WAV/MP3/OGG, detección y plan CPU/GPU, gestor de modelos (descarga local, hash, corrupción, sin red, disco lleno), servidor HTTP completo y seguridad básica, con un motor sintético. **No probado**: síntesis con el modelo Kokoro real, GPU real, adaptador Chatterbox, instalador `.exe`, la interfaz en un navegador, y que la URL/hashes del modelo coincidan con la fuente oficial. Ver `docs/TROUBLESHOOTING.md` para validarlo en 5 minutos.

## Licencia
Código: MIT (ver `LICENSE`). Modelos y dependencias de terceros: ver `THIRD_PARTY_NOTICES.md` y `docs/TTS.md`.
