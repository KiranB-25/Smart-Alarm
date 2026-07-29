import math
import os
import struct
import wave
from typing import List, Tuple
from src.utils.logger import setup_logger

logger = setup_logger("ToneGenerator")

SAMPLE_RATE = 44100


def create_sine_wave(freq: float, duration: float, volume: float = 0.5) -> List[float]:
    num_samples = int(SAMPLE_RATE * duration)
    samples = []
    for i in range(num_samples):
        t = i / SAMPLE_RATE
        val = volume * math.sin(2 * math.pi * freq * t)
        samples.append(val)
    return samples


def create_square_wave(freq: float, duration: float, volume: float = 0.3) -> List[float]:
    num_samples = int(SAMPLE_RATE * duration)
    samples = []
    period = SAMPLE_RATE / freq
    for i in range(num_samples):
        val = volume if (i % period) < (period / 2) else -volume
        samples.append(val)
    return samples


def create_triangle_wave(freq: float, duration: float, volume: float = 0.5) -> List[float]:
    num_samples = int(SAMPLE_RATE * duration)
    samples = []
    period = SAMPLE_RATE / freq
    for i in range(num_samples):
        phase = (i % period) / period
        val = volume * (4 * abs(phase - 0.5) - 1)
        samples.append(val)
    return samples


def apply_envelope(samples: List[float], attack: float = 0.02, decay: float = 0.05) -> List[float]:
    n = len(samples)
    attack_samples = int(SAMPLE_RATE * attack)
    decay_samples = int(SAMPLE_RATE * decay)

    result = list(samples)
    for i in range(n):
        env = 1.0
        if i < attack_samples and attack_samples > 0:
            env = i / attack_samples
        elif i >= (n - decay_samples) and decay_samples > 0:
            env = (n - i) / decay_samples
        result[i] *= env
    return result


def write_wav(file_path: str, samples: List[float]) -> None:
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with wave.open(file_path, "wb") as wav_file:
        wav_file.setnchannels(1)  # Mono
        wav_file.setsampwidth(2)  # 16-bit
        wav_file.setframerate(SAMPLE_RATE)
        
        packed_data = bytearray()
        for sample in samples:
            clamped = max(-1.0, min(1.0, sample))
            int_val = int(clamped * 32767)
            packed_data.extend(struct.pack("<h", int_val))
            
        wav_file.writeframes(packed_data)


def generate_tone(tone_id: str, output_path: str) -> None:
    samples: List[float] = []

    if tone_id == "classic-bell":
        # Warm bell chime sequence (784Hz, 988Hz, 784Hz)
        notes = [(784.0, 0.28), (988.0, 0.28), (784.0, 0.4)]
        for freq, dur in notes:
            n_samples = apply_envelope(create_sine_wave(freq, dur, 0.6), attack=0.01, decay=dur * 0.7)
            samples.extend(n_samples)

    elif tone_id == "digital-alarm":
        # Classic digital alarm beep (880Hz, 880Hz, 1047Hz)
        notes = [(880.0, 0.12), (880.0, 0.12), (1047.0, 0.25)]
        for freq, dur in notes:
            n_samples = apply_envelope(create_square_wave(freq, dur, 0.35), attack=0.005, decay=0.02)
            samples.extend(n_samples)
            # silence gap
            samples.extend([0.0] * int(SAMPLE_RATE * 0.05))

    elif tone_id == "morning-birds":
        # Chirping frequency sweep
        dur = 0.22
        num_samples = int(SAMPLE_RATE * dur)
        for i in range(num_samples):
            t = i / SAMPLE_RATE
            freq = 1200.0 + (1000.0 * (t / dur))
            val = 0.4 * math.sin(2 * math.pi * freq * t)
            samples.append(val)
        samples = apply_envelope(samples, attack=0.02, decay=0.05)
        # Second chirp
        samples2 = []
        for i in range(num_samples):
            t = i / SAMPLE_RATE
            freq = 1800.0 + (1000.0 * (t / dur))
            val = 0.4 * math.sin(2 * math.pi * freq * t)
            samples2.append(val)
        samples.extend(apply_envelope(samples2, attack=0.02, decay=0.05))

    elif tone_id == "soft-piano":
        # Harmonic piano chords C5 - E5 - G5
        notes = [(523.25, 0.4), (659.25, 0.4), (783.99, 0.6)]
        for freq, dur in notes:
            n_samples = apply_envelope(create_triangle_wave(freq, dur, 0.5), attack=0.02, decay=dur * 0.6)
            samples.extend(n_samples)

    elif tone_id == "nature":
        # Soft gentle breeze/nature melody (392Hz, 493.88Hz)
        notes = [(392.0, 0.5), (493.88, 0.6)]
        for freq, dur in notes:
            n_samples = apply_envelope(create_sine_wave(freq, dur, 0.4), attack=0.05, decay=dur * 0.5)
            samples.extend(n_samples)

    elif tone_id == "electronic":
        # Electronic synth staccato (440, 660, 880, 660)
        notes = [(440.0, 0.1), (660.0, 0.1), (880.0, 0.1), (660.0, 0.2)]
        for freq, dur in notes:
            n_samples = apply_envelope(create_square_wave(freq, dur, 0.25), attack=0.005, decay=0.02)
            samples.extend(n_samples)

    elif tone_id == "gentle-chime":
        # High crystal chimes (1046.5Hz, 1318.5Hz)
        notes = [(1046.5, 0.5), (1318.5, 0.7)]
        for freq, dur in notes:
            n_samples = apply_envelope(create_sine_wave(freq, dur, 0.5), attack=0.01, decay=dur * 0.7)
            samples.extend(n_samples)

    elif tone_id == "sunrise":
        # Sunrise warmth C4, E4, G4, C5
        notes = [(261.63, 0.35), (329.63, 0.35), (392.0, 0.35), (523.25, 0.5)]
        for freq, dur in notes:
            n_samples = apply_envelope(create_triangle_wave(freq, dur, 0.45), attack=0.03, decay=dur * 0.5)
            samples.extend(n_samples)

    else:
        # Fallback sine
        samples = apply_envelope(create_sine_wave(440.0, 0.5, 0.5))

    write_wav(output_path, samples)
    logger.info(f"Generated tone asset '{tone_id}' at '{output_path}'.")


def ensure_all_tones_exist(audio_dir: str = "assets/audio") -> None:
    tone_ids = [
        "classic-bell",
        "digital-alarm",
        "morning-birds",
        "soft-piano",
        "nature",
        "electronic",
        "gentle-chime",
        "sunrise",
    ]
    for tid in tone_ids:
        path = os.path.join(audio_dir, f"{tid}.wav")
        if not os.path.exists(path):
            generate_tone(tid, path)
