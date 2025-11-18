from __future__ import annotations

from typing import TYPE_CHECKING, List, Optional, Sequence

import numpy as np

from entities.items import Collectible
from entities.player import Player

if TYPE_CHECKING:
    from core.context import GameContext
    from entities.base import Entity
    from entities.node import Node


class Level:
    def __init__(
        self,
        grid: Sequence[Sequence[int]],
        grid_entities: Sequence["Entity"],
        node_entities: Optional[Sequence["Node"]] = None,
        grid_np: Optional[np.ndarray] = None,
    ):
        self.grid = grid
        self.grid_np = (
            grid_np if grid_np is not None else np.array(grid, dtype=np.int16)
        )
        self.grid_entities: List["Entity"] = list(grid_entities)
        self.node_entities: List["Node"] = (
            list(node_entities) if node_entities is not None else []
        )
        self.level_width = len(grid[0])
        self.level_height = len(grid)

        self.num_of_collectibles = sum(
            isinstance(x, Collectible) for x in self.grid_entities
        )
        self.num_of_collected = 0

    @staticmethod
    def load(level_object, *, context: "GameContext"):
        """Load a level and attach the provided context to all entities."""
        level = Level(
            level_object.grid,
            level_object.grid_entities,
            level_object.node_entities,
            grid_np=level_object.grid_np,
        )
        level.attach_context(context)
        return level

    def attach_context(self, context: "GameContext"):
        """Attach the shared context to level entities and cache references."""
        # Type: ignore needed because self is Level, and update_level expects Level
        context.update_level(self)  # type: ignore[arg-type]
        for entity in self.grid_entities:
            entity.set_context(context)
        player = next((x for x in self.grid_entities if isinstance(x, Player)), None)
        if player is not None and context.player is None:
            context.update_player(player)

    def pick_random_point(self):
        """Pick a random empty point in the level grid."""
        import random

        max_attempts = self.level_width * self.level_height * 2
        attempts = 0
        
        while attempts < max_attempts:
            random_w = random.randint(0, self.level_width - 1)
            random_h = random.randint(0, self.level_height - 1)
            if self.grid[random_w][random_h] == 0:
                return (random_w, random_h)
            attempts += 1
        
        raise RuntimeError(
            f"Failed to find empty point in level after {max_attempts} attempts. "
            f"Level may be completely filled with walls."
        )

