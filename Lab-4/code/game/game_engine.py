import pygame
import random
from .fruit import Fruit

# Game Engine

WHITE = (255, 255, 255)
BOMB_BLACK = (30, 30, 30)
FRUIT_COLORS = [(220, 60, 60), (230, 140, 40), (230, 200, 40), (90, 180, 90)]

# Game over screen
DIM = (0, 0, 0, 115)  # translucent black, so the frozen game shows through
PANEL = (0, 0, 0, 200)  # darker still behind the text, to keep it readable.
# Note: drawn onto the SRCALPHA overlay, which replaces pixels rather than
# blending, so this alpha is the total cover there - not DIM plus this.
TITLE_RED = (235, 80, 80)
MUTED = (200, 200, 210)

# Difficulty presets. Harder means fruit arriving more often, more of them
# being bombs, thrown a little harder, and fewer lives to lose.
DIFFICULTIES = {
    "easy":   {"label": "Easy",   "spawn_interval": 75, "bomb_chance": 0.08,
               "speed_scale": 0.90, "lives": 5},
    "medium": {"label": "Medium", "spawn_interval": 50, "bomb_chance": 0.15,
               "speed_scale": 1.00, "lives": 3},
    "hard":   {"label": "Hard",   "spawn_interval": 30, "bomb_chance": 0.25,
               "speed_scale": 1.15, "lives": 2},
}
DEFAULT_DIFFICULTY = "medium"

# Keys offered on the game over screen.
REPLAY_KEYS = {pygame.K_e: "easy", pygame.K_m: "medium", pygame.K_h: "hard"}
QUIT_KEYS = (pygame.K_ESCAPE, pygame.K_q)

# After these the pointer can reappear somewhere else entirely, so the blade
# must not be joined up across them.
BLADE_BREAK_EVENTS = {
    e for e in (getattr(pygame, "WINDOWLEAVE", None),
                getattr(pygame, "WINDOWFOCUSLOST", None))
    if e is not None
}

