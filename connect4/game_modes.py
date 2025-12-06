"""
Game mode implementations for Connect 4.

This module contains the game loop functions for each game mode:
- Human vs AI
- AI vs AI
- Human vs Human
"""

import pygame
import time
from .state import Connect4State
from .ai_agent import AIAgent
from .renderer import draw_board, draw_debug_panel, draw_timer
from .mcts import mcts_search, get_mcts_win_rates
from . import config
from .config import (
    BOARD_WIDTH, SQUARESIZE, FPS, HEIGHT, DEBUG_PANEL_WIDTH,
    PLAYER1, PLAYER2,
    AI_ITERATIONS_PLAYER1, AI_ITERATIONS_PLAYER2, AI_MOVE_DELAY,
    TIME_BANK_SECONDS, get_window_width
)


def run_human_vs_ai(screen, clock, font):
    """
    Run Human vs AI game mode.

    Human player (Player 1) makes moves via mouse clicks.
    AI agent (Player 2) makes moves automatically using MCTS.
    Press H for hint, D for debug, T for theme, R to restart, ESC to return to menu.
    """
    pygame.display.set_caption("MCTS Connect4 - Human vs AI")

    state = Connect4State()
    game_over = False
    hint_col = None
    message = "Your turn (Player 1) - Click to move, Press H for hint, D for debug, T for theme"
    winning_positions = []
    animation_frame = 0

    ai_agent = AIAgent(n_iter=AI_ITERATIONS_PLAYER2, player_id=PLAYER2)
    ai_thinking = False
    debug_mode = False
    debug_stats = None
    last_state_hash = None
    
    # Track last AI move and its statistics
    last_ai_move = None
    last_ai_stats = None

    def get_state_hash(s):
        """Create a hash of the current game state to detect changes."""
        return tuple(tuple(row) for row in s.board) + (s.current_player,)

    running = True
    while running:
        clock.tick(FPS)

        # Check if state changed and update debug stats if needed
        current_state_hash = get_state_hash(state)
        if debug_mode and current_state_hash != last_state_hash and not state.is_terminal():
            if debug_stats is None or last_state_hash is None:
                # Calculate stats for new state (keep old stats visible during calculation)
                new_debug_stats = get_mcts_win_rates(state, n_iter=600)
                debug_stats = new_debug_stats
            last_state_hash = current_state_hash

        # Handle AI turn
        if not game_over and not ai_thinking and state.current_player == PLAYER2:
            ai_thinking = True
            message = "AI thinking..."
            draw_board(screen, state, font, hint_col, message,
                       config.current_theme, winning_positions, animation_frame)
            if debug_mode:
                draw_debug_panel(screen, font, state, debug_mode,
                                 debug_stats, config.current_theme, last_ai_move, last_ai_stats)
            pygame.display.update()

            # Get AI move with statistics for debug panel
            if debug_mode:
                ai_move, last_ai_stats = ai_agent.get_move_with_stats(state)
                last_ai_move = ai_move
            else:
                ai_move = ai_agent.get_move(state)
                
            if ai_move is not None:
                time.sleep(AI_MOVE_DELAY)
                state.make_move(ai_move)
                last_state_hash = None  # Force recalculation on next frame

                # Check game over conditions
                winner, winning_positions = state.check_winner()
                if winner == PLAYER1:
                    message = "You win! Press R to restart, ESC for menu"
                    game_over = True
                    hint_col = None
                    debug_stats = None
                elif winner == PLAYER2:
                    message = "AI wins! Press R to restart, ESC for menu"
                    game_over = True
                    hint_col = None
                    debug_stats = None
                elif state.is_full():
                    message = "Draw! Press R to restart, ESC for menu"
                    game_over = True
                    hint_col = None
                    debug_stats = None
                    winning_positions = []
                else:
                    message = "Your turn (Player 1) - Click to move, Press H for hint"
                    hint_col = None  # Clear hint after AI move
                    winning_positions = []

            ai_thinking = False

        # Update animation frame for win animation
        if game_over and winning_positions:
            animation_frame += 1

        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False  # Exit game

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return True  # Return to menu
                elif event.key == pygame.K_r:
                    # Restart game
                    state = Connect4State()
                    game_over = False
                    hint_col = None
                    message = "Your turn (Player 1) - Click to move, Press H for hint, D for debug, T for theme"
                    ai_thinking = False
                    debug_stats = None
                    last_state_hash = None
                    winning_positions = []
                    animation_frame = 0
                    last_ai_move = None
                    last_ai_stats = None
                elif event.key == pygame.K_t:
                    # Cycle theme
                    config.cycle_theme()
                elif event.key == pygame.K_d and not game_over:
                    # Toggle debug mode and resize window
                    debug_mode = not debug_mode
                    new_width = get_window_width(debug_mode)
                    screen = pygame.display.set_mode((new_width, HEIGHT))
                    if debug_mode:
                        # Force recalculation on next frame if needed
                        last_state_hash = None
                    message = "Your turn (Player 1) - Click to move, Press H for hint, D for debug, T for theme"
                elif event.key == pygame.K_h and not game_over and state.current_player == PLAYER1:
                    # Show hint for human player
                    hint_col = mcts_search(state, n_iter=400)
                    if hint_col is not None:
                        message = f"Hint: Column {hint_col + 1} - Click to move, Press H for hint, D for debug"

            if event.type == pygame.MOUSEBUTTONDOWN:
                if not game_over and not ai_thinking and state.current_player == PLAYER1:
                    x, _ = event.pos
                    # Only process clicks on the board area (not debug panel)
                    if x < BOARD_WIDTH:
                        col = x // SQUARESIZE
                        legal_moves = state.get_legal_moves()
                        if col in legal_moves:
                            state.make_move(col)
                            last_state_hash = None  # Force recalculation on next frame

                            # Check game over conditions
                            winner, winning_positions = state.check_winner()
                            if winner == PLAYER1:
                                message = "You win! Press R to restart, ESC for menu"
                                game_over = True
                                hint_col = None
                                debug_stats = None
                            elif winner == PLAYER2:
                                message = "AI wins! Press R to restart, ESC for menu"
                                game_over = True
                                hint_col = None
                                debug_stats = None
                            elif state.is_full():
                                message = "Draw! Press R to restart, ESC for menu"
                                game_over = True
                                hint_col = None
                                debug_stats = None
                                winning_positions = []
                            else:
                                message = "AI thinking..."
                                hint_col = None
                                winning_positions = []

        draw_board(screen, state, font, hint_col, message,
                   config.current_theme, winning_positions, animation_frame)
        if debug_mode:
            draw_debug_panel(screen, font, state, debug_mode,
                             debug_stats, config.current_theme, last_ai_move, last_ai_stats)
        pygame.display.update()

    return False


