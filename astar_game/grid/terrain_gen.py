"""
Terrain generation using Perlin Noise.
Creates organic, smooth terrain layouts.
"""

import random
from astar_game.config import (
    ROWS, COLS,
    TERRAIN_GRASS, TERRAIN_WATER, TERRAIN_MUD, TERRAIN_WALL,
)
from astar_game.grid.perlin import PerlinNoise
from astar_game.astar import run_astar

def generate_perlin_terrain(start, goal, max_attempts=10, scale=0.1, octaves=4):
    """
    Generate terrain using Perlin Noise.
    
    Args:
        start: (row, col) tuple for start position
        goal: (row, col) tuple for goal position
        max_attempts: Number of retries if path doesn't exist
        scale: Zoom level of the noise (smaller = larger features)
        octaves: Detail level of noise
        
    Returns:
        Dictionary mapping (row, col) -> terrain_type
    """
    
    # Thresholds for terrain types based on noise value (-1.0 to 1.0)
    # Adjust these to change the ratio of terrain
    # Typical noise distribution is bell-shaped centered at 0
    
    # Deep water: very low
    THRES_WATER = -0.25
    # Mud: transition from water to grass
    THRES_MUD = -0.15
    # Grass: main ground
    # Walls: high peaks (lowered to increase wall density)
    THRES_WALL = 0.1 
    
    for attempt in range(max_attempts):
        # New seed for each attempt
        seed = random.randint(0, 100000)
        p = PerlinNoise(seed=seed)
        
        terrain = {}
        
        # Random offsets to sample different parts of noise space
        offset_x = random.random() * 1000
        offset_y = random.random() * 1000
        
        for r in range(ROWS):
            for c in range(COLS):
                # Sample noise
                # Multiply by scale to zoom in/out
                val = p.generate_octave_noise(
                    (r * scale) + offset_x, 
                    (c * scale) + offset_y, 
                    octaves=octaves
                )
                
                # Determine terrain type
                if val < THRES_WATER:
                    t_type = TERRAIN_WATER
                elif val < THRES_MUD:
                    t_type = TERRAIN_MUD
                elif val < THRES_WALL:
                    t_type = TERRAIN_GRASS
                else:
                    t_type = TERRAIN_WALL
                    
                terrain[(r, c)] = t_type
        
        # Ensure start and goal are always grass and safe
        terrain[start] = TERRAIN_GRASS
        terrain[goal] = TERRAIN_GRASS
        
        # Clear a small area around start/goal to ensure they aren't trapped immediately
        for dr in [-1, 0, 1]:
            for dc in [-1, 0, 1]:
                nr, nc = start[0] + dr, start[1] + dc
                if 0 <= nr < ROWS and 0 <= nc < COLS:
                    terrain[(nr, nc)] = TERRAIN_GRASS
                    
                nr, nc = goal[0] + dr, goal[1] + dc
                if 0 <= nr < ROWS and 0 <= nc < COLS:
                    terrain[(nr, nc)] = TERRAIN_GRASS

        # Validate path
        from astar_game.config import ALLOW_DIAGONAL_NEIGHBORS
        path, _ = run_astar(start, goal, terrain, ALLOW_DIAGONAL_NEIGHBORS)
        
        if path is not None:
            return terrain
            
    # Fallback to all grass if generation fails
    return {(r, c): TERRAIN_GRASS for r in range(ROWS) for c in range(COLS)}
