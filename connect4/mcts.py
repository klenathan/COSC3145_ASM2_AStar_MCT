"""
Monte Carlo Tree Search (MCTS) implementation for Connect 4.

This module contains the MCTS algorithm implementation including:
- MCTSNode class for tree nodes
- MCTS search functions
- Win rate calculation for debug panel

MCTS is built on 4 main steps that are repeated many times:

1. SELECTION
   - Start from the root node that represents the current game state.
   - If the node has already been visited and fully expanded,
     we use a formula called UCT (Upper Confidence bound applied to Trees)
     to pick the child that balances:
        * Exploitation: children that won more often in the past.
        * Exploration: children that have been visited fewer times.
   - We follow this path of best children until we reach a node that:
        * is not fully expanded, or
        * represents a terminal game state (win, loss, or draw).

2. EXPANSION
   - If the selected node is not terminal, we can add a new child.
   - A child corresponds to playing one of the moves that has not been tried yet.
   - We pick one untried move, apply it to a copy of the game state,
     and create a new child node that stores this new state.

3. SIMULATION (also called ROLLOUT)
   - From the newly created child state, we play a random game until the end.
   - That means we randomly select legal moves until we reach a win, loss, or draw.
   - At the end we know the result:
        * The root player wins, loses, or it is a draw.
   - We convert this result into a numeric reward:
        * 1.0 for a win for the root player
        * 0.0 for a loss for the root player
        * 0.5 for a draw

4. BACKPROPAGATION
   - We then walk back from the simulation node up to the root node.
   - For each node on this path we:
        * Increase the visit count.
        * Add the reward to the node's total wins.
   - This way, each node stores:
        * How many times we visited it.
        * How many wins the root player got through this node.

After doing many iterations of these four steps:
   - The root node will have some children, each corresponding to a possible move.
   - Each child has a visit count and a total win count.
   - We can then pick the child that has the most visits.
   - The move that leads to that child is our suggested move.

The main idea:
   - Random simulations plus statistics guide us to good moves.
   - More iterations usually gives a smarter suggestion.
"""

import math
import random
from .state import Connect4State
from .config import COLS, PLAYER1, PLAYER2


class MCTSNode:
    """
    Node in the MCTS tree.

    It stores:
    - state: a Connect4State instance
    - parent: parent node in the tree (None for root)
    - move: the move (column index) that led from the parent state to this state
    - children: list of child MCTSNode objects
    - visits: how many times this node was visited in the search
    - wins: total reward from the root player's perspective
    """

    def __init__(self, state, parent=None, move=None):
        self.state = state          # Game state at this node
        self.parent = parent        # Parent node
        self.move = move            # Move that led to this node from parent
        self.children = []          # List of child MCTSNode instances
        self.visits = 0             # Number of times this node has been visited
        self.wins = 0.0             # Sum of rewards from root player's point of view

    def is_fully_expanded(self):
        """
        Check if this node has created children for all legal moves.

        If the state is terminal, we consider it fully expanded,
        because there are no moves to expand.

        Otherwise:
        - We get all legal moves from this state.
        - We compare them with the moves that are already used by children.
        - If every legal move has a child, then the node is fully expanded.
        """
        if self.state.is_terminal():
            return True

        child_moves = {child.move for child in self.children}
        legal_moves = set(self.state.get_legal_moves())
        # Node is fully expanded if:
        # - the number of children matches the number of legal moves
        # - and every legal move already has a child
        return legal_moves.issubset(child_moves) and len(legal_moves) == len(child_moves)

    def best_child(self, c_param=1.4):
        """
        Select a child using the UCT formula.

        UCT score for a child:
            exploit = wins / visits
            explore = sqrt( 2 * ln(parent_visits) / child_visits )
            score = exploit + c_param * explore

        - exploit encourages moves that have good win ratio.
        - explore encourages trying moves that are less visited.

        c_param (exploration constant) controls how much we explore.
        A common choice is around 1.4 (square root of 2).

        If a child has never been visited (visits == 0),
        we treat its score as infinity to ensure it is explored at least once.
        """
        best_score = float("-inf")
        best_children = []

        for child in self.children:
            if child.visits == 0:
                # Encourage at least one visit for every child
                score = float("inf")
            else:
                exploit = child.wins / child.visits
                explore = math.sqrt(2 * math.log(self.visits) / child.visits)
                score = exploit + c_param * explore

            # Keep track of the best score and all children that achieve it
            if score > best_score:
                best_score = score
                best_children = [child]
            elif score == best_score:
                best_children.append(child)

        # If several children tie, pick one at random
        return random.choice(best_children)

    def most_visited_child(self):
        """
        After MCTS finishes, we want to pick the move that was explored the most.

        This function returns the child with the highest visit count.
        If there are no children (no moves), returns None.
        If multiple children tie for most visits, prefer the center column (column 3).
        """
        if not self.children:
            return None

        # Find the maximum visit count
        max_visits = max(child.visits for child in self.children)

        # Get all children with the maximum visit count
        best_children = [
            child for child in self.children if child.visits == max_visits]

        # If there's a tie, prefer the center column (column 3) as it's strategically better
        # This helps on the first turn when all moves are equally good
        center_col = COLS // 2  # Column 3 (0-indexed)
        for child in best_children:
            if child.move == center_col:
                return child

        # If center column is not among the best, return the first one (or random if you prefer)
        return best_children[0]


