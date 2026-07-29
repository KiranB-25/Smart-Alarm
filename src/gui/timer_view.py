import customtkinter as ctk
from src.models.settings import Settings
from src.services.audio import AudioService
from src.services.timer_service import TimerService


class TimerView(ctk.CTkFrame):
    def __init__(
        self,
        master: ctk.CTk,
        timer_service: TimerService,
        settings: Settings,
        audio_service: AudioService,
        **kwargs
    ):
        super().__init__(master, **kwargs)
        self.timer_service = timer_service
        self.settings = settings
        self.audio_service = audio_service
        self.timer_service.on_complete = self._on_timer_complete

        self._build_ui()
        self._update_loop()

    def _build_ui(self) -> None:
        # Title Header
        ctk.CTkLabel(
            self, text="Countdown Timer", font=ctk.CTkFont(size=28, weight="bold")
        ).pack(anchor="w", padx=30, pady=(20, 10))

        # Main Card
        self.card = ctk.CTkFrame(self, corner_radius=16)
        self.card.pack(fill="x", padx=30, pady=10)

        # Time Input Controls (HH, MM, SS)
        self.input_frame = ctk.CTkFrame(self.card, fg_color="transparent")
        self.input_frame.pack(pady=(30, 15))

        # Hours
        ctk.CTkLabel(self.input_frame, text="Hours", font=ctk.CTkFont(size=12, weight="bold")).grid(row=0, column=0, padx=8)
        self.combo_h = ctk.CTkComboBox(self.input_frame, values=[f"{i:02d}" for i in range(100)], width=80)
        self.combo_h.set("00")
        self.combo_h.grid(row=1, column=0, padx=8)

        ctk.CTkLabel(self.input_frame, text=":", font=ctk.CTkFont(size=24, weight="bold")).grid(row=1, column=1)

        # Minutes
        ctk.CTkLabel(self.input_frame, text="Minutes", font=ctk.CTkFont(size=12, weight="bold")).grid(row=0, column=2, padx=8)
        self.combo_m = ctk.CTkComboBox(self.input_frame, values=[f"{i:02d}" for i in range(60)], width=80)
        self.combo_m.set("05")
        self.combo_m.grid(row=1, column=2, padx=8)

        ctk.CTkLabel(self.input_frame, text=":", font=ctk.CTkFont(size=24, weight="bold")).grid(row=1, column=3)

        # Seconds
        ctk.CTkLabel(self.input_frame, text="Seconds", font=ctk.CTkFont(size=12, weight="bold")).grid(row=0, column=4, padx=8)
        self.combo_s = ctk.CTkComboBox(self.input_frame, values=[f"{i:02d}" for i in range(60)], width=80)
        self.combo_s.set("00")
        self.combo_s.grid(row=1, column=4, padx=8)

        # Display Label
        self.lbl_display = ctk.CTkLabel(
            self.card,
            text="00 : 05 : 00",
            font=ctk.CTkFont(size=56, weight="bold")
        )
        self.lbl_display.pack(pady=20)

        # Control Buttons
        btn_frame = ctk.CTkFrame(self.card, fg_color="transparent")
        btn_frame.pack(pady=(0, 30))

        self.btn_start = ctk.CTkButton(
            btn_frame,
            text="Start",
            font=ctk.CTkFont(size=16, weight="bold"),
            fg_color="#10B981",
            hover_color="#059669",
            width=130,
            height=45,
            command=self._toggle_start_pause
        )
        self.btn_start.pack(side="left", padx=10)

        self.btn_reset = ctk.CTkButton(
            btn_frame,
            text="Reset",
            font=ctk.CTkFont(size=16, weight="bold"),
            fg_color="gray",
            hover_color="gray40",
            width=130,
            height=45,
            command=self._reset
        )
        self.btn_reset.pack(side="left", padx=10)

        # Status / Toast label
        self.lbl_status = ctk.CTkLabel(self.card, text="", font=ctk.CTkFont(size=14, weight="bold"), text_color="#10B981")
        self.lbl_status.pack(pady=(0, 15))

    def _toggle_start_pause(self) -> None:
        self.lbl_status.configure(text="")
        if self.timer_service.is_running:
            self.timer_service.pause()
            self.btn_start.configure(text="Resume", fg_color="#3B82F6", hover_color="#2563EB")
            self._set_inputs_state("normal")
        else:
            if self.timer_service.remaining_sec <= 0:
                h = int(self.combo_h.get())
                m = int(self.combo_m.get())
                s = int(self.combo_s.get())
                total = self.timer_service.set_duration(h, m, s)
                if total <= 0:
                    self.lbl_status.configure(text="Please set a duration greater than zero.", text_color="#EF4444")
                    return

            started = self.timer_service.start()
            if started:
                self.btn_start.configure(text="Pause", fg_color="#EF4444", hover_color="#DC2626")
                self._set_inputs_state("disabled")

    def _reset(self) -> None:
        self.timer_service.reset()
        self.audio_service.stop()
        self.btn_start.configure(text="Start", fg_color="#10B981", hover_color="#059669")
        self._set_inputs_state("normal")
        self.lbl_status.configure(text="")

    def _set_inputs_state(self, state: str) -> None:
        self.combo_h.configure(state=state)
        self.combo_m.configure(state=state)
        self.combo_s.configure(state=state)

    def _on_timer_complete(self) -> None:
        self.btn_start.configure(text="Start", fg_color="#10B981", hover_color="#059669")
        self._set_inputs_state("normal")
        self.lbl_status.configure(text="🎉 Timer Complete!", text_color="#10B981")
        self.audio_service.play(self.settings.default_tone, loop=False)

    def _update_loop(self) -> None:
        if not self.winfo_exists():
            return

        h, m, s = self.timer_service.format_remaining()
        self.lbl_display.configure(text=f"{h:02d} : {m:02d} : {s:02d}")

        self.after(200, self._update_loop)
