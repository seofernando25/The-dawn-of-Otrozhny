"""Configuration constants for the game."""

from .entity_config import (
    ENEMY_CONFIG,
    PLAYER_CONFIG,
    ENTITY_DEFAULTS,
)
from .gameplay_config import (
    COLLISION_DISTANCES,
    ENEMY_STATUS_TIMERS,
    DAMAGE_CONFIG,
    SOUND_CONFIG,
)
from .editor_config import EDITOR_CONFIG

__all__ = [
    "ENEMY_CONFIG",
    "PLAYER_CONFIG",
    "ENTITY_DEFAULTS",
    "COLLISION_DISTANCES",
    "ENEMY_STATUS_TIMERS",
    "DAMAGE_CONFIG",
    "SOUND_CONFIG",
    "EDITOR_CONFIG",
]

