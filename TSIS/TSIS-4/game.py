# game.py — Core game logic # Main file defining the fundamental mechanics of the game

import pygame # Import Pygame library for multimedia and game engine functions
import random # Import random module for spawning food and obstacles in random locations
import json # Import json for potential data serialization or config handling
import os # Import os for interacting with the operating system and file paths
import math # Import math for wave generation and trigonometric calculations
import array # Import array for efficient storage of binary sound data
from config import * # Import all constants and settings from the local config file


# ─────────────────────────────────────────────────────────────
#  Sound Manager # Section for procedural sound generation and management
# ─────────────────────────────────────────────────────────────

class SoundManager: # Define a class to handle audio without external sound files
    """Generates and plays all game sounds procedurally (no audio files needed).""" # Class documentation string

    SAMPLE_RATE = 22050 # Set the standard audio sampling rate in Hertz

    def __init__(self): # Constructor for initializing the sound system
        self._enabled = False # Default state for sound is disabled
        self._sounds: dict[str, pygame.mixer.Sound] = {} # Dictionary to store pre-generated Sound objects
        try: # Use a try block to handle audio hardware initialization risks
            pygame.mixer.pre_init(self.SAMPLE_RATE, -16, 1, 512) # Configure audio mixer settings before init
            pygame.mixer.init() # Initialize the Pygame mixer module
            self._sounds = { # Map sound names to their procedurally generated waveforms
                "eat":      self._make_eat(), # Sound for consuming regular food
                "bonus":    self._make_bonus(), # Sound for consuming bonus items
                "rare":     self._make_rare(), # Sparkle sound for rare food items
                "poison":   self._make_poison(), # Negative sound for eating poison
                "powerup":  self._make_powerup(), # Arpeggio sound for collecting power-ups
                "levelup":  self._make_levelup(), # Fanfare sound for reaching a new level
                "die":      self._make_die(), # Crash sound for game over events
            } # End of sound dictionary
        except Exception as e: # Catch any errors during mixer or sound generation
            print(f"[Sound] init error: {e}") # Print the error to console for debugging

    # ── Public API ──────────────────────────────────────────

    def set_enabled(self, enabled: bool): # Method to toggle game sounds on or off
        self._enabled = enabled # Update the internal enabled status

    def play(self, name: str): # Method to play a generated sound by its key name
        if not self._enabled: # Check if the sound system is currently muted
            return # Exit if sound is disabled
        snd = self._sounds.get(name) # Retrieve the sound object from the dictionary
        if snd: # If the sound exists in our collection
            snd.play() # Trigger the audio playback

    # ── Waveform builders ───────────────────────────────────

    def _build(self, samples: list[float], volume: float = 0.6) -> pygame.mixer.Sound: # Convert raw numbers to Pygame sound
        """Convert float samples [-1,1] to a pygame Sound.""" # Docstring for sample conversion
        peak = max(abs(s) for s in samples) or 1.0 # Find the maximum amplitude for normalization
        int_samples = array.array("h", [ # Convert float list to a signed 16-bit integer array
            int(s / peak * 32767 * volume) for s in samples # Scale float to range [-32767, 32767]
        ]) # End of sample list comprehension
        sound = pygame.mixer.Sound(buffer=int_samples) # Create a Sound object from the raw buffer
        return sound # Return the playable Sound object

    def _sine(self, freq: float, duration: float, decay: float = 3.0) -> list[float]: # Generate a simple sine wave
        n = int(self.SAMPLE_RATE * duration) # Calculate total number of samples needed
        return [ # Create a list of sine wave values with exponential decay
            math.sin(2 * math.pi * freq * i / self.SAMPLE_RATE) # Calculate the pure sine tone
            * math.exp(-decay * i / n) # Apply the volume decay over time
            for i in range(n) # Iterate through every sample index
        ] # End of list comprehension

    def _sweep(self, f0: float, f1: float, duration: float, decay: float = 2.0) -> list[float]: # Generate a frequency sweep
        n = int(self.SAMPLE_RATE * duration) # Calculate total sample count
        return [ # Create a list where the frequency shifts from start to end
            math.sin(2 * math.pi * (f0 + (f1 - f0) * i / n) * i / self.SAMPLE_RATE) # Calculate swept tone
            * math.exp(-decay * i / n) # Apply exponential volume decay
            for i in range(n) # Iterate through every sample index
        ] # End of list comprehension

    def _noise(self, duration: float, decay: float = 8.0) -> list[float]: # Generate randomized noise (static)
        n = int(self.SAMPLE_RATE * duration) # Calculate sample count
        return [ # Create a list of random values for a "crunchy" sound
            (random.random() * 2 - 1) * math.exp(-decay * i / n) # Generate range [-1, 1] with decay
            for i in range(n) # Iterate through every sample index
        ] # End of list comprehension

    def _mix(self, *tracks: list[float]) -> list[float]: # Combine multiple audio tracks into one
        length = max(len(t) for t in tracks) # Determine the longest track length
        result = [] # Initialize the combined result list
        for i in range(length): # Iterate through each time index
            result.append(sum(t[i] if i < len(t) else 0.0 for t in tracks)) # Sum amplitudes at this index
        return result # Return the layered audio data

    # ── Sound definitions ───────────────────────────────────

    def _make_eat(self) -> pygame.mixer.Sound: # Create a quick upward blip
        """Short upward blip for normal food.""" # Docstring
        return self._build(self._sweep(300, 600, 0.08, decay=4.0), volume=0.5) # Sweep from 300Hz to 600Hz

    def _make_bonus(self) -> pygame.mixer.Sound: # Create a double chime sound
        """Two-tone chime for bonus food.""" # Docstring
        a = self._sweep(500, 900, 0.1, decay=3.0) # Primary sweep
        b = [0.0] * int(self.SAMPLE_RATE * 0.05) + self._sweep(700, 1100, 0.1, decay=3.0) # Delayed second sweep
        return self._build(self._mix(a, b), volume=0.55) # Mix and build the sound

    def _make_rare(self) -> pygame.mixer.Sound: # Create a triple-note sparkle
        """Three-tone sparkle for rare food.""" # Docstring
        a = self._sine(880, 0.08, decay=4.0) # First high note
        b = [0.0] * int(self.SAMPLE_RATE * 0.07) + self._sine(1100, 0.08, decay=4.0) # Second note delayed
        c = [0.0] * int(self.SAMPLE_RATE * 0.14) + self._sine(1320, 0.10, decay=3.0) # Third note delayed
        return self._build(self._mix(a, b, c), volume=0.5) # Mix into a single sparkle sound

    def _make_poison(self) -> pygame.mixer.Sound: # Create a harsh downward sound
        """Downward buzz for poison.""" # Docstring
        tone = self._sweep(400, 150, 0.18, decay=2.5) # Deep downward frequency sweep
        noise = self._noise(0.18, decay=5.0) # Add a layer of static noise
        return self._build(self._mix(tone, [n * 0.3 for n in noise]), volume=0.6) # Mix and build

    def _make_powerup(self) -> pygame.mixer.Sound: # Create a rising melodic sequence
        """Rising arpeggio for power-up pickup.""" # Docstring
        freqs = [523, 659, 784, 1047] # Musical frequencies (C, E, G, C)
        result: list[float] = [] # Initialize the sequence list
        step = int(self.SAMPLE_RATE * 0.07) # Set duration for each note
        for freq in freqs: # Loop through the frequencies
            result += self._sine(freq, 0.07, decay=5.0) + [0.0] * (step - int(self.SAMPLE_RATE * 0.07)) # Append notes
        return self._build(result, volume=0.55) # Build the final arpeggio

    def _make_levelup(self) -> pygame.mixer.Sound: # Create a overlapping triumphant fanfare
        """Fanfare for level-up.""" # Docstring
        freqs = [523, 659, 784, 1047, 1319] # Chord frequencies
        result: list[float] = [] # Initialize result list
        for i, freq in enumerate(freqs): # Loop through notes with index
            pause = [0.0] * int(self.SAMPLE_RATE * 0.04 * i) # Calculate staggered start time
            result = self._mix(result + [0.0] * (len(pause) + int(self.SAMPLE_RATE * 0.18)), # Extend list
                               pause + self._sine(freq, 0.18, decay=2.0)) # Add new note to the mix
        return self._build(result, volume=0.6) # Build fanfare

    def _make_die(self) -> pygame.mixer.Sound: # Create a heavy crashing/failing sound
        """Descending crash for death.""" # Docstring
        tone = self._sweep(300, 60, 0.5, decay=1.5) # Long downward bass sweep
        noise = self._noise(0.4, decay=2.0) # Heavy static noise
        combined = self._mix(tone, [n * 0.5 for n in noise]) # Mix the crash elements
        return self._build(combined, volume=0.7) # Build death sound


