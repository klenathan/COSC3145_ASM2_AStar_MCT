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
from .config import COLS, PLAYER1, PLAYER2, EMPTY


# =============================================================================
# AI v AI Optimization Components
# =============================================================================

def get_board_hash(board, current_player):
    """
    Compute hash of board state for transposition table.
    
    Arguments:
        board: 2D list representing the game board
        current_player: Current player to move
    
    Returns:
        Integer hash value unique to this game state
    """
    return hash(tuple(tuple(row) for row in board) + (current_player,))


# =============================================================================
# Ultra-Fast Board Simulation (No Object Overhead)
# =============================================================================

def fast_copy_board(board):
    """Create a fast shallow copy of board for simulation."""
    return [row[:] for row in board]


def fast_get_legal_moves(board):
    """Get legal moves from raw board (no object overhead)."""
    return [c for c in range(len(board[0])) if board[0][c] == EMPTY]


def fast_make_move(board, col, player):
    """
    Make a move on raw board and return the row where piece landed.
    Returns -1 if column is full.
    """
    rows = len(board)
    for r in range(rows - 1, -1, -1):
        if board[r][col] == EMPTY:
            board[r][col] = player
            return r
    return -1


def fast_undo_move(board, col, row):
    """Undo a move by clearing the cell."""
    board[row][col] = EMPTY


def fast_check_win(board, row, col, player):
    """
    Check if the move at (row, col) wins the game.
    Only checks lines through the placed piece.
    """
    rows = len(board)
    cols = len(board[0])
    
    directions = [(0, 1), (1, 0), (1, 1), (1, -1)]
    
    for dr, dc in directions:
        count = 1
        # Positive direction
        r, c = row + dr, col + dc
        while 0 <= r < rows and 0 <= c < cols and board[r][c] == player:
            count += 1
            r += dr
            c += dc
        # Negative direction 
        r, c = row - dr, col - dc
        while 0 <= r < rows and 0 <= c < cols and board[r][c] == player:
            count += 1
            r -= dr
            c -= dc
        if count >= 4:
            return True
    return False


def fast_rollout(board, current_player, root_player):
    """
    Ultra-fast rollout using random moves on raw board.
    
    This is much faster than smart_rollout because:
    1. No object creation
    2. No state cloning
    3. Simple random move selection
    
    Returns:
        1.0 if root_player wins
        0.0 if opponent wins
        0.5 if draw
    """
    player = current_player
    
    while True:
        legal_moves = fast_get_legal_moves(board)
        if not legal_moves:
            return 0.5  # Draw - board full
        
        # Random move selection
        col = random.choice(legal_moves)
        row = fast_make_move(board, col, player)
        
        if row >= 0 and fast_check_win(board, row, col, player):
            return 1.0 if player == root_player else 0.0
        
        # Switch player
        player = PLAYER1 if player == PLAYER2 else PLAYER2


def fast_smart_rollout(board, current_player, root_player):
    """
    Fast rollout with win/block detection but minimal object overhead.
    Balances speed with smart play.
    """
    player = current_player
    rows = len(board)
    
    while True:
        legal_moves = fast_get_legal_moves(board)
        if not legal_moves:
            return 0.5  # Draw
        
        opponent = PLAYER1 if player == PLAYER2 else PLAYER2
        selected_move = None
        
        # Check for winning move
        for col in legal_moves:
            row = -1
            for r in range(rows - 1, -1, -1):
                if board[r][col] == EMPTY:
                    row = r
                    break
            if row >= 0:
                board[row][col] = player
                if fast_check_win(board, row, col, player):
                    # Found win - clean up and return
                    return 1.0 if player == root_player else 0.0
                board[row][col] = EMPTY
        
        # Check for blocking move
        for col in legal_moves:
            row = -1
            for r in range(rows - 1, -1, -1):
                if board[r][col] == EMPTY:
                    row = r
                    break
            if row >= 0:
                board[row][col] = opponent
                if fast_check_win(board, row, col, opponent):
                    board[row][col] = EMPTY
                    selected_move = col
                    break
                board[row][col] = EMPTY
        
        # Random if no forced move
        if selected_move is None:
            selected_move = random.choice(legal_moves)
        
        # Make the move
        row = fast_make_move(board, selected_move, player)
        
        if row >= 0 and fast_check_win(board, row, selected_move, player):
            return 1.0 if player == root_player else 0.0
        
        player = opponent


