import datetime
import math
import customtkinter as ctk
from typing import Callable, Optional
from src.models.alarm import Alarm
from src.models.settings import Settings
from src.services.audio import AudioService
from src.utils.helpers import format_alarm_time, get_tone_display_name


class RingingWindow(ctk.CTkToplevel):
    def __init__(
        self,
        master: ctk.CTk,
        alarm: Alarm,
        settings: Settings,
        audio_service: AudioService,
        on_snooze: Callable[[Alarm], None],
        on_dismiss: Callable[[Alarm, str], None],
    ):
        super().__init__(master)
        self.alarm = alarm
        self.settings = settings
        self.audio_service = audio_service
        self.on_snooze = on_snooze
        self.on_dismiss = on_dismiss

        self.title("Smart Alarm - Ringing!")
        self.geometry("480x520")
        self.resizable(False, False)
        self.grab_set()  # Make window modal
        self.focus_force()

        # Canvas bell animation state
        self.bell_angle = 0
        self.bell_dir = 1
        self._anim_job = None

        self._build_ui()

        # Start ringing sound
        self.audio_service.play(self.alarm.tone, loop=True)
        self._animate_bell()
        self._update_clock()

    def _build_ui(self) -> None:
        self.container = ctk.CTkFrame(self, corner_radius=16)
        self.container.pack(fill="both", expand=True, padx=20, pady=20)

        # Pulsing Bell Canvas
        self.canvas = ctk.CTkCanvas(
            self.container,
            width=100,
            height=100,
            bg=self.container._apply_appearance_mode(self.container._fg_color),
            highlightthickness=0
        )
        self.canvas.pack(pady=(20, 10))

        # Time label
        self.time_label = ctk.CTkLabel(
            self.container,
            text="",
            font=ctk.CTkFont(size=42, weight="bold")
        )
        self.time_label.pack(pady=5)

        # Alarm Label / Title
        label_text = self.alarm.label or "Alarm"
        self.alarm_label = ctk.CTkLabel(
            self.container,
            text=label_text,
            font=ctk.CTkFont(size=22, weight="bold")
        )
        self.alarm_label.pack(pady=5)

        # Ringtone info
        tone_text = f"🔔 {get_tone_display_name(self.alarm.tone)}"
        self.tone_label = ctk.CTkLabel(
            self.container,
            text=tone_text,
            font=ctk.CTkFont(size=14),
            text_color="gray"
        )
        self.tone_label.pack(pady=5)

        # Action Buttons Frame
        btn_frame = ctk.CTkFrame(self.container, fg_color="transparent")
        btn_frame.pack(pady=30)

        snooze_text = f"Snooze ({self.settings.snooze_minutes} min)"
        self.btn_snooze = ctk.CTkButton(
            btn_frame,
            text=snooze_text,
            font=ctk.CTkFont(size=15, weight="bold"),
            fg_color="#3B82F6",
            hover_color="#2563EB",
            width=140,
            height=45,
            command=self._handle_snooze
        )
        self.btn_snooze.pack(side="left", padx=10)

        self.btn_dismiss = ctk.CTkButton(
            btn_frame,
            text="Dismiss",
            font=ctk.CTkFont(size=15, weight="bold"),
            fg_color="#EF4444",
            hover_color="#DC2626",
            width=140,
            height=45,
            command=self._handle_dismiss
        )
        self.btn_dismiss.pack(side="left", padx=10)

    def _animate_bell(self) -> None:
        if not self.winfo_exists():
            return
        self.canvas.delete("all")
        # Draw animated swinging bell icon
        cx, cy = 50, 50
        r = 30
        self.bell_angle += self.bell_dir * 3
        if abs(self.bell_angle) >= 20:
            self.bell_dir *= -1

        rad = math.radians(self.bell_angle)
        # Bell body arc/polygon
        x1 = cx - r * math.cos(rad)
        y1 = cy + r * math.sin(rad)
        x2 = cx + r * math.cos(rad)
        y2 = cy - r * math.sin(rad)

        color = "#F59E0B"
        self.canvas.create_oval(cx - 20, cy - 25, cx + 20, cy + 15, fill=color, outline="")
        self.canvas.create_oval(cx - 6, cy + 12, cx + 6, cy + 24, fill="#D97706", outline="")

        self._anim_job = self.after(50, self._animate_bell)

    def _update_clock(self) -> None:
        if not self.winfo_exists():
            return
        now = datetime.datetime.now()
        formatted = format_alarm_time(now.hour, now.minute, self.settings.time_format)
        self.time_label.configure(text=formatted)
        self.after(1000, self._update_clock)

    def _handle_snooze(self) -> None:
        self.audio_service.stop()
        self.on_snooze(self.alarm)
        self.destroy()

    def _handle_dismiss(self) -> None:
        self.audio_service.stop()
        self.on_dismiss(self.alarm, "dismissed")
        self.destroy()
