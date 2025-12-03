"""
A* Pathfinding Visualization Game

Entry point for the A* pathfinding visualization application.

Controls:
  - Left click: toggle wall on or off on a cell.
  - Right click: set the start cell.
  - Middle click: set the goal cell.
  - Space key: run A* from start to goal and draw the path.
  - Escape or window close: quit the program.
"""

from astar_game import Game


def main():
    """Main entry point for the application."""
    game = Game()
    game.run()


if __name__ == "__main__":
    main()
