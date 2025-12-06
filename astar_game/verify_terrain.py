import sys
import os

# Add the project root to the python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from astar_game.grid.terrain_gen import generate_perlin_terrain
from astar_game.config import DEFAULT_START, DEFAULT_GOAL, ROWS, COLS

def test_terrain_generation():
    print("Testing Perlin Terrain Generation...")
    try:
        terrain = generate_perlin_terrain(DEFAULT_START, DEFAULT_GOAL, max_attempts=5)
        
        # Check size
        assert len(terrain) == ROWS * COLS, f"Expected {ROWS*COLS} cells, got {len(terrain)}"
        
        # Check start and goal are grass
        from astar_game.config import TERRAIN_GRASS
        assert terrain[DEFAULT_START] == TERRAIN_GRASS, "Start must be grass"
        assert terrain[DEFAULT_GOAL] == TERRAIN_GRASS, "Goal must be grass"
        
        # Count terrain types
        counts = {}
        for t in terrain.values():
            counts[t] = counts.get(t, 0) + 1
            
        print("Terrain distribution:")
        for t, count in counts.items():
            print(f"  {t}: {count} ({count/(ROWS*COLS)*100:.1f}%)")
            
        print("SUCCESS: Terrain generated successfully.")
        
    except Exception as e:
        print(f"FAILED: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_terrain_generation()
