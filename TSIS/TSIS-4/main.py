# main.py — Entry point & all game screens

import pygame
import sys
import json
import os
from datetime import datetime
from config import *
import db
from game import GameState, SoundManager

# ─────────────────────────────────────────────────────────────
#  Settings helpers
# ─────────────────────────────────────────────────────────────

SETTINGS_FILE = os.path.join(os.path.dirname(__file__), "settings.json")

DEFAULT_SETTINGS = {
    "snake_color": list(GREEN),
    "grid_overlay": True,
    "sound": False,
}


def load_settings() -> dict:
    try:
        with open(SETTINGS_FILE, "r") as f:
            data = json.load(f)
        # Fill missing keys with defaults
        for k, v in DEFAULT_SETTINGS.items():
            data.setdefault(k, v)
        return data
    except Exception:
        return dict(DEFAULT_SETTINGS)


def save_settings(settings: dict):
    try:
        with open(SETTINGS_FILE, "w") as f:
            json.dump(settings, f, indent=4)
    except Exception as e:
        print(f"[Settings] save error: {e}")


# ─────────────────────────────────────────────────────────────
#  UI Helpers
# ─────────────────────────────────────────────────────────────

def draw_text(surface, text, font, color, x, y, align="left"):
    surf = font.render(text, True, color)
    if align == "center":
        rect = surf.get_rect(centerx=x, y=y)
    elif align == "right":
        rect = surf.get_rect(right=x, y=y)
    else:
        rect = surf.get_rect(x=x, y=y)
    surface.blit(surf, rect)
    return rect


def draw_button(surface, text, font, rect, color, text_color=BLACK, radius=8):
    pygame.draw.rect(surface, color, rect, border_radius=radius)
    pygame.draw.rect(surface, WHITE, rect, 2, border_radius=radius)
    t = font.render(text, True, text_color)
    surface.blit(t, t.get_rect(center=rect.center))
    return rect


def make_button(cx, cy, w, h, text, font, color, surface=None, text_color=BLACK):
    rect = pygame.Rect(0, 0, w, h)
    rect.center = (cx, cy)
    if surface:
        draw_button(surface, text, font, rect, color, text_color)
    return rect


def draw_sidebar(surface, fonts, score, level, personal_best, active_effect, effect_start, effect_ms):
    sidebar = pygame.Rect(SIDEBAR_X, 0, SIDEBAR_WIDTH, WINDOW_HEIGHT)
    pygame.draw.rect(surface, SIDEBAR_BG, sidebar)
    pygame.draw.line(surface, ACCENT, (SIDEBAR_X, 0), (SIDEBAR_X, WINDOW_HEIGHT), 2)

    cx = SIDEBAR_X + SIDEBAR_WIDTH // 2
    y = 20

    draw_text(surface, "SNAKE", fonts["title"], ACCENT, cx, y, "center")
    y += 36

    pygame.draw.line(surface, MID_GRAY, (SIDEBAR_X + 10, y), (SIDEBAR_X + SIDEBAR_WIDTH - 10, y))
    y += 12

    draw_text(surface, "SCORE", fonts["label"], LIGHT_GRAY, cx, y, "center")
    y += 20
    draw_text(surface, str(score), fonts["big"], WHITE, cx, y, "center")
    y += 44

    draw_text(surface, f"LEVEL  {level}", fonts["label"], YELLOW, cx, y, "center")
    y += 28

    draw_text(surface, f"BEST  {personal_best}", fonts["label"], CYAN, cx, y, "center")
    y += 40

    pygame.draw.line(surface, MID_GRAY, (SIDEBAR_X + 10, y), (SIDEBAR_X + SIDEBAR_WIDTH - 10, y))
    y += 12

    # Active effect
    if active_effect:
        now = pygame.time.get_ticks()
        if active_effect == "shield":
            label = "⬡ SHIELD"
            col = POWERUP_COLORS["shield"]
            remaining_txt = "until hit"
        else:
            remaining = max(0, effect_ms - (now - effect_start)) // 1000
            label = {"speed": "SPEED BOOST", "slow": "SLOW MO"}[active_effect]
            col = POWERUP_COLORS[active_effect]
            remaining_txt = f"{remaining}s"

        draw_text(surface, label, fonts["label"], col, cx, y, "center")
        y += 20
        draw_text(surface, remaining_txt, fonts["small"], col, cx, y, "center")
        y += 28

    # Legend
    y = WINDOW_HEIGHT - 120
    pygame.draw.line(surface, MID_GRAY, (SIDEBAR_X + 10, y), (SIDEBAR_X + SIDEBAR_WIDTH - 10, y))
    y += 10
    draw_text(surface, "LEGEND", fonts["label"], LIGHT_GRAY, cx, y, "center")
    y += 20
    items = [
        (RED,                    "Food"),
        (YELLOW,                 "Bonus (timed)"),
        (CYAN,                   "Rare (timed)"),
        (POISON_COLOR,           "Poison"),
        (POWERUP_COLORS["speed"],"Speed boost"),
        (POWERUP_COLORS["slow"], "Slow motion"),
        (POWERUP_COLORS["shield"],"Shield"),
    ]
    for col, lbl in items:
        pygame.draw.circle(surface, col, (SIDEBAR_X + 14, y + 7), 5)
        draw_text(surface, lbl, fonts["tiny"], LIGHT_GRAY, SIDEBAR_X + 24, y)
        y += 16


