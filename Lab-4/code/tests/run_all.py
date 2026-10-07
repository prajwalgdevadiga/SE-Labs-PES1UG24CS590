"""Run every check in one go:

    python tests/run_all.py
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from _support import run
from test_game_over import GameOverInput, GameOverScreen, GameOverState
from test_replay import (DifficultyPresets, ReplayInput, ReplayScreen,
                         ReplayWipesTheLastGame)
from test_slice_detection import SliceDetection
from test_sound import BoardSurvivesBadAudio, EngineAsksForSounds, GeneratedAudio

if __name__ == "__main__":
    sys.exit(run(SliceDetection, GameOverState, GameOverScreen, GameOverInput,
                 DifficultyPresets, ReplayWipesTheLastGame, ReplayInput, ReplayScreen,
                 EngineAsksForSounds, BoardSurvivesBadAudio, GeneratedAudio))
