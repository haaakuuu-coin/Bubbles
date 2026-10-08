"""Prueba de integración con el modelo REAL. Se omite si Kokoro o sus archivos no están instalados."""
import unittest, os
from pathlib import Path
from ttschat.config import Config, KOKORO_FILES
from ttschat.hardware import detect, make_plan
from ttschat.tts.kokoro_engine import KokoroEngine

HOME = Path(os.environ.get("TTS_CHATBOT_HOME", Path.home() / ".tts-chatbot")) / "models"
READY = KokoroEngine.dependencies_ok()[0] and all((HOME / m.filename).exists() for m in KOKORO_FILES)


@unittest.skipUnless(READY, "Kokoro o sus modelos no están instalados")
class RealKokoro(unittest.TestCase):
    def test_spanish(self):
        e = KokoroEngine(); e.load(HOME, make_plan(detect()))
        voices = e.voices("es"); self.assertTrue(voices)
        s, sr = e.synthesize("Hola, ¿cómo estás? Hoy es un buen día.", voices[0].id, "es", 1.0)
        self.assertEqual(sr, 24000); self.assertGreater(len(s) / sr, 1.0)
        fast, _ = e.synthesize("Hola, ¿cómo estás? Hoy es un buen día.", voices[0].id, "es", 1.5)
        self.assertLess(len(fast), len(s))
