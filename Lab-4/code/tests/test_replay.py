"""Replay and difficulty checks for Task 3.

Runs headless (no game window, no mouse):

    python tests/test_replay.py

The difficulty presets are checked by playing with them, not just by reading
the table, and the replay checks are mostly about what must NOT survive a
restart.
"""

import random
import sys
import unittest

import pygame

from _support import (FRUIT_X, FRUIT_Y, HEIGHT, RADIUS, WIDTH, Fruit, GameEngine,
                      blank_screen, make_engine, press, run, swipe)

from game.game_engine import DIFFICULTIES


def play_frames(difficulty, frames=6000, seed=5):
    """Run a game of the given difficulty and report what it threw up."""
    random.seed(seed)
    engine = GameEngine(WIDTH, HEIGHT, difficulty)
    engine.lives = 10 ** 6  # keep it running; we only care about the spawns
    spawned = []
    throw = engine.spawn_fruit

    def record():
        throw()
        spawned.append(engine.fruits[-1].kind)

    engine.spawn_fruit = record
    for _ in range(frames):
        engine.update()
    return spawned


class DifficultyPresets(unittest.TestCase):

    def test_the_levels_are_ordered(self):
        """Each step up must move every dial the harder way."""
        easy, medium, hard = (DIFFICULTIES[name] for name in ("easy", "medium", "hard"))
        self.assertGreater(easy["spawn_interval"], medium["spawn_interval"])
        self.assertGreater(medium["spawn_interval"], hard["spawn_interval"])
        self.assertLess(easy["bomb_chance"], medium["bomb_chance"])
        self.assertLess(medium["bomb_chance"], hard["bomb_chance"])
        self.assertGreater(easy["lives"], medium["lives"])
        self.assertGreater(medium["lives"], hard["lives"])
        self.assertLess(easy["speed_scale"], medium["speed_scale"])
        self.assertLess(medium["speed_scale"], hard["speed_scale"])

    def test_choosing_a_level_applies_all_of_its_settings(self):
        for name, settings in DIFFICULTIES.items():
            with self.subTest(difficulty=name):
                engine = GameEngine(WIDTH, HEIGHT)
                engine.start_game(name)
                self.assertEqual(engine.difficulty, name)
                self.assertEqual(engine.spawn_interval, settings["spawn_interval"])
                self.assertEqual(engine.bomb_chance, settings["bomb_chance"])
                self.assertEqual(engine.speed_scale, settings["speed_scale"])
                self.assertEqual(engine.lives, settings["lives"])

    def test_hard_throws_more_fruit_than_easy(self):
        self.assertGreater(len(play_frames("hard")), len(play_frames("easy")) * 2)

    def test_hard_throws_a_bigger_share_of_bombs(self):
        def bomb_share(difficulty):
            spawned = play_frames(difficulty)
            return spawned.count("bomb") / len(spawned)

        self.assertGreater(bomb_share("hard"), bomb_share("easy") * 1.5)

    def test_unknown_difficulty_is_rejected(self):
        """Better a clear error than silently playing on the old settings."""
        engine, _ = make_engine()
        with self.assertRaises(KeyError):
            engine.start_game("impossible")


