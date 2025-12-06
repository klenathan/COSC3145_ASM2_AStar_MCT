"""
AI Agent for Connect 4 using Monte Carlo Tree Search.

This module contains the AIAgent class that uses MCTS to play Connect 4.
"""

from .mcts import (
    mcts_search, 
    mcts_search_with_stats,
    mcts_search_optimized,
    mcts_search_optimized_with_stats,
    MCTSTreeManager
)


class AIAgent:
    """
    AI agent that uses MCTS to play Connect 4.

    Attributes:
        n_iter: Number of MCTS iterations to perform
        player_id: The player ID this agent represents (PLAYER1 or PLAYER2)
        use_optimizations: If True, use optimized MCTS with tree reuse
        tree_manager: MCTSTreeManager for tree reuse between moves
        opponent_last_move: Last move made by opponent (for tree reuse)
    """

    def __init__(self, n_iter=200, player_id=None, use_optimizations=True):
        """
        Initialize the AI agent.

        Arguments:
            n_iter: Number of MCTS iterations (default 200)
            player_id: Player ID (PLAYER1 or PLAYER2), can be None
            use_optimizations: If True, use optimized MCTS (default True)
        """
        self.n_iter = n_iter
        self.player_id = player_id
        self.use_optimizations = use_optimizations
        self.tree_manager = MCTSTreeManager() if use_optimizations else None
        self.opponent_last_move = None

    def notify_opponent_move(self, move):
        """
        Notify the agent about opponent's move for tree reuse.
        
        Call this after opponent makes a move but before calling get_move.
        
        Arguments:
            move: Column index where opponent played
        """
        self.opponent_last_move = move

    def reset(self):
        """Reset the agent's state (e.g., on new game)."""
        if self.tree_manager:
            self.tree_manager.clear()
        self.opponent_last_move = None

    def get_move(self, state):
        """
        Get the best move for the current game state using MCTS.

        Arguments:
            state: Connect4State instance representing current game state

        Returns:
            Column index of the best move, or None if no legal moves
        """
        if self.use_optimizations:
            move = mcts_search_optimized(
                state, 
                n_iter=self.n_iter,
                tree_manager=self.tree_manager,
                use_adaptive_iterations=True,
                opponent_last_move=self.opponent_last_move
            )
            self.opponent_last_move = None  # Clear after use
            return move
        return mcts_search(state, n_iter=self.n_iter)

    def get_move_with_stats(self, state):
        """
        Get the best move for the current game state using MCTS, along with statistics.

        Arguments:
            state: Connect4State instance representing current game state

        Returns:
            Tuple (move, stats) where:
            - move: Column index of the best move, or None if no legal moves
            - stats: Dict with analytics about the decision:
                - selected_col: The selected column
                - visits: Number of visits to the selected node
                - win_rate: Win rate percentage for the selected move
                - total_simulations: Total number of MCTS iterations
                - all_moves: Dict of all considered moves with their stats
                - actual_iterations: Actual iterations used (if optimized)
        """
        if self.use_optimizations:
            root_node, root_player, actual_iterations = mcts_search_optimized_with_stats(
                state,
                n_iter=self.n_iter,
                tree_manager=self.tree_manager,
                use_adaptive_iterations=True,
                opponent_last_move=self.opponent_last_move
            )
            self.opponent_last_move = None  # Clear after use
        else:
            root_node, root_player = mcts_search_with_stats(state, n_iter=self.n_iter)
            actual_iterations = self.n_iter
        
        if root_node is None:
            return None, None
        
        # Find the most visited child (the selected move)
        best_child = root_node.most_visited_child()
        
        if best_child is None:
            return None, None
        
        selected_col = best_child.move
        visits = best_child.visits
        win_rate = (best_child.wins / best_child.visits * 100.0) if best_child.visits > 0 else 0.0
        
        # Store for tree reuse
        if self.tree_manager:
            self.tree_manager.store_root(root_node, selected_col)
        
        # Gather stats for all moves
        all_moves = {}
        c_param = 1.4  # Exploration constant for UCB
        for child in root_node.children:
            child_visits = child.visits
            child_win_rate = (child.wins / child.visits * 100.0) if child.visits > 0 else 0.0
            # Calculate UCB score
            if child_visits == 0:
                ucb_score = float('inf')
            else:
                import math
                exploit = child.wins / child.visits
                explore = math.sqrt(2 * math.log(root_node.visits) / child.visits)
                ucb_score = exploit + c_param * explore
            all_moves[child.move] = {
                'visits': child_visits,
                'win_rate': child_win_rate,
                'ucb_score': ucb_score
            }
        
        stats = {
            'selected_col': selected_col,
            'visits': visits,
            'win_rate': win_rate,
            'total_simulations': root_node.visits,
            'all_moves': all_moves,
            'actual_iterations': actual_iterations
        }
        
        return selected_col, stats
