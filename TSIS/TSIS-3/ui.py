import pygame  # Import the Pygame library for UI and graphics
from persistence import load_leaderboard, load_settings, save_settings  # Import data handling functions

C_BG       = (14, 14, 22)  # Define background color (dark blue/black)
C_ROAD     = (30, 30, 40)  # Define road/stripe color for the background animation
C_ACCENT   = (255, 200, 0)  # Define accent color (gold/yellow) for buttons and highlights
C_WHITE    = (240, 240, 255)  # Define off-white color for text
C_GRAY     = (100, 100, 120)  # Define gray color for secondary information
C_RED      = (220, 60, 60)  # Define red for "Off" states or "Game Over"
C_GREEN    = (60, 200, 100)  # Define green for "On" states or success
C_BLUE     = (60, 130, 230)  # Define a blue color for buttons or cars
C_DARK     = (22, 22, 35)  # Define a very dark shade for text on light backgrounds
C_PANEL    = (28, 28, 42)  # Define a panel color for button backgrounds

CAR_COLOR_OPTIONS = [  # List of available car colors with their display names and RGB values
    ("Red",    (220, 60,  60)),
    ("Blue",   (60,  130, 230)),
    ("Green",  (60,  200, 100)),
    ("Yellow", (230, 200, 40)),
    ("Purple", (160, 80,  220)),
]

def draw_rect_alpha(surface, color, rect, alpha, radius=0):  # Helper to draw semi-transparent rectangles
    shape_surf = pygame.Surface(pygame.Rect(rect).size, pygame.SRCALPHA)  # Create a surface that supports transparency
    pygame.draw.rect(shape_surf, (*color, alpha), shape_surf.get_rect(), border_radius=radius)  # Draw the rectangle
    surface.blit(shape_surf, rect)  # Blit the transparent shape onto the main surface

def draw_title(screen, font, text, x, y, color=C_ACCENT):  # Helper to draw centered text titles
    img = font.render(text, True, color)  # Render the text into an image
    rect = img.get_rect(center=(x, y))  # Get the rectangle and center it on coordinates
    screen.blit(img, rect)  # Draw the text to the screen

def draw_stripe_bg(screen, w, h, offset):  # Draw the moving stripe background for the menu
    screen.fill(C_BG)  # Fill with solid background color first
    for y in range(-100, h + 100, 100):  # Loop to draw stripes across the height
        draw_rect_alpha(screen, C_ROAD, (0, y + offset % 100, w, 50), 100)  # Draw each moving stripe

