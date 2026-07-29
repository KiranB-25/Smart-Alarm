import datetime
from dataclasses import dataclass, field
from src.utils.helpers import generate_id

@dataclass
class AlarmHistory:
    id: str = field(default_factory=generate_id)
    alarm_id: str = ""
    label: str = ""
    tone: str = ""
    action: str = "triggered"  # 'triggered', 'snoozed', 'dismissed', 'stopped'
    timestamp: str = field(default_factory=lambda: datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "alarm_id": self.alarm_id,
            "label": self.label,
            "tone": self.tone,
            "action": self.action,
            "timestamp": self.timestamp,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "AlarmHistory":
        return cls(
            id=str(data.get("id", generate_id())),
            alarm_id=str(data.get("alarm_id", "")),
            label=str(data.get("label", "")),
            tone=str(data.get("tone", "")),
            action=str(data.get("action", "triggered")),
            timestamp=str(data.get("timestamp", datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))),
        )
