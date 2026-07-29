import time
from typing import Callable, Optional, Tuple
from src.utils.logger import setup_logger

logger = setup_logger("TimerService")


class TimerService:
    def __init__(self, on_complete: Optional[Callable[[], None]] = None):
        self.is_running = False
        self.total_duration_sec = 0
        self.remaining_sec = 0
        self.ends_at_perf = 0.0
        self.on_complete = on_complete

    def set_duration(self, hours: int, minutes: int, seconds: int) -> int:
        h = max(0, min(99, int(hours)))
        m = max(0, min(59, int(minutes)))
        s = max(0, min(59, int(seconds)))
        self.total_duration_sec = (h * 3600) + (m * 60) + s
        self.remaining_sec = self.total_duration_sec
        return self.total_duration_sec

    def start(self) -> bool:
        if self.is_running or self.remaining_sec <= 0:
            return False
        self.is_running = True
        self.ends_at_perf = time.perf_counter() + self.remaining_sec
        logger.info(f"Timer started for {self.remaining_sec} seconds.")
        return True

    def pause(self) -> None:
        if not self.is_running:
            return
        self.remaining_sec = max(0, int(self.ends_at_perf - time.perf_counter()))
        self.is_running = False
        logger.info(f"Timer paused with {self.remaining_sec} seconds remaining.")

    def reset(self) -> None:
        self.is_running = False
        self.total_duration_sec = 0
        self.remaining_sec = 0
        self.ends_at_perf = 0.0
        logger.info("Timer reset.")

    def get_remaining_sec(self) -> int:
        if self.is_running:
            rem = max(0, int(round(self.ends_at_perf - time.perf_counter())))
            self.remaining_sec = rem
            if rem <= 0:
                self.is_running = False
                logger.info("Timer completed!")
                if self.on_complete:
                    self.on_complete()
            return rem
        return self.remaining_sec

    def format_remaining(self) -> Tuple[int, int, int]:
        rem = self.get_remaining_sec()
        hours = rem // 3600
        minutes = (rem // 60) % 60
        seconds = rem % 60
        return hours, minutes, seconds
