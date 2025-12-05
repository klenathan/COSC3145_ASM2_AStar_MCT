"""
Configuration constants for the A* pathfinding game.
"""

# Grid dimensions (increased for better terrain visualization)
ROWS = 50
COLS = 80

# Cell size in pixels
CELL_SIZE = 15

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

# Default start and goal positions (proportional to new grid size)
DEFAULT_START = (10, 10)
DEFAULT_GOAL = (30, 50)

# Terrain type constants
TERRAIN_GRASS = "grass"
TERRAIN_WATER = "water"
TERRAIN_MUD = "mud"
TERRAIN_WALL = "wall"

# Terrain movement costs
COST_GRASS = 1.0
COST_WATER = 3.0
COST_MUD = 5.0
COST_WALL = float('inf')

# Terrain color definitions (RGB)
COLOR_GRASS = (50, 150, 50)      # Green for grass
COLOR_WATER = (50, 100, 200)     # Blue for water
COLOR_MUD = (139, 90, 43)        # Brown for mud
# COLOR_WALL already defined above

# Terrain cost mapping
TERRAIN_COSTS = {
    TERRAIN_GRASS: COST_GRASS,
    TERRAIN_WATER: COST_WATER,
    TERRAIN_MUD: COST_MUD,
    TERRAIN_WALL: COST_WALL,
}

# Terrain generation density (percentage of grid cells for each terrain type)
# These should sum to <= 1.0, remaining cells will be grass
TERRAIN_WATER_DENSITY = 0.15  # 15% water
TERRAIN_MUD_DENSITY = 0.10    # 10% mud
TERRAIN_WALL_DENSITY = 0.30   # 20% walls
# Remaining ~55% will be grass

# Clustering parameters for realistic terrain generation
# Number of seed points to place for each terrain type (more seeds = more clusters)
CLUSTER_WATER_SEEDS = 8   # Number of water cluster seeds
CLUSTER_MUD_SEEDS = 6     # Number of mud cluster seeds
CLUSTER_WALL_SEEDS = 10   # Number of wall cluster seeds
# Maximum cluster growth radius (in cells) - controls how large clusters can grow
CLUSTER_MAX_RADIUS = 5    # Maximum distance from seed to grow cluster
# Probability of growing to a neighboring cell (0.0 to 1.0)
CLUSTER_GROWTH_PROBABILITY = 0.6  # 60% chance to expand to each neighbor

# Legacy: Random wall generation (kept for backward compatibility)
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