def run_ai_vs_ai(screen, clock, font):
    """
    Run AI vs AI game mode.

    Both players are AI agents using MCTS.
    Press SPACE to pause/resume, UP/DOWN to adjust delay, D for debug, T for theme, R to restart, ESC to return to menu.
    """
    pygame.display.set_caption("MCTS Connect4 - AI vs AI")

    state = Connect4State()
    game_over = False
    message = "AI Player 1 thinking..."
    winning_positions = []
    animation_frame = 0

    ai_agent1 = AIAgent(n_iter=AI_ITERATIONS_PLAYER1, player_id=PLAYER1)
    ai_agent2 = AIAgent(n_iter=AI_ITERATIONS_PLAYER2, player_id=PLAYER2)
    ai_thinking = False
    last_move_time = time.time()
    debug_mode = False
    
    # Track last AI move and its statistics for debug panel
    last_ai_move = None
    last_ai_stats = None
    
    # Pause/resume and adjustable delay
    is_paused = False
    current_ai_delay = config.AI_MOVE_DELAY

    running = True
    while running:
        clock.tick(FPS)

        # In AI vs AI mode, we don't need to recalculate debug stats separately
        # The AI agents already provide statistics via get_move_with_stats()
        # This eliminates expensive redundant MCTS calculations (up to 2,700 iterations)

        # Handle AI turns (only if not paused)
        if not game_over and not ai_thinking and not is_paused:
            current_time = time.time()
            if current_time - last_move_time >= current_ai_delay:
                ai_thinking = True
                current_player = state.current_player

                if current_player == PLAYER1:
                    message = "AI Player 1 thinking..."
                else:
                    message = "AI Player 2 thinking..."

                draw_board(screen, state, font, None, message,
                           config.current_theme, winning_positions, animation_frame)
                if debug_mode:
                    draw_debug_panel(screen, font, state,
                                     debug_mode, None, config.current_theme, last_ai_move, last_ai_stats)
                # Draw AI controls panel
                from .renderer import draw_ai_controls
                draw_ai_controls(screen, font, current_ai_delay, is_paused, config.current_theme)
                pygame.display.update()

                # Get AI move with statistics for debug panel
                if debug_mode:
                    if current_player == PLAYER1:
                        ai_move, last_ai_stats = ai_agent1.get_move_with_stats(state)
                    else:
                        ai_move, last_ai_stats = ai_agent2.get_move_with_stats(state)
                    last_ai_move = ai_move
                else:
                    if current_player == PLAYER1:
                        ai_move = ai_agent1.get_move(state)
                    else:
                        ai_move = ai_agent2.get_move(state)

                if ai_move is not None:
                    state.make_move(ai_move)
                    
                    # Notify opponent about the move for tree reuse
                    if current_player == PLAYER1:
                        ai_agent2.notify_opponent_move(ai_move)
                    else:
                        ai_agent1.notify_opponent_move(ai_move)

                    # Check game over conditions
                    winner, winning_positions = state.check_winner()
                    if winner == PLAYER1:
                        message = "AI Player 1 wins! Press R to restart, ESC for menu"
                        game_over = True
                    elif winner == PLAYER2:
                        message = "AI Player 2 wins! Press R to restart, ESC for menu"
                        game_over = True
                    elif state.is_full():
                        message = "Draw! Press R to restart, ESC for menu"
                        game_over = True
                        winning_positions = []
                    else:
                        if state.current_player == PLAYER1:
                            message = "AI Player 1 thinking..."
                        else:
                            message = "AI Player 2 thinking..."
                        winning_positions = []

                    last_move_time = time.time()  # Update after move is made

                ai_thinking = False

        # Update animation frame for win animation
        if game_over and winning_positions:
            animation_frame += 1

        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False  # Exit game

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return True  # Return to menu
                elif event.key == pygame.K_r:
                    # Restart game
                    state = Connect4State()
                    game_over = False
                    message = "AI Player 1 thinking..."
                    ai_thinking = False
                    last_move_time = time.time()
                    winning_positions = []
                    animation_frame = 0
                    last_ai_move = None
                    last_ai_stats = None
                    is_paused = False
                    # Reset AI agents' tree managers
                    ai_agent1.reset()
                    ai_agent2.reset()
                elif event.key == pygame.K_t:
                    # Cycle theme
                    config.cycle_theme()
                elif event.key == pygame.K_d and not game_over:
                    # Toggle debug mode and resize window
                    debug_mode = not debug_mode
                    new_width = get_window_width(debug_mode)
                    screen = pygame.display.set_mode((new_width, HEIGHT))
                    if state.current_player == PLAYER1:
                        message = "AI Player 1 thinking..."
                    else:
                        message = "AI Player 2 thinking..."
                elif event.key == pygame.K_SPACE and not game_over:
                    # Toggle pause/resume
                    is_paused = not is_paused
                    if is_paused:
                        message = "⏸️  PAUSED - Press SPACE to resume"
                    else:
                        if state.current_player == PLAYER1:
                            message = "AI Player 1 thinking..."
                        else:
                            message = "AI Player 2 thinking..."
                elif event.key == pygame.K_UP and not game_over:
                    # Increase AI delay
                    current_ai_delay = min(current_ai_delay + config.AI_MOVE_DELAY_STEP, config.AI_MOVE_DELAY_MAX)
                elif event.key == pygame.K_DOWN and not game_over:
                    # Decrease AI delay
                    current_ai_delay = max(current_ai_delay - config.AI_MOVE_DELAY_STEP, config.AI_MOVE_DELAY_MIN)

        draw_board(screen, state, font, None, message,
                   config.current_theme, winning_positions, animation_frame)
        if debug_mode:
            draw_debug_panel(screen, font, state, debug_mode,
                             None, config.current_theme, last_ai_move, last_ai_stats)
        # Always draw AI controls panel in AI vs AI mode
        from .renderer import draw_ai_controls
        draw_ai_controls(screen, font, current_ai_delay, is_paused, config.current_theme)
        pygame.display.update()

    return False


