import datetime
import os
import tempfile
import unittest
from src.models.alarm import Alarm
from src.storage.db import DatabaseManager
from src.services.scheduler import AlarmScheduler


class TestAlarmScheduler(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db_path = os.path.join(self.temp_dir.name, "test_scheduler.db")
        self.db = DatabaseManager(db_path=self.db_path)
        self.triggered_list = []
        self.scheduler = AlarmScheduler(
            db=self.db,
            on_trigger=lambda alarm, key: self.triggered_list.append((alarm, key))
        )

    def tearDown(self):
        self.scheduler.stop()
        try:
            self.temp_dir.cleanup()
        except Exception:
            pass

    def test_alarm_triggering_and_duplicate_prevention(self):
        dt = datetime.datetime(2026, 9, 5, 7, 30, 0)
        alarm = Alarm(id="sched1", hour=7, minute=30, repeat="everyday", enabled=True)
        self.db.save_alarm(alarm)

        # First check -> should trigger
        triggered = self.scheduler.check_alarms(dt)
        self.assertEqual(len(triggered), 1)
        self.assertEqual(len(self.triggered_list), 1)

        # Second check at exact same minute -> should NOT trigger duplicate
        triggered_again = self.scheduler.check_alarms(dt)
        self.assertEqual(len(triggered_again), 0)
        self.assertEqual(len(self.triggered_list), 1)

    def test_one_time_alarm_disables_after_trigger(self):
        dt = datetime.datetime(2026, 9, 5, 8, 0, 0)
        alarm = Alarm(id="once1", hour=8, minute=0, repeat="once", enabled=True)
        self.db.save_alarm(alarm)

        self.scheduler.check_alarms(dt)
        
        # Check alarm state in DB
        updated_alarm = self.db.get_all_alarms()[0]
        self.assertFalse(updated_alarm.enabled)


if __name__ == "__main__":
    unittest.main()
