"""
Gameplay system - handles entity updates, win/lose conditions, and game logic.
"""

from typing import Optional, Tuple
from core.context import GameContext
from core.game_state import GameState
from core.enemy_state import EnemyStateManager


class GameplaySystem:
    """Handles all gameplay logic including entity updates and win/lose conditions."""

    def __init__(self, context: GameContext):
        self.context = context
        self.time = 0.0
        self.enemy_state: Optional[EnemyStateManager] = None

    def initialize(self):
        """Initialize the gameplay system."""
        player = self.context.player
        if player is None:
            raise RuntimeError("GameContext.player is not set.")
        
        player.keys = 0
        
        # Get or ensure enemy state manager is initialized
        self.enemy_state = self.context.ensure_enemy_state()
        self.enemy_state.reset()
        self.time = 0.0

    def update(self, delta_time: float, events: list) -> Optional[Tuple[GameState, Optional[float]]]:
        """Update all gameplay systems and return game state if game should end."""
        self.time += delta_time
        
        player = self.context.player
        if player is None:
            raise RuntimeError("GameContext.player is not set.")
        
        current_map = self.context.level
        if current_map is None:
            raise RuntimeError("GameContext.level is not set.")
        
        # Check win/lose conditions
        if player.health <= 0:
            if self.enemy_state:
                self.enemy_state.reset()
            return (GameState.Play, None)  # Signal loss, time not needed
        
        if current_map.num_of_collected == current_map.num_of_collectibles:
            if self.enemy_state:
                self.enemy_state.reset()
            return (GameState.Play, self.time)  # Signal win with time
        
        # Update enemy state
        if self.enemy_state:
            self.enemy_state.update(delta_time)
        
        # Update all entities
        # Note: Player input is handled by InputSystem, not through entity.update()
        for entity in current_map.grid_entities:
            entity.update(delta_time)
        
        return None

