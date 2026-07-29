import datetime
from dataclasses import dataclass, field
from typing import List, Optional
from src.utils.helpers import generate_id, format_alarm_time, describe_repeat, get_tone_display_name


@dataclass
class Alarm:
    id: str = field(default_factory=generate_id)
    hour: int = 7
    minute: int = 0
    label: str = ""
    tone: str = "classic-bell"
    repeat: str = "once"  # 'once', 'everyday', 'weekdays', 'weekends', 'custom'
    days: List[int] = field(default_factory=list)  # 0=Sun, 1=Mon, ..., 6=Sat
    enabled: bool = True

    def validate(self) -> Optional[str]:
        """Returns error message string if invalid, or None if valid."""
        if not isinstance(self.hour, int) or not (0 <= self.hour <= 23):
            return "Hour must be an integer between 0 and 23."
        if not isinstance(self.minute, int) or not (0 <= self.minute <= 59):
            return "Minute must be an integer between 0 and 59."
        if self.repeat == "custom" and not self.days:
            return "Please select at least one custom repeat day."
        valid_repeats = {"once", "everyday", "weekdays", "weekends", "custom"}
        if self.repeat not in valid_repeats:
            return f"Invalid repeat schedule '{self.repeat}'."
        return None

    def matches_datetime(self, dt: datetime.datetime) -> bool:
        """Determines whether this alarm should trigger at the specified datetime."""
        if not self.enabled:
            return False
        if self.hour != dt.hour or self.minute != dt.minute:
            return False

        # Python weekday: Mon=0 .. Sun=6 -> Map to 0=Sun, 1=Mon .. 6=Sat
        py_weekday = dt.weekday()
        day_of_week = (py_weekday + 1) % 7

        if self.repeat == "once" or self.repeat == "everyday":
            return True
        elif self.repeat == "weekdays":
            return 1 <= day_of_week <= 5
        elif self.repeat == "weekends":
            return day_of_week in (0, 6)
        elif self.repeat == "custom":
            return day_of_week in self.days
        return False

    def is_duplicate_of(self, other: "Alarm") -> bool:
        """Checks if another alarm has the exact same time and repeat schedule."""
        if self.id == other.id:
            return False
        if self.hour != other.hour or self.minute != other.minute:
            return False
        if self.repeat != other.repeat:
            return False
        if self.repeat == "custom":
            return sorted(self.days) == sorted(other.days)
        return True

    def formatted_time(self, time_format: str = "12") -> str:
        return format_alarm_time(self.hour, self.minute, time_format)

    @property
    def repeat_summary(self) -> str:
        return describe_repeat(self.repeat, self.days)

    @property
    def tone_display_name(self) -> str:
        return get_tone_display_name(self.tone)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "hour": self.hour,
            "minute": self.minute,
            "label": self.label,
            "tone": self.tone,
            "repeat": self.repeat,
            "days": self.days,
            "enabled": self.enabled,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Alarm":
        return cls(
            id=str(data.get("id", generate_id())),
            hour=int(data.get("hour", 7)),
            minute=int(data.get("minute", 0)),
            label=str(data.get("label", "")),
            tone=str(data.get("tone", "classic-bell")),
            repeat=str(data.get("repeat", "once")),
            days=[int(d) for d in data.get("days", []) if isinstance(d, (int, str))],
            enabled=bool(data.get("enabled", True)),
        )
