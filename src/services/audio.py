import os
import threading
from typing import Optional
from src.utils.tone_generator import ensure_all_tones_exist
from src.utils.logger import setup_logger

logger = setup_logger("AudioService")


class AudioService:
    def __init__(self, audio_dir: str = "assets/audio", initial_volume: float = 0.7):
        self.audio_dir = audio_dir
        self.volume = max(0.0, min(1.0, float(initial_volume)))
        self._mixer_initialized = False
        self._active_sound = None
        self._active_channel = None
        self._current_tone_id: Optional[str] = None
        self._lock = threading.Lock()

        # Pre-generate WAV files if missing
        ensure_all_tones_exist(self.audio_dir)
        self._init_mixer()

    def _init_mixer(self) -> None:
        try:
            import pygame
            if not pygame.mixer.get_init():
                pygame.mixer.init(frequency=44100, size=-16, channels=1, buffer=1024)
            self._mixer_initialized = True
            logger.info("Pygame mixer initialized successfully.")
        except Exception as e:
            logger.error(f"Failed to initialize pygame mixer: {e}", exc_info=True)
            self._mixer_initialized = False

    def set_volume(self, volume: float) -> None:
        with self._lock:
            self.volume = max(0.0, min(1.0, float(volume)))
            if self._active_channel and self._mixer_initialized:
                self._active_channel.set_volume(self.volume)
            logger.info(f"Audio volume set to {int(self.volume * 100)}%.")

    def play(self, tone_id: str, loop: bool = True) -> bool:
        with self._lock:
            if not self._mixer_initialized:
                self._init_mixer()
                if not self._mixer_initialized:
                    logger.warning("Cannot play audio: mixer not initialized.")
                    return False

            wav_path = os.path.join(self.audio_dir, f"{tone_id}.wav")
            if not os.path.exists(wav_path):
                wav_path = os.path.join(self.audio_dir, "classic-bell.wav")

            try:
                import pygame
                self._stop_unlocked()
                sound = pygame.mixer.Sound(wav_path)
                channel = sound.play(loops=-1 if loop else 0)
                if channel:
                    channel.set_volume(self.volume)
                self._active_sound = sound
                self._active_channel = channel
                self._current_tone_id = tone_id
                logger.info(f"Playing ringtone '{tone_id}' (loop={loop}).")
                return True
            except Exception as e:
                logger.error(f"Error playing sound '{tone_id}': {e}", exc_info=True)
                return False

    def _stop_unlocked(self) -> None:
        if self._active_channel:
            try:
                self._active_channel.stop()
            except Exception:
                pass
        self._active_sound = None
        self._active_channel = None
        self._current_tone_id = None

    def stop(self) -> None:
        with self._lock:
            self._stop_unlocked()
            logger.info("Audio playback stopped.")

    def is_playing(self) -> bool:
        with self._lock:
            return self._active_channel is not None and self._active_channel.get_busy()
