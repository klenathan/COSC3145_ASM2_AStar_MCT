# Game AI Design - Assignment 2

This project contains two AI-powered game applications demonstrating **A\* Pathfinding** and **Monte Carlo Tree Search (MCTS)** algorithms.

## Requirements

```bash
pip install pygame
```

Or using `uv`:
```bash
uv sync
```

---

## 1. A* Pathfinding Visualization

An interactive visualization of the A\* pathfinding algorithm with terrain costs, diagonal movement, and a frog character that follows the computed path.

### Run

```bash
python astar_game.py
```

### Features

- **Procedural Terrain Generation**: Perlin noise-based terrain with grass, water, mud, and walls
- **Terrain Costs**: Different terrains have different traversal costs
- **Diagonal Movement**: Toggle diagonal pathfinding for more natural movement
- **Real-time Visualization**: Watch A\* explore the grid step-by-step
- **Frog Character**: Animated frog follows the computed path using steering behaviors

### Controls

| Input | Action |
|-------|--------|
| **Left Click** | Place selected terrain type |
| **Right Click** | Set goal and run pathfinding from frog to clicked position |
| **Middle Click** | Set goal position (legacy) |
| **Space** | Run A\* from frog's current position to goal |
| **R** | Regenerate terrain |
| **D** | Toggle debug mode |
| **I** | Toggle info panel |
| **1-4** | Select terrain type (1=Grass, 2=Water, 3=Mud, 4=Wall) |
| **Escape** | Quit |

### Info Panel

The info panel (toggle with **I**) displays:
- Visualization speed slider
- Diagonal movement toggle
- A\* overlay visibility toggle
- Path statistics (cost breakdown by terrain type)

---

## 2. Connect 4 with MCTS AI

A Connect 4 game featuring an AI opponent powered by Monte Carlo Tree Search with smart rollouts and win-rate analysis.

### Run

```bash
python connect4.py
```

### Game Modes

| Mode | Description |
|------|-------------|
| **Human vs AI** | Play against the MCTS AI opponent |
| **AI vs AI** | Watch two MCTS agents compete |
| **Human vs Human** | Two-player local multiplayer |
| **Time Attack** | Two players with time banks |

### Controls

| Input | Action |
|-------|--------|
| **Click Column** | Drop piece in that column |
| **H** | Get hint from MCTS (Human modes) |
| **D** | Toggle debug panel with AI statistics |
| **R** | Restart current game |
| **T** | Cycle theme |
| **Escape** | Return to menu |

### MCTS AI Features

- **UCT Selection**: Balances exploration vs exploitation
- **Smart Rollouts**: Uses heuristics (win/block detection) during simulation
- **Win Rate Display**: Debug panel shows per-column win probabilities
- **Tree Persistence**: Reuses search tree in AI vs AI mode for faster decisions

---

## Project Structure

```
├── astar_game.py          # A* game entry point
├── astar_game/            # A* pathfinding module
│   ├── astar.py           # A* algorithm implementation
│   ├── frog.py            # Frog character with steering behaviors
│   ├── renderer.py        # Grid and UI rendering
│   └── ...
├── connect4.py            # Connect 4 entry point
├── connect4/              # Connect 4 module
│   ├── mcts.py            # MCTS algorithm implementation
│   ├── state.py           # Game state management
│   ├── renderer.py        # Board and UI rendering
│   └── ...
└── requirements.txt       # Python dependencies
```
