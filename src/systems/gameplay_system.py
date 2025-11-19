from __future__ import annotations

from typing import TYPE_CHECKING, cast

from core.context import GameContext
from core.game_state import GameState
from entities.enemy_state import EnemyStateManager
from entities.player import Player
from level.level import Level

if TYPE_CHECKING:
    from core.backend.api import Event


class GameplaySystem:
    """Handles all gameplay logic including entity updates and win/lose conditions."""

    def __init__(self, context: GameContext):
        self.context: GameContext = context
        self.time: float = 0.0

    def initialize(self):
        """Initialize the gameplay system."""
        player_obj = cast(Player | None, self.context.player)
        if player_obj is None:
            raise RuntimeError("GameContext.player is not set.")
        player = player_obj
        player.keys = 0

        # Get or ensure enemy state manager is initialized
        enemy_state = cast(EnemyStateManager, self.context.ensure_enemy_state())
        enemy_state.reset()
        self.time = 0.0

    def update(
        self,
        delta_time: float,
        _events: list["Event"],
    ) -> tuple[GameState, float | None] | None:
        """Update all gameplay systems."""
        self.time += delta_time

        player_obj = cast(Player | None, self.context.player)
        if player_obj is None:
            raise RuntimeError("GameContext.player is not set.")
        player = player_obj

        current_map_obj = cast(Level | None, self.context.level)
        if current_map_obj is None:
            raise RuntimeError("GameContext.level is not set.")
        current_map = current_map_obj

        # Get enemy state from context
        enemy_state_obj = cast(EnemyStateManager | None, self.context.enemy_state)
        if enemy_state_obj is None:
            raise RuntimeError("GameContext.enemy_state is not set.")
        enemy_state = enemy_state_obj

        # Check win/lose conditions
        if player.health <= 0:
            enemy_state.reset()
            return (GameState.Play, None)  # Signal loss, time not needed

        if current_map.num_of_collected == current_map.num_of_collectibles:
            enemy_state.reset()
            return (GameState.Play, self.time)  # Signal win with time

        # Update enemy state
        enemy_state.update(delta_time)

        # Update all entities
        # Note: Player input is handled by InputSystem, not through entity.update()
        for entity in current_map.grid_entities:
            entity.update(delta_time)

        return None
