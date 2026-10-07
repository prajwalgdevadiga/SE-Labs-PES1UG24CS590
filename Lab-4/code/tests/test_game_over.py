"""Game over screen checks for Task 2.

Runs headless (no game window, no mouse):

    python tests/test_game_over.py

The screen is asserted two ways: what text the engine puts on it, and what the
rendered pixels look like (dimmed, with the frozen game still showing through).
"""

import sys
import unittest

import pygame

from _support import (DARK_BLUE, FRUIT_X, FRUIT_Y, Fruit, blank_screen,
                      centred_texts, make_engine, press, run, swipe)


def rendered_frame(engine):
    """Render one frame onto a background-filled surface and hand it back."""
    screen = blank_screen()
    screen.fill(DARK_BLUE)
    engine.render(screen)
    return screen


class GameOverState(unittest.TestCase):

    def test_slicing_a_bomb_ends_the_game(self):
        engine, bomb = make_engine(kind="bomb")
        swipe(engine, (150, FRUIT_Y), (550, FRUIT_Y))
        self.assertTrue(engine.game_over)
        self.assertEqual(engine.game_over_reason, "You sliced a bomb")

    def test_running_out_of_lives_ends_the_game(self):
        engine, fruit = make_engine()
        engine.lives = 1
        fruit.y = engine.height + fruit.radius + 1  # already past the bottom
        engine.update()
        self.assertEqual(engine.lives, 0)
        self.assertTrue(engine.game_over)
        self.assertEqual(engine.game_over_reason, "You ran out of lives")

    def test_slicing_fruit_does_not_end_the_game(self):
        engine, fruit = make_engine()
        swipe(engine, (150, FRUIT_Y), (550, FRUIT_Y))
        self.assertFalse(engine.game_over)
        self.assertEqual(engine.game_over_reason, "")

    def test_play_freezes_once_the_game_is_over(self):
        """update() must leave the scene where it was, for the dim to sit over."""
        engine, _ = make_engine()
        engine.spawn_interval = 1  # would spawn every frame if still running
        engine._end_game("You sliced a bomb")
        moving = Fruit(100, 100, vx=5, vy=-5, gravity=0.35)
        engine.fruits = [moving]

        for _ in range(30):
            engine.update()

        self.assertEqual((moving.x, moving.y), (100, 100))
        self.assertEqual(len(engine.fruits), 1)

    def test_score_cannot_climb_after_the_game_is_over(self):
        """Swiping behind the screen must not move the number it is showing."""
        engine, fruit = make_engine()
        engine._end_game("You ran out of lives")
        swipe(engine, (150, FRUIT_Y), (550, FRUIT_Y))
        self.assertFalse(fruit.sliced)
        self.assertEqual(engine.score, 0)


class GameOverScreen(unittest.TestCase):

    def test_screen_shows_title_score_and_reason(self):
        engine, _ = make_engine()
        engine.score = 7
        engine._end_game("You sliced a bomb")
        texts = centred_texts(engine)
        self.assertIn("GAME OVER", texts)
        self.assertIn("Final Score: 7", texts)
        self.assertIn("You sliced a bomb", texts)

    def test_nothing_is_drawn_over_the_game_while_playing(self):
        engine, _ = make_engine()
        texts = centred_texts(engine)  # the HUD difficulty label is centred too
        self.assertNotIn("GAME OVER", texts)
        self.assertNotIn("Play again:", texts)
        background = rendered_frame(engine).get_at((10, 560))
        self.assertEqual(background[:3], DARK_BLUE)

    def test_screen_dims_the_frame_behind_it(self):
        engine, _ = make_engine()
        before = rendered_frame(engine).get_at((10, 560))
        engine._end_game("You sliced a bomb")
        after = rendered_frame(engine).get_at((10, 560))
        self.assertLess(sum(after[:3]), sum(before[:3]), "frame was not dimmed")
        self.assertGreater(sum(after[:3]), 0, "frame was blacked out, not dimmed")

    def test_game_is_still_visible_through_the_dim(self):
        """The fruit must still be distinguishable from the dimmed background."""
        engine, fruit = make_engine()
        engine._end_game("You sliced a bomb")
        frame = rendered_frame(engine)
        on_fruit = frame.get_at((FRUIT_X, FRUIT_Y))
        empty = frame.get_at((10, 560))
        self.assertNotEqual(on_fruit[:3], empty[:3])


class GameOverInput(unittest.TestCase):

    def test_escape_asks_the_loop_to_close(self):
        engine, _ = make_engine()
        engine._end_game("You sliced a bomb")
        press(engine, pygame.K_ESCAPE)
        self.assertTrue(engine.should_quit)

    def test_q_also_quits(self):
        engine, _ = make_engine()
        engine._end_game("You sliced a bomb")
        press(engine, pygame.K_q)
        self.assertTrue(engine.should_quit)

    def test_other_keys_do_not_quit(self):
        """Only Esc and Q close the window; the replay keys are tested in
        test_replay.py."""
        engine, _ = make_engine()
        engine._end_game("You sliced a bomb")
        for key in (pygame.K_SPACE, pygame.K_r, pygame.K_1, pygame.K_RETURN):
            press(engine, key)
        self.assertFalse(engine.should_quit)

    def test_escape_during_play_does_not_quit(self):
        engine, _ = make_engine()
        press(engine, pygame.K_ESCAPE)
        self.assertFalse(engine.should_quit)

    def test_the_loop_keeps_running_and_stays_responsive(self):
        """No blocking wait: frames keep going and keys still land.

        Stands in for the real main loop - if the engine blocked anywhere, this
        check would hang rather than fail.
        """
        engine, _ = make_engine()
        engine._end_game("You sliced a bomb")
        screen = blank_screen()

        frames = 0
        for frame in range(120):
            engine.handle_event(pygame.event.Event(pygame.QUIT))  # must not crash
            swipe(engine, (frame * 3, 200))
            if frame == 60:
                press(engine, pygame.K_ESCAPE)
            engine.update()
            engine.render(screen)
            frames += 1
            if engine.should_quit:
                break

        # Esc goes in on the 61st pass (frame == 60) and is seen in that same pass.
        self.assertEqual(frames, 61, "Esc was not acted on straight away")


if __name__ == "__main__":
    sys.exit(run(GameOverState, GameOverScreen, GameOverInput))
