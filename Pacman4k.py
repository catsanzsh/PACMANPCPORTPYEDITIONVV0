import pygame
import random
import math

# --- Constants ---
# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
PINK = (255, 182, 193)
CYAN = (0, 255, 255)
ORANGE = (255, 165, 0)
GREY = (128, 128, 128) # For ghost house door

# Screen dimensions
CELL_SIZE = 20
GRID_WIDTH = 30
GRID_HEIGHT = 30
SCREEN_WIDTH = GRID_WIDTH * CELL_SIZE  # 600
SCREEN_HEIGHT = GRID_HEIGHT * CELL_SIZE + 70 # 600 for game + 70 for UI

# Entity properties
PACMAN_RADIUS = CELL_SIZE // 2 - 2
PACMAN_SPEED = 2.5 # Cells per second
GHOST_RADIUS = CELL_SIZE // 2 - 2
GHOST_SPEED = 2.0 # Cells per second
GHOST_FRIGHTENED_SPEED = 1.5
GHOST_EATEN_SPEED = 4.0
PELLET_RADIUS = 3
POWER_PELLET_RADIUS = 6

# Directions
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)
STOP = (0,0)

# Ghost modes
SCATTER = 0
CHASE = 1
FRIGHTENED = 2
EATEN = 3

# Ghost Types (for easier indexing and color mapping)
BLINKY = 0 # Red
PINKY = 1  # Pink
INKY = 2   # Cyan
CLYDE = 3  # Orange

GHOST_COLORS = {
    BLINKY: RED,
    PINKY: PINK,
    INKY: CYAN,
    CLYDE: ORANGE
}

