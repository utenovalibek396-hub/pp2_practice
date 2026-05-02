import json  # Import the json module to work with JSON file formats
import os  # Import the os module to handle file and directory paths
from datetime import datetime  # Import datetime to get current date for score entries

LEADERBOARD_FILE = "leaderboard.json"  # Define the filename for storing high scores
SETTINGS_FILE    = "settings.json"  # Define the filename for storing user settings

DEFAULT_SETTINGS = {  # Create a dictionary containing the default game configuration
    "sound":       True,  # Default audio state (enabled)
    "car_color":   [220, 60, 60],  # Default car color in RGB format
    "difficulty":  "normal",  # Default difficulty level
}

DIFFICULTY_PARAMS = {  # Define specific game constants for each difficulty level
    "easy":   {"spawn_rate": 0.012, "enemy_speed": 4, "scale": 0.6},  # Parameters for easy mode
    "normal": {"spawn_rate": 0.020, "enemy_speed": 6, "scale": 1.0},  # Parameters for normal mode
    "hard":   {"spawn_rate": 0.030, "enemy_speed": 9, "scale": 1.5},  # Parameters for hard mode
}

def load_settings() -> dict:  # Define a function to load settings, returning a dictionary
    if os.path.exists(SETTINGS_FILE):  # Check if the settings file exists in the directory
        try:  # Use a try block to handle potential file reading errors
            with open(SETTINGS_FILE, "r", encoding="utf-8") as f:  # Open the settings file in read mode
                data = json.load(f)  # Parse the JSON data into a Python dictionary
            merged = DEFAULT_SETTINGS.copy()  # Create a copy of the default settings
            merged.update(data)  # Overwrite defaults with any values found in the file
            return merged  # Return the merged dictionary of settings
        except: pass  # If an error occurs, skip the remaining logic in the try block
    return DEFAULT_SETTINGS.copy()  # Return default settings if file doesn't exist or is corrupted

def save_settings(settings: dict) -> None:  # Define a function to save the settings dictionary to a file
    with open(SETTINGS_FILE, "w", encoding="utf-8") as f:  # Open the settings file in write mode
        json.dump(settings, f, indent=2)  # Write the dictionary as JSON with 2-space indentation

def load_leaderboard() -> list:  # Define a function to load the high score list
    if os.path.exists(LEADERBOARD_FILE):  # Check if the leaderboard file exists
        try:  # Use a try block to handle potential JSON parsing issues
            with open(LEADERBOARD_FILE, "r", encoding="utf-8") as f:  # Open the leaderboard file
                data = json.load(f)  # Load the file content into a Python object
            if isinstance(data, list): return data  # Return data only if it is correctly stored as a list
        except: pass  # If an error occurs, proceed to return an empty list
    return []  # Return an empty list if file doesn't exist or is invalid

def save_score(name: str, score: int, distance: int, coins: int) -> None:  # Function to save a new record
    board = load_leaderboard()  # Retrieve the current list of high scores
    board.append({  # Add a new dictionary representing the current game session
        "name":     name,  # Store the player's name
        "score":    score,  # Store the total points achieved
        "distance": distance,  # Store the distance traveled in meters
        "coins":    coins,  # Store the amount of coins collected
        "date":     datetime.now().strftime("%Y-%m-%d")  # Store the date of the record (Year-Month-Day)
    })  # End of the new entry dictionary
    board.sort(key=lambda x: x["score"], reverse=True)  # Sort the list by score in descending order
    with open(LEADERBOARD_FILE, "w", encoding="utf-8") as f:  # Open the leaderboard file for writing
        json.dump(board[:10], f, indent=2)  # Save only the top 10 scores to the file in JSON format