"""
Perlin Noise Generator
A pure Python implementation of 2D Perlin Noise.
"""

import math
import random

class PerlinNoise:
    def __init__(self, seed=None):
        """
        Initialize the Perlin Noise generator.
        
        Args:
            seed: Optional random seed for reproducible noise
        """
        if seed is not None:
            random.seed(seed)
            
        self.perm = list(range(256))
        random.shuffle(self.perm)
        self.perm += self.perm  # Duplicate to avoid overflow wrapping
        
    def _fade(self, t):
        """Fade function: 6t^5 - 15t^4 + 10t^3"""
        return t * t * t * (t * (t * 6 - 15) + 10)
        
    def _lerp(self, t, a, b):
        """Linear interpolation"""
        return a + t * (b - a)
        
    def _grad(self, hash_val, x, y):
        """
        Calculate gradient dot product.
        Picks a gradient vector based on the hash value and computes dot product
        with the distance vector (x, y).
        """
        h = hash_val & 15
        # Convert lower 4 bits of hash into 12 gradient directions
        u = x if h < 8 else y
        v = y if h < 4 else (x if h == 12 or h == 14 else 0)
        return (u if (h & 1) == 0 else -u) + (v if (h & 2) == 0 else -v)
        
    def noise(self, x, y):
        """
        Generate 2D Perlin noise value for coordinates (x, y).
        
        Args:
            x, y: Float coordinates
            
        Returns:
            Noise value approximately between -1.0 and 1.0
        """
        # Determine grid cell coordinates
        X = int(math.floor(x)) & 255
        Y = int(math.floor(y)) & 255
        
        # Relative x, y in the cell
        x -= math.floor(x)
        y -= math.floor(y)
        
        # Compute fade curves for x, y
        u = self._fade(x)
        v = self._fade(y)
        
        # Hash coordinates of the 4 square corners
        A = self.perm[X] + Y
        B = self.perm[X + 1] + Y
        
        # Add blended results from 4 corners of the square
        return self._lerp(v, 
                   self._lerp(u, self._grad(self.perm[A], x, y),
                               self._grad(self.perm[B], x - 1, y)),
                   self._lerp(u, self._grad(self.perm[A + 1], x, y - 1),
                               self._grad(self.perm[B + 1], x - 1, y - 1)))
                               
    def generate_octave_noise(self, x, y, octaves=4, persistence=0.5, lacunarity=2.0):
        """
        Generate fractal noise by combining multiple octaves of Perlin noise.
        
        Args:
            x, y: Coordinates
            octaves: Number of layers of noise to combine
            persistence: How much amplitude decreases each octave (0-1)
            lacunarity: How much frequency increases each octave
            
        Returns:
            Combined noise value
        """
        total = 0
        frequency = 1
        amplitude = 1
        max_value = 0  # Used for normalizing result
        
        for _ in range(octaves):
            total += self.noise(x * frequency, y * frequency) * amplitude
            max_value += amplitude
            
            amplitude *= persistence
            frequency *= lacunarity
            
        return total / max_value
