"""
Main game class and game loop implementation.
"""

import sys
import pygame
from astar_game.config import (
    WINDOW_WIDTH,
    WINDOW_HEIGHT,
    DEFAULT_START,
    DEFAULT_GOAL,
    FPS,
    FONT_NAME,
    FONT_SIZE,
    COLOR_BG,
    TERRAIN_GRASS,
    TERRAIN_WATER,
    TERRAIN_MUD,
    TERRAIN_WALL,
    ROWS,
    COLS,
    ALLOW_DIAGONAL_NEIGHBORS,
)
from astar_game.grid import cell_from_mouse, generate_random_terrain, generate_clustered_terrain, generate_perlin_terrain
from astar_game.astar import run_astar
from astar_game.renderer import draw_grid, draw_help_text
from astar_game.frog import Frog
from astar_game.slider import Slider
from astar_game.toggle_button import ToggleButton
from astar_game.config import FROG_SPEED


class Game:
    """
    Main game class that manages the game state and game loop.
    """

    def __init__(self):
        """Initialize the game with default settings."""
        pygame.init()
        pygame.display.set_caption("A* Pathfinding - Lab 1 Week 5")
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont(FONT_NAME, FONT_SIZE)

        # Game state
        self.start = DEFAULT_START
        self.goal = DEFAULT_GOAL
        # Use Perlin terrain generation for more realistic terrain
        self.terrain = generate_perlin_terrain(self.start, self.goal)
        self.current_path = None  # list of cells from start to goal
        self.current_closed = set()  # set of visited cells
        
        # Terrain placement state
        self.current_terrain = TERRAIN_GRASS  # Default to grass
        self.mouse_held = False  # Track if left mouse button is held down
        
        # Debug mode
        self.debug_mode = False  # Toggle with 'D' key
        
        # Pathfinding settings (OOP style - instance variable instead of modifying config)
        self.allow_diagonal_neighbors = ALLOW_DIAGONAL_NEIGHBORS

        # Create frog entity at start position
        self.frog = Frog(DEFAULT_START)

        # Create speed slider
        slider_x = 10
        slider_y = WINDOW_HEIGHT - 60
        slider_width = 200
        self.speed_slider = Slider(
            slider_x, slider_y, slider_width,
            min_value=50.0,
            max_value=800.0,
            initial_value=FROG_SPEED,
            label="Frog Speed"
        )

        # Create diagonal movement toggle button
        toggle_x = slider_x + slider_width + 30
        toggle_y = slider_y
        self.diagonal_toggle = ToggleButton(
            toggle_x, toggle_y, 50, 24,
            initial_state=ALLOW_DIAGONAL_NEIGHBORS,
            label="Diagonal Movement"
        )

        self.running = True

    def reset_search(self):
        """
        Reset path and closed set when the map changes.
        This avoids showing an old path that no longer matches the current grid.
        """
        self.current_path = None
        self.current_closed = set()

    def handle_events(self):
        """Handle pygame events."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            if event.type == pygame.KEYDOWN:
                # Escape closes the window
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                # D key toggles debug mode
                elif event.key == pygame.K_d:
                    self.debug_mode = not self.debug_mode
                # Number keys select terrain type
                elif event.key == pygame.K_1:
                    self.current_terrain = TERRAIN_GRASS
                elif event.key == pygame.K_2:
                    self.current_terrain = TERRAIN_WATER
                elif event.key == pygame.K_3:
                    self.current_terrain = TERRAIN_MUD
                elif event.key == pygame.K_4:
                    self.current_terrain = TERRAIN_WALL
                # Space runs the A* algorithm from frog's current position to goal
                elif event.key == pygame.K_SPACE:
                    # Get frog's current grid cell
                    frog_cell = self.frog.get_cell()
                    # Run A* from frog's position to goal
                    self.current_path, self.current_closed = run_astar(
                        frog_cell, self.goal, self.terrain, self.allow_diagonal_neighbors
                    )
                    # Set the path on the frog so it moves along the calculated path
                    if self.current_path is not None:
                        self.frog.set_path(self.current_path)
                # R key regenerates terrain using Perlin noise
                elif event.key == pygame.K_r:
                    self.terrain = generate_perlin_terrain(self.start, self.goal)
                    self.reset_search()
                    self.frog = Frog(DEFAULT_START)

            if event.type == pygame.MOUSEBUTTONDOWN:
                # Check if slider was clicked first
                if self.speed_slider.handle_event(event):
                    # Slider handled the event, update frog speed
                    self.frog.set_speed(self.speed_slider.value)
                    continue
                
                # Check if diagonal toggle was clicked
                if self.diagonal_toggle.handle_event(event):
                    # Update the instance variable (OOP style)
                    self.allow_diagonal_neighbors = self.diagonal_toggle.state
                    # Reset search so user can see the effect
                    self.reset_search()
                    continue

                cell = cell_from_mouse(pygame.mouse.get_pos())
                if cell is not None:
                    # Left click places selected terrain type
                    if event.button == 1:
                        # Don't allow placing terrain on start or goal
                        if cell != self.start and cell != self.goal:
                            self.terrain[cell] = self.current_terrain
                            # Clear previous A* result, as the map changed
                            self.reset_search()
                            # Enable continuous placement
                            self.mouse_held = True
                    # Right click sets target and runs A* pathfinding for frog
                    elif event.button == 3:
                        # Get frog's current grid cell
                        frog_cell = self.frog.get_cell()
                        target_cell = cell

                        # Run A* from frog's position to target
                        path, closed_set = run_astar(
                            frog_cell, target_cell, self.terrain, self.allow_diagonal_neighbors)

                        if path is not None:
                            # Set the path on the frog
                            self.frog.set_path(path)
                            # Store path and closed set for rendering
                            self.current_path = path
                            self.current_closed = closed_set
                        else:
                            # No path found
                            self.current_path = None
                            self.current_closed = closed_set
                    # Middle click sets goal (legacy, kept for compatibility)
                    elif event.button == 2:
                        self.goal = cell
                        self.reset_search()

            elif event.type == pygame.MOUSEBUTTONUP:
                # Handle slider release
                self.speed_slider.handle_event(event)
                # Stop continuous terrain placement on left button release
                if event.button == 1:
                    self.mouse_held = False

            elif event.type == pygame.MOUSEMOTION:
                # Handle slider dragging
                if self.speed_slider.handle_event(event):
                    # Update frog speed while dragging
                    self.frog.set_speed(self.speed_slider.value)

    def update(self, dt):
        """Update game state.

        Args:
            dt: Delta time in seconds since last frame
        """
        # Update slider if dragging (for smooth continuous updates)
        if self.speed_slider.dragging:
            mouse_pos = pygame.mouse.get_pos()
            self.speed_slider.update(mouse_pos)
            self.frog.set_speed(self.speed_slider.value)

        # Handle continuous terrain placement while mouse is held
        if self.mouse_held:
            mouse_pos = pygame.mouse.get_pos()
            cell = cell_from_mouse(mouse_pos)
            if cell is not None:
                # Don't allow placing terrain on start or goal
                if cell != self.start and cell != self.goal:
                    # Only update if the terrain is different (avoid redundant resets)
                    if self.terrain[cell] != self.current_terrain:
                        self.terrain[cell] = self.current_terrain
                        # Clear previous A* result, as the map changed
                        self.reset_search()

        # Update frog
        self.frog.update(dt)

    def draw(self):
        """Draw the current game state."""
        self.screen.fill(COLOR_BG)
        draw_grid(
            self.screen,
            self.terrain,
            self.start,
            self.goal,
            self.current_path,
            self.current_closed,
        )
        # Draw frog on top of grid
        self.frog.draw(self.screen)

        # Draw speed slider
        self.speed_slider.draw(self.screen, self.font)
        
        # Draw diagonal movement toggle
        self.diagonal_toggle.draw(self.screen, self.font)

        draw_help_text(self.screen, self.font, self.current_terrain, self.debug_mode)
        
        # Draw debug info if enabled
        if self.debug_mode:
            try:
                from astar_game.renderer import draw_debug_info, draw_debug_visuals
                # Draw visual debug overlays on the grid
                draw_debug_visuals(
                    self.screen,
                    self.frog,
                    self.current_path,
                    self.start,
                    self.goal
                )
                # Draw debug info panels
                draw_debug_info(
                    self.screen,
                    self.font,
                    self.frog,
                    self.terrain,
                    self.current_path,
                    self.current_closed,
                    self.start,
                    self.goal,
                    self.clock.get_fps()
                )
            except Exception as e:
                # If debug rendering fails, show error message but don't crash
                error_text = f"Debug Error: {str(e)}"
                error_surface = self.font.render(error_text, True, (255, 100, 100))
                self.screen.blit(error_surface, (10, 50))
        
        pygame.display.flip()

    def run(self):
        """Main game loop."""
        while self.running:
            # Measure delta time (convert milliseconds to seconds)
            dt = self.clock.tick(FPS) / 1000.0

            # Handle input
            self.handle_events()

            # Update game state
            self.update(dt)

            # Draw everything
            self.draw()

        pygame.quit()
        sys.exit(0)