def detect_forced_move(state):
    """
    Detect if there's a forced win or block available.
    
    Returns:
        (move, is_winning) tuple where:
        - move: Column index of forced move, or None
        - is_winning: True if it's a winning move, False if blocking
    """
    current_player = state.current_player
    opponent = PLAYER1 if current_player == PLAYER2 else PLAYER2
    board = state.board
    legal_moves = state.get_legal_moves()
    rows = len(board)
    
    # Check for immediate winning move
    for col in legal_moves:
        # Find drop row
        row = -1
        for r in range(rows - 1, -1, -1):
            if board[r][col] == EMPTY:
                row = r
                break
        if row >= 0:
            # Check if this creates a win
            board[row][col] = current_player
            if check_win_at_position(board, row, col, current_player):
                board[row][col] = EMPTY
                return (col, True)
            board[row][col] = EMPTY
    
    # Check for blocking move
    for col in legal_moves:
        row = -1
        for r in range(rows - 1, -1, -1):
            if board[r][col] == EMPTY:
                row = r
                break
        if row >= 0:
            board[row][col] = opponent
            if check_win_at_position(board, row, col, opponent):
                board[row][col] = EMPTY
                return (col, False)
            board[row][col] = EMPTY
    
    return (None, False)


def estimate_position_complexity(state):
    """
    Estimate how many iterations needed based on position complexity.
    
    Simple positions (forced moves, few legal moves) need fewer iterations.
    Complex positions (many options, mid-game) need more iterations.
    
    Arguments:
        state: Current Connect4State
    
    Returns:
        Suggested iteration multiplier (0.25 to 1.0)
    """
    # Check for forced moves (win or block)
    forced_move, is_winning = detect_forced_move(state)
    if forced_move is not None:
        if is_winning:
            return 0.1  # Just take the win
        else:
            return 0.25  # Must block, but verify no better option
    
    # Count legal moves
    legal_moves = state.get_legal_moves()
    num_moves = len(legal_moves)
    
    if num_moves <= 2:
        return 0.5  # Few options, less exploration needed
    elif num_moves <= 4:
        return 0.75
    else:
        return 1.0  # Full exploration


class MCTSTreeManager:
    """
    Manages tree persistence between moves for AI v AI optimization.
    
    Instead of discarding the entire MCTS tree after each move, this class
    allows reusing the subtree that corresponds to the opponent's actual move.
    This preserves valuable search information from previous iterations.
    """
    
    def __init__(self):
        self.last_root = None
        self.last_move = None
    
    def get_reusable_root(self, opponent_move):
        """
        Find and return a reusable subtree after opponent's move.
        
        Arguments:
            opponent_move: The column where opponent just played
        
        Returns:
            MCTSNode that can be used as root, or None if no reusable tree
        """
        if self.last_root is None or opponent_move is None:
            return None
        
        # Find the child that corresponds to opponent's move
        for child in self.last_root.children:
            if child.move == opponent_move:
                # Found it! Detach from parent and return
                child.parent = None
                return child
        
        # Opponent's move wasn't explored - start fresh
        return None
    
    def store_root(self, root_node, selected_move):
        """
        Store the root and selected move for potential reuse.
        
        Arguments:
            root_node: The MCTSNode that was used as root
            selected_move: The move that was selected
        """
        # Find the child corresponding to our selected move
        for child in root_node.children:
            if child.move == selected_move:
                self.last_root = child
                self.last_move = selected_move
                return
        
        self.last_root = None
        self.last_move = None
    
    def clear(self):
        """Clear the stored tree (e.g., on game restart)."""
        self.last_root = None
        self.last_move = None


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