def rollout(state, root_player):
    """
    Perform a random simulation (rollout) from the given state until the game ends.

    We work on a cloned state so we do not modify the original.

    At each step:
        - Get the list of legal moves.
        - Pick one move uniformly at random.
        - Apply this move.

    When the game reaches a terminal state:
        - If the winner is the root player, we return 1.0
        - If the winner is the opponent, we return 0.0
        - If there is no winner (draw), we return 0.5

    Arguments:
        state: Connect4State from which to start simulation
        root_player: the player we consider as "our" perspective
    """
    temp_state = state.clone()

    # Play random moves until the game is over
    while not temp_state.is_terminal():
        legal_moves = temp_state.get_legal_moves()
        if not legal_moves:
            break  # No moves left, should be a draw
        move = random.choice(legal_moves)
        temp_state.make_move(move)

    # Game is over, check the result
    winner, _ = temp_state.check_winner()
    if winner is None:
        return 0.5
    if winner == root_player:
        return 1.0
    else:
        return 0.0


def mcts_search(root_state, n_iter=400):
    """
    Run MCTS from the given root_state and return the best move.

    Arguments:
        root_state:
            The current game state from which we search.
        n_iter:
            Number of MCTS iterations. More iterations usually means a better hint
            but it is also slower.

    Returns:
        The column index of the suggested move, or
        None if there is no legal move.

    Steps:
        1. Create a root MCTSNode that holds a copy of root_state.
        2. For n_iter iterations:
            a) Selection
            b) Expansion
            c) Simulation
            d) Backpropagation
        3. Return the move of the most visited child of the root.
    """
    # If the game is already finished, we return no move
    if root_state.is_terminal():
        return None

    # The root player is the player who is about to move in root_state
    root_player = root_state.current_player

    # Create a root node for the MCTS tree
    root_node = MCTSNode(root_state.clone())

    for _ in range(n_iter):
        # 1. Start at the root node and work on a fresh copy of root_state
        node = root_node
        state = root_state.clone()

        # 2. SELECTION
        # While the current node has children, is fully expanded,
        # and the state is not terminal, choose the best child with UCT.
        while node.children and node.is_fully_expanded() and not state.is_terminal():
            node = node.best_child()
            # Apply the move that led to this child to our simulation state
            if node.move is not None:
                state.make_move(node.move)

        # 3. EXPANSION
        # If the state is not terminal, we can expand by creating a new child.
        if not state.is_terminal():
            legal_moves = state.get_legal_moves()
            existing_moves = {child.move for child in node.children}
            # Untried moves are legal moves without a child yet
            untried_moves = [m for m in legal_moves if m not in existing_moves]

            if untried_moves:
                # Prefer center column (column 3) when expanding, especially on first turn
                # This helps the AI make smarter first moves
                center_col = COLS // 2  # Column 3 (0-indexed)
                if center_col in untried_moves and len(untried_moves) > 1:
                    # Give center column higher probability, but still allow exploration
                    # Weight: center gets 3x probability, others get 1x
                    weights = [3.0 if m ==
                               center_col else 1.0 for m in untried_moves]
                    move = random.choices(
                        untried_moves, weights=weights, k=1)[0]
                else:
                    # If center is not available or it's the only move, pick randomly
                    move = random.choice(untried_moves)
                # Apply it to the simulation state
                state.make_move(move)
                # Create the new child node
                child_node = MCTSNode(state.clone(), parent=node, move=move)
                # Attach this new child to the tree
                node.children.append(child_node)
                # And select this new child as the node to simulate from
                node = child_node

        # 4. SIMULATION (ROLLOUT)
        # From this node's state, simulate a random game until the end.
        reward = rollout(state, root_player)

        # 5. BACKPROPAGATION
        # Walk up the tree and update visit and win counts.
        while node is not None:
            node.visits += 1
            node.wins += reward
            node = node.parent

    # After finishing all iterations, pick the child with the most visits.
    best_child = root_node.most_visited_child()
    if best_child is None:
        return None
    return best_child.move


