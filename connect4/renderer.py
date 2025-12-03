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


def draw_debug_panel(screen, font, state, debug_mode=False, debug_stats=None, theme=None):
    """
    Draw the debug panel showing MCTS win rates for each column.

    Arguments:
        screen: Pygame surface
        font: Pygame font object
        state: Current Connect4State
        debug_mode: Boolean indicating if debug mode is enabled
        debug_stats: Tuple (player1_rates, player2_rates, overall_rates) from get_mcts_win_rates
        theme: Theme object (uses current_theme if None)
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

    subtitle_text = font.render("Win Rates (%)", True, theme.text_color)
    screen.blit(subtitle_text, (panel_x + 10, 60))

    if debug_stats is None:
        no_data_text = font.render("Press D to", True, theme.text_color)
        screen.blit(no_data_text, (panel_x + 10, 85))
        no_data_text2 = font.render("calculate", True, theme.text_color)
        screen.blit(no_data_text2, (panel_x + 10, 110))
        return

    player1_rates, player2_rates, overall_rates = debug_stats
    overall_p1, overall_p2 = overall_rates

    # Draw legend
    legend_y = 85
    legend_font = pygame.font.SysFont("arial", 16)
    # Player 1 legend
    pygame.draw.rect(screen, theme.player1_color, (panel_x + 10, legend_y, 15, 15))
    p1_legend = legend_font.render("P1", True, theme.text_color)
    screen.blit(p1_legend, (panel_x + 30, legend_y))

    # Player 2 legend
    pygame.draw.rect(screen, theme.player2_color, (panel_x + 70, legend_y, 15, 15))
    p2_legend = legend_font.render("P2", True, theme.text_color)
    screen.blit(p2_legend, (panel_x + 90, legend_y))

    # Draw overall winning percentage
    overall_y = 110
    overall_title_font = pygame.font.SysFont("arial", 18)
    overall_title = overall_title_font.render(
        "Overall Win Rate:", True, theme.text_color)
    screen.blit(overall_title, (panel_x + 10, overall_y))

    # Normalize overall rates to ensure they total 100%
    total_overall = overall_p1 + overall_p2
    if total_overall > 0:
        overall_p1_norm = (overall_p1 / total_overall) * 100.0
        overall_p2_norm = (overall_p2 / total_overall) * 100.0
    else:
        overall_p1_norm = 50.0
        overall_p2_norm = 50.0

    # Draw overall stacked bar
    overall_bar_y = overall_y + 25
    overall_bar_height = 30
    overall_bar_width = 300

    # Calculate bar widths
    p1_overall_width = int((overall_p1_norm / 100.0) * overall_bar_width)
    p2_overall_width = overall_bar_width - p1_overall_width

    # Draw background
    pygame.draw.rect(screen, (50, 50, 50), (panel_x + 10,
                     overall_bar_y, overall_bar_width, overall_bar_height))

    # Draw Player 1 segment
    if p1_overall_width > 0:
        pygame.draw.rect(screen, theme.player1_color, (panel_x + 10,
                         overall_bar_y, p1_overall_width, overall_bar_height))

    # Draw Player 2 segment
    if p2_overall_width > 0:
        pygame.draw.rect(screen, theme.player2_color, (panel_x + 10 + p1_overall_width,
                         overall_bar_y, p2_overall_width, overall_bar_height))

    # Draw percentage labels
    overall_label_font = pygame.font.SysFont("arial", 18)
    if p1_overall_width > 40:
        p1_overall_text = overall_label_font.render(
            f"{overall_p1_norm:.1f}%", True, (255, 255, 255))
        text_x = panel_x + 10 + p1_overall_width // 2 - p1_overall_text.get_width() // 2
        screen.blit(p1_overall_text, (text_x, overall_bar_y + 5))

    if p2_overall_width > 40:
        p2_overall_text = overall_label_font.render(
            f"{overall_p2_norm:.1f}%", True, (0, 0, 0))
        text_x = panel_x + 10 + p1_overall_width + \
            p2_overall_width // 2 - p2_overall_text.get_width() // 2
        screen.blit(p2_overall_text, (text_x, overall_bar_y + 5))

    # Draw total percentage
    total_text = overall_label_font.render("100%", True, theme.text_color)
    screen.blit(total_text, (panel_x + 10 +
                overall_bar_width + 10, overall_bar_y + 5))

    # Draw for each column
    y_start = overall_bar_y + overall_bar_height + 15
    bar_height = 25
    bar_spacing = 50
    bar_width = 300

    for col in range(COLS):
        y_pos = y_start + col * bar_spacing

        # Column label
        col_text = font.render(f"Col {col}:", True, theme.text_color)
        screen.blit(col_text, (panel_x + 10, y_pos))

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

        # Calculate bar widths based on normalized percentages
        p1_bar_width = int((p1_normalized / 100.0) * bar_width)
        p2_bar_width = int((p2_normalized / 100.0) * bar_width)

        # Ensure they fill the entire bar width
        if p1_bar_width + p2_bar_width < bar_width:
            p2_bar_width = bar_width - p1_bar_width

        # Draw background bar
        pygame.draw.rect(screen, (50, 50, 50), (panel_x + 60,
                         y_pos, bar_width, bar_height))

        # Draw Player 1 segment (left side)
        if p1_bar_width > 0:
            pygame.draw.rect(screen, theme.player1_color, (panel_x + 60,
                             y_pos, p1_bar_width, bar_height))

        # Draw Player 2 segment (right side) - stacked after P1
        if p2_bar_width > 0:
            pygame.draw.rect(screen, theme.player2_color, (panel_x + 60 + p1_bar_width,
                             y_pos, p2_bar_width, bar_height))

        # Draw percentage labels on the bar segments
        if p1_bar_width > 30:  # Only show text if segment is wide enough
            p1_text = font.render(
                f"{p1_normalized:.1f}%", True, (255, 255, 255))
            text_x = panel_x + 60 + p1_bar_width // 2 - p1_text.get_width() // 2
            screen.blit(p1_text, (text_x, y_pos + 3))

        if p2_bar_width > 30:  # Only show text if segment is wide enough
            p2_text = font.render(f"{p2_normalized:.1f}%", True, (0, 0, 0))
            text_x = panel_x + 60 + p1_bar_width + \
                p2_bar_width // 2 - p2_text.get_width() // 2
            screen.blit(p2_text, (text_x, y_pos + 3))

        # Draw total percentage at the end
        total_text = font.render("100%", True, theme.text_color)
        screen.blit(total_text, (panel_x + 60 + bar_width + 10, y_pos + 3))


def draw_menu(screen, font, theme=None):
    """
    Draw the menu screen for selecting game mode.

    Arguments:
        screen: the Pygame surface where we draw
        font: a Pygame font object for rendering text
        theme: Theme object (uses current_theme if None)
    """
    if theme is None:
        theme = current_theme
    
    screen.fill(theme.bg_color)

    # Title
    title_font = pygame.font.SysFont("arial", 36)
    title_text = title_font.render("Connect 4 - MCTS", True, theme.text_color)
    title_rect = title_text.get_rect(center=(BOARD_WIDTH // 2, HEIGHT // 4))
    screen.blit(title_text, title_rect)

    # Menu options
    menu_options = [
        "1. Human vs AI",
        "2. AI vs AI",
        "3. Human vs Human",
        "4. Time Attack"
    ]

    y_offset = HEIGHT // 2
    for i, option in enumerate(menu_options):
        option_text = font.render(option, True, theme.text_color)
        option_rect = option_text.get_rect(
            center=(BOARD_WIDTH // 2, y_offset + i * 50))
        screen.blit(option_text, option_rect)

    # Theme display
    theme_text = font.render(f"Theme: {theme.name} (Press T to change)", True, theme.text_color)
    theme_rect = theme_text.get_rect(
        center=(BOARD_WIDTH // 2, HEIGHT - 150))
    screen.blit(theme_text, theme_rect)

    # Instructions
    instruction_text = font.render(
        "Press 1-4 to select a mode", True, theme.text_color)
    instruction_rect = instruction_text.get_rect(
        center=(BOARD_WIDTH // 2, HEIGHT - 100))
    screen.blit(instruction_text, instruction_rect)

    # Clear debug panel area
    pygame.draw.rect(screen, theme.bg_color, (BOARD_WIDTH,
                     0, DEBUG_PANEL_WIDTH, HEIGHT))

    pygame.display.update()


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
    
    # Fill the screen with background color
    screen.fill(theme.bg_color)

    # Draw message area at the top
    text_surface = font.render(message, True, theme.text_color)
    screen.blit(text_surface, (10, 5))

    # Draw hint marker if we have a suggested column
    if hint_col is not None:
        x_center = hint_col * SQUARESIZE + SQUARESIZE // 2
        pygame.draw.circle(
            screen,
            theme.hint_color,
            (x_center, SQUARESIZE),
            RADIUS // 2,
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