def run_human_vs_human(screen, clock, font):
    """
    Run Human vs Human game mode (original functionality).

    Two human players alternate turns.
    Press H for hint, D for debug, T for theme, R to restart, ESC to return to menu.
    """
    pygame.display.set_caption("MCTS Connect4 - Human vs Human")

    state = Connect4State()
    game_over = False
    hint_col = None
    message = "Player 1 turn - Click to move, Press H for hint, D for debug, T for theme"
    winning_positions = []
    animation_frame = 0
    debug_mode = False
    debug_stats = None
    last_state_hash = None

    def get_state_hash(s):
        """Create a hash of the current game state to detect changes."""
        return tuple(tuple(row) for row in s.board) + (s.current_player,)

    running = True
    while running:
        clock.tick(FPS)

        # Check if state changed and update debug stats if needed
        current_state_hash = get_state_hash(state)
        if debug_mode and current_state_hash != last_state_hash and not state.is_terminal():
            if debug_stats is None or last_state_hash is None:
                # Calculate stats for new state (keep old stats visible during calculation)
                new_debug_stats = get_mcts_win_rates(state, n_iter=600)
                debug_stats = new_debug_stats
            last_state_hash = current_state_hash

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False  # Exit game

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return True  # Return to menu
                elif event.key == pygame.K_r:
                    state = Connect4State()
                    game_over = False
                    message = "Player 1 turn - Click to move, Press H for hint, D for debug, T for theme"
                    hint_col = mcts_search(state, n_iter=600)
                    debug_stats = None
                    last_state_hash = None
                    winning_positions = []
                    animation_frame = 0
                elif event.key == pygame.K_t:
                    # Cycle theme
                    config.cycle_theme()
                elif event.key == pygame.K_d and not game_over:
                    # Toggle debug mode and resize window
                    debug_mode = not debug_mode
                    new_width = get_window_width(debug_mode)
                    screen = pygame.display.set_mode((new_width, HEIGHT))
                    if debug_mode:
                        # Force recalculation on next frame if needed
                        last_state_hash = None
                    current = state.current_player
                    message = f"Player {current} turn - Click to move, Press H for hint, D for debug, T for theme"
                elif event.key == pygame.K_h and not game_over:
                    # Show hint for current player
                    hint_col = mcts_search(state, n_iter=600)
                    current = state.current_player
                    message = f"Player {current} turn - Hint shown - Click to move, Press H for hint, D for debug"

            if event.type == pygame.MOUSEBUTTONDOWN:
                if not game_over:
                    x, _ = event.pos
                    # Only process clicks on the board area (not debug panel)
                    if x < BOARD_WIDTH:
                        col = x // SQUARESIZE

                        legal_moves = state.get_legal_moves()
                        if col in legal_moves:
                            state.make_move(col)
                            last_state_hash = None  # Force recalculation on next frame

                            winner, winning_positions = state.check_winner()
                            if winner == PLAYER1:
                                message = "Player 1 wins! Press R to restart, ESC for menu"
                                game_over = True
                                hint_col = None
                                debug_stats = None
                            elif winner == PLAYER2:
                                message = "Player 2 wins! Press R to restart, ESC for menu"
                                game_over = True
                                hint_col = None
                                debug_stats = None
                            elif state.is_full():
                                message = "Draw! Press R to restart, ESC for menu"
                                game_over = True
                                hint_col = None
                                debug_stats = None
                                winning_positions = []
                            else:
                                current = state.current_player
                                message = f"Player {current} turn - Click to move, Press H for hint, D for debug"
                                hint_col = None
                                winning_positions = []

        # Update animation frame for win animation
        if game_over and winning_positions:
            animation_frame += 1

        draw_board(screen, state, font, hint_col, message,
                   config.current_theme, winning_positions, animation_frame)
        if debug_mode:
            draw_debug_panel(screen, font, state, debug_mode,
                             debug_stats, config.current_theme)
        pygame.display.update()

    return False


