# config.py — Game Configuration Constants

# Window
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
TITLE = "Snake Game — TSIS 4"
FPS = 60

# Grid
CELL_SIZE = 20
GRID_COLS = 30   # 600 px play area
GRID_ROWS = 30   # 600 px play area
PLAY_AREA_X = 0
PLAY_AREA_Y = 0
PLAY_AREA_WIDTH = CELL_SIZE * GRID_COLS   # 600
PLAY_AREA_HEIGHT = CELL_SIZE * GRID_ROWS  # 600
SIDEBAR_X = PLAY_AREA_WIDTH
SIDEBAR_WIDTH = WINDOW_WIDTH - PLAY_AREA_WIDTH  # 200

# Snake base speed (moves per second)
BASE_SPEED = 8
SPEED_INCREMENT = 1   # added per level

# Level progression
FOOD_PER_LEVEL = 5

# Food timers (ms)
FOOD_DISAPPEAR_MS = 7000   # timed food vanishes after 7 s

# Power-up settings (ms)
POWERUP_FIELD_MS = 8000    # power-up stays on field 8 s
POWERUP_EFFECT_MS = 5000   # effect lasts 5 s
SPEED_BOOST_FACTOR = 1.6
SLOW_FACTOR = 0.5

# Obstacle
OBSTACLE_LEVEL_START = 3
OBSTACLES_PER_LEVEL = 5    # extra blocks added each qualifying level

# Colours (R, G, B)
BLACK       = (0, 0, 0)
WHITE       = (255, 255, 255)
DARK_GRAY   = (30, 30, 30)
MID_GRAY    = (60, 60, 60)
LIGHT_GRAY  = (180, 180, 180)
GREEN       = (0, 200, 80)
DARK_GREEN  = (0, 140, 50)
RED         = (220, 40, 40)
DARK_RED    = (140, 0, 0)
ORANGE      = (255, 140, 0)
YELLOW      = (255, 215, 0)
CYAN        = (0, 220, 220)
PURPLE      = (160, 32, 240)
BLUE        = (30, 100, 220)
WALL_COLOR  = (100, 100, 120)
BG_COLOR    = (15, 15, 25)
GRID_COLOR  = (25, 25, 40)
SIDEBAR_BG  = (10, 10, 20)
ACCENT      = (0, 255, 120)

# Food colours / weights
FOOD_TYPES = [
    {"color": (255, 80, 80),  "points": 1, "timed": False, "label": "normal"},
    {"color": (255, 200, 0),  "points": 3, "timed": True,  "label": "bonus"},
    {"color": (0, 200, 255),  "points": 5, "timed": True,  "label": "rare"},
]

POISON_COLOR = DARK_RED

# Power-up colours
POWERUP_COLORS = {
    "speed":  (255, 165, 0),
    "slow":   (100, 149, 237),
    "shield": (50, 205, 50),
}

# DB (override via environment variables if needed)
DB_HOST = "localhost"
DB_PORT = 5432
DB_NAME = "snake_game"
DB_USER = "postgres"
DB_PASS = "123456789qaz"