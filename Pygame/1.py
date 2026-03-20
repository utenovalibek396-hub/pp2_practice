import pygame
import random

pygame.init()

WIDTH, HEIGHT = 800, 600
CELL = 20

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Snake")

clock = pygame.time.Clock()
font = pygame.font.SysFont("arial", 25)
big_font = pygame.font.SysFont("arial", 50)

def draw_text(text, font, color, x, y):
    img = font.render(text, True, color)
    screen.blit(img, (x, y))

def random_food(snake):
    while True:
        x = random.randrange(0, WIDTH, CELL)
        y = random.randrange(0, HEIGHT, CELL)
        if (x, y) not in snake:
            return (x, y)

def game():
    snake = [(WIDTH // 2, HEIGHT // 2)]
    direction = (CELL, 0)
    food = random_food(snake)
    score = 0
    paused = False
    game_over = False

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p:
                    paused = not paused
                if event.key == pygame.K_r and game_over:
                    return game()
                if not paused and not game_over:
                    if event.key == pygame.K_LEFT and direction != (CELL, 0):
                        direction = (-CELL, 0)
                    elif event.key == pygame.K_RIGHT and direction != (-CELL, 0):
                        direction = (CELL, 0)
                    elif event.key == pygame.K_UP and direction != (0, CELL):
                        direction = (0, -CELL)
                    elif event.key == pygame.K_DOWN and direction != (0, -CELL):
                        direction = (0, CELL)

        if not paused and not game_over:
            head = (snake[0][0] + direction[0], snake[0][1] + direction[1])

            if (
                head[0] < 0 or head[0] >= WIDTH or
                head[1] < 0 or head[1] >= HEIGHT or
                head in snake
            ):
                game_over = True
            else:
                snake.insert(0, head)

                if head == food:
                    score += 1
                    food = random_food(snake)
                else:
                    snake.pop()

        screen.fill((20, 20, 20))

        for i, s in enumerate(snake):
            color = (0, 255 - i*5, 0)
            pygame.draw.rect(screen, color, (s[0], s[1], CELL, CELL), border_radius=5)

        pygame.draw.rect(screen, (255, 50, 50), (food[0], food[1], CELL, CELL), border_radius=5)

        draw_text(f"Score: {score}", font, (255, 255, 255), 10, 10)

        if paused:
            draw_text("PAUSED", big_font, (255, 255, 0), WIDTH//2 - 100, HEIGHT//2 - 30)

        if game_over:
            draw_text("GAME OVER", big_font, (255, 0, 0), WIDTH//2 - 150, HEIGHT//2 - 50)
            draw_text("Press R to Restart", font, (255, 255, 255), WIDTH//2 - 120, HEIGHT//2 + 20)

        pygame.display.flip()
        clock.tick(12 + score // 3)

game()
pygame.quit()