def check_win_at_position(board, row, col, player):
    """
    Efficiently check if placing a piece at (row, col) creates a win.
    
    Only checks lines passing through the given position rather than
    scanning the entire board. This is O(1) instead of O(rows*cols).
    
    Arguments:
        board: 2D list representing the game board
        row: Row where piece was placed
        col: Column where piece was placed
        player: Player ID to check for
    
    Returns:
        True if this position creates 4-in-a-row, False otherwise
    """
    directions = [
        (0, 1),   # Horizontal
        (1, 0),   # Vertical
        (1, 1),   # Diagonal down-right
        (1, -1),  # Diagonal down-left
    ]
    
    rows = len(board)
    cols = len(board[0])
    
    for dr, dc in directions:
        count = 1  # Count the piece at (row, col)
        
        # Check in positive direction
        r, c = row + dr, col + dc
        while 0 <= r < rows and 0 <= c < cols and board[r][c] == player:
            count += 1
            r += dr
            c += dc
        
        # Check in negative direction
        r, c = row - dr, col - dc
        while 0 <= r < rows and 0 <= c < cols and board[r][c] == player:
            count += 1
            r -= dr
            c -= dc
        
        if count >= 4:
            return True
    
    return False


def get_drop_row(board, col):
    """
    Get the row where a piece would land if dropped in the given column.
    
    Returns:
        Row index where piece would land, or -1 if column is full
    """
    rows = len(board)
    for r in range(rows - 1, -1, -1):
        if board[r][col] == EMPTY:
            return r
    return -1


def select_smart_move(state, legal_moves):
    """
    Select a move using simple heuristics for smarter rollout.
    
    OPTIMIZED VERSION: Uses local win checking instead of full board scan.

    Priority order:
        1. Take a winning move if available
        2. Block opponent's winning move if they can win next turn
        3. Otherwise, pick a move uniformly at random

    Arguments:
        state: Current Connect4State
        legal_moves: List of legal column indices

    Returns:
        Column index of the selected move
    """
    current_player = state.current_player
    opponent = PLAYER1 if current_player == PLAYER2 else PLAYER2
    board = state.board

    # 1. Check for immediate winning move (fast check)
    for col in legal_moves:
        row = get_drop_row(board, col)
        if row >= 0:
            # Temporarily place piece
            board[row][col] = current_player
            if check_win_at_position(board, row, col, current_player):
                board[row][col] = EMPTY  # Restore
                return col  # Take the win!
            board[row][col] = EMPTY  # Restore

    # 2. Check if opponent can win and block them (fast check)
    for col in legal_moves:
        row = get_drop_row(board, col)
        if row >= 0:
            # Temporarily place opponent's piece
            board[row][col] = opponent
            if check_win_at_position(board, row, col, opponent):
                board[row][col] = EMPTY  # Restore
                return col  # Block opponent's winning move!
            board[row][col] = EMPTY  # Restore

    # 3. No immediate wins or blocks, choose randomly
    return random.choice(legal_moves)


def smart_rollout(state, root_player):
    """
    Perform a heuristic-guided simulation (rollout) from the given state.

    This is an improved version of the basic random rollout that uses
    simple heuristics during simulation:
        1. Always take a winning move if available
        2. Always block opponent's winning move
        3. Otherwise choose randomly

    This produces more realistic game outcomes and helps MCTS
    converge faster to good moves.

    Arguments:
        state: Connect4State from which to start simulation
        root_player: the player we consider as "our" perspective

    Returns:
        1.0 if root_player wins
        0.0 if opponent wins
        0.5 if draw
    """
    temp_state = state.clone()

    while not temp_state.is_terminal():
        legal_moves = temp_state.get_legal_moves()
        if not legal_moves:
            break

        # Use smart move selection instead of random
        move = select_smart_move(temp_state, legal_moves)
        temp_state.make_move(move)

    winner, _ = temp_state.check_winner()
    if winner is None:
        return 0.5
    if winner == root_player:
        return 1.0
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
                # Pure MCTS: select untried move uniformly at random
                # This ensures unbiased exploration of the game tree
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
        # Use smart rollout with win/block detection for better estimates
        reward = smart_rollout(state, root_player)

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
                # Pure MCTS: select untried move uniformly at random
                # This ensures unbiased exploration of the game tree
                move = random.choice(untried_moves)
                state.make_move(move)
                child_node = MCTSNode(state.clone(), parent=node, move=move)
                node.children.append(child_node)
                node = child_node

        # SIMULATION - use smart rollout for better estimates
        reward = smart_rollout(state, root_player)

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


