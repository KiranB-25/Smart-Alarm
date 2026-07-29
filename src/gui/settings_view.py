import customtkinter as ctk
from typing import Callable, Optional
from src.models.settings import Settings
from src.services.audio import AudioService
from src.storage.db import DatabaseManager
from src.utils.helpers import TONE_OPTIONS, get_tone_display_name


class SettingsView(ctk.CTkFrame):
    def __init__(
        self,
        master: ctk.CTk,
        db: DatabaseManager,
        settings: Settings,
        audio_service: AudioService,
        on_settings_changed: Optional[Callable[[Settings], None]] = None,
        **kwargs
    ):
        super().__init__(master, **kwargs)
        self.db = db
        self.settings = settings
        self.audio_service = audio_service
        self.on_settings_changed = on_settings_changed

        self._build_ui()

    def _build_ui(self) -> None:
        # Title Header
        ctk.CTkLabel(
            self, text="Settings", font=ctk.CTkFont(size=28, weight="bold")
        ).pack(anchor="w", padx=30, pady=(20, 10))

        # Main Scrollable Settings Container
        self.scroll = ctk.CTkScrollableFrame(self, corner_radius=12)
        self.scroll.pack(fill="both", expand=True, padx=30, pady=(0, 20))

        # --- Appearance & Theme ---
        group_app = self._create_group("Appearance & Theme")
        
        row_theme = ctk.CTkFrame(group_app, fg_color="transparent")
        row_theme.pack(fill="x", padx=15, pady=10)
        ctk.CTkLabel(row_theme, text="Color Mode:", font=ctk.CTkFont(size=14, weight="bold")).pack(side="left")

        theme_map = {"system": "System", "dark": "Dark", "light": "Light"}
        inv_theme_map = {v: k for k, v in theme_map.items()}

        self.seg_theme = ctk.CTkSegmentedButton(
            row_theme,
            values=["System", "Dark", "Light"],
            command=lambda v: self._change_theme(inv_theme_map.get(v, "system"))
        )
        self.seg_theme.set(theme_map.get(self.settings.theme, "System"))
        self.seg_theme.pack(side="right")

        # --- Time Format ---
        row_fmt = ctk.CTkFrame(group_app, fg_color="transparent")
        row_fmt.pack(fill="x", padx=15, pady=10)
        ctk.CTkLabel(row_fmt, text="24-Hour Time Format:", font=ctk.CTkFont(size=14, weight="bold")).pack(side="left")

        self.switch_fmt = ctk.CTkSwitch(
            row_fmt,
            text="",
            width=45,
            command=self._change_time_format
        )
        if self.settings.time_format == "24":
            self.switch_fmt.select()
        else:
            self.switch_fmt.deselect()
        self.switch_fmt.pack(side="right")

        # --- Sound & Volume ---
        group_snd = self._create_group("Sound & Audio")

        row_vol = ctk.CTkFrame(group_snd, fg_color="transparent")
        row_vol.pack(fill="x", padx=15, pady=10)
        ctk.CTkLabel(row_vol, text="Master Volume:", font=ctk.CTkFont(size=14, weight="bold")).pack(side="left")

        self.lbl_vol = ctk.CTkLabel(
            row_vol, text=f"{int(self.settings.volume * 100)}%", font=ctk.CTkFont(size=14, weight="bold"), width=50
        )
        self.lbl_vol.pack(side="right")

        self.slider_vol = ctk.CTkSlider(
            row_vol, from_=0.0, to=1.0, number_of_steps=100, command=self._change_volume
        )
        self.slider_vol.set(self.settings.volume)
        self.slider_vol.pack(side="right", padx=15, fill="x", expand=True)

        row_tone = ctk.CTkFrame(group_snd, fg_color="transparent")
        row_tone.pack(fill="x", padx=15, pady=10)
        ctk.CTkLabel(row_tone, text="Default Ringtone:", font=ctk.CTkFont(size=14, weight="bold")).pack(side="left")

        tone_names = [name for _, name in TONE_OPTIONS]
        self.combo_tone = ctk.CTkComboBox(
            row_tone, values=tone_names, width=180, command=self._change_default_tone
        )
        self.combo_tone.set(get_tone_display_name(self.settings.default_tone))
        self.combo_tone.pack(side="right", padx=(10, 0))

        btn_prev = ctk.CTkButton(
            row_tone, text="▶ Preview", width=80, fg_color="#10B981", hover_color="#059669", command=self._preview_default_tone
        )
        btn_prev.pack(side="right")

        # --- Alarm Behavior ---
        group_beh = self._create_group("Alarm Behavior")

        row_snz = ctk.CTkFrame(group_beh, fg_color="transparent")
        row_snz.pack(fill="x", padx=15, pady=10)
        ctk.CTkLabel(row_snz, text="Snooze Duration:", font=ctk.CTkFont(size=14, weight="bold")).pack(side="left")

        snooze_opts = ["1 min", "5 min", "10 min", "15 min", "30 min"]
        self.combo_snooze = ctk.CTkComboBox(
            row_snz, values=snooze_opts, width=120, command=self._change_snooze
        )
        self.combo_snooze.set(f"{self.settings.snooze_minutes} min")
        self.combo_snooze.pack(side="right")

        # --- Alarm History Log ---
        group_hist = self._create_group("Alarm Execution History")
        
        self.hist_container = ctk.CTkFrame(group_hist, fg_color="transparent")
        self.hist_container.pack(fill="x", padx=15, pady=10)
        self.refresh_history()

    def _create_group(self, title: str) -> ctk.CTkFrame:
        group = ctk.CTkFrame(self.scroll, corner_radius=12)
        group.pack(fill="x", pady=10)
        ctk.CTkLabel(group, text=title, font=ctk.CTkFont(size=16, weight="bold")).pack(anchor="w", padx=15, pady=(12, 5))
        return group

    def _save_and_notify(self) -> None:
        self.db.save_settings(self.settings)
        if self.on_settings_changed:
            self.on_settings_changed(self.settings)

    def _change_theme(self, mode: str) -> None:
        self.settings.theme = mode
        ctk.set_appearance_mode(mode)
        self._save_and_notify()

    def _change_time_format(self) -> None:
        self.settings.time_format = "24" if self.switch_fmt.get() else "12"
        self._save_and_notify()

    def _change_volume(self, val: float) -> None:
        self.settings.volume = round(val, 2)
        self.audio_service.set_volume(self.settings.volume)
        self.lbl_vol.configure(text=f"{int(self.settings.volume * 100)}%")
        self._save_and_notify()

    def _change_default_tone(self, choice: str) -> None:
        for tid, name in TONE_OPTIONS:
            if name == choice:
                self.settings.default_tone = tid
                break
        self._save_and_notify()

    def _preview_default_tone(self) -> None:
        self.audio_service.play(self.settings.default_tone, loop=False)

    def _change_snooze(self, choice: str) -> None:
        mins = int(choice.split()[0])
        self.settings.snooze_minutes = mins
        self._save_and_notify()

    def refresh_history(self) -> None:
        for child in self.hist_container.winfo_children():
            child.destroy()

        history = self.db.get_alarm_history(limit=15)
        if not history:
            ctk.CTkLabel(self.hist_container, text="No alarm history recorded yet.", text_color="gray").pack(pady=10)
            return

        for entry in history:
            row = ctk.CTkFrame(self.hist_container, fg_color="transparent")
            row.pack(fill="x", pady=2)

            ctk.CTkLabel(row, text=entry.timestamp, font=ctk.CTkFont(size=12), text_color="gray", width=150, anchor="w").pack(side="left")
            ctk.CTkLabel(row, text=entry.label or "Alarm", font=ctk.CTkFont(size=13, weight="bold"), width=150, anchor="w").pack(side="left")
            
            action_color = "#10B981" if entry.action == "triggered" else ("#3B82F6" if entry.action == "snoozed" else "#EF4444")
            ctk.CTkLabel(row, text=entry.action.capitalize(), font=ctk.CTkFont(size=13, weight="bold"), text_color=action_color).pack(side="right")
