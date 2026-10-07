"""Sound effects, generated in code - there are no audio files to ship.

Nothing in here is allowed to take the game down with it. If the mixer will
not start (no device, drivers playing up, audio already in use) the board
reports itself disabled and every play() is a no-op, so the game runs silently
instead of crashing.
"""

import array
import math
import random

import pygame

SAMPLE_RATE = 44100
PEAK = 32767  # loudest signed 16-bit sample

# Its own generator, so making the noise in these effects cannot shift the
# sequence the game uses to throw fruit.
_noise = random.Random(1234)


def _envelope(i, n, attack_frac=0.02, decay=5.0):
    """Quick fade in, exponential fade out - stops clicks at both ends."""
    attack = max(1, int(n * attack_frac))
    if i < attack:
        return i / attack
    return math.exp(-decay * (i - attack) / max(1, n - attack))


def _swish(duration=0.10, f0=700.0, f1=1500.0, noise=0.25):
    """Short bright rising sweep - the blade going through a fruit."""
    n = int(SAMPLE_RATE * duration)
    frames = []
    phase = 0.0
    for i in range(n):
        t = i / n
        phase += 2 * math.pi * (f0 + (f1 - f0) * t) / SAMPLE_RATE
        value = math.sin(phase) * (1 - noise) + _noise.uniform(-1, 1) * noise
        frames.append(value * _envelope(i, n))
    return frames


def _thud(duration=0.45, f0=180.0, f1=60.0):
    """Low, buzzy and falling, with grit on the front - hitting a bomb."""
    n = int(SAMPLE_RATE * duration)
    frames = []
    phase = 0.0
    for i in range(n):
        t = i / n
        phase += 2 * math.pi * (f0 + (f1 - f0) * t) / SAMPLE_RATE
        saw = 2 * ((phase / (2 * math.pi)) % 1.0) - 1
        grit = _noise.uniform(-1, 1) * 0.35 * math.exp(-12 * t)
        frames.append((saw * 0.7 + grit) * _envelope(i, n, decay=3.0))
    return frames


def _fall(notes=(392.0, 311.1, 233.1), note_duration=0.22):
    """Three notes walking downwards - the game over moment."""
    frames = []
    for freq in notes:
        n = int(SAMPLE_RATE * note_duration)
        phase = 0.0
        for i in range(n):
            phase += 2 * math.pi * freq / SAMPLE_RATE
            # A little second harmonic, so it is not a bare sine tone.
            value = math.sin(phase) * 0.8 + math.sin(2 * phase) * 0.2
            frames.append(value * _envelope(i, n, decay=4.0))
    return frames


def _to_sound(frames, channels):
    """Turn floats in [-1, 1] into a Sound the open mixer can play."""
    samples = array.array("h")
    for value in frames:
        sample = int(max(-1.0, min(1.0, value)) * PEAK)
        for _ in range(channels):  # the same signal in every channel
            samples.append(sample)
    return pygame.mixer.Sound(buffer=samples.tobytes())


class SoundBoard:
    """The game's three effects, built once at startup.

    `enabled` says whether any noise will actually come out; the game does not
    need to care either way.
    """

    RECIPES = {
        "slice": (_swish, 0.5),
        "bomb": (_thud, 0.7),
        "game_over": (_fall, 0.6),
    }

    def __init__(self):
        self.enabled = False
        self._sounds = {}
        self._build()

    def _build(self):
        try:
            # pygame.init() may already have opened the mixer in a format that
            # does not match what is generated here, so take it over.
            if pygame.mixer.get_init():
                pygame.mixer.quit()
            pygame.mixer.init(frequency=SAMPLE_RATE, size=-16, channels=1)

            opened = pygame.mixer.get_init()
            if not opened or opened[1] != -16:
                raise pygame.error(f"unusable mixer format: {opened}")
            channels = opened[2]

            for name, (recipe, volume) in self.RECIPES.items():
                sound = _to_sound(recipe(), channels)
                sound.set_volume(volume)
                self._sounds[name] = sound
            self.enabled = True
        except Exception as exc:  # audio failures come in many shapes
            # Deliberately broad: a missing device, a driver that refuses to
            # open, a format the build cannot do. None of it is worth a crash.
            print(f"Sound unavailable ({exc}) - playing without it.")
            self.enabled = False
            self._sounds = {}

    def play(self, name):
        if not self.enabled:
            return
        sound = self._sounds.get(name)
        if sound is None:
            return
        try:
            sound.play()
        except pygame.error:
            # Device went away mid-game (headphones unplugged, say). Go quiet
            # rather than throwing on every slice from here on.
            self.enabled = False
