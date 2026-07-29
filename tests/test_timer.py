import time
import unittest
from src.services.timer_service import TimerService


class TestTimerService(unittest.TestCase):

    def setUp(self):
        self.completed = False
        self.timer = TimerService(on_complete=self._on_complete)

    def _on_complete(self):
        self.completed = True

    def test_duration_setting(self):
        dur = self.timer.set_duration(0, 1, 30)
        self.assertEqual(dur, 90)
        self.assertEqual(self.timer.get_remaining_sec(), 90)

    def test_start_countdown(self):
        self.timer.set_duration(0, 0, 2)
        started = self.timer.start()
        self.assertTrue(started)
        self.assertTrue(self.timer.is_running)

        time.sleep(1.1)
        rem = self.timer.get_remaining_sec()
        self.assertLessEqual(rem, 1)

    def test_pause_reset(self):
        self.timer.set_duration(0, 0, 10)
        self.timer.start()
        time.sleep(0.05)
        self.timer.pause()
        self.assertFalse(self.timer.is_running)

        rem = self.timer.get_remaining_sec()
        self.assertGreater(rem, 0)

        self.timer.reset()
        self.assertEqual(self.timer.get_remaining_sec(), 0)


if __name__ == "__main__":
    unittest.main()
