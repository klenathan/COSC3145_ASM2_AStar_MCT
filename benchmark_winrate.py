"""
AI vs AI Win Rate Benchmark for Connect 4 MCTS

This script simulates multiple AI vs AI matches to calculate win rates and statistics.
It allows you to test different MCTS configurations and analyze performance.

Usage:
    python benchmark_winrate.py -n 100                    # Run 100 matches with default settings
    python benchmark_winrate.py -n 50 --p1-iter 500       # Player 1 with 500 iterations
    python benchmark_winrate.py -n 100 --p1-iter 500 --p2-iter 200  # Different iterations
    python benchmark_winrate.py -n 100 --no-opt            # Disable optimizations
    python benchmark_winrate.py -n 100 --verbose           # Show detailed match info
"""

import argparse
import sys
import time
from collections import defaultdict
from connect4.state import Connect4State
from connect4.ai_agent import AIAgent
from connect4.config import PLAYER1, PLAYER2


class BenchmarkStats:
    """Track statistics for AI vs AI benchmark."""
    
    def __init__(self):
        self.total_matches = 0
        self.p1_wins = 0
        self.p2_wins = 0
        self.draws = 0
        self.total_moves = 0
        self.total_time = 0.0
        self.match_times = []
        self.match_moves = []
        
    def record_match(self, winner, num_moves, match_time):
        """Record the result of a single match."""
        self.total_matches += 1
        
        if winner == PLAYER1:
            self.p1_wins += 1
        elif winner == PLAYER2:
            self.p2_wins += 1
        else:
            self.draws += 1
        
        self.total_moves += num_moves
        self.total_time += match_time
        self.match_times.append(match_time)
        self.match_moves.append(num_moves)
    
    def get_summary(self):
        """Get summary statistics as a dictionary."""
        if self.total_matches == 0:
            return {}
        
        return {
            'total_matches': self.total_matches,
            'p1_wins': self.p1_wins,
            'p2_wins': self.p2_wins,
            'draws': self.draws,
            'p1_win_rate': (self.p1_wins / self.total_matches) * 100,
            'p2_win_rate': (self.p2_wins / self.total_matches) * 100,
            'draw_rate': (self.draws / self.total_matches) * 100,
            'avg_moves': self.total_moves / self.total_matches,
            'avg_time': self.total_time / self.total_matches,
            'total_time': self.total_time,
            'min_time': min(self.match_times) if self.match_times else 0,
            'max_time': max(self.match_times) if self.match_times else 0,
            'min_moves': min(self.match_moves) if self.match_moves else 0,
            'max_moves': max(self.match_moves) if self.match_moves else 0,
        }


def simulate_match(agent1, agent2, verbose=False):
    """
    Simulate a single AI vs AI match.
    
    Arguments:
        agent1: AIAgent for Player 1
        agent2: AIAgent for Player 2
        verbose: If True, print move-by-move details
    
    Returns:
        Tuple (winner, num_moves, match_time) where:
        - winner: PLAYER1, PLAYER2, or None (draw)
        - num_moves: Total number of moves in the match
        - match_time: Time taken for the match in seconds
    """
    # Reset agents for new game
    agent1.reset()
    agent2.reset()
    
    # Initialize game state
    state = Connect4State()
    num_moves = 0
    start_time = time.time()
    
    # Play until game is over
    while not state.is_terminal():
        # Get current player's agent
        current_agent = agent1 if state.current_player == PLAYER1 else agent2
        
        # Get move from agent
        move = current_agent.get_move(state)
        
        if move is None:
            # No legal moves (shouldn't happen in Connect 4)
            break
        
        if verbose:
            print(f"Move {num_moves + 1}: Player {state.current_player} plays column {move}")
        
        # Make the move
        state.make_move(move)
        num_moves += 1
        
        # Notify opponent about the move for tree reuse
        opponent_agent = agent2 if state.current_player == PLAYER1 else agent1
        opponent_agent.notify_opponent_move(move)
    
    match_time = time.time() - start_time
    
    # Determine winner
    winner, _ = state.check_winner()
    
    if verbose:
        if winner:
            print(f"Player {winner} wins in {num_moves} moves! ({match_time:.2f}s)")
        else:
            print(f"Draw after {num_moves} moves! ({match_time:.2f}s)")
        print()
    
    return winner, num_moves, match_time