class MainMenu:  # Class for the main navigation menu
    def __init__(self, w, h):  # Initialize menu dimensions and fonts
        self.W, self.H = w, h
        self.font_t = pygame.font.SysFont("Impact", 100)  # Large font for the game title
        self.font_b = pygame.font.SysFont("Arial", 32, True)  # Bold font for buttons
        self.offset = 0  # Track background animation offset

    def run(self, screen, clock):  # Main menu loop
        btns = [("PLAY", "play"), ("LEADERBOARD", "leaderboard"), ("SETTINGS", "settings"), ("QUIT", "quit")]
        while True:
            self.offset += 1  # Increment background animation
            mp = pygame.mouse.get_pos()  # Get current mouse cursor position
            for event in pygame.event.get():  # Process user events
                if event.type == pygame.QUIT: return "quit"  # Exit if window is closed
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:  # Check for left click
                    for i, (text, action) in enumerate(btns):  # Loop through buttons to check for clicks
                        rect = pygame.Rect(self.W//2 - 150, 300 + i*80, 300, 60)
                        if rect.collidepoint(mp): return action  # Return the action associated with the button

            draw_stripe_bg(screen, self.W, self.H, self.offset)  # Render animated background
            draw_title(screen, self.font_t, "RACER", self.W//2, 180, C_WHITE)  # Draw game logo

            for i, (text, action) in enumerate(btns):  # Draw each menu button
                rect = pygame.Rect(self.W//2 - 150, 300 + i*80, 300, 60)
                color = C_ACCENT if rect.collidepoint(mp) else C_PANEL  # Highlight button on hover
                pygame.draw.rect(screen, color, rect, border_radius=12)  # Draw button shape
                txt = self.font_b.render(text, True, C_WHITE if color==C_PANEL else C_DARK)  # Set text color
                screen.blit(txt, txt.get_rect(center=rect.center))  # Draw button label
            
            pygame.display.flip()  # Update the display
            clock.tick(60)  # Maintain 60 FPS

class UsernameScreen:  # Screen to capture player name before the game
    def __init__(self, w, h):  # Setup dimensions and state
        self.W, self.H = w, h
        self.font = pygame.font.SysFont("Arial", 40, True)
        self.name = ""  # Initialize empty string for the name

    def run(self, screen, clock):  # Input loop for the name
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT: return None
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN and self.name: return self.name  # Confirm name with Enter
                    if event.key == pygame.K_BACKSPACE: self.name = self.name[:-1]  # Delete last character
                    elif len(self.name) < 12 and event.unicode.isalnum(): self.name += event.unicode  # Add alphanumeric chars
            
            screen.fill(C_BG)
            draw_title(screen, self.font, "ENTER YOUR NAME", self.W//2, 250, C_WHITE)
            box = pygame.Rect(self.W//2 - 200, 320, 400, 70)  # Define input box
            pygame.draw.rect(screen, C_PANEL, box, border_radius=10)  # Draw input box background
            pygame.draw.rect(screen, C_ACCENT, box, 3, border_radius=10)  # Draw input box border
            txt = self.font.render(self.name, True, C_ACCENT)  # Render current name string
            screen.blit(txt, txt.get_rect(center=box.center))  # Centered text in box
            pygame.display.flip()
            clock.tick(60)

class LeaderboardScreen:  # Screen to display high scores
    def __init__(self, w, h):
        self.W, self.H = w, h
        self.font = pygame.font.SysFont("Arial", 24)

    def run(self, screen, clock):  # Display loop
        data = load_leaderboard()  # Fetch scores from storage
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE): return
                if event.type == pygame.MOUSEBUTTONDOWN: return  # Exit on any click

            screen.fill(C_BG)
            draw_title(screen, self.font, "TOP 10 RUNS", self.W//2, 80, C_ACCENT)
            for i, row in enumerate(data[:10]):  # Loop through top 10 scores
                y = 150 + i * 45
                txt = f"{i+1}. {row['name']} - {row['score']} pts"
                img = self.font.render(txt, True, C_WHITE)
                screen.blit(img, (self.W//2 - 150, y))  # List scores vertically
            pygame.display.flip()
            clock.tick(60)

class SettingsScreen:  # Screen for user preferences
    def __init__(self, w, h):
        self.W, self.H = w, h
        self.font = pygame.font.SysFont("Arial", 28, True)

    def run(self, screen, clock):  # Settings interaction loop
        settings = load_settings()  # Load current preferences
        DIFFICULTY_OPTIONS = ["easy", "normal", "hard"]
        selected_diff = DIFFICULTY_OPTIONS.index(settings.get("difficulty", "normal"))

        while True:
            mp = pygame.mouse.get_pos()
            for event in pygame.event.get():
                if event.type == pygame.QUIT: return settings
                if event.type == pygame.MOUSEBUTTONDOWN:
                    # SAVE BUTTON detection
                    if pygame.Rect(self.W//2-100, self.H-100, 200, 50).collidepoint(mp):
                        settings["difficulty"] = DIFFICULTY_OPTIONS[selected_diff]
                        save_settings(settings)  # Write changes to file
                        return settings

                    # SOUND TOGGLE detection
                    if pygame.Rect(self.W//2-50, 180, 100, 40).collidepoint(mp):
                        settings["sound"] = not settings["sound"]

                    # CAR COLOR selection detection
                    for i, (name, rgb) in enumerate(CAR_COLOR_OPTIONS):
                        if pygame.Rect(self.W//2-150 + i*65, 300, 50, 50).collidepoint(mp):
                            settings["car_color"] = list(rgb)

                    # DIFFICULTY BUTTON detection
                    for i, diff in enumerate(DIFFICULTY_OPTIONS):
                        rect = pygame.Rect(self.W//2 - 150 + i*120, 420, 100, 40)
                        if rect.collidepoint(mp):
                            selected_diff = i
                            settings["difficulty"] = DIFFICULTY_OPTIONS[i]

            screen.fill(C_BG)
            draw_title(screen, self.font, "SETTINGS", self.W//2, 80, C_WHITE)

            # Draw Sound setting
            snd_txt = f"Sound: {'ON' if settings['sound'] else 'OFF'}"
            draw_title(screen, self.font, snd_txt, self.W//2, 200, C_GREEN if settings['sound'] else C_RED)

            # Draw Car Color options
            draw_title(screen, self.font, "Car Color:", self.W//2, 270, C_GRAY)
            for i, (name, rgb) in enumerate(CAR_COLOR_OPTIONS):
                rect = pygame.Rect(self.W//2-150 + i*65, 300, 50, 50)
                pygame.draw.rect(screen, rgb, rect, border_radius=5)
                if list(rgb) == settings["car_color"]:  # Highlight selected color
                    pygame.draw.rect(screen, C_WHITE, rect, 3, border_radius=5)

            # Draw Difficulty options
            draw_title(screen, self.font, "Difficulty:", self.W//2, 380, C_GRAY)
            for i, diff in enumerate(DIFFICULTY_OPTIONS):
                rect = pygame.Rect(self.W//2 - 150 + i*120, 420, 100, 40)
                color = C_ACCENT if i == selected_diff else C_PANEL
                pygame.draw.rect(screen, color, rect, border_radius=10)
                txt_color = C_DARK if i == selected_diff else C_WHITE
                txt = self.font.render(diff.upper(), True, txt_color)
                screen.blit(txt, txt.get_rect(center=rect.center))

            # Draw the Save/Back button
            back_btn = pygame.Rect(self.W//2-100, self.H-100, 200, 50)
            pygame.draw.rect(screen, C_PANEL, back_btn, border_radius=10)
            draw_title(screen, self.font, "SAVE & BACK", self.W//2, self.H-75, C_ACCENT)

            pygame.display.flip()
            clock.tick(60)
            
class GameOverScreen:  # Summary screen shown after a crash
    def __init__(self, w, h):
        self.W, self.H = w, h
        self.font = pygame.font.SysFont("Arial", 30, True)

    def run(self, screen, clock, score, dist, coins):  # Display results loop
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT: return "menu"
                if event.type == pygame.MOUSEBUTTONDOWN:
                    mp = pygame.mouse.get_pos()
                    if pygame.Rect(self.W//2-110, 500, 220, 50).collidepoint(mp): return "retry"  # Restart game
                    if pygame.Rect(self.W//2-110, 570, 220, 50).collidepoint(mp): return "menu"  # Back to menu

            screen.fill(C_BG)
            draw_title(screen, self.font, "GAME OVER", self.W//2, 150, C_RED)
            draw_title(screen, self.font, f"Final Score: {score}", self.W//2, 250, C_WHITE)
            draw_title(screen, self.font, f"Distance: {dist}m", self.W//2, 300, C_GRAY)
            draw_title(screen, self.font, f"Coins: {coins}", self.W//2, 350, C_ACCENT)
            
            # Draw Retry/Menu action buttons
            pygame.draw.rect(screen, C_PANEL, (self.W//2-110, 500, 220, 50), border_radius=10)
            draw_title(screen, self.font, "RETRY", self.W//2, 525, C_WHITE)
            pygame.draw.rect(screen, C_PANEL, (self.W//2-110, 570, 220, 50), border_radius=10)
            draw_title(screen, self.font, "MAIN MENU", self.W//2, 595, C_WHITE)
            
            pygame.display.flip()
            clock.tick(60)