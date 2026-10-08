import threading, time, unittest, wave, io
from ttschat import audio
from ttschat.errors import AppError
from ttschat.pipeline import synthesize_text
from ttschat.server import create_server
from ttschat.storage import Store
from ttschat.tts.manager import EngineManager
from tests.helpers import FakeEngine, tmp_cfg, HW_CPU, http


class Pipeline(unittest.TestCase):
    def test_20000_chars_single_wav(self):
        cfg = tmp_cfg(); store = Store(cfg); FakeEngine.calls = []; FakeEngine.fail_with = None
        text = ("Una oración de ejemplo para el texto largo. " * 500)[:20000]
        prog = []
        aid = synthesize_text(text, FakeEngine(), "fake", "v1", "es", 1.0, 400, cfg, store, prog.append)
        self.assertGreater(len(FakeEngine.calls), 40)
        self.assertEqual(len(list(cfg.audio_dir.glob("*.wav"))), 1)  # un único archivo final
        dur = audio.validate_wav(cfg.audio_dir / f"{aid}.wav")
        self.assertGreater(dur, 100)
        self.assertEqual(prog[-1].done, prog[-1].total)
        self.assertEqual(store.list()[0]["id"], aid)

    def test_cancel(self):
        cfg = tmp_cfg(); ev = threading.Event(); ev.set()
        with self.assertRaises(AppError) as c:
            synthesize_text("Hola. " * 50, FakeEngine(), "fake", "v1", "es", 1.0, 20, cfg, Store(cfg), cancel=ev)
        self.assertEqual(c.exception.code, "CANCELLED")

    def test_generation_error_is_friendly(self):
        cfg = tmp_cfg(); FakeEngine.fail_with = RuntimeError("CUDA out of memory")
        try:
            with self.assertRaises(AppError) as c:
                synthesize_text("Hola mundo.", FakeEngine(), "fake", "v1", "es", 1.0, 100, cfg, Store(cfg))
            self.assertEqual(c.exception.code, "GPU_OUT_OF_MEMORY")
        finally: FakeEngine.fail_with = None

    def test_too_long_not_generated(self):
        cfg = tmp_cfg()
        with self.assertRaises(AppError) as c:
            synthesize_text("a" * 20001, FakeEngine(), "fake", "v1", "es", 1.0, 400, cfg, Store(cfg))
        self.assertEqual(c.exception.code, "TEXT_TOO_LONG")
        self.assertEqual(list(cfg.audio_dir.glob("*")), [])


class ServerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        FakeEngine.fail_with = None
        cls.srv = create_server(tmp_cfg(), HW_CPU, {"fake": FakeEngine})
        cls.port = cls.srv.server_address[1]
        threading.Thread(target=cls.srv.serve_forever, daemon=True).start()

    @classmethod
    def tearDownClass(cls): cls.srv.shutdown()

    def wait(self, job):
        for _ in range(200):
            s, j, _ = http(self.port, "GET", f"/api/jobs/{job}")
            if j["status"] in ("done", "error", "cancelled"): return j
            time.sleep(0.05)
        self.fail("timeout")

    def gen(self, **kw):
        body = {"text": "Hola mundo. Esto es una prueba.", "engine": "fake", "voice": "v1", "language": "es", "speed": 1.0, **kw}
        return http(self.port, "POST", "/api/generate", body)

    def test_index_and_status(self):
        s, raw, h = http(self.port, "GET", "/"); self.assertEqual(s, 200); self.assertIn(b"TTS Chatbot", raw)
        self.assertIn("default-src 'self'", h["Content-Security-Policy"])
        s, st, _ = http(self.port, "GET", "/api/status")
        self.assertEqual(st["max_chars"], 20000); self.assertEqual(st["plan"]["device"], "cpu")
        self.assertIn("wav", st["formats"])

    def test_full_flow_wav_mp3_range_history(self):
        s, r, _ = self.gen(); self.assertEqual(s, 202)
        j = self.wait(r["job"]); self.assertEqual(j["status"], "done", j)
        aid = j["result"]
        s, wav, h = http(self.port, "GET", f"/api/audio/{aid}.wav"); self.assertEqual((s, wav[:4]), (200, b"RIFF"))
        s, part, h = http(self.port, "GET", f"/api/audio/{aid}.wav", headers={"Range": "bytes=0-99"})
        self.assertEqual((s, len(part)), (206, 100)); self.assertIn("bytes 0-99/", h["Content-Range"])
        if audio.ffmpeg_path():
            s, mp3, _ = http(self.port, "GET", f"/api/audio/{aid}.mp3?download=1"); self.assertEqual(s, 200); self.assertGreater(len(mp3), 100)
        s, hist, _ = http(self.port, "GET", "/api/history"); self.assertEqual(hist["items"][0]["id"], aid)
        s, _, _ = http(self.port, "DELETE", f"/api/history/{aid}")
        s, hist, _ = http(self.port, "GET", "/api/history"); self.assertFalse([i for i in hist["items"] if i["id"] == aid])
        s, _, _ = http(self.port, "GET", f"/api/audio/{aid}.wav"); self.assertEqual(s, 404)

    def test_limits_over_http(self):
        s, e, _ = self.gen(text="a" * 20001); self.assertEqual((s, e["error"]["code"]), (400, "TEXT_TOO_LONG"))
        s, e, _ = self.gen(text="  "); self.assertEqual(e["error"]["code"], "EMPTY_TEXT")
        s, r, _ = self.gen(text="a" * 20000); self.assertEqual(s, 202); self.wait(r["job"])

    def test_bad_voice_and_speed(self):
        s, r, _ = self.gen(voice="nope"); j = self.wait(r["job"]); self.assertEqual(j["error"]["code"], "VOICE_NOT_FOUND")
        s, e, _ = self.gen(speed=9); self.assertEqual(e["error"]["code"], "BAD_SPEED")

    def test_security_guards(self):
        s, _, _ = http(self.port, "GET", "/api/status", headers={"Host": "evil.com"}); self.assertEqual(s, 403)
        s, _, _ = http(self.port, "POST", "/api/chat", {}, headers={"Origin": "http://evil.com"}); self.assertEqual(s, 403)
        s, _, _ = http(self.port, "GET", "/../config.py"); self.assertEqual(s, 404)

    def test_chat_echo_and_errors(self):
        s, r, _ = http(self.port, "POST", "/api/chat", {"provider": "echo", "messages": [{"role": "user", "content": "hola"}]})
        self.assertEqual(r["reply"], "Dijiste: hola")
        s, e, _ = http(self.port, "POST", "/api/chat", {"provider": "openai", "messages": [{"role": "user", "content": "x"}]})
        self.assertEqual(e["error"]["code"], "LLM_NO_KEY")

    def test_voices_endpoint(self):
        s, v, _ = http(self.port, "GET", "/api/voices?engine=fake&language=es"); self.assertEqual(v["voices"][0]["id"], "v1")


if __name__ == "__main__":
    unittest.main()
