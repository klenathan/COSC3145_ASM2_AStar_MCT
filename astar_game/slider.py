"""
Simple slider UI component for adjusting values.
"""

import pygame
from pygame.math import Vector2 as V2


class Slider:
    """
    A simple horizontal slider for adjusting numeric values.
    """

    def __init__(self, x, y, width, min_value, max_value, initial_value, label=""):
        """
        Initialize a slider.

        Args:
            x: X position of the slider (left edge)
            y: Y position of the slider (center)
            width: Width of the slider track in pixels
            min_value: Minimum value the slider can represent
            max_value: Maximum value the slider can represent
            initial_value: Initial value of the slider
            label: Optional label text to display above the slider
        """
        self.x = x
        self.y = y
        self.width = width
        self.min_value = min_value
        self.max_value = max_value
        self.value = initial_value
        self.label = label

        # Slider appearance
        self.track_height = 6
        self.handle_radius = 8
        self.dragging = False

        # Colors
        self.track_color = (100, 100, 120)
        self.track_fill_color = (90, 220, 120)  # Green for filled portion
        self.handle_color = (200, 200, 220)
        self.handle_active_color = (255, 255, 255)
        self.text_color = (230, 230, 230)

    def get_handle_x(self):
        """Get the X position of the slider handle based on current value."""
        ratio = (self.value - self.min_value) / \
            (self.max_value - self.min_value)
        return self.x + ratio * self.width

    def set_value_from_x(self, x):
        """Set the slider value based on an X coordinate."""
        # Clamp x to slider bounds
        x = max(self.x, min(self.x + self.width, x))
        ratio = (x - self.x) / self.width
        self.value = self.min_value + ratio * (self.max_value - self.min_value)
        self.value = max(self.min_value, min(self.max_value, self.value))

    def handle_event(self, event):
        """
        Handle pygame events for slider interaction.

        Args:
            event: pygame.Event object

        Returns:
            True if the event was handled, False otherwise
        """
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left mouse button
                mouse_x, mouse_y = event.pos
                handle_x = self.get_handle_x()

                # Check if click is on the handle or track
                if (abs(mouse_x - handle_x) < self.handle_radius * 2 or
                    (self.x <= mouse_x <= self.x + self.width and
                     self.y - self.handle_radius <= mouse_y <= self.y + self.handle_radius)):
                    self.dragging = True
                    self.set_value_from_x(mouse_x)
                    return True

        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                self.dragging = False

        elif event.type == pygame.MOUSEMOTION:
            if self.dragging:
                mouse_x, _ = event.pos
                self.set_value_from_x(mouse_x)
                return True

        return False

    def update(self, mouse_pos):
        """
        Update slider if dragging (for continuous updates).

        Args:
            mouse_pos: Tuple of (x, y) mouse position
        """
        if self.dragging:
            mouse_x, _ = mouse_pos
            self.set_value_from_x(mouse_x)

    def draw(self, surface, font):
        """
        Draw the slider on the screen.

        Args:
            surface: pygame.Surface to draw on
            font: pygame.font.Font for rendering text
        """
        # Draw track background
        track_rect = pygame.Rect(self.x, self.y - self.track_height // 2,
                                 self.width, self.track_height)
        pygame.draw.rect(surface, self.track_color, track_rect)

        # Draw filled portion of track
        handle_x = self.get_handle_x()
        fill_width = handle_x - self.x
        if fill_width > 0:
            fill_rect = pygame.Rect(self.x, self.y - self.track_height // 2,
                                    fill_width, self.track_height)
            pygame.draw.rect(surface, self.track_fill_color, fill_rect)

        # Draw handle
        handle_color = self.handle_active_color if self.dragging else self.handle_color
        pygame.draw.circle(surface, handle_color, (int(
            handle_x), int(self.y)), self.handle_radius)
        pygame.draw.circle(surface, (50, 50, 50), (int(
            handle_x), int(self.y)), self.handle_radius, 2)

        # Draw label and value
        if self.label:
            label_surface = font.render(self.label, True, self.text_color)
            surface.blit(label_surface, (self.x, self.y - 25))

        # Draw current value
        value_text = f"{int(self.value)}"
        value_surface = font.render(value_text, True, self.text_color)
        value_rect = value_surface.get_rect(center=(handle_x, self.y + 20))
        surface.blit(value_surface, value_rect)
