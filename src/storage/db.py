import json
import os
import sqlite3
from typing import List, Optional
from src.models.alarm import Alarm
from src.models.settings import Settings
from src.models.history import AlarmHistory
from src.utils.logger import setup_logger

logger = setup_logger("DatabaseManager")


class DatabaseManager:
    def __init__(self, db_path: str = "storage/smart_alarm.db"):
        self.db_path = db_path
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self._init_db()

    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self) -> None:
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                # Alarms table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS alarms (
                        id TEXT PRIMARY KEY,
                        hour INTEGER NOT NULL,
                        minute INTEGER NOT NULL,
                        label TEXT,
                        tone TEXT NOT NULL,
                        repeat TEXT NOT NULL,
                        days TEXT,
                        enabled INTEGER NOT NULL
                    )
                """)
                # Settings table (single key-value store or single row)
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS settings (
                        key TEXT PRIMARY KEY,
                        value TEXT NOT NULL
                    )
                """)
                # Alarm history table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS alarm_history (
                        id TEXT PRIMARY KEY,
                        alarm_id TEXT NOT NULL,
                        label TEXT,
                        tone TEXT,
                        action TEXT NOT NULL,
                        timestamp TEXT NOT NULL
                    )
                """)
                conn.commit()
                logger.info(f"Database initialized successfully at '{self.db_path}'.")
        except Exception as e:
            logger.error(f"Failed to initialize database: {e}", exc_info=True)
            raise

    # --- Alarms CRUD ---

    def get_all_alarms(self) -> List[Alarm]:
        alarms = []
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM alarms ORDER BY hour ASC, minute ASC")
                rows = cursor.fetchall()
                for row in rows:
                    days = json.loads(row["days"]) if row["days"] else []
                    alarm = Alarm(
                        id=row["id"],
                        hour=row["hour"],
                        minute=row["minute"],
                        label=row["label"] or "",
                        tone=row["tone"],
                        repeat=row["repeat"],
                        days=days,
                        enabled=bool(row["enabled"])
                    )
                    alarms.append(alarm)
        except Exception as e:
            logger.error(f"Error fetching alarms: {e}", exc_info=True)
        return alarms

    def save_alarm(self, alarm: Alarm) -> None:
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO alarms (id, hour, minute, label, tone, repeat, days, enabled)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    ON CONFLICT(id) DO UPDATE SET
                        hour=excluded.hour,
                        minute=excluded.minute,
                        label=excluded.label,
                        tone=excluded.tone,
                        repeat=excluded.repeat,
                        days=excluded.days,
                        enabled=excluded.enabled
                """, (
                    alarm.id,
                    alarm.hour,
                    alarm.minute,
                    alarm.label,
                    alarm.tone,
                    alarm.repeat,
                    json.dumps(alarm.days),
                    1 if alarm.enabled else 0
                ))
                conn.commit()
                logger.info(f"Saved alarm '{alarm.id}' ({alarm.hour:02d}:{alarm.minute:02d}).")
        except Exception as e:
            logger.error(f"Error saving alarm '{alarm.id}': {e}", exc_info=True)

    def delete_alarm(self, alarm_id: str) -> None:
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM alarms WHERE id = ?", (alarm_id,))
                conn.commit()
                logger.info(f"Deleted alarm '{alarm_id}'.")
        except Exception as e:
            logger.error(f"Error deleting alarm '{alarm_id}': {e}", exc_info=True)

    # --- Settings Storage ---

    def get_settings(self) -> Settings:
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT key, value FROM settings")
                rows = cursor.fetchall()
                if not rows:
                    default_settings = Settings()
                    self.save_settings(default_settings)
                    return default_settings

                data = {row["key"]: json.loads(row["value"]) for row in rows}
                return Settings.from_dict(data)
        except Exception as e:
            logger.error(f"Error fetching settings: {e}", exc_info=True)
            return Settings()

    def save_settings(self, settings: Settings) -> None:
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                settings_dict = settings.to_dict()
                for key, val in settings_dict.items():
                    cursor.execute("""
                        INSERT INTO settings (key, value)
                        VALUES (?, ?)
                        ON CONFLICT(key) DO UPDATE SET value=excluded.value
                    """, (key, json.dumps(val)))
                conn.commit()
                logger.info("Saved settings successfully.")
        except Exception as e:
            logger.error(f"Error saving settings: {e}", exc_info=True)

    # --- Alarm History Storage ---

    def add_history_entry(self, entry: AlarmHistory) -> None:
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO alarm_history (id, alarm_id, label, tone, action, timestamp)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    entry.id,
                    entry.alarm_id,
                    entry.label,
                    entry.tone,
                    entry.action,
                    entry.timestamp
                ))
                conn.commit()
        except Exception as e:
            logger.error(f"Error adding history entry: {e}", exc_info=True)

    def get_alarm_history(self, limit: int = 50) -> List[AlarmHistory]:
        history = []
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM alarm_history ORDER BY timestamp DESC LIMIT ?", (limit,))
                rows = cursor.fetchall()
                for row in rows:
                    entry = AlarmHistory(
                        id=row["id"],
                        alarm_id=row["alarm_id"],
                        label=row["label"] or "",
                        tone=row["tone"] or "",
                        action=row["action"],
                        timestamp=row["timestamp"]
                    )
                    history.append(entry)
        except Exception as e:
            logger.error(f"Error fetching alarm history: {e}", exc_info=True)
        return history
