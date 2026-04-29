import pygame
from persistence import load_leaderboard, load_settings, save_settings

C_BG       = (14, 14, 22)
C_ROAD     = (30, 30, 40)
C_ACCENT   = (255, 200, 0)
C_WHITE    = (240, 240, 255)
C_GRAY     = (100, 100, 120)
C_RED      = (220, 60, 60)
C_GREEN    = (60, 200, 100)
C_BLUE     = (60, 130, 230)
C_DARK     = (22, 22, 35)
C_PANEL    = (28, 28, 42)

CAR_COLOR_OPTIONS = [
    ("Red",    (220, 60,  60)),
    ("Blue",   (60,  130, 230)),
    ("Green",  (60,  200, 100)),
    ("Yellow", (230, 200, 40)),
    ("Purple", (160, 80,  220)),
]

def draw_rect_alpha(surface, color, rect, alpha, radius=0):
    shape_surf = pygame.Surface(pygame.Rect(rect).size, pygame.SRCALPHA)
    pygame.draw.rect(shape_surf, (*color, alpha), shape_surf.get_rect(), border_radius=radius)
    surface.blit(shape_surf, rect)

def draw_title(screen, font, text, x, y, color=C_ACCENT):
    img = font.render(text, True, color)
    rect = img.get_rect(center=(x, y))
    screen.blit(img, rect)

def draw_stripe_bg(screen, w, h, offset):
    screen.fill(C_BG)
    for y in range(-100, h + 100, 100):
        draw_rect_alpha(screen, C_ROAD, (0, y + offset % 100, w, 50), 100)