def run_benchmark(n_matches, p1_iterations, p2_iterations, use_optimizations, verbose):
    """
    Run AI vs AI benchmark for n matches.
    
    Arguments:
        n_matches: Number of matches to simulate
        p1_iterations: MCTS iterations for Player 1
        p2_iterations: MCTS iterations for Player 2
        use_optimizations: Whether to use MCTS optimizations
        verbose: Whether to print detailed match information
    
    Returns:
        BenchmarkStats object with all statistics
    """
    print("=" * 70)
    print("AI vs AI Win Rate Benchmark - Connect 4 MCTS")
    print("=" * 70)
    print(f"Configuration:")
    print(f"  Total Matches: {n_matches}")
    print(f"  Player 1 Iterations: {p1_iterations}")
    print(f"  Player 2 Iterations: {p2_iterations}")
    print(f"  Optimizations: {'Enabled' if use_optimizations else 'Disabled'}")
    print("=" * 70)
    print()
    
    # Create AI agents
    agent1 = AIAgent(n_iter=p1_iterations, player_id=PLAYER1, use_optimizations=use_optimizations)
    agent2 = AIAgent(n_iter=p2_iterations, player_id=PLAYER2, use_optimizations=use_optimizations)
    
    # Track statistics
    stats = BenchmarkStats()
    
    # Run matches
    for match_num in range(1, n_matches + 1):
        if not verbose:
            # Show progress for non-verbose mode
            print(f"Running match {match_num}/{n_matches}...", end='\r')
        else:
            print(f"\n{'=' * 70}")
            print(f"Match {match_num}/{n_matches}")
            print(f"{'=' * 70}")
        
        winner, num_moves, match_time = simulate_match(agent1, agent2, verbose)
        stats.record_match(winner, num_moves, match_time)
    
    if not verbose:
        print()  # New line after progress indicator
    
    return stats


def print_results(stats):
    """Print formatted benchmark results."""
    summary = stats.get_summary()
    
    if not summary:
        print("No matches completed.")
        return
    
    print("\n" + "=" * 70)
    print("BENCHMARK RESULTS")
    print("=" * 70)
    print()
    
    print("Win Statistics:")
    print(f"  Total Matches:  {summary['total_matches']}")
    print(f"  Player 1 Wins:  {summary['p1_wins']:4d} ({summary['p1_win_rate']:5.2f}%)")
    print(f"  Player 2 Wins:  {summary['p2_wins']:4d} ({summary['p2_win_rate']:5.2f}%)")
    print(f"  Draws:          {summary['draws']:4d} ({summary['draw_rate']:5.2f}%)")
    print()
    
    print("Game Statistics:")
    print(f"  Average Moves per Game:  {summary['avg_moves']:.2f}")
    print(f"  Move Range:              {summary['min_moves']} - {summary['max_moves']}")
    print()
    
    print("Performance Statistics:")
    print(f"  Total Time:              {summary['total_time']:.2f}s")
    print(f"  Average Time per Game:   {summary['avg_time']:.2f}s")
    print(f"  Time Range:              {summary['min_time']:.2f}s - {summary['max_time']:.2f}s")
    print(f"  Games per Minute:        {60 / summary['avg_time']:.2f}")
    print()
    
    # Determine if there's a significant advantage
    if summary['p1_wins'] > summary['p2_wins']:
        advantage = summary['p1_win_rate'] - summary['p2_win_rate']
        print(f"Player 1 has a {advantage:.2f}% advantage")
    elif summary['p2_wins'] > summary['p1_wins']:
        advantage = summary['p2_win_rate'] - summary['p1_win_rate']
        print(f"Player 2 has a {advantage:.2f}% advantage")
    else:
        print("Players are evenly matched")
    
    print("=" * 70)


def main():
    """Main entry point for benchmark script."""
    parser = argparse.ArgumentParser(
        description='Benchmark AI vs AI win rates for Connect 4 MCTS',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s -n 100                           # Run 100 matches with default settings
  %(prog)s -n 50 --p1-iter 500              # Player 1 with 500 iterations
  %(prog)s -n 100 --p1-iter 500 --p2-iter 200  # Different iterations for each player
  %(prog)s -n 100 --no-opt                  # Disable optimizations
  %(prog)s -n 100 --verbose                 # Show detailed match information
        """
    )
    
    parser.add_argument(
        '-n', '--matches',
        type=int,
        required=True,
        help='Number of matches to simulate'
    )
    
    parser.add_argument(
        '--p1-iter',
        type=int,
        default=200,
        help='MCTS iterations for Player 1 (default: 200)'
    )
    
    parser.add_argument(
        '--p2-iter',
        type=int,
        default=200,
        help='MCTS iterations for Player 2 (default: 200)'
    )
    
    parser.add_argument(
        '--no-opt',
        action='store_true',
        help='Disable MCTS optimizations (tree reuse, adaptive iterations, etc.)'
    )
    
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Print detailed information for each match'
    )
    
    args = parser.parse_args()
    
    # Validate arguments
    if args.matches <= 0:
        print("Error: Number of matches must be positive")
        sys.exit(1)
    
    if args.p1_iter <= 0 or args.p2_iter <= 0:
        print("Error: Iterations must be positive")
        sys.exit(1)
    
    # Run benchmark
    try:
        stats = run_benchmark(
            n_matches=args.matches,
            p1_iterations=args.p1_iter,
            p2_iterations=args.p2_iter,
            use_optimizations=not args.no_opt,
            verbose=args.verbose
        )
        
        # Print results
        print_results(stats)
        
    except KeyboardInterrupt:
        print("\n\nBenchmark interrupted by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n\nError during benchmark: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
