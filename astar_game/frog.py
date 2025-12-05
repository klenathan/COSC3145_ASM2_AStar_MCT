"""
Frog entity class that follows A* paths using steering behaviors.
"""

import pygame
from pygame.math import Vector2 as V2
from astar_game.config import FROG_RADIUS, FROG_SPEED, ARRIVE_STOP_RADIUS, GREEN, CELL_SIZE, SPEED_CLAMP, PATH_LOOKAHEAD
from astar_game.steering import follow_path, integrate_velocity
from astar_game.grid.coordinates import cell_to_pixel_center


class Frog:
    """
    Frog entity that follows paths using steering behaviors.
    """

    def __init__(self, start_cell, speed=FROG_SPEED):
        """
        Initialize the frog at a grid cell position.

        Args:
            start_cell: Tuple of (row, col) representing the starting grid cell
            speed: Initial speed of the frog in pixels per second
        """
        # Convert grid cell to pixel position (center of cell)
        x, y = cell_to_pixel_center(start_cell)
        self.pos = V2(x, y)
        self.vel = V2(0, 0)
        self.speed = speed  # Dynamic speed that can be adjusted

        # Path following state
        # List of waypoints in cell coordinates (row, col)
        self.path: list[tuple] = []

    def set_path(self, path_cells):
        """
        Set a new path for the frog to follow.

        Args:
            path_cells: List of (row, col) tuples representing the path in grid coordinates
        """
        if path_cells is None or len(path_cells) == 0:
            self.path = []
            return

        # Store cell coordinates directly
        self.path = list(path_cells)

    def update(self, dt):
        """
        Update the frog's position using path following behavior.

        Args:
            dt: Delta time in seconds since last frame
        """
        # If no path, stop
        if not self.path or len(self.path) < 2:
            # Apply braking force to slow down
            self.vel = integrate_velocity(
                self.vel, -self.vel * 5.0, dt, self.speed)
            return

        # Check if we've reached the end of the path
        # Convert last cell to pixel center for distance calculation
        end_cell = self.path[-1]
        end_pixel = V2(*cell_to_pixel_center(end_cell))
        distance_to_end = (end_pixel - self.pos).length()
        # if distance_to_end < ARRIVE_STOP_RADIUS:
        #     # Reached the end, stop
        #     self.vel = integrate_velocity(
        #         self.vel, -self.vel * 5.0, dt, self.speed)
        #     return

        # Use path following behavior to follow the path smoothly
        # Pass cell coordinates to follow_path
        steering_force = follow_path(
            self.pos, self.vel, self.path, PATH_LOOKAHEAD, self.speed)

        # Apply steering force to velocity
        self.vel = integrate_velocity(self.vel, steering_force, dt, self.speed)

        # Update position based on velocity
        self.pos += self.vel * dt

    def get_cell(self):
        """
        Get the current grid cell the frog is in.

        Returns:
            Tuple of (row, col) representing the current grid cell
        """
        c = int(self.pos.x // CELL_SIZE)
        r = int(self.pos.y // CELL_SIZE)
        return (r, c)

    def draw(self, surface):
        """
        Draw the frog on the screen.

        Args:
            surface: pygame.Surface to draw on
        """
        pygame.draw.circle(surface, GREEN, (int(self.pos.x),
                           int(self.pos.y)), FROG_RADIUS)

    def set_speed(self, speed):
        """
        Set the frog's movement speed.

        Args:
            speed: New speed in pixels per second
        """
        self.speed = max(10.0, min(SPEED_CLAMP, speed)
                         )  # Clamp between 10 and SPEED_CLAMP
