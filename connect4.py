"""
Main entry point for Connect 4 game with MCTS.

This module initializes pygame and runs the main game loop with menu system.
"""

import pygame
import sys
from connect4.game_modes import run_human_vs_ai, run_ai_vs_ai, run_human_vs_human, run_time_attack
from connect4.renderer import draw_menu
from connect4 import config


def main():
    """
    Main function that runs the Pygame event loop with menu system.

    Game modes:
        - Human vs AI: Human player vs MCTS AI agent
        - AI vs AI: Two MCTS agents playing against each other
        - Human vs Human: Two human players (original functionality)
        - Time Attack: Two human players with time banks

    Controls:
        - Menu: Press 1-4 to select game mode, T to change theme
        - In game: Press H for hint (Human vs AI and Human vs Human modes)
        - Press R to restart current game
        - Press ESC to return to menu
    """
    pygame.init()

    screen = pygame.display.set_mode(config.SIZE)
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("arial", 24)

    current_mode = config.MENU
    running = True

    while running:
        clock.tick(config.FPS)

        if current_mode == config.MENU:
            # Get current theme from config module each time to ensure it's up to date
            draw_menu(screen, font, config.current_theme)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_1:
                        current_mode = config.HUMAN_VS_AI
                    elif event.key == pygame.K_2:
                        current_mode = config.AI_VS_AI
                    elif event.key == pygame.K_3:
                        current_mode = config.HUMAN_VS_HUMAN
                    elif event.key == pygame.K_4:
                        current_mode = config.TIME_ATTACK
                    elif event.key == pygame.K_t:
                        # Cycle theme - this updates config.current_theme
                        config.cycle_theme()

        elif current_mode == config.HUMAN_VS_AI:
            return_to_menu = run_human_vs_ai(screen, clock, font)
            if return_to_menu:
                current_mode = config.MENU
            else:
                running = False

        elif current_mode == config.AI_VS_AI:
            return_to_menu = run_ai_vs_ai(screen, clock, font)
            if return_to_menu:
                current_mode = config.MENU
            else:
                running = False

        elif current_mode == config.HUMAN_VS_HUMAN:
            return_to_menu = run_human_vs_human(screen, clock, font)
            if return_to_menu:
                current_mode = config.MENU
            else:
                running = False

        elif current_mode == config.TIME_ATTACK:
            return_to_menu = run_time_attack(screen, clock, font)
            if return_to_menu:
                current_mode = config.MENU
            else:
                running = False

    pygame.quit()
    sys.exit()


# This ensures that main() is called only when this file is run directly,
# not when it is imported as a module in another script.
if __name__ == "__main__":
    main()
