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
    COLOR_OPEN,
    COLOR_CURRENT,
    COLOR_GRASS,
    COLOR_WATER,
    COLOR_MUD,
    TERRAIN_GRASS,
    TERRAIN_WATER,
    TERRAIN_MUD,
    TERRAIN_WALL,
)


def _get_terrain_color(terrain_type):
    """Get the base color for a terrain type."""
    if terrain_type == TERRAIN_GRASS:
        return COLOR_GRASS
    elif terrain_type == TERRAIN_WATER:
        return COLOR_WATER
    elif terrain_type == TERRAIN_MUD:
        return COLOR_MUD
    elif terrain_type == TERRAIN_WALL:
        return COLOR_WALL
    else:
        return COLOR_BG


def _lerp_color(color1, color2, t):
    """Linear interpolation between two colors."""
    return tuple(int(c1 + (c2 - c1) * t) for c1, c2 in zip(color1, color2))


def _get_blended_color(terrain, cell, rows, cols):
    """
    Get a blended color for a cell based on its neighbors.
    Creates smooth transitions between different terrain types.
    
    Args:
        terrain: Dictionary mapping (row, col) -> terrain_type
        cell: Tuple (row, col) for the current cell
        rows: Total number of rows in grid
        cols: Total number of columns in grid
        
    Returns:
        RGB color tuple
    """
    r, c = cell
    current_terrain = terrain.get(cell, TERRAIN_GRASS)
    current_color = _get_terrain_color(current_terrain)
    
    # Sample neighbors for blending
    neighbors = []
    for dr in [-1, 0, 1]:
        for dc in [-1, 0, 1]:
            if dr == 0 and dc == 0:
                continue
            nr, nc = r + dr, c + dc
            if 0 <= nr < rows and 0 <= nc < cols:
                neighbor_terrain = terrain.get((nr, nc), TERRAIN_GRASS)
                neighbors.append(neighbor_terrain)
    
    # If all neighbors are the same type, no blending needed
    if all(n == current_terrain for n in neighbors):
        return current_color
    
    # Blend with neighboring colors
    blend_color = list(current_color)
    blend_weight = 0.85  # Weight for current cell (higher = less blending)
    neighbor_weight = (1.0 - blend_weight) / len(neighbors) if neighbors else 0
    
    for neighbor_terrain in neighbors:
        if neighbor_terrain != current_terrain:
            neighbor_color = _get_terrain_color(neighbor_terrain)
            for i in range(3):
                blend_color[i] += neighbor_color[i] * neighbor_weight
    
    # Normalize
    blend_color = tuple(int(c * blend_weight + c * (1 - blend_weight)) for c in current_color)
    
    # Better blending: weighted average
    final_color = [current_color[i] * blend_weight for i in range(3)]
    for neighbor_terrain in neighbors:
        neighbor_color = _get_terrain_color(neighbor_terrain)
        for i in range(3):
            final_color[i] += neighbor_color[i] * neighbor_weight
    
    return tuple(int(c) for c in final_color)


def _add_texture_variation(color, cell, variation_amount=0.08):
    """
    Add subtle texture variation to a color based on cell position.
    Uses cell coordinates as a pseudo-random seed for consistency.
    
    Args:
        color: Base RGB color tuple
        cell: Tuple (row, col) for deterministic variation
        variation_amount: How much to vary (0.0 to 1.0)
        
    Returns:
        Modified RGB color tuple
    """
    r, c = cell
    # Use cell coordinates to generate consistent pseudo-random variation
    seed = (r * 73856093) ^ (c * 19349663)  # Hash function
    
    # Generate variation for each color channel
    variation = []
    for i in range(3):
        # Simple pseudo-random based on seed and channel
        channel_seed = (seed + i * 12345) % 1000
        noise = (channel_seed / 1000.0) * 2.0 - 1.0  # Range: -1 to 1
        variation.append(noise * variation_amount)
    
    # Apply variation
    varied_color = tuple(
        max(0, min(255, int(color[i] * (1.0 + variation[i]))))
        for i in range(3)
    )
    
    return varied_color


