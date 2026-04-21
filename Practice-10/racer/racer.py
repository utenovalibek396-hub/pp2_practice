import pygame
import random
import sys
import time
import os

pygame.init()

# ---------------------------------
# Game settings
# ---------------------------------
SCREEN_WIDTH = 400
SCREEN_HEIGHT = 600
FPS = 60

SPEED = 5
PLAYER_SPEED = 5

SCORE = 0
COINS_COLLECTED = 0

# Road lanes
LANES = [110, 200, 290]

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 180, 0)
GRAY = (70, 70, 70)
RED = (220, 0, 0)
ROAD_LINE = (240, 240, 240)

# ---------------------------------
# Image paths
# ---------------------------------
BASE_DIR = os.path.dirname(__file__)
RED_CAR_PATH = os.path.join(BASE_DIR, "assets", "red_car.png")
COIN_PATH = os.path.join(BASE_DIR, "assets", "coin.png")

# Create display
DISPLAYSURF = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Racer")

# Fonts
font_big = pygame.font.SysFont("Verdana", 50)
font_small = pygame.font.SysFont("Verdana", 20)
game_over_text = font_big.render("Game Over", True, BLACK)

# FPS controller
FramePerSec = pygame.time.Clock()

# Custom event for increasing speed
INC_SPEED = pygame.USEREVENT + 1
pygame.time.set_timer(INC_SPEED, 1000)


# ---------------------------------
# Function to change red car to blue
# ---------------------------------
def make_blue_car(image):
    blue_car = image.copy()

    for x in range(blue_car.get_width()):
        for y in range(blue_car.get_height()):
            color = blue_car.get_at((x, y))

            r = color.r
            g = color.g
            b = color.b
            a = color.a

            # Change only visible red pixels
            if a > 0 and r > g and r > b:
                brightness = max(r, g, b)
                blue_car.set_at((x, y), (0, 120, brightness, a))

    return blue_car


# ---------------------------------
# Function to draw road background
# ---------------------------------
def draw_road(surface, line_offset):
    # Fill whole screen with green grass
    surface.fill(GREEN)

    # Draw gray road in the middle
    pygame.draw.rect(surface, GRAY, (50, 0, 300, SCREEN_HEIGHT))

    # Draw road borders
    pygame.draw.line(surface, WHITE, (50, 0), (50, SCREEN_HEIGHT), 4)
    pygame.draw.line(surface, WHITE, (350, 0), (350, SCREEN_HEIGHT), 4)

    # Draw moving dashed line in the center
    for y in range(-40, SCREEN_HEIGHT, 80):
        pygame.draw.rect(surface, ROAD_LINE, (192, y + line_offset, 16, 40))


# ---------------------------------
# Enemy class
# ---------------------------------
class Enemy(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()

        # Load red car PNG for enemy
        self.image = pygame.image.load(RED_CAR_PATH).convert_alpha()
        self.image = pygame.transform.scale(self.image, (40, 70))

        self.rect = self.image.get_rect()
        self.reset_position()

    def reset_position(self):
        # Enemy appears in one of the road lanes
        self.rect.centerx = random.choice(LANES)

        # Enemy starts above the screen
        self.rect.y = random.randint(-600, -100)

    def move(self):
        global SCORE

        self.rect.move_ip(0, SPEED)

        if self.rect.top > SCREEN_HEIGHT:
            SCORE += 1
            self.reset_position()


# ---------------------------------
# Player class
# ---------------------------------
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()

        # Load same red car PNG
        red_car = pygame.image.load(RED_CAR_PATH).convert_alpha()
        red_car = pygame.transform.scale(red_car, (40, 70))

        # Convert red car image to blue car image
        self.image = make_blue_car(red_car)

        self.rect = self.image.get_rect()
        self.rect.center = (200, 520)

    def move(self):
        pressed_keys = pygame.key.get_pressed()

        if pressed_keys[pygame.K_LEFT] and self.rect.left > 55:
            self.rect.move_ip(-PLAYER_SPEED, 0)

        if pressed_keys[pygame.K_RIGHT] and self.rect.right < 345:
            self.rect.move_ip(PLAYER_SPEED, 0)


# ---------------------------------
# Coin class
# ---------------------------------
class Coin(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()

        # Load coin PNG
        self.image = pygame.image.load(COIN_PATH).convert_alpha()
        self.image = pygame.transform.scale(self.image, (24, 24))

        self.rect = self.image.get_rect()
        self.reset_position()

    def reset_position(self):
        self.rect.center = (
            random.choice(LANES),
            random.randint(-500, -50)
        )

    def move(self):
        self.rect.move_ip(0, SPEED)

        if self.rect.top > SCREEN_HEIGHT:
            self.reset_position()


# Create objects
P1 = Player()
E1 = Enemy()
E2 = Enemy()

# Start enemies in different places so they do not overlap at the beginning
E1.rect.centerx = 110
E1.rect.y = -100

E2.rect.centerx = 290
E2.rect.y = -400

C1 = Coin()

# Create groups
enemies = pygame.sprite.Group()
enemies.add(E1)
enemies.add(E2)

coins = pygame.sprite.Group()
coins.add(C1)

all_sprites = pygame.sprite.Group()
all_sprites.add(P1)
all_sprites.add(E1)
all_sprites.add(E2)
all_sprites.add(C1)

# Offset for moving road lines
line_offset = 0


# ---------------------------------
# Main game loop
# ---------------------------------
while True:
    for event in pygame.event.get():
        if event.type == INC_SPEED:
            SPEED += 1

        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    # Draw road background
    draw_road(DISPLAYSURF, line_offset)

    # Animate road center lines
    line_offset += SPEED
    if line_offset >= 80:
        line_offset = 0

    # Show score text
    score_text = font_small.render("Score: " + str(SCORE), True, BLACK)
    coin_text = font_small.render("Coins: " + str(COINS_COLLECTED), True, BLACK)

    DISPLAYSURF.blit(score_text, (10, 10))
    DISPLAYSURF.blit(coin_text, (SCREEN_WIDTH - coin_text.get_width() - 10, 10))

    # Draw and move all sprites
    for entity in all_sprites:
        DISPLAYSURF.blit(entity.image, entity.rect)
        entity.move()

    # Check if player collects coin
    collected = pygame.sprite.spritecollide(P1, coins, False)

    if collected:
        COINS_COLLECTED += 1
        C1.reset_position()

    # Check collision with enemy
    if pygame.sprite.spritecollideany(P1, enemies):
        time.sleep(0.3)

        DISPLAYSURF.fill(RED)
        DISPLAYSURF.blit(game_over_text, (60, 250))
        pygame.display.update()

        time.sleep(2)
        pygame.quit()
        sys.exit()

    pygame.display.update()
    FramePerSec.tick(FPS)