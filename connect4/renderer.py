"""
Rendering functions for Connect 4 game using Pygame.

This module contains all pygame drawing functions including:
- Board rendering
- Menu screen
- Debug panel with MCTS statistics
- Win animations
- Timer display
"""

import pygame
import math
from .config import (
    BOARD_WIDTH, DEBUG_PANEL_WIDTH, HEIGHT, SQUARESIZE, RADIUS,
    ROWS, COLS, PLAYER1, PLAYER2, current_theme
)
from .button import Button
from .state import Connect4State

def draw_debug_panel(screen, font, state: Connect4State, debug_mode=False, debug_stats=None, theme=None, last_ai_move=None, last_ai_stats=None):
    """
    Draw the debug panel showing MCTS win rates for each column and AI move selection.

    Arguments:
        screen: Pygame surface
        font: Pygame font object
        state: Current Connect4State
        debug_mode: Boolean indicating if debug mode is enabled
        debug_stats: Tuple (player1_rates, player2_rates, overall_rates) from get_mcts_win_rates
        theme: Theme object (uses current_theme if None)
        last_ai_move: The column index of the last AI move (for highlighting)
        last_ai_stats: Dict with analytics about the AI's move decision
                      Keys: 'selected_col', 'visits', 'win_rate', 'total_simulations', 'all_moves'
    """
    if theme is None:
        theme = current_theme
    
    panel_x = BOARD_WIDTH
    panel_y = 0
    panel_width = DEBUG_PANEL_WIDTH
    panel_height = HEIGHT

    # Draw panel background
    pygame.draw.rect(screen, (30, 30, 30),
                     (panel_x, panel_y, panel_width, panel_height))

    # Title with status
    title_font = pygame.font.SysFont("arial", 20)
    status_text = "ON" if debug_mode else "OFF"
    status_color = (0, 255, 0) if debug_mode else (255, 100, 100)
    title_text = title_font.render("DEBUG MODE", True, theme.accent_color)
    screen.blit(title_text, (panel_x + 10, 10))
    status_text_surface = title_font.render(
        f"Status: {status_text}", True, status_color)
    screen.blit(status_text_surface, (panel_x + 10, 35))

    # If debug mode is off, show instructions and return
    if not debug_mode:
        subtitle_text = font.render("Press D to enable", True, theme.text_color)
        screen.blit(subtitle_text, (panel_x + 10, 60))
        return

    # Y offset for content
    y_offset = 60
    
    # === AI Move Selection Section ===
    if last_ai_stats is not None:
        section_font = pygame.font.SysFont("arial", 18, bold=True)
        ai_section_text = section_font.render("AI MOVE ANALYSIS", True, (100, 200, 255))
        screen.blit(ai_section_text, (panel_x + 10, y_offset))
        y_offset += 25
        
        selected_col = last_ai_stats.get('selected_col')
        visits = last_ai_stats.get('visits', 0)
        win_rate = last_ai_stats.get('win_rate', 0.0)
        total_sims = last_ai_stats.get('total_simulations', 0)
        all_moves = last_ai_stats.get('all_moves', {})
        
        # Selected move highlight box
        if selected_col is not None:
            highlight_color = (50, 150, 50)  # Green highlight
            pygame.draw.rect(screen, highlight_color, 
                           (panel_x + 5, y_offset - 2, panel_width - 10, 45), 
                           border_radius=5)
            pygame.draw.rect(screen, (100, 255, 100), 
                           (panel_x + 5, y_offset - 2, panel_width - 10, 45), 
                           width=2, border_radius=5)
            
            # Selected move text
            selected_font = pygame.font.SysFont("arial", 16)
            selected_text = selected_font.render(
                f"✓ SELECTED: Column {selected_col}", True, (255, 255, 255))
            screen.blit(selected_text, (panel_x + 15, y_offset + 2))
            
            # Stats for selected move
            stats_text = selected_font.render(
                f"Win Rate: {win_rate:.1f}%  |  Visits: {visits}", True, (200, 255, 200))
            screen.blit(stats_text, (panel_x + 15, y_offset + 22))
            y_offset += 50
        
        # Total simulations
        sim_font = pygame.font.SysFont("arial", 14)
        sim_text = sim_font.render(f"Total Simulations: {total_sims}", True, theme.text_color)
        screen.blit(sim_text, (panel_x + 10, y_offset))
        y_offset += 22
        
        # All considered moves with comparison
        if all_moves:
            moves_title = sim_font.render("All Moves Considered:", True, theme.text_color)
            screen.blit(moves_title, (panel_x + 10, y_offset))
            y_offset += 20
            
            # Sort by visits descending
            sorted_moves = sorted(all_moves.items(), key=lambda x: x[1]['visits'], reverse=True)
            
            for col, stats in sorted_moves:
                is_selected = (col == selected_col)
                mv_visits = stats.get('visits', 0)
                mv_win_rate = stats.get('win_rate', 0.0)
                mv_ucb = stats.get('ucb_score', 0.0)
                
                # Color coding: selected = green, others = gray
                if is_selected:
                    text_color = (100, 255, 100)
                    prefix = "► "
                else:
                    text_color = (180, 180, 180)
                    prefix = "  "
                
                # Format UCB score (handle infinity)
                if mv_ucb == float('inf'):
                    ucb_str = "∞"
                else:
                    ucb_str = f"{mv_ucb:.3f}"
                
                move_text = sim_font.render(
                    f"{prefix}Col {col}: {mv_win_rate:.1f}% | UCB: {ucb_str} ({mv_visits})", 
                    True, text_color)
                screen.blit(move_text, (panel_x + 15, y_offset))
                y_offset += 18
            
            y_offset += 10
        
        # Separator line
        pygame.draw.line(screen, (80, 80, 80), 
                        (panel_x + 10, y_offset), 
                        (panel_x + panel_width - 10, y_offset), 2)
        y_offset += 15
        
        # === Vertical Bar Chart from AI Stats ===
        # If we have AI stats but no debug_stats (AI vs AI mode), show vertical bars
        if all_moves and debug_stats is None:
            # Title for the vertical bar chart
            chart_title_font = pygame.font.SysFont("arial", 14, bold=True)
            chart_title = chart_title_font.render("Column Win Rates:", True, theme.text_color)
            screen.blit(chart_title, (panel_x + 10, y_offset))
            y_offset += 22

            # Vertical bar chart settings
            max_bar_height = 180  # Maximum height for bars
            bar_width_per_col = 30  # Width of each vertical bar
            bar_spacing = 8  # Space between bars
            chart_start_x = panel_x + 15
            chart_start_y = y_offset + max_bar_height + 5  # Bottom of the chart
            
            # Determine which player made the last move (whose stats we're showing)
            # The stats are from the perspective of the player who JUST moved
            # state.current_player is the NEXT player to move, so the last player is the opposite
            if state.current_player == PLAYER1:
                last_moving_player = PLAYER2
            else:
                last_moving_player = PLAYER1
            
            # Draw all columns in order (0 to COLS-1)
            for col in range(COLS):
                # Get win rate for this column from all_moves
                col_stats = all_moves.get(col)
                
                if col_stats:
                    win_rate = col_stats.get('win_rate', 50.0)
                    # Win rate is from the last moving player's perspective
                    # For visualization: last moving player's win rate vs opponent's win rate
                    moving_player_rate = win_rate
                    opponent_rate = 100.0 - win_rate
                else:
                    # Column not explored (illegal move)
                    moving_player_rate = 0.0
                    opponent_rate = 0.0

                # Calculate bar heights based on normalized percentages
                moving_player_height = int((moving_player_rate / 100.0) * max_bar_height)
                opponent_height = int((opponent_rate / 100.0) * max_bar_height)

                # X position for this column's bar
                bar_x = chart_start_x + col * (bar_width_per_col + bar_spacing)
                
                # Highlight selected column with background
                if selected_col is not None and col == selected_col:
                    highlight_rect = pygame.Rect(
                        bar_x - 3, 
                        chart_start_y - max_bar_height - 20,
                        bar_width_per_col + 6,
                        max_bar_height + 40
                    )
                    pygame.draw.rect(screen, (50, 100, 50), highlight_rect, border_radius=5)
                    pygame.draw.rect(screen, (100, 200, 100), highlight_rect, width=2, border_radius=5)

                # Draw background bar (gray)
                pygame.draw.rect(screen, (50, 50, 50), 
                               (bar_x, chart_start_y - max_bar_height, 
                                bar_width_per_col, max_bar_height))

                # Determine colors based on who made the last move
                # The win rates are from the last moving player's perspective
                moving_player_color = theme.player1_color if last_moving_player == PLAYER1 else theme.player2_color
                opponent_color = theme.player2_color if last_moving_player == PLAYER1 else theme.player1_color

                # Draw moving player segment (bottom, stacked from bottom)
                if moving_player_height > 0:
                    pygame.draw.rect(screen, moving_player_color, 
                                   (bar_x, chart_start_y - moving_player_height, 
                                    bar_width_per_col, moving_player_height))

                # Draw opponent segment (top, stacked above moving player)
                if opponent_height > 0:
                    pygame.draw.rect(screen, opponent_color, 
                                   (bar_x, chart_start_y - moving_player_height - opponent_height, 
                                    bar_width_per_col, opponent_height))

                # Draw column label below the bar
                col_font = pygame.font.SysFont("arial", 12, bold=True)
                col_text = col_font.render(f"{col}", True, theme.text_color)
                col_text_rect = col_text.get_rect(center=(bar_x + bar_width_per_col // 2, chart_start_y + 12))
                screen.blit(col_text, col_text_rect)
                
                # Draw percentage labels on bars if there's enough space
                label_font = pygame.font.SysFont("arial", 10)
                
                # Opponent label (top segment)
                if opponent_height > 20:
                    opponent_text = label_font.render(f"{opponent_rate:.0f}%", True, (0, 0, 0))
                    opponent_text_rect = opponent_text.get_rect(
                        center=(bar_x + bar_width_per_col // 2, 
                               chart_start_y - moving_player_height - opponent_height // 2))
                    screen.blit(opponent_text, opponent_text_rect)
                
                # Moving player label (bottom segment)
                if moving_player_height > 20:
                    moving_text = label_font.render(f"{moving_player_rate:.0f}%", True, (255, 255, 255))
                    moving_text_rect = moving_text.get_rect(
                        center=(bar_x + bar_width_per_col // 2, 
                               chart_start_y - moving_player_height // 2))
                    screen.blit(moving_text, moving_text_rect)

            # Update y_offset to account for the vertical chart
            y_offset = chart_start_y + 25


    # === Win Rates Section ===
    # Only show this section if debug_stats is available (e.g., Human vs AI mode)
    # In AI vs AI mode, we skip this to avoid expensive recalculations
    if debug_stats is not None:
        subtitle_text = font.render("Win Rates Analysis", True, theme.text_color)
        screen.blit(subtitle_text, (panel_x + 10, y_offset))
        y_offset += 25

        player1_rates, player2_rates, overall_rates = debug_stats
        overall_p1, overall_p2 = overall_rates

        # Draw legend
        legend_y = y_offset
        legend_font = pygame.font.SysFont("arial", 14)
        # Player 1 legend
        pygame.draw.rect(screen, theme.player1_color, (panel_x + 10, legend_y, 12, 12))
        p1_legend = legend_font.render("P1", True, theme.text_color)
        screen.blit(p1_legend, (panel_x + 26, legend_y - 2))

        # Player 2 legend
        pygame.draw.rect(screen, theme.player2_color, (panel_x + 60, legend_y, 12, 12))
        p2_legend = legend_font.render("P2", True, theme.text_color)
        screen.blit(p2_legend, (panel_x + 76, legend_y - 2))
        y_offset += 20

        # Draw overall winning percentage
        overall_title_font = pygame.font.SysFont("arial", 14)
        overall_title = overall_title_font.render(
            "Overall:", True, theme.text_color)
        screen.blit(overall_title, (panel_x + 10, y_offset))

        # Normalize overall rates to ensure they total 100%
        total_overall = overall_p1 + overall_p2
        if total_overall > 0:
            overall_p1_norm = (overall_p1 / total_overall) * 100.0
            overall_p2_norm = (overall_p2 / total_overall) * 100.0
        else:
            overall_p1_norm = 50.0
            overall_p2_norm = 50.0

        # Draw overall stacked bar
        overall_bar_y = y_offset
        overall_bar_height = 18
        bar_width = panel_width - 90

        # Calculate bar widths
        p1_overall_width = int((overall_p1_norm / 100.0) * bar_width)
        p2_overall_width = bar_width - p1_overall_width

        # Draw background
        pygame.draw.rect(screen, (50, 50, 50), (panel_x + 60,
                         overall_bar_y, bar_width, overall_bar_height))

        # Draw Player 1 segment
        if p1_overall_width > 0:
            pygame.draw.rect(screen, theme.player1_color, (panel_x + 60,
                             overall_bar_y, p1_overall_width, overall_bar_height))

        # Draw Player 2 segment
        if p2_overall_width > 0:
            pygame.draw.rect(screen, theme.player2_color, (panel_x + 60 + p1_overall_width,
                             overall_bar_y, p2_overall_width, overall_bar_height))

        # Draw percentage labels
        bar_label_font = pygame.font.SysFont("arial", 12)
        if p1_overall_width > 35:
            p1_overall_text = bar_label_font.render(
                f"{overall_p1_norm:.0f}%", True, (255, 255, 255))
            text_x = panel_x + 60 + p1_overall_width // 2 - p1_overall_text.get_width() // 2
            screen.blit(p1_overall_text, (text_x, overall_bar_y + 1))

        if p2_overall_width > 35:
            p2_overall_text = bar_label_font.render(
                f"{overall_p2_norm:.0f}%", True, (0, 0, 0))
            text_x = panel_x + 60 + p1_overall_width + \
                p2_overall_width // 2 - p2_overall_text.get_width() // 2
            screen.blit(p2_overall_text, (text_x, overall_bar_y + 1))

        y_offset += overall_bar_height + 10

        # Draw vertical bars for each column (ordered by index)
        # Title for the vertical bar chart
        chart_title_font = pygame.font.SysFont("arial", 14, bold=True)
        chart_title = chart_title_font.render("Column Win Rates:", True, theme.text_color)
        screen.blit(chart_title, (panel_x + 10, y_offset))
        y_offset += 22

        # Vertical bar chart settings
        max_bar_height = 180  # Maximum height for bars
        bar_width_per_col = 30  # Width of each vertical bar
        bar_spacing = 8  # Space between bars
        chart_start_x = panel_x + 15
        chart_start_y = y_offset + max_bar_height + 5  # Bottom of the chart
        
        # Draw all columns in order (0 to COLS-1)
        for col in range(COLS):
            # Get rates for this column
            p1_rate = player1_rates.get(col, 0.0)
            p2_rate = player2_rates.get(col, 0.0)

            # Normalize to ensure they total 100%
            total_rate = p1_rate + p2_rate
            if total_rate > 0:
                p1_normalized = (p1_rate / total_rate) * 100.0
                p2_normalized = (p2_rate / total_rate) * 100.0
            else:
                p1_normalized = 50.0
                p2_normalized = 50.0

            # Calculate bar heights based on normalized percentages
            p1_bar_height = int((p1_normalized / 100.0) * max_bar_height)
            p2_bar_height = int((p2_normalized / 100.0) * max_bar_height)

            # X position for this column's bar
            bar_x = chart_start_x + col * (bar_width_per_col + bar_spacing)
            
            # Highlight selected column with background
            if last_ai_move is not None and col == last_ai_move:
                highlight_rect = pygame.Rect(
                    bar_x - 3, 
                    chart_start_y - max_bar_height - 20,
                    bar_width_per_col + 6,
                    max_bar_height + 40
                )
                pygame.draw.rect(screen, (50, 100, 50), highlight_rect, border_radius=5)
                pygame.draw.rect(screen, (100, 200, 100), highlight_rect, width=2, border_radius=5)

            # Draw background bar (gray)
            pygame.draw.rect(screen, (50, 50, 50), 
                           (bar_x, chart_start_y - max_bar_height, 
                            bar_width_per_col, max_bar_height))

            # Draw Player 1 segment (bottom, stacked from bottom)
            if p1_bar_height > 0:
                pygame.draw.rect(screen, theme.player1_color, 
                               (bar_x, chart_start_y - p1_bar_height, 
                                bar_width_per_col, p1_bar_height))

            # Draw Player 2 segment (top, stacked above P1)
            if p2_bar_height > 0:
                pygame.draw.rect(screen, theme.player2_color, 
                               (bar_x, chart_start_y - p1_bar_height - p2_bar_height, 
                                bar_width_per_col, p2_bar_height))

            # Draw column label below the bar
            col_font = pygame.font.SysFont("arial", 12, bold=True)
            col_text = col_font.render(f"{col}", True, theme.text_color)
            col_text_rect = col_text.get_rect(center=(bar_x + bar_width_per_col // 2, chart_start_y + 12))
            screen.blit(col_text, col_text_rect)
            
            # Draw percentage labels on bars if there's enough space
            label_font = pygame.font.SysFont("arial", 10)
            
            # P2 label (top segment)
            if p2_bar_height > 20:
                p2_text = label_font.render(f"{p2_normalized:.0f}%", True, (0, 0, 0))
                p2_text_rect = p2_text.get_rect(
                    center=(bar_x + bar_width_per_col // 2, 
                           chart_start_y - p1_bar_height - p2_bar_height // 2))
                screen.blit(p2_text, p2_text_rect)
            
            # P1 label (bottom segment)
            if p1_bar_height > 20:
                p1_text = label_font.render(f"{p1_normalized:.0f}%", True, (255, 255, 255))
                p1_text_rect = p1_text.get_rect(
                    center=(bar_x + bar_width_per_col // 2, 
                           chart_start_y - p1_bar_height // 2))
                screen.blit(p1_text, p1_text_rect)

        # Update y_offset to account for the vertical chart
        y_offset = chart_start_y + 25


def draw_menu(screen, font, theme=None, mouse_pos=(0, 0)):
    """
    Draw the menu screen for selecting game mode with interactive buttons.

    Arguments:
        screen: the Pygame surface where we draw
        font: a Pygame font object for rendering text
        theme: Theme object (uses current_theme if None)
        mouse_pos: Current mouse position for hover effects
        
    Returns:
        Dictionary mapping button names to Button instances
    """
    if theme is None:
        theme = current_theme
    
    # Draw gradient background if theme supports it
    if theme.bg_gradient_top and theme.bg_gradient_bottom:
        for y in range(HEIGHT):
            # Interpolate between top and bottom colors
            ratio = y / HEIGHT
            color = tuple(
                int(theme.bg_gradient_top[i] + (theme.bg_gradient_bottom[i] - theme.bg_gradient_top[i]) * ratio)
                for i in range(3)
            )
            pygame.draw.line(screen, color, (0, y), (BOARD_WIDTH, y))
    else:
        screen.fill(theme.bg_color)

    # Title with shadow effect
    title_font = pygame.font.SysFont("arial", 48, bold=True)
    
    # Title shadow
    title_shadow = title_font.render("Connect 4 - MCTS", True, (0, 0, 0))
    title_shadow_rect = title_shadow.get_rect(center=(BOARD_WIDTH // 2 + 3, HEIGHT // 6 + 3))
    screen.blit(title_shadow, title_shadow_rect)
    
    # Main title
    title_text = title_font.render("Connect 4 - MCTS", True, theme.accent_color)
    title_rect = title_text.get_rect(center=(BOARD_WIDTH // 2, HEIGHT // 6))
    screen.blit(title_text, title_rect)

    # Subtitle
    subtitle_font = pygame.font.SysFont("arial", 20)
    subtitle_text = subtitle_font.render("Select a Game Mode", True, theme.text_color)
    subtitle_rect = subtitle_text.get_rect(center=(BOARD_WIDTH // 2, HEIGHT // 6 + 60))
    screen.blit(subtitle_text, subtitle_rect)

    # Create buttons
    button_font = pygame.font.SysFont("arial", 24)
    button_width = 300
    button_height = 50
    button_x = (BOARD_WIDTH - button_width) // 2
    y_start = HEIGHT // 2 - 50
    button_spacing = 70

    buttons = {}
    
    # Game mode buttons with emojis
    mode_buttons = [
        ("human_vs_ai", "Human vs AI"),
        ("ai_vs_ai", "AI vs AI"),
        ("human_vs_human", "Human vs Human"),
        ("time_attack", "Time Attack")
    ]
    
    for i, (key, text) in enumerate(mode_buttons):
        y_pos = y_start + i * button_spacing
        button = Button(button_x, y_pos, button_width, button_height, 
                       text, button_font)
        button.update(mouse_pos)
        button.draw(screen, theme)
        buttons[key] = button
    
    # Theme button (smaller, at the bottom)
    theme_button_width = 250
    theme_button_height = 40
    theme_button_x = (BOARD_WIDTH - theme_button_width) // 2
    theme_button_y = HEIGHT - 120
    theme_button = Button(theme_button_x, theme_button_y, 
                         theme_button_width, theme_button_height,
                         f"Theme: {theme.name}", 
                         pygame.font.SysFont("arial", 20))
    theme_button.update(mouse_pos)
    theme_button.draw(screen, theme)
    buttons["theme"] = theme_button
    
    # Instructions
    instruction_font = pygame.font.SysFont("arial", 18)
    instruction_text = instruction_font.render(
        "Click a button to begin", True, theme.text_color)
    instruction_rect = instruction_text.get_rect(
        center=(BOARD_WIDTH // 2, HEIGHT - 60))
    screen.blit(instruction_text, instruction_rect)

    return buttons


def draw_board(screen, state, font, hint_col=None, message="", theme=None, winning_positions=None, animation_frame=0):
    """
    Draw the entire game screen.

    This includes:
    - A message text at the top (whose turn, winner, instructions).
    - A small hint marker at the top to show the suggested column.
    - The board with circular holes.
    - The pieces for both players.
    - Win animation if winning_positions is provided.

    Arguments:
        screen: the Pygame surface where we draw
        state: the Connect4State we want to display
        font:  a Pygame font object for rendering text
        hint_col: optional column index for the hint move
        message: text message to display at the top
        theme: Theme object (uses current_theme if None)
        winning_positions: list of (row, col) tuples for winning pieces
        animation_frame: frame number for win animation (0 = no animation)
    """
    if theme is None:
        theme = current_theme
    
    # Draw gradient background if theme supports it
    if theme.bg_gradient_top and theme.bg_gradient_bottom:
        for y in range(HEIGHT):
            # Interpolate between top and bottom colors
            ratio = y / HEIGHT
            color = tuple(
                int(theme.bg_gradient_top[i] + (theme.bg_gradient_bottom[i] - theme.bg_gradient_top[i]) * ratio)
                for i in range(3)
            )
            pygame.draw.line(screen, color, (0, y), (BOARD_WIDTH, y))
    else:
        screen.fill(theme.bg_color)

    # Draw message area at the top with background
    message_bg_rect = pygame.Rect(0, 0, BOARD_WIDTH, SQUARESIZE * 2)
    message_bg_surface = pygame.Surface((message_bg_rect.width, message_bg_rect.height), pygame.SRCALPHA)
    pygame.draw.rect(message_bg_surface, (*theme.bg_color, 180), message_bg_surface.get_rect())
    screen.blit(message_bg_surface, message_bg_rect)
    
    # Message text with shadow
    text_shadow = font.render(message, True, (0, 0, 0))
    screen.blit(text_shadow, (11, 6))
    text_surface = font.render(message, True, theme.text_color)
    screen.blit(text_surface, (10, 5))

    # Draw hint marker if we have a suggested column
    if hint_col is not None:
        x_center = hint_col * SQUARESIZE + SQUARESIZE // 2
        # Pulsing hint effect
        pulse = int(5 * math.sin(animation_frame * 0.2))
        pygame.draw.circle(
            screen,
            theme.hint_color,
            (x_center, SQUARESIZE),
            RADIUS // 2 + pulse,
        )

    # Draw board and empty holes
    for c in range(COLS):
        for r in range(ROWS):
            pygame.draw.rect(
                screen,
                theme.board_color,
                (
                    c * SQUARESIZE,
                    (r + 2) * SQUARESIZE,
                    SQUARESIZE,
                    SQUARESIZE,
                ),
            )
            pygame.draw.circle(
                screen,
                theme.bg_color,
                (
                    c * SQUARESIZE + SQUARESIZE // 2,
                    (r + 2) * SQUARESIZE + SQUARESIZE // 2,
                ),
                RADIUS,
            )

    # Draw pieces for player 1 and player 2
    for c in range(COLS):
        for r in range(ROWS):
            piece = state.board[r][c]
            if piece == PLAYER1:
                color = theme.player1_color
            elif piece == PLAYER2:
                color = theme.player2_color
            else:
                continue  # Skip empty cells
            
            center_x = c * SQUARESIZE + SQUARESIZE // 2
            center_y = (r + 2) * SQUARESIZE + SQUARESIZE // 2
            
            # Draw win animation glow if this is a winning piece
            if winning_positions and (r, c) in winning_positions:
                # Pulsing glow effect using sine wave
                glow_intensity = int(127 + 127 * math.sin(animation_frame * 0.3))
                # Create a brighter version of the piece color
                glow_color = tuple(min(255, c + glow_intensity // 2) for c in color)
                glow_radius = RADIUS + int(10 * math.sin(animation_frame * 0.3))
                # Draw glow behind piece
                pygame.draw.circle(screen, glow_color, (center_x, center_y), glow_radius)
            
            pygame.draw.circle(
                screen,
                color,
                (center_x, center_y),
                RADIUS,
            )

    # Note: Don't update display here - let the caller update after all drawing is done


def draw_timer(screen, font, player1_time, player2_time, current_player, theme=None):
    """
    Draw timer display for both players with color coding.
    
    Arguments:
        screen: Pygame surface
        font: Pygame font object
        player1_time: seconds remaining for player 1
        player2_time: seconds remaining for player 2
        current_player: PLAYER1 or PLAYER2
        theme: Theme object (uses current_theme if None)
    """
    if theme is None:
        theme = current_theme
    
    # Format time as MM:SS
    def format_time(seconds):
        minutes = int(seconds // 60)
        secs = int(seconds % 60)
        return f"{minutes:02d}:{secs:02d}"
    
    # Determine color based on time remaining
    def get_time_color(seconds):
        if seconds > 30:
            return (0, 255, 0)  # Green
        elif seconds > 10:
            return (255, 255, 0)  # Yellow
        else:
            return (255, 0, 0)  # Red
    
    # Draw player 1 timer
    p1_color = get_time_color(player1_time)
    p1_text = font.render(f"P1: {format_time(player1_time)}", True, p1_color)
    p1_x = BOARD_WIDTH // 2 - 150
    p1_y = 40
    
    # Highlight current player
    if current_player == PLAYER1:
        pygame.draw.rect(screen, theme.accent_color, (p1_x - 5, p1_y - 5, p1_text.get_width() + 10, p1_text.get_height() + 10), 2)
    
    screen.blit(p1_text, (p1_x, p1_y))
    
    # Draw player 2 timer
    p2_color = get_time_color(player2_time)
    p2_text = font.render(f"P2: {format_time(player2_time)}", True, p2_color)
    p2_x = BOARD_WIDTH // 2 + 50
    p2_y = 40
    
    # Highlight current player
    if current_player == PLAYER2:
        pygame.draw.rect(screen, theme.accent_color, (p2_x - 5, p2_y - 5, p2_text.get_width() + 10, p2_text.get_height() + 10), 2)
    
    screen.blit(p2_text, (p2_x, p2_y))


def draw_ai_controls(screen, font, ai_delay, is_paused, theme=None):
    """
    Draw AI vs AI control panel showing current delay and pause status.
    
    Arguments:
        screen: Pygame surface
        font: Pygame font object
        ai_delay: Current AI move delay in seconds
        is_paused: Boolean indicating if game is paused
        theme: Theme object (uses current_theme if None)
    """
    if theme is None:
        theme = current_theme
    
    # Position at bottom right of board
    panel_width = 280
    panel_height = 90
    panel_x = BOARD_WIDTH - panel_width - 10
    panel_y = HEIGHT - panel_height - 10
    
    # Draw panel background with transparency
    panel_surface = pygame.Surface((panel_width, panel_height), pygame.SRCALPHA)
    pygame.draw.rect(panel_surface, (*theme.board_color, 200), panel_surface.get_rect(), border_radius=10)
    screen.blit(panel_surface, (panel_x, panel_y))
    
    # Draw border
    pygame.draw.rect(screen, theme.accent_color, (panel_x, panel_y, panel_width, panel_height), 2, border_radius=10)
    
    # Title
    title_font = pygame.font.SysFont("arial", 14, bold=True)
    title_text = title_font.render("AI CONTROLS", True, theme.text_color)
    screen.blit(title_text, (panel_x + 10, panel_y + 8))
    
    # Pause status
    status_font = pygame.font.SysFont("arial", 13)
    if is_paused:
        status_text = status_font.render("⏸️  PAUSED", True, (255, 200, 0))
    else:
        status_text = status_font.render("▶️  RUNNING", True, (0, 255, 100))
    screen.blit(status_text, (panel_x + 10, panel_y + 28))
    
    # Delay display
    delay_text = status_font.render(f"Delay: {ai_delay:.1f}s", True, theme.text_color)
    screen.blit(delay_text, (panel_x + 10, panel_y + 48))
    
    # Controls hint
    hint_font = pygame.font.SysFont("arial", 11)
    hint1 = hint_font.render("SPACE: Pause/Resume", True, theme.text_color)
    hint2 = hint_font.render("↑↓: Adjust Delay", True, theme.text_color)
    screen.blit(hint1, (panel_x + 10, panel_y + 68))
    screen.blit(hint2, (panel_x + 160, panel_y + 68))


