import unittest
from ttschat.hardware import make_plan, detect
from ttschat.errors import friendly
from tests.helpers import HW_CPU, HW_GPU, HW_LOW


class HardwareTests(unittest.TestCase):
    def test_detect_runs(self):
        hw = detect(); self.assertGreaterEqual(hw.cpu_cores, 1)

    def test_auto_gpu(self):
        p = make_plan(HW_GPU); self.assertEqual((p.device, p.profile, p.providers[0]), ("gpu", "high", "CUDAExecutionProvider"))
        self.assertEqual(p.providers[-1], "CPUExecutionProvider")

    def test_auto_cpu_medium_and_low(self):
        self.assertEqual(make_plan(HW_CPU).profile, "medium")
        low = make_plan(HW_LOW); self.assertEqual((low.profile, low.device), ("low", "cpu")); self.assertTrue(low.warnings)

    def test_force_cpu_on_gpu_machine(self):
        self.assertEqual(make_plan(HW_GPU, "cpu").device, "cpu")

    def test_force_gpu_without_gpu_falls_back(self):
        p = make_plan(HW_CPU, "gpu"); self.assertEqual(p.device, "cpu"); self.assertTrue(p.warnings)

    def test_manual_profile_and_chunk(self):
        self.assertLess(make_plan(HW_CPU, "auto", "low").chunk_chars, make_plan(HW_CPU, "auto", "high").chunk_chars)

    def test_invalid_values_default(self):
        self.assertEqual(make_plan(HW_CPU, "xx", "yy").profile, "medium")

    def test_friendly_errors(self):
        self.assertEqual(friendly(RuntimeError("CUDA out of memory")).code, "GPU_OUT_OF_MEMORY")
        self.assertIn("modo CPU", friendly(RuntimeError("CUDA out of memory")).message)
        self.assertEqual(friendly(MemoryError()).code, "OUT_OF_MEMORY")
        self.assertEqual(friendly(OSError(28, "No space left")).code, "DISK_FULL")
        self.assertEqual(friendly(ValueError("x")).code, "GENERATION_FAILED")
