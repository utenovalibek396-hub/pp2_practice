# main.py — Entry point & all game screens

import pygame                                          # Import the core Pygame library for game development
import sys                                             # Import sys for system-specific functions like exiting
import json                                            # Import json to handle settings file parsing and saving
import os                                              # Import os for file path and directory operations
from datetime import datetime                          # Import datetime for timestamping game sessions
from config import *                                   # Import all constants and colors from config module
import db                                              # Import the custom database handler module
from game import GameState, SoundManager               # Import the game logic and sound management classes

# ─────────────────────────────────────────────────────────────
#  Settings helpers
# ─────────────────────────────────────────────────────────────

SETTINGS_FILE = os.path.join(os.path.dirname(__file__), "settings.json") # Define the absolute path for settings file

DEFAULT_SETTINGS = {                                   # Define a dictionary containing default game configurations
    "snake_color": list(GREEN),                        # Set the default snake color to green (from config)
    "grid_overlay": True,                              # Enable the background grid by default
    "sound": False,                                    # Keep sound disabled by default
}


def load_settings() -> dict:                           # Function to load settings from the JSON file
    try:                                               # Start a try block to handle potential file errors
        with open(SETTINGS_FILE, "r") as f:            # Open the settings file in read mode
            data = json.load(f)                        # Parse the JSON content into a Python dictionary
        # Fill missing keys with defaults
        for k, v in DEFAULT_SETTINGS.items():          # Iterate through all default setting keys
            data.setdefault(k, v)                      # Ensure all necessary keys exist, otherwise use defaults
        return data                                    # Return the loaded and verified settings data
    except Exception:                                  # Execute if file is missing or contains invalid JSON
        return dict(DEFAULT_SETTINGS)                  # Return a copy of the default settings


def save_settings(settings: dict):                     # Function to write settings back to the JSON file
    try:                                               # Start a try block to catch file writing errors
        with open(SETTINGS_FILE, "w") as f:            # Open the settings file in write mode
            json.dump(settings, f, indent=4)           # Serialize the dictionary to JSON with 4-space indentation
    except Exception as e:                             # Catch any exception during the saving process
        print(f"[Settings] save error: {e}")           # Print the error message to the console for debugging


# ─────────────────────────────────────────────────────────────
#  UI Helpers
# ─────────────────────────────────────────────────────────────

def draw_text(surface, text, font, color, x, y, align="left"): # Helper to render text on a specific surface
    surf = font.render(text, True, color)              # Create a text surface with antialiasing enabled
    if align == "center":                              # Check if the text should be horizontally centered
        rect = surf.get_rect(centerx=x, y=y)           # Get rect centered on X coordinate at specified Y
    elif align == "right":                             # Check if the text should be right-aligned
        rect = surf.get_rect(right=x, y=y)             # Get rect with the right edge at specified X and Y
    else:                                              # Default behavior for left alignment
        rect = surf.get_rect(x=x, y=y)                 # Get rect with the top-left corner at (x, y)
    surface.blit(surf, rect)                           # Draw the text surface onto the destination surface
    return rect                                        # Return the rectangle for further collision or UI logic


def draw_button(surface, text, font, rect, color, text_color=BLACK, radius=8): # Function to draw a styled button
    pygame.draw.rect(surface, color, rect, border_radius=radius) # Draw the main button body with rounded corners
    pygame.draw.rect(surface, WHITE, rect, 2, border_radius=radius) # Draw the button's white border outline
    t = font.render(text, True, text_color)            # Render the button's text label
    surface.blit(t, t.get_rect(center=rect.center))    # Draw text centered perfectly inside the button rect
    return rect                                        # Return the button's rectangle for mouse click detection


def make_button(cx, cy, w, h, text, font, color, surface=None, text_color=BLACK): # Helper to create button rects
    rect = pygame.Rect(0, 0, w, h)                     # Initialize a new rectangle with width and height
    rect.center = (cx, cy)                             # Position the rectangle's center at (cx, cy)
    if surface:                                        # If a surface is provided, draw the button immediately
        draw_button(surface, text, font, rect, color, text_color) # Call the draw_button function to render it
    return rect                                        # Return the rectangle object for the button


