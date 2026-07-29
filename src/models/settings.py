from dataclasses import dataclass

@dataclass
class Settings:
    time_format: str = "12"        # '12' or '24'
    theme: str = "system"          # 'dark', 'light', 'system'
    snooze_minutes: int = 5        # 1, 5, 10, 15, 30
    volume: float = 0.7            # 0.0 to 1.0
    default_tone: str = "classic-bell"
    animations_enabled: bool = True

    def validate(self) -> None:
        if self.time_format not in ("12", "24"):
            self.time_format = "12"
        if self.theme not in ("dark", "light", "system"):
            self.theme = "system"
        if self.snooze_minutes not in (1, 5, 10, 15, 30):
            self.snooze_minutes = 5
        self.volume = max(0.0, min(1.0, float(self.volume)))

    def to_dict(self) -> dict:
        return {
            "time_format": self.time_format,
            "theme": self.theme,
            "snooze_minutes": self.snooze_minutes,
            "volume": self.volume,
            "default_tone": self.default_tone,
            "animations_enabled": self.animations_enabled,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Settings":
        settings = cls(
            time_format=str(data.get("time_format", "12")),
            theme=str(data.get("theme", "system")),
            snooze_minutes=int(data.get("snooze_minutes", 5)),
            volume=float(data.get("volume", 0.7)),
            default_tone=str(data.get("default_tone", "classic-bell")),
            animations_enabled=bool(data.get("animations_enabled", True)),
        )
        settings.validate()
        return settings
