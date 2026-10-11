import array
import math

import pygame

VOLUME = 0.4  # moderate overall level, 0.0 - 1.0


def _tone(freq_start, freq_end, duration, sample_rate, channels, volume=VOLUME):
    """Build a 16-bit sine sweep from freq_start to freq_end with a fade-out."""
    count = int(sample_rate * duration)
    samples = array.array("h")
    phase = 0.0
    for i in range(count):
        t = i / count
        phase += 2 * math.pi * (freq_start + (freq_end - freq_start) * t) / sample_rate
        envelope = min(1.0, i / 80) * (1.0 - t) ** 1.5  # short attack, smooth decay
        value = int(32767 * volume * envelope * math.sin(phase))
        samples.extend([value] * channels)
    return pygame.mixer.Sound(buffer=samples.tobytes())


class SoundBank:
    """Synthesised sound effects. Silently does nothing if audio is unavailable."""

    def __init__(self):
        self._sounds = {}
        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init()
            rate, fmt, channels = pygame.mixer.get_init()
            if fmt != -16:  # only signed 16-bit output is generated here
                return
            self._sounds = {
                "jump": _tone(380, 760, 0.12, rate, channels),
                "score": _tone(1320, 1320, 0.10, rate, channels, VOLUME * 0.8),
                "game_over": _tone(440, 110, 0.70, rate, channels),
            }
        except Exception:
            self._sounds = {}

    def play(self, name):
        sound = self._sounds.get(name)
        if sound is not None:
            try:
                sound.play()
            except Exception:
                pass