def draw_sidebar(surface, fonts, score, level, personal_best, active_effect, effect_start, effect_ms): # UI sidebar
    sidebar = pygame.Rect(SIDEBAR_X, 0, SIDEBAR_WIDTH, WINDOW_HEIGHT) # Define the sidebar area rectangle
    pygame.draw.rect(surface, SIDEBAR_BG, sidebar)     # Fill the sidebar background with its specific color
    pygame.draw.line(surface, ACCENT, (SIDEBAR_X, 0), (SIDEBAR_X, WINDOW_HEIGHT), 2) # Draw a vertical separator line

    cx = SIDEBAR_X + SIDEBAR_WIDTH // 2                # Calculate the horizontal center point of the sidebar
    y = 20                                             # Set the starting vertical offset for sidebar elements

    draw_text(surface, "SNAKE", fonts["title"], ACCENT, cx, y, "center") # Draw the game title in the sidebar
    y += 36                                            # Increment Y to move to the next section

    pygame.draw.line(surface, MID_GRAY, (SIDEBAR_X + 10, y), (SIDEBAR_X + SIDEBAR_WIDTH - 10, y)) # Draw horizontal divider
    y += 12                                            # Add spacing after the line

    draw_text(surface, "SCORE", fonts["label"], LIGHT_GRAY, cx, y, "center") # Draw the "SCORE" label
    y += 20                                            # Move down for the actual score value
    draw_text(surface, str(score), fonts["big"], WHITE, cx, y, "center") # Draw current score in big font
    y += 44                                            # Add space for the level section

    draw_text(surface, f"LEVEL  {level}", fonts["label"], YELLOW, cx, y, "center") # Display the current game level
    y += 28                                            # Move down for personal best section

    draw_text(surface, f"BEST  {personal_best}", fonts["label"], CYAN, cx, y, "center") # Display the player's high score
    y += 40                                            # Move down for the next section

    pygame.draw.line(surface, MID_GRAY, (SIDEBAR_X + 10, y), (SIDEBAR_X + SIDEBAR_WIDTH - 10, y)) # Draw another divider
    y += 12                                            # Add spacing after the line

    # Active effect
    if active_effect:                                  # Check if there is an active power-up effect
        now = pygame.time.get_ticks()                  # Get current time in milliseconds
        if active_effect == "shield":                  # Specific handling for the shield effect
            label = "⬡ SHIELD"                         # Set the label for shield
            col = POWERUP_COLORS["shield"]             # Get the color assigned to the shield power-up
            remaining_txt = "until hit"                # Shield doesn't expire by time, but by contact
        else:                                          # Handling for timed effects like speed or slow
            remaining = max(0, effect_ms - (now - effect_start)) // 1000 # Calculate remaining seconds
            label = {"speed": "SPEED BOOST", "slow": "SLOW MO"}[active_effect] # Map effect name to display name
            col = POWERUP_COLORS[active_effect]        # Get the corresponding color for the effect
            remaining_txt = f"{remaining}s"            # Format the remaining time as a string

        draw_text(surface, label, fonts["label"], col, cx, y, "center") # Draw the power-up name
        y += 20                                        # Move down for time remaining
        draw_text(surface, remaining_txt, fonts["small"], col, cx, y, "center") # Draw the duration text
        y += 28                                        # Add bottom spacing

    # Legend
    y = WINDOW_HEIGHT - 120                            # Position the legend section near the bottom
    pygame.draw.line(surface, MID_GRAY, (SIDEBAR_X + 10, y), (SIDEBAR_X + SIDEBAR_WIDTH - 10, y)) # Legend divider
    y += 10                                            # Add spacing
    draw_text(surface, "LEGEND", fonts["label"], LIGHT_GRAY, cx, y, "center") # Draw "LEGEND" heading
    y += 20                                            # Move to list items
    items = [                                          # Define a list of legend items with colors and labels
        (RED,                    "Food"),              # Basic food item
        (YELLOW,                 "Bonus (timed)"),     # Time-limited bonus food
        (CYAN,                   "Rare (timed)"),      # High-value rare food
        (POISON_COLOR,           "Poison"),            # Harmful poison item
        (POWERUP_COLORS["speed"],"Speed boost"),       # Speed increase power-up
        (POWERUP_COLORS["slow"], "Slow motion"),       # Speed decrease power-up
        (POWERUP_COLORS["shield"],"Shield"),           # Protective shield power-up
    ]
    for col, lbl in items:                             # Loop through each legend item to draw it
        pygame.draw.circle(surface, col, (SIDEBAR_X + 14, y + 7), 5) # Draw a colored circle for the item
        draw_text(surface, lbl, fonts["tiny"], LIGHT_GRAY, SIDEBAR_X + 24, y) # Draw the item description
        y += 16                                        # Move to the next row in the legend


