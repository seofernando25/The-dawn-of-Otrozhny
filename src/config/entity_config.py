"""Entity configuration constants."""

# Enemy configuration
ENEMY_CONFIG: dict[str, object] = {
    "fov_degrees": 90,
    "move_speed": 2,
    "fov_depth": 6,
    "sprite_pack": "droog",
    "camera_yaw_sensitivity": 4,
    "alert_fov_multiplier": 1.5,  # FOV multiplier when in alert states
    "alert_fov_depth_multiplier": 1.5,  # FOV depth multiplier when in alert states
    "patrol_guard_time": 1.0,  # Time to guard a patrol point
    "patrol_rotation_speed": 36,  # Degrees per second when guarding
    "pathfinding_node_adjustment": 0.5,  # Offset for pathfinding nodes
    "pathfinding_target_distance": 0.5,  # Distance threshold for reaching target
    "retarget_attempts": 10,  # Max attempts to find valid retarget point
    "attack_distance": 3,  # Distance to start attacking player
    "sound_trigger_distance": 5,  # Distance to trigger sound effects
    "attack_damage_per_second": 30,  # Damage dealt per second when attacking
    "attack_look_speed_multiplier": 2,  # Look speed multiplier during attack
    "attack_rotation_range": (-3, 3),  # Random rotation range during attack
    "attack_angle_range": (-400, 400),  # Random angle range during attack
    "node_bias_factor": 0.5,  # Bias factor for random node selection
}

# Player configuration
PLAYER_CONFIG: dict[str, object] = {
    "fov_degrees": 90,
    "move_speed": 2,
    "camera_yaw_sensitivity": 2,
    "camera_pitch_sensitivity": 360,
    "sprite_pack": "enemyIdle",
}

# Default entity values
ENTITY_DEFAULTS: dict[str, float | int] = {
    "health": 100,
    "plane_y": 0.66,  # Camera plane Y component
    "move_to_look_speed_multiplier": 2,  # Look speed multiplier when moving to target
}