def mcts_search_optimized(root_state, n_iter=400, tree_manager=None, 
                          use_adaptive_iterations=True, opponent_last_move=None,
                          use_fast_rollout=True):
    """
    Ultra-optimized MCTS search for AI v AI with maximum performance.
    
    Optimizations:
    1. Tree Reuse: Reuses subtree from opponent's move
    2. Adaptive Iterations: Reduces iterations for simple positions
    3. Forced Move Detection: Instantly returns winning moves
    4. Fast Rollout: Uses raw board operations without state objects
    5. Minimal Cloning: Only clones when absolutely necessary
    
    Arguments:
        root_state: The current game state from which we search.
        n_iter: Base number of MCTS iterations.
        tree_manager: MCTSTreeManager instance for tree reuse (optional).
        use_adaptive_iterations: If True, adjust iterations based on position.
        opponent_last_move: The move opponent just made (for tree reuse).
        use_fast_rollout: If True, use ultra-fast random rollout (faster but less accurate).
    
    Returns:
        The column index of the suggested move, or None if no legal move.
    """
    if root_state.is_terminal():
        return None
    
    root_player = root_state.current_player
    root_board = root_state.board
    
    # Check for forced moves first (immediate win or must-block)
    forced_move, is_winning = detect_forced_move(root_state)
    if is_winning and forced_move is not None:
        if tree_manager:
            tree_manager.clear()
        return forced_move
    
    # Adjust iterations based on position complexity
    actual_iterations = n_iter
    if use_adaptive_iterations:
        multiplier = estimate_position_complexity(root_state)
        actual_iterations = max(40, int(n_iter * multiplier))
    
    # Try to reuse tree from previous search
    root_node = None
    if tree_manager and opponent_last_move is not None:
        root_node = tree_manager.get_reusable_root(opponent_last_move)
        if root_node is not None:
            root_node.state = root_state.clone()
            actual_iterations = max(40, int(actual_iterations * 0.6))
    
    if root_node is None:
        root_node = MCTSNode(root_state.clone())
    
    # Pre-compute for the loop
    cols = len(root_board[0])
    
    # Run MCTS iterations with minimal object creation
    for _ in range(actual_iterations):
        node = root_node
        
        # Use list to track moves made (for reconstruction) instead of cloning
        moves_made = []
        current_player = root_player
        
        # SELECTION - traverse tree using move list
        while node.children and node.is_fully_expanded():
            if node.state.is_terminal():
                break
            node = node.best_child()
            if node.move is not None:
                moves_made.append(node.move)
                current_player = PLAYER1 if current_player == PLAYER2 else PLAYER2
        
        # Create simulation board by replaying moves (cheaper than cloning each iteration)
        sim_board = fast_copy_board(root_board)
        sim_player = root_player
        for m in moves_made:
            fast_make_move(sim_board, m, sim_player)
            sim_player = PLAYER1 if sim_player == PLAYER2 else PLAYER2
        
        # EXPANSION
        if not node.state.is_terminal():
            legal_moves = fast_get_legal_moves(sim_board)
            existing_moves = {child.move for child in node.children}
            untried_moves = [m for m in legal_moves if m not in existing_moves]
            
            if untried_moves:
                move = random.choice(untried_moves)
                row = fast_make_move(sim_board, move, sim_player)
                sim_player = PLAYER1 if sim_player == PLAYER2 else PLAYER2
                
                # Create child node (need state object for tree structure)
                child_state = Connect4State(sim_board, sim_player)
                child_node = MCTSNode(child_state, parent=node, move=move)
                node.children.append(child_node)
                node = child_node
        
        # SIMULATION - use fast rollout on raw board
        if use_fast_rollout:
            reward = fast_rollout(sim_board, sim_player, root_player)
        else:
            reward = fast_smart_rollout(sim_board, sim_player, root_player)
        
        # BACKPROPAGATION
        while node is not None:
            node.visits += 1
            node.wins += reward
            node = node.parent
    
    # Select best move
    best_child = root_node.most_visited_child()
    if best_child is None:
        return None
    
    selected_move = best_child.move
    
    if tree_manager:
        tree_manager.store_root(root_node, selected_move)
    
    return selected_move


