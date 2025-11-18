from typing import Optional, Tuple
from core.context import GameContext
from core.game_state import GameState


class GameplaySystem:
    """Handles all gameplay logic including entity updates and win/lose conditions."""

    def __init__(self, context: GameContext):
        self.context = context
        self.time = 0.0

    def initialize(self):
        """Initialize the gameplay system."""
        player = self.context.player
        if player is None:
            raise RuntimeError("GameContext.player is not set.")
        
        player.keys = 0
        
        # Get or ensure enemy state manager is initialized
        enemy_state = self.context.ensure_enemy_state()
        enemy_state.reset()
        self.time = 0.0

    def update(self, delta_time: float, events: list) -> Optional[Tuple[GameState, Optional[float]]]:
        """Update all gameplay systems."""
        self.time += delta_time
        
        player = self.context.player
        if player is None:
            raise RuntimeError("GameContext.player is not set.")
        
        current_map = self.context.level
        if current_map is None:
            raise RuntimeError("GameContext.level is not set.")
        
        # Get enemy state from context
        enemy_state = self.context.enemy_state
        if enemy_state is None:
            raise RuntimeError("GameContext.enemy_state is not set.")
        
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