def run_time_attack(screen, clock, font):
    """
    Run Time Attack game mode.

    Two human players alternate turns with time banks.
    Each player starts with TIME_BANK_SECONDS. Running out of time = instant loss.
    Press T for theme, R to restart, ESC to return to menu.
    """
    pygame.display.set_caption("MCTS Connect4 - Time Attack")

    state = Connect4State()
    game_over = False
    message = "Player 1 turn - Click to move"
    winning_positions = []
    animation_frame = 0

    # Initialize time banks
    player1_time = float(TIME_BANK_SECONDS)
    player2_time = float(TIME_BANK_SECONDS)
    last_frame_time = time.time()

    running = True
    while running:
        clock.tick(FPS)

        # Update timers
        if not game_over:
            current_time = time.time()
            delta_time = current_time - last_frame_time
            last_frame_time = current_time

            # Decrement active player's time
            if state.current_player == PLAYER1:
                player1_time -= delta_time
                if player1_time <= 0:
                    player1_time = 0
                    message = "Player 1 ran out of time! Player 2 wins! Press R to restart, ESC for menu"
                    game_over = True
                    winning_positions = []
            else:
                player2_time -= delta_time
                if player2_time <= 0:
                    player2_time = 0
                    message = "Player 2 ran out of time! Player 1 wins! Press R to restart, ESC for menu"
                    game_over = True
                    winning_positions = []

        # Update animation frame for win animation
        if game_over and winning_positions:
            animation_frame += 1

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False  # Exit game

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return True  # Return to menu
                elif event.key == pygame.K_r:
                    # Restart game
                    state = Connect4State()
                    game_over = False
                    message = "Player 1 turn - Click to move"
                    player1_time = float(TIME_BANK_SECONDS)
                    player2_time = float(TIME_BANK_SECONDS)
                    last_frame_time = time.time()
                    winning_positions = []
                    animation_frame = 0
                elif event.key == pygame.K_t:
                    # Cycle theme
                    config.cycle_theme()

            if event.type == pygame.MOUSEBUTTONDOWN:
                if not game_over:
                    x, _ = event.pos
                    # Only process clicks on the board area (not debug panel)
                    if x < BOARD_WIDTH:
                        col = x // SQUARESIZE

                        legal_moves = state.get_legal_moves()
                        if col in legal_moves:
                            state.make_move(col)
                            last_frame_time = time.time()  # Reset timer on move

                            winner, winning_positions = state.check_winner()
                            if winner == PLAYER1:
                                message = "Player 1 wins! Press R to restart, ESC for menu"
                                game_over = True
                            elif winner == PLAYER2:
                                message = "Player 2 wins! Press R to restart, ESC for menu"
                                game_over = True
                            elif state.is_full():
                                message = "Draw! Press R to restart, ESC for menu"
                                game_over = True
                                winning_positions = []
                            else:
                                current = state.current_player
                                message = f"Player {current} turn - Click to move"
                                winning_positions = []

        draw_board(screen, state, font, None, message,
                   config.current_theme, winning_positions, animation_frame)
        draw_timer(screen, font, player1_time, player2_time,
                   state.current_player, config.current_theme)
        pygame.display.update()

    return False
