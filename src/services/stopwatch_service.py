import time
from typing import List, Tuple
from src.utils.logger import setup_logger

logger = setup_logger("StopwatchService")


class StopwatchService:
    def __init__(self):
        self.is_running = False
        self.start_time = 0.0
        self.elapsed_offset = 0.0
        self.laps: List[float] = []  # Stores cumulative elapsed milliseconds for each lap

    def start(self) -> None:
        if self.is_running:
            return
        self.is_running = True
        self.start_time = time.perf_counter()
        logger.info("Stopwatch started.")

    def pause(self) -> None:
        if not self.is_running:
            return
        self.elapsed_offset += (time.perf_counter() - self.start_time)
        self.is_running = False
        logger.info("Stopwatch paused.")

    def reset(self) -> None:
        self.is_running = False
        self.start_time = 0.0
        self.elapsed_offset = 0.0
        self.laps.clear()
        logger.info("Stopwatch reset.")

    def lap(self) -> float:
        if not self.is_running and self.elapsed_offset == 0:
            return 0.0
        current_elapsed = self.get_elapsed_ms()
        self.laps.insert(0, current_elapsed)
        logger.info(f"Stopwatch recorded lap: {current_elapsed:.2f} ms")
        return current_elapsed

    def get_elapsed_ms(self) -> float:
        if self.is_running:
            return (self.elapsed_offset + (time.perf_counter() - self.start_time)) * 1000.0
        return self.elapsed_offset * 1000.0

    def format_time(self, ms: float) -> Tuple[int, int, int, int]:
        """Returns (hours, minutes, seconds, centiseconds)"""
        total_cs = int(ms / 10)
        centiseconds = total_cs % 100
        total_seconds = total_cs // 100
        seconds = total_seconds % 60
        minutes = (total_seconds // 60) % 60
        hours = total_seconds // 3600
        return hours, minutes, seconds, centiseconds