class ReplayWipesTheLastGame(unittest.TestCase):

    def setUp(self):
        """A finished game with plenty of mess left in it."""
        self.engine, self.fruit = make_engine()
        swipe(self.engine, (150, FRUIT_Y), (550, FRUIT_Y))  # score 1, trail, blade
        self.engine.score = 9
        self.engine.lives = 1
        self.engine._spawn_timer = 40
        self.engine.fruits.append(Fruit(100, 100, 0, 0, 0))
        self.engine._end_game("You sliced a bomb")

    def test_score_does_not_carry_over(self):
        press(self.engine, pygame.K_m)
        self.assertEqual(self.engine.score, 0)

    def test_fruit_do_not_carry_over(self):
        press(self.engine, pygame.K_m)
        self.assertEqual(self.engine.fruits, [])

    def test_game_over_state_does_not_carry_over(self):
        press(self.engine, pygame.K_m)
        self.assertFalse(self.engine.game_over)
        self.assertEqual(self.engine.game_over_reason, "")

    def test_lives_come_from_the_chosen_difficulty(self):
        press(self.engine, pygame.K_e)
        self.assertEqual(self.engine.lives, DIFFICULTIES["easy"]["lives"])

    def test_spawn_timer_restarts(self):
        press(self.engine, pygame.K_m)
        self.assertEqual(self.engine._spawn_timer, 0)

    def test_blade_does_not_carry_over(self):
        """A swipe from before the restart must not slice after it."""
        press(self.engine, pygame.K_m)
        fresh = Fruit(FRUIT_X, FRUIT_Y, 0, 0, 0, radius=RADIUS)
        self.engine.fruits = [fresh]
        swipe(self.engine, (550, FRUIT_Y))  # the old swipe ended at (150, 300)
        self.assertFalse(fresh.sliced)
        self.assertEqual(self.engine.trail, [(550, FRUIT_Y)])

    def test_every_piece_of_state_is_covered(self):
        """A fresh engine and a replayed one must look identical.

        Catches new per-game state being added to __init__ but forgotten in
        start_game, which is exactly how a stale value would creep back.
        """
        press(self.engine, pygame.K_h)
        fresh = GameEngine(WIDTH, HEIGHT, "hard")
        skip = {"font", "title_font", "small_font"}  # surfaces, not state
        self.assertEqual({k: v for k, v in vars(self.engine).items() if k not in skip},
                         {k: v for k, v in vars(fresh).items() if k not in skip})


class ReplayInput(unittest.TestCase):

    def test_each_key_picks_its_difficulty(self):
        for key, expected in ((pygame.K_e, "easy"), (pygame.K_m, "medium"),
                              (pygame.K_h, "hard")):
            with self.subTest(difficulty=expected):
                engine, _ = make_engine()
                engine._end_game("You ran out of lives")
                press(engine, key)
                self.assertEqual(engine.difficulty, expected)
                self.assertFalse(engine.game_over)

    def test_replay_keys_do_nothing_mid_game(self):
        """Pressing H while playing must not wipe the game in progress."""
        engine, _ = make_engine()
        engine.score = 4
        press(engine, pygame.K_h)
        self.assertEqual(engine.score, 4)
        self.assertEqual(engine.difficulty, "medium")

    def test_quitting_is_still_offered(self):
        engine, _ = make_engine()
        engine._end_game("You sliced a bomb")
        press(engine, pygame.K_ESCAPE)
        self.assertTrue(engine.should_quit)

    def test_the_new_game_actually_plays(self):
        engine, _ = make_engine()
        engine._end_game("You sliced a bomb")
        press(engine, pygame.K_m)

        for _ in range(DIFFICULTIES["medium"]["spawn_interval"] + 1):
            engine.update()
        self.assertTrue(engine.fruits, "no fruit thrown after the replay")

        target = Fruit(FRUIT_X, FRUIT_Y, 0, 0, 0, radius=RADIUS)
        engine.fruits.append(target)
        swipe(engine, (150, FRUIT_Y), (550, FRUIT_Y))
        self.assertTrue(target.sliced, "blade is dead after the replay")
        self.assertEqual(engine.score, 1)

    def test_you_can_die_and_replay_repeatedly(self):
        engine, _ = make_engine()
        for key, name in ((pygame.K_h, "hard"), (pygame.K_e, "easy"),
                          (pygame.K_m, "medium")):
            engine.score = 5
            engine._end_game("You sliced a bomb")
            press(engine, key)
            self.assertEqual(engine.difficulty, name)
            self.assertEqual(engine.score, 0)
            self.assertFalse(engine.game_over)


class ReplayScreen(unittest.TestCase):

    def centred_texts(self, engine):
        texts = []
        engine._blit_centered = lambda screen, font, text, color, y: texts.append(text)
        engine.render(blank_screen())
        return texts

    def test_screen_offers_all_four_choices(self):
        engine, _ = make_engine()
        engine._end_game("You sliced a bomb")
        shown = " | ".join(self.centred_texts(engine))
        for choice in ("Easy", "Medium", "Hard", "Esc"):
            self.assertIn(choice, shown)

    def test_hud_names_the_current_difficulty(self):
        engine, _ = make_engine()
        engine.start_game("hard")
        self.assertIn("Hard", self.centred_texts(engine))


if __name__ == "__main__":
    sys.exit(run(DifficultyPresets, ReplayWipesTheLastGame, ReplayInput, ReplayScreen))
