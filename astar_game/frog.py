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
        self.path_index = 0

    def set_path(self, path_cells):
        """
        Set a new path for the frog to follow.

        Args:
            path_cells: List of (row, col) tuples representing the path in grid coordinates
        """
        if path_cells is None or len(path_cells) == 0:
            self.path = []
            self.path_index = 0
            return

        # Store cell coordinates directly
        self.path = list(path_cells)
        # Reset path index. Note: path normally includes the starting cell as index 0.
        # If we are already at index 0, logic will quickly advance to index 1.
        self.path_index = 0

    def update(self, dt):
        """
        Update the frog's position using path following behavior.

        Args:
            dt: Delta time in seconds since last frame
        """
        # If no path, stop
        if not self.path:
            self.vel = V2()
            return
            
        # Use strict path following
        from astar_game.steering import follow_path_strict
        self.vel, self.path_index = follow_path_strict(
            self.pos, self.path, self.path_index, self.speed
        )
        
        # Check if we finished the path
        if self.path_index >= len(self.path):
            self.vel = V2()
            # Optionally snap to exact end position
            if len(self.path) > 0:
                end_cell = self.path[-1]
                end_pos = V2(*cell_to_pixel_center(end_cell))
                # Only snap if very close, to avoid teleporting if something weird happened
                if (end_pos - self.pos).length() < 10.0:
                    self.pos = end_pos

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
        Draw the frog on the screen with enhanced visuals.

        Args:
            surface: pygame.Surface to draw on
        """
        import math
        
        # Get direction from velocity
        angle = 0
        if self.vel.length() > 1.0:
            angle = math.atan2(self.vel.y, self.vel.x)
        
        # Create a surface for the frog to allow rotation
        frog_size = FROG_RADIUS * 3
        frog_surface = pygame.Surface((frog_size, frog_size), pygame.SRCALPHA)
        center = frog_size // 2
        
        # Color palette for the frog
        body_color = (90, 220, 120)  # Bright green
        body_dark = (60, 180, 80)    # Darker green for shading
        eye_white = (255, 255, 255)  # White for eyes
        eye_black = (20, 20, 20)     # Black for pupils
        belly_color = (200, 240, 180)  # Light yellow-green for belly
        
        # Animation: subtle pulsing effect based on movement
        pulse = 0
        if self.vel.length() > 1.0:
            pulse = abs(math.sin(pygame.time.get_ticks() / 150.0)) * 0.15
        
        # Body radius with pulse
        body_radius = int(FROG_RADIUS * (1.0 + pulse))
        
        # Draw back legs (simple ovals)
        leg_offset = FROG_RADIUS * 0.6
        leg_radius_x = FROG_RADIUS * 0.5
        leg_radius_y = FROG_RADIUS * 0.3
        
        # Left back leg
        leg_rect_left = pygame.Rect(
            center - leg_offset - leg_radius_x,
            center + FROG_RADIUS * 0.3,
            leg_radius_x * 2,
            leg_radius_y * 2
        )
        pygame.draw.ellipse(frog_surface, body_dark, leg_rect_left)
        
        # Right back leg
        leg_rect_right = pygame.Rect(
            center + leg_offset - leg_radius_x,
            center + FROG_RADIUS * 0.3,
            leg_radius_x * 2,
            leg_radius_y * 2
        )
        pygame.draw.ellipse(frog_surface, body_dark, leg_rect_right)
        
        # Draw main body (circle with gradient effect)
        # Outer darker circle for depth
        pygame.draw.circle(frog_surface, body_dark, (center, center), body_radius + 2)
        # Main body
        pygame.draw.circle(frog_surface, body_color, (center, center), body_radius)
        
        # Draw belly (lighter oval in the center-bottom)
        belly_rect = pygame.Rect(
            center - FROG_RADIUS * 0.5,
            center + FROG_RADIUS * 0.2,
            FROG_RADIUS,
            FROG_RADIUS * 0.8
        )
        pygame.draw.ellipse(frog_surface, belly_color, belly_rect)
        
        # Draw eyes (positioned based on direction)
        eye_offset_x = FROG_RADIUS * 0.4
        eye_offset_y = -FROG_RADIUS * 0.3
        eye_radius = FROG_RADIUS * 0.35
        pupil_radius = FROG_RADIUS * 0.15
        
        # Left eye
        left_eye_pos = (int(center - eye_offset_x), int(center + eye_offset_y))
        # Eye white with slight outline
        pygame.draw.circle(frog_surface, body_dark, left_eye_pos, int(eye_radius) + 1)
        pygame.draw.circle(frog_surface, eye_white, left_eye_pos, int(eye_radius))
        # Pupil
        pygame.draw.circle(frog_surface, eye_black, left_eye_pos, int(pupil_radius))
        # Highlight for shine effect
        highlight_offset = int(pupil_radius * 0.4)
        pygame.draw.circle(frog_surface, (255, 255, 255), 
                         (left_eye_pos[0] - highlight_offset, left_eye_pos[1] - highlight_offset), 
                         max(1, int(pupil_radius * 0.3)))
        
        # Right eye
        right_eye_pos = (int(center + eye_offset_x), int(center + eye_offset_y))
        # Eye white with slight outline
        pygame.draw.circle(frog_surface, body_dark, right_eye_pos, int(eye_radius) + 1)
        pygame.draw.circle(frog_surface, eye_white, right_eye_pos, int(eye_radius))
        # Pupil
        pygame.draw.circle(frog_surface, eye_black, right_eye_pos, int(pupil_radius))
        # Highlight for shine effect
        pygame.draw.circle(frog_surface, (255, 255, 255), 
                         (right_eye_pos[0] - highlight_offset, right_eye_pos[1] - highlight_offset), 
                         max(1, int(pupil_radius * 0.3)))
        
        # Draw front legs (small circles)
        front_leg_radius = FROG_RADIUS * 0.25
        front_leg_offset_x = FROG_RADIUS * 0.7
        front_leg_offset_y = FROG_RADIUS * 0.1
        
        # Left front leg
        pygame.draw.circle(frog_surface, body_dark, 
                         (int(center - front_leg_offset_x), int(center + front_leg_offset_y)), 
                         int(front_leg_radius))
        
        # Right front leg
        pygame.draw.circle(frog_surface, body_dark, 
                         (int(center + front_leg_offset_x), int(center + front_leg_offset_y)), 
                         int(front_leg_radius))
        
        # Rotate the frog surface based on movement direction
        if self.vel.length() > 1.0:
            # Convert angle to degrees and rotate
            angle_deg = math.degrees(angle)
            rotated_surface = pygame.transform.rotate(frog_surface, -angle_deg)
            rotated_rect = rotated_surface.get_rect(center=(int(self.pos.x), int(self.pos.y)))
            surface.blit(rotated_surface, rotated_rect)
        else:
            # No rotation when stationary
            frog_rect = frog_surface.get_rect(center=(int(self.pos.x), int(self.pos.y)))
            surface.blit(frog_surface, frog_rect)


    def set_speed(self, speed):
        """
        Set the frog's movement speed.

        Args:
            speed: New speed in pixels per second
        """
        self.speed = max(10.0, min(SPEED_CLAMP, speed))  # Clamp between 10 and SPEED_CLAMP