class MainMenu:
    def __init__(self, w, h):
        self.W, self.H = w, h
        self.font_t = pygame.font.SysFont("Impact", 100)
        self.font_b = pygame.font.SysFont("Arial", 32, True)
        self.offset = 0

    def run(self, screen, clock):
        btns = [("PLAY", "play"), ("LEADERBOARD", "leaderboard"), ("SETTINGS", "settings"), ("QUIT", "quit")]
        while True:
            self.offset += 1
            mp = pygame.mouse.get_pos()
            for event in pygame.event.get():
                if event.type == pygame.QUIT: return "quit"
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    for i, (text, action) in enumerate(btns):
                        rect = pygame.Rect(self.W//2 - 150, 300 + i*80, 300, 60)
                        if rect.collidepoint(mp): return action

            draw_stripe_bg(screen, self.W, self.H, self.offset)
            draw_title(screen, self.font_t, "RACER", self.W//2, 180, C_WHITE)

            for i, (text, action) in enumerate(btns):
                rect = pygame.Rect(self.W//2 - 150, 300 + i*80, 300, 60)
                color = C_ACCENT if rect.collidepoint(mp) else C_PANEL
                pygame.draw.rect(screen, color, rect, border_radius=12)
                txt = self.font_b.render(text, True, C_WHITE if color==C_PANEL else C_DARK)
                screen.blit(txt, txt.get_rect(center=rect.center))
            
            pygame.display.flip()
            clock.tick(60)

class UsernameScreen:
    def __init__(self, w, h):
        self.W, self.H = w, h
        self.font = pygame.font.SysFont("Arial", 40, True)
        self.name = ""

    def run(self, screen, clock):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT: return None
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN and self.name: return self.name
                    if event.key == pygame.K_BACKSPACE: self.name = self.name[:-1]
                    elif len(self.name) < 12 and event.unicode.isalnum(): self.name += event.unicode
            
            screen.fill(C_BG)
            draw_title(screen, self.font, "ENTER YOUR NAME", self.W//2, 250, C_WHITE)
            box = pygame.Rect(self.W//2 - 200, 320, 400, 70)
            pygame.draw.rect(screen, C_PANEL, box, border_radius=10)
            pygame.draw.rect(screen, C_ACCENT, box, 3, border_radius=10)
            txt = self.font.render(self.name, True, C_ACCENT)
            screen.blit(txt, txt.get_rect(center=box.center))
            pygame.display.flip()
            clock.tick(60)

class LeaderboardScreen:
    def __init__(self, w, h):
        self.W, self.H = w, h
        self.font = pygame.font.SysFont("Arial", 24)

    def run(self, screen, clock):
        data = load_leaderboard()
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE): return
                if event.type == pygame.MOUSEBUTTONDOWN: return

            screen.fill(C_BG)
            draw_title(screen, self.font, "TOP 10 RUNS", self.W//2, 80, C_ACCENT)
            for i, row in enumerate(data[:10]):
                y = 150 + i * 45
                txt = f"{i+1}. {row['name']} - {row['score']} pts"
                img = self.font.render(txt, True, C_WHITE)
                screen.blit(img, (self.W//2 - 150, y))
            pygame.display.flip()
            clock.tick(60)

class SettingsScreen:
    def __init__(self, w, h):
        self.W, self.H = w, h
        self.font = pygame.font.SysFont("Arial", 28, True)

    def run(self, screen, clock):
        settings = load_settings()
        while True:
            mp = pygame.mouse.get_pos()
            for event in pygame.event.get():
                if event.type == pygame.QUIT: return settings
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if pygame.Rect(self.W//2-100, self.H-100, 200, 50).collidepoint(mp):
                        save_settings(settings)
                        return settings
                    if pygame.Rect(self.W//2-50, 180, 100, 40).collidepoint(mp):
                        settings["sound"] = not settings["sound"]
                    for i, (name, rgb) in enumerate(CAR_COLOR_OPTIONS):
                        if pygame.Rect(self.W//2-150 + i*65, 300, 50, 50).collidepoint(mp):
                            settings["car_color"] = list(rgb)
            
            screen.fill(C_BG)
            draw_title(screen, self.font, "SETTINGS", self.W//2, 80, C_WHITE)
            
            snd_txt = f"Sound: {'ON' if settings['sound'] else 'OFF'}"
            draw_title(screen, self.font, snd_txt, self.W//2, 200, C_GREEN if settings['sound'] else C_RED)
            
            draw_title(screen, self.font, "Car Color:", self.W//2, 270, C_GRAY)
            for i, (name, rgb) in enumerate(CAR_COLOR_OPTIONS):
                rect = pygame.Rect(self.W//2-150 + i*65, 300, 50, 50)
                pygame.draw.rect(screen, rgb, rect, border_radius=5)
                if list(rgb) == settings["car_color"]:
                    pygame.draw.rect(screen, C_WHITE, rect, 3, border_radius=5)

            back_btn = pygame.Rect(self.W//2-100, self.H-100, 200, 50)
            pygame.draw.rect(screen, C_PANEL, back_btn, border_radius=10)
            draw_title(screen, self.font, "SAVE & BACK", self.W//2, self.H-75, C_ACCENT)
            
            pygame.display.flip()
            clock.tick(60)

class GameOverScreen:
    def __init__(self, w, h):
        self.W, self.H = w, h
        self.font = pygame.font.SysFont("Arial", 30, True)

    def run(self, screen, clock, score, dist, coins):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT: return "menu"
                if event.type == pygame.MOUSEBUTTONDOWN:
                    mp = pygame.mouse.get_pos()
                    if pygame.Rect(self.W//2-110, 500, 220, 50).collidepoint(mp): return "retry"
                    if pygame.Rect(self.W//2-110, 570, 220, 50).collidepoint(mp): return "menu"

            screen.fill(C_BG)
            draw_title(screen, self.font, "GAME OVER", self.W//2, 150, C_RED)
            draw_title(screen, self.font, f"Final Score: {score}", self.W//2, 250, C_WHITE)
            draw_title(screen, self.font, f"Distance: {dist}m", self.W//2, 300, C_GRAY)
            draw_title(screen, self.font, f"Coins: {coins}", self.W//2, 350, C_ACCENT)
            
            pygame.draw.rect(screen, C_PANEL, (self.W//2-110, 500, 220, 50), border_radius=10)
            draw_title(screen, self.font, "RETRY", self.W//2, 525, C_WHITE)
            pygame.draw.rect(screen, C_PANEL, (self.W//2-110, 570, 220, 50), border_radius=10)
            draw_title(screen, self.font, "MAIN MENU", self.W//2, 595, C_WHITE)
            
            pygame.display.flip()
            clock.tick(60)