def mcts_search_with_stats(root_state, n_iter=400):
    """
    Run MCTS from the given root_state and return the root node with statistics.

    Arguments:
        root_state: The current game state from which we search.
        n_iter: Number of MCTS iterations.

    Returns:
        A tuple (root_node, root_player) where:
        - root_node: The MCTSNode root containing all children statistics
        - root_player: The player who was about to move in root_state
        Returns (None, None) if game is terminal.
    """
    if root_state.is_terminal():
        return None, None

    root_player = root_state.current_player
    root_node = MCTSNode(root_state.clone())

    for _ in range(n_iter):
        node = root_node
        state = root_state.clone()

        # SELECTION
        while node.children and node.is_fully_expanded() and not state.is_terminal():
            node = node.best_child()
            if node.move is not None:
                state.make_move(node.move)

        # EXPANSION
        if not state.is_terminal():
            legal_moves = state.get_legal_moves()
            existing_moves = {child.move for child in node.children}
            untried_moves = [m for m in legal_moves if m not in existing_moves]

            if untried_moves:
                # Prefer center column (column 3) when expanding, especially on first turn
                # This helps the AI make smarter first moves
                center_col = COLS // 2  # Column 3 (0-indexed)
                if center_col in untried_moves and len(untried_moves) > 1:
                    # Give center column higher probability, but still allow exploration
                    # Weight: center gets 3x probability, others get 1x
                    weights = [3.0 if m ==
                               center_col else 1.0 for m in untried_moves]
                    move = random.choices(
                        untried_moves, weights=weights, k=1)[0]
                else:
                    # If center is not available or it's the only move, pick randomly
                    move = random.choice(untried_moves)
                state.make_move(move)
                child_node = MCTSNode(state.clone(), parent=node, move=move)
                node.children.append(child_node)
                node = child_node

        # SIMULATION
        reward = rollout(state, root_player)

        # BACKPROPAGATION
        while node is not None:
            node.visits += 1
            node.wins += reward
            node = node.parent

    return root_node, root_player


def get_mcts_win_rates(state, n_iter=400):
    """
    Calculate MCTS win rates for each column from both players' perspectives.

    Arguments:
        state: Current Connect4State
        n_iter: Number of MCTS iterations

    Returns:
        A tuple (player1_rates, player2_rates, overall_rates) where:
        - player1_rates: dict {column_index: win_rate_percentage}
        - player2_rates: dict {column_index: win_rate_percentage}
        - overall_rates: tuple (p1_overall, p2_overall) overall win percentages
    """
    player1_rates = {}
    player2_rates = {}
    overall_p1 = 50.0
    overall_p2 = 50.0

    # Get statistics from current player's perspective
    root_node, root_player = mcts_search_with_stats(state, n_iter)

    if root_node:
        # Calculate overall win rate from root node
        if root_node.visits > 0:
            root_win_rate = (root_node.wins / root_node.visits) * 100.0
            if root_player == PLAYER1:
                overall_p1 = root_win_rate
                overall_p2 = 100.0 - root_win_rate
            else:
                overall_p2 = root_win_rate
                overall_p1 = 100.0 - root_win_rate
        # Calculate win rates for current player
        for child in root_node.children:
            if child.visits > 0:
                win_rate = (child.wins / child.visits) * 100.0
                if root_player == PLAYER1:
                    player1_rates[child.move] = win_rate
                else:
                    player2_rates[child.move] = win_rate
            else:
                if root_player == PLAYER1:
                    player1_rates[child.move] = 0.0
                else:
                    player2_rates[child.move] = 0.0

        # For the opponent's perspective, simulate what happens after current player moves
        # and calculate opponent's win rate from the resulting state
        for child in root_node.children:
            temp_state = state.clone()
            temp_state.make_move(child.move)

            if not temp_state.is_terminal():
                # Run MCTS from opponent's perspective
                opp_root_node, opp_player = mcts_search_with_stats(
                    temp_state, n_iter // 2)  # Use fewer iterations for speed
                if opp_root_node:
                    # Calculate average win rate for opponent across all their moves
                    total_wins = 0.0
                    total_visits = 0
                    for opp_child in opp_root_node.children:
                        total_wins += opp_child.wins
                        total_visits += opp_child.visits

                    if total_visits > 0:
                        opp_win_rate = (total_wins / total_visits) * 100.0
                    else:
                        opp_win_rate = 50.0  # Unknown, assume 50%

                    if root_player == PLAYER1:
                        player2_rates[child.move] = opp_win_rate
                    else:
                        player1_rates[child.move] = opp_win_rate
                else:
                    # No moves available for opponent
                    if root_player == PLAYER1:
                        player2_rates[child.move] = 0.0
                    else:
                        player1_rates[child.move] = 0.0
            else:
                # Terminal state - check winner
                winner, _ = temp_state.check_winner()
                if winner == PLAYER1:
                    player1_rates[child.move] = 100.0
                    player2_rates[child.move] = 0.0
                elif winner == PLAYER2:
                    player1_rates[child.move] = 0.0
                    player2_rates[child.move] = 100.0
                else:
                    # Draw
                    player1_rates[child.move] = 50.0
                    player2_rates[child.move] = 50.0

    return player1_rates, player2_rates, (overall_p1, overall_p2)
