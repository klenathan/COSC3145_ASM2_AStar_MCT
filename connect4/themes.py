"""
Theme system for Connect 4 game.

This module defines visual themes with different color schemes.
"""

from dataclasses import dataclass


@dataclass
class Theme:
    """Represents a visual theme with color scheme."""
    name: str
    board_color: tuple  # RGB color for board background
    bg_color: tuple  # RGB color for screen background
    player1_color: tuple  # RGB color for player 1 pieces
    player2_color: tuple  # RGB color for player 2 pieces
    text_color: tuple  # RGB color for text
    hint_color: tuple  # RGB color for hint marker
    accent_color: tuple  # RGB color for accents/debug panel
    bg_gradient_top: tuple = None  # Optional gradient top color
    bg_gradient_bottom: tuple = None  # Optional gradient bottom color
    button_color: tuple = None  # Optional custom button color
    button_hover_color: tuple = None  # Optional button hover color


# Classic theme - original blue/red/yellow scheme
CLASSIC = Theme(
    name="Classic",
    board_color=(0, 0, 200),        # Blue board background
    bg_color=(0, 0, 0),             # Black background
    player1_color=(200, 0, 0),      # Red discs for player 1
    player2_color=(230, 230, 0),    # Yellow discs for player 2
    text_color=(255, 255, 255),     # White text
    hint_color=(0, 200, 0),         # Green hint marker
    accent_color=(255, 255, 0),     # Yellow accent
    button_color=(40, 40, 120),
    button_hover_color=(60, 60, 180),
)

# Neon theme - cyberpunk style with bright colors
NEON = Theme(
    name="Neon",
    board_color=(0, 255, 255),      # Cyan board background
    bg_color=(10, 10, 30),          # Dark blue background
    player1_color=(255, 0, 255),    # Magenta discs for player 1
    player2_color=(0, 255, 0),     # Lime green discs for player 2
    text_color=(255, 255, 255),     # White text
    hint_color=(255, 255, 0),       # Yellow hint marker
    accent_color=(0, 255, 255),     # Cyan accent
    bg_gradient_top=(20, 0, 40),
    bg_gradient_bottom=(0, 20, 40),
    button_color=(80, 0, 120),
    button_hover_color=(120, 0, 180),
)

# Minimalist theme - elegant and refined with warm neutrals
MINIMALIST = Theme(
    name="Minimalist",
    board_color=(215, 204, 190),    # Warm taupe board
    bg_color=(245, 241, 235),       # Soft warm off-white background
    player1_color=(187, 107, 93),   # Muted terracotta for player 1
    player2_color=(122, 145, 123),  # Soft sage green for player 2
    text_color=(65, 60, 55),        # Warm charcoal text
    hint_color=(180, 160, 140),     # Warm beige hint marker
    accent_color=(97, 78, 68),      # Deep mocha accent
    button_color=(200, 190, 180),
    button_hover_color=(180, 170, 160),
)

# Modern theme - vibrant gradients and contemporary colors
MODERN = Theme(
    name="Modern",
    board_color=(70, 130, 180),     # Steel blue board
    bg_color=(25, 25, 35),          # Dark slate background
    player1_color=(255, 99, 71),    # Tomato red for player 1
    player2_color=(64, 224, 208),   # Turquoise for player 2
    text_color=(255, 255, 255),     # White text
    hint_color=(255, 215, 0),       # Gold hint marker
    accent_color=(138, 43, 226),    # Blue violet accent
    bg_gradient_top=(45, 20, 60),
    bg_gradient_bottom=(20, 40, 60),
    button_color=(100, 60, 140),
    button_hover_color=(130, 80, 180),
)

# Dark Mode theme - sleek dark aesthetics
DARK_MODE = Theme(
    name="Dark Mode",
    board_color=(50, 50, 60),       # Dark gray board
    bg_color=(18, 18, 20),          # Almost black background
    player1_color=(220, 80, 100),   # Coral pink for player 1
    player2_color=(100, 200, 255),  # Sky blue for player 2
    text_color=(240, 240, 245),     # Off-white text
    hint_color=(150, 255, 150),     # Light green hint
    accent_color=(255, 180, 50),    # Orange accent
    bg_gradient_top=(25, 25, 30),
    bg_gradient_bottom=(15, 15, 18),
    button_color=(60, 60, 70),
    button_hover_color=(80, 80, 95),
)

# List of all available themes
ALL_THEMES = [CLASSIC, NEON, MINIMALIST, MODERN, DARK_MODE]


