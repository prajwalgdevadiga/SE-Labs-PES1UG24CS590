"""Sound checks for Task 4.

Runs headless (no game window, no audio device):

    python tests/test_sound.py

Two halves. The engine checks use a recording stand-in, so they assert what the
game asks for and when. The SoundBoard checks exercise the real thing against
SDL's dummy audio driver, including what happens when audio refuses to start.
"""

import array
import sys
import unittest

import pygame

from _support import (FRUIT_X, FRUIT_Y, RADIUS, WIDTH, HEIGHT, Fruit, GameEngine,
                      blank_screen, make_engine, press, run, swipe)

from game.sounds import SoundBoard


class EngineAsksForSounds(unittest.TestCase):

    def test_slicing_a_fruit_makes_a_noise(self):
        engine, _ = make_engine()
        swipe(engine, (150, FRUIT_Y), (550, FRUIT_Y))
        self.assertEqual(engine.sounds.played, ["slice"])

    def test_each_fruit_in_one_swipe_is_heard(self):
        engine, _ = make_engine()
        engine.fruits.append(Fruit(FRUIT_X + 120, FRUIT_Y, 0, 0, 0, radius=RADIUS))
        swipe(engine, (150, FRUIT_Y), (600, FRUIT_Y))
        self.assertEqual(engine.sounds.played, ["slice", "slice"])

    def test_a_bomb_sounds_different_from_a_fruit(self):
        engine, _ = make_engine(kind="bomb")
        swipe(engine, (150, FRUIT_Y), (550, FRUIT_Y))
        self.assertEqual(engine.sounds.played, ["bomb", "game_over"])

    def test_running_out_of_lives_only_plays_the_game_over_sound(self):
        engine, fruit = make_engine()
        engine.lives = 1
        fruit.y = engine.height + fruit.radius + 1  # already past the bottom
        engine.update()
        self.assertEqual(engine.sounds.played, ["game_over"])

    def test_missing_a_fruit_is_silent(self):
        engine, fruit = make_engine()
        engine.lives = 5
        fruit.y = engine.height + fruit.radius + 1
        engine.update()
        self.assertEqual(engine.sounds.played, [])

    def test_game_over_sound_plays_once_not_every_frame(self):
        """The screen can sit there for a minute; it must stay quiet."""
        engine, _ = make_engine(kind="bomb")
        swipe(engine, (150, FRUIT_Y), (550, FRUIT_Y))
        screen = blank_screen()
        for frame in range(600):  # ten seconds of staring at the screen
            swipe(engine, (frame % 700, FRUIT_Y))  # and waving the mouse about
            engine.update()
            engine.render(screen)
        self.assertEqual(engine.sounds.played.count("game_over"), 1)

    def test_each_new_game_gets_its_own_game_over_sound(self):
        engine, _ = make_engine()
        for _ in range(3):
            engine._end_game("You sliced a bomb")
            press(engine, pygame.K_m)
        self.assertEqual(engine.sounds.played.count("game_over"), 3)


class BoardSurvivesBadAudio(unittest.TestCase):

    def test_a_mixer_that_will_not_start_leaves_the_game_playable(self):
        """The whole point: flaky audio must not take the game down."""
        def refuse(*args, **kwargs):
            raise pygame.error("No available audio device")

        real_init = pygame.mixer.init
        pygame.mixer.init = refuse
        try:
            board = SoundBoard()
        finally:
            pygame.mixer.init = real_init

        self.assertFalse(board.enabled)
        board.play("slice")  # must not raise

        engine = GameEngine(WIDTH, HEIGHT, sounds=board)
        engine.fruits = [Fruit(FRUIT_X, FRUIT_Y, 0, 0, 0, radius=RADIUS)]
        swipe(engine, (150, FRUIT_Y), (550, FRUIT_Y))
        self.assertEqual(engine.score, 1, "game did not keep working without audio")

    def test_a_device_lost_mid_game_goes_quiet_instead_of_raising(self):
        board = SoundBoard()
        if not board.enabled:
            self.skipTest("no mixer available to lose")

        class Dead:
            def play(self):
                raise pygame.error("device disconnected")

        board._sounds["slice"] = Dead()
        board.play("slice")  # must not raise
        self.assertFalse(board.enabled)

    def test_an_unknown_name_is_ignored(self):
        board = SoundBoard()
        board.play("no such sound")  # must not raise


class GeneratedAudio(unittest.TestCase):
    """The real board, against SDL's dummy audio device."""

    @classmethod
    def setUpClass(cls):
        cls.board = SoundBoard()
        if not cls.board.enabled:
            raise unittest.SkipTest("mixer unavailable in this environment")

    def test_all_three_effects_are_built(self):
        self.assertEqual(set(self.board._sounds), {"slice", "bomb", "game_over"})

    def test_every_effect_is_audible_and_short(self):
        for name, sound in self.board._sounds.items():
            with self.subTest(sound=name):
                self.assertGreater(sound.get_length(), 0.05)
                self.assertLess(sound.get_length(), 1.5, "effect drags on")

    def test_the_three_effects_are_actually_different(self):
        raw = [sound.get_raw() for sound in self.board._sounds.values()]
        self.assertEqual(len(set(raw)), 3, "two effects are the same audio")

    def test_audio_is_loud_but_not_clipped(self):
        for name, sound in self.board._sounds.items():
            with self.subTest(sound=name):
                samples = array.array("h")
                samples.frombytes(sound.get_raw())
                peak = max(abs(s) for s in samples)
                self.assertGreater(peak, 3000, "effect is near silent")
                self.assertLess(peak, 32767, "effect is clipping")

    def test_effects_start_and_end_near_zero(self):
        """A waveform that starts loud clicks in the speakers."""
        for name, sound in self.board._sounds.items():
            with self.subTest(sound=name):
                samples = array.array("h")
                samples.frombytes(sound.get_raw())
                self.assertLess(abs(samples[0]), 1500)
                self.assertLess(abs(samples[-1]), 1500)

    def test_building_sounds_does_not_disturb_the_games_randomness(self):
        """Fruit must be thrown the same way whether or not audio started."""
        import random

        random.seed(99)
        before = [random.random() for _ in range(5)]
        random.seed(99)
        SoundBoard()
        after = [random.random() for _ in range(5)]
        self.assertEqual(before, after)


if __name__ == "__main__":
    sys.exit(run(EngineAsksForSounds, BoardSurvivesBadAudio, GeneratedAudio))
