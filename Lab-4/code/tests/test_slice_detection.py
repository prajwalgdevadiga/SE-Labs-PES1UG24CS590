"""Slice-detection checks for Task 1 - fast swipes must register.

Runs headless (no game window, no mouse), so it can be run on its own:

    python tests/test_slice_detection.py

Every check feeds the engine a sequence of mouse positions, exactly as
pygame's MOUSEMOTION events would, and asserts what got sliced.
"""

import os
import sys
import unittest

# Pick the dummy SDL backends so pygame starts without a display or audio
# device, and make the project importable however this file is launched.
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pygame

from game.fruit import Fruit
from game.game_engine import GameEngine

WIDTH, HEIGHT = 700, 600
FRUIT_X, FRUIT_Y = 350, 300  # where the test fruit is parked
RADIUS = 28


def make_engine(kind="fruit"):
    """An engine holding one motionless fruit at (350, 300) and nothing else."""
    engine = GameEngine(WIDTH, HEIGHT)
    engine.spawn_interval = 10 ** 9  # don't let update() spawn during a test
    fruit = Fruit(FRUIT_X, FRUIT_Y, vx=0, vy=0, gravity=0, radius=RADIUS, kind=kind)
    engine.fruits = [fruit]
    return engine, fruit


def swipe(engine, *positions):
    """Feed positions in as real MOUSEMOTION events, one per frame."""
    for pos in positions:
        engine.handle_event(pygame.event.Event(pygame.MOUSEMOTION, pos=pos))


class SliceDetection(unittest.TestCase):

    def test_slow_move_onto_fruit_still_slices(self):
        """The behaviour that always worked must keep working."""
        engine, fruit = make_engine()
        swipe(engine, (FRUIT_X - 10, FRUIT_Y), (FRUIT_X, FRUIT_Y))
        self.assertTrue(fruit.sliced)
        self.assertEqual(engine.score, 1)

    def test_fast_swipe_straddling_fruit_slices(self):
        """The bug: two samples either side, neither of them inside the circle."""
        engine, fruit = make_engine()
        swipe(engine, (150, FRUIT_Y), (550, FRUIT_Y))
        self.assertFalse(engine.fruits[0].contains_point(150, FRUIT_Y))
        self.assertFalse(engine.fruits[0].contains_point(550, FRUIT_Y))
        self.assertTrue(fruit.sliced, "fast swipe through the centre did not slice")
        self.assertEqual(engine.score, 1)

    def test_fast_diagonal_swipe_slices(self):
        """Same thing off-axis, corner to corner through the fruit."""
        engine, fruit = make_engine()
        swipe(engine, (FRUIT_X - 200, FRUIT_Y - 200), (FRUIT_X + 200, FRUIT_Y + 200))
        self.assertTrue(fruit.sliced)

    def test_fast_swipe_grazing_the_edge_slices(self):
        """Just inside the radius still counts as a cut."""
        engine, fruit = make_engine()
        swipe(engine, (150, FRUIT_Y - RADIUS + 2), (550, FRUIT_Y - RADIUS + 2))
        self.assertTrue(fruit.sliced)

    def test_fast_swipe_clear_of_fruit_does_not_slice(self):
        """A swipe that misses must not be turned into a hit."""
        engine, fruit = make_engine()
        swipe(engine, (150, FRUIT_Y - RADIUS - 5), (550, FRUIT_Y - RADIUS - 5))
        self.assertFalse(fruit.sliced)
        self.assertEqual(engine.score, 0)

    def test_swipe_stopping_short_does_not_slice(self):
        """Only the segment counts, not the infinite line it lies on.

        (150,300) -> (250,300) points straight at the fruit but stops 100px
        short of it; extending the line would wrongly hit.
        """
        engine, fruit = make_engine()
        swipe(engine, (150, FRUIT_Y), (250, FRUIT_Y))
        self.assertFalse(fruit.sliced)

    def test_fast_swipe_through_bomb_ends_game(self):
        engine, bomb = make_engine(kind="bomb")
        swipe(engine, (150, FRUIT_Y), (550, FRUIT_Y))
        self.assertTrue(bomb.sliced)
        self.assertTrue(engine.game_over)
        self.assertEqual(engine.score, 0)

    def test_one_swipe_through_two_fruit_scores_two(self):
        engine, first = make_engine()
        second = Fruit(FRUIT_X + 120, FRUIT_Y, vx=0, vy=0, gravity=0, radius=RADIUS)
        engine.fruits.append(second)
        swipe(engine, (150, FRUIT_Y), (600, FRUIT_Y))
        self.assertTrue(first.sliced and second.sliced)
        self.assertEqual(engine.score, 2)

    def test_fruit_is_not_scored_twice(self):
        engine, fruit = make_engine()
        swipe(engine, (150, FRUIT_Y), (550, FRUIT_Y), (150, FRUIT_Y))
        self.assertEqual(engine.score, 1)

    def test_pointer_leaving_the_window_breaks_the_blade(self):
        """Re-entering elsewhere must not sweep a segment across the screen."""
        engine, fruit = make_engine()
        swipe(engine, (150, FRUIT_Y))
        engine.handle_event(pygame.event.Event(pygame.WINDOWLEAVE))
        swipe(engine, (550, FRUIT_Y))
        self.assertFalse(fruit.sliced)
        self.assertEqual(engine.score, 0)

    def test_first_sample_after_entering_is_a_point_test(self):
        """A single sample landing on the fruit slices with no history."""
        engine, fruit = make_engine()
        swipe(engine, (FRUIT_X, FRUIT_Y))
        self.assertTrue(fruit.sliced)

    def test_trail_is_still_capped(self):
        """Rendering relies on the trail staying short."""
        engine, _ = make_engine()
        swipe(engine, *[(x, 10) for x in range(0, 400, 10)])
        self.assertLessEqual(len(engine.trail), 15)


def main():
    pygame.init()  # GameEngine builds a font, so pygame must be initialised
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(SliceDetection)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    pygame.quit()

    total = result.testsRun
    bad = len(result.failures) + len(result.errors)
    print()
    if bad:
        print(f"FAIL - {bad} of {total} checks failed")
    else:
        print(f"PASS - all {total} checks passed")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