# Maze layout (Completed and adjusted)
# 1: Wall, 2: Pellet, 3: Power Pellet, 0: Empty path/Tunnel, 4: Ghost House (wall for Pacman), 5: Pacman Start
# Pacman start (5) is now at a more traditional location.
# Ghost house (4) is a zone ghosts can enter/exit.
DEFAULT_MAZE = [
    [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
    [1,2,2,2,2,2,2,2,2,2,2,2,2,1,1,2,2,2,2,2,2,2,2,2,2,2,2,2,3,1],
    [1,2,1,1,1,2,1,1,1,2,1,1,2,1,1,2,1,1,2,1,1,1,2,1,1,1,1,1,2,1],
    [1,3,1,1,1,2,1,1,1,2,1,1,2,1,1,2,1,1,2,1,1,1,2,1,1,1,1,1,3,1],
    [1,2,1,1,1,2,1,1,1,2,1,1,2,1,1,2,1,1,2,1,1,1,2,1,1,1,1,1,2,1],
    [1,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,1],
    [1,2,1,1,1,2,1,1,2,1,1,1,1,1,1,1,1,1,2,1,1,2,1,1,1,1,1,1,2,1],
    [1,2,1,1,1,2,1,1,2,1,1,1,1,1,1,1,1,1,2,1,1,2,1,1,1,1,1,1,2,1],
    [1,2,2,2,2,2,2,2,2,1,1,2,2,1,1,2,2,1,1,2,2,2,2,2,2,2,2,2,2,1],
    [1,1,1,1,1,2,1,1,1,1,1,2,1,1,1,1,2,1,1,1,1,1,2,1,1,1,1,1,1,1],
    [1,1,1,1,1,2,1,1,1,1,1,2,1,1,1,1,2,1,1,1,1,1,2,1,1,1,1,1,1,1], # Row 10
    [1,1,1,1,1,2,1,1,2,2,2,2,2,2,2,2,2,2,2,2,1,1,2,1,1,1,1,1,1,1],
    [1,1,1,1,1,2,1,1,2,1,1,1,4,4,4,4,1,1,2,1,1,2,1,1,1,1,1,1,1,1], # Ghost house top boundary (4 is wall to pacman)
    [1,0,0,0,0,2,2,2,2,1,4,0,0,0,0,0,0,4,1,2,2,2,2,0,0,0,0,0,0,1], # Tunnel row, ghost house main area (0 is path, 4 is ghost only)
    [1,1,1,1,1,2,1,1,2,1,4,0,0,0,0,0,0,4,1,2,1,1,2,1,1,1,1,1,1,1], # Ghost house bottom boundary
    [1,1,1,1,1,2,1,1,2,2,2,2,2,2,2,2,2,2,2,2,1,1,2,1,1,1,1,1,1,1], # Row 15 (mirror of 11)
    [1,1,1,1,1,2,1,1,1,1,1,2,1,1,1,1,2,1,1,1,1,1,2,1,1,1,1,1,1,1], # (mirror of 10)
    [1,1,1,1,1,2,1,1,1,1,1,2,1,1,1,1,2,1,1,1,1,1,2,1,1,1,1,1,1,1], # (mirror of 9)
    [1,2,2,2,2,2,2,2,2,1,1,2,2,1,1,2,2,1,1,2,2,2,2,2,2,2,2,2,2,1], # (mirror of 8)
    [1,2,1,1,1,2,1,1,2,1,1,1,1,1,1,1,1,1,2,1,1,2,1,1,1,1,1,1,2,1], # (mirror of 7)
    [1,2,1,1,1,2,1,1,2,1,1,1,1,1,1,1,1,1,2,1,1,2,1,1,1,1,1,1,2,1], # Row 20 (mirror of 6)
    [1,2,2,2,2,2,2,2,2,2,2,2,2,5,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,1], # Pacman Start (5), (mirror of 5 with P)
    [1,2,1,1,1,2,1,1,1,2,1,1,2,1,1,2,1,1,2,1,1,1,2,1,1,1,1,1,2,1], # (mirror of 4)
    [1,3,1,1,1,2,1,1,1,2,1,1,2,1,1,2,1,1,2,1,1,1,2,1,1,1,1,1,3,1], # (mirror of 3)
    [1,2,1,1,1,2,1,1,1,2,1,1,2,1,1,2,1,1,2,1,1,1,2,1,1,1,1,1,2,1], # (mirror of 2)
    [1,2,2,2,2,2,2,2,2,2,2,2,2,1,1,2,2,2,2,2,2,2,2,2,2,2,2,2,3,1], # Row 25 (mirror of 1)
    [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1]  # Bottom border (not mirrored, just solid)
]
# Actual GRID_HEIGHT for maze array
MAZE_ARRAY_HEIGHT = len(DEFAULT_MAZE)
MAZE_ARRAY_WIDTH = len(DEFAULT_MAZE[0])


# --- Helper Functions ---
def to_pixel(grid_pos):
    return (grid_pos[0] * CELL_SIZE + CELL_SIZE // 2, grid_pos[1] * CELL_SIZE + CELL_SIZE // 2)

def to_grid(pixel_pos):
    return (int(pixel_pos[0] / CELL_SIZE), int(pixel_pos[1] / CELL_SIZE))

# --- Entity Classes ---
class Entity:
    def __init__(self, game, grid_pos, color, radius, speed):
        self.game = game
        self.grid_pos = list(grid_pos) # Current grid cell (col, row)
        self.pixel_pos = list(to_pixel(grid_pos)) # Center pixel position
        self.color = color
        self.radius = radius
        self.speed_val = speed # Grid cells per second
        self.direction = STOP
        self.next_direction = STOP # For Pacman queued movement

    def get_rect(self):
        return pygame.Rect(self.pixel_pos[0] - self.radius, self.pixel_pos[1] - self.radius,
                           self.radius * 2, self.radius * 2)

    def is_wall(self, grid_pos, for_ghost=False):
        col, row = int(grid_pos[0]), int(grid_pos[1])
        if not (0 <= col < MAZE_ARRAY_WIDTH and 0 <= row < MAZE_ARRAY_HEIGHT):
            return True # Outside bounds is wall

        cell_type = self.game.maze[row][col]
        if cell_type == 1: return True # Standard wall
        if not for_ghost and cell_type == 4: return True # Ghost house wall for Pacman
        return False

    def move(self, dt):
        # Movement is target-based: try to reach center of target_grid_pos
        target_pixel_pos = to_pixel(self.grid_pos)
        distance_to_target = math.hypot(target_pixel_pos[0] - self.pixel_pos[0], target_pixel_pos[1] - self.pixel_pos[1])
        
        # Move pixel-wise towards target grid cell center
        move_dist = self.current_speed() * CELL_SIZE * dt
        
        if distance_to_target == 0: # Reached center of current grid cell
            # Try to apply next_direction if Pacman or continue current for Ghost
            potential_next_grid_pos = (self.grid_pos[0] + self.direction[0], self.grid_pos[1] + self.direction[1])
            
            if hasattr(self, 'next_direction') and self.next_direction != STOP:
                # Pacman specific: check if queued direction is valid
                next_tile_for_queued_dir = (self.grid_pos[0] + self.next_direction[0], self.grid_pos[1] + self.next_direction[1])
                if not self.is_wall(next_tile_for_queued_dir, isinstance(self, Ghost)):
                    self.direction = self.next_direction
                    self.next_direction = STOP # Clear queued direction
                    potential_next_grid_pos = next_tile_for_queued_dir
                # If queued is not valid, try current direction
                elif self.is_wall(potential_next_grid_pos, isinstance(self, Ghost)):
                     self.direction = STOP # Can't move in current or queued direction

            elif self.is_wall(potential_next_grid_pos, isinstance(self, Ghost)):
                 self.direction = STOP # Can't move in current direction

            # Update grid_pos if successfully moved to a new cell
            if self.direction != STOP and not self.is_wall(potential_next_grid_pos, isinstance(self, Ghost)):
                 self.grid_pos[0] += self.direction[0]
                 self.grid_pos[1] += self.direction[1]
                 self.handle_tunnels() # Check for tunnels after grid pos update
        
        # Actual pixel movement
        if self.direction != STOP:
            self.pixel_pos[0] += self.direction[0] * move_dist
            self.pixel_pos[1] += self.direction[1] * move_dist

        # Snap to grid cell center if overshot or very close
        new_target_pixel_pos = to_pixel(self.grid_pos)
        new_dist_to_target = math.hypot(new_target_pixel_pos[0] - self.pixel_pos[0], new_target_pixel_pos[1] - self.pixel_pos[1])

        # If moving away from target due to overshoot, or very close, snap.
        if (self.direction[0] * (new_target_pixel_pos[0] - self.pixel_pos[0]) < 0 or \
            self.direction[1] * (new_target_pixel_pos[1] - self.pixel_pos[1]) < 0) or \
            new_dist_to_target < move_dist / 2 : # Heuristic for snapping
            self.pixel_pos = list(new_target_pixel_pos)


    def handle_tunnels(self):
        # Specific to the maze layout where tunnels are on row 13 (0-indexed)
        if self.grid_pos[1] == 13: # Middle row with tunnels
            if self.grid_pos[0] < 0 and self.direction == LEFT:
                self.grid_pos[0] = MAZE_ARRAY_WIDTH -1
                self.pixel_pos[0] = to_pixel(self.grid_pos)[0]
            elif self.grid_pos[0] >= MAZE_ARRAY_WIDTH and self.direction == RIGHT:
                self.grid_pos[0] = 0
                self.pixel_pos[0] = to_pixel(self.grid_pos)[0]
                
    def current_speed(self): # To be overridden by Ghost for different states
        return self.speed_val

class Pacman(Entity):
    def __init__(self, game, grid_pos):
        super().__init__(game, grid_pos, YELLOW, PACMAN_RADIUS, PACMAN_SPEED)
        self.lives = 3
        self.score = 0
        self.mouth_angle = 0 # For animation
        self.mouth_open = True
        self.mouth_timer = 0
        self.start_pos = list(grid_pos) # Store initial position for reset

    def handle_input(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT: self.next_direction = LEFT
            elif event.key == pygame.K_RIGHT: self.next_direction = RIGHT
            elif event.key == pygame.K_UP: self.next_direction = UP
            elif event.key == pygame.K_DOWN: self.next_direction = DOWN

    def update(self, dt):
        self.move(dt)
        # Mouth animation
        self.mouth_timer += dt
        if self.mouth_timer > 0.1: # Toggle every 0.1s
            self.mouth_open = not self.mouth_open
            self.mouth_timer = 0
        self.mouth_angle = 30 if self.mouth_open and self.direction != STOP else 0
        
        self.check_pellet_collision()

    def check_pellet_collision(self):
        # Check collision with pellets at current grid_pos
        center_grid_x, center_grid_y = self.grid_pos[0], self.grid_pos[1]
        
        # Check for pellet
        for i, pellet_pos in enumerate(self.game.pellets):
            if pellet_pos == (center_grid_x, center_grid_y):
                self.game.pellets.pop(i)
                self.score += 10
                self.game.eaten_pellets_count +=1
                # Add sound effect here if desired
                break 
        
        # Check for power pellet
        for i, pp_pos in enumerate(self.game.power_pellets):
            if pp_pos == (center_grid_x, center_grid_y):
                self.game.power_pellets.pop(i)
                self.score += 50
                self.game.eaten_pellets_count +=1
                self.game.start_fright_mode()
                # Add sound effect here
                break

    def draw(self, screen):
        if self.lives < 0: return # Don't draw if game over animation done

        # Calculate rotation for Pac-Man sprite based on direction
        angle_rad = 0
        if self.direction == RIGHT: angle_rad = 0
        elif self.direction == LEFT: angle_rad = math.pi
        elif self.direction == UP: angle_rad = math.pi / 2
        elif self.direction == DOWN: angle_rad = -math.pi / 2
        
        # Draw Pac-Man body (circle)
        pygame.draw.circle(screen, self.color, (int(self.pixel_pos[0]), int(self.pixel_pos[1])), self.radius)

        # Draw mouth if moving
        if self.direction != STOP and self.mouth_angle > 0:
            # Points for the mouth wedge
            p1 = self.pixel_pos
            p2_offset_x = self.radius * math.cos(angle_rad + math.radians(self.mouth_angle))
            p2_offset_y = self.radius * math.sin(angle_rad + math.radians(self.mouth_angle))
            p2 = (self.pixel_pos[0] + p2_offset_x, self.pixel_pos[1] + p2_offset_y)

            p3_offset_x = self.radius * math.cos(angle_rad - math.radians(self.mouth_angle))
            p3_offset_y = self.radius * math.sin(angle_rad - math.radians(self.mouth_angle))
            p3 = (self.pixel_pos[0] + p3_offset_x, self.pixel_pos[1] + p3_offset_y)
            
            pygame.draw.polygon(screen, BLACK, [p1, p2, p3])
            
    def reset(self):
        self.grid_pos = list(self.start_pos)
        self.pixel_pos = list(to_pixel(self.start_pos))
        self.direction = STOP
        self.next_direction = STOP


class Ghost(Entity):
    def __init__(self, game, grid_pos, ghost_type):
        super().__init__(game, grid_pos, GHOST_COLORS[ghost_type], GHOST_RADIUS, GHOST_SPEED)
        self.type = ghost_type
        self.state = SCATTER # Initial state
        self.target_pos = None # Target grid cell for AI
        self.scatter_target = self.get_scatter_target()
        self.start_pos = list(grid_pos) # For returning to house
        self.is_in_house = True # Ghosts may start in house
        self.exit_house_pos = (14, 11) # Grid position outside ghost house door

    def get_scatter_target(self):
        if self.type == BLINKY: return (MAZE_ARRAY_WIDTH - 2, 1) # Top-right
        if self.type == PINKY: return (1, 1) # Top-left
        if self.type == INKY: return (MAZE_ARRAY_WIDTH - 2, MAZE_ARRAY_HEIGHT - 2) # Bottom-right
        if self.type == CLYDE: return (1, MAZE_ARRAY_HEIGHT - 2) # Bottom-left
        return (self.grid_pos[0], self.grid_pos[1]) # Default

    def current_speed(self):
        if self.state == FRIGHTENED: return GHOST_FRIGHTENED_SPEED
        if self.state == EATEN: return GHOST_EATEN_SPEED
        return self.speed_val

    def update(self, dt, pacman):
        if self.is_in_house:
            # Simple logic: move towards exit, then leave. Could be pellet-count based for staggered release.
            if self.grid_pos == self.exit_house_pos:
                self.is_in_house = False
            else: # Move towards exit_house_pos (simplified)
                self.target_pos = self.exit_house_pos
        else:
            self.update_target(pacman)

        self.make_move_decision()
        self.move(dt) # Entity.move()

    def update_target(self, pacman):
        if self.state == EATEN:
            self.target_pos = self.exit_house_pos # Target house entrance
            if self.grid_pos == self.exit_house_pos: # Reached entrance
                self.is_in_house = True # Go back in house
                self.state = CHASE # Or scatter, depending on global mode
                self.grid_pos = list(self.start_pos) # Reset to spawn inside house
                self.pixel_pos = list(to_pixel(self.grid_pos))
        elif self.state == FRIGHTENED:
            # Move randomly (implemented in make_move_decision)
            self.target_pos = None 
        elif self.state == SCATTER:
            self.target_pos = self.scatter_target
        elif self.state == CHASE:
            # Basic Chase AI
            if self.type == BLINKY: # Targets Pac-Man directly
                self.target_pos = pacman.grid_pos
            elif self.type == PINKY: # Targets 4 tiles ahead of Pac-Man
                px, py = pacman.grid_pos
                dx, dy = pacman.direction
                self.target_pos = (px + dx * 4, py + dy * 4)
            elif self.type == INKY: # More complex, uses Blinky. Simplified: target Pacman for now
                self.target_pos = pacman.grid_pos 
            elif self.type == CLYDE: # If far, target Pacman. If close, scatter.
                dist_to_pacman = math.hypot(self.grid_pos[0] - pacman.grid_pos[0], self.grid_pos[1] - pacman.grid_pos[1])
                if dist_to_pacman > 8:
                    self.target_pos = pacman.grid_pos
                else:
                    self.target_pos = self.scatter_target
    
    def make_move_decision(self):
        # Only make decision if at center of a cell
        current_pixel_center = to_pixel(self.grid_pos)
        if abs(self.pixel_pos[0] - current_pixel_center[0]) > 1 or \
           abs(self.pixel_pos[1] - current_pixel_center[1]) > 1:
            return # Not at center yet, continue current direction

        possible_directions = []
        for d in [UP, DOWN, LEFT, RIGHT]:
            # Ghosts cannot reverse direction unless forced (e.g. dead end or mode change)
            if (d[0] == -self.direction[0] and d[1] == -self.direction[1]) and self.direction != STOP:
                continue
            
            next_pos = (self.grid_pos[0] + d[0], self.grid_pos[1] + d[1])
            if not self.is_wall(next_pos, for_ghost=True):
                possible_directions.append(d)
        
        if not possible_directions: # Should not happen in a valid maze if not reversing
            self.direction = (-self.direction[0], -self.direction[1]) # Reverse if stuck
            return

        if self.state == FRIGHTENED:
            # Move randomly
            if possible_directions:
                self.direction = random.choice(possible_directions)
        else:
            # Choose direction that minimizes distance to target
            best_direction = self.direction # Default to current if no better option or only one way
            min_dist = float('inf')

            if len(possible_directions) == 1:
                 best_direction = possible_directions[0]
            elif self.target_pos:
                for d in possible_directions:
                    next_node = (self.grid_pos[0] + d[0], self.grid_pos[1] + d[1])
                    dist = math.hypot(next_node[0] - self.target_pos[0], next_node[1] - self.target_pos[1])
                    if dist < min_dist:
                        min_dist = dist
                        best_direction = d
            self.direction = best_direction


    def draw(self, screen):
        body_color = self.color
        eye_color = WHITE
        pupil_color = BLACK

        if self.state == FRIGHTENED:
            body_color = BLUE
            # Flash white near end of frightened mode
            if self.game.fright_timer < 2000 and int(self.game.fright_timer / 250) % 2 == 0: # Flash every 0.25s in last 2s
                body_color = WHITE
        elif self.state == EATEN:
            body_color = None # Only eyes
            eye_color = WHITE
            pupil_color = BLUE # Or some indication of eaten state for pupils

        # Draw body (simplified: circle)
        if body_color:
            pygame.draw.circle(screen, body_color, (int(self.pixel_pos[0]), int(self.pixel_pos[1])), self.radius)
        
        # Draw eyes (simplified: two small circles)
        eye_offset_x = self.radius * 0.3
        eye_offset_y = -self.radius * 0.2
        eye_radius = self.radius * 0.25
        pupil_radius = eye_radius * 0.5

        # Adjust eye direction based on ghost's movement direction
        pupil_shift_x = 0
        pupil_shift_y = 0
        if self.direction == LEFT: pupil_shift_x = -pupil_radius
        if self.direction == RIGHT: pupil_shift_x = pupil_radius
        if self.direction == UP: pupil_shift_y = -pupil_radius
        if self.direction == DOWN: pupil_shift_y = pupil_radius
        
        # Left eye
        left_eye_pos = (int(self.pixel_pos[0] - eye_offset_x), int(self.pixel_pos[1] + eye_offset_y))
        pygame.draw.circle(screen, eye_color, left_eye_pos, eye_radius)
        pygame.draw.circle(screen, pupil_color, (int(left_eye_pos[0] + pupil_shift_x), int(left_eye_pos[1] + pupil_shift_y)), pupil_radius)
        
        # Right eye
        right_eye_pos = (int(self.pixel_pos[0] + eye_offset_x), int(self.pixel_pos[1] + eye_offset_y))
        pygame.draw.circle(screen, eye_color, right_eye_pos, eye_radius)
        pygame.draw.circle(screen, pupil_color, (int(right_eye_pos[0] + pupil_shift_x), int(right_eye_pos[1] + pupil_shift_y)), pupil_radius)

    def reverse_direction(self):
        if self.direction != STOP:
            self.direction = (-self.direction[0], -self.direction[1])
            # Try to immediately apply this new direction to prevent getting stuck if previous move was into a wall logic
            next_grid_pos = (self.grid_pos[0] + self.direction[0], self.grid_pos[1] + self.direction[1])
            if not self.is_wall(next_grid_pos, isinstance(self, Ghost)):
                 self.grid_pos[0] += self.direction[0]
                 self.grid_pos[1] += self.direction[1]
                 self.pixel_pos = list(to_pixel(self.grid_pos)) # Snap to new grid pos center
            else: # If reversed into a wall, this needs better handling, or means ghost was cornered.
                  # For simplicity, we'll allow it and assume next make_move_decision fixes it.
                  pass


    def reset(self):
        self.grid_pos = list(self.start_pos)
        self.pixel_pos = list(to_pixel(self.start_pos))
        self.state = SCATTER # Or based on initial game state setup
        self.direction = STOP # Or an initial exit direction
        self.is_in_house = True
        self.target_pos = self.exit_house_pos


# --- Game Class ---
class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Pac-Man")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)

        self.maze = DEFAULT_MAZE # Use the array directly
        self.pellets = []
        self.power_pellets = []
        self.pacman_start_pos = None
        self.ghost_start_positions = {} # type: (pos)

        self.total_pellets_in_level = 0
        self.eaten_pellets_count = 0
        
        self.populate_maze_elements()

        self.pacman = Pacman(self, self.pacman_start_pos)
        self.ghosts = self.create_ghosts()
        
        self.game_state = "START" # START, PLAYING, PACMAN_DEATH, GAME_OVER, WIN
        self.fright_timer = 0 # in ms
        self.fright_duration = 7000 # 7 seconds
        
        self.scatter_chase_timer = 0
        self.scatter_chase_pattern = [
            (7000, SCATTER), (20000, CHASE),
            (7000, SCATTER), (20000, CHASE),
            (5000, SCATTER), (20000, CHASE),
            (5000, SCATTER), (-1, CHASE) # Last one is indefinite chase
        ]
        self.current_scatter_chase_index = 0
        self.current_ghost_mode = SCATTER # Initial

        self.death_timer = 0
        self.death_duration = 2000 # 2 seconds for death animation/pause

    def populate_maze_elements(self):
        # Ghost spawn points within the house (approximate)
        # (col, row)
        base_ghost_positions = [(13,13), (14,13), (15,13), (16,13)] 
        
        for r, row_data in enumerate(self.maze):
            for c, cell_type in enumerate(row_data):
                if cell_type == 2: # Pellet
                    self.pellets.append((c, r))
                    self.total_pellets_in_level += 1
                elif cell_type == 3: # Power Pellet
                    self.power_pellets.append((c, r))
                    self.total_pellets_in_level += 1
                elif cell_type == 5: # Pacman Start
                    self.pacman_start_pos = (c, r)
                
        # Assign specific start positions if needed, or use a central one for all.
        # For now, they all start near the center of the ghost house area.
        # More advanced: specific spots, Blinky starts outside or first out.
        self.ghost_start_positions[BLINKY] = base_ghost_positions[0]
        self.ghost_start_positions[PINKY]  = base_ghost_positions[1]
        self.ghost_start_positions[INKY]   = base_ghost_positions[2]
        self.ghost_start_positions[CLYDE]  = base_ghost_positions[3]


    def create_ghosts(self):
        ghost_list = []
        for ghost_type, start_pos_key in enumerate(self.ghost_start_positions):
             # Ensure we map type correctly if dict isn't ordered or keys are specific
             actual_start_pos = self.ghost_start_positions[ghost_type]
             ghost_list.append(Ghost(self, actual_start_pos, ghost_type))
        return ghost_list

    def reset_level(self):
        self.pacman.reset()
        for ghost in self.ghosts:
            ghost.reset()
        
        # Reset timers and ghost modes (but keep score and lives)
        self.fright_timer = 0
        self.scatter_chase_timer = 0
        self.current_scatter_chase_index = 0
        self.current_ghost_mode = self.scatter_chase_pattern[0][1]
        for ghost in self.ghosts:
            ghost.state = self.current_ghost_mode
            ghost.is_in_house = True # Put them back in house
            ghost.target_pos = ghost.exit_house_pos # Aim for exit initially

        self.game_state = "START" # Go to ready state

    def full_game_reset(self):
        self.pacman.lives = 3
        self.pacman.score = 0
        self.pellets = []
        self.power_pellets = []
        self.total_pellets_in_level = 0
        self.eaten_pellets_count = 0
        self.populate_maze_elements() # Repopulate pellets
        self.reset_level()
        self.game_state = "START"


    def run(self):
        running = True
        while running:
            dt_ms = self.clock.tick(60) # Milliseconds since last frame
            dt_s = dt_ms / 1000.0    # Seconds since last frame

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                self.handle_input(event)

            self.update(dt_s, dt_ms)
            self.render()
        
        pygame.quit()

    def handle_input(self, event):
        if self.game_state == "START":
            if event.type == pygame.KEYDOWN:
                self.game_state = "PLAYING"
                self.current_ghost_mode = self.scatter_chase_pattern[0][1] # Set initial ghost mode
                for ghost in self.ghosts:
                    ghost.state = self.current_ghost_mode
                    ghost.is_in_house = True # Ensure they start process of exiting
                    ghost.target_pos = ghost.exit_house_pos
        elif self.game_state == "PLAYING":
            self.pacman.handle_input(event)
        elif self.game_state == "GAME_OVER" or self.game_state == "WIN":
            if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                self.full_game_reset()


    def update(self, dt_s, dt_ms):
        if self.game_state == "PLAYING":
            self.pacman.update(dt_s)
            
            # Update ghost mode (Scatter/Chase)
            self.scatter_chase_timer += dt_ms
            duration, mode = self.scatter_chase_pattern[self.current_scatter_chase_index]
            
            if duration != -1 and self.scatter_chase_timer >= duration: # -1 for indefinite
                self.scatter_chase_timer = 0
                self.current_scatter_chase_index = min(self.current_scatter_chase_index + 1, len(self.scatter_chase_pattern) - 1)
                _, new_mode = self.scatter_chase_pattern[self.current_scatter_chase_index]
                self.current_ghost_mode = new_mode
                # Update ghosts only if not frightened or eaten
                for ghost in self.ghosts:
                    if ghost.state not in [FRIGHTENED, EATEN]:
                        ghost.state = self.current_ghost_mode

            for ghost in self.ghosts:
                ghost.update(dt_s, self.pacman)

            self.check_collisions()
            
            if self.fright_timer > 0:
                self.fright_timer -= dt_ms
                if self.fright_timer <= 0:
                    self.end_fright_mode()
            
            if self.eaten_pellets_count >= self.total_pellets_in_level:
                self.game_state = "WIN"

        elif self.game_state == "PACMAN_DEATH":
            self.death_timer += dt_ms
            if self.death_timer >= self.death_duration:
                self.death_timer = 0
                self.pacman.lives -= 1
                if self.pacman.lives < 0:
                    self.game_state = "GAME_OVER"
                else:
                    self.reset_level() # Reset positions for new life
                    self.game_state = "START" # Go to "Ready?" state


    def check_collisions(self):
        pacman_rect = self.pacman.get_rect()
        for ghost in self.ghosts:
            if pacman_rect.colliderect(ghost.get_rect()):
                if ghost.state == FRIGHTENED:
                    ghost.state = EATEN
                    self.pacman.score += 200 # Score for eating ghost
                    # Sound effect for eating ghost
                elif ghost.state != EATEN: # Pacman caught by active ghost
                    self.game_state = "PACMAN_DEATH"
                    # Death sound, animation start
                    break # Stop further collision checks this frame
    
    def start_fright_mode(self):
        self.fright_timer = self.fright_duration
        for ghost in self.ghosts:
            if ghost.state != EATEN: # Don't affect eaten ghosts
                ghost.state = FRIGHTENED
                ghost.reverse_direction()

    def end_fright_mode(self):
        self.fright_timer = 0
        for ghost in self.ghosts:
            if ghost.state == FRIGHTENED: # Only if still frightened
                 # Revert to current global scatter/chase mode
                ghost.state = self.current_ghost_mode


    def render(self):
        self.screen.fill(BLACK)
        self.draw_maze()
        self.draw_pellets()
        
        self.pacman.draw(self.screen)
        for ghost in self.ghosts:
            ghost.draw(self.screen)
            
        self.draw_ui()

        if self.game_state == "START":
            self.draw_text("READY?", SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50)
        elif self.game_state == "GAME_OVER":
            self.draw_text("GAME OVER", SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50)
            self.draw_text("Press ENTER to Restart", SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2, self.small_font)
        elif self.game_state == "WIN":
            self.draw_text("YOU WIN!", SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50)
            self.draw_text("Press ENTER to Restart", SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2, self.small_font)
        elif self.game_state == "PACMAN_DEATH":
            # Could add a "dying" animation for Pacman here
             self.draw_text("CAUGHT!", SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50, color=RED)


        pygame.display.flip()

    def draw_maze(self):
        for r, row_data in enumerate(self.maze):
            for c, cell_type in enumerate(row_data):
                rect = pygame.Rect(c * CELL_SIZE, r * CELL_SIZE, CELL_SIZE, CELL_SIZE)
                if cell_type == 1: # Wall
                    pygame.draw.rect(self.screen, BLUE, rect)
                elif cell_type == 4: # Ghost house "wall" (visual only, logic in Entity)
                    pygame.draw.rect(self.screen, GREY, rect, 1) # Draw outline for ghost house area

    def draw_pellets(self):
        for c, r in self.pellets:
            pixel_pos = to_pixel((c,r))
            pygame.draw.circle(self.screen, YELLOW, pixel_pos, PELLET_RADIUS)
        for c, r in self.power_pellets:
            pixel_pos = to_pixel((c,r))
            # Pulsating effect for power pellets
            pulse = abs(math.sin(pygame.time.get_ticks() * 0.005)) # Slow pulse
            current_radius = int(POWER_PELLET_RADIUS * (0.8 + 0.2 * pulse))
            pygame.draw.circle(self.screen, ORANGE, pixel_pos, current_radius)

    def draw_ui(self):
        # Score
        score_text = self.font.render(f"SCORE: {self.pacman.score}", True, WHITE)
        self.screen.blit(score_text, (20, GRID_HEIGHT * CELL_SIZE + 15))
        # Lives
        lives_text = self.font.render(f"LIVES: {self.pacman.lives if self.pacman.lives >= 0 else 0}", True, WHITE)
        self.screen.blit(lives_text, (SCREEN_WIDTH - 150, GRID_HEIGHT * CELL_SIZE + 15))

    def draw_text(self, text, x, y, font=None, color=YELLOW, center=True):
        if font is None: font = self.font
        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect()
        if center:
            text_rect.center = (x, y)
        else:
            text_rect.topleft = (x,y)
        self.screen.blit(text_surface, text_rect)

# --- Main Execution ---
if __name__ == '__main__':
    game = Game()
    game.run()
