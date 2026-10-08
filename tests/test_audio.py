import tempfile, unittest, wave
from pathlib import Path
import numpy as np
from ttschat import audio
from ttschat.errors import AppError
from tests.helpers import FakeEngine


class AudioTests(unittest.TestCase):
    def setUp(self): self.d = Path(tempfile.mkdtemp())

    def test_concat_with_pauses(self):
        a = np.ones(1000, dtype=np.int16); b = np.ones(500, dtype=np.int16)
        out = audio.concat([a, b], [0.5], 1000)
        self.assertEqual(len(out), 1000 + 500 + 500)
        self.assertTrue((out[1000:1500] == 0).all())

    def test_write_and_validate_wav(self):
        p = self.d / "a.wav"
        audio.write_wav(p, np.zeros(24000, dtype=np.float32) + 0.1, 24000)
        self.assertAlmostEqual(audio.validate_wav(p), 1.0, 2)
        with wave.open(str(p)) as w: self.assertEqual((w.getnchannels(), w.getframerate()), (1, 24000))

    def test_corrupt_wav(self):
        p = self.d / "bad.wav"; p.write_bytes(b"not a wav")
        with self.assertRaises(AppError) as c: audio.validate_wav(p)
        self.assertEqual(c.exception.code, "AUDIO_CORRUPT")

    def test_float_clipping(self):
        self.assertEqual(audio.to_int16(np.array([2.0, -2.0], dtype=np.float32)).tolist(), [32767, -32767])

    @unittest.skipUnless(audio.ffmpeg_path(), "FFmpeg no instalado")
    def test_mp3_ogg(self):
        p = self.d / "a.wav"; audio.write_wav(p, np.sin(np.arange(24000) / 10).astype(np.float32), 24000)
        for fmt, magic in (("mp3", None), ("ogg", b"OggS")):
            out = audio.convert(p, fmt)
            self.assertGreater(out.stat().st_size, 100)
            if magic: self.assertEqual(out.read_bytes()[:4], magic)

    def test_unknown_format(self):
        with self.assertRaises(AppError): audio.convert(self.d / "x.wav", "flac")

    def test_ffmpeg_missing(self):
        p = self.d / "a.wav"; audio.write_wav(p, np.zeros(100, dtype=np.float32), 24000)
        orig = audio.ffmpeg_path; audio.ffmpeg_path = lambda: None
        try:
            with self.assertRaises(AppError) as c: audio.convert(p, "mp3")
            self.assertEqual(c.exception.code, "FFMPEG_MISSING")
        finally: audio.ffmpeg_path = orig
