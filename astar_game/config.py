"""
Configuration constants for the A* pathfinding game.
"""

# Grid dimensions
ROWS = 20
COLS = 30

# Cell size in pixels
CELL_SIZE = 25

# Window dimensions (computed from grid size)
WINDOW_WIDTH = COLS * CELL_SIZE
WINDOW_HEIGHT = ROWS * CELL_SIZE

# Color definitions (RGB)
COLOR_BG = (30, 30, 40)
COLOR_GRID = (60, 60, 70)
COLOR_WALL = (40, 40, 120)
COLOR_START = (0, 200, 0)
COLOR_GOAL = (200, 0, 0)
COLOR_PATH = (0, 255, 0)  # Green path color
COLOR_CLOSED = (120, 0, 120)
COLOR_TEXT = (230, 230, 230)

# Default start and goal positions
DEFAULT_START = (5, 5)
DEFAULT_GOAL = (10, 20)

# Random wall generation
WALL_DENSITY = 0.4  # Percentage of grid cells that become walls (0.0 to 1.0)

# A* pathfinding settings
# If False, only allow movement in 4 cardinal directions
ALLOW_DIAGONAL_NEIGHBORS = False

# FPS for the game loop
FPS = 60

# Font settings
FONT_NAME = "consolas"
FONT_SIZE = 18


#################### Config from ASM 1 ####################

# Colors as RGB tuples. Used by drawing code for the UI and agents.
BG = (28, 33, 38)     # background color
WHITE = (240, 240, 240)  # text and highlights
GREEN = (90, 220, 120)   # frog color
BLUE = (120, 180, 250)  # bubble color
YELLOW = (250, 225, 120)  # fly color when flocking or idle
PURPLE = (185, 120, 250)  # fly color when fleeing
RED = (232, 88, 88)    # health hearts
MUTED = (180, 188, 196)  # hint text
TARGET_COLOR = (250, 170, 90)  # indicator for the movement target

# Frog setup
FROG_RADIUS = 16          # draw size and collision size for the frog
FROG_SPEED = 200.0       # top speed for the frog in pixels per second
HURT_INVULN = 1.0         # seconds of temporary invulnerability after damage
SPEED_CLAMP = 2000.0
# Arrive behavior
# Slow inside slow radius and stop inside stop radius
ARRIVE_SLOW_RADIUS = 125.0
ARRIVE_STOP_RADIUS = 8.0
# lateral steering multiplier inside slow radius to pivot faster
ARRIVE_SNAP_GAIN = 1.5
ARRIVE_BRAKE_BOOST = 2.0    # boost to steering force when slowing down near target

# Path following
PATH_LOOKAHEAD = 50.0        # how far ahead to look along the path when following

# Obstacle avoidance tuning
AVOID_LOOKAHEAD = 120.0   # how far the snake looks ahead when checking a corridor
# degrees to rotate per step when searching for a free path
AVOID_ANGLE_INCREMENT = 12
AVOID_MAX_ANGLE = 84      # maximum deviation to try on either side

# Game rules
START_HEALTH = 10                 # how many hits the frog can take
FLIES_TO_WIN = 3                # win condition counter

DRAW_DEBUG = True
