# Motor TTS

## Elección: Kokoro-82M (ONNX)
- 82 M parámetros, arquitectura StyleTTS 2 + ISTFTNet, 24 kHz, 54 voces en 8 idiomas; pesos **Apache-2.0** (card oficial: https://huggingface.co/hexgrad/Kokoro-82M).
- Archivos ONNX: ~310 MB + ~27 MB de voces. Corre en CPU; sin clonación de voz.
- Código de inferencia `kokoro-onnx` (MIT): https://github.com/thewh1teagle/kokoro-onnx
- Español: voces `ef_dora` y `em_alex` verificadas en conversiones del modelo; el dialecto (rioplatense/mexicano/peninsular) **no está documentado** y no se verificó. Escucha antes de decidir.

## Descartados
| Motor | Motivo |
|---|---|
| XTTS v2 | Licencia CPML no comercial; Coqui cerró; 4–6 GB |
| F5-TTS | Pesos CC-BY-NC-4.0 (código MIT) |
| Piper (activo) | GPL-3.0 (el repo original MIT está archivado desde oct. 2025); calidad variable según voz |
| Qwen3-TTS | Apache-2.0 y con español, pero ~10 GB (1.7B); candidato futuro como adaptador |
| Fish Speech, MeloTTS, OpenVoice, StyleTTS2 | No se revisaron los repositorios oficiales; no se afirma nada sobre ellos |

## Alternativa GPU: Chatterbox Multilingual (MIT)
Adaptador incluido (`tts/chatterbox_engine.py`), **experimental y sin probar**. Existe un finetune LatAm dedicado (ResembleAI/Chatterbox-Multilingual-es-mx-latam) que **no está integrado**: el adaptador usa el modelo multilingüe general.

## Licencias a revisar antes de redistribuir un instalador
(Resumen en `THIRD_PARTY_NOTICES.md`.)
- Kokoro pesos: Apache-2.0 (atribución).
- eSpeak NG (fonemización del español, vía kokoro-onnx/misaki): **GPL-3.0**. Si empaquetas un `.exe` que lo incluye, aplican las obligaciones de la GPL (ofrecer el código fuente). Verifica qué trae `espeakng-loader` en tu versión.
- num2words: LGPL (opcional).
- Para uso personal no hay problema; para distribuir, consulta a un abogado.

## Descarga y verificación
Origen: GitHub Releases de kokoro-onnx (`model-files-v1.0`). Los SHA-256 de `config.py` provienen de una copia pública de los mismos archivos; **no pude contrastarlos con el origen oficial** (sin red). Si da «archivo dañado» con un archivo completo, ejecuta `TTS_CHATBOT_SKIP_HASH=1` y avisa del hash real.

## Optimizaciones aplicadas (y su efecto en calidad)
Carga única del modelo en memoria; fragmentos adaptados al perfil; hilos según perfil; liberación al cambiar de motor. **Sin cuantización** (no se usa la variante int8, para no reducir calidad). Perfil Bajo usa fragmentos más cortos y menos hilos: más lento, misma calidad (puede haber más pausas entre fragmentos).

## Lo que NO hace
Tono (pitch), estilo/emoción y clonación: Kokoro no los soporta, por eso no hay controles. El volumen no se implementó.
