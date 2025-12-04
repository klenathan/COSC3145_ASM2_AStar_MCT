"""
Rendering functions for drawing the game grid and UI elements.
"""

import pygame
try:
    import pygame.gfxdraw
    HAS_GFXDRAW = True
except ImportError:
    HAS_GFXDRAW = False
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
    COLOR_GRASS,
    COLOR_WATER,
    COLOR_MUD,
    TERRAIN_GRASS,
    TERRAIN_WATER,
    TERRAIN_MUD,
    TERRAIN_WALL,
)


def draw_grid(surface, terrain, start, goal, current_path, current_closed):
    """
    Draw the grid cells: terrain, start, goal, closed set, and path.
    The draw order matters so that path and special cells are visible.
    
    Args:
        surface: pygame.Surface to draw on
        terrain: Dictionary mapping (row, col) -> terrain_type
        start: Tuple of (row, col) representing the start cell
        goal: Tuple of (row, col) representing the goal cell
        current_path: List of (row, col) tuples representing the current path, or None
        current_closed: Set of (row, col) tuples representing visited cells
    """
    from astar_game.config import ROWS, COLS
    
    # First draw terrain base colors
    for r in range(ROWS):
        for c in range(COLS):
            x = c * CELL_SIZE
            y = r * CELL_SIZE
            rect = pygame.Rect(x, y, CELL_SIZE, CELL_SIZE)

            # Get terrain type for this cell
            cell = (r, c)
            terrain_type = terrain.get(cell, TERRAIN_GRASS)
            
            # Choose color based on terrain type
            if terrain_type == TERRAIN_GRASS:
                color = COLOR_GRASS
            elif terrain_type == TERRAIN_WATER:
                color = COLOR_WATER
            elif terrain_type == TERRAIN_MUD:
                color = COLOR_MUD
            elif terrain_type == TERRAIN_WALL:
                color = COLOR_WALL
            else:
                color = COLOR_BG  # Fallback

            # Fill the cell with the terrain color
            # Use anti-aliased rounded rectangle for smoother edges if available
            if HAS_GFXDRAW and terrain_type != TERRAIN_GRASS:
                # Draw a slightly rounded rectangle for smoother appearance
                # Create a surface for anti-aliasing effect
                cell_surface = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
                # Draw filled rounded rectangle
                pygame.draw.rect(cell_surface, color, (0, 0, CELL_SIZE, CELL_SIZE), border_radius=2)
                surface.blit(cell_surface, (x, y))
            else:
                # Standard rectangle drawing
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


def draw_help_text(surface, font, current_terrain=None):
    """
    Draw the help text at the bottom of the screen.
    
    Args:
        surface: pygame.Surface to draw on
        font: pygame.font.Font object for rendering text
        current_terrain: Current selected terrain type for placement (optional)
    """
    from astar_game.config import COLOR_TEXT, WINDOW_HEIGHT, TERRAIN_GRASS, TERRAIN_WATER, TERRAIN_MUD, TERRAIN_WALL
    
    # Build terrain indicator
    terrain_name = "Grass"
    if current_terrain == TERRAIN_WATER:
        terrain_name = "Water"
    elif current_terrain == TERRAIN_MUD:
        terrain_name = "Mud"
    elif current_terrain == TERRAIN_WALL:
        terrain_name = "Wall"
    
    help_text = f"1-4: terrain ({terrain_name})  LMB: place  RMB: target  MMB: goal  SPACE: A*  G: toggle gen  ESC: quit"
    text_surface = font.render(help_text, True, COLOR_TEXT)
    surface.blit(text_surface, (10, WINDOW_HEIGHT - 24))

