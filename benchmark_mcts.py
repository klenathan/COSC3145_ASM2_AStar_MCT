#!/usr/bin/env python3
"""
MCTS Performance Benchmark for Connect 4.

This script compares the performance of original vs optimized MCTS implementations.
Run with: python benchmark_mcts.py

Output: Timing comparisons for AI v AI games with and without optimizations.
"""

import time
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from connect4.state import Connect4State
from connect4.ai_agent import AIAgent
from connect4.config import PLAYER1, PLAYER2


def run_benchmark_game(use_optimizations=True, iterations=400, verbose=False):
    """
    Run a full AI vs AI game and measure performance.
    
    Arguments:
        use_optimizations: If True, use optimized MCTS
        iterations: Number of MCTS iterations per move
        verbose: If True, print move-by-move info
    
    Returns:
        dict with timing and game statistics
    """
    state = Connect4State()
    
    ai_agent1 = AIAgent(n_iter=iterations, player_id=PLAYER1, use_optimizations=use_optimizations)
    ai_agent2 = AIAgent(n_iter=iterations, player_id=PLAYER2, use_optimizations=use_optimizations)
    
    move_times = []
    move_count = 0
    
    game_start = time.time()
    
    while not state.is_terminal():
        move_count += 1
        current_player = state.current_player
        
        move_start = time.time()
        
        if current_player == PLAYER1:
            move = ai_agent1.get_move(state)
        else:
            move = ai_agent2.get_move(state)
        
        if move is None:
            break
            
        move_time = time.time() - move_start
        move_times.append(move_time)
        
        if verbose:
            print(f"Move {move_count}: Player {current_player} -> Column {move} ({move_time:.3f}s)")
        
        state.make_move(move)
        
        # Notify opponent for tree reuse
        if current_player == PLAYER1:
            ai_agent2.notify_opponent_move(move)
        else:
            ai_agent1.notify_opponent_move(move)
    
    game_time = time.time() - game_start
    winner, _ = state.check_winner()
    
    return {
        'total_time': game_time,
        'move_count': move_count,
        'avg_move_time': sum(move_times) / len(move_times) if move_times else 0,
        'min_move_time': min(move_times) if move_times else 0,
        'max_move_time': max(move_times) if move_times else 0,
        'winner': winner
    }


def run_benchmark(num_games=3, iterations=400):
    """
    Run the full benchmark comparing original vs optimized MCTS.
    
    Arguments:
        num_games: Number of games to run for each configuration
        iterations: MCTS iterations per move
    """
    print("=" * 60)
    print("MCTS Performance Benchmark for Connect 4")
    print("=" * 60)
    print(f"\nConfiguration: {iterations} iterations per move, {num_games} games each\n")
    
    # Benchmark optimized version
    print("Testing OPTIMIZED MCTS (tree reuse + adaptive iterations)...")
    print("-" * 40)
    
    optimized_results = []
    for i in range(num_games):
        print(f"  Game {i+1}/{num_games}...", end=" ", flush=True)
        result = run_benchmark_game(use_optimizations=True, iterations=iterations)
        optimized_results.append(result)
        print(f"Done ({result['total_time']:.2f}s, {result['move_count']} moves, Winner: P{result['winner'] or 'Draw'})")
    
    # Benchmark original version
    print("\nTesting ORIGINAL MCTS (no optimizations)...")
    print("-" * 40)
    
    original_results = []
    for i in range(num_games):
        print(f"  Game {i+1}/{num_games}...", end=" ", flush=True)
        result = run_benchmark_game(use_optimizations=False, iterations=iterations)
        original_results.append(result)
        print(f"Done ({result['total_time']:.2f}s, {result['move_count']} moves, Winner: P{result['winner'] or 'Draw'})")
    
    # Calculate and display summary
    print("\n" + "=" * 60)
    print("RESULTS SUMMARY")
    print("=" * 60)
    
    def avg(lst, key):
        return sum(r[key] for r in lst) / len(lst)
    
    opt_avg_game = avg(optimized_results, 'total_time')
    orig_avg_game = avg(original_results, 'total_time')
    opt_avg_move = avg(optimized_results, 'avg_move_time')
    orig_avg_move = avg(original_results, 'avg_move_time')
    
    speedup_game = (orig_avg_game - opt_avg_game) / orig_avg_game * 100 if orig_avg_game > 0 else 0
    speedup_move = (orig_avg_move - opt_avg_move) / orig_avg_move * 100 if orig_avg_move > 0 else 0
    
    print(f"\n{'Metric':<25} {'Optimized':>12} {'Original':>12} {'Improvement':>12}")
    print("-" * 63)
    print(f"{'Avg game time (s)':<25} {opt_avg_game:>12.2f} {orig_avg_game:>12.2f} {speedup_game:>11.1f}%")
    print(f"{'Avg move time (s)':<25} {opt_avg_move:>12.3f} {orig_avg_move:>12.3f} {speedup_move:>11.1f}%")
    
    print("\n" + "=" * 60)
    print("Optimizations applied:")
    print("  • Tree reuse between moves")
    print("  • Adaptive iteration count (fewer for simple positions)")
    print("  • Immediate forced move detection (wins/blocks)")
    print("=" * 60)


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="MCTS Performance Benchmark")
    parser.add_argument("-n", "--num-games", type=int, default=3,
                        help="Number of games to run for each configuration (default: 3)")
    parser.add_argument("-i", "--iterations", type=int, default=400,
                        help="MCTS iterations per move (default: 400)")
    
    args = parser.parse_args()
    
    run_benchmark(num_games=args.num_games, iterations=args.iterations)
