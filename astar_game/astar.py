"""
A* pathfinding algorithm implementation.
"""

import math
import heapq
from astar_game.grid import get_neighbors
from astar_game.config import TERRAIN_COSTS, TERRAIN_WALL, TERRAIN_GRASS


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


def run_astar_step(start, goal, terrain, allow_diagonal_neighbors=False):
    """
    Generator that yields the state of the A* algorithm at each step.
    
    Yields:
        Tuple of (current_path, open_set, closed_set, current_node)
        - current_path: Path from start to current node (or None)
        - open_set: Set of cells in the frontier
        - closed_set: Set of visited cells
        - current_node: The node currently being processed
    """
    # If start or goal is a wall, we cannot find a path
    if start in terrain and terrain[start] == TERRAIN_WALL:
        return
    if goal in terrain and terrain[goal] == TERRAIN_WALL:
        return

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

        # Mark as visited (temporarily add to closed set for visualization before expansion)
        closed_set.add(current)
        
        # Build current path for visualization
        path_so_far = reconstruct_path(came_from, current)
        
        # Yield current state
        yield path_so_far, open_set.copy(), closed_set.copy(), current

        # If we reached the goal, we are done
        if current == goal:
            return

        # Check all neighbors
        for neighbor in get_neighbors(current, terrain, allow_diagonal_neighbors):
            # Skip if we already visited this cell
            if neighbor in closed_set:
                continue

            # Get terrain type for neighbor cell
            neighbor_terrain = terrain.get(neighbor, TERRAIN_GRASS)
            
            # Skip if neighbor is a wall (shouldn't happen due to get_neighbors, but safety check)
            if neighbor_terrain == TERRAIN_WALL:
                continue
            
            # Get terrain cost multiplier
            terrain_cost = TERRAIN_COSTS.get(neighbor_terrain, 1.0)

            # Calculate base movement cost based on whether move is diagonal
            dr = neighbor[0] - current[0]
            dc = neighbor[1] - current[1]
            is_diagonal = abs(dr) == 1 and abs(dc) == 1
            base_move_cost = math.sqrt(2) if is_diagonal else 1.0

            # Cost from start to this neighbor through current (multiply by terrain cost)
            tentative_g = g_score[current] + base_move_cost * terrain_cost

            # If neighbor is new or we found a better path
            if neighbor not in g_score or tentative_g < g_score[neighbor]:
                came_from[neighbor] = current
                g_score[neighbor] = tentative_g
                f_score[neighbor] = tentative_g + heuristic(neighbor, goal)

                # Add to open_set and heap if not already there
                if neighbor not in open_set:
                    heapq.heappush(open_heap, (f_score[neighbor], neighbor))
                    open_set.add(neighbor)
    
    # Yield final state if no path found
    yield None, open_set.copy(), closed_set.copy(), None


def run_astar(start, goal, terrain, allow_diagonal_neighbors=False):
    """
    Execute the A* algorithm on the current grid with terrain costs.
    Now implemented as a wrapper around the generator.
    """
    generator = run_astar_step(start, goal, terrain, allow_diagonal_neighbors)
    
    last_state = (None, set(), set(), None)
    try:
        for state in generator:
            last_state = state
            # If we found the goal (current node is goal), break early if we want optimal
            # But the generator yields until queue empty or goal found inside loop
            path, _, _, current = state
            if current == goal:
                return path, state[2] # Return path and closed set
    except StopIteration:
        pass
        
    return last_state[0], last_state[2]

