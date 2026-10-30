"""Short, synthesized sound effects; no sound assets are required."""

import array
import math
import random

import pygame


class SoundEffects:
    def __init__(self):
        self.enabled = True
        self._sounds = {}
        self._ready = False
        self._siren_channel = None

    def _ensure_ready(self):
        if self._ready:
            return True
        if not pygame.mixer.get_init():
            pygame.mixer.init(frequency=22050, size=-16, channels=1, buffer=512)
        rate = pygame.mixer.get_init()[0]
        self._sounds = {
            "lane": self._make_tone(680, 350, 0.095, 0.15, rate),
            "accelerate": self._make_tone(230, 620, 0.14, 0.2, rate),
            "brake": self._make_tone(400, 170, 0.16, 0.18, rate),
            "restart": self._make_tone(300, 760, 0.22, 0.18, rate),
            "pickup": self._make_tone(780, 1240, 0.16, 0.2, rate),
            "nitro": self._make_tone(170, 920, 0.32, 0.24, rate),
            "near_miss": self._make_tone(980, 1480, 0.11, 0.16, rate),
            "crash": self._make_crash(0.38, 0.28, rate),
            "siren": self._make_siren(1.2, 0.13, rate),
        }
        self._ready = True
        return True

    @staticmethod
    def _make_tone(start_hz, end_hz, duration, volume, sample_rate):
        samples = array.array("h")
        count = round(duration * sample_rate)
        phase = 0.0
        for index in range(count):
            progress = index / max(1, count - 1)
            frequency = start_hz + (end_hz - start_hz) * progress
            phase += 2 * math.pi * frequency / sample_rate
            envelope = min(1.0, progress * 18) * (1.0 - progress) ** 1.7
            samples.append(round(math.sin(phase) * envelope * volume * 32767))
        return pygame.mixer.Sound(buffer=samples.tobytes())

    @staticmethod
    def _make_crash(duration, volume, sample_rate):
        samples = array.array("h")
        count = round(duration * sample_rate)
        for index in range(count):
            progress = index / max(1, count - 1)
            envelope = (1.0 - progress) ** 2.2
            noise = random.uniform(-1.0, 1.0)
            low_rumble = math.sin(index * 2 * math.pi * 72 / sample_rate) * 0.42
            samples.append(round((noise * 0.58 + low_rumble) * envelope * volume * 32767))
        return pygame.mixer.Sound(buffer=samples.tobytes())

    def play(self, name):
        if not self.enabled:
            return
        if self._ensure_ready():
            sound = self._sounds.get(name)
            if sound:
                sound.play()

    def toggle(self):
        self.enabled = not self.enabled
        if not self.enabled:
            self.stop_siren()
        return self.enabled

    def start_siren(self):
        if self.enabled and self._ensure_ready() and self._siren_channel is None:
            self._siren_channel = self._sounds["siren"].play(loops=-1)

    def stop_siren(self):
        if self._siren_channel is not None:
            self._siren_channel.stop()
            self._siren_channel = None

    @staticmethod
    def _make_siren(duration, volume, sample_rate):
        samples = array.array("h")
        count = round(duration * sample_rate)
        phase = 0.0
        for index in range(count):
            progress = index / max(1, count - 1)
            sweep = (1 - math.cos(progress * 2 * math.pi)) / 2
            frequency = 620 + sweep * 420
            phase += 2 * math.pi * frequency / sample_rate
            samples.append(round(math.sin(phase) * volume * 32767))
        return pygame.mixer.Sound(buffer=samples.tobytes())