# ─────────────────────────────────────────────────────────────
#  Screens
# ─────────────────────────────────────────────────────────────

class Screen:                                          # Base class for all different game states/screens
    def __init__(self, app):                           # Initialize the screen with a reference to the main app
        self.app = app                                 # Store the app instance for switching screens

    def handle_event(self, event):                     # Virtual method to handle user input events
        pass                                           # To be overridden in child classes

    def update(self):                                  # Virtual method to update screen logic every frame
        pass                                           # To be overridden in child classes

    def draw(self, surface):                           # Virtual method to render screen content
        pass                                           # To be overridden in child classes


# ── Main Menu ─────────────────────────────────────────────────

class MainMenuScreen(Screen):                          # Class representing the main menu screen
    def __init__(self, app):                           # Initialize the main menu variables
        super().__init__(app)                          # Call parent Screen constructor
        self.username = app.username                   # Link to the app's current username string
        self.typing = False                            # Boolean to track if the user is currently typing
        self.cursor_visible = True                     # Boolean for the blinking text cursor
        self.cursor_timer = 0                          # Timer to handle cursor blink rate
        self.buttons = {}                              # Dictionary to store button rectangles for interaction

    def handle_event(self, event):                     # Process input for the main menu
        if event.type == pygame.MOUSEBUTTONDOWN:       # Check if the user clicked the mouse
            mx, my = event.pos                         # Get the (x, y) coordinates of the click
            if self.buttons.get("username_box") and self.buttons["username_box"].collidepoint(mx, my): # Box click
                self.typing = True                     # Enable typing mode when clicking the username box
            else:                                      # Clicking anywhere else
                self.typing = False                    # Disable typing mode

            if self.buttons.get("play") and self.buttons["play"].collidepoint(mx, my): # Play button click
                if self.username.strip():              # Only start if the username is not empty
                    self.app.start_game()              # Trigger game start in the main app
            elif self.buttons.get("leaderboard") and self.buttons["leaderboard"].collidepoint(mx, my): # Leaderboard
                self.app.show_leaderboard()            # Switch to the leaderboard screen
            elif self.buttons.get("settings") and self.buttons["settings"].collidepoint(mx, my): # Settings
                self.app.show_settings()               # Switch to the settings screen
            elif self.buttons.get("quit") and self.buttons["quit"].collidepoint(mx, my): # Quit button click
                self.app.quit()                        # Exit the application

        if event.type == pygame.KEYDOWN and self.typing: # Process keyboard input if typing is active
            if event.key == pygame.K_BACKSPACE:        # Handle backspace key
                self.username = self.username[:-1]     # Remove the last character from the username
            elif event.key == pygame.K_RETURN:         # Handle enter/return key
                self.typing = False                    # Stop typing mode
            elif len(self.username) < 20 and event.unicode.isprintable(): # Allow printable characters
                self.username += event.unicode         # Append the typed character to the username string
            self.app.username = self.username          # Sync the username with the main app state

    def update(self):                                  # Update logic for the main menu (cursor blinking)
        now = pygame.time.get_ticks()                  # Get the current system time
        if now - self.cursor_timer > 500:               # Toggle every 500 milliseconds
            self.cursor_visible = not self.cursor_visible # Invert the cursor visibility boolean
            self.cursor_timer = now                    # Reset the timer for the next blink

    def draw(self, surface):                           # Render the main menu to the screen
        surface.fill(BG_COLOR)                         # Clear the screen with the background color
        f = self.app.fonts                             # Shortcut to the loaded fonts dictionary
        cx = WINDOW_WIDTH // 2                         # Center X coordinate of the window

        # Title
        draw_text(surface, "🐍  SNAKE", f["huge"], ACCENT, cx, 60, "center") # Draw big title with icon
        draw_text(surface, "TSIS 4  —  Advanced Edition", f["label"], MID_GRAY, cx, 115, "center") # Subtitle

        # Username
        y = 180                                        # Y offset for username input section
        draw_text(surface, "Enter your username:", f["body"], LIGHT_GRAY, cx, y, "center") # Prompt label
        y += 34                                        # Move down for the input box
        box = pygame.Rect(cx - 150, y, 300, 40)        # Define the username input box area
        pygame.draw.rect(surface, DARK_GRAY, box, border_radius=6) # Draw the box background
        border_col = ACCENT if self.typing else MID_GRAY # Highlight border if active typing
        pygame.draw.rect(surface, border_col, box, 2, border_radius=6) # Draw the box border
        txt = self.username + ("|" if self.typing and self.cursor_visible else "") # Append cursor if typing
        draw_text(surface, txt, f["body"], WHITE, cx, y + 8, "center") # Render the actual username text
        self.buttons["username_box"] = box             # Store box rect for collision detection
        y += 70                                        # Move down for menu buttons

        # Buttons
        btn_w, btn_h = 220, 48                         # Standard button dimensions
        gap = 14                                       # Gap between vertical buttons
        can_play = bool(self.username.strip())         # Check if username is valid to enable Play
        play_col = ACCENT if can_play else MID_GRAY    # Use accent color if enabled, gray if disabled
        self.buttons["play"] = make_button(cx, y, btn_w, btn_h, "PLAY", f["body"], play_col, surface, BLACK) # Play
        y += btn_h + gap                               # Move to next button
        self.buttons["leaderboard"] = make_button(cx, y, btn_w, btn_h, "LEADERBOARD", f["body"], DARK_GRAY, surface, WHITE)
        y += btn_h + gap                               # Move to next button
        self.buttons["settings"] = make_button(cx, y, btn_w, btn_h, "SETTINGS", f["body"], DARK_GRAY, surface, WHITE)
        y += btn_h + gap                               # Move to next button
        self.buttons["quit"] = make_button(cx, y, btn_w, btn_h, "QUIT", f["body"], (60, 20, 20), surface, WHITE) # Quit

        # Hint
        if not can_play:                               # Show warning if username is empty
            draw_text(surface, "Type a username to start", f["small"], ORANGE, cx, y + btn_h + 20, "center")


