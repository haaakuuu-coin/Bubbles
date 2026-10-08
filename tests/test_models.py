import hashlib, http.server, tempfile, threading, unittest
from pathlib import Path
from unittest import mock
from ttschat.config import Config, ModelFile
from ttschat.errors import AppError
from ttschat.models import ModelManager
from tests.helpers import tmp_cfg


class Srv:
    def __enter__(self):
        d = tempfile.mkdtemp(); self.dir = Path(d)
        (self.dir / "m.bin").write_bytes(b"x" * 300000)
        handler = lambda *a, **k: http.server.SimpleHTTPRequestHandler(*a, directory=d, **k)
        handler.log_message = lambda *a: None
        self.s = http.server.ThreadingHTTPServer(("127.0.0.1", 0), handler)
        threading.Thread(target=self.s.serve_forever, daemon=True).start()
        self.url = f"http://127.0.0.1:{self.s.server_address[1]}/m.bin"; return self
    def __exit__(self, *a): self.s.shutdown()


class ModelTests(unittest.TestCase):
    def test_download_ok_and_progress(self):
        with Srv() as s:
            mm = ModelManager(tmp_cfg()); calls = []
            mf = ModelFile("m.bin", s.url, hashlib.sha256(b"x" * 300000).hexdigest(), 1)
            mm.download([mf], lambda d, t, m: calls.append(d))
            self.assertEqual(mm.ensure([mf])[0].stat().st_size, 300000); self.assertTrue(calls)

    def test_bad_hash_is_corrupt_and_removed(self):
        with Srv() as s:
            mm = ModelManager(tmp_cfg()); mf = ModelFile("m.bin", s.url, "0" * 64, 1)
            with self.assertRaises(AppError) as c: mm.download([mf])
            self.assertEqual(c.exception.code, "MODEL_CORRUPT"); self.assertFalse(mm.path(mf).exists())

    def test_missing_and_corrupt_existing(self):
        mm = ModelManager(tmp_cfg()); mf = ModelFile("m.bin", "http://x", "a" * 64, 1)
        with self.assertRaises(AppError) as c: mm.ensure([mf])
        self.assertEqual(c.exception.code, "MODEL_MISSING")
        mm.path(mf).write_bytes(b"garbage")
        with self.assertRaises(AppError) as c: mm.ensure([mf])
        self.assertEqual(c.exception.code, "MODEL_CORRUPT")
        mm.path(mf).write_bytes(b"")
        with self.assertRaises(AppError) as c: mm.ensure([mf])
        self.assertEqual(c.exception.code, "MODEL_CORRUPT")

    def test_offline(self):
        mm = ModelManager(tmp_cfg()); mf = ModelFile("m.bin", "http://127.0.0.1:1/m.bin", None, 1)
        with self.assertRaises(AppError) as c: mm.download([mf])
        self.assertEqual(c.exception.code, "DOWNLOAD_FAILED")

    def test_disk_full(self):
        mm = ModelManager(tmp_cfg()); mf = ModelFile("m.bin", "http://x", None, 500)
        with mock.patch("ttschat.models.shutil.disk_usage", return_value=mock.Mock(free=1000)):
            with self.assertRaises(AppError) as c: mm.download([mf])
        self.assertEqual(c.exception.code, "DISK_FULL")
