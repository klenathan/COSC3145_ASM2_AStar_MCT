"""
A* pathfinding algorithm implementation.
"""

import math
import heapq
from astar_game.grid import get_neighbors


def heuristic(a, b):
    """
    Euclidean distance heuristic between two cells.
    Better suited for diagonal movement than Manhattan distance.
    
    Args:
        a: Tuple of (row, col) representing the first cell
        b: Tuple of (row, col) representing the second cell
        
    Returns:
        Float representing the Euclidean distance between the two cells
    """
    r1, c1 = a
    r2, c2 = b
    dr = r1 - r2
    dc = c1 - c2
    return math.sqrt(dr * dr + dc * dc)


def reconstruct_path(came_from, current):
    """
    Rebuild the path from start to goal using the parent pointers in came_from.
    
    Args:
        came_from: Dictionary mapping each cell to the cell we came from
        current: The goal cell (row, col)
        
    Returns:
        List of (row, col) tuples representing the path from start to goal
    """
    path = [current]
    while current in came_from:
        current = came_from[current]
        path.append(current)
    path.reverse()
    return path


def run_astar(start, goal, walls):
    """
    Execute the A* algorithm on the current grid.
    
    Args:
        start: Tuple of (row, col) representing the start cell
        goal: Tuple of (row, col) representing the goal cell
        walls: Set of (row, col) tuples representing wall cells
        
    Returns:
        Tuple of (path, closed_set) where:
        - path: List of (row, col) tuples from start to goal, or None if no path exists
        - closed_set: Set of (row, col) tuples representing visited cells
    """
    # If start or goal is on a wall, we cannot find a path
    if start in walls or goal in walls:
        return None, set()

    # Priority queue (min heap) of (f_score, cell)
    open_heap = []
    heapq.heappush(open_heap, (0, start))

    # For fast membership checks
    open_set = {start}
    closed_set = set()

    # g_score and f_score dictionaries
    g_score = {start: 0}
    f_score = {start: heuristic(start, goal)}

    # For reconstructing the path
    came_from = {}

    while open_heap:
        # Get the cell with the smallest f_score
        current_f, current = heapq.heappop(open_heap)
        open_set.remove(current)

        # If we reached the goal, reconstruct the path and return results
        if current == goal:
            path = reconstruct_path(came_from, current)
            return path, closed_set

        # Mark as visited
        closed_set.add(current)

        # Check all neighbors
        for neighbor in get_neighbors(current, walls):
            # Skip if we already visited this cell
            if neighbor in closed_set:
                continue

            # Calculate cost based on whether move is diagonal
            dr = neighbor[0] - current[0]
            dc = neighbor[1] - current[1]
            is_diagonal = abs(dr) == 1 and abs(dc) == 1
            move_cost = math.sqrt(2) if is_diagonal else 1.0

            # Cost from start to this neighbor through current
            tentative_g = g_score[current] + move_cost

            # If neighbor is new or we found a better path
            if neighbor not in g_score or tentative_g < g_score[neighbor]:
                came_from[neighbor] = current
                g_score[neighbor] = tentative_g
                f_score[neighbor] = tentative_g + heuristic(neighbor, goal)

                # Add to open_set and heap if not already there
                if neighbor not in open_set:
                    heapq.heappush(open_heap, (f_score[neighbor], neighbor))
                    open_set.add(neighbor)

    # If we finish the loop, there is no path
    return None, closed_set

