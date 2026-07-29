import datetime
import threading
import time
from typing import Callable, Dict, List, Set
from src.models.alarm import Alarm
from src.storage.db import DatabaseManager
from src.utils.logger import setup_logger

logger = setup_logger("AlarmScheduler")


class AlarmScheduler:
    def __init__(self, db: DatabaseManager, on_trigger: Callable[[Alarm, str], None]):
        self.db = db
        self.on_trigger = on_trigger  # Callback to schedule on GUI thread
        self.running = False
        self._thread: Optional[threading.Thread] = None
        self.triggered_occurrences: Set[str] = set()
        self.snooze_timers: Dict[str, threading.Timer] = {}
        self._lock = threading.Lock()

    def start(self) -> None:
        with self._lock:
            if self.running:
                return
            self.running = True
            self._thread = threading.Thread(target=self._run_loop, daemon=True, name="AlarmSchedulerThread")
            self._thread.start()
            logger.info("Alarm scheduler thread started.")

    def stop(self) -> None:
        with self._lock:
            self.running = False
            for timer in self.snooze_timers.values():
                timer.cancel()
            self.snooze_timers.clear()
            logger.info("Alarm scheduler stopped.")

    def _run_loop(self) -> None:
        while self.running:
            try:
                now = datetime.datetime.now()
                # Check only during the first 2 seconds of a minute
                if now.second <= 2:
                    self.check_alarms(now)
            except Exception as e:
                logger.error(f"Error in scheduler check loop: {e}", exc_info=True)
            time.sleep(1.0)

    def check_alarms(self, now: datetime.datetime) -> List[Alarm]:
        triggered = []
        alarms = self.db.get_all_alarms()
        
        for alarm in alarms:
            if not alarm.enabled:
                continue

            if alarm.matches_datetime(now):
                occurrence_key = f"{alarm.id}:{now.strftime('%Y-%m-%d-%H-%M')}"
                with self._lock:
                    if occurrence_key in self.triggered_occurrences:
                        continue
                    self.triggered_occurrences.add(occurrence_key)

                logger.info(f"Triggering alarm '{alarm.label or 'Alarm'}' ({alarm.formatted_time()}) [key={occurrence_key}]")

                # If one-time alarm, disable it in database
                if alarm.repeat == "once":
                    alarm.enabled = False
                    self.db.save_alarm(alarm)

                triggered.append(alarm)
                # Safely invoke trigger callback
                if self.on_trigger:
                    self.on_trigger(alarm, occurrence_key)

        # Cleanup old occurrence keys (keep under 500)
        with self._lock:
            if len(self.triggered_occurrences) > 500:
                self.triggered_occurrences.clear()

        return triggered

    def snooze_alarm(self, alarm: Alarm, snooze_minutes: int) -> None:
        def _snooze_expire():
            snooze_alarm_obj = Alarm(
                id=alarm.id,
                hour=alarm.hour,
                minute=alarm.minute,
                label=f"{alarm.label or 'Alarm'} (Snoozed)",
                tone=alarm.tone,
                repeat=alarm.repeat,
                days=alarm.days,
                enabled=True
            )
            occurrence_key = f"snooze:{alarm.id}:{datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S')}"
            logger.info(f"Snooze expired for alarm '{alarm.id}'. Re-triggering ring window.")
            if self.on_trigger:
                self.on_trigger(snooze_alarm_obj, occurrence_key)

        delay_seconds = snooze_minutes * 60
        timer = threading.Timer(delay_seconds, _snooze_expire)
        timer.daemon = True
        with self._lock:
            self.snooze_timers[alarm.id] = timer
            timer.start()
        logger.info(f"Alarm '{alarm.id}' snoozed for {snooze_minutes} minute(s).")
