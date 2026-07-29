import customtkinter as ctk
from typing import Callable, List, Optional
from src.models.alarm import Alarm
from src.models.settings import Settings
from src.services.audio import AudioService
from src.storage.db import DatabaseManager
from src.utils.helpers import DAY_NAMES, REPEAT_OPTIONS, TONE_OPTIONS, generate_id, get_tone_display_name


class AlarmEditorDialog(ctk.CTkToplevel):
    def __init__(
        self,
        master: ctk.CTk,
        alarm: Optional[Alarm],
        settings: Settings,
        audio_service: AudioService,
        on_save: Callable[[Alarm], Optional[str]],
    ):
        super().__init__(master)
        self.editing_alarm = alarm
        self.settings = settings
        self.audio_service = audio_service
        self.on_save = on_save

        self.title("Edit Alarm" if alarm else "New Alarm")
        self.geometry("450x580")
        self.resizable(False, False)
        self.grab_set()
        self.focus_force()

        self._build_ui()

    def _build_ui(self) -> None:
        container = ctk.CTkFrame(self, corner_radius=12)
        container.pack(fill="both", expand=True, padx=20, pady=20)

        # Title
        title_text = "Edit Alarm" if self.editing_alarm else "New Alarm"
        ctk.CTkLabel(container, text=title_text, font=ctk.CTkFont(size=20, weight="bold")).pack(pady=(15, 10))

        # Time Selection (Hours & Minutes)
        time_frame = ctk.CTkFrame(container, fg_color="transparent")
        time_frame.pack(pady=10)

        h_val = self.editing_alarm.hour if self.editing_alarm else 7
        m_val = self.editing_alarm.minute if self.editing_alarm else 0

        ctk.CTkLabel(time_frame, text="Time:", font=ctk.CTkFont(size=14, weight="bold")).pack(side="left", padx=10)

        self.spin_hour = ctk.CTkComboBox(
            time_frame, values=[f"{h:02d}" for h in range(24)], width=75
        )
        self.spin_hour.set(f"{h_val:02d}")
        self.spin_hour.pack(side="left", padx=5)

        ctk.CTkLabel(time_frame, text=":", font=ctk.CTkFont(size=18, weight="bold")).pack(side="left")

        self.spin_minute = ctk.CTkComboBox(
            time_frame, values=[f"{m:02d}" for m in range(60)], width=75
        )
        self.spin_minute.set(f"{m_val:02d}")
        self.spin_minute.pack(side="left", padx=5)

        # Label Entry
        label_frame = ctk.CTkFrame(container, fg_color="transparent")
        label_frame.pack(fill="x", padx=20, pady=10)
        ctk.CTkLabel(label_frame, text="Label:", font=ctk.CTkFont(size=14, weight="bold")).pack(anchor="w")
        self.entry_label = ctk.CTkEntry(label_frame, placeholder_text="Alarm Label (e.g. Work, Gym)")
        self.entry_label.insert(0, self.editing_alarm.label if self.editing_alarm else "")
        self.entry_label.pack(fill="x", pady=5)

        # Tone Selector & Preview Buttons
        tone_frame = ctk.CTkFrame(container, fg_color="transparent")
        tone_frame.pack(fill="x", padx=20, pady=10)
        ctk.CTkLabel(tone_frame, text="Ringtone:", font=ctk.CTkFont(size=14, weight="bold")).pack(anchor="w")

        tone_sub = ctk.CTkFrame(tone_frame, fg_color="transparent")
        tone_sub.pack(fill="x", pady=5)

        tone_names = [name for _, name in TONE_OPTIONS]
        default_tone_id = self.editing_alarm.tone if self.editing_alarm else self.settings.default_tone
        
        self.combo_tone = ctk.CTkComboBox(tone_sub, values=tone_names, width=220)
        self.combo_tone.set(get_tone_display_name(default_tone_id))
        self.combo_tone.pack(side="left", fill="x", expand=True)

        self.btn_preview = ctk.CTkButton(
            tone_sub, text="▶ Preview", width=90, fg_color="#10B981", hover_color="#059669", command=self._preview_tone
        )
        self.btn_preview.pack(side="right", padx=(10, 0))

        # Repeat Selection
        repeat_frame = ctk.CTkFrame(container, fg_color="transparent")
        repeat_frame.pack(fill="x", padx=20, pady=10)
        ctk.CTkLabel(repeat_frame, text="Repeat Schedule:", font=ctk.CTkFont(size=14, weight="bold")).pack(anchor="w")

        repeat_names = [name for _, name in REPEAT_OPTIONS]
        cur_repeat = self.editing_alarm.repeat if self.editing_alarm else "once"
        cur_repeat_name = dict(REPEAT_OPTIONS).get(cur_repeat, "Once")

        self.combo_repeat = ctk.CTkComboBox(
            repeat_frame, values=repeat_names, width=220, command=self._on_repeat_change
        )
        self.combo_repeat.set(cur_repeat_name)
        self.combo_repeat.pack(anchor="w", pady=5)

        # Custom Days Checkboxes Frame
        self.days_frame = ctk.CTkFrame(container, fg_color="transparent")
        self.day_checkboxes = []
        cur_days = self.editing_alarm.days if self.editing_alarm else []

        cb_sub = ctk.CTkFrame(self.days_frame, fg_color="transparent")
        cb_sub.pack(fill="x", pady=2)
        for i, name in enumerate(DAY_NAMES):
            var = ctk.BooleanVar(value=(i in cur_days))
            cb = ctk.CTkCheckBox(cb_sub, text=name, variable=var, width=50)
            cb.pack(side="left", padx=2)
            self.day_checkboxes.append((i, var))

        if cur_repeat == "custom":
            self.days_frame.pack(fill="x", padx=20, pady=5)

        # Error label
        self.lbl_error = ctk.CTkLabel(container, text="", text_color="#EF4444", font=ctk.CTkFont(size=13))
        self.lbl_error.pack(pady=5)

        # Actions (Save / Cancel)
        act_frame = ctk.CTkFrame(container, fg_color="transparent")
        act_frame.pack(side="bottom", fill="x", padx=20, pady=15)

        btn_save = ctk.CTkButton(act_frame, text="Save Alarm", fg_color="#3B82F6", hover_color="#2563EB", command=self._save)
        btn_save.pack(side="right", padx=5)

        btn_cancel = ctk.CTkButton(act_frame, text="Cancel", fg_color="gray", command=self._cancel)
        btn_cancel.pack(side="right", padx=5)

    def _on_repeat_change(self, choice: str) -> None:
        if choice == "Custom Days":
            self.days_frame.pack(fill="x", padx=20, pady=5)
        else:
            self.days_frame.pack_forget()

    def _preview_tone(self) -> None:
        selected_name = self.combo_tone.get()
        tone_id = "classic-bell"
        for tid, name in TONE_OPTIONS:
            if name == selected_name:
                tone_id = tid
                break
        self.audio_service.play(tone_id, loop=False)

    def _save(self) -> None:
        self.audio_service.stop()
        h = int(self.spin_hour.get())
        m = int(self.spin_minute.get())
        label = self.entry_label.get().strip()

        # Get tone_id
        selected_tone_name = self.combo_tone.get()
        tone_id = "classic-bell"
        for tid, name in TONE_OPTIONS:
            if name == selected_tone_name:
                tone_id = tid
                break

        # Get repeat key
        selected_repeat_name = self.combo_repeat.get()
        repeat_key = "once"
        for rk, rname in REPEAT_OPTIONS:
            if rname == selected_repeat_name:
                repeat_key = rk
                break

        days = []
        if repeat_key == "custom":
            days = [i for i, var in self.day_checkboxes if var.get()]

        alarm = Alarm(
            id=self.editing_alarm.id if self.editing_alarm else generate_id(),
            hour=h,
            minute=m,
            label=label,
            tone=tone_id,
            repeat=repeat_key,
            days=days,
            enabled=True
        )

        error = self.on_save(alarm)
        if error:
            self.lbl_error.configure(text=error)
        else:
            self.destroy()

    def _cancel(self) -> None:
        self.audio_service.stop()
        self.destroy()


