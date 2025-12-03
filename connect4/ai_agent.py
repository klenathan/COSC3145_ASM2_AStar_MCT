"""
AI Agent for Connect 4 using Monte Carlo Tree Search.

This module contains the AIAgent class that uses MCTS to play Connect 4.
"""

from .mcts import mcts_search


class AIAgent:
    """
    AI agent that uses MCTS to play Connect 4.

    Attributes:
        n_iter: Number of MCTS iterations to perform
        player_id: The player ID this agent represents (PLAYER1 or PLAYER2)
    """

    def __init__(self, n_iter=200, player_id=None):
        """
        Initialize the AI agent.

        Arguments:
            n_iter: Number of MCTS iterations (default 400)
            player_id: Player ID (PLAYER1 or PLAYER2), can be None
        """
        self.n_iter = n_iter
        self.player_id = player_id

    def get_move(self, state):
        """
        Get the best move for the current game state using MCTS.

        Arguments:
            state: Connect4State instance representing current game state

        Returns:
            Column index of the best move, or None if no legal moves
        """
        return mcts_search(state, n_iter=self.n_iter)

