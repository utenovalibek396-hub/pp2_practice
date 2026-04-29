"""
sound.py — Procedurally generated sound effects (no external audio files).
Uses numpy to synthesise waveforms and pygame.sndarray to play them.

Sounds:
  engine   — continuous low rumble (looped), pitch rises with speed
  coin     — short bright ding
  powerup  — ascending sweep
  crash    — burst of noise
  shield   — low thud / deflection
  nitro    — whoosh
  bump     — dull thud
"""

import pygame
import numpy as np

_RATE = 44_100   # samples per second
_CHANNELS = 1    # mono


def _make_sound(samples: np.ndarray) -> pygame.mixer.Sound:
    """Convert a float32 array (range -1..1) to a pygame Sound."""
    samples = np.clip(samples, -1.0, 1.0)
    buf = (samples * 32767).astype(np.int16)
    if _CHANNELS == 1:
        buf = np.column_stack([buf, buf])   # pygame needs stereo
    return pygame.sndarray.make_sound(buf)


def _t(duration: float) -> np.ndarray:
    return np.linspace(0, duration, int(_RATE * duration), endpoint=False)


# ── individual synthesisers ───────────────────

def _synth_engine(base_freq=60.0, duration=0.5) -> pygame.mixer.Sound:
    """Low rumble with harmonics — used as looped engine sound."""
    t = _t(duration)
    wave = (
        0.50 * np.sin(2 * np.pi * base_freq * t) +
        0.25 * np.sin(2 * np.pi * base_freq * 2 * t) +
        0.15 * np.sin(2 * np.pi * base_freq * 3 * t) +
        0.10 * np.random.uniform(-1, 1, len(t))
    )
    # gentle amplitude envelope (avoid click at loop boundaries)
    env = np.ones(len(t))
    fade = int(_RATE * 0.02)
    env[:fade]  = np.linspace(0, 1, fade)
    env[-fade:] = np.linspace(1, 0, fade)
    return _make_sound(wave * env * 0.4)


def _synth_coin() -> pygame.mixer.Sound:
    t = _t(0.18)
    freq = 880 + 440 * np.exp(-12 * t)
    wave = np.sin(2 * np.pi * freq * t)
    env  = np.exp(-18 * t)
    return _make_sound(wave * env * 0.7)


def _synth_powerup() -> pygame.mixer.Sound:
    t = _t(0.35)
    freq = 300 + 700 * (t / 0.35) ** 1.5
    wave = np.sin(2 * np.pi * freq * t)
    env  = np.exp(-3 * t)
    return _make_sound(wave * env * 0.6)


def _synth_crash() -> pygame.mixer.Sound:
    t = _t(0.45)
    noise = np.random.uniform(-1, 1, len(t))
    env   = np.exp(-8 * t)
    thud  = 0.6 * np.sin(2 * np.pi * 55 * t) * np.exp(-20 * t)
    return _make_sound((noise * env * 0.8 + thud))


def _synth_shield() -> pygame.mixer.Sound:
    t = _t(0.25)
    freq = 220 + 80 * np.sin(2 * np.pi * 12 * t)
    wave = np.sin(2 * np.pi * freq * t)
    env  = np.exp(-10 * t)
    return _make_sound(wave * env * 0.65)


def _synth_nitro() -> pygame.mixer.Sound:
    t = _t(0.3)
    noise = np.random.uniform(-1, 1, len(t))
    sweep = np.sin(2 * np.pi * (200 + 600 * t / 0.3) * t)
    env   = np.exp(-4 * t)
    return _make_sound((0.5 * noise + 0.5 * sweep) * env * 0.7)


def _synth_bump() -> pygame.mixer.Sound:
    t = _t(0.2)
    wave = np.sin(2 * np.pi * 80 * t) + 0.3 * np.random.uniform(-1, 1, len(t))
    env  = np.exp(-25 * t)
    return _make_sound(wave * env * 0.8)


# ─────────────────────────────────────────────
#  SoundManager — singleton-like, created once per game session
# ─────────────────────────────────────────────
class SoundManager:
    def __init__(self, enabled: bool = True):
        self.enabled = enabled
        self._engine_channel = None
        self._sounds = {}
        if not enabled:
            return
        try:
            pygame.mixer.pre_init(_RATE, -16, 2, 512)
            pygame.mixer.init()
            self._sounds = {
                "coin":    _synth_coin(),
                "powerup": _synth_powerup(),
                "crash":   _synth_crash(),
                "shield":  _synth_shield(),
                "nitro":   _synth_nitro(),
                "bump":    _synth_bump(),
            }
            # Engine sound is looped on a dedicated channel
            self._engine_snd = _synth_engine(base_freq=65, duration=0.4)
            self._engine_channel = pygame.mixer.find_channel(True)
            self._engine_channel.set_volume(0.35)
        except Exception as e:
            print(f"[SoundManager] init failed: {e}")
            self.enabled = False

    # ── public API ───────────────────────────

    def start_engine(self):
        if not self.enabled or self._engine_channel is None:
            return
        self._engine_channel.play(self._engine_snd, loops=-1)

    def stop_engine(self):
        if self._engine_channel:
            self._engine_channel.stop()

    def set_engine_pitch(self, speed_factor: float):
        """Vary engine volume slightly with speed (true pitch-shift needs more code)."""
        if not self.enabled or self._engine_channel is None:
            return
        vol = min(0.6, 0.25 + speed_factor * 0.06)
        self._engine_channel.set_volume(vol)

    def play(self, name: str):
        if not self.enabled:
            return
        snd = self._sounds.get(name)
        if snd:
            snd.play()

    def stop_all(self):
        if self.enabled:
            pygame.mixer.stop()