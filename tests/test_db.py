import os
import tempfile
import unittest
from src.models.alarm import Alarm
from src.models.settings import Settings
from src.models.history import AlarmHistory
from src.storage.db import DatabaseManager


class TestDatabaseManager(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db_path = os.path.join(self.temp_dir.name, "test_smart_alarm.db")
        self.db = DatabaseManager(db_path=self.db_path)

    def tearDown(self):
        try:
            self.temp_dir.cleanup()
        except Exception:
            pass

    def test_save_and_get_alarms(self):
        alarm = Alarm(id="test1", hour=6, minute=45, label="Workout", tone="digital-alarm", repeat="weekdays", days=[])
        self.db.save_alarm(alarm)

        alarms = self.db.get_all_alarms()
        self.assertEqual(len(alarms), 1)
        self.assertEqual(alarms[0].id, "test1")
        self.assertEqual(alarms[0].label, "Workout")
        self.assertEqual(alarms[0].hour, 6)
        self.assertEqual(alarms[0].minute, 45)

    def test_delete_alarm(self):
        alarm = Alarm(id="test2", hour=7, minute=0)
        self.db.save_alarm(alarm)
        self.assertEqual(len(self.db.get_all_alarms()), 1)

        self.db.delete_alarm("test2")
        self.assertEqual(len(self.db.get_all_alarms()), 0)

    def test_settings_persistence(self):
        settings = Settings(time_format="24", theme="dark", volume=0.8, snooze_minutes=10)
        self.db.save_settings(settings)

        loaded = self.db.get_settings()
        self.assertEqual(loaded.time_format, "24")
        self.assertEqual(loaded.theme, "dark")
        self.assertEqual(loaded.volume, 0.8)
        self.assertEqual(loaded.snooze_minutes, 10)

    def test_history_persistence(self):
        entry = AlarmHistory(alarm_id="test1", label="Morning", tone="classic-bell", action="triggered")
        self.db.add_history_entry(entry)

        history = self.db.get_alarm_history()
        self.assertEqual(len(history), 1)
        self.assertEqual(history[0].label, "Morning")
        self.assertEqual(history[0].action, "triggered")


if __name__ == "__main__":
    unittest.main()