# ─────────────────────────────────────────────────────────────
#  Screens
# ─────────────────────────────────────────────────────────────

class Screen:
    def __init__(self, app):
        self.app = app

    def handle_event(self, event):
        pass

    def update(self):
        pass

    def draw(self, surface):
        pass


# ── Main Menu ─────────────────────────────────────────────────

class MainMenuScreen(Screen):
    def __init__(self, app):
        super().__init__(app)
        self.username = app.username
        self.typing = False
        self.cursor_visible = True
        self.cursor_timer = 0
        self.buttons = {}

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            mx, my = event.pos
            if self.buttons.get("username_box") and self.buttons["username_box"].collidepoint(mx, my):
                self.typing = True
            else:
                self.typing = False

            if self.buttons.get("play") and self.buttons["play"].collidepoint(mx, my):
                if self.username.strip():
                    self.app.start_game()
            elif self.buttons.get("leaderboard") and self.buttons["leaderboard"].collidepoint(mx, my):
                self.app.show_leaderboard()
            elif self.buttons.get("settings") and self.buttons["settings"].collidepoint(mx, my):
                self.app.show_settings()
            elif self.buttons.get("quit") and self.buttons["quit"].collidepoint(mx, my):
                self.app.quit()

        if event.type == pygame.KEYDOWN and self.typing:
            if event.key == pygame.K_BACKSPACE:
                self.username = self.username[:-1]
            elif event.key == pygame.K_RETURN:
                self.typing = False
            elif len(self.username) < 20 and event.unicode.isprintable():
                self.username += event.unicode
            self.app.username = self.username

    def update(self):
        now = pygame.time.get_ticks()
        if now - self.cursor_timer > 500:
            self.cursor_visible = not self.cursor_visible
            self.cursor_timer = now

    def draw(self, surface):
        surface.fill(BG_COLOR)
        f = self.app.fonts
        cx = WINDOW_WIDTH // 2

        # Title
        draw_text(surface, "🐍  SNAKE", f["huge"], ACCENT, cx, 60, "center")
        draw_text(surface, "TSIS 4  —  Advanced Edition", f["label"], MID_GRAY, cx, 115, "center")

        # Username
        y = 180
        draw_text(surface, "Enter your username:", f["body"], LIGHT_GRAY, cx, y, "center")
        y += 34
        box = pygame.Rect(cx - 150, y, 300, 40)
        pygame.draw.rect(surface, DARK_GRAY, box, border_radius=6)
        border_col = ACCENT if self.typing else MID_GRAY
        pygame.draw.rect(surface, border_col, box, 2, border_radius=6)
        txt = self.username + ("|" if self.typing and self.cursor_visible else "")
        draw_text(surface, txt, f["body"], WHITE, cx, y + 8, "center")
        self.buttons["username_box"] = box
        y += 70

        # Buttons
        btn_w, btn_h = 220, 48
        gap = 14
        can_play = bool(self.username.strip())
        play_col = ACCENT if can_play else MID_GRAY
        self.buttons["play"] = make_button(cx, y, btn_w, btn_h, "PLAY", f["body"], play_col, surface, BLACK)
        y += btn_h + gap
        self.buttons["leaderboard"] = make_button(cx, y, btn_w, btn_h, "LEADERBOARD", f["body"], DARK_GRAY, surface, WHITE)
        y += btn_h + gap
        self.buttons["settings"] = make_button(cx, y, btn_w, btn_h, "SETTINGS", f["body"], DARK_GRAY, surface, WHITE)
        y += btn_h + gap
        self.buttons["quit"] = make_button(cx, y, btn_w, btn_h, "QUIT", f["body"], (60, 20, 20), surface, WHITE)

        # Hint
        if not can_play:
            draw_text(surface, "Type a username to start", f["small"], ORANGE, cx, y + btn_h + 20, "center")