def mcts_search_optimized_with_stats(root_state, n_iter=400, tree_manager=None,
                                      use_adaptive_iterations=True, opponent_last_move=None,
                                      use_fast_rollout=True):
    """
    Ultra-optimized MCTS search that also returns statistics for debug panel.
    
    Same optimizations as mcts_search_optimized plus returns root_node for stats.
    
    Returns:
        Tuple (root_node, root_player, actual_iterations) where:
        - root_node: The MCTSNode root containing all children statistics
        - root_player: The player who was about to move
        - actual_iterations: Number of iterations actually performed
        Returns (None, None, 0) if game is terminal.
    """
    if root_state.is_terminal():
        return None, None, 0
    
    root_player = root_state.current_player
    root_board = root_state.board
    
    # Check for forced winning move
    forced_move, is_winning = detect_forced_move(root_state)
    
    # Adjust iterations based on position complexity
    actual_iterations = n_iter
    if use_adaptive_iterations:
        multiplier = estimate_position_complexity(root_state)
        actual_iterations = max(40, int(n_iter * multiplier))
    
    # Try to reuse tree from previous search
    root_node = None
    if tree_manager and opponent_last_move is not None:
        root_node = tree_manager.get_reusable_root(opponent_last_move)
        if root_node is not None:
            root_node.state = root_state.clone()
            actual_iterations = max(40, int(actual_iterations * 0.6))
    
    if root_node is None:
        root_node = MCTSNode(root_state.clone())
    
    # Run MCTS iterations with minimal object creation
    for _ in range(actual_iterations):
        node = root_node
        moves_made = []
        current_player = root_player
        
        # SELECTION
        while node.children and node.is_fully_expanded():
            if node.state.is_terminal():
                break
            node = node.best_child()
            if node.move is not None:
                moves_made.append(node.move)
                current_player = PLAYER1 if current_player == PLAYER2 else PLAYER2
        
        # Create simulation board
        sim_board = fast_copy_board(root_board)
        sim_player = root_player
        for m in moves_made:
            fast_make_move(sim_board, m, sim_player)
            sim_player = PLAYER1 if sim_player == PLAYER2 else PLAYER2
        
        # EXPANSION
        if not node.state.is_terminal():
            legal_moves = fast_get_legal_moves(sim_board)
            existing_moves = {child.move for child in node.children}
            untried_moves = [m for m in legal_moves if m not in existing_moves]
            
            if untried_moves:
                move = random.choice(untried_moves)
                row = fast_make_move(sim_board, move, sim_player)
                sim_player = PLAYER1 if sim_player == PLAYER2 else PLAYER2
                
                child_state = Connect4State(sim_board, sim_player)
                child_node = MCTSNode(child_state, parent=node, move=move)
                node.children.append(child_node)
                node = child_node
        
        # SIMULATION
        if use_fast_rollout:
            reward = fast_rollout(sim_board, sim_player, root_player)
        else:
            reward = fast_smart_rollout(sim_board, sim_player, root_player)
        
        # BACKPROPAGATION
        while node is not None:
            node.visits += 1
            node.wins += reward
            node = node.parent
    
    return root_node, root_player, actual_iterations
