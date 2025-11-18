"""Gameplay configuration constants."""

from typing import Dict

# Collision and interaction distances
COLLISION_DISTANCES: Dict[str, float] = {
    "collectible_pickup": 0.5,  # Distance to pick up collectibles
    "key_pickup": 0.5,  # Distance to pick up keys
    "gate_interaction": 0.5,  # Distance to interact with gates
    "gate_knockback": 1.0,  # Distance for gate knockback effect
    "gate_knockback_strength": 0.5,  # Knockback strength multiplier
}

# Enemy status timer values (in seconds)
ENEMY_STATUS_TIMERS: Dict[str, int] = {
    "alert": 10,
    "evasion": 20,
    "caution": 30,
}

# Damage configuration
DAMAGE_CONFIG: Dict[str, float] = {
    "enemy_attack_dps": 30,  # Damage per second from enemy attacks
}

# Sound configuration
SOUND_CONFIG: Dict[str, float] = {
    "volume_min": 0.5,  # Minimum volume for distance-based sounds
    "volume_max": 2.0,  # Maximum volume for distance-based sounds
    "volume_distance_min": 0,  # Minimum distance for volume calculation
    "volume_distance_max": 5,  # Maximum distance for volume calculation
}

