"""
Configuration constants for Connect 4 game.

Contains all game constants, visual settings, screen dimensions,
game mode constants, and AI configuration.
"""

# ==========================================
#              GAME CONSTANTS AND COLORS
#             ==========================

# In Connect 4, the board has 6 rows and 7 columns.
ROWS = 6
COLS = 7

# Simple integers to represent the content of each cell.
EMPTY = 0      # No piece in this cell
PLAYER1 = 1    # Player 1 piece (red)
PLAYER2 = 2    # Player 2 piece (yellow)

# Visual settings for Pygame. Up to you if you want to tweak these to resize
SQUARESIZE = 100
RADIUS = SQUARESIZE // 2 - 5

# Colors are given in RGB format (red, green, blue)
BOARD_COLOR = (0, 0, 200)        # Blue board background
BG_COLOR = (0, 0, 0)             # Black background
PLAYER1_COLOR = (200, 0, 0)      # Red discs for player 1
PLAYER2_COLOR = (230, 230, 0)    # Yellow discs for player 2
TEXT_COLOR = (255, 255, 255)     # White text
HINT_COLOR = (0, 200, 0)         # Green hint marker

# Screen size
BOARD_WIDTH = COLS * SQUARESIZE
DEBUG_PANEL_WIDTH = 700  # Width for debug panel
WIDTH = BOARD_WIDTH + DEBUG_PANEL_WIDTH
# Extra 2 rows of space for messages and hint marker
HEIGHT = (ROWS + 2) * SQUARESIZE
SIZE = (WIDTH, HEIGHT)

FPS = 60

# Game mode constants
MENU = 0
HUMAN_VS_AI = 1
AI_VS_AI = 2
HUMAN_VS_HUMAN = 3
TIME_ATTACK = 4

# Time Attack Configuration
TIME_BANK_SECONDS = 120  # 2 minutes per player

# Theme system
from .themes import CLASSIC, ALL_THEMES
current_theme = CLASSIC  # Default theme

def set_theme(theme):
    """Set the current theme."""
    global current_theme
    current_theme = theme

def cycle_theme():
    """Cycle to the next theme and return it."""
    global current_theme
    current_index = ALL_THEMES.index(current_theme)
    next_index = (current_index + 1) % len(ALL_THEMES)
    current_theme = ALL_THEMES[next_index]
    return current_theme

# AI Configuration
AI_ITERATIONS_PLAYER1 = 400  # MCTS iterations for AI Player 1
AI_ITERATIONS_PLAYER2 = 400  # MCTS iterations for AI Player 2
AI_MOVE_DELAY = 0.2  # Delay in seconds between AI moves

