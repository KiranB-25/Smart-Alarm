import time
import unittest
from src.services.stopwatch_service import StopwatchService


class TestStopwatchService(unittest.TestCase):

    def setUp(self):
        self.stopwatch = StopwatchService()

    def test_start_pause_reset(self):
        self.assertFalse(self.stopwatch.is_running)
        self.assertEqual(self.stopwatch.get_elapsed_ms(), 0.0)

        self.stopwatch.start()
        self.assertTrue(self.stopwatch.is_running)
        time.sleep(0.05)
        self.assertGreater(self.stopwatch.get_elapsed_ms(), 30.0)

        self.stopwatch.pause()
        self.assertFalse(self.stopwatch.is_running)
        elapsed_paused = self.stopwatch.get_elapsed_ms()
        time.sleep(0.02)
        self.assertEqual(self.stopwatch.get_elapsed_ms(), elapsed_paused)

        self.stopwatch.reset()
        self.assertEqual(self.stopwatch.get_elapsed_ms(), 0.0)

    def test_laps(self):
        self.stopwatch.start()
        time.sleep(0.02)
        lap1 = self.stopwatch.lap()
        self.assertGreater(lap1, 0.0)
        self.assertEqual(len(self.stopwatch.laps), 1)

        time.sleep(0.02)
        lap2 = self.stopwatch.lap()
        self.assertGreater(lap2, lap1)
        self.assertEqual(len(self.stopwatch.laps), 2)

    def test_formatting(self):
        # 1h 2m 3s 45cs = (3600 + 120 + 3)*1000 + 450 = 3723450 ms
        h, m, s, cs = self.stopwatch.format_time(3723450.0)
        self.assertEqual(h, 1)
        self.assertEqual(m, 2)
        self.assertEqual(s, 3)
        self.assertEqual(cs, 45)


if __name__ == "__main__":
    unittest.main()
