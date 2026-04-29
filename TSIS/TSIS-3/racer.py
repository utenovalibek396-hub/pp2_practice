import pygame
import random
import math
from persistence import DIFFICULTY_PARAMS
from sound import SoundManager

C_WHITE  = (240, 240, 255)
C_BLACK  = (10,  10,  15)
C_ROAD   = (35,  35,  48)
C_MARK   = (200, 180, 40)
C_CURB_L = (230, 60,  60)
C_CURB_R = (240, 240, 240)
C_GRASS  = (40,  90,  40)
C_GRAY   = (100, 100, 120)
C_ACCENT = (255, 200, 0)
C_GREEN  = (60,  200, 100)
C_RED    = (220, 60,  60)
C_BLUE   = (60,  130, 230)
C_SHIELD = (80,  160, 255)
C_NITRO  = (255, 140, 0)

class Road:
    def __init__(self, w, h):
        self.w, self.h = w, h
        self.y = 0
        self.lane_w = 120
        self.road_w = self.lane_w * 3
        self.left   = (w - self.road_w) // 2

    def update(self, speed):
        self.y = (self.y + speed) % 80

    def draw(self, screen):
        pygame.draw.rect(screen, C_GRASS, (0, 0, self.w, self.h))
        pygame.draw.rect(screen, C_ROAD, (self.left, 0, self.road_w, self.h))
        
        for i in range(-1, self.h // 80 + 1):
            y_pos = i * 80 + self.y
            pygame.draw.rect(screen, C_CURB_L, (self.left - 15, y_pos, 15, 40))
            pygame.draw.rect(screen, C_CURB_R, (self.left - 15, y_pos + 40, 15, 40))
            pygame.draw.rect(screen, C_CURB_R, (self.left + self.road_w, y_pos, 15, 40))
            pygame.draw.rect(screen, C_CURB_L, (self.left + self.road_w, y_pos + 40, 15, 40))

        for lx in [self.left + self.lane_w, self.left + 2 * self.lane_w]:
            for i in range(-1, self.h // 60 + 1):
                pygame.draw.rect(screen, C_MARK, (lx - 2, i * 60 + self.y, 4, 30))

class Player:
    SIZE = 45
    def __init__(self, x, y, color):
        self.x, self.y = x, y
        self.color = color
        self.target_x = x

    def move(self, dx):
        self.target_x += dx
        self.target_x = max(330, min(570, self.target_x))

    def update(self):
        self.x += (self.target_x - self.x) * 0.2

    def draw(self, screen):
        s = self.SIZE
        pygame.draw.rect(screen, self.color, self.rect, border_radius=6)
        pygame.draw.rect(screen, C_BLACK, (self.rect.x + 5, self.rect.y + 5, 10, 12))
        pygame.draw.rect(screen, C_BLACK, (self.rect.right - 15, self.rect.y + 5, 10, 12))

    @property
    def rect(self):
        s = self.SIZE
        return pygame.Rect(int(self.x) - s // 2, int(self.y) - s // 2, s, s)

class EnemyCar:
    SIZE = 45
    def __init__(self, x, y, speed):
        self.rect = pygame.Rect(x - self.SIZE//2, y - self.SIZE//2, self.SIZE, self.SIZE)
        self.speed = speed
        self.color = (random.randint(100, 200), random.randint(100, 200), random.randint(100, 200))

    def update(self):
        self.rect.y += self.speed

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, self.rect, border_radius=6)
        pygame.draw.circle(screen, (255, 255, 180),
                       (self.rect.left + 10, self.rect.y + 10), 4)
        pygame.draw.circle(screen, (255, 255, 180),
                       (self.rect.right - 10, self.rect.y + 10), 4)
class RoadObstacle:
    def __init__(self, x, y, kind):
        self.rect = pygame.Rect(x - 25, y - 25, 50, 50)
        self.kind = kind

    def update(self, speed):
        self.rect.y += speed

    def draw(self, screen):
        if self.kind == "oil":   color = (40, 40, 50)
        elif self.kind == "bump": color = (120, 100, 80)
        else: color = (200, 150, 0)
        pygame.draw.ellipse(screen, color, self.rect)

class Coin:
    def __init__(self, x, y, value):
        self.rect = pygame.Rect(x-15, y-15, 30, 30)
        self.value = value

    def update(self, speed):
        self.rect.y += speed

    def draw(self, screen):
        pygame.draw.circle(screen, C_ACCENT, self.rect.center, 15)

class PowerUp:
    def __init__(self, x, y, kind):
        self.rect = pygame.Rect(x-20, y-20, 40, 40)
        self.kind = kind

    def update(self, speed):
        self.rect.y += speed

    def draw(self, screen):
        color = C_SHIELD if self.kind == "shield" else C_NITRO
        pygame.draw.rect(screen, color, self.rect, border_radius=20)

class RacerGame:
    FINISH_DIST = 1000
    def __init__(self, screen, clock, settings, name):
        self.screen = screen
        self.clock  = clock
        self.w, self.h = screen.get_size()
        self.player_name = name
        
        diff = settings.get("difficulty", "normal")
        params = DIFFICULTY_PARAMS.get(diff, DIFFICULTY_PARAMS["normal"])
        self.base_speed = params["enemy_speed"]
        self.spawn_rate = params["spawn_rate"]
        self.score_scale = params["scale"]

        self.sfx = SoundManager(settings.get("sound", True))
        self.road = Road(self.w, self.h)
        self.player = Player(self.w // 2, self.h - 100, settings.get("car_color", C_RED))
        
        self.enemies, self.obstacles, self.coins, self.powerups = [], [], [], []
        self.score, self.distance, self.coins_count = 0, 0, 0
        self.active_pu, self.pu_end_time = None, 0
        self.alive = True
        self.font = pygame.font.SysFont("Arial", 24, True)

    def run(self):
        self.sfx.start_engine()
        while self.alive:
            now = pygame.time.get_ticks()
            self._handle_input()
            self._update(now)
            self._draw(now)
            pygame.display.flip()
            self.clock.tick(60)
        self.sfx.stop_engine()
        return int(self.score), int(self.distance), self.coins_count

    def _handle_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT: self.alive = False
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] or keys[pygame.K_a]: self.player.move(-12)
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]: self.player.move(12)

    def _update(self, now):
        speed_mult = 1.8 if self.active_pu == "nitro" else 1.0
        cur_speed = (self.base_speed + (self.distance / 200)) * speed_mult
        self.sfx.set_engine_pitch(cur_speed / 15)

        self.road.update(cur_speed)
        self.player.update()
        self.distance += cur_speed / 60
        self.score += (cur_speed / 60) * self.score_scale

        if self.active_pu and now > self.pu_end_time:
            self.active_pu = None

        self._spawn_logic(cur_speed)

        for e in self.enemies: e.update()
        for o in self.obstacles: o.update(cur_speed)
        for c in self.coins: c.update(cur_speed)
        for p in self.powerups: p.update(cur_speed)

        self._check_collisions()

        self.enemies   = [e for e in self.enemies if e.rect.y < self.h]
        self.obstacles = [o for o in self.obstacles if o.rect.y < self.h]
        self.coins     = [c for c in self.coins if c.rect.y < self.h]
        self.powerups  = [p for p in self.powerups if p.rect.y < self.h]

    def _spawn_logic(self, speed):
        lane_x = [330, 450, 570]
        if random.random() < self.spawn_rate:
            x = random.choice(lane_x)
            if not any(e.rect.colliderect(pygame.Rect(x-30, -100, 60, 150)) for e in self.enemies):
                self.enemies.append(EnemyCar(x, -50, speed + random.uniform(1, 3)))
        
        if random.random() < 0.01:
            self.coins.append(Coin(random.choice(lane_x), -30, random.choice([1, 1, 1, 3, 5])))
        
        if random.random() < 0.005:
            self.obstacles.append(RoadObstacle(random.choice(lane_x), -30, random.choice(["oil", "bump", "strip"])))
            
        if random.random() < 0.002:
            self.powerups.append(PowerUp(random.choice(lane_x), -30, random.choice(["shield", "nitro"])))

    def _activate_powerup(self, kind):
        if kind == "repair": return
        self.active_pu = kind
        self.pu_end_time = pygame.time.get_ticks() + (4000 if kind == "nitro" else 1000000)

    def _check_collisions(self):
        pr = self.player.rect
        for e in self.enemies[:]:
            if pr.colliderect(e.rect):
                if self.active_pu == "shield":
                    self.active_pu = None
                    self.enemies.remove(e)
                    self.sfx.play("shield")
                else:
                    self.sfx.play("crash")
                    self.alive = False

        for o in self.obstacles[:]:
            if pr.colliderect(o.rect):
                if o.kind == "strip":
                    self._activate_powerup("nitro")
                    self.sfx.play("nitro")
                self.obstacles.remove(o)

        for c in self.coins[:]:
            if pr.colliderect(c.rect):
                self.coins_count += c.value
                self.score += c.value * 15
                self.coins.remove(c)
                self.sfx.play("coin")

        for p in self.powerups[:]:
            if pr.colliderect(p.rect):
                self._activate_powerup(p.kind)
                self.powerups.remove(p)
                self.sfx.play("powerup")

        if self.distance >= self.FINISH_DIST:
            self.score += 500
            self.alive = False

    def _draw(self, now):
        self.road.draw(self.screen)
        for o in self.obstacles: o.draw(self.screen)
        for c in self.coins: c.draw(self.screen)
        for p in self.powerups: p.draw(self.screen)
        for e in self.enemies: e.draw(self.screen)
        self.player.draw(self.screen)

        s_txt = self.font.render(f"Score: {int(self.score)}", True, C_WHITE)
        c_txt = self.font.render(f"Coins: {self.coins_count}", True, C_ACCENT)
        d_txt = self.font.render(f"Dist: {int(self.distance)}m", True, C_GRAY)
        self.screen.blit(s_txt, (20, 20))
        self.screen.blit(c_txt, (20, 55))
        self.screen.blit(d_txt, (20, 90))

        if self.active_pu:
            p_txt = self.font.render(f"ACTIVE: {self.active_pu.upper()}", True, C_GREEN)
            self.screen.blit(p_txt, (self.w - 200, 20))