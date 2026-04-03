import pygame
import random
import sys

pygame.init()
WIDTH, HEIGHT = 500, 700
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Dodge Game")
clock = pygame.time.Clock()

WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
BLACK = (0, 0, 0)

pygame.mixer.init()
hit_sound = pygame.mixer.Sound("GAME/Metal Hit.wav")
bonus_sound = pygame.mixer.Sound("GAME/Bonus 1.wav")
game_over_sound = pygame.mixer.Sound("GAME/deadsound.wav")  

pygame.mixer.music.load("GAME/Кайрат Нуртас - Ауырмайды Жүрек.wav")  
pygame.mixer.music.set_volume(0.5)

player_size = 50
player_speed = 7
block_size = 50
block_speed = 5
bonus_size = 30
font = pygame.font.SysFont(None, 36)

def draw_text(text, x, y, color=WHITE, size=None, center=False):
    f = font if size is None else pygame.font.SysFont(None, size)
    img = f.render(text, True, color)
    if center:
        rect = img.get_rect(center=(x, y))
        screen.blit(img, rect)
    else:
        screen.blit(img, (x, y))

def create_block(blocks):
    x = random.randint(0, WIDTH - block_size)
    blocks.append([x, 0, block_size, block_size])

def create_bonus(bonuses):
    x = random.randint(0, WIDTH - bonus_size)
    bonuses.append([x, 0, bonus_size, bonus_size])

def check_collision(rect1, rect2):
    return (rect1[0] < rect2[0] + rect2[2] and
            rect1[0] + rect1[2] > rect2[0] and
            rect1[1] < rect2[1] + rect2[3] and
            rect1[1] + rect1[3] > rect2[1])

def start_screen():
    screen.fill(BLACK)
    draw_text("DODGE GAME", WIDTH // 2, HEIGHT // 2 - 60, WHITE, 50, center=True)
    draw_text("Press SPACE to Start", WIDTH // 2, HEIGHT // 2, WHITE, 36, center=True)
    pygame.display.update()
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:   
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    waiting = False

def game_over_screen(score):
    game_over_sound.play()
    screen.fill(BLACK)
    draw_text("GAME OVER", WIDTH // 2, HEIGHT // 2 - 60, RED, 50, center=True)
    draw_text(f"Score: {score}", WIDTH // 2, HEIGHT // 2, WHITE, 36, center=True)
    draw_text("Press R to Restart or Q to Quit", WIDTH // 2, HEIGHT // 2 + 60, WHITE, 28, center=True)
    pygame.display.update()
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    waiting = False
                if event.key == pygame.K_q:
                    pygame.quit()
                    sys.exit()

while True:
    start_screen()
    pygame.mixer.music.play(-1)  # Музыка үздіксіз ойнатылсын

    player_x = WIDTH // 2
    player_y = HEIGHT - 70
    lives = 3
    score = 0
    blocks = []
    bonuses = []
    block_speed = 5

    running = True
    while running:
        screen.fill(BLACK)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and player_x > 0:
            player_x -= player_speed
        if keys[pygame.K_RIGHT] and player_x < WIDTH - player_size:
            player_x += player_speed

        if random.randint(1, 20) == 1:
            create_block(blocks)
        if random.randint(1, 200) == 1:
            create_bonus(bonuses)

        for block in blocks:
            block[1] += block_speed
            pygame.draw.rect(screen, RED, block)

        for bonus in bonuses:
            bonus[1] += block_speed // 2
            pygame.draw.rect(screen, GREEN, bonus)

        player_rect = [player_x, player_y, player_size, player_size]
        for block in blocks[:]:
            if check_collision(player_rect, block):
                hit_sound.play()
                blocks.remove(block)
                lives -= 1
                if lives <= 0:
                    running = False
            elif block[1] > HEIGHT:
                blocks.remove(block)

        for bonus in bonuses[:]:
            if check_collision(player_rect, bonus):
                bonus_sound.play()
                bonuses.remove(bonus)
                score += 50
            elif bonus[1] > HEIGHT:
                bonuses.remove(bonus)

        pygame.draw.rect(screen, BLUE, player_rect)
        draw_text(f"Score: {score}", WIDTH // 2, 30, WHITE, 36, center=True)
        draw_text(f"Lives: {lives}", WIDTH // 2, 70, WHITE, 36, center=True)
        block_speed += 0.001

        pygame.display.update()
        clock.tick(60)

    pygame.mixer.music.stop()
    game_over_screen(score)