"""
Coordinate conversion utilities for converting between pixel coordinates and grid cells.
"""

from astar_game.config import CELL_SIZE, ROWS, COLS


def cell_from_mouse(pos):
    """
    Convert mouse pixel position (x, y) to grid cell coordinates (row, col).

    Args:
        pos: Tuple of (x, y) pixel coordinates

    Returns:
        Tuple of (row, col) if position is within grid bounds, None otherwise
    """
    x, y = pos
    c = x // CELL_SIZE
    r = y // CELL_SIZE
    if 0 <= r < ROWS and 0 <= c < COLS:
        return (r, c)
    return None


def cell_to_pixel_center(cell):
    """
    Convert grid cell coordinates (row, col) to pixel coordinates at the center of the cell.

    Args:
        cell: Tuple of (row, col) representing the grid cell

    Returns:
        Tuple of (x, y) pixel coordinates at the center of the cell
    """
    r, c = cell
    x = c * CELL_SIZE + CELL_SIZE / 2
    y = r * CELL_SIZE + CELL_SIZE / 2
    return (x, y)