# ── Playing ───────────────────────────────────────────────────

class PlayingScreen(Screen):
    def __init__(self, app, player_id: int, personal_best: int):
        super().__init__(app)
        self.player_id = player_id
        self.personal_best = personal_best
        self.state = GameState(app.settings["snake_color"])
        self.paused = False

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.paused = not self.paused
            if not self.paused:
                if event.key in (pygame.K_UP, pygame.K_w):
                    self.state.snake.set_direction(0, -1)
                elif event.key in (pygame.K_DOWN, pygame.K_s):
                    self.state.snake.set_direction(0, 1)
                elif event.key in (pygame.K_LEFT, pygame.K_a):
                    self.state.snake.set_direction(-1, 0)
                elif event.key in (pygame.K_RIGHT, pygame.K_d):
                    self.state.snake.set_direction(1, 0)

    def update(self):
        if self.paused:
            return
        result, sounds = self.state.update()
        for snd in sounds:
            self.app.sounds.play(snd)
        if result == "dead":
            # Save to DB
            db.save_session(self.player_id, self.state.score, self.state.level)
            new_best = max(self.personal_best, self.state.score)
            self.app.show_game_over(self.state.score, self.state.level, new_best)

    def draw(self, surface):
        self.state.draw(surface, self.app.settings)
        draw_sidebar(
            surface,
            self.app.fonts,
            self.state.score,
            self.state.level,
            self.personal_best,
            self.state.active_effect,
            self.state.effect_start,
            POWERUP_EFFECT_MS,
        )
        if self.paused:
            overlay = pygame.Surface((PLAY_AREA_WIDTH, PLAY_AREA_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 140))
            surface.blit(overlay, (0, 0))
            draw_text(surface, "PAUSED", self.app.fonts["huge"], ACCENT, PLAY_AREA_WIDTH // 2, PLAY_AREA_HEIGHT // 2 - 30, "center")
            draw_text(surface, "Press ESC to resume", self.app.fonts["body"], LIGHT_GRAY, PLAY_AREA_WIDTH // 2, PLAY_AREA_HEIGHT // 2 + 20, "center")


# ── Game Over ─────────────────────────────────────────────────

class GameOverScreen(Screen):
    def __init__(self, app, score: int, level: int, personal_best: int):
        super().__init__(app)
        self.score = score
        self.level = level
        self.personal_best = personal_best
        self.buttons = {}

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            mx, my = event.pos
            if self.buttons.get("retry") and self.buttons["retry"].collidepoint(mx, my):
                self.app.start_game()
            elif self.buttons.get("menu") and self.buttons["menu"].collidepoint(mx, my):
                self.app.show_main_menu()

    def draw(self, surface):
        surface.fill(BG_COLOR)
        f = self.app.fonts
        cx = WINDOW_WIDTH // 2

        draw_text(surface, "GAME OVER", f["huge"], RED, cx, 80, "center")

        y = 180
        stats = [
            ("Final Score", str(self.score), WHITE),
            ("Level Reached", str(self.level), YELLOW),
            ("Personal Best", str(self.personal_best), CYAN),
        ]
        for label, val, col in stats:
            draw_text(surface, label, f["label"], LIGHT_GRAY, cx - 10, y, "right")
            draw_text(surface, val, f["big"], col, cx + 10, y - 4, "left")
            y += 50

        if self.score >= self.personal_best and self.score > 0:
            draw_text(surface, "NEW PERSONAL BEST!", f["body"], ACCENT, cx, y, "center")
            y += 34

        y += 10
        btn_w, btn_h = 220, 48
        self.buttons["retry"] = make_button(cx, y, btn_w, btn_h, "RETRY", f["body"], ACCENT, surface, BLACK)
        y += btn_h + 14
        self.buttons["menu"] = make_button(cx, y, btn_w, btn_h, "MAIN MENU", f["body"], DARK_GRAY, surface, WHITE)


# ── Leaderboard ───────────────────────────────────────────────

class LeaderboardScreen(Screen):
    def __init__(self, app):
        super().__init__(app)
        self.rows = db.get_leaderboard(10)
        self.buttons = {}

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            mx, my = event.pos
            if self.buttons.get("back") and self.buttons["back"].collidepoint(mx, my):
                self.app.show_main_menu()

    def draw(self, surface):
        surface.fill(BG_COLOR)
        f = self.app.fonts
        cx = WINDOW_WIDTH // 2

        draw_text(surface, "LEADERBOARD", f["huge"], YELLOW, cx, 30, "center")

        # Table header
        y = 90
        cols_x = [60, 120, 340, 460, 560]
        headers = ["#", "Player", "Score", "Level", "Date"]
        for hdr, x in zip(headers, cols_x):
            draw_text(surface, hdr, f["label"], ACCENT, x, y)
        y += 24
        pygame.draw.line(surface, MID_GRAY, (50, y), (WINDOW_WIDTH - 50, y))
        y += 6

        if not self.rows:
            draw_text(surface, "No scores yet — be the first!", f["body"], LIGHT_GRAY, cx, y + 40, "center")
        else:
            for i, row in enumerate(self.rows):
                bg_col = (20, 30, 20) if i % 2 == 0 else BG_COLOR
                row_rect = pygame.Rect(50, y, WINDOW_WIDTH - 100, 24)
                pygame.draw.rect(surface, bg_col, row_rect)

                rank_col = (YELLOW, LIGHT_GRAY, (180, 100, 50))[min(i, 2)] if i < 3 else LIGHT_GRAY
                date_str = row["played_at"].strftime("%d %b") if row.get("played_at") else "—"
                cells = [
                    str(i + 1),
                    str(row["username"])[:16],
                    str(row["score"]),
                    str(row["level_reached"]),
                    date_str,
                ]
                for val, x in zip(cells, cols_x):
                    draw_text(surface, val, f["small"], rank_col if i < 3 else WHITE, x, y + 2)
                y += 26

        self.buttons["back"] = make_button(cx, WINDOW_HEIGHT - 54, 200, 44, "← BACK", f["body"], DARK_GRAY, surface, WHITE)


# ── Settings ──────────────────────────────────────────────────

PRESET_COLORS = [
    ((0, 200, 80),   "Green"),
    ((0, 180, 220),  "Cyan"),
    ((220, 80, 220), "Purple"),
    ((220, 140, 0),  "Orange"),
    ((220, 60, 60),  "Red"),
    ((255, 255, 255),"White"),
]


class SettingsScreen(Screen):
    def __init__(self, app):
        super().__init__(app)
        self.tmp = {
            "snake_color": list(app.settings["snake_color"]),
            "grid_overlay": app.settings["grid_overlay"],
            "sound": app.settings["sound"],
        }
        self.buttons = {}

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            mx, my = event.pos

            if self.buttons.get("grid") and self.buttons["grid"].collidepoint(mx, my):
                self.tmp["grid_overlay"] = not self.tmp["grid_overlay"]
            if self.buttons.get("sound") and self.buttons["sound"].collidepoint(mx, my):
                self.tmp["sound"] = not self.tmp["sound"]

            for (col, _), rect in self.buttons.get("colors", []):
                if rect.collidepoint(mx, my):
                    self.tmp["snake_color"] = list(col)

            if self.buttons.get("save") and self.buttons["save"].collidepoint(mx, my):
                self.app.settings.update(self.tmp)
                save_settings(self.app.settings)
                self.app.sounds.set_enabled(self.app.settings.get("sound", False))
                self.app.show_main_menu()

            if self.buttons.get("back") and self.buttons["back"].collidepoint(mx, my):
                self.app.show_main_menu()

    def draw(self, surface):
        surface.fill(BG_COLOR)
        f = self.app.fonts
        cx = WINDOW_WIDTH // 2

        draw_text(surface, "SETTINGS", f["huge"], ACCENT, cx, 40, "center")

        y = 130
        # Grid toggle
        g_col = ACCENT if self.tmp["grid_overlay"] else MID_GRAY
        g_lbl = "Grid Overlay:  ON" if self.tmp["grid_overlay"] else "Grid Overlay:  OFF"
        self.buttons["grid"] = make_button(cx, y, 260, 44, g_lbl, f["body"], g_col, surface, BLACK if self.tmp["grid_overlay"] else WHITE)
        y += 60

        # Sound toggle
        s_col = ACCENT if self.tmp["sound"] else MID_GRAY
        s_lbl = "Sound:  ON" if self.tmp["sound"] else "Sound:  OFF"
        self.buttons["sound"] = make_button(cx, y, 260, 44, s_lbl, f["body"], s_col, surface, BLACK if self.tmp["sound"] else WHITE)
        y += 60

        # Color presets
        draw_text(surface, "Snake Color:", f["label"], LIGHT_GRAY, cx, y, "center")
        y += 30
        self.buttons["colors"] = []
        total_w = len(PRESET_COLORS) * 48 + (len(PRESET_COLORS) - 1) * 10
        start_x = cx - total_w // 2
        for i, (col, name) in enumerate(PRESET_COLORS):
            rect = pygame.Rect(start_x + i * 58, y, 44, 44)
            pygame.draw.rect(surface, col, rect, border_radius=6)
            if list(col) == self.tmp["snake_color"]:
                pygame.draw.rect(surface, WHITE, rect, 3, border_radius=6)
            self.buttons["colors"].append(((col, name), rect))
        y += 70

        # Save / Back
        self.buttons["save"] = make_button(cx - 70, y, 120, 44, "SAVE", f["body"], ACCENT, surface, BLACK)
        self.buttons["back"] = make_button(cx + 70, y, 120, 44, "BACK", f["body"], DARK_GRAY, surface, WHITE)


# ─────────────────────────────────────────────────────────────
#  App
# ─────────────────────────────────────────────────────────────

class App:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption(TITLE)
        self.clock = pygame.time.Clock()
        self.settings = load_settings()
        self.username = ""
        self.player_id: int | None = None
        self.personal_best: int = 0
        self.db_available = db.init_db()

        self.fonts = self._load_fonts()
        self.sounds = SoundManager()
        self.sounds.set_enabled(self.settings.get("sound", False))
        self.current_screen: Screen = MainMenuScreen(self)

    def _load_fonts(self) -> dict:
        try:
            pygame.font.init()
            mono = "monospace"
            return {
                "huge":  pygame.font.SysFont(mono, 42, bold=True),
                "big":   pygame.font.SysFont(mono, 30, bold=True),
                "title": pygame.font.SysFont(mono, 22, bold=True),
                "body":  pygame.font.SysFont(mono, 18),
                "label": pygame.font.SysFont(mono, 14, bold=True),
                "small": pygame.font.SysFont(mono, 13),
                "tiny":  pygame.font.SysFont(mono, 11),
            }
        except Exception:
            f = pygame.font.Font(None, 24)
            return {k: f for k in ["huge", "big", "title", "body", "label", "small", "tiny"]}

    # ── Navigation ───────────────────────────────────────────

    def show_main_menu(self):
        self.current_screen = MainMenuScreen(self)

    def start_game(self):
        if not self.username.strip():
            return
        if self.db_available:
            self.player_id = db.get_or_create_player(self.username.strip())
            self.personal_best = db.get_personal_best(self.player_id) if self.player_id else 0
        else:
            self.player_id = -1
            self.personal_best = 0
        self.current_screen = PlayingScreen(self, self.player_id, self.personal_best)

    def show_game_over(self, score: int, level: int, personal_best: int):
        self.personal_best = personal_best
        self.current_screen = GameOverScreen(self, score, level, personal_best)

    def show_leaderboard(self):
        self.current_screen = LeaderboardScreen(self)

    def show_settings(self):
        self.current_screen = SettingsScreen(self)

    def quit(self):
        db.close()
        pygame.quit()
        sys.exit()

    # ── Main loop ────────────────────────────────────────────

    def run(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.quit()
                self.current_screen.handle_event(event)

            self.current_screen.update()
            self.current_screen.draw(self.screen)
            pygame.display.flip()
            self.clock.tick(FPS)


if __name__ == "__main__":
    App().run()