"""
Neighbor cell utilities for finding valid adjacent cells in the grid.
"""

from astar_game.config import ROWS, COLS, ALLOW_DIAGONAL_NEIGHBORS


def get_neighbors(cell, walls):
    """
    Return the valid neighbor cells for a given cell.
    Movement can be in 8 directions (4 cardinal + 4 diagonal) or 4 directions (cardinal only),
    depending on the ALLOW_DIAGONAL_NEIGHBORS config setting.
    Skip cells that are outside the grid or in the walls set.

    Args:
        cell: Tuple of (row, col) representing the current cell
        walls: Set of (row, col) tuples representing wall cells

    Returns:
        List of (row, col) tuples representing valid neighbor cells
    """
    r, c = cell
    neighbors = []

    # Cardinal directions (always allowed)
    cardinal_directions = [
        (-1, 0), (1, 0), (0, -1), (0, 1)  # Up, Down, Left, Right
    ]

    # Diagonal directions (only if allowed by config)
    diagonal_directions = [
        # Top-left, Top-right, Bottom-left, Bottom-right
        (-1, -1), (-1, 1), (1, -1), (1, 1)
    ]

    # Combine directions based on config
    if ALLOW_DIAGONAL_NEIGHBORS:
        directions = cardinal_directions + diagonal_directions
    else:
        directions = cardinal_directions

    for dr, dc in directions:
        nr = r + dr
        nc = c + dc
        # Check grid bounds
        if 0 <= nr < ROWS and 0 <= nc < COLS:
            # Only include neighbor if it is not a wall
            if (nr, nc) not in walls:
                neighbors.append((nr, nc))

    return neighbors