class AlarmView(ctk.CTkFrame):
    def __init__(
        self,
        master: ctk.CTk,
        db: DatabaseManager,
        settings: Settings,
        audio_service: AudioService,
        on_alarms_changed: Optional[Callable[[], None]] = None,
        **kwargs
    ):
        super().__init__(master, **kwargs)
        self.db = db
        self.settings = settings
        self.audio_service = audio_service
        self.on_alarms_changed = on_alarms_changed

        self._build_ui()
        self.refresh_list()

    def _build_ui(self) -> None:
        # Header
        top_bar = ctk.CTkFrame(self, fg_color="transparent")
        top_bar.pack(fill="x", padx=30, pady=(20, 10))

        ctk.CTkLabel(top_bar, text="Alarms", font=ctk.CTkFont(size=28, weight="bold")).pack(side="left")

        btn_add = ctk.CTkButton(
            top_bar,
            text="+ Add Alarm",
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color="#3B82F6",
            hover_color="#2563EB",
            command=self._open_add_dialog
        )
        btn_add.pack(side="right")

        # Scrollable Alarm Cards List
        self.scroll_list = ctk.CTkScrollableFrame(self, corner_radius=12)
        self.scroll_list.pack(fill="both", expand=True, padx=30, pady=10)

    def refresh_list(self) -> None:
        for child in self.scroll_list.winfo_children():
            child.destroy()

        alarms = self.db.get_all_alarms()

        if not alarms:
            empty_lbl = ctk.CTkLabel(
                self.scroll_list,
                text="No alarms configured. Click '+ Add Alarm' to create one.",
                font=ctk.CTkFont(size=15),
                text_color="gray"
            )
            empty_lbl.pack(pady=50)
            return

        for alarm in alarms:
            card = ctk.CTkFrame(self.scroll_list, corner_radius=12)
            card.pack(fill="x", padx=10, pady=8)

            # Left: Toggle switch
            switch_var = ctk.BooleanVar(value=alarm.enabled)
            switch = ctk.CTkSwitch(
                card,
                text="",
                variable=switch_var,
                width=45,
                command=lambda a=alarm, v=switch_var: self._toggle_alarm(a, v.get())
            )
            switch.pack(side="left", padx=15)

            # Center: Time & Details
            info_frame = ctk.CTkFrame(card, fg_color="transparent")
            info_frame.pack(side="left", fill="both", expand=True, pady=10)

            time_str = alarm.formatted_time(self.settings.time_format)
            lbl_time = ctk.CTkLabel(
                info_frame, text=time_str, font=ctk.CTkFont(size=24, weight="bold")
            )
            lbl_time.pack(anchor="w")

            meta_str = f"{alarm.label or 'Alarm'}  ·  {alarm.repeat_summary}  ·  {alarm.tone_display_name}"
            lbl_meta = ctk.CTkLabel(
                info_frame, text=meta_str, font=ctk.CTkFont(size=13), text_color="gray"
            )
            lbl_meta.pack(anchor="w")

            # Right: Edit & Delete Buttons
            btn_frame = ctk.CTkFrame(card, fg_color="transparent")
            btn_frame.pack(side="right", padx=15)

            btn_edit = ctk.CTkButton(
                btn_frame,
                text="✎",
                width=36,
                height=36,
                fg_color="gray30",
                hover_color="gray40",
                command=lambda a=alarm: self._open_edit_dialog(a)
            )
            btn_edit.pack(side="left", padx=4)

            btn_del = ctk.CTkButton(
                btn_frame,
                text="✕",
                width=36,
                height=36,
                fg_color="#EF4444",
                hover_color="#DC2626",
                command=lambda a=alarm: self._delete_alarm(a)
            )
            btn_del.pack(side="left", padx=4)

    def _toggle_alarm(self, alarm: Alarm, enabled: bool) -> None:
        alarm.enabled = enabled
        self.db.save_alarm(alarm)
        if self.on_alarms_changed:
            self.on_alarms_changed()

    def _delete_alarm(self, alarm: Alarm) -> None:
        self.db.delete_alarm(alarm.id)
        self.refresh_list()
        if self.on_alarms_changed:
            self.on_alarms_changed()

    def _open_add_dialog(self) -> None:
        AlarmEditorDialog(
            master=self.winfo_toplevel(),
            alarm=None,
            settings=self.settings,
            audio_service=self.audio_service,
            on_save=self._save_alarm
        )

    def _open_edit_dialog(self, alarm: Alarm) -> None:
        AlarmEditorDialog(
            master=self.winfo_toplevel(),
            alarm=alarm,
            settings=self.settings,
            audio_service=self.audio_service,
            on_save=self._save_alarm
        )

    def _save_alarm(self, candidate: Alarm) -> Optional[str]:
        # Validate model
        err = candidate.validate()
        if err:
            return err

        # Prevent duplicate alarms (same time & repeat schedule)
        existing_alarms = self.db.get_all_alarms()
        for existing in existing_alarms:
            if candidate.is_duplicate_of(existing):
                return "An alarm with the exact same time and repeat schedule already exists."

        self.db.save_alarm(candidate)
        self.refresh_list()
        if self.on_alarms_changed:
            self.on_alarms_changed()
        return None
