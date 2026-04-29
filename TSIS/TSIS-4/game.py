# game.py — Core game logic

import pygame
import random
import json
import os
import math
import array
from config import *


# ─────────────────────────────────────────────────────────────
#  Sound Manager
# ─────────────────────────────────────────────────────────────

class SoundManager:
    """Generates and plays all game sounds procedurally (no audio files needed)."""

    SAMPLE_RATE = 22050

    def __init__(self):
        self._enabled = False
        self._sounds: dict[str, pygame.mixer.Sound] = {}
        try:
            pygame.mixer.pre_init(self.SAMPLE_RATE, -16, 1, 512)
            pygame.mixer.init()
            self._sounds = {
                "eat":      self._make_eat(),
                "bonus":    self._make_bonus(),
                "rare":     self._make_rare(),
                "poison":   self._make_poison(),
                "powerup":  self._make_powerup(),
                "levelup":  self._make_levelup(),
                "die":      self._make_die(),
            }
        except Exception as e:
            print(f"[Sound] init error: {e}")

    # ── Public API ──────────────────────────────────────────

    def set_enabled(self, enabled: bool):
        self._enabled = enabled

    def play(self, name: str):
        if not self._enabled:
            return
        snd = self._sounds.get(name)
        if snd:
            snd.play()

    # ── Waveform builders ───────────────────────────────────

    def _build(self, samples: list[float], volume: float = 0.6) -> pygame.mixer.Sound:
        """Convert float samples [-1,1] to a pygame Sound."""
        peak = max(abs(s) for s in samples) or 1.0
        int_samples = array.array("h", [
            int(s / peak * 32767 * volume) for s in samples
        ])
        sound = pygame.mixer.Sound(buffer=int_samples)
        return sound

    def _sine(self, freq: float, duration: float, decay: float = 3.0) -> list[float]:
        n = int(self.SAMPLE_RATE * duration)
        return [
            math.sin(2 * math.pi * freq * i / self.SAMPLE_RATE)
            * math.exp(-decay * i / n)
            for i in range(n)
        ]

    def _sweep(self, f0: float, f1: float, duration: float, decay: float = 2.0) -> list[float]:
        n = int(self.SAMPLE_RATE * duration)
        return [
            math.sin(2 * math.pi * (f0 + (f1 - f0) * i / n) * i / self.SAMPLE_RATE)
            * math.exp(-decay * i / n)
            for i in range(n)
        ]

    def _noise(self, duration: float, decay: float = 8.0) -> list[float]:
        n = int(self.SAMPLE_RATE * duration)
        return [
            (random.random() * 2 - 1) * math.exp(-decay * i / n)
            for i in range(n)
        ]

    def _mix(self, *tracks: list[float]) -> list[float]:
        length = max(len(t) for t in tracks)
        result = []
        for i in range(length):
            result.append(sum(t[i] if i < len(t) else 0.0 for t in tracks))
        return result

    # ── Sound definitions ───────────────────────────────────

    def _make_eat(self) -> pygame.mixer.Sound:
        """Short upward blip for normal food."""
        return self._build(self._sweep(300, 600, 0.08, decay=4.0), volume=0.5)

    def _make_bonus(self) -> pygame.mixer.Sound:
        """Two-tone chime for bonus food."""
        a = self._sweep(500, 900, 0.1, decay=3.0)
        b = [0.0] * int(self.SAMPLE_RATE * 0.05) + self._sweep(700, 1100, 0.1, decay=3.0)
        return self._build(self._mix(a, b), volume=0.55)

    def _make_rare(self) -> pygame.mixer.Sound:
        """Three-tone sparkle for rare food."""
        a = self._sine(880, 0.08, decay=4.0)
        b = [0.0] * int(self.SAMPLE_RATE * 0.07) + self._sine(1100, 0.08, decay=4.0)
        c = [0.0] * int(self.SAMPLE_RATE * 0.14) + self._sine(1320, 0.10, decay=3.0)
        return self._build(self._mix(a, b, c), volume=0.5)

    def _make_poison(self) -> pygame.mixer.Sound:
        """Downward buzz for poison."""
        tone = self._sweep(400, 150, 0.18, decay=2.5)
        noise = self._noise(0.18, decay=5.0)
        return self._build(self._mix(tone, [n * 0.3 for n in noise]), volume=0.6)

    def _make_powerup(self) -> pygame.mixer.Sound:
        """Rising arpeggio for power-up pickup."""
        freqs = [523, 659, 784, 1047]
        result: list[float] = []
        step = int(self.SAMPLE_RATE * 0.07)
        for freq in freqs:
            result += self._sine(freq, 0.07, decay=5.0) + [0.0] * (step - int(self.SAMPLE_RATE * 0.07))
        return self._build(result, volume=0.55)

    def _make_levelup(self) -> pygame.mixer.Sound:
        """Fanfare for level-up."""
        freqs = [523, 659, 784, 1047, 1319]
        result: list[float] = []
        for i, freq in enumerate(freqs):
            pause = [0.0] * int(self.SAMPLE_RATE * 0.04 * i)
            result = self._mix(result + [0.0] * (len(pause) + int(self.SAMPLE_RATE * 0.18)),
                               pause + self._sine(freq, 0.18, decay=2.0))
        return self._build(result, volume=0.6)

    def _make_die(self) -> pygame.mixer.Sound:
        """Descending crash for death."""
        tone = self._sweep(300, 60, 0.5, decay=1.5)
        noise = self._noise(0.4, decay=2.0)
        combined = self._mix(tone, [n * 0.5 for n in noise])
        return self._build(combined, volume=0.7)