def draw_grid(surface, terrain, start, goal, current_path, current_closed, **kwargs):
    """
    Draw the grid cells: terrain, start, goal, closed set, and path.
    The draw order matters so that path and special cells are visible.
    
    Args:
        surface: pygame.Surface to draw on
        terrain: Dictionary mapping (row, col) -> terrain_type
        start: Tuple of (row, col) representing the start cell
        goal: Tuple of (row, col) representing the goal cell
        current_path: List of (row, col) tuples representing the current path, or None
        goal: Tuple of (row, col) representing the goal cell
        current_path: List of (row, col) tuples representing the current path, or None
        current_closed: Set of (row, col) tuples representing visited cells
        current_open: Set of (row, col) tuples representing frontier cells (optional)
        current_node: Tuple of (row, col) representing the current processing node (optional)
        show_overlay: Boolean to show/hide A* traversal overlay (optional, default True)
        terrain_colors_cache: Pre-calculated terrain colors (optional, for performance)
        
    Returns:
        terrain_colors_cache: The calculated or passed-in terrain colors cache
    """
    from astar_game.config import ROWS, COLS
    
    # Default optional arguments if not provided by caller (compatibility)
    current_open = kwargs.get('current_open', set())
    current_node = kwargs.get('current_node', None)
    show_overlay = kwargs.get('show_overlay', True)  # Default to showing overlay
    terrain_colors_cache = kwargs.get('terrain_colors_cache', None)
    
    # Calculate terrain colors only if cache is invalid (first time or terrain changed)
    if terrain_colors_cache is None:
        terrain_colors_cache = {}
        for r in range(ROWS):
            for c in range(COLS):
                cell = (r, c)
                # Get blended color based on neighbors
                color = _get_blended_color(terrain, cell, ROWS, COLS)
                # Add subtle texture variation
                color = _add_texture_variation(color, cell, variation_amount=0.12)
                terrain_colors_cache[cell] = color
    
    # First draw terrain base colors using cached colors
    for r in range(ROWS):
        for c in range(COLS):
            x = c * CELL_SIZE
            y = r * CELL_SIZE
            rect = pygame.Rect(x, y, CELL_SIZE, CELL_SIZE)

            # Get terrain type for this cell
            cell = (r, c)
            
            # Use cached color
            color = terrain_colors_cache.get(cell, (0, 0, 0))

            # Fill the cell with the blended and textured color
            pygame.draw.rect(surface, color, rect)

    # Only show A* visualization if overlay is enabled
    if show_overlay:
        # Then show visited cells from the last A* run
        for r, c in current_closed:
            x = c * CELL_SIZE
            y = r * CELL_SIZE
            rect = pygame.Rect(x, y, CELL_SIZE, CELL_SIZE)
            # Color for visited cells
            pygame.draw.rect(surface, COLOR_CLOSED, rect)

        # Draw frontier (open set)
        if current_open:
            for r, c in current_open:
                x = c * CELL_SIZE
                y = r * CELL_SIZE
                rect = pygame.Rect(x, y, CELL_SIZE, CELL_SIZE)
                pygame.draw.rect(surface, COLOR_OPEN, rect)
                
        # Draw current node being processed
        if current_node:
            r, c = current_node
            x = c * CELL_SIZE
            y = r * CELL_SIZE
            rect = pygame.Rect(x, y, CELL_SIZE, CELL_SIZE)
            pygame.draw.rect(surface, COLOR_CURRENT, rect)

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

    # Draw subtle grid lines with transparency
    # Create a semi-transparent surface for grid lines
    grid_surface = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
    grid_alpha = 30  # Low alpha for subtle grid lines (0-255)
    grid_color = (*COLOR_GRID, grid_alpha)
    
    for c in range(COLS + 1):
        x = c * CELL_SIZE
        pygame.draw.line(grid_surface, grid_color, (x, 0), (x, WINDOW_HEIGHT), 1)
    for r in range(ROWS + 1):
        y = r * CELL_SIZE
        pygame.draw.line(grid_surface, grid_color, (0, y), (WINDOW_WIDTH, y), 1)
    
    surface.blit(grid_surface, (0, 0))
    
    # Return the cache for reuse in next frame
    return terrain_colors_cache




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
            terrain_type = terrain.get(current_path[i + 1], TERRAIN_GRASS)
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
