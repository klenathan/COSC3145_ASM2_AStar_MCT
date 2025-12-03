"""
Connect 4 Game with Monte Carlo Tree Search (MCTS)

A pygame-based Connect 4 game implementation with MCTS-based AI agents.
"""

__version__ = "0.1.0"

from .state import Connect4State
from .ai_agent import AIAgent
from .mcts import mcts_search, MCTSNode

__all__ = [
    "Connect4State",
    "AIAgent",
    "mcts_search",
    "MCTSNode",
    "connect4",
]
