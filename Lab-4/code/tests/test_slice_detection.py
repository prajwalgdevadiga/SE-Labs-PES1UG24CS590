"""Slice-detection checks for Task 1 - fast swipes must register.

Runs headless (no game window, no mouse):

    python tests/test_slice_detection.py

Every check feeds the engine a sequence of mouse positions, exactly as
pygame's MOUSEMOTION events would, and asserts what got sliced.
"""

import sys
import unittest

from _support import (FRUIT_X, FRUIT_Y, RADIUS, Fruit, leave_window, make_engine,
                      run, swipe)


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
        leave_window(engine)
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


if __name__ == "__main__":
    sys.exit(run(SliceDetection))
