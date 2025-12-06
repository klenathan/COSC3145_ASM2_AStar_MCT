"""
Overlay info/config panel component for displaying game controls and status.
"""

import pygame

from .config import WINDOW_WIDTH


class InfoPanel:
    """
    An overlay panel that displays game controls, status, and settings with interactive elements.
    """

    def __init__(self, x=WINDOW_WIDTH - 10, y=10, width=320, visible=True):
        """
        Initialize the info panel.

        Args:
            x: X position of the panel (left edge)
            y: Y position of the panel (top edge)
            width: Width of the panel
            visible: Initial visibility state
        """
        self.x = x - width
        self.y = y
        self.width = width
        self.visible = visible
        self.settings_expanded = True  # Default to expanded (open)
        
        # Colors
        self.bg_color = (20, 25, 30)
        self.border_color = (255, 200, 80)  # Golden/yellow border
        self.text_color = (230, 230, 230)
        self.header_color = (90, 220, 120)  # Green for headers
        self.status_running_color = (90, 220, 120)  # Green
        self.status_paused_color = (255, 200, 80)  # Yellow
        self.status_idle_color = (180, 180, 180)  # Gray
        self.toggle_button_color = (60, 65, 70)  # Dark gray for toggle button
        self.toggle_button_hover_color = (80, 85, 90)  # Lighter gray on hover
        
        # Panel settings
        self.padding = 12
        self.line_height = 20
        self.border_width = 2
        self.border_radius = 8
        self.bg_alpha = 220  # Semi-transparent background
        self.collapsed_height = 50  # Height when settings are collapsed
        
        # Toggle button state
        self.toggle_button_hovered = False
        
        # Store references to UI components (will be set externally)

        self.viz_speed_slider = None
        self.diagonal_toggle = None
        self.overlay_toggle = None

    def toggle(self):
        """Toggle panel visibility."""
        self.visible = not self.visible

    def set_ui_components(self, viz_speed_slider, diagonal_toggle, overlay_toggle):
        """
        Set references to UI components that will be embedded in the panel.
        
        Args:

            viz_speed_slider: Slider for visualization speed
            diagonal_toggle: Toggle for diagonal movement
            overlay_toggle: Toggle for A* overlay visibility
        """

        self.viz_speed_slider = viz_speed_slider
        self.diagonal_toggle = diagonal_toggle
        self.overlay_toggle = overlay_toggle

    def handle_event(self, event):
        """
        Handle pygame events for interactive elements in the panel.
        
        Args:
            event: pygame.Event object
            
        Returns:
            True if the event was handled by a UI component, False otherwise
        """
        if not self.visible:
            return False
        
        # Check if event is within panel bounds first
        # We only restrict MOUSEBUTTONDOWN to the panel area.
        # We MUST allow MOUSEBUTTONUP and MOUSEMOTION to pass through so that
        # dragging operations (which might go outside the panel) can be handled correctly.
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_x, mouse_y = event.pos
            # Calculate panel height dynamically
            panel_height = self._calculate_panel_height()
            if not (self.x <= mouse_x <= self.x + self.width and 
                    self.y <= mouse_y <= self.y + panel_height):
                return False
        
        # Only handle UI component events if settings are expanded
        if self.settings_expanded:
            # Delegate to UI components

            if self.viz_speed_slider and self.viz_speed_slider.handle_event(event):
                return True
            if self.diagonal_toggle and self.diagonal_toggle.handle_event(event):
                return True
            if self.overlay_toggle and self.overlay_toggle.handle_event(event):
                return True
        
        return False

    def update(self, mouse_pos):
        """
        Update UI components (for dragging sliders).
        
        Args:
            mouse_pos: Current mouse position tuple (x, y)
        """
        if not self.visible:
            return
        

        if self.viz_speed_slider and self.viz_speed_slider.dragging:
            self.viz_speed_slider.update(mouse_pos)

    def _calculate_panel_height(self):
        """Calculate the height of the panel based on content."""
        # If settings are collapsed, return minimal height
        if not self.settings_expanded:
            return self.collapsed_height
        
        # Base content lines (increased for A* stats section)
        lines = 20  # Approximate number of text lines (increased for terrain breakdown)
        
        # Add space for sliders (2 sliders)
        slider_space = 80 * 1  # Each slider needs about 80px
        
        # Add space for toggles (2 toggles)
        toggle_space = 50 * 2  # Each toggle needs about 50px
        
        return int(self.padding * 2 + lines * self.line_height + slider_space + toggle_space)

    def draw(self, surface, font, game_state):
        """
        Draw the info panel on the screen.

        Args:
            surface: pygame.Surface to draw on
            font: pygame.font.Font for rendering text
            game_state: Dictionary containing current game state information
        """
        if not self.visible:
            return

        # Extract game state
        is_visualizing = game_state.get('is_visualizing', False)
        current_terrain = game_state.get('current_terrain', 'grass')
        debug_mode = game_state.get('debug_mode', False)
        current_path = game_state.get('current_path', None)
        terrain = game_state.get('terrain', {})

        # Calculate panel height
        panel_height = self._calculate_panel_height()

        # Create semi-transparent background surface
        panel_surface = pygame.Surface((self.width, panel_height), pygame.SRCALPHA)
        
        # Draw background with alpha
        bg_rect = pygame.Rect(0, 0, self.width, panel_height)
        pygame.draw.rect(panel_surface, (*self.bg_color, self.bg_alpha), bg_rect, border_radius=self.border_radius)
        
        # Draw border
        pygame.draw.rect(panel_surface, self.border_color, bg_rect, width=self.border_width, border_radius=self.border_radius)

        # Render text content
        y_offset = self.padding
        
        # === STATUS SECTION ===
        header_surface = font.render("AI CONTROLS", True, self.header_color)
        panel_surface.blit(header_surface, (self.padding, y_offset))
        y_offset += self.line_height
        
        # Status
        if is_visualizing:
            status_text = "RUNNING"
            status_color = self.status_running_color
        else:
            status_text = "IDLE"
            status_color = self.status_idle_color
        
        status_surface = font.render(status_text, True, status_color)
        panel_surface.blit(status_surface, (self.padding + 10, y_offset))
        y_offset += self.line_height
        
        # Controls hint
        item_surface = font.render("  SPACE: Run/Pause A*", True, self.text_color)
        panel_surface.blit(item_surface, (self.padding + 5, y_offset))
        y_offset += self.line_height + 5
        
        # Only show full content if settings are expanded
        if self.settings_expanded:
            # === A* STATS SECTION ===
            header_surface = font.render("A* STATS", True, self.header_color)
            panel_surface.blit(header_surface, (self.padding, y_offset))
            y_offset += self.line_height
            
            # Calculate and display terrain statistics if path exists
            if current_path and len(current_path) > 1:
                from astar_game.config import TERRAIN_COSTS, TERRAIN_GRASS, TERRAIN_WATER, TERRAIN_MUD, TERRAIN_WALL
                import math
                
                # Calculate path cost and terrain breakdown
                path_cost = 0.0
                terrain_counts = {TERRAIN_GRASS: 0, TERRAIN_WATER: 0, TERRAIN_MUD: 0, TERRAIN_WALL: 0}
                terrain_costs_breakdown = {TERRAIN_GRASS: 0.0, TERRAIN_WATER: 0.0, TERRAIN_MUD: 0.0, TERRAIN_WALL: 0.0}
                
                for i in range(len(current_path) - 1):
                    r1, c1 = current_path[i]
                    r2, c2 = current_path[i + 1]
                    dr = abs(r2 - r1)
                    dc = abs(c2 - c1)
                    is_diagonal = dr == 1 and dc == 1
                    base_cost = math.sqrt(2) if is_diagonal else 1.0
                    terrain_type = terrain.get(current_path[i + 1], TERRAIN_GRASS)
                    terrain_multiplier = TERRAIN_COSTS.get(terrain_type, 1.0)
                    step_cost = base_cost * terrain_multiplier
                    path_cost += step_cost
                    
                    if terrain_type in terrain_counts:
                        terrain_counts[terrain_type] += 1
                        terrain_costs_breakdown[terrain_type] += step_cost
                
                # Display total path cost
                cost_text = f"  Total Cost: {path_cost:.2f}"
                cost_surface = font.render(cost_text, True, self.text_color)
                panel_surface.blit(cost_surface, (self.padding + 5, y_offset))
                y_offset += self.line_height
                
                # Display terrain breakdown
                terrain_names = {
                    TERRAIN_GRASS: "Grass",
                    TERRAIN_WATER: "Water",
                    TERRAIN_MUD: "Mud",
                    TERRAIN_WALL: "Wall"
                }
                
                for terrain_type in [TERRAIN_GRASS, TERRAIN_WATER, TERRAIN_MUD, TERRAIN_WALL]:
                    count = terrain_counts.get(terrain_type, 0)
                    cost = terrain_costs_breakdown.get(terrain_type, 0.0)
                    if count > 0:
                        terrain_name = terrain_names.get(terrain_type, "Unknown")
                        terrain_text = f"  {terrain_name}: {count} ({cost:.1f})"
                        terrain_surface = font.render(terrain_text, True, self.text_color)
                        panel_surface.blit(terrain_surface, (self.padding + 5, y_offset))
                        y_offset += self.line_height
            else:
                # No path available
                no_path_surface = font.render("  No path", True, self.status_idle_color)
                panel_surface.blit(no_path_surface, (self.padding + 5, y_offset))
                y_offset += self.line_height
            
            y_offset += 5
            
            # === CONTROLS SECTION ===
            header_surface = font.render("CONTROLS", True, self.header_color)
            panel_surface.blit(header_surface, (self.padding, y_offset))
            y_offset += self.line_height
            
            terrain_names = {
                'grass': 'Grass',
                'water': 'Water',
                'mud': 'Mud',
                'wall': 'Wall'
            }
            terrain_display = terrain_names.get(current_terrain, 'Grass')
            
            controls = [
                f"1-4: Terrain ({terrain_display})",
                "LMB: Place Terrain",
                "RMB: Set Target",
                "R: Regenerate Map",
                f"D: Debug {'ON' if debug_mode else 'OFF'}",
                "I: Toggle This Panel",
            ]
            
            for control in controls:
                item_surface = font.render(f"  {control}", True, self.text_color)
                panel_surface.blit(item_surface, (self.padding + 5, y_offset))
                y_offset += self.line_height
            
            y_offset += 10
        
        # === SETTINGS SECTION WITH TOGGLE ===
        # Draw settings header with toggle button
        header_surface = font.render("SETTINGS", True, self.header_color)
        panel_surface.blit(header_surface, (self.padding, y_offset))
        
        # Draw arrow indicator
        arrow_text = "▼" if self.settings_expanded else "▲"
        arrow_surface = font.render(arrow_text, True, self.text_color)
        
        y_offset += self.line_height + 5
        
        # Blit the panel surface to the main surface first
        surface.blit(panel_surface, (self.x, self.y))
        
        # Only draw UI components if settings are expanded
        if self.settings_expanded:
            # Now draw UI components directly on the main surface at adjusted positions
            if self.viz_speed_slider:
                y_offset += self.line_height + 5
                # Position sliders inside the panel
                slider_x = self.x + self.padding + 5
                slider_y = self.y + y_offset
                
                # Temporarily adjust slider position
                original_x = self.viz_speed_slider.x
                original_y = self.viz_speed_slider.y
                self.viz_speed_slider.x = slider_x
                self.viz_speed_slider.y = slider_y
                
                self.viz_speed_slider.draw(surface, font)
                
                # Restore original position (for hit detection)
                self.viz_speed_slider.x = slider_x
                self.viz_speed_slider.y = slider_y
                
                y_offset += 60
            

            
            if self.diagonal_toggle:
                toggle_x = self.x + self.padding + 5
                toggle_y = self.y + y_offset
                
                original_x = self.diagonal_toggle.x
                original_y = self.diagonal_toggle.y
                self.diagonal_toggle.x = toggle_x
                self.diagonal_toggle.y = toggle_y
                
                self.diagonal_toggle.draw(surface, font)
                
                self.diagonal_toggle.x = toggle_x
                self.diagonal_toggle.y = toggle_y
                
                y_offset += 70
            
            if self.overlay_toggle:
                toggle_x = self.x + self.padding + 5
                toggle_y = self.y + y_offset
                
                original_x = self.overlay_toggle.x
                original_y = self.overlay_toggle.y
                self.overlay_toggle.x = toggle_x
                self.overlay_toggle.y = toggle_y
                
                self.overlay_toggle.draw(surface, font)
                
                self.overlay_toggle.x = toggle_x
                self.overlay_toggle.y = toggle_y

