import pygame, sys, random
from pygame.locals import *

pygame.init()
pygame.mixer.init()

# --- CONFIG ---
CELL_SIZE = 20
GRID_WIDTH = 30
GRID_HEIGHT = 20

WIDTH = CELL_SIZE * GRID_WIDTH
HEIGHT = CELL_SIZE * GRID_HEIGHT

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)

# --- LOAD IMAGE ---
def load(name):
    return pygame.transform.scale(
        pygame.image.load(name),
        (CELL_SIZE, CELL_SIZE)
    )

# HEAD
head_up = load("head_up.png")
head_down = load("head_down.png")
head_left = load("head_left.png")
head_right = load("head_right.png")

# TAIL
tail_up = load("tail_up.png")
tail_down = load("tail_down.png")
tail_left = load("tail_left.png")
tail_right = load("tail_right.png")

# BODY
body_vertical = load("body_vertical.png")
body_horizontal = load("body_horizontal.png")
body_topleft = load("body_topleft.png")
body_topright = load("body_topright.png")
body_bottomleft = load("body_bottomleft.png")
body_bottomright = load("body_bottomright.png")

# FOOD + BACKGROUND
food_img = load("apple.png")
bg_img = pygame.transform.scale(
    pygame.image.load("background.jpg"),
    (WIDTH, HEIGHT)
)
eat_sound = pygame.mixer.Sound("eat.wav")
gameover_sound = pygame.mixer.Sound("gameover.wav")
move_sound = pygame.mixer.Sound("move.wav")
# --- SCREEN ---
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Snake Game")
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 36)

# --- SNAKE CLASS ---
class Snake:
    def __init__(self):
        self.body = [(10,10),(9,10),(8,10)]
        self.direction = (1,0)
        self.grow = False

    def update(self):
        head_x, head_y = self.body[0]
        dx, dy = self.direction

        new_head = (head_x + dx, head_y + dy)
        self.body.insert(0, new_head)

        if not self.grow:
            self.body.pop()
        else:
            self.grow = False

    def draw(self, surface):
        for i, segment in enumerate(self.body):
            x, y = segment[0]*CELL_SIZE, segment[1]*CELL_SIZE

            # HEAD
            if i == 0:
                if self.direction == (1,0):
                    surface.blit(head_right, (x,y))
                elif self.direction == (-1,0):
                    surface.blit(head_left, (x,y))
                elif self.direction == (0,-1):
                    surface.blit(head_up, (x,y))
                elif self.direction == (0,1):
                    surface.blit(head_down, (x,y))

            # TAIL
            elif i == len(self.body)-1:
                prev = self.body[i-1]
                dx = segment[0] - prev[0]
                dy = segment[1] - prev[1]

                if dx == 1:
                    surface.blit(tail_right, (x,y))
                elif dx == -1:
                    surface.blit(tail_left, (x,y))
                elif dy == 1:
                    surface.blit(tail_down, (x,y))
                elif dy == -1:
                    surface.blit(tail_up, (x,y))

            # BODY
            else:
                prev = self.body[i-1]
                next = self.body[i+1]

                dx1 = segment[0] - prev[0]
                dy1 = segment[1] - prev[1]
                dx2 = segment[0] - next[0]
                dy2 = segment[1] - next[1]

                if dx1 == dx2:
                    surface.blit(body_horizontal, (x,y))
                elif dy1 == dy2:
                    surface.blit(body_vertical, (x,y))
                else:
                    surface.blit(body_horizontal, (x,y))

# --- FOOD CLASS ---
class Food:
    def __init__(self, snake_body):
        self.randomize(snake_body)

    def randomize(self, snake_body):
        while True:
            pos = (
                random.randint(1, GRID_WIDTH-2),
                random.randint(1, GRID_HEIGHT-2)
            )
            if pos not in snake_body:
                self.position = pos
                break

    def draw(self, surface):
        x, y = self.position[0]*CELL_SIZE, self.position[1]*CELL_SIZE
        surface.blit(food_img, (x,y))

# --- GAME OVER ---
def game_over(score, level):
    gameover_sound.play()
    while True:
        screen.fill(BLACK)

        t1 = font.render(f"GAME OVER", True, RED)
        t2 = font.render(f"Score: {score}  Level: {level}", True, WHITE)
        t3 = font.render("Press R to Restart", True, WHITE)

        screen.blit(t1, (WIDTH//3, HEIGHT//3))
        screen.blit(t2, (WIDTH//4, HEIGHT//2))
        screen.blit(t3, (WIDTH//4, HEIGHT//2 + 40))

        pygame.display.update()

        for e in pygame.event.get():
            if e.type == QUIT:
                pygame.quit()
                sys.exit()
            if e.type == KEYDOWN and e.key == K_r:
                main()

# --- MAIN GAME ---
def main():
    snake = Snake()
    food = Food(snake.body)

    score = 0
    level = 1

    base_speed = 8
    fps = base_speed

    while True:
        # --- EVENTS ---
        for e in pygame.event.get():
            if e.type == QUIT:
                pygame.quit()
                sys.exit()

            if e.type == KEYDOWN:
                if e.key == K_UP and snake.direction != (0,1):
                    snake.direction = (0,-1)
                    move_sound.play()
                elif e.key == K_DOWN and snake.direction != (0,-1):
                    snake.direction = (0,1)
                    move_sound.play()
                elif e.key == K_LEFT and snake.direction != (1,0):
                    snake.direction = (-1,0)
                    move_sound.play()
                elif e.key == K_RIGHT and snake.direction != (-1,0):
                    snake.direction = (1,0)
                    move_sound.play()

        snake.update()
        head = snake.body[0]

        # --- COLLISION ---
        if (
            head[0] < 0 or head[0] >= GRID_WIDTH or
            head[1] < 0 or head[1] >= GRID_HEIGHT or
            head in snake.body[1:]
        ):
            game_over(score, level)

        # --- EAT FOOD ---
        if head == food.position:
            snake.grow = True
            score += 10
            food.randomize(snake.body)
            eat_sound.play()

            # LEVEL SYSTEM
            if score % 40 == 0:
                level += 1
                fps = base_speed + (level - 1) * 2

        # --- DRAW ---
        screen.blit(bg_img, (0,0))

        # BORDER
        pygame.draw.rect(screen, WHITE, (0,0,WIDTH,HEIGHT), 10)

        snake.draw(screen)
        food.draw(screen)

        # SCORE + LEVEL
        text = font.render(
            f"Score: {score}   Level: {level}",
            True,
            GREEN
        )
        screen.blit(text, (10,10))

        pygame.display.update()
        clock.tick(fps)

# --- RUN GAME ---
if __name__ == "__main__":
    main()