# Lab 4 — Vibe Coding

**Prajwal G Devadiga** · **PES1UG24CS590**
Software Engineering — Lab 4 · PES University, Dept. of CSE

Assigned repo: [SETAPESU26/41_fruit-ninja](https://github.com/SETAPESU26/41_fruit-ninja) —
*Real-Time Fruit Slice Game* (Pygame). Individual assignment.

## Contents

| Path | What it is |
|---|---|
| [`PROMPTS.md`](PROMPTS.md) | The prompts used with the vibe-coding tool, one per task |
| `code/` | The game — starter code, then updated task by task |
| `videos/` | 10-second gameplay recordings, before and after |
| `chat/` | The vibe-coding chat history exported as PDF |

## Tasks (from the assigned repo's README)

| # | Task | Status |
|---|---|---|
| 1 | Refine collision detection — fast swipes pass through fruit | ✅ |
| 2 | Implement a game-over screen instead of a console `print` | ✅ |
| 3 | Add a replay option with Easy / Medium / Hard difficulty | ✅ |
| 4 | Add sound feedback for slice, bomb and game over | ✅ |

## Running it

Python 3.14 has no stock `pygame` wheel and building it from source fails here, so use
**pygame-ce**, which is a drop-in fork — `import pygame` still works:

```bash
pip install pygame-ce
```

```bash
cd Lab-4/code && python main.py
```

## The bug, as it was before the fix

`Fruit.contains_point()` tests a single point against the fruit's circle. At 60 FPS a fast
swipe reports two `MOUSEMOTION` positions that straddle the fruit, so no reported point ever
lands inside it and the slice never registers.

With a fruit parked at (350, 300) radius 28:

| Mouse points fed to `_handle_motion` | Sliced? |
|---|---|
| `(350, 300)` — slow, lands inside the circle | yes |
| `(150, 300)` then `(550, 300)` — segment passes through the centre | **no** |

That is what the *before* video shows. It is fixed now — `Fruit.intersects_segment()` tests the
segment between consecutive mouse samples instead of the single current point.

## Tests

```bash
cd Lab-4/code && python tests/run_all.py
```

61 headless checks across collision detection, the game-over screen, replay/difficulty and the
generated audio. They run with dummy SDL drivers, so no window or audio device is needed.

## Difficulty settings

| | Spawn interval | Bomb chance | Speed | Lives |
|---|---|---|---|---|
| Easy | 75 frames | 8% | 0.90 | 5 |
| Medium | 50 frames | 15% | 1.00 | 3 |
| Hard | 30 frames | 25% | 1.15 | 2 |

On the game-over screen: **E** / **M** / **H** to replay, **Q** or **Esc** to quit.
