"""
Wall generation utilities for creating random wall configurations on the grid.
"""

import random
from astar_game.config import ROWS, COLS


def generate_random_walls(wall_density, start, goal, max_attempts=10):
    """
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

