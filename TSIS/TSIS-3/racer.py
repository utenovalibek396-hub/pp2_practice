import pygame  # Import the Pygame library for 2D game development
import random  # Import random for generating spawns and positions
import math  # Import math for mathematical operations
from persistence import DIFFICULTY_PARAMS  # Import difficulty settings from the persistence module
from sound import SoundManager  # Import the sound manager to handle game audio

C_WHITE  = (240, 240, 255)  # Define a light white color for text and UI
C_BLACK  = (10,  10,  15)  # Define a near-black color for car details
C_ROAD   = (35,  35,  48)  # Define the dark gray color of the asphalt road
C_MARK   = (200, 180, 40)  # Define the yellowish color for road lane markings
C_CURB_L = (230, 60,  60)  # Define the red color for the left road curb
C_CURB_R = (240, 240, 240)  # Define the white color for the right road curb
C_GRASS  = (40,  90,  40)  # Define the green color for the roadside grass
C_GRAY   = (100, 100, 120)  # Define a standard gray color for secondary UI
C_ACCENT = (255, 200, 0)  # Define an accent gold color for coins
C_GREEN  = (60,  200, 100)  # Define a bright green for active power-ups
C_RED    = (220, 60,  60)  # Define a red color for the player or crashes
C_BLUE   = (60,  130, 230)  # Define a blue color for UI elements
C_SHIELD = (80,  160, 255)  # Define a light blue color for the shield power-up
C_NITRO  = (255, 140, 0)  # Define an orange color for the nitro boost

