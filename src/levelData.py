

from __future__ import annotations

from typing import Optional

import numpy as np

from entities.items import Collectible
from entities.player import Player


class Level():
    currentMap: Optional["Level"] = None

    def __init__(self, grid, grid_entities, node_entities=None, grid_np=None):
        self.grid = grid
        self.grid_np = grid_np if grid_np is not None else np.array(
            grid, dtype=np.int16)
        self.grid_entities = grid_entities
        self.node_entities = node_entities
        self.level_width = len(grid[0]) 
        self.level_height = len(grid) 

        # Sorry I did not had time to organize it in a better way :/
        self.num_of_collectibles = sum(isinstance(x, Collectible) for x in self.grid_entities)
        self.num_of_collected = 0
        Player.instance = next(
            (x for x in self.grid_entities if isinstance(x, Player)),
            None)

    @staticmethod
    def load(level_object):
        grid_np = getattr(level_object, "grid_np", None)
        Level.currentMap = Level(level_object.grid, level_object.grid_entities,
                                 getattr(level_object, "node_entities", None),
                                 grid_np=grid_np)
    
  

    def pick_random_point(self):
        import random
        random_w = random.randint(0, self.level_width - 1) 
        random_h = random.randint(0, self.level_height - 1)
        random_position =  (random_w, random_h) 
        if self.grid[random_w] [random_h] != 0:
            while self.grid[random_w] [random_h] != 0:
                random_w = random.randint(0, self.level_width - 1)
                random_h = random.randint(0, self.level_height - 1)
                random_position =  (random_w, random_h) 
        return random_position


def require_current_map() -> Level:
    current_map = Level.currentMap
    if current_map is None:
        raise RuntimeError("Level.currentMap is not set. Call Level.load first.")
    return current_map
    
