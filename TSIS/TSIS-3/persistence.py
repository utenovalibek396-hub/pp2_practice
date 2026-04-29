import json
import os
from datetime import datetime
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

LEADERBOARD_FILE = os.path.join(BASE_DIR, "leaderboard.json")
SETTINGS_FILE    = os.path.join(BASE_DIR, "settings.json")

DEFAULT_SETTINGS = {
    "sound":       True,
    "car_color":   [220, 60, 60],
    "difficulty":  "normal",
}

DIFFICULTY_PARAMS = {
    "easy":   {"spawn_rate": 0.012, "enemy_speed": 4, "scale": 0.6},
    "normal": {"spawn_rate": 0.020, "enemy_speed": 6, "scale": 1.0},
    "hard":   {"spawn_rate": 0.030, "enemy_speed": 9, "scale": 1.5},
}

def load_settings() -> dict:
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            merged = DEFAULT_SETTINGS.copy()
            merged.update(data)
            return merged
        except: pass
    return DEFAULT_SETTINGS.copy()

def save_settings(settings: dict) -> None:
    with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
        json.dump(settings, f, indent=2)

def load_leaderboard() -> list:
    if os.path.exists(LEADERBOARD_FILE):
        try:
            with open(LEADERBOARD_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            if isinstance(data, list): return data
        except: pass
    return []

def save_score(name: str, score: int, distance: int, coins: int) -> None:
    board = load_leaderboard()
    board.append({
        "name":     name,
        "score":    score,
        "distance": distance,
        "coins":    coins,
        "date":     datetime.now().strftime("%Y-%m-%d")
    })
    board.sort(key=lambda x: x["score"], reverse=True)
    with open(LEADERBOARD_FILE, "w", encoding="utf-8") as f:
        json.dump(board[:10], f, indent=2)