# ── Playing ───────────────────────────────────────────────────

class PlayingScreen(Screen):                           # Class managing the active gameplay state
    def __init__(self, app, player_id: int, personal_best: int): # Setup playing screen data
        super().__init__(app)                          # Parent constructor
        self.player_id = player_id                     # Store the DB player ID
        self.personal_best = personal_best             # Store current high score for display
        self.state = GameState(app.settings["snake_color"]) # Initialize the game logic with chosen color
        self.paused = False                            # Initialize pause state as false

    def handle_event(self, event):                     # Handle gameplay controls
        if event.type == pygame.KEYDOWN:               # Check for key presses
            if event.key == pygame.K_ESCAPE:           # Toggle pause on Escape key
                self.paused = not self.paused          # Flip the pause boolean
            if not self.paused:                        # Only process movement if not paused
                if event.key in (pygame.K_UP, pygame.K_w): # Move Up
                    self.state.snake.set_direction(0, -1) # Set direction vector to (0, -1)
                elif event.key in (pygame.K_DOWN, pygame.K_s): # Move Down
                    self.state.snake.set_direction(0, 1)  # Set direction vector to (0, 1)
                elif event.key in (pygame.K_LEFT, pygame.K_a): # Move Left
                    self.state.snake.set_direction(-1, 0) # Set direction vector to (-1, 0)
                elif event.key in (pygame.K_RIGHT, pygame.K_d): # Move Right
                    self.state.snake.set_direction(1, 0)  # Set direction vector to (1, 0)

    def update(self):                                  # Logical game update loop
        if self.paused:                                # Skip logic updates if paused
            return                                     # Exit update function
        result, sounds = self.state.update()           # Update game state and get sound/event results
        for snd in sounds:                             # Process all sound events triggered during update
            self.app.sounds.play(snd)                  # Play sound through the sound manager
        if result == "dead":                           # Check if the game over condition was met
            # Save to DB
            db.save_session(self.player_id, self.state.score, self.state.level) # Persist score to DB
            new_best = max(self.personal_best, self.state.score) # Calculate if high score was broken
            self.app.show_game_over(self.state.score, self.state.level, new_best) # Transition to Game Over

    def draw(self, surface):                           # Render game world and UI
        self.state.draw(surface, self.app.settings)    # Draw the snake, food, and grid from GameState
        draw_sidebar(                                  # Draw the information sidebar
            surface,                                   # Target surface
            self.app.fonts,                            # App fonts
            self.state.score,                          # Current score
            self.state.level,                          # Current level
            self.personal_best,                        # Best score
            self.state.active_effect,                  # Current power-up effect
            self.state.effect_start,                   # When effect started
            POWERUP_EFFECT_MS,                         # Max duration of effect
        )
        if self.paused:                                # Render pause overlay if active
            overlay = pygame.Surface((PLAY_AREA_WIDTH, PLAY_AREA_HEIGHT), pygame.SRCALPHA) # Transparent surface
            overlay.fill((0, 0, 0, 140))               # Fill with semi-transparent black
            surface.blit(overlay, (0, 0))              # Blit overlay onto the play area
            draw_text(surface, "PAUSED", self.app.fonts["huge"], ACCENT, PLAY_AREA_WIDTH // 2, PLAY_AREA_HEIGHT // 2 - 30, "center")
            draw_text(surface, "Press ESC to resume", self.app.fonts["body"], LIGHT_GRAY, PLAY_AREA_WIDTH // 2, PLAY_AREA_HEIGHT // 2 + 20, "center")


# ── Game Over ─────────────────────────────────────────────────

class GameOverScreen(Screen):                          # Class for the end-of-game summary screen
    def __init__(self, app, score: int, level: int, personal_best: int): # Init with session stats
        super().__init__(app)                          # Parent constructor
        self.score = score                             # Store achieved score
        self.level = level                             # Store reached level
        self.personal_best = personal_best             # Store player's high score
        self.buttons = {}                              # Button dictionary for collision

    def handle_event(self, event):                     # Process input for the game over screen
        if event.type == pygame.MOUSEBUTTONDOWN:       # Mouse click detected
            mx, my = event.pos                         # Get click coordinates
            if self.buttons.get("retry") and self.buttons["retry"].collidepoint(mx, my): # Retry button
                self.app.start_game()                  # Restart the game immediately
            elif self.buttons.get("menu") and self.buttons["menu"].collidepoint(mx, my): # Menu button
                self.app.show_main_menu()              # Return to main menu

    def draw(self, surface):                           # Render the game over screen UI
        surface.fill(BG_COLOR)                         # Reset screen background
        f = self.app.fonts                             # Get app fonts
        cx = WINDOW_WIDTH // 2                         # Screen center X

        draw_text(surface, "GAME OVER", f["huge"], RED, cx, 80, "center") # Display big red title

        y = 180                                        # Y offset for stats
        stats = [                                      # Create a list of stats to display
            ("Final Score", str(self.score), WHITE),   # Show final score
            ("Level Reached", str(self.level), YELLOW),# Show level
            ("Personal Best", str(self.personal_best), CYAN), # Show best score
        ]
        for label, val, col in stats:                  # Iterate and draw each stat row
            draw_text(surface, label, f["label"], LIGHT_GRAY, cx - 10, y, "right") # Stat label
            draw_text(surface, val, f["big"], col, cx + 10, y - 4, "left") # Stat value
            y += 50                                    # Move down for next row

        if self.score >= self.personal_best and self.score > 0: # Check if a new record was set
            draw_text(surface, "NEW PERSONAL BEST!", f["body"], ACCENT, cx, y, "center") # Celebration text
            y += 34                                    # Extra spacing

        y += 10                                        # Spacing before buttons
        btn_w, btn_h = 220, 48                         # Standard button size
        self.buttons["retry"] = make_button(cx, y, btn_w, btn_h, "RETRY", f["body"], ACCENT, surface, BLACK) # Retry
        y += btn_h + 14                                # Space between buttons
        self.buttons["menu"] = make_button(cx, y, btn_w, btn_h, "MAIN MENU", f["body"], DARK_GRAY, surface, WHITE) # Menu


# ── Leaderboard ───────────────────────────────────────────────

class LeaderboardScreen(Screen):                       # Class showing global high scores from DB
    def __init__(self, app):                           # Initialize leaderboard screen
        super().__init__(app)                          # Parent constructor
        self.rows = db.get_leaderboard(10)             # Fetch top 10 scores from the database module
        self.buttons = {}                              # Button tracking dictionary

    def handle_event(self, event):                     # Handle input for leaderboard screen
        if event.type == pygame.MOUSEBUTTONDOWN:       # Mouse click check
            mx, my = event.pos                         # Click position
            if self.buttons.get("back") and self.buttons["back"].collidepoint(mx, my): # Back button
                self.app.show_main_menu()              # Go back to menu screen

    def draw(self, surface):                           # Render the leaderboard table
        surface.fill(BG_COLOR)                         # Clear screen
        f = self.app.fonts                             # Fonts shortcut
        cx = WINDOW_WIDTH // 2                         # Center X

        draw_text(surface, "LEADERBOARD", f["huge"], YELLOW, cx, 30, "center") # Screen title

        # Table header
        y = 90                                         # Start Y for table
        cols_x = [60, 120, 340, 460, 560]              # X offsets for table columns
        headers = ["#", "Player", "Score", "Level", "Date"] # Column headers
        for hdr, x in zip(headers, cols_x):            # Draw each header text
            draw_text(surface, hdr, f["label"], ACCENT, x, y) # Render header
        y += 24                                        # Spacing after header
        pygame.draw.line(surface, MID_GRAY, (50, y), (WINDOW_WIDTH - 50, y)) # Underline for header
        y += 6                                         # Padding after line

        if not self.rows:                              # If no records exist in DB
            draw_text(surface, "No scores yet — be the first!", f["body"], LIGHT_GRAY, cx, y + 40, "center")
        else:                                          # If records are found
            for i, row in enumerate(self.rows):        # Loop through score records
                bg_col = (20, 30, 20) if i % 2 == 0 else BG_COLOR # Alternate row colors for readability
                row_rect = pygame.Rect(50, y, WINDOW_WIDTH - 100, 24) # Row highlight rectangle
                pygame.draw.rect(surface, bg_col, row_rect) # Draw row background

                rank_col = (YELLOW, LIGHT_GRAY, (180, 100, 50))[min(i, 2)] if i < 3 else LIGHT_GRAY # Top 3 colors
                date_str = row["played_at"].strftime("%d %b") if row.get("played_at") else "—" # Format date
                cells = [                              # Prepare cell strings
                    str(i + 1),                        # Rank number
                    str(row["username"])[:16],         # Username (truncated)
                    str(row["score"]),                 # Player score
                    str(row["level_reached"]),         # Player level
                    date_str,                          # Date played
                ]
                for val, x in zip(cells, cols_x):      # Draw each cell in the row
                    draw_text(surface, val, f["small"], rank_col if i < 3 else WHITE, x, y + 2) # Draw value
                y += 26                                # Move to next row position

        self.buttons["back"] = make_button(cx, WINDOW_HEIGHT - 54, 200, 44, "← BACK", f["body"], DARK_GRAY, surface, WHITE)


# ── Settings ──────────────────────────────────────────────────

PRESET_COLORS = [                                      # List of available color presets for the snake
    ((0, 200, 80),   "Green"),
    ((0, 180, 220),  "Cyan"),
    ((220, 80, 220), "Purple"),
    ((220, 140, 0),  "Orange"),
    ((220, 60, 60),  "Red"),
    ((255, 255, 255),"White"),
]


class SettingsScreen(Screen):                          # Class managing game configuration UI
    def __init__(self, app):                           # Initialize settings screen
        super().__init__(app)                          # Parent constructor
        self.tmp = {                                   # Create temporary settings storage for unsaved changes
            "snake_color": list(app.settings["snake_color"]), # Copy current color
            "grid_overlay": app.settings["grid_overlay"], # Copy grid preference
            "sound": app.settings["sound"],            # Copy sound preference
        }
        self.buttons = {}                              # Button dictionary

    def handle_event(self, event):                     # Handle settings interactions
        if event.type == pygame.MOUSEBUTTONDOWN:       # Mouse click detection
            mx, my = event.pos                         # Click position

            if self.buttons.get("grid") and self.buttons["grid"].collidepoint(mx, my): # Grid toggle
                self.tmp["grid_overlay"] = not self.tmp["grid_overlay"] # Flip temporary value
            if self.buttons.get("sound") and self.buttons["sound"].collidepoint(mx, my): # Sound toggle
                self.tmp["sound"] = not self.tmp["sound"] # Flip temporary value

            for (col, _), rect in self.buttons.get("colors", []): # Color selection loop
                if rect.collidepoint(mx, my):           # Check if a color block was clicked
                    self.tmp["snake_color"] = list(col) # Update temporary color choice

            if self.buttons.get("save") and self.buttons["save"].collidepoint(mx, my): # Save button
                self.app.settings.update(self.tmp)     # Apply temporary settings to main app
                save_settings(self.app.settings)       # Save main app settings to JSON file
                self.app.sounds.set_enabled(self.app.settings.get("sound", False)) # Update sound engine
                self.app.show_main_menu()              # Go back to menu

            if self.buttons.get("back") and self.buttons["back"].collidepoint(mx, my): # Cancel/Back button
                self.app.show_main_menu()              # Exit without saving

    def draw(self, surface):                           # Render settings screen UI
        surface.fill(BG_COLOR)                         # Clear screen
        f = self.app.fonts                             # Shortcut for fonts
        cx = WINDOW_WIDTH // 2                         # Center X

        draw_text(surface, "SETTINGS", f["huge"], ACCENT, cx, 40, "center") # Screen title

        y = 130                                        # Start Y for options
        # Grid toggle
        g_col = ACCENT if self.tmp["grid_overlay"] else MID_GRAY # Color based on state
        g_lbl = "Grid Overlay:  ON" if self.tmp["grid_overlay"] else "Grid Overlay:  OFF" # Label based on state
        self.buttons["grid"] = make_button(cx, y, 260, 44, g_lbl, f["body"], g_col, surface, BLACK if self.tmp["grid_overlay"] else WHITE)
        y += 60                                        # Spacing

        # Sound toggle
        s_col = ACCENT if self.tmp["sound"] else MID_GRAY # Color based on state
        s_lbl = "Sound:  ON" if self.tmp["sound"] else "Sound:  OFF" # Label based on state
        self.buttons["sound"] = make_button(cx, y, 260, 44, s_lbl, f["body"], s_col, surface, BLACK if self.tmp["sound"] else WHITE)
        y += 60                                        # Spacing

        # Color presets
        draw_text(surface, "Snake Color:", f["label"], LIGHT_GRAY, cx, y, "center") # Color section label
        y += 30                                        # Spacing for blocks
        self.buttons["colors"] = []                    # Reset color button list
        total_w = len(PRESET_COLORS) * 48 + (len(PRESET_COLORS) - 1) * 10 # Calculate row width
        start_x = cx - total_w // 2                    # Center the row of colors
        for i, (col, name) in enumerate(PRESET_COLORS): # Draw each color choice
            rect = pygame.Rect(start_x + i * 58, y, 44, 44) # Define color block rect
            pygame.draw.rect(surface, col, rect, border_radius=6) # Draw colored rectangle
            if list(col) == self.tmp["snake_color"]:   # Check if this is the currently selected color
                pygame.draw.rect(surface, WHITE, rect, 3, border_radius=6) # Highlight with white border
            self.buttons["colors"].append(((col, name), rect)) # Store for click detection
        y += 70                                        # Spacing

        # Save / Back
        self.buttons["save"] = make_button(cx - 70, y, 120, 44, "SAVE", f["body"], ACCENT, surface, BLACK) # Save button
        self.buttons["back"] = make_button(cx + 70, y, 120, 44, "BACK", f["body"], DARK_GRAY, surface, WHITE) # Back button


# ─────────────────────────────────────────────────────────────
#  App
# ─────────────────────────────────────────────────────────────

class App:                                             # Main application controller class
    def __init__(self):                                # Initialize the application
        pygame.init()                                  # Boot up all imported pygame modules
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT)) # Create the game window
        pygame.display.set_caption(TITLE)              # Set the window title from config
        self.clock = pygame.time.Clock()               # Create a clock object to control framerate
        self.settings = load_settings()                # Load user settings from JSON
        self.username = ""                             # Initialize empty username
        self.player_id: int | None = None              # Initialize player ID as null
        self.personal_best: int = 0                    # Initialize high score as zero
        self.db_available = db.init_db()               # Initialize database and check connectivity

        self.fonts = self._load_fonts()                # Load game fonts into a dictionary
        self.sounds = SoundManager()                   # Initialize the sound management system
        self.sounds.set_enabled(self.settings.get("sound", False)) # Sync sound state with settings
        self.current_screen: Screen = MainMenuScreen(self) # Set the initial screen to Main Menu

    def _load_fonts(self) -> dict:                     # Internal helper to load system fonts
        try:                                           # Try loading specified fonts
            pygame.font.init()                         # Ensure font module is ready
            mono = "monospace"                         # Preferred font family
            return {                                   # Return a dictionary of font objects at different sizes
                "huge":   pygame.font.SysFont(mono, 42, bold=True),
                "big":    pygame.font.SysFont(mono, 30, bold=True),
                "title":  pygame.font.SysFont(mono, 22, bold=True),
                "body":   pygame.font.SysFont(mono, 18),
                "label":  pygame.font.SysFont(mono, 14, bold=True),
                "small":  pygame.font.SysFont(mono, 13),
                "tiny":   pygame.font.SysFont(mono, 11),
            }
        except Exception:                              # Fallback if system fonts are unavailable
            f = pygame.font.Font(None, 24)             # Use default Pygame font
            return {k: f for k in ["huge", "big", "title", "body", "label", "small", "tiny"]}

    # ── Navigation ───────────────────────────────────────────

    def show_main_menu(self):                          # Switch state to main menu screen
        self.current_screen = MainMenuScreen(self)     # Instantiate and set current screen

    def start_game(self):                              # Logic to initiate a game session
        if not self.username.strip():                  # Guard against empty names
            return                                     # Cancel start
        if self.db_available:                          # If DB is working
            self.player_id = db.get_or_create_player(self.username.strip()) # Fetch/Create player ID
            self.personal_best = db.get_personal_best(self.player_id) if self.player_id else 0 # Get high score
        else:                                          # If DB failed
            self.player_id = -1                        # Use dummy ID
            self.personal_best = 0                     # Default high score
        self.current_screen = PlayingScreen(self, self.player_id, self.personal_best) # Start game screen

    def show_game_over(self, score: int, level: int, personal_best: int): # Transition to game over screen
        self.personal_best = personal_best             # Update the app's record of high score
        self.current_screen = GameOverScreen(self, score, level, personal_best) # Show summary

    def show_leaderboard(self):                        # Transition to leaderboard screen
        self.current_screen = LeaderboardScreen(self)  # Instantiate leaderboard screen

    def show_settings(self):                           # Transition to settings screen
        self.current_screen = SettingsScreen(self)     # Instantiate settings screen

    def quit(self):                                    # Cleanly exit the application
        db.close()                                     # Close database connections
        pygame.quit()                                  # Shutdown pygame
        sys.exit()                                     # Exit Python script

    # ── Main loop ────────────────────────────────────────────

    def run(self):                                     # The core execution loop of the app
        while True:                                    # Loop forever until quit
            for event in pygame.event.get():           # Poll for user events
                if event.type == pygame.QUIT:          # If the user closed the window
                    self.quit()                        # Call the quit function
                self.current_screen.handle_event(event)# Pass the event to the current active screen

            self.current_screen.update()               # Update logic of the current screen
            self.current_screen.draw(self.screen)      # Render visuals of the current screen
            pygame.display.flip()                      # Update the full display surface to the screen
            self.clock.tick(FPS)                       # Wait enough time to maintain target FPS


if __name__ == "__main__":                             # Check if script is executed directly
    App().run()                                        # Create App instance and start the game loop