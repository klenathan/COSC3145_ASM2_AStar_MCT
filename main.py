"""
Complete A* pathfinding playground in one file.

Controls:
  - Left click: toggle wall on or off on a cell.
  - Right click: set the start cell.
  - Middle click: set the goal cell.
  - Space key: run A* from start to goal and draw the path.
  - Escape or window close: quit the program.

The code is heavily commented so you can follow each step.
"""

import sys
import heapq
import pygame

# --------------------------
# Grid and window settings
# --------------------------

# How many rows and columns in the grid
ROWS = 20
COLS = 30

# Size of each grid cell in pixels
CELL_SIZE = 25

# Compute window size from grid size
WINDOW_WIDTH = COLS * CELL_SIZE
WINDOW_HEIGHT = ROWS * CELL_SIZE

# Colors in RGB format
COLOR_BG = (30, 30, 40)
COLOR_GRID = (60, 60, 70)
COLOR_WALL = (40, 40, 120)
COLOR_START = (0, 200, 0)
COLOR_GOAL = (200, 0, 0)
COLOR_PATH = (250, 220, 120)
COLOR_CLOSED = (120, 0, 120)
COLOR_TEXT = (230, 230, 230)

# Set of wall cells stored as (row, col) pairs
walls = set()

# Initial start and goal cells
start = (5, 5)
goal = (10, 20)

# Latest path and closed set produced by A*
current_path = None       # list of cells from start to goal
current_closed = set()    # set of visited cells


# --------------------------
# Helper functions for grid
# --------------------------

def cell_from_mouse(pos):
    """
    Convert mouse pixel position (x, y) to grid cell coordinates (row, col).
    If the position is outside the grid, return None.
    """
    x, y = pos
    c = x // CELL_SIZE
    r = y // CELL_SIZE
    if 0 <= r < ROWS and 0 <= c < COLS:
        return (r, c)
    return None

def draw_grid(surface):
    """
    Draw the grid cells: background, walls, start, goal, closed set, and path.
    The draw order matters so that path and special cells are visible.
    """
    # First draw base cells (background and walls)
    for r in range(ROWS):
        for c in range(COLS):
            x = c * CELL_SIZE
            y = r * CELL_SIZE
            rect = pygame.Rect(x, y, CELL_SIZE, CELL_SIZE)

            # Start from plain background color
            color = COLOR_BG

            # Walls override background
            if (r, c) in walls:
                color = COLOR_WALL

            # Fill the cell with the chosen color
            pygame.draw.rect(surface, color, rect)

    # Then show visited cells from the last A* run
    for (r, c) in current_closed:
        x = c * CELL_SIZE
        y = r * CELL_SIZE
        rect = pygame.Rect(x, y, CELL_SIZE, CELL_SIZE)
        # Color for visited cells
        pygame.draw.rect(surface, COLOR_CLOSED, rect)

    # Then draw the path if it exists
    if current_path is not None:
        for (r, c) in current_path:
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


# --------------------------
# A* algorithm helpers
# --------------------------

def heuristic(a, b):
    """
    Manhattan distance heuristic between two cells a and b.
    a and b are (row, col) pairs.
    """
    (r1, c1) = a
    (r2, c2) = b
    return abs(r1 - r2) + abs(c1 - c2)

def get_neighbors(cell):
    """
    Return the valid neighbor cells for a given cell.
    We allow movement up, down, left, and right (no diagonals).
    Skip cells that are outside the grid or in the walls set.
    """
    (r, c) = cell
    neighbors = []

    # Four cardinal directions
    directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]

    for dr, dc in directions:
        nr = r + dr
        nc = c + dc
        # Check grid bounds
        if 0 <= nr < ROWS and 0 <= nc < COLS:
            # Only include neighbor if it is not a wall
            if (nr, nc) not in walls:
                neighbors.append((nr, nc))

    return neighbors

def reconstruct_path(came_from, current):
    """
    Rebuild the path from start to goal using the parent pointers in came_from.
    came_from maps each cell to the cell we came from when we found the best path to it.
    """
    path = [current]
    while current in came_from:
        current = came_from[current]
        path.append(current)
    path.reverse()
    return path

def run_astar():
    """
    Execute the A* algorithm on the current grid using the global start, goal, and walls.
    Update the global current_path and current_closed sets so they can be drawn.
    """
    global current_path, current_closed

    # Clear the previous results
    current_path = None
    current_closed = set()

    # If start or goal is on a wall, we cannot find a path
    if start in walls or goal in walls:
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

        # If we reached the goal, reconstruct the path and store results
        if current == goal:
            current_path = reconstruct_path(came_from, current)
            current_closed = closed_set
            return

        # Mark as visited
        closed_set.add(current)

        # Check all neighbors
        for neighbor in get_neighbors(current):
            # Skip if we already visited this cell
            if neighbor in closed_set:
                continue

            # Cost from start to this neighbor through current
            tentative_g = g_score[current] + 1  # each step has cost 1

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
    current_path = None
    current_closed = closed_set


# --------------------------
# Main application loop
# --------------------------

def main():
    global start, goal

    pygame.init()
    pygame.display.set_caption("A* Pathfinding - Lab 1 Week 5")
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    clock = pygame.time.Clock()

    font = pygame.font.SysFont("consolas", 18)

    running = True
    while running:
        # Handle input events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.KEYDOWN:
                # Escape closes the window
                if event.key == pygame.K_ESCAPE:
                    running = False
                # Space runs the A* algorithm
                if event.key == pygame.K_SPACE:
                    run_astar()

            if event.type == pygame.MOUSEBUTTONDOWN:
                cell = cell_from_mouse(pygame.mouse.get_pos())
                if cell is not None:
                    # Left click toggles wall
                    if event.button == 1:
                        if cell == start or cell == goal:
                            pass
                        elif cell in walls:
                            walls.remove(cell)
                        else:
                            walls.add(cell)
                        # Clear previous A* result, as the map changed
                        reset_search()
                    # Right click sets start
                    elif event.button == 3:
                        if cell != goal:
                            start = cell
                            reset_search()
                    # Middle click sets goal
                    elif event.button == 2:
                        if cell != start:
                            goal = cell
                            reset_search()

        # Draw everything
        screen.fill(COLOR_BG)
        draw_grid(screen)

        # Draw help text at the bottom with the mouse
        help_text = "LMB: wall  RMB: start  MMB: goal  SPACE: run A*  ESC: quit"
        text_surface = font.render(help_text, True, COLOR_TEXT)
        screen.blit(text_surface, (10, WINDOW_HEIGHT - 24))

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit(0)

def reset_search():
    """
    Reset path and closed set when the map changes (start, goal, or walls changed).
    This avoids showing an old path that no longer matches the current grid.
    """
    global current_path, current_closed
    current_path = None
    current_closed = set()

if __name__ == "__main__":
    main()