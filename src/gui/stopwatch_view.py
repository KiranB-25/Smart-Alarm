import customtkinter as ctk
from src.services.stopwatch_service import StopwatchService


class StopwatchView(ctk.CTkFrame):
    def __init__(self, master: ctk.CTk, stopwatch_service: StopwatchService, **kwargs):
        super().__init__(master, **kwargs)
        self.stopwatch = stopwatch_service
        self._anim_job = None

        self._build_ui()
        self._update_loop()

    def _build_ui(self) -> None:
        # Title Header
        ctk.CTkLabel(
            self, text="Stopwatch", font=ctk.CTkFont(size=28, weight="bold")
        ).pack(anchor="w", padx=30, pady=(20, 10))

        # Main Display Card
        self.card = ctk.CTkFrame(self, corner_radius=16)
        self.card.pack(fill="x", padx=30, pady=10)

        # Time Display (HH : MM : SS . cs)
        self.lbl_display = ctk.CTkLabel(
            self.card,
            text="00 : 00 : 00 . 00",
            font=ctk.CTkFont(size=52, weight="bold")
        )
        self.lbl_display.pack(pady=30)

        # Control Buttons
        btn_frame = ctk.CTkFrame(self.card, fg_color="transparent")
        btn_frame.pack(pady=(0, 25))

        self.btn_start = ctk.CTkButton(
            btn_frame,
            text="Start",
            font=ctk.CTkFont(size=16, weight="bold"),
            fg_color="#10B981",
            hover_color="#059669",
            width=120,
            height=42,
            command=self._toggle_start_pause
        )
        self.btn_start.pack(side="left", padx=10)

        self.btn_lap = ctk.CTkButton(
            btn_frame,
            text="Lap",
            font=ctk.CTkFont(size=16, weight="bold"),
            fg_color="#3B82F6",
            hover_color="#2563EB",
            width=120,
            height=42,
            command=self._record_lap
        )
        self.btn_lap.pack(side="left", padx=10)

        self.btn_reset = ctk.CTkButton(
            btn_frame,
            text="Reset",
            font=ctk.CTkFont(size=16, weight="bold"),
            fg_color="gray",
            hover_color="gray40",
            width=120,
            height=42,
            command=self._reset
        )
        self.btn_reset.pack(side="left", padx=10)

        # Laps Table Header & Scrollable List
        lap_header = ctk.CTkFrame(self, fg_color="transparent")
        lap_header.pack(fill="x", padx=35, pady=(15, 5))

        ctk.CTkLabel(lap_header, text="Lap #", font=ctk.CTkFont(size=14, weight="bold"), width=80, anchor="w").pack(side="left")
        ctk.CTkLabel(lap_header, text="Lap Time", font=ctk.CTkFont(size=14, weight="bold"), width=160, anchor="center").pack(side="left", expand=True)
        ctk.CTkLabel(lap_header, text="Overall Time", font=ctk.CTkFont(size=14, weight="bold"), width=160, anchor="e").pack(side="right")

        self.scroll_laps = ctk.CTkScrollableFrame(self, corner_radius=12)
        self.scroll_laps.pack(fill="both", expand=True, padx=30, pady=(0, 20))

    def _toggle_start_pause(self) -> None:
        if self.stopwatch.is_running:
            self.stopwatch.pause()
            self.btn_start.configure(text="Resume", fg_color="#3B82F6", hover_color="#2563EB")
        else:
            self.stopwatch.start()
            self.btn_start.configure(text="Pause", fg_color="#EF4444", hover_color="#DC2626")

    def _record_lap(self) -> None:
        self.stopwatch.lap()
        self.refresh_laps()

    def _reset(self) -> None:
        self.stopwatch.reset()
        self.btn_start.configure(text="Start", fg_color="#10B981", hover_color="#059669")
        self.refresh_laps()

    def refresh_laps(self) -> None:
        for child in self.scroll_laps.winfo_children():
            child.destroy()

        laps = self.stopwatch.laps
        if not laps:
            ctk.CTkLabel(
                self.scroll_laps,
                text="No laps recorded.",
                font=ctk.CTkFont(size=14),
                text_color="gray"
            ).pack(pady=30)
            return

        total_laps = len(laps)
        for idx, lap_total_ms in enumerate(laps):
            lap_num = total_laps - idx
            prev_total_ms = laps[idx + 1] if (idx + 1) < total_laps else 0.0
            split_ms = lap_total_ms - prev_total_ms

            row = ctk.CTkFrame(self.scroll_laps, fg_color="transparent")
            row.pack(fill="x", padx=10, pady=4)

            h, m, s, cs = self.stopwatch.format_time(split_ms)
            split_str = f"{h:02d}:{m:02d}:{s:02d}.{cs:02d}"

            oh, om, os_, ocs = self.stopwatch.format_time(lap_total_ms)
            overall_str = f"{oh:02d}:{om:02d}:{os_:02d}.{ocs:02d}"

            ctk.CTkLabel(row, text=f"Lap {lap_num}", font=ctk.CTkFont(size=14), width=80, anchor="w").pack(side="left")
            ctk.CTkLabel(row, text=split_str, font=ctk.CTkFont(size=14, weight="bold"), width=160, anchor="center").pack(side="left", expand=True)
            ctk.CTkLabel(row, text=overall_str, font=ctk.CTkFont(size=14), width=160, anchor="e").pack(side="right")

    def _update_loop(self) -> None:
        if not self.winfo_exists():
            return

        ms = self.stopwatch.get_elapsed_ms()
        h, m, s, cs = self.stopwatch.format_time(ms)
        self.lbl_display.configure(text=f"{h:02d} : {m:02d} : {s:02d} . {cs:02d}")

        self.after(30, self._update_loop)
