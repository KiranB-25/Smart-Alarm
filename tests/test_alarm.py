import datetime
import unittest
from src.models.alarm import Alarm


class TestAlarmModel(unittest.TestCase):

    def test_validation(self):
        alarm = Alarm(hour=7, minute=30, repeat="once")
        self.assertIsNone(alarm.validate())

        bad_hour = Alarm(hour=25, minute=0)
        self.assertIsNotNone(bad_hour.validate())

        bad_min = Alarm(hour=12, minute=60)
        self.assertIsNotNone(bad_min.validate())

        empty_custom = Alarm(hour=8, minute=0, repeat="custom", days=[])
        self.assertIsNotNone(empty_custom.validate())

    def test_matches_datetime(self):
        # 2026-09-05 is a Saturday (python weekday() = 5 -> day_of_week = 6)
        sat_dt = datetime.datetime(2026, 9, 5, 8, 30)

        # Every day alarm
        everyday_alarm = Alarm(hour=8, minute=30, repeat="everyday", enabled=True)
        self.assertTrue(everyday_alarm.matches_datetime(sat_dt))

        # Weekday alarm (should not match Saturday)
        weekday_alarm = Alarm(hour=8, minute=30, repeat="weekdays", enabled=True)
        self.assertFalse(weekday_alarm.matches_datetime(sat_dt))

        # Weekend alarm (should match Saturday)
        weekend_alarm = Alarm(hour=8, minute=30, repeat="weekends", enabled=True)
        self.assertTrue(weekend_alarm.matches_datetime(sat_dt))

        # Custom days alarm matching Saturday (day 6)
        custom_alarm = Alarm(hour=8, minute=30, repeat="custom", days=[0, 6], enabled=True)
        self.assertTrue(custom_alarm.matches_datetime(sat_dt))

        # Disabled alarm
        disabled_alarm = Alarm(hour=8, minute=30, repeat="everyday", enabled=False)
        self.assertFalse(disabled_alarm.matches_datetime(sat_dt))

    def test_duplicate_checking(self):
        alarm1 = Alarm(id="a1", hour=9, minute=15, repeat="everyday")
        alarm2 = Alarm(id="a2", hour=9, minute=15, repeat="everyday")
        alarm3 = Alarm(id="a3", hour=9, minute=15, repeat="once")

        self.assertTrue(alarm1.is_duplicate_of(alarm2))
        self.assertFalse(alarm1.is_duplicate_of(alarm3))


if __name__ == "__main__":
    unittest.main()
