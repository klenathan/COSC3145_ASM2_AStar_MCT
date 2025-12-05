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
)

# Minimalist theme - clean and simple
MINIMALIST = Theme(
    name="Minimalist",
    board_color=(200, 200, 200),   # Light gray board background
    bg_color=(255, 255, 255),      # White background
    player1_color=(0, 0, 0),       # Black discs for player 1
    player2_color=(100, 100, 100), # Dark gray discs for player 2
    text_color=(0, 0, 0),          # Black text
    hint_color=(150, 150, 150),   # Gray hint marker
    accent_color=(50, 50, 50),     # Dark gray accent
)

# List of all available themes
ALL_THEMES = [CLASSIC, NEON, MINIMALIST]


