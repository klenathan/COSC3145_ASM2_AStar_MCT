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


def draw_help_text(surface, font, current_terrain=None, debug_mode=False):
    """
    Draw the help text at the bottom of the screen.
    
    Args:
        surface: pygame.Surface to draw on
        font: pygame.font.Font object for rendering text
        current_terrain: Current selected terrain type for placement (optional)
        debug_mode: Whether debug mode is enabled (optional)
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
    
    debug_indicator = " [DEBUG: ON]" if debug_mode else ""
    help_text = f"1-4: terrain ({terrain_name})  LMB: place  RMB: target  MMB: goal  SPACE: A*  G: toggle gen  D: debug{debug_indicator}  ESC: quit"
    text_surface = font.render(help_text, True, COLOR_TEXT)
    surface.blit(text_surface, (10, WINDOW_HEIGHT - 24))



def draw_debug_info(surface, font, frog, terrain, current_path, current_closed, start, goal, fps):
    """
    Draw debug information overlay on the screen.
    
    Args:
        surface: pygame.Surface to draw on
        font: pygame.font.Font object for rendering text
        frog: Frog object to get debug info from
        terrain: Terrain dictionary
        current_path: Current path being followed (or None)
        current_closed: Set of explored cells from last A* run
        start: Start cell position
        goal: Goal cell position
        fps: Current frames per second
    """
    from astar_game.config import COLOR_TEXT, CELL_SIZE, TERRAIN_COSTS, WINDOW_WIDTH, WINDOW_HEIGHT
    from astar_game.astar import heuristic
    import math
    
    # === LEFT PANEL: General Debug Info ===
    debug_bg = pygame.Surface((350, 200))
    debug_bg.set_alpha(200)
    debug_bg.fill((20, 20, 30))
    surface.blit(debug_bg, (10, 10))
    
    # Gather debug information
    frog_cell = frog.get_cell()
    frog_pos = (frog.pos.x, frog.pos.y)
    frog_vel = (frog.vel.x, frog.vel.y)
    frog_speed_current = frog.vel.length()
    frog_speed_max = frog.speed
    
    # Get terrain under frog
    terrain_type = terrain.get(frog_cell, "grass")
    terrain_cost = TERRAIN_COSTS.get(terrain_type, 1.0)
    
    # Path information
    path_length = len(current_path) if current_path else 0
    path_progress = 0
    if current_path and len(frog.path) > 0:
        path_progress = len(current_path) - len(frog.path)
    
    # Prepare debug text lines
    debug_lines = [
        "=== DEBUG INFO ===",
        f"FPS: {fps:.1f}",
        f"Frog Position: ({frog_pos[0]:.1f}, {frog_pos[1]:.1f}) px",
        f"Frog Grid Cell: {frog_cell}",
        f"Frog Velocity: ({frog_vel[0]:.1f}, {frog_vel[1]:.1f}) px/s",
        f"Frog Speed: {frog_speed_current:.1f} / {frog_speed_max:.1f} px/s",
        f"Terrain: {terrain_type} (cost: {terrain_cost})",
        f"Path Length: {path_length} cells",
        f"Path Progress: {path_progress} / {path_length}",
    ]
    
    # Render debug text
    y_offset = 20
    for line in debug_lines:
        text_surface = font.render(line, True, COLOR_TEXT)
        surface.blit(text_surface, (20, y_offset))
        y_offset += 20
    
    # === RIGHT PANEL: A* Statistics ===
    astar_bg = pygame.Surface((380, 250))
    astar_bg.set_alpha(200)
    astar_bg.fill((30, 20, 40))  # Slightly purple tint
    surface.blit(astar_bg, (WINDOW_WIDTH - 390, 10))
    
    # Calculate A* specific metrics
    nodes_explored = len(current_closed)
    
    # Calculate path cost if path exists
    path_cost = 0.0
    if current_path and len(current_path) > 1:
        for i in range(len(current_path) - 1):
            r1, c1 = current_path[i]
            r2, c2 = current_path[i + 1]
            # Calculate movement cost
            dr = abs(r2 - r1)
            dc = abs(c2 - c1)
            is_diagonal = dr == 1 and dc == 1
            base_cost = math.sqrt(2) if is_diagonal else 1.0
            # Get terrain cost of destination cell
            terrain_type = terrain.get(current_path[i + 1], "grass")
            terrain_multiplier = TERRAIN_COSTS.get(terrain_type, 1.0)
            path_cost += base_cost * terrain_multiplier
    
    # Calculate heuristic from frog to goal
    h_to_goal = heuristic(frog_cell, goal)
    
    # Calculate estimated total cost (current cost + heuristic)
    # Estimate: traveled distance + heuristic to goal
    current_traveled = 0.0
    if current_path and len(frog.path) > 0:
        traveled_cells = path_length - len(frog.path)
        for i in range(min(traveled_cells, len(current_path) - 1)):
            r1, c1 = current_path[i]
            r2, c2 = current_path[i + 1]
            dr = abs(r2 - r1)
            dc = abs(c2 - c1)
            is_diagonal = dr == 1 and dc == 1
            base_cost = math.sqrt(2) if is_diagonal else 1.0
            terrain_type = terrain.get(current_path[i + 1], "grass")
            terrain_multiplier = TERRAIN_COSTS.get(terrain_type, 1.0)
            current_traveled += base_cost * terrain_multiplier
    
    estimated_total = current_traveled + h_to_goal
    
    # Waypoints remaining
    waypoints_remaining = len(frog.path)
    
    # Next waypoint
    next_waypoint = "None"
    if frog.path and len(frog.path) > 0:
        next_waypoint = str(frog.path[0])
    
    # A* statistics lines
    astar_lines = [
        "=== A* PATHFINDING ===",
        f"Nodes Explored: {nodes_explored}",
        f"Total Path Cost: {path_cost:.2f}",
        f"Distance to Goal: {h_to_goal:.2f}",
        f"Estimated Total: {estimated_total:.2f}",
        "",
        "=== PATH FOLLOWING ===",
        f"Waypoints Remaining: {waypoints_remaining}",
        f"Next Waypoint: {next_waypoint}",
        f"Start Cell: {start}",
        f"Goal Cell: {goal}",
    ]
    
    # Render A* stats
    y_offset = 20
    for line in astar_lines:
        if line:  # Skip empty lines for spacing
            text_surface = font.render(line, True, COLOR_TEXT)
            surface.blit(text_surface, (WINDOW_WIDTH - 380, y_offset))
        y_offset += 20


def draw_debug_visuals(surface, frog, current_path, start, goal):
    """
    Draw visual debug overlays on the grid.
    
    Args:
        surface: pygame.Surface to draw on
        frog: Frog object
        current_path: Current path being followed
        start: Start cell position
        goal: Goal cell position
    """
    import pygame
    import pygame.time
    import math
    from astar_game.config import CELL_SIZE, PATH_LOOKAHEAD
    from astar_game.grid.coordinates import cell_to_pixel_center
    from pygame.math import Vector2 as V2
    
    # Color definitions for debug visuals
    VELOCITY_COLOR = (255, 100, 255)  # Magenta for velocity vector
    LOOKAHEAD_COLOR = (100, 255, 255)  # Cyan for lookahead point
    WAYPOINT_COLOR = (255, 255, 100)  # Yellow for next waypoint
    
    # Draw velocity vector as an arrow
    if frog.vel.length() > 1.0:  # Only draw if moving
        vel_normalized = frog.vel.normalize()
        arrow_length = min(frog.vel.length() * 0.15, 60)  # Scale with velocity
        arrow_end = frog.pos + vel_normalized * arrow_length
        
        # Draw arrow shaft
        pygame.draw.line(surface, VELOCITY_COLOR, 
                        (int(frog.pos.x), int(frog.pos.y)),
                        (int(arrow_end.x), int(arrow_end.y)), 3)
        
        # Draw arrow head
        arrow_head_size = 8
        perp = V2(-vel_normalized.y, vel_normalized.x)
        head_point1 = arrow_end - vel_normalized * arrow_head_size + perp * arrow_head_size / 2
        head_point2 = arrow_end - vel_normalized * arrow_head_size - perp * arrow_head_size / 2
        pygame.draw.polygon(surface, VELOCITY_COLOR, [
            (int(arrow_end.x), int(arrow_end.y)),
            (int(head_point1.x), int(head_point1.y)),
            (int(head_point2.x), int(head_point2.y))
        ])
    
    # Draw next waypoint target
    if frog.path and len(frog.path) > 0:
        next_waypoint = frog.path[0]
        waypoint_pixel = V2(*cell_to_pixel_center(next_waypoint))
        
        # Draw a pulsing circle around the next waypoint
        pulse = abs(math.sin(pygame.time.get_ticks() / 300.0))  # Pulse effect
        radius = int(12 + pulse * 6)
        pygame.draw.circle(surface, WAYPOINT_COLOR, 
                         (int(waypoint_pixel.x), int(waypoint_pixel.y)), 
                         radius, 3)
        
        # Draw a line from frog to next waypoint
        pygame.draw.line(surface, WAYPOINT_COLOR,
                        (int(frog.pos.x), int(frog.pos.y)),
                        (int(waypoint_pixel.x), int(waypoint_pixel.y)), 1)
    
    # Draw lookahead point for path following
    if frog.path and len(frog.path) >= 2:
        # Calculate lookahead point along the path
        from astar_game.steering import _find_lookahead_on_path
        lookahead_point = _find_lookahead_on_path(frog.pos, frog.path, PATH_LOOKAHEAD)
        
        if lookahead_point:
            # Draw lookahead indicator
            pygame.draw.circle(surface, LOOKAHEAD_COLOR,
                             (int(lookahead_point.x), int(lookahead_point.y)),
                             8, 2)
            # Draw crosshair
            pygame.draw.line(surface, LOOKAHEAD_COLOR,
                           (int(lookahead_point.x) - 10, int(lookahead_point.y)),
                           (int(lookahead_point.x) + 10, int(lookahead_point.y)), 2)
            pygame.draw.line(surface, LOOKAHEAD_COLOR,
                           (int(lookahead_point.x), int(lookahead_point.y) - 10),
                           (int(lookahead_point.x), int(lookahead_point.y) + 10), 2)