# ─────────────────────────────────────────────────────────────
#  Helpers
# ─────────────────────────────────────────────────────────────

def cell_rect(col: int, row: int) -> pygame.Rect:
    return pygame.Rect(
        PLAY_AREA_X + col * CELL_SIZE,
        PLAY_AREA_Y + row * CELL_SIZE,
        CELL_SIZE,
        CELL_SIZE,
    )


def random_free_cell(occupied: set) -> tuple[int, int] | None:
    free = [
        (c, r)
        for c in range(GRID_COLS)
        for r in range(GRID_ROWS)
        if (c, r) not in occupied
    ]
    return random.choice(free) if free else None


# ─────────────────────────────────────────────────────────────
#  Food
# ─────────────────────────────────────────────────────────────

class Food:
    def __init__(self, pos: tuple[int, int], ftype: dict):
        self.pos = pos
        self.color = ftype["color"]
        self.points = ftype["points"]
        self.timed = ftype["timed"]
        self.spawn_time = pygame.time.get_ticks()

    def is_expired(self) -> bool:
        if not self.timed:
            return False
        return pygame.time.get_ticks() - self.spawn_time > FOOD_DISAPPEAR_MS

    def draw(self, surface: pygame.Surface):
        rect = cell_rect(*self.pos)
        pygame.draw.ellipse(surface, self.color, rect.inflate(-4, -4))
        # Blinking effect when about to expire
        if self.timed:
            elapsed = pygame.time.get_ticks() - self.spawn_time
            remaining = FOOD_DISAPPEAR_MS - elapsed
            if remaining < 2000 and (remaining // 200) % 2 == 0:
                pygame.draw.ellipse(surface, WHITE, rect.inflate(-8, -8), 2)


class PoisonFood:
    def __init__(self, pos: tuple[int, int]):
        self.pos = pos
        self.spawn_time = pygame.time.get_ticks()

    def draw(self, surface: pygame.Surface):
        rect = cell_rect(*self.pos)
        pygame.draw.rect(surface, POISON_COLOR, rect.inflate(-4, -4), border_radius=4)
        # Skull-like cross mark
        cx, cy = rect.centerx, rect.centery
        pygame.draw.line(surface, WHITE, (cx - 4, cy - 4), (cx + 4, cy + 4), 2)
        pygame.draw.line(surface, WHITE, (cx + 4, cy - 4), (cx - 4, cy + 4), 2)


# ─────────────────────────────────────────────────────────────
#  Power-ups
# ─────────────────────────────────────────────────────────────

class PowerUp:
    def __init__(self, pos: tuple[int, int], kind: str):
        self.pos = pos
        self.kind = kind
        self.color = POWERUP_COLORS[kind]
        self.spawn_time = pygame.time.get_ticks()

    def is_expired(self) -> bool:
        return pygame.time.get_ticks() - self.spawn_time > POWERUP_FIELD_MS

    def draw(self, surface: pygame.Surface):
        rect = cell_rect(*self.pos)
        pygame.draw.polygon(
            surface,
            self.color,
            [
                (rect.centerx, rect.top + 2),
                (rect.right - 2, rect.bottom - 2),
                (rect.left + 2, rect.bottom - 2),
            ],
        )
        label = {"speed": "S", "slow": "W", "shield": "X"}[self.kind]
        font = pygame.font.SysFont("monospace", 10, bold=True)
        surf = font.render(label, True, BLACK)
        surface.blit(surf, surf.get_rect(center=rect.center))


# ─────────────────────────────────────────────────────────────
#  Snake
# ─────────────────────────────────────────────────────────────

class Snake:
    def __init__(self, color: list):
        self.color = tuple(color)
        self.reset()

    def reset(self):
        cx, cy = GRID_COLS // 2, GRID_ROWS // 2
        self.body = [(cx, cy), (cx - 1, cy), (cx - 2, cy)]
        self.direction = (1, 0)
        self.next_direction = (1, 0)
        self.grow_pending = 0

    def set_direction(self, dx: int, dy: int):
        # Prevent 180-degree reversal
        if (dx, dy) != (-self.direction[0], -self.direction[1]):
            self.next_direction = (dx, dy)

    def move(self) -> tuple[int, int]:
        """Advance the snake one step. Returns new head position."""
        self.direction = self.next_direction
        hx, hy = self.body[0]
        new_head = (hx + self.direction[0], hy + self.direction[1])
        self.body.insert(0, new_head)
        if self.grow_pending > 0:
            self.grow_pending -= 1
        else:
            self.body.pop()
        return new_head

    def grow(self, segments: int = 1):
        self.grow_pending += segments

    def shorten(self, segments: int = 2):
        remove = min(segments, len(self.body) - 1)
        if remove > 0:
            self.body = self.body[:-remove]

    @property
    def head(self) -> tuple[int, int]:
        return self.body[0]

    def occupies(self) -> set:
        return set(self.body)

    def draw(self, surface: pygame.Surface, shield_active: bool):
        for i, (col, row) in enumerate(self.body):
            rect = cell_rect(col, row)
            shade = max(30, 255 - i * 8)
            color = (
                min(self.color[0], shade),
                min(self.color[1], shade),
                min(self.color[2], shade),
            )
            pygame.draw.rect(surface, color, rect.inflate(-2, -2), border_radius=4)

        # Draw shield aura on head
        if shield_active:
            head_rect = cell_rect(*self.body[0])
            pygame.draw.rect(
                surface, POWERUP_COLORS["shield"],
                head_rect.inflate(4, 4), 2, border_radius=6
            )


# ─────────────────────────────────────────────────────────────
#  GameState
# ─────────────────────────────────────────────────────────────

class GameState:
    """Encapsulates one active game session."""

    def __init__(self, snake_color: list):
        self.snake = Snake(snake_color)
        self.score = 0
        self.level = 1
        self.food_eaten_this_level = 0
        self.foods: list[Food] = []
        self.poison: PoisonFood | None = None
        self.powerup: PowerUp | None = None
        self.obstacles: set = set()

        # Power-up effect state
        self.active_effect: str | None = None   # 'speed', 'slow', 'shield'
        self.effect_start: int = 0
        self.shield_triggered = False

        # Move timer
        self._last_move_ms = 0

        # Spawn initial food
        self._spawn_food()
        self._try_spawn_poison()

    # ── Speed ──────────────────────────────────────────────

    def _current_speed(self) -> float:
        base = BASE_SPEED + (self.level - 1) * SPEED_INCREMENT
        if self.active_effect == "speed":
            return base * SPEED_BOOST_FACTOR
        if self.active_effect == "slow":
            return base * SLOW_FACTOR
        return base

    def _move_interval_ms(self) -> int:
        return int(1000 / self._current_speed())

    # ── Occupied cells ─────────────────────────────────────

    def _all_occupied(self) -> set:
        occupied = self.snake.occupies() | self.obstacles
        for f in self.foods:
            occupied.add(f.pos)
        if self.poison:
            occupied.add(self.poison.pos)
        if self.powerup:
            occupied.add(self.powerup.pos)
        return occupied

    # ── Spawning ───────────────────────────────────────────

    def _spawn_food(self):
        # Keep up to 3 food items on field (one per type)
        existing_types = {f.points for f in self.foods}
        for ftype in FOOD_TYPES:
            if ftype["points"] not in existing_types:
                pos = random_free_cell(self._all_occupied())
                if pos:
                    self.foods.append(Food(pos, ftype))

    def _try_spawn_poison(self):
        if self.poison is None and random.random() < 0.3:
            pos = random_free_cell(self._all_occupied())
            if pos:
                self.poison = PoisonFood(pos)

    def _try_spawn_powerup(self):
        if self.powerup is None and random.random() < 0.2:
            kind = random.choice(["speed", "slow", "shield"])
            pos = random_free_cell(self._all_occupied())
            if pos:
                self.powerup = PowerUp(pos, kind)

    def _place_obstacles(self):
        """Place obstacle blocks for the current level (Level 3+)."""
        if self.level < OBSTACLE_LEVEL_START:
            return
        count = OBSTACLES_PER_LEVEL * (self.level - OBSTACLE_LEVEL_START + 1)
        attempts = 0
        while len(self.obstacles) < count and attempts < 500:
            attempts += 1
            c = random.randint(0, GRID_COLS - 1)
            r = random.randint(0, GRID_ROWS - 1)
            if (c, r) in self.snake.occupies():
                continue
            # Don't trap snake: ensure head neighbours remain open
            hx, hy = self.snake.head
            if abs(c - hx) <= 2 and abs(r - hy) <= 2:
                continue
            self.obstacles.add((c, r))

    # ── Collision helpers ──────────────────────────────────

    def _out_of_bounds(self, pos: tuple[int, int]) -> bool:
        c, r = pos
        return not (0 <= c < GRID_COLS and 0 <= r < GRID_ROWS)

    # ── Main update ────────────────────────────────────────

    def update(self) -> tuple[str, list[str]]:
        """
        Call every frame. Returns:
          (status, sounds)
          status: 'alive' | 'dead'
          sounds: list of sound event names to play this frame
        """
        now = pygame.time.get_ticks()
        sounds: list[str] = []

        # ─ Effect expiry ─
        if self.active_effect and self.active_effect != "shield":
            if now - self.effect_start > POWERUP_EFFECT_MS:
                self.active_effect = None

        # ─ Power-up field expiry ─
        if self.powerup and self.powerup.is_expired():
            self.powerup = None

        # ─ Food expiry ─
        self.foods = [f for f in self.foods if not f.is_expired()]

        # ─ Move timer ─
        if now - self._last_move_ms < self._move_interval_ms():
            return "alive", sounds
        self._last_move_ms = now

        # ─ Move snake ─
        new_head = self.snake.move()

        # ─ Wall / border collision ─
        if self._out_of_bounds(new_head):
            if self.active_effect == "shield" and not self.shield_triggered:
                self.shield_triggered = True
                self.active_effect = None
                c, r = new_head
                c = c % GRID_COLS
                r = r % GRID_ROWS
                self.snake.body[0] = (c, r)
                new_head = (c, r)
            else:
                sounds.append("die")
                return "dead", sounds

        # ─ Obstacle collision ─
        if new_head in self.obstacles:
            if self.active_effect == "shield" and not self.shield_triggered:
                self.shield_triggered = True
                self.active_effect = None
                self.snake.body.pop(0)
                self.snake.body.insert(0, self.snake.body[0])
            else:
                sounds.append("die")
                return "dead", sounds

        # ─ Self collision ─
        if new_head in set(self.snake.body[1:]):
            if self.active_effect == "shield" and not self.shield_triggered:
                self.shield_triggered = True
                self.active_effect = None
            else:
                sounds.append("die")
                return "dead", sounds

        # ─ Food collision ─
        for food in self.foods[:]:
            if new_head == food.pos:
                self.score += food.points * self.level
                self.snake.grow(1)
                self.food_eaten_this_level += 1
                self.foods.remove(food)
                self._spawn_food()
                self._try_spawn_poison()
                self._try_spawn_powerup()
                leveled = self._check_level_up()
                # Pick sound by food type
                if food.points >= 5:
                    sounds.append("rare")
                elif food.points >= 3:
                    sounds.append("bonus")
                else:
                    sounds.append("eat")
                if leveled:
                    sounds.append("levelup")
                break

        # ─ Poison collision ─
        if self.poison and new_head == self.poison.pos:
            self.snake.shorten(2)
            self.poison = None
            sounds.append("poison")
            if len(self.snake.body) <= 1:
                sounds.append("die")
                return "dead", sounds
            self._try_spawn_poison()

        # ─ Power-up collision ─
        if self.powerup and new_head == self.powerup.pos:
            kind = self.powerup.kind
            self.powerup = None
            self.active_effect = kind
            self.effect_start = now
            self.shield_triggered = False
            sounds.append("powerup")

        return "alive", sounds

    def _check_level_up(self) -> bool:
        """Returns True if a level-up occurred."""
        if self.food_eaten_this_level >= FOOD_PER_LEVEL:
            self.level += 1
            self.food_eaten_this_level = 0
            self._place_obstacles()
            return True
        return False

    # ── Draw ───────────────────────────────────────────────

    def draw(self, surface: pygame.Surface, settings: dict):
        # Background
        play_rect = pygame.Rect(PLAY_AREA_X, PLAY_AREA_Y, PLAY_AREA_WIDTH, PLAY_AREA_HEIGHT)
        pygame.draw.rect(surface, BG_COLOR, play_rect)

        # Grid overlay
        if settings.get("grid_overlay", True):
            for c in range(GRID_COLS):
                for r in range(GRID_ROWS):
                    pygame.draw.rect(surface, GRID_COLOR, cell_rect(c, r), 1)

        # Obstacles
        for (c, r) in self.obstacles:
            rect = cell_rect(c, r)
            pygame.draw.rect(surface, WALL_COLOR, rect)
            pygame.draw.rect(surface, MID_GRAY, rect, 1)

        # Foods
        for food in self.foods:
            food.draw(surface)

        # Poison
        if self.poison:
            self.poison.draw(surface)

        # Power-up
        if self.powerup:
            self.powerup.draw(surface)

        # Snake
        shield_active = (self.active_effect == "shield" and not self.shield_triggered)
        self.snake.draw(surface, shield_active)