import datetime
import math
import customtkinter as ctk
from src.models.settings import Settings
from src.utils.helpers import FULL_DAY_NAMES


class ClockView(ctk.CTkFrame):
    def __init__(self, master: ctk.CTk, settings: Settings, **kwargs):
        super().__init__(master, **kwargs)
        self.settings = settings
        self._update_job = None

        self._build_ui()
        self.update_clock()

    def _build_ui(self) -> None:
        # Title Header
        self.header = ctk.CTkLabel(
            self, text="Clock", font=ctk.CTkFont(size=28, weight="bold")
        )
        self.header.pack(anchor="w", padx=30, pady=(20, 10))

        # Main Layout Container (Digital + Analog side by side or stacked)
        self.container = ctk.CTkFrame(self, fg_color="transparent")
        self.container.pack(fill="both", expand=True, padx=30, pady=10)

        # Digital Clock Card
        self.card_digital = ctk.CTkFrame(self.container, corner_radius=16)
        self.card_digital.pack(side="left", fill="both", expand=True, padx=(0, 15), pady=10)

        self.lbl_day = ctk.CTkLabel(
            self.card_digital, text="", font=ctk.CTkFont(size=22, weight="bold"), text_color="#3B82F6"
        )
        self.lbl_day.pack(pady=(40, 5))

        self.lbl_time = ctk.CTkLabel(
            self.card_digital, text="", font=ctk.CTkFont(size=56, weight="bold")
        )
        self.lbl_time.pack(pady=10)

        self.lbl_date = ctk.CTkLabel(
            self.card_digital, text="", font=ctk.CTkFont(size=16), text_color="gray"
        )
        self.lbl_date.pack(pady=(5, 40))

        # Analog Clock Card
        self.card_analog = ctk.CTkFrame(self.container, corner_radius=16)
        self.card_analog.pack(side="right", fill="both", expand=True, padx=(15, 0), pady=10)

        self.canvas_analog = ctk.CTkCanvas(
            self.card_analog,
            width=280,
            height=280,
            bg=self.card_analog._apply_appearance_mode(self.card_analog._fg_color),
            highlightthickness=0
        )
        self.canvas_analog.pack(expand=True, pady=20)

    def update_clock(self) -> None:
        if not self.winfo_exists():
            return

        now = datetime.datetime.now()
        hour24 = now.hour
        hour = hour24 if self.settings.time_format == "24" else (hour24 % 12 or 12)
        period = f" {('PM' if hour24 >= 12 else 'AM')}" if self.settings.time_format == "12" else ""

        # Update Digital Clock
        time_str = f"{hour:02d} : {now.minute:02d} : {now.second:02d}{period}"
        self.lbl_time.configure(text=time_str)

        py_weekday = now.weekday()
        day_index = (py_weekday + 1) % 7
        self.lbl_day.configure(text=FULL_DAY_NAMES[day_index])
        self.lbl_date.configure(text=now.strftime("%B %d, %Y"))

        # Update Analog Clock Canvas
        self._draw_analog_clock(now)

        self._update_job = self.after(1000 - int(now.microsecond / 1000), self.update_clock)

    def _draw_analog_clock(self, now: datetime.datetime) -> None:
        self.canvas_analog.delete("all")
        cx, cy, r = 140, 140, 110

        bg_color = self.card_analog._apply_appearance_mode(self.card_analog._fg_color)
        self.canvas_analog.configure(bg=bg_color)

        # Outer ring
        self.canvas_analog.create_oval(cx - r, cy - r, cx + r, cy + r, outline="#4B5563", width=4)

        # Hour ticks
        for i in range(12):
            angle = math.radians(i * 30 - 90)
            x_outer = cx + (r - 8) * math.cos(angle)
            y_outer = cy + (r - 8) * math.sin(angle)
            x_inner = cx + (r - 20) * math.cos(angle)
            y_inner = cy + (r - 20) * math.sin(angle)
            self.canvas_analog.create_line(x_inner, y_inner, x_outer, y_outer, fill="#9CA3AF", width=3 if i % 3 == 0 else 1)

        # Hour hand
        hour_angle = math.radians(((now.hour % 12) + now.minute / 60.0) * 30 - 90)
        hx = cx + (r * 0.5) * math.cos(hour_angle)
        hy = cy + (r * 0.5) * math.sin(hour_angle)
        self.canvas_analog.create_line(cx, cy, hx, hy, fill="#F3F4F6", width=6, capstyle="round")

        # Minute hand
        min_angle = math.radians((now.minute + now.second / 60.0) * 6 - 90)
        mx = cx + (r * 0.75) * math.cos(min_angle)
        my = cy + (r * 0.75) * math.sin(min_angle)
        self.canvas_analog.create_line(cx, cy, mx, my, fill="#60A5FA", width=4, capstyle="round")

        # Second hand
        sec_angle = math.radians(now.second * 6 - 90)
        sx = cx + (r * 0.85) * math.cos(sec_angle)
        sy = cy + (r * 0.85) * math.sin(sec_angle)
        self.canvas_analog.create_line(cx, cy, sx, sy, fill="#EF4444", width=2)

        # Center pin
        self.canvas_analog.create_oval(cx - 6, cy - 6, cx + 6, cy + 6, fill="#EF4444", outline="")