class GameEngine:
    def __init__(self, width, height, difficulty=DEFAULT_DIFFICULTY):
        self.width = width
        self.height = height

        # Outlives any single game.
        self.font = pygame.font.SysFont("Arial", 28)
        self.title_font = pygame.font.SysFont("Arial", 64, bold=True)
        self.small_font = pygame.font.SysFont("Arial", 22)
        self.should_quit = False  # main loop watches this

        self.start_game(difficulty)

    def start_game(self, difficulty=DEFAULT_DIFFICULTY):
        """Begin a game, wiping anything left over from the previous one.

        Every piece of per-game state is set here and nowhere else, so a replay
        cannot inherit a stale score, leftover fruit or the game over flag.
        """
        settings = DIFFICULTIES[difficulty]
        self.difficulty = difficulty
        self.spawn_interval = settings["spawn_interval"]  # frames between spawns
        self.bomb_chance = settings["bomb_chance"]
        self.speed_scale = settings["speed_scale"]
        self.lives = settings["lives"]

        self.fruits = []
        self.trail = []  # recent mouse positions, drawn as the "blade"
        self._last_pos = None  # previous mouse position, start of the swept blade
        self._spawn_timer = 0
        self.score = 0
        self.game_over = False
        self.game_over_reason = ""

    def spawn_fruit(self):
        x = random.randint(60, self.width - 60)
        vy = -random.uniform(13, 16) * self.speed_scale
        vx = random.uniform(-2, 2)
        gravity = 0.35
        kind = "bomb" if random.random() < self.bomb_chance else "fruit"

        fruit = Fruit(x, self.height + 30, vx, vy, gravity, kind=kind)
        fruit.color = BOMB_BLACK if kind == "bomb" else random.choice(FRUIT_COLORS)
        self.fruits.append(fruit)

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self._handle_motion(event.pos)
        elif event.type == pygame.KEYDOWN:
            self._handle_keydown(event.key)
        elif event.type in BLADE_BREAK_EVENTS:
            self._break_blade()

    def _handle_motion(self, pos):
        if self.game_over:
            # The blade is dead once the game is over; without this the score
            # would keep climbing behind the game over screen.
            return

        x, y = pos
        if self._last_pos is None:
            # First sample since the blade entered the window - there's no
            # previous position to sweep from, so test the point on its own.
            x1, y1 = x, y
        else:
            x1, y1 = self._last_pos

        for fruit in self.fruits:
            if not fruit.sliced and fruit.intersects_segment(x1, y1, x, y):
                self._slice(fruit)

        self._last_pos = pos
        self.trail.append(pos)
        if len(self.trail) > 15:
            self.trail.pop(0)

    def _handle_keydown(self, key):
        # The game over screen is just another frame drawn by the main loop, not
        # a blocking wait, so key presses keep arriving here while it is up.
        if not self.game_over:
            return

        if key in QUIT_KEYS:
            self.should_quit = True
        elif key in REPLAY_KEYS:
            self.start_game(REPLAY_KEYS[key])

    def _break_blade(self):
        # Forgetting the last position stops the next swipe from being joined to
        # a stale one, which would sweep a segment clear across the screen and
        # slice everything on the way.
        self._last_pos = None
        self.trail = []

    def _slice(self, fruit):
        fruit.sliced = True
        if fruit.kind == "bomb":
            self._end_game("You sliced a bomb")
        else:
            self.score += 1

    def _end_game(self, reason):
        self.game_over = True
        self.game_over_reason = reason
        self._last_pos = None  # don't carry a stale swipe into the next game

    def handle_input(self):
        # Reserved for continuously-held-key input; this game is
        # entirely mouse-driven, so there's nothing to poll here.
        pass

    def update(self):
        if self.game_over:
            # Everything stops where it is, which is what the game over screen
            # then dims and draws over.
            return

        self._spawn_timer += 1
        if self._spawn_timer >= self.spawn_interval:
            self._spawn_timer = 0
            self.spawn_fruit()

        still_alive = []
        for fruit in self.fruits:
            fruit.update()
            if fruit.sliced:
                continue
            if fruit.off_screen(self.height):
                if fruit.kind == "fruit":
                    self.lives -= 1
                continue
            still_alive.append(fruit)
        self.fruits = still_alive

        if self.lives <= 0:
            self._end_game("You ran out of lives")

    def render(self, screen):
        for fruit in self.fruits:
            color = getattr(fruit, "color", WHITE)
            pygame.draw.circle(screen, color, (int(fruit.x), int(fruit.y)), fruit.radius)

        if len(self.trail) >= 2:
            pygame.draw.lines(screen, WHITE, False, self.trail, 3)

        score_text = self.font.render(f"Score: {self.score}", True, WHITE)
        screen.blit(score_text, (10, 10))
        lives_text = self.font.render(f"Lives: {max(self.lives, 0)}", True, WHITE)
        screen.blit(lives_text, (self.width - 130, 10))
        self._blit_centered(screen, self.small_font,
                            DIFFICULTIES[self.difficulty]["label"], MUTED, 16)

        if self.game_over:
            self._render_game_over(screen)

    def _render_game_over(self, screen):
        # Dim the whole frame rather than clearing it, so the last moment of
        # play stays visible underneath.
        overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        overlay.fill(DIM)

        # A fruit can end up sitting right behind the title, so the text block
        # gets a little more cover than the rest of the frame.
        panel = pygame.Rect(0, 0, 540, 360)
        panel.center = (self.width // 2, 295)
        pygame.draw.rect(overlay, PANEL, panel, border_radius=18)
        screen.blit(overlay, (0, 0))

        self._blit_centered(screen, self.title_font, "GAME OVER", TITLE_RED, 150)
        if self.game_over_reason:
            self._blit_centered(screen, self.small_font, self.game_over_reason, MUTED, 235)
        self._blit_centered(screen, self.font, f"Final Score: {self.score}", WHITE, 280)
        self._blit_centered(screen, self.small_font, "Play again:", MUTED, 350)
        self._blit_centered(screen, self.font,
                            "[E] Easy    [M] Medium    [H] Hard", WHITE, 383)
        self._blit_centered(screen, self.small_font, "[Esc] Quit", MUTED, 432)

    def _blit_centered(self, screen, font, text, color, y):
        surface = font.render(text, True, color)
        screen.blit(surface, (self.width // 2 - surface.get_width() // 2, y))