# ─────────────────────────────────────────────────────────────
#  Helpers # Utility functions for coordinates and grid logic
# ─────────────────────────────────────────────────────────────

def cell_rect(col: int, row: int) -> pygame.Rect: # Convert grid coordinates to screen pixels
    return pygame.Rect( # Return a Pygame Rect object
        PLAY_AREA_X + col * CELL_SIZE, # Calculate X position relative to play area
        PLAY_AREA_Y + row * CELL_SIZE, # Calculate Y position relative to play area
        CELL_SIZE, # Width of the cell
        CELL_SIZE, # Height of the cell
    ) # End of Rect parameters


def random_free_cell(occupied: set) -> tuple[int, int] | None: # Find an empty grid cell
    free = [ # Create a list of all cells not currently occupied
        (c, r) # The grid coordinate tuple
        for c in range(GRID_COLS) # Iterate through all columns
        for r in range(GRID_ROWS) # Iterate through all rows
        if (c, r) not in occupied # Filter out snake, food, and obstacles
    ] # End list comprehension
    return random.choice(free) if free else None # Pick a random free cell or return None if full


# ─────────────────────────────────────────────────────────────
#  Food # Classes representing items to be consumed
# ─────────────────────────────────────────────────────────────

class Food: # Represents different types of beneficial food
    def __init__(self, pos: tuple[int, int], ftype: dict): # Constructor with position and type info
        self.pos = pos # Store grid position
        self.color = ftype["color"] # Store drawing color
        self.points = ftype["points"] # Store point value
        self.timed = ftype["timed"] # Boolean indicating if food disappears
        self.spawn_time = pygame.time.get_ticks() # Record timestamp of creation

    def is_expired(self) -> bool: # Check if timed food has been on screen too long
        if not self.timed: # Permanent food never expires
            return False # Keep on screen
        return pygame.time.get_ticks() - self.spawn_time > FOOD_DISAPPEAR_MS # Compare age to limit

    def draw(self, surface: pygame.Surface): # Render the food to the screen
        rect = cell_rect(*self.pos) # Get pixel coordinates
        pygame.draw.ellipse(surface, self.color, rect.inflate(-4, -4)) # Draw food as an ellipse
        # Blinking effect when about to expire
        if self.timed: # Only apply logic to temporary food
            elapsed = pygame.time.get_ticks() - self.spawn_time # Calculate current age
            remaining = FOOD_DISAPPEAR_MS - elapsed # Calculate time left
            if remaining < 2000 and (remaining // 200) % 2 == 0: # Blink if less than 2 seconds left
                pygame.draw.ellipse(surface, WHITE, rect.inflate(-8, -8), 2) # Draw blink ring


class PoisonFood: # Represents harmful obstacles that shrink the snake
    def __init__(self, pos: tuple[int, int]): # Initialize position
        self.pos = pos # Store grid position
        self.spawn_time = pygame.time.get_ticks() # Record creation time

    def draw(self, surface: pygame.Surface): # Render the poison block
        rect = cell_rect(*self.pos) # Get pixel coordinates
        pygame.draw.rect(surface, POISON_COLOR, rect.inflate(-4, -4), border_radius=4) # Draw block
        # Skull-like cross mark
        cx, cy = rect.centerx, rect.centery # Get center points
        pygame.draw.line(surface, WHITE, (cx - 4, cy - 4), (cx + 4, cy + 4), 2) # Draw first line of 'X'
        pygame.draw.line(surface, WHITE, (cx + 4, cy - 4), (cx - 4, cy + 4), 2) # Draw second line of 'X'


# ─────────────────────────────────────────────────────────────
#  Power-ups # Items that grant special abilities
# ─────────────────────────────────────────────────────────────

class PowerUp: # Represents collectible abilities
    def __init__(self, pos: tuple[int, int], kind: str): # Initialize with type (speed/shield/etc)
        self.pos = pos # Store grid position
        self.kind = kind # Store type identifier
        self.color = POWERUP_COLORS[kind] # Assign color based on type
        self.spawn_time = pygame.time.get_ticks() # Record creation time

    def is_expired(self) -> bool: # Check if power-up should vanish from field
        return pygame.time.get_ticks() - self.spawn_time > POWERUP_FIELD_MS # Compare age to lifetime

    def draw(self, surface: pygame.Surface): # Render power-up as a triangle
        rect = cell_rect(*self.pos) # Get pixel coordinates
        pygame.draw.polygon( # Draw triangular shape
            surface, # Target surface
            self.color, # Color based on kind
            [ # Define three points of the triangle
                (rect.centerx, rect.top + 2), # Top point
                (rect.right - 2, rect.bottom - 2), # Bottom right point
                (rect.left + 2, rect.bottom - 2), # Bottom left point
            ], # End points
        ) # End polygon
        label = {"speed": "S", "slow": "W", "shield": "X"}[self.kind] # Get letter representation
        font = pygame.font.SysFont("monospace", 10, bold=True) # Prepare small bold font
        surf = font.render(label, True, BLACK) # Render the letter
        surface.blit(surf, surf.get_rect(center=rect.center)) # Center the letter on the triangle


# ─────────────────────────────────────────────────────────────
#  Snake # Class managing the player character's behavior and rendering
# ─────────────────────────────────────────────────────────────

class Snake: # Main player class
    def __init__(self, color: list): # Initialize with user-chosen color
        self.color = tuple(color) # Store color as immutable tuple
        self.reset() # Setup initial state

    def reset(self): # Reset snake to starting state
        cx, cy = GRID_COLS // 2, GRID_ROWS // 2 # Find center of grid
        self.body = [(cx, cy), (cx - 1, cy), (cx - 2, cy)] # Initialize segments list
        self.direction = (1, 0) # Start moving right
        self.next_direction = (1, 0) # Queue initial direction
        self.grow_pending = 0 # Count segments waiting to be added

    def set_direction(self, dx: int, dy: int): # Update intended movement direction
        # Prevent 180-degree reversal
        if (dx, dy) != (-self.direction[0], -self.direction[1]): # Check if input is not opposite current
            self.next_direction = (dx, dy) # Save new valid direction

    def move(self) -> tuple[int, int]: # Calculate and execute next movement step
        """Advance the snake one step. Returns new head position.""" # Docstring
        self.direction = self.next_direction # Apply the queued direction
        hx, hy = self.body[0] # Get current head coordinates
        new_head = (hx + self.direction[0], hy + self.direction[1]) # Calculate new head coordinates
        self.body.insert(0, new_head) # Add new head to front of body list
        if self.grow_pending > 0: # Check if snake should grow instead of shrinking tail
            self.grow_pending -= 1 # Consume one growth segment
        else: # Standard move: remove the last tail segment
            self.body.pop() # Remove last segment
        return new_head # Return the position for collision checking

    def grow(self, segments: int = 1): # Mark snake to increase length
        self.grow_pending += segments # Increment growth counter

    def shorten(self, segments: int = 2): # Shrink snake length (from poison)
        remove = min(segments, len(self.body) - 1) # Calculate how many segments can be safely removed
        if remove > 0: # If there are segments to remove
            self.body = self.body[:-remove] # Slice the body list to remove tail parts

    @property
    def head(self) -> tuple[int, int]: # Convenience property to get head position
        return self.body[0] # Return first element of body list

    def occupies(self) -> set: # Get all coordinates occupied by the snake
        return set(self.body) # Return as a set for fast lookup

    def draw(self, surface: pygame.Surface, shield_active: bool): # Render the snake body
        for i, (col, row) in enumerate(self.body): # Loop through each segment
            rect = cell_rect(col, row) # Get pixel coordinates
            shade = max(30, 255 - i * 8) # Calculate gradient darkening for tail
            color = ( # Blend segment color with calculated shade
                min(self.color[0], shade), # Adjusted Red
                min(self.color[1], shade), # Adjusted Green
                min(self.color[2], shade), # Adjusted Blue
            ) # End color tuple
            pygame.draw.rect(surface, color, rect.inflate(-2, -2), border_radius=4) # Draw segment

        # Draw shield aura on head
        if shield_active: # If the shield effect is currently enabled
            head_rect = cell_rect(*self.body[0]) # Get head pixel coordinates
            pygame.draw.rect( # Draw an outer glow around the head
                surface, POWERUP_COLORS["shield"], # Use shield color
                head_rect.inflate(4, 4), 2, border_radius=6 # Draw border outline
            ) # End shield drawing


# ─────────────────────────────────────────────────────────────
#  GameState # Orchestrator class managing levels, score, and all objects
# ─────────────────────────────────────────────────────────────

class GameState: # Active session manager
    """Encapsulates one active game session.""" # Docstring

    def __init__(self, snake_color: list): # Initialize new game session
        self.snake = Snake(snake_color) # Create the snake object
        self.score = 0 # Initial score
        self.level = 1 # Initial level
        self.food_eaten_this_level = 0 # Progress tracker for level up
        self.foods: list[Food] = [] # List of active beneficial food items
        self.poison: PoisonFood | None = None # Slot for a single poison item
        self.powerup: PowerUp | None = None # Slot for a single power-up item
        self.obstacles: set = set() # Set of coordinates for wall blocks

        # Power-up effect state
        self.active_effect: str | None = None   # Current buff: 'speed', 'slow', or 'shield'
        self.effect_start: int = 0 # Timestamp when power-up was collected
        self.shield_triggered = False # Flag to track if shield has already blocked one hit

        # Move timer
        self._last_move_ms = 0 # Last timestamp when the snake advanced

        # Spawn initial food
        self._spawn_food() # Create first set of food
        self._try_spawn_poison() # Potentially create poison

    # ── Speed ──────────────────────────────────────────────

    def _current_speed(self) -> float: # Calculate steps per second
        base = BASE_SPEED + (self.level - 1) * SPEED_INCREMENT # Base speed increases per level
        if self.active_effect == "speed": # Check for speed buff
            return base * SPEED_BOOST_FACTOR # Multiply speed
        if self.active_effect == "slow": # Check for slow debuff/buff
            return base * SLOW_FACTOR # Reduce speed
        return base # Return default level speed

    def _move_interval_ms(self) -> int: # Calculate delay between moves in milliseconds
        return int(1000 / self._current_speed()) # Convert frequency to period

    # ── Occupied cells ─────────────────────────────────────

    def _all_occupied(self) -> set: # Get all taken spots for spawning logic
        occupied = self.snake.occupies() | self.obstacles # Include snake and static walls
        for f in self.foods: # Add current food positions
            occupied.add(f.pos) # Add coordinate
        if self.poison: # Add poison position if exists
            occupied.add(self.poison.pos) # Add coordinate
        if self.powerup: # Add power-up position if exists
            occupied.add(self.powerup.pos) # Add coordinate
        return occupied # Return comprehensive set of taken spots

    # ── Spawning ───────────────────────────────────────────

    def _spawn_food(self): # Logic to keep food items on screen
        # Keep up to 3 food items on field (one per type)
        existing_types = {f.points for f in self.foods} # Identify which food types are missing
        for ftype in FOOD_TYPES: # Iterate through defined food varieties
            if ftype["points"] not in existing_types: # If this specific variety is missing
                pos = random_free_cell(self._all_occupied()) # Find a valid empty spot
                if pos: # If a spot was found
                    self.foods.append(Food(pos, ftype)) # Instantiate and add the food

    def _try_spawn_poison(self): # Chance-based logic for poison spawning
        if self.poison is None and random.random() < 0.3: # Check if empty and roll 30% chance
            pos = random_free_cell(self._all_occupied()) # Find free spot
            if pos: # If found
                self.poison = PoisonFood(pos) # Spawn poison

    def _try_spawn_powerup(self): # Chance-based logic for power-up spawning
        if self.powerup is None and random.random() < 0.2: # Check if empty and roll 20% chance
            kind = random.choice(["speed", "slow", "shield"]) # Pick a random effect
            pos = random_free_cell(self._all_occupied()) # Find free spot
            if pos: # If found
                self.powerup = PowerUp(pos, kind) # Spawn power-up

    def _place_obstacles(self): # Generate level-specific wall blocks
        """Place obstacle blocks for the current level (Level 3+).""" # Docstring
        if self.level < OBSTACLE_LEVEL_START: # Walls don't appear in early levels
            return # Exit function
        count = OBSTACLES_PER_LEVEL * (self.level - OBSTACLE_LEVEL_START + 1) # Scaling obstacle count
        attempts = 0 # Prevent infinite loops
        while len(self.obstacles) < count and attempts < 500: # Try to place up to the count
            attempts += 1 # Increment attempt counter
            c = random.randint(0, GRID_COLS - 1) # Random column
            r = random.randint(0, GRID_ROWS - 1) # Random row
            if (c, r) in self.snake.occupies(): # Don't place on snake body
                continue # Skip attempt
            # Don't trap snake: ensure head neighbours remain open
            hx, hy = self.snake.head # Get head pos
            if abs(c - hx) <= 2 and abs(r - hy) <= 2: # Keep 2-cell buffer around head
                continue # Skip attempt
            self.obstacles.add((c, r)) # Successfully add obstacle

    # ── Collision helpers ──────────────────────────────────

    def _out_of_bounds(self, pos: tuple[int, int]) -> bool: # Check if a point is outside play area
        c, r = pos # Unpack coordinates
        return not (0 <= c < GRID_COLS and 0 <= r < GRID_ROWS) # Return True if outside limits

    # ── Main update ────────────────────────────────────────

    def update(self) -> tuple[str, list[str]]: # Process game frame logic
        """
        Call every frame. Returns:
          (status, sounds)
          status: 'alive' | 'dead'
          sounds: list of sound event names to play this frame
        """ # Docstring describing return interface
        now = pygame.time.get_ticks() # Get current time in ms
        sounds: list[str] = [] # List to collect sounds to play

        # ─ Effect expiry ─
        if self.active_effect and self.active_effect != "shield": # Check if timed buff is active
            if now - self.effect_start > POWERUP_EFFECT_MS: # Check if duration elapsed
                self.active_effect = None # Remove the effect

        # ─ Power-up field expiry ─
        if self.powerup and self.powerup.is_expired(): # Check if item on ground expired
            self.powerup = None # Remove from field

        # ─ Food expiry ─
        self.foods = [f for f in self.foods if not f.is_expired()] # Keep only non-expired food

        # ─ Move timer ─
        if now - self._last_move_ms < self._move_interval_ms(): # Throttle movement by speed
            return "alive", sounds # Not time to move yet
        self._last_move_ms = now # Update move timestamp

        # ─ Move snake ─
        new_head = self.snake.move() # Advance snake and get new head position

        # ─ Wall / border collision ─
        if self._out_of_bounds(new_head): # Check if snake hit the map edge
            if self.active_effect == "shield" and not self.shield_triggered: # If shield active
                self.shield_triggered = True # Mark shield as used
                self.active_effect = None # Lose shield buff
                c, r = new_head # Get current head
                c = c % GRID_COLS # Wrap X coordinate to other side
                r = r % GRID_ROWS # Wrap Y coordinate to other side
                self.snake.body[0] = (c, r) # Teleport head
                new_head = (c, r) # Update head reference
            else: # No protection
                sounds.append("die") # Add death sound
                return "dead", sounds # Player lost

        # ─ Obstacle collision ─
        if new_head in self.obstacles: # Check if snake hit a wall block
            if self.active_effect == "shield" and not self.shield_triggered: # If shield active
                self.shield_triggered = True # Use shield
                self.active_effect = None # Remove shield
                self.snake.body.pop(0) # Undo head movement
                self.snake.body.insert(0, self.snake.body[0]) # Keep snake in place
            else: # No protection
                sounds.append("die") # Add death sound
                return "dead", sounds # Player lost

        # ─ Self collision ─
        if new_head in set(self.snake.body[1:]): # Check if snake hit its own tail
            if self.active_effect == "shield" and not self.shield_triggered: # If shield active
                self.shield_triggered = True # Mark shield as used
                self.active_effect = None # Remove shield
            else: # No protection
                sounds.append("die") # Add death sound
                return "dead", sounds # Player lost

        # ─ Food collision ─
        for food in self.foods[:]: # Iterate over a copy of food list
            if new_head == food.pos: # If head is on food cell
                self.score += food.points * self.level # Increase score adjusted by level
                self.snake.grow(1) # Lengthen snake
                self.food_eaten_this_level += 1 # Increment level progress
                self.foods.remove(food) # Remove eaten food
                self._spawn_food() # Replace food
                self._try_spawn_poison() # Chance to spawn poison
                self._try_spawn_powerup() # Chance to spawn power-up
                leveled = self._check_level_up() # Check for level transition
                # Pick sound by food type
                if food.points >= 5: # Rare food
                    sounds.append("rare") # Queue rare sound
                elif food.points >= 3: # Bonus food
                    sounds.append("bonus") # Queue bonus sound
                else: # Regular food
                    sounds.append("eat") # Queue eat sound
                if leveled: # If level increased
                    sounds.append("levelup") # Queue level-up sound
                break # Process only one food per frame

        # ─ Poison collision ─
        if self.poison and new_head == self.poison.pos: # If head on poison cell
            self.snake.shorten(2) # Shrink snake by 2 segments
            self.poison = None # Remove poison item
            sounds.append("poison") # Queue poison sound
            if len(self.snake.body) <= 1: # If snake becomes too short
                sounds.append("die") # Queue death sound
                return "dead", sounds # Player lost
            self._try_spawn_poison() # Potentially spawn new poison

        # ─ Power-up collision ─
        if self.powerup and new_head == self.powerup.pos: # If head on power-up cell
            kind = self.powerup.kind # Identify buff type
            self.powerup = None # Remove from field
            self.active_effect = kind # Activate buff
            self.effect_start = now # Set start time
            self.shield_triggered = False # Reset shield use flag
            sounds.append("powerup") # Queue power-up sound

        return "alive", sounds # Snake survived this frame

    def _check_level_up(self) -> bool: # Handle level transition logic
        """Returns True if a level-up occurred.""" # Docstring
        if self.food_eaten_this_level >= FOOD_PER_LEVEL: # If quota reached
            self.level += 1 # Increment level number
            self.food_eaten_this_level = 0 # Reset quota counter
            self._place_obstacles() # Generate new obstacles for the level
            return True # Signal level-up
        return False # Stay on current level

    # ── Draw ───────────────────────────────────────────────

    def draw(self, surface: pygame.Surface, settings: dict): # Render all game objects
        # Background
        play_rect = pygame.Rect(PLAY_AREA_X, PLAY_AREA_Y, PLAY_AREA_WIDTH, PLAY_AREA_HEIGHT) # Define area
        pygame.draw.rect(surface, BG_COLOR, play_rect) # Fill background color

        # Grid overlay
        if settings.get("grid_overlay", True): # Check user setting for grid
            for c in range(GRID_COLS): # Loop columns
                for r in range(GRID_ROWS): # Loop rows
                    pygame.draw.rect(surface, GRID_COLOR, cell_rect(c, r), 1) # Draw subtle outlines

        # Obstacles
        for (c, r) in self.obstacles: # Loop through walls
            rect = cell_rect(c, r) # Get position
            pygame.draw.rect(surface, WALL_COLOR, rect) # Draw solid wall
            pygame.draw.rect(surface, MID_GRAY, rect, 1) # Draw wall border

        # Foods
        for food in self.foods: # Loop through beneficial food
            food.draw(surface) # Trigger food render

        # Poison
        if self.poison: # If poison exists
            self.poison.draw(surface) # Trigger poison render

        # Power-up
        if self.powerup: # If power-up exists
            self.powerup.draw(surface) # Trigger power-up render

        # Snake
        shield_active = (self.active_effect == "shield" and not self.shield_triggered) # Determine aura state
        self.snake.draw(surface, shield_active) # Trigger snake render with optional aura