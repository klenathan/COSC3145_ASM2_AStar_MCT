"""
Rendering functions for drawing the game grid and UI elements.
"""

import pygame
from astar_game.config import (
    CELL_SIZE,
    WINDOW_WIDTH,
    WINDOW_HEIGHT,
    COLOR_BG,
    COLOR_GRID,
    COLOR_WALL,
    COLOR_START,
    COLOR_GOAL,
    COLOR_PATH,
    COLOR_CLOSED,
)


def draw_grid(surface, walls, start, goal, current_path, current_closed):
    """
    Draw the grid cells: background, walls, start, goal, closed set, and path.
    The draw order matters so that path and special cells are visible.
    
    Args:
        surface: pygame.Surface to draw on
        walls: Set of (row, col) tuples representing wall cells
        start: Tuple of (row, col) representing the start cell
        goal: Tuple of (row, col) representing the goal cell
        current_path: List of (row, col) tuples representing the current path, or None
        current_closed: Set of (row, col) tuples representing visited cells
    """
    from astar_game.config import ROWS, COLS
    
    # First draw base cells (background and walls)
    for r in range(ROWS):
        for c in range(COLS):
            x = c * CELL_SIZE
            y = r * CELL_SIZE
            rect = pygame.Rect(x, y, CELL_SIZE, CELL_SIZE)

            # Start from plain background color
            color = COLOR_BG

            # Walls override background
            if (r, c) in walls:
                color = COLOR_WALL

            # Fill the cell with the chosen color
            pygame.draw.rect(surface, color, rect)

    # Then show visited cells from the last A* run
    for r, c in current_closed:
        x = c * CELL_SIZE
        y = r * CELL_SIZE
        rect = pygame.Rect(x, y, CELL_SIZE, CELL_SIZE)
        # Color for visited cells
        pygame.draw.rect(surface, COLOR_CLOSED, rect)

    # Then draw the path if it exists
    if current_path is not None:
        for r, c in current_path:
            x = c * CELL_SIZE
            y = r * CELL_SIZE
            rect = pygame.Rect(x, y, CELL_SIZE, CELL_SIZE)
            pygame.draw.rect(surface, COLOR_PATH, rect)

    # Finally draw start and goal on top so they are visible
    sr, sc = start
    gr, gc = goal
    start_rect = pygame.Rect(sc * CELL_SIZE, sr * CELL_SIZE, CELL_SIZE, CELL_SIZE)
    goal_rect = pygame.Rect(gc * CELL_SIZE, gr * CELL_SIZE, CELL_SIZE, CELL_SIZE)
    pygame.draw.rect(surface, COLOR_START, start_rect)
    pygame.draw.rect(surface, COLOR_GOAL, goal_rect)

    # Draw grid lines last so they frame everything
    for c in range(COLS + 1):
        x = c * CELL_SIZE
        pygame.draw.line(surface, COLOR_GRID, (x, 0), (x, WINDOW_HEIGHT))
    for r in range(ROWS + 1):
        y = r * CELL_SIZE
        pygame.draw.line(surface, COLOR_GRID, (0, y), (WINDOW_WIDTH, y))


def draw_help_text(surface, font):
    """
    Draw the help text at the bottom of the screen.
    
    Args:
        surface: pygame.Surface to draw on
        font: pygame.font.Font object for rendering text
    """
    from astar_game.config import COLOR_TEXT, WINDOW_HEIGHT
    
    help_text = "LMB: wall  RMB: frog target  MMB: goal  SPACE: run A*  ESC: quit"
    text_surface = font.render(help_text, True, COLOR_TEXT)
    surface.blit(text_surface, (10, WINDOW_HEIGHT - 24))

