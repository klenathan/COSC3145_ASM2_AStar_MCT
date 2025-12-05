"""
Neighbor cell utilities for finding valid adjacent cells in the grid.
"""

from astar_game.config import ROWS, COLS, TERRAIN_WALL, TERRAIN_GRASS


def get_neighbors(cell, terrain, allow_diagonal_neighbors=False):
    """
    Return the valid neighbor cells for a given cell.
    Movement can be in 8 directions (4 cardinal + 4 diagonal) or 4 directions (cardinal only),
    depending on the allow_diagonal_neighbors parameter.
    Skip cells that are outside the grid or are walls (impassable).

    Args:
        cell: Tuple of (row, col) representing the current cell
        terrain: Dictionary mapping (row, col) -> terrain_type
        allow_diagonal_neighbors: Boolean flag to enable/disable diagonal movement

    Returns:
        List of (row, col) tuples representing valid neighbor cells
    """
    r, c = cell
    neighbors = []

    # Cardinal directions (always allowed)
    cardinal_directions = [
        (-1, 0), (1, 0), (0, -1), (0, 1)  # Up, Down, Left, Right
    ]

    # Diagonal directions (only if allowed by parameter)
    diagonal_directions = [
        # Top-left, Top-right, Bottom-left, Bottom-right
        (-1, -1), (-1, 1), (1, -1), (1, 1)
    ]

    # Combine directions based on parameter
    if allow_diagonal_neighbors:
        directions = cardinal_directions + diagonal_directions
    else:
        directions = cardinal_directions

    for dr, dc in directions:
        nr = r + dr
        nc = c + dc
        # Check grid bounds
        if 0 <= nr < ROWS and 0 <= nc < COLS:
            neighbor_cell = (nr, nc)
            # Only include neighbor if it is not a wall (walls are impassable)
            # Default to grass if cell not in terrain dictionary
            neighbor_terrain = terrain.get(neighbor_cell, TERRAIN_GRASS)
            if neighbor_terrain != TERRAIN_WALL:
                neighbors.append(neighbor_cell)

    return neighbors
