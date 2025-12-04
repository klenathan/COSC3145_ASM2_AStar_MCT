"""
Terrain generation utilities for creating random terrain configurations on the grid.
"""

import random
from collections import deque
from astar_game.config import (
    ROWS, COLS,
    TERRAIN_GRASS, TERRAIN_WATER, TERRAIN_MUD, TERRAIN_WALL,
    TERRAIN_WATER_DENSITY, TERRAIN_MUD_DENSITY, TERRAIN_WALL_DENSITY,
    CLUSTER_WATER_SEEDS, CLUSTER_MUD_SEEDS, CLUSTER_WALL_SEEDS,
    CLUSTER_MAX_RADIUS, CLUSTER_GROWTH_PROBABILITY,
)


def generate_random_terrain(start, goal, max_attempts=10):
    """
    Generate random terrain on the grid while ensuring a valid path exists from start to goal.

    Args:
        start: Tuple of (row, col) representing the start cell
        goal: Tuple of (row, col) representing the goal cell
        max_attempts: Maximum number of attempts to generate valid terrain (default: 10)

    Returns:
        Dictionary mapping (row, col) -> terrain_type. If max_attempts is exceeded,
        returns all grass as fallback.
    """
    # Generate all possible cell positions
    all_cells = [(r, c) for r in range(ROWS) for c in range(COLS)]

    # Remove start and goal from possible terrain placement positions
    valid_terrain_cells = [
        cell for cell in all_cells if cell != start and cell != goal]

    total_cells = ROWS * COLS
    available_cells = len(valid_terrain_cells)

    # Calculate number of cells for each terrain type
    num_water = int(total_cells * TERRAIN_WATER_DENSITY)
    num_mud = int(total_cells * TERRAIN_MUD_DENSITY)
    num_walls = int(total_cells * TERRAIN_WALL_DENSITY)

    # Ensure we don't exceed available cells
    total_terrain_cells = num_water + num_mud + num_walls
    if total_terrain_cells > available_cells:
        # Scale down proportionally
        scale = available_cells / total_terrain_cells
        num_water = int(num_water * scale)
        num_mud = int(num_mud * scale)
        num_walls = available_cells - num_water - num_mud

    # Import here to avoid circular import (astar imports get_neighbors from grid)
    from astar_game.astar import run_astar

    for attempt in range(max_attempts):
        # Initialize all cells as grass
        terrain = {}
        for r in range(ROWS):
            for c in range(COLS):
                terrain[(r, c)] = TERRAIN_GRASS

        # Ensure start and goal remain grass
        terrain[start] = TERRAIN_GRASS
        terrain[goal] = TERRAIN_GRASS

        # Randomly assign terrain types
        shuffled_cells = valid_terrain_cells.copy()
        random.shuffle(shuffled_cells)

        # Assign water
        for i in range(min(num_water, len(shuffled_cells))):
            terrain[shuffled_cells[i]] = TERRAIN_WATER

        # Assign mud
        for i in range(num_water, min(num_water + num_mud, len(shuffled_cells))):
            terrain[shuffled_cells[i]] = TERRAIN_MUD

        # Assign walls
        for i in range(num_water + num_mud, min(num_water + num_mud + num_walls, len(shuffled_cells))):
            terrain[shuffled_cells[i]] = TERRAIN_WALL

        # Verify a path exists using A* algorithm
        path, _ = run_astar(start, goal, terrain)

        if path is not None:
            # Valid configuration found
            return terrain

    # If we couldn't find a valid configuration after max_attempts, return all grass
    terrain = {}
    for r in range(ROWS):
        for c in range(COLS):
            terrain[(r, c)] = TERRAIN_GRASS
    return terrain


def generate_random_walls(wall_density, start, goal, max_attempts=10):
    """
    Legacy function for backward compatibility.
    Generate random walls on the grid while ensuring a valid path exists from start to goal.

    Args:
        wall_density: Float between 0.0 and 1.0 representing the percentage of cells to become walls
        start: Tuple of (row, col) representing the start cell
        goal: Tuple of (row, col) representing the goal cell
        max_attempts: Maximum number of attempts to generate valid walls (default: 10)

    Returns:
        Set of (row, col) tuples representing wall cells. If max_attempts is exceeded,
        returns an empty set as fallback.
    """
    # Calculate total number of walls based on density
    total_cells = ROWS * COLS
    num_walls = int(total_cells * wall_density)

    # Ensure we don't try to place more walls than available cells (minus start/goal)
    available_cells = total_cells - 2  # Exclude start and goal
    num_walls = min(num_walls, available_cells)

    if num_walls <= 0:
        return set()

    # Generate all possible cell positions
    all_cells = [(r, c) for r in range(ROWS) for c in range(COLS)]

    # Remove start and goal from possible wall positions
    valid_wall_cells = [
        cell for cell in all_cells if cell != start and cell != goal]

    # Import here to avoid circular import (astar imports get_neighbors from grid)
    from astar_game.astar import run_astar

    for attempt in range(max_attempts):
        # Randomly sample cells to become walls
        walls = set(random.sample(valid_wall_cells, num_walls))

        # Verify a path exists using A* algorithm
        path, _ = run_astar(start, goal, walls)

        if path is not None:
            # Valid configuration found
            return walls

    # If we couldn't find a valid configuration after max_attempts, return empty set
    # This ensures the game can still run, just without walls
    return set()


