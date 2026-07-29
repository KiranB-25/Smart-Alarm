import uuid
from typing import List

DAY_NAMES = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]
FULL_DAY_NAMES = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]

TONE_OPTIONS = [
    ("classic-bell", "Classic Bell"),
    ("digital-alarm", "Digital Alarm"),
    ("morning-birds", "Morning Birds"),
    ("soft-piano", "Soft Piano"),
    ("nature", "Nature"),
    ("electronic", "Electronic"),
    ("gentle-chime", "Gentle Chime"),
    ("sunrise", "Sunrise"),
]

REPEAT_OPTIONS = [
    ("once", "Once"),
    ("everyday", "Every day"),
    ("weekdays", "Weekdays"),
    ("weekends", "Weekends"),
    ("custom", "Custom Days"),
]


def generate_id() -> str:
    return str(uuid.uuid4())[:8]


def format_alarm_time(hour: int, minute: int, time_format: str = "12") -> str:
    if time_format == "24":
        return f"{hour:02d}:{minute:02d}"
    
    period = "PM" if hour >= 12 else "AM"
    display_hour = hour % 12
    if display_hour == 0:
        display_hour = 12
    return f"{display_hour:02d}:{minute:02d} {period}"


def describe_repeat(repeat: str, days: List[int]) -> str:
    if repeat == "once":
        return "Once"
    elif repeat == "everyday":
        return "Every day"
    elif repeat == "weekdays":
        return "Weekdays (Mon-Fri)"
    elif repeat == "weekends":
        return "Weekends (Sat-Sun)"
    elif repeat == "custom":
        if not days:
            return "No days selected"
        sorted_days = sorted(days)
        return ", ".join(DAY_NAMES[d] for d in sorted_days if 0 <= d <= 6)
    return "Once"


def get_tone_display_name(tone_id: str) -> str:
    for tid, name in TONE_OPTIONS:
        if tid == tone_id:
            return name
    return "Classic Bell"
