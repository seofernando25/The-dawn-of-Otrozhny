"""Entity configuration constants."""

from typing import TypedDict


class EnemyConfig(TypedDict):
    fov_degrees: float
    move_speed: float
    fov_depth: float
    sprite_pack: str
    camera_yaw_sensitivity: float
    alert_fov_multiplier: float
    alert_fov_depth_multiplier: float
    patrol_guard_time: float
    patrol_rotation_speed: float
    pathfinding_node_adjustment: float
    pathfinding_target_distance: float
    retarget_attempts: int
    attack_distance: float
    sound_trigger_distance: float
    attack_damage_per_second: float
    attack_look_speed_multiplier: float
    attack_rotation_range: tuple[float, float]
    attack_angle_range: tuple[float, float]
    node_bias_factor: float


class PlayerConfig(TypedDict):
    fov_degrees: float
    move_speed: float
    camera_yaw_sensitivity: float
    camera_pitch_sensitivity: float
    sprite_pack: str


ENEMY_CONFIG: EnemyConfig = {
    "fov_degrees": 90.0,
    "move_speed": 2.0,
    "fov_depth": 6.0,
    "sprite_pack": "droog",
    "camera_yaw_sensitivity": 4.0,
    "alert_fov_multiplier": 1.5,
    "alert_fov_depth_multiplier": 1.5,
    "patrol_guard_time": 1.0,
    "patrol_rotation_speed": 36.0,
    "pathfinding_node_adjustment": 0.5,
    "pathfinding_target_distance": 0.5,
    "retarget_attempts": 10,
    "attack_distance": 3.0,
    "sound_trigger_distance": 5.0,
    "attack_damage_per_second": 30.0,
    "attack_look_speed_multiplier": 2.0,
    "attack_rotation_range": (-3.0, 3.0),
    "attack_angle_range": (-400.0, 400.0),
    "node_bias_factor": 0.5,
}

PLAYER_CONFIG: PlayerConfig = {
    "fov_degrees": 90.0,
    "move_speed": 2.0,
    "camera_yaw_sensitivity": 2.0,
    "camera_pitch_sensitivity": 360.0,
    "sprite_pack": "enemyIdle",
}

ENTITY_DEFAULTS: dict[str, float] = {
    "health": 100.0,
    "plane_y": 0.66,
    "move_to_look_speed_multiplier": 2.0,
}
