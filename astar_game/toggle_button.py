"""
Simple toggle button UI component.
"""

import pygame


class ToggleButton:
    """
    A toggle button (switch) that can be clicked to toggle between on/off states.
    """

    def __init__(self, x, y, width, height, initial_state=False, label=""):
        """
        Initialize a toggle button.

        Args:
            x: X position of the button (left edge)
            y: Y position of the button (top edge)
            width: Width of the button
            height: Height of the button
            initial_state: Initial state (True = on, False = off)
            label: Optional label text to display next to the button
        """
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.state = initial_state
        self.label = label

        # Button appearance
        self.switch_width = 50
        self.switch_height = 24
        self.handle_radius = 10

        # Colors
        self.bg_color_off = (80, 80, 90)
        self.bg_color_on = (90, 220, 120)  # Green when on
        self.handle_color = (240, 240, 240)
        self.text_color = (230, 230, 230)
        self.label_color = (200, 200, 200)

    def toggle(self):
        """Toggle the button state."""
        self.state = not self.state

    def is_clicked(self, mouse_pos):
        """
        Check if the button was clicked.

        Args:
            mouse_pos: Tuple of (x, y) mouse position

        Returns:
            True if the button was clicked, False otherwise
        """
        mouse_x, mouse_y = mouse_pos
        
        # Check if click is within the switch area
        switch_x = self.x
        switch_y = self.y
        
        return (switch_x <= mouse_x <= switch_x + self.switch_width and
                switch_y <= mouse_y <= switch_y + self.switch_height)

    def handle_event(self, event):
        """
        Handle pygame events for button interaction.

        Args:
            event: pygame.Event object

        Returns:
            True if the event was handled (button was clicked), False otherwise
        """
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left mouse button
                if self.is_clicked(event.pos):
                    self.toggle()
                    return True
        return False

    def draw(self, surface, font):
        """
        Draw the toggle button on the screen.

        Args:
            surface: pygame.Surface to draw on
            font: pygame.font.Font for rendering text
        """
        # Draw label if provided
        if self.label:
            label_surface = font.render(self.label, True, self.label_color)
            surface.blit(label_surface, (self.x, self.y - 22))

        # Draw switch background
        bg_color = self.bg_color_on if self.state else self.bg_color_off
        switch_rect = pygame.Rect(self.x, self.y, self.switch_width, self.switch_height)
        pygame.draw.rect(surface, bg_color, switch_rect, border_radius=12)
        
        # Draw border
        pygame.draw.rect(surface, (50, 50, 50), switch_rect, width=2, border_radius=12)

        # Draw handle (circle that moves left/right)
        handle_x = self.x + self.switch_width - self.handle_radius - 2 if self.state else self.x + self.handle_radius + 2
        handle_y = self.y + self.switch_height // 2
        pygame.draw.circle(surface, self.handle_color, (int(handle_x), int(handle_y)), self.handle_radius)
        pygame.draw.circle(surface, (50, 50, 50), (int(handle_x), int(handle_y)), self.handle_radius, 2)

        # Draw state text (ON/OFF)
        state_text = "ON" if self.state else "OFF"
        state_surface = font.render(state_text, True, self.text_color)
        state_rect = state_surface.get_rect(center=(self.x + self.switch_width // 2, self.y + self.switch_height + 15))
        surface.blit(state_surface, state_rect)