def _grow_cluster(terrain, seed, terrain_type, valid_cells, max_radius, growth_prob):
    """
    Grow a cluster of terrain from a seed cell using BFS-like expansion.

    Args:
        terrain: Dictionary mapping (row, col) -> terrain_type (modified in place)
        seed: Tuple of (row, col) representing the seed cell
        terrain_type: Type of terrain to place (TERRAIN_WATER, TERRAIN_MUD, or TERRAIN_WALL)
        valid_cells: Set of cells that can be modified (excludes start/goal)
        max_radius: Maximum distance from seed to grow
        growth_prob: Probability (0.0 to 1.0) of expanding to each neighbor

    Returns:
        Number of cells added to the cluster
    """
    if seed not in valid_cells:
        return 0

    # Import here to avoid circular import
    from astar_game.grid.neighbors import get_neighbors

    queue = deque([(seed, 0)])  # (cell, distance_from_seed)
    visited = {seed}
    cells_added = 0

    # Place seed cell
    terrain[seed] = terrain_type
    cells_added += 1

    while queue:
        current_cell, distance = queue.popleft()

        # Stop if we've reached max radius
        if distance >= max_radius:
            continue

        # Get neighbors (pass terrain to check for walls, but we'll filter by grass/validity ourselves)
        neighbors = get_neighbors(current_cell, terrain)

        for neighbor in neighbors:
            # Skip if already visited or not valid
            if neighbor in visited or neighbor not in valid_cells:
                continue

            # Skip if already has terrain assigned (not grass)
            if terrain.get(neighbor, TERRAIN_GRASS) != TERRAIN_GRASS:
                continue

            # Randomly decide whether to expand to this neighbor
            if random.random() < growth_prob:
                terrain[neighbor] = terrain_type
                cells_added += 1
                visited.add(neighbor)

                # Add to queue for further expansion
                queue.append((neighbor, distance + 1))

    return cells_added


def generate_clustered_terrain(start, goal, max_attempts=10):
    """
    Generate realistic clustered terrain on the grid while ensuring a valid path exists.

    This function creates more natural-looking terrain by:
    1. Placing seed cells randomly for each terrain type
    2. Growing clusters around seeds using probabilistic expansion
    3. Ensuring path validity using A* validation

    Args:
        start: Tuple of (row, col) representing the start cell
        goal: Tuple of (row, col) representing the goal cell
        max_attempts: Maximum number of attempts to generate valid terrain (default: 10)

    Returns:
        Dictionary mapping (row, col) -> terrain_type. If max_attempts is exceeded,
        returns all grass as fallback.
    """
    # Generate all possible cell positions
    all_cells = [(r, c) for r in range(ROWS) for c in range(COLS)]

    # Remove start and goal from possible terrain placement positions
    valid_terrain_cells = set(
        cell for cell in all_cells if cell != start and cell != goal
    )

    # Import here to avoid circular import
    from astar_game.astar import run_astar

    for attempt in range(max_attempts):
        # Initialize all cells as grass
        terrain = {}
        for r in range(ROWS):
            for c in range(COLS):
                terrain[(r, c)] = TERRAIN_GRASS

        # Ensure start and goal remain grass
        terrain[start] = TERRAIN_GRASS
        terrain[goal] = TERRAIN_GRASS

        # Create a copy of valid cells that we can modify
        available_cells = valid_terrain_cells.copy()

        # Place water clusters
        water_seeds = random.sample(list(available_cells),
                                    min(CLUSTER_WATER_SEEDS, len(available_cells)))
        for seed in water_seeds:
            if seed in available_cells:
                _grow_cluster(terrain, seed, TERRAIN_WATER, available_cells,
                              CLUSTER_MAX_RADIUS, CLUSTER_GROWTH_PROBABILITY)

        # Place mud clusters (avoid overlapping with water)
        mud_candidates = [cell for cell in available_cells
                          if terrain.get(cell, TERRAIN_GRASS) == TERRAIN_GRASS]
        if mud_candidates:
            mud_seeds = random.sample(mud_candidates,
                                      min(CLUSTER_MUD_SEEDS, len(mud_candidates)))
            for seed in mud_seeds:
                if terrain.get(seed, TERRAIN_GRASS) == TERRAIN_GRASS:
                    _grow_cluster(terrain, seed, TERRAIN_MUD, available_cells,
                                  CLUSTER_MAX_RADIUS, CLUSTER_GROWTH_PROBABILITY)

        # Place wall clusters (avoid overlapping with water and mud)
        wall_candidates = [cell for cell in available_cells
                           if terrain.get(cell, TERRAIN_GRASS) == TERRAIN_GRASS]
        if wall_candidates:
            wall_seeds = random.sample(wall_candidates,
                                       min(CLUSTER_WALL_SEEDS, len(wall_candidates)))
            for seed in wall_seeds:
                if terrain.get(seed, TERRAIN_GRASS) == TERRAIN_GRASS:
                    _grow_cluster(terrain, seed, TERRAIN_WALL, available_cells,
                                  CLUSTER_MAX_RADIUS, CLUSTER_GROWTH_PROBABILITY)

        # Verify a path exists using A* algorithm
        path, _ = run_astar(start, goal, terrain)

        if path is not None:
            # Valid configuration found
            return terrain

    # If we couldn't find a valid configuration after max_attempts, return all grass
    terrain = {}
    for r in range(ROWS):
        for c in range(COLS):
            terrain[(r, c)] = TERRAIN_GRASS
    return terrain
