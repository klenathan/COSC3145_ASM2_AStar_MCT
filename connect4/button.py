"""
Button class for Connect 4 GUI.

Provides a reusable button component with hover effects and click detection.
"""

import pygame


class Button:
    """
    A clickable button for the GUI menu.
    
    Features:
    - Hover effect with color change
    - Click detection
    - Customizable text, position, and colors
    """
    
    def __init__(self, x, y, width, height, text, font, 
                 normal_color=(70, 70, 70), 
                 hover_color=(100, 100, 100),
                 text_color=(255, 255, 255),
                 border_color=(150, 150, 150)):
        """
        Initialize a button.
        
        Arguments:
            x: X position of button (top-left corner)
            y: Y position of button (top-left corner)
            width: Button width
            height: Button height
            text: Button text
            font: Pygame font object
            normal_color: Button color in normal state
            hover_color: Button color when hovered
            text_color: Text color
            border_color: Border color
        """
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.font = font
        self.normal_color = normal_color
        self.hover_color = hover_color
        self.text_color = text_color
        self.border_color = border_color
        self.is_hovered = False
    
    def update(self, mouse_pos):
        """
        Update button state based on mouse position.
        
        Arguments:
            mouse_pos: Tuple (x, y) of mouse position
        """
        self.is_hovered = self.rect.collidepoint(mouse_pos)
    
    def is_clicked(self, mouse_pos):
        """
        Check if button was clicked.
        
        Arguments:
            mouse_pos: Tuple (x, y) of mouse position
            
        Returns:
            True if button bounds contain the mouse position, False otherwise
        """
        return self.rect.collidepoint(mouse_pos)
    
    def draw(self, screen, theme=None):
        """
        Draw the button on the screen with modern styling.
        
        Arguments:
            screen: Pygame surface to draw on
            theme: Optional theme object for theming
        """
        # Determine button colors based on theme and hover state
        if theme:
            if theme.button_color and theme.button_hover_color:
                normal_color = theme.button_color
                hover_color = theme.button_hover_color
            else:
                # Fallback to default colors if theme doesn't specify
                normal_color = self.normal_color
                hover_color = self.hover_color
        else:
            normal_color = self.normal_color
            hover_color = self.hover_color
        
        color = hover_color if self.is_hovered else normal_color
        
        # Draw shadow for depth (offset slightly down and right)
        if self.is_hovered:
            shadow_offset = 2
            shadow_color = (0, 0, 0, 100)  # Semi-transparent black
        else:
            shadow_offset = 4
            shadow_color = (0, 0, 0, 80)
        
        shadow_rect = self.rect.copy()
        shadow_rect.x += shadow_offset
        shadow_rect.y += shadow_offset
        
        # Create a surface for the shadow with alpha
        shadow_surface = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
        pygame.draw.rect(shadow_surface, shadow_color, shadow_surface.get_rect(), border_radius=8)
        screen.blit(shadow_surface, shadow_rect)
        
        # Draw button background with rounded corners
        pygame.draw.rect(screen, color, self.rect, border_radius=8)
        
        # Draw subtle gradient overlay for depth
        if self.is_hovered:
            # Lighter gradient on hover
            gradient_surface = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
            for i in range(self.rect.height // 2):
                alpha = int(30 * (1 - i / (self.rect.height // 2)))
                pygame.draw.line(gradient_surface, (*color[:3], alpha), 
                               (0, i), (self.rect.width, i))
            screen.blit(gradient_surface, self.rect.topleft)
        
        # Draw border with theme color
        border_color = theme.accent_color if theme else self.border_color
        border_width = 3 if self.is_hovered else 2
        pygame.draw.rect(screen, border_color, self.rect, border_width, border_radius=8)
        
        # Draw text centered on button with shadow
        text_color = (255, 255, 255)
        
        # Text shadow for better readability
        text_shadow = self.font.render(self.text, True, (0, 0, 0))
        text_shadow_rect = text_shadow.get_rect(center=(self.rect.centerx + 1, self.rect.centery + 1))
        screen.blit(text_shadow, text_shadow_rect)
        
        # Main text
        text_surface = self.font.render(self.text, True, text_color)
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)

