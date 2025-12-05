# A* Pathfinding Visualization

An interactive pygame-based visualization tool for the A* pathfinding algorithm.

## Features

- Interactive grid-based pathfinding visualization
- Click to place/remove walls
- Set custom start and goal positions
- Visual feedback showing the A* algorithm's search process
- Clean, modular codebase following industry standards

## Installation

This project uses `uv` for dependency management. Install dependencies with:

```bash
uv sync
```

Or if using pip:

```bash
pip install -e .
```

## Running the Game

Run the game with:

```bash
python main.py
```

Or:

```bash
uv run main.py
```

## Controls

- **Left Mouse Button**: Toggle wall on/off on a cell
- **Right Mouse Button**: Set the start cell
- **Middle Mouse Button**: Set the goal cell
- **Space**: Run A* algorithm from start to goal
- **Escape**: Quit the program

## Project Structure

```
asm2/
├── astar_game/          # Main game package
│   ├── __init__.py      # Package initialization
│   ├── config.py        # Configuration constants
│   ├── grid.py          # Grid utility functions
│   ├── astar.py         # A* pathfinding algorithm
│   ├── renderer.py      # Rendering functions
│   └── game.py          # Main Game class and loop
├── main.py              # Application entry point
├── pyproject.toml       # Project configuration
└── README.md            # This file
```

## Architecture

The codebase is organized into modular components:

- **config.py**: Centralized configuration including grid dimensions, colors, and default values
- **grid.py**: Utility functions for grid operations (cell conversion, neighbor finding)
- **astar.py**: Core A* pathfinding algorithm implementation
- **renderer.py**: All drawing and rendering logic
- **game.py**: Main Game class that manages state and the game loop
- **main.py**: Simple entry point that instantiates and runs the game

This structure makes the codebase maintainable, testable, and easy to extend.