class Road:  # Class to manage the scrolling background and road drawing
    def __init__(self, w, h):  # Initialize road dimensions and lane setup
        self.w, self.h = w, h  # Store screen width and height
        self.y = 0  # Initialize the vertical offset for the scrolling effect
        self.lane_w = 120  # Define the fixed width for a single lane
        self.road_w = self.lane_w * 3  # Calculate total road width (3 lanes)
        self.left   = (w - self.road_w) // 2  # Calculate the starting X-coordinate of the road

    def update(self, speed):  # Update the road's scroll position based on speed
        self.y = (self.y + speed) % 80  # Loop the Y-offset to create a seamless scrolling animation

    def draw(self, screen):  # Render the grass, road, curbs, and markings
        pygame.draw.rect(screen, C_GRASS, (0, 0, self.w, self.h))  # Draw the green background
        pygame.draw.rect(screen, C_ROAD, (self.left, 0, self.road_w, self.h))  # Draw the asphalt road
        
        for i in range(-1, self.h // 80 + 1):  # Loop to draw repeating curb segments
            y_pos = i * 80 + self.y  # Calculate the dynamic Y position for each segment
            pygame.draw.rect(screen, C_CURB_L, (self.left - 15, y_pos, 15, 40))  # Draw left red curb
            pygame.draw.rect(screen, C_CURB_R, (self.left - 15, y_pos + 40, 15, 40))  # Draw left white curb
            pygame.draw.rect(screen, C_CURB_R, (self.left + self.road_w, y_pos, 15, 40))  # Draw right white curb
            pygame.draw.rect(screen, C_CURB_L, (self.left + self.road_w, y_pos + 40, 15, 40))  # Draw right red curb

        for lx in [self.left + self.lane_w, self.left + 2 * self.lane_w]:  # Loop through lane boundaries
            for i in range(-1, self.h // 60 + 1):  # Loop to draw dashed lane markings
                pygame.draw.rect(screen, C_MARK, (lx - 2, i * 60 + self.y, 4, 30))  # Render yellow dashes

class Player:  # Class representing the player-controlled car
    SIZE = 45  # Define a constant size for the player's car
    def __init__(self, x, y, color):  # Initialize player position and appearance
        self.x, self.y = x, y  # Set current coordinates
        self.color = color  # Set car color from settings
        self.target_x = x  # Store the target X for smooth interpolation

    def move(self, dx):  # Update target X position based on user input
        self.target_x += dx  # Adjust the target position horizontally
        self.target_x = max(330, min(570, self.target_x))  # Clamp position to stay within road bounds

    def update(self):  # Smoothly move the car toward the target X position
        self.x += (self.target_x - self.x) * 0.2  # Apply linear interpolation for smooth movement

    def draw(self, screen):  # Render the player car and its details
        s = self.SIZE  # Use the car size constant
        pygame.draw.rect(screen, self.color, self.rect, border_radius=6)  # Draw the main car body
        pygame.draw.rect(screen, C_BLACK, (self.rect.x + 5, self.rect.y + 5, 10, 12))  # Draw left headlight/window
        pygame.draw.rect(screen, C_BLACK, (self.rect.right - 15, self.rect.y + 5, 10, 12))  # Draw right headlight/window

    @property
    def rect(self):  # Property to get a Pygame Rect object for collision detection
        s = self.SIZE  # Get size
        return pygame.Rect(int(self.x) - s // 2, int(self.y) - s // 2, s, s)  # Create Rect centered on current X, Y

class EnemyCar:  # Class for AI-controlled obstacle cars
    SIZE = 45  # Define constant size for enemy cars
    def __init__(self, x, y, speed):  # Initialize enemy car attributes
        self.rect = pygame.Rect(x - self.SIZE//2, y - self.SIZE//2, self.SIZE, self.SIZE)  # Set bounding box
        self.speed = speed  # Set movement speed
        self.color = (random.randint(100, 200), random.randint(100, 200), random.randint(100, 200))  # Assign random color

    def update(self):  # Move the enemy car down the screen
        self.rect.y += self.speed  # Increase Y position by speed every frame

    def draw(self, screen):  # Render the enemy car body and headlight effects
        # main body
        pygame.draw.rect(screen, self.color, self.rect, border_radius=6)  # Draw main body

        # 🔥 headlights (fara)
        pygame.draw.circle(  # Draw the left headlight core
            screen,
            (255, 255, 200),
            (self.rect.left + 10, self.rect.y + 8),
            4
        )

        pygame.draw.circle(  # Draw the right headlight core
            screen,
            (255, 255, 200),
            (self.rect.right - 10, self.rect.y + 8),
            4
        )

        # optional: small glow effect (әдемірек көріну үшін)
        pygame.draw.circle(  # Draw the outer glow for the left headlight
            screen,
            (255, 255, 150),
            (self.rect.left + 10, self.rect.y + 8),
            8,
            1
        )

        pygame.draw.circle(  # Draw the outer glow for the right headlight
            screen,
            (255, 255, 150),
            (self.rect.right - 10, self.rect.y + 8),
            8,
            1
        )

class RoadObstacle:  # Class for non-car road hazards (oil spills, etc.)
    def __init__(self, x, y, kind):  # Initialize obstacle type and position
        self.rect = pygame.Rect(x - 25, y - 25, 50, 50)  # Set bounding box for the obstacle
        self.kind = kind  # Store the type of obstacle (oil, bump, or strip)

    def update(self, speed):  # Move the obstacle downward at the road speed
        self.rect.y += speed  # Sync movement with the scrolling road

    def draw(self, screen):  # Render the obstacle based on its type
        if self.kind == "oil":   color = (40, 40, 50)  # Set dark color for oil spill
        elif self.kind == "bump": color = (120, 100, 80)  # Set brown color for road bumps
        else: color = (200, 150, 0)  # Set orange color for speed strips
        pygame.draw.ellipse(screen, color, self.rect)  # Draw the obstacle as an oval shape

class Coin:  # Class for collectable coins
    def __init__(self, x, y, value):  # Initialize coin position and point value
        self.rect = pygame.Rect(x-15, y-15, 30, 30)  # Set bounding box for the coin
        self.value = value  # Store how many points/coins this item is worth

    def update(self, speed):  # Move the coin downward with the road
        self.rect.y += speed  # Sync movement speed

    def draw(self, screen):  # Render the coin on the screen
        pygame.draw.circle(screen, C_ACCENT, self.rect.center, 15)  # Draw a golden circle for the coin

class PowerUp:  # Class for temporary ability items
    def __init__(self, x, y, kind):  # Initialize power-up type and position
        self.rect = pygame.Rect(x-20, y-20, 40, 40)  # Set bounding box for the power-up
        self.kind = kind  # Store type (shield or nitro)

    def update(self, speed):  # Move the power-up downward with the road
        self.rect.y += speed  # Sync movement speed

    def draw(self, screen):  # Render the power-up with a specific color
        color = C_SHIELD if self.kind == "shield" else C_NITRO  # Select blue for shield, orange for nitro
        pygame.draw.rect(screen, color, self.rect, border_radius=20)  # Draw a rounded square

class RacerGame:  # Main controller class for the game logic and loop
    FINISH_DIST = 1000  # Distance required to complete the level
    def __init__(self, screen, clock, settings, name):  # Setup game state and assets
        self.screen = screen  # Reference to the Pygame window
        self.clock  = clock  # Reference to the frame rate controller
        self.w, self.h = screen.get_size()  # Store current screen dimensions
        self.player_name = name  # Store current player name
        
        diff = settings.get("difficulty", "normal")  # Get difficulty level from user settings
        params = DIFFICULTY_PARAMS.get(diff, DIFFICULTY_PARAMS["normal"])  # Load specific difficulty values
        self.base_speed = params["enemy_speed"]  # Set starting enemy speed
        self.spawn_rate = params["spawn_rate"]  # Set frequency of enemy spawns
        self.score_scale = params["scale"]  # Set score multiplier based on difficulty

        self.sfx = SoundManager(settings.get("sound", True))  # Initialize sound system
        self.road = Road(self.w, self.h)  # Create road instance
        self.player = Player(self.w // 2, self.h - 100, settings.get("car_color", C_RED))  # Create player instance
        
        self.enemies, self.obstacles, self.coins, self.powerups = [], [], [], []  # Initialize object lists
        self.score, self.distance, self.coins_count = 0, 0, 0  # Initialize game stats
        self.active_pu, self.pu_end_time = None, 0  # Manage active power-up state
        self.alive = True  # Flag to track if the game session is active
        self.font = pygame.font.SysFont("Arial", 24, True)  # Load font for HUD display

    def run(self):  # Main game loop method
        self.sfx.start_engine()  # Play the looping engine sound
        while self.alive:  # Loop until the player crashes or finishes
            now = pygame.time.get_ticks()  # Get the current time in milliseconds
            self._handle_input()  # Process keyboard events
            self._update(now)  # Update all game object positions and states
            self._draw(now)  # Render all objects to the screen
            pygame.display.flip()  # Refresh the display window
            self.clock.tick(60)  # Cap the frame rate at 60 FPS
        self.sfx.stop_engine()  # Stop the engine sound when the game ends
        return int(self.score), int(self.distance), self.coins_count  # Return session results

    def _handle_input(self):  # Process user controls
        for event in pygame.event.get():  # Iterate through Pygame event queue
            if event.type == pygame.QUIT: self.alive = False  # End game if window is closed
        keys = pygame.key.get_pressed()  # Get the state of all keyboard keys
        if keys[pygame.K_LEFT] or keys[pygame.K_a]: self.player.move(-12)  # Move left on key press
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]: self.player.move(12)  # Move right on key press

    def _update(self, now):  # Manage game logic and movement
        speed_mult = 1.8 if self.active_pu == "nitro" else 1.0  # Apply nitro speed multiplier if active
        cur_speed = (self.base_speed + (self.distance / 200)) * speed_mult  # Calculate speed increasing over time
        self.sfx.set_engine_pitch(cur_speed / 15)  # Adjust engine sound pitch based on speed

        self.road.update(cur_speed)  # Update scrolling road position
        self.player.update()  # Update player car position
        self.distance += cur_speed / 60  # Increment total distance traveled
        self.score += (cur_speed / 60) * self.score_scale  # Increment score based on speed and difficulty

        if self.active_pu and now > self.pu_end_time:  # Check if power-up duration has expired
            self.active_pu = None  # Reset active power-up

        self._spawn_logic(cur_speed)  # Handle procedural generation of items

        for e in self.enemies: e.update()  # Update all enemy positions
        for o in self.obstacles: o.update(cur_speed)  # Update all obstacle positions
        for c in self.coins: c.update(cur_speed)  # Update all coin positions
        for p in self.powerups: p.update(cur_speed)  # Update all power-up positions

        self._check_collisions()  # Check for player contact with objects

        self.enemies   = [e for e in self.enemies if e.rect.y < self.h]  # Remove off-screen enemies
        self.obstacles = [o for o in self.obstacles if o.rect.y < self.h]  # Remove off-screen obstacles
        self.coins     = [c for c in self.coins if c.rect.y < self.h]  # Remove off-screen coins
        self.powerups  = [p for p in self.powerups if p.rect.y < self.h]  # Remove off-screen power-ups

    def _spawn_logic(self, speed):  # Procedurally generate game objects
        lane_x = [330, 450, 570]  # Define center X-coordinates for the three lanes
        if random.random() < self.spawn_rate:  # Random chance to spawn an enemy car
            x = random.choice(lane_x)  # Pick a random lane
            if not any(e.rect.colliderect(pygame.Rect(x-30, -100, 60, 150)) for e in self.enemies):  # Prevent overlapping spawns
                self.enemies.append(EnemyCar(x, -50, speed + random.uniform(1, 3)))  # Add new enemy car
        
        if random.random() < 0.01:  # 1% chance to spawn a coin
            self.coins.append(Coin(random.choice(lane_x), -30, random.choice([1, 1, 1, 3, 5])))  # Add new coin with random value
        
        if random.random() < 0.005:  # 0.5% chance to spawn a road obstacle
            self.obstacles.append(RoadObstacle(random.choice(lane_x), -30, random.choice(["oil", "bump", "strip"])))  # Add new obstacle
            
        if random.random() < 0.002:  # 0.2% chance to spawn a power-up
            self.powerups.append(PowerUp(random.choice(lane_x), -30, random.choice(["shield", "nitro"])))  # Add new power-up

    def _activate_powerup(self, kind):  # Handle activation of different power-up types
        if kind == "repair": return  # Ignore repair type for now
        self.active_pu = kind  # Set the current active power-up type
        self.pu_end_time = pygame.time.get_ticks() + (4000 if kind == "nitro" else 1000000)  # Set duration (infinite for shield until used)

    def _check_collisions(self):  # Detect interactions between player and world objects
        pr = self.player.rect  # Get the player's current bounding box
        for e in self.enemies[:]:  # Check each enemy car
            if pr.colliderect(e.rect):  # If a collision with an enemy occurs
                if self.active_pu == "shield":  # If player has an active shield
                    self.active_pu = None  # Consume the shield
                    self.enemies.remove(e)  # Remove the hit enemy
                    self.sfx.play("shield")  # Play shield sound effect
                else:  # If no shield
                    self.sfx.play("crash")  # Play crash sound effect
                    self.alive = False  # End the game session

        for o in self.obstacles[:]:  # Check for road obstacles
            if pr.colliderect(o.rect):  # If hit
                if o.kind == "strip":  # If it's a speed strip
                    self._activate_powerup("nitro")  # Grant nitro boost
                    self.sfx.play("nitro")  # Play nitro sound
                self.obstacles.remove(o)  # Remove the obstacle after contact

        for c in self.coins[:]:  # Check for coins
            if pr.colliderect(c.rect):  # If collected
                self.coins_count += c.value  # Add to total coins
                self.score += c.value * 15  # Add bonus points to score
                self.coins.remove(c)  # Remove the coin from the game
                self.sfx.play("coin")  # Play coin sound effect

        for p in self.powerups[:]:  # Check for power-up items
            if pr.colliderect(p.rect):  # If collected
                self._activate_powerup(p.kind)  # Activate the specific power-up
                self.powerups.remove(p)  # Remove the item
                self.sfx.play("powerup")  # Play power-up collection sound

        if self.distance >= self.FINISH_DIST:  # Check if player reached the finish line
            self.score += 500  # Grant finish line bonus
            self.alive = False  # Successfully end the game session

    def _draw(self, now):  # Render the game frame
        self.road.draw(self.screen)  # Draw the scrolling road background
        for o in self.obstacles: o.draw(self.screen)  # Draw all active obstacles
        for c in self.coins: c.draw(self.screen)  # Draw all active coins
        for p in self.powerups: p.draw(self.screen)  # Draw all active power-ups
        for e in self.enemies: e.draw(self.screen)  # Draw all enemy cars
        self.player.draw(self.screen)  # Draw the player's car

        s_txt = self.font.render(f"Score: {int(self.score)}", True, C_WHITE)  # Create score text
        c_txt = self.font.render(f"Coins: {self.coins_count}", True, C_ACCENT)  # Create coins text
        d_txt = self.font.render(f"Dist: {int(self.distance)}m", True, C_GRAY)  # Create distance text
        self.screen.blit(s_txt, (20, 20))  # Draw score to HUD
        self.screen.blit(c_txt, (20, 55))  # Draw coins to HUD
        self.screen.blit(d_txt, (20, 90))  # Draw distance to HUD

        if self.active_pu:  # If a power-up is active
            p_txt = self.font.render(f"ACTIVE: {self.active_pu.upper()}", True, C_GREEN)  # Create power-up alert text
            self.screen.blit(p_txt, (self.w - 200, 20))  # Draw power-up text to the top-right