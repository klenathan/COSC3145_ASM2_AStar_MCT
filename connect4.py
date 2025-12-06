"""
Main entry point for Connect 4 game with MCTS.

This module initializes pygame and runs the main game loop with menu system.
"""

import pygame
import sys
from connect4.game_modes import run_human_vs_ai, run_ai_vs_ai, run_human_vs_human, run_time_attack
from connect4.renderer import draw_menu
from connect4 import config
from connect4.config import BOARD_WIDTH, HEIGHT


def main():
    """
    Main function that runs the Pygame event loop with menu system.

    Game modes:
        - Human vs AI: Human player vs MCTS AI agent
        - AI vs AI: Two MCTS agents playing against each other
        - Human vs Human: Two human players (original functionality)
        - Time Attack: Two human players with time banks

    Controls:
        - Menu: Click buttons to select game mode or change theme
        - In game: Press H for hint (Human vs AI and Human vs Human modes)
        - Press D to toggle debug panel (dynamically resizes window)
        - Press R to restart current game
        - Press ESC to return to menu
    """
    pygame.init()

    # Start with board-only size (no debug panel)
    screen = pygame.display.set_mode((BOARD_WIDTH, HEIGHT))
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("arial", 24)

    current_mode = config.MENU
    running = True
    menu_buttons = None  # Store menu buttons for click detection

    while running:
        clock.tick(config.FPS)

        if current_mode == config.MENU:
            # Ensure window is reset to board-only size for menu
            if screen.get_width() != BOARD_WIDTH:
                screen = pygame.display.set_mode((BOARD_WIDTH, HEIGHT))
            
            # Get current mouse position for hover effects
            mouse_pos = pygame.mouse.get_pos()
            
            # Draw menu and get button instances
            menu_buttons = draw_menu(screen, font, config.current_theme, mouse_pos)
            pygame.display.update()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    # Check which button was clicked
                    if menu_buttons["human_vs_ai"].is_clicked(mouse_pos):
                        current_mode = config.HUMAN_VS_AI
                    elif menu_buttons["ai_vs_ai"].is_clicked(mouse_pos):
                        current_mode = config.AI_VS_AI
                    elif menu_buttons["human_vs_human"].is_clicked(mouse_pos):
                        current_mode = config.HUMAN_VS_HUMAN
                    elif menu_buttons["time_attack"].is_clicked(mouse_pos):
                        current_mode = config.TIME_ATTACK
                    elif menu_buttons["theme"].is_clicked(mouse_pos):
                        # Cycle theme when theme button is clicked
                        config.cycle_theme()
                elif event.type == pygame.KEYDOWN:
                    # Keep 'T' key for theme cycling as alternative
                    if event.key == pygame.K_t:
                        config.cycle_theme()

        elif current_mode == config.HUMAN_VS_AI:
            return_to_menu = run_human_vs_ai(screen, clock, font)
            if return_to_menu:
                current_mode = config.MENU
                # Reset window size for menu
                screen = pygame.display.set_mode((BOARD_WIDTH, HEIGHT))
            else:
                running = False

        elif current_mode == config.AI_VS_AI:
            return_to_menu = run_ai_vs_ai(screen, clock, font)
            if return_to_menu:
                current_mode = config.MENU
                # Reset window size for menu
                screen = pygame.display.set_mode((BOARD_WIDTH, HEIGHT))
            else:
                running = False

        elif current_mode == config.HUMAN_VS_HUMAN:
            return_to_menu = run_human_vs_human(screen, clock, font)
            if return_to_menu:
                current_mode = config.MENU
                # Reset window size for menu
                screen = pygame.display.set_mode((BOARD_WIDTH, HEIGHT))
            else:
                running = False

        elif current_mode == config.TIME_ATTACK:
            return_to_menu = run_time_attack(screen, clock, font)
            if return_to_menu:
                current_mode = config.MENU
                # Reset window size for menu
                screen = pygame.display.set_mode((BOARD_WIDTH, HEIGHT))
            else:
                running = False

    pygame.quit()
    sys.exit()


# This ensures that main() is called only when this file is run directly,
# not when it is imported as a module in another script.
if __name__ == "__main__":
    main()
