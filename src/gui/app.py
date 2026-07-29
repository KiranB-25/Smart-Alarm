import customtkinter as ctk
from typing import Dict, Optional
from src.models.alarm import Alarm
from src.models.history import AlarmHistory
from src.models.settings import Settings
from src.services.audio import AudioService
from src.services.scheduler import AlarmScheduler
from src.services.stopwatch_service import StopwatchService
from src.services.timer_service import TimerService
from src.storage.db import DatabaseManager
from src.utils.logger import setup_logger

from src.gui.clock_view import ClockView
from src.gui.alarm_view import AlarmView
from src.gui.stopwatch_view import StopwatchView
from src.gui.timer_view import TimerView
from src.gui.settings_view import SettingsView
from src.gui.ringing_window import RingingWindow

logger = setup_logger("SmartAlarmApp")


class SmartAlarmApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Smart Alarm Desktop")
        self.geometry("980x660")
        self.minsize(840, 560)

        # Database & Services Initialisation
        self.db = DatabaseManager()
        self.settings: Settings = self.db.get_settings()

        # Apply saved appearance mode
        ctk.set_appearance_mode(self.settings.theme)
        ctk.set_default_color_theme("blue")

        self.audio_service = AudioService(initial_volume=self.settings.volume)
        self.stopwatch_service = StopwatchService()
        self.timer_service = TimerService()

        # Thread-safe scheduler callback handler
        self.scheduler = AlarmScheduler(
            db=self.db,
            on_trigger=self._on_alarm_triggered_threadsafe
        )

        self.active_ringing_window: Optional[RingingWindow] = None

        self._build_ui()
        self.scheduler.start()

        self.protocol("WM_DELETE_WINDOW", self._on_close)

    def _build_ui(self) -> None:
        # Layout: Left Sidebar + Right View Area
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Sidebar
        self.sidebar = ctk.CTkFrame(self, width=200, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_rowconfigure(6, weight=1)

        # Logo / Title
        logo_lbl = ctk.CTkLabel(
            self.sidebar, text="⏰ Smart Alarm", font=ctk.CTkFont(size=20, weight="bold")
        )
        logo_lbl.grid(row=0, column=0, padx=20, pady=(25, 20))

        # Nav Buttons
        self.nav_buttons: Dict[str, ctk.CTkButton] = {}
        nav_items = [
            ("clock", "🕒 Clock"),
            ("alarms", "⏰ Alarms"),
            ("stopwatch", "⏱ Stopwatch"),
            ("timer", "⌛ Timer"),
            ("settings", "⚙ Settings"),
        ]

        for idx, (view_name, label) in enumerate(nav_items, start=1):
            btn = ctk.CTkButton(
                self.sidebar,
                text=label,
                font=ctk.CTkFont(size=15, weight="bold"),
                anchor="w",
                fg_color="transparent",
                text_color=("gray10", "gray90"),
                hover_color=("gray70", "gray30"),
                height=42,
                command=lambda name=view_name: self.show_view(name)
            )
            btn.grid(row=idx, column=0, padx=15, pady=4, sticky="ew")
            self.nav_buttons[view_name] = btn

        # Main View Container Area
        self.view_container = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.view_container.grid(row=0, column=1, sticky="nsew")
        self.view_container.grid_columnconfigure(0, weight=1)
        self.view_container.grid_rowconfigure(0, weight=1)

        # Views Dictionary
        self.views = {
            "clock": ClockView(self.view_container, settings=self.settings),
            "alarms": AlarmView(
                self.view_container,
                db=self.db,
                settings=self.settings,
                audio_service=self.audio_service,
                on_alarms_changed=self._on_alarms_changed
            ),
            "stopwatch": StopwatchView(self.view_container, stopwatch_service=self.stopwatch_service),
            "timer": TimerView(
                self.view_container,
                timer_service=self.timer_service,
                settings=self.settings,
                audio_service=self.audio_service
            ),
            "settings": SettingsView(
                self.view_container,
                db=self.db,
                settings=self.settings,
                audio_service=self.audio_service,
                on_settings_changed=self._on_settings_changed
            ),
        }

        for view in self.views.values():
            view.grid(row=0, column=0, sticky="nsew")

        # Show initial view
        self.show_view("clock")

    def show_view(self, view_name: str) -> None:
        for name, btn in self.nav_buttons.items():
            if name == view_name:
                btn.configure(fg_color=("#3B82F6", "#2563EB"), text_color="white")
            else:
                btn.configure(fg_color="transparent", text_color=("gray10", "gray90"))

        view = self.views.get(view_name)
        if view:
            view.tkraise()

    def _on_alarms_changed(self) -> None:
        # Refresh any relevant UI
        pass

    def _on_settings_changed(self, updated_settings: Settings) -> None:
        self.settings = updated_settings
        # Refresh views that depend on settings
        if "clock" in self.views and isinstance(self.views["clock"], ClockView):
            self.views["clock"].update_clock()
        if "alarms" in self.views and isinstance(self.views["alarms"], AlarmView):
            self.views["alarms"].refresh_list()

    def _on_alarm_triggered_threadsafe(self, alarm: Alarm, occurrence_key: str) -> None:
        """Safely called from background thread. Schedules GUI update on main thread via root.after()."""
        logger.info(f"Received alarm trigger event on main thread: {alarm.label} ({occurrence_key})")
        self.after(0, self._open_ringing_window, alarm, occurrence_key)

    def _open_ringing_window(self, alarm: Alarm, occurrence_key: str) -> None:
        # Record trigger in history
        history_entry = AlarmHistory(
            alarm_id=alarm.id,
            label=alarm.label or "Alarm",
            tone=alarm.tone,
            action="triggered"
        )
        self.db.add_history_entry(history_entry)

        # Close existing ringing window if any
        if self.active_ringing_window and self.active_ringing_window.winfo_exists():
            self.active_ringing_window.destroy()

        # Open top-level modal RingingWindow
        self.active_ringing_window = RingingWindow(
            master=self,
            alarm=alarm,
            settings=self.settings,
            audio_service=self.audio_service,
            on_snooze=self._on_snooze_alarm,
            on_dismiss=self._on_dismiss_alarm
        )

    def _on_snooze_alarm(self, alarm: Alarm) -> None:
        history_entry = AlarmHistory(
            alarm_id=alarm.id,
            label=alarm.label or "Alarm",
            tone=alarm.tone,
            action="snoozed"
        )
        self.db.add_history_entry(history_entry)
        self.scheduler.snooze_alarm(alarm, self.settings.snooze_minutes)

        # Refresh settings history table if visible
        if "settings" in self.views and isinstance(self.views["settings"], SettingsView):
            self.views["settings"].refresh_history()

    def _on_dismiss_alarm(self, alarm: Alarm, action: str) -> None:
        history_entry = AlarmHistory(
            alarm_id=alarm.id,
            label=alarm.label or "Alarm",
            tone=alarm.tone,
            action=action
        )
        self.db.add_history_entry(history_entry)

        if "settings" in self.views and isinstance(self.views["settings"], SettingsView):
            self.views["settings"].refresh_history()

    def _on_close(self) -> None:
        logger.info("Closing application...")
        self.scheduler.stop()
        self.audio_service.stop()
        self.destroy()
