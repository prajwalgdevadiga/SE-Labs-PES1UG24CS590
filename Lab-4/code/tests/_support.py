"""Shared setup for the headless game tests.

Importing this picks dummy SDL backends, so pygame starts with no display and
no audio device, and puts the project on sys.path however the tests are run.
"""

import os
import sys
import unittest

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

TESTS_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(TESTS_DIR)
for _path in (PROJECT_DIR, TESTS_DIR):
    if _path not in sys.path:
        sys.path.insert(0, _path)

import pygame  # noqa: E402  (must follow the SDL_* settings above)

from game.fruit import Fruit  # noqa: E402
from game.game_engine import GameEngine  # noqa: E402

WIDTH, HEIGHT = 700, 600
DARK_BLUE = (20, 25, 45)  # the background main.py fills with
FRUIT_X, FRUIT_Y = 350, 300  # where the test fruit is parked
RADIUS = 28


class Recorder:
    """Stands in for the SoundBoard and remembers what was asked for.

    Tests inject this so they never touch the real mixer, and so the game is
    checked against the sound interface rather than against audio coming out.
    """

    enabled = True

    def __init__(self):
        self.played = []

    def play(self, name):
        self.played.append(name)


def make_engine(kind="fruit", difficulty=None):
    """An engine holding one motionless fruit at (350, 300) and nothing else."""
    engine = GameEngine(WIDTH, HEIGHT, sounds=Recorder())
    if difficulty:
        engine.start_game(difficulty)
    engine.spawn_interval = 10 ** 9  # don't let update() spawn during a test
    fruit = Fruit(FRUIT_X, FRUIT_Y, vx=0, vy=0, gravity=0, radius=RADIUS, kind=kind)
    engine.fruits = [fruit]
    return engine, fruit


def swipe(engine, *positions):
    """Feed positions in as real MOUSEMOTION events, one per frame."""
    for pos in positions:
        engine.handle_event(pygame.event.Event(pygame.MOUSEMOTION, pos=pos))


def press(engine, key):
    """Feed one key press in as a real KEYDOWN event."""
    engine.handle_event(pygame.event.Event(pygame.KEYDOWN, key=key))


def leave_window(engine):
    """Feed in the event pygame sends when the pointer leaves the window."""
    engine.handle_event(pygame.event.Event(pygame.WINDOWLEAVE))


def blank_screen():
    """An off-screen surface to render into, standing in for the window."""
    return pygame.Surface((WIDTH, HEIGHT))


def centred_texts(engine):
    """The centred strings one rendered frame would show, captured not drawn."""
    texts = []
    engine._blit_centered = lambda screen, font, text, color, y: texts.append(text)
    engine.render(blank_screen())
    return texts


def run(*test_cases):
    """Run the given TestCases and print a single PASS/FAIL line."""
    pygame.init()  # GameEngine builds fonts, so pygame must be initialised
    suite = unittest.TestSuite(
        unittest.defaultTestLoader.loadTestsFromTestCase(case) for case in test_cases)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    pygame.quit()

    bad = len(result.failures) + len(result.errors)
    print()
    if bad:
        print(f"FAIL - {bad} of {result.testsRun} checks failed")
    else:
        print(f"PASS - all {result.testsRun} checks passed")
    return 1 if bad else 0
