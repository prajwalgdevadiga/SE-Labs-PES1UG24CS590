# Lab 4 — Vibe Coding prompts

Four prompts, one per task. Paste them into a **fresh chat** with your vibe-coding tool, in
order. That chat history is itself a deliverable, so keep it clean — don't mix other work in.

Work in `Lab-4/code/`. Commit after each one.

---

## Prompt 1 — Task 1: the collision bug

Attach or paste `main.py`, `game/fruit.py` and `game/game_engine.py` with this one.

> Hey, I've got a small Fruit Ninja style game in Pygame that I need to fix up for a lab. I've
> pasted the three files below.
>
> The problem: when I swipe quickly across a fruit the blade goes straight through it and
> nothing happens — no slice, no score. But if I move the mouse slowly over the same fruit it
> cuts fine every time. My guess is it's only looking at wherever the mouse is at that instant
> instead of the line it travelled along, so a fast swipe just skips over the fruit between
> frames.
>
> Have a quick read of the code first and tell me if that's actually the cause, then fix it so
> fast swipes register properly. Also give me some way to test it without playing the game over
> and over — something I can just run and see pass or fail.

---

## Prompt 2 — Task 2: a proper game over screen

> Nice, that works now. Next thing.
>
> At the moment when you hit a bomb or run out of lives, the game window just sits there frozen
> and prints "Game over" into the terminal, which is useless. I want a real game over screen
> inside the window showing the final score, with the game still visible but dimmed behind it.
>
> Important bit — it mustn't lock up. I should still be able to close the window with the X
> button, and in the next step I'm going to add a restart option so it needs to keep listening
> for key presses.

---

## Prompt 3 — Task 3: play again with a difficulty choice

> Now I want to be able to start a new game after dying instead of having to close and reopen
> it. On the game over screen let me pick easy, medium or hard, or quit out.
>
> Harder should mean fruit coming faster and more bombs, easier the opposite — pick values that
> actually feel different and tell me what you went with so I can tweak them.
>
> One thing to watch: make sure starting a new game properly wipes everything from the last one.
> I don't want the old score, leftover fruit or the game over state hanging around.

---

## Prompt 4 — Task 4: sound, then a final check

> Last feature — sound. I want a noise when you slice a fruit, a different one when you hit a
> bomb, and something for the game over moment.
>
> Two catches. I don't have any sound files and I'd rather not go downloading any, so can you
> generate the sounds in code instead? And my laptop's audio is flaky, so if sound fails to
> start up the game should just carry on silently rather than crashing. Also make sure the game
> over sound only plays once — I don't want it going off every frame while the screen is up.
>
> Once that's in, that's all four things done — so have a look over the whole lot and tell me
> whether any of the later changes broke something we did earlier, whether there's leftover
> code sitting around that isn't used any more, and anything you reckon someone marking this
> would pick holes in. Then give me the final version of all three files so I know what I'm
> committing.

---

## After each one

Run the game, check it actually behaves, then commit before moving on — the handout wants a
separate commit per task:

```bash
git add Lab-4/code && git commit -m "Lab 4 Task 1: fix fast-swipe collision detection"
```

| Task | Commit message |
|---|---|
| 1 | `Lab 4 Task 1: fix fast-swipe collision detection` |
| 2 | `Lab 4 Task 2: add game over screen` |
| 3 | `Lab 4 Task 3: add replay with difficulty selection` |
| 4 | `Lab 4 Task 4: add sound effects` |

## If one doesn't land first time

Four prompts is the plan, not a rule — the handout says three to four *attempts*, so a
follow-up when something's wrong is expected. Keep it short and factual:

- *"That didn't work — fast swipes still go through. Here's what I see when I run it: …"*
- *"The game over screen shows but now I can't close the window."*
- *"Restarting works but the score carried over from the last game."*
- *"It crashes on startup with this error: …"*
