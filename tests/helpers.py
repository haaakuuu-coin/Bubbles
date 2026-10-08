import json, tempfile, threading, urllib.request, urllib.error
import numpy as np
from ttschat.config import Config, ModelFile
from ttschat.hardware import Hardware
from ttschat.tts.base import TTSEngine, Language, Voice, LoadInfo


class FakeEngine(TTSEngine):
    """Motor sintético SOLO para tests: genera un tono proporcional al largo del texto."""
    id, name, supports_speed = "fake", "Fake", True
    calls: list = []
    fail_with: Exception | None = None

    @classmethod
    def dependencies_ok(cls): return True, ""
    def model_files(self): return []
    def languages(self): return [Language("es", "Español")]
    def voices(self, language): return [Voice("v1", "Voz 1")]
    def load(self, model_dir, plan): return LoadInfo(plan.device, [])

    def synthesize(self, text, voice, language, speed):
        if FakeEngine.fail_with:
            raise FakeEngine.fail_with
        if voice != "v1":
            from ttschat.errors import AppError
            raise AppError("VOICE_NOT_FOUND", "La voz seleccionada no existe.", 400)
        FakeEngine.calls.append(text)
        n = int(24000 * 0.01 * len(text) / speed)
        t = np.arange(n) / 24000
        return (0.3 * np.sin(2 * np.pi * 220 * t)).astype(np.float32), 24000


def tmp_cfg(**kw):
    d = tempfile.mkdtemp()
    return Config(home=d, port=0, **kw)


HW_CPU = Hardware("Linux", 8, 16.0, None, None, ["CPUExecutionProvider"])
HW_GPU = Hardware("Linux", 8, 16.0, "RTX", 8.0, ["CUDAExecutionProvider", "CPUExecutionProvider"])
HW_LOW = Hardware("Windows", 2, 3.0, None, None, ["CPUExecutionProvider"])


def http(port, method, path, body=None, headers=None):
    data = json.dumps(body).encode() if body is not None else None
    h = {"Content-Type": "application/json", **(headers or {})}
    req = urllib.request.Request(f"http://127.0.0.1:{port}{path}", data, h, method=method)
    try:
        with urllib.request.urlopen(req) as r:
            raw = r.read()
            return r.status, (json.loads(raw) if r.headers.get_content_type() == "application/json" else raw), r.headers
    except urllib.error.HTTPError as e:
        raw = e.read()
        try:
            return e.code, json.loads(raw), e.headers
        except Exception:
            return e.code, raw, e.headers
