"""
Movement utilities - shared movement logic for entities.

Consolidates collision detection, movement, and steering logic used by Player and Enemy classes.

This module provides pure calculation functions - no input reading is done here.
Input reading should be handled by the InputSystem.
"""

import math
from typing import Protocol, cast

from config import renderer_config
from utils import math_helpers
from utils.math_helpers import HasPosition


class SupportsAgent(Protocol):
    dirX: float
    dirY: float
    moveSpeed: float
    cameraYawSens: float
    cameraPitchSens: float
    angleY: float

    def rotate(self, amount: float) -> None: ...

    def get_pos(self) -> tuple[float, float]: ...


def calculate_movement_vector(
    entity: SupportsAgent,
    dt: float,
    move_forward: bool = False,
    move_backward: bool = False,
    move_left: bool = False,
    move_right: bool = False,
) -> tuple[float, float]:
    """Calculate movement vector from boolean input flags."""
    newPx = 0.0
    newPy = 0.0
    angle = math.atan2(-entity.dirY, entity.dirX)

    # Movement input
    if move_right:
        newPx -= math.sin(angle) * 2 * dt
        newPy -= math.cos(angle) * 2 * dt

    if move_left:
        newPx += math.sin(angle) * entity.moveSpeed * dt
        newPy += math.cos(angle) * entity.moveSpeed * dt

    if move_forward:
        newPx += math.cos(angle) * entity.moveSpeed * dt
        newPy -= math.sin(angle) * entity.moveSpeed * dt

    if move_backward:
        newPx -= math.cos(angle) * entity.moveSpeed * dt
        newPy += math.sin(angle) * entity.moveSpeed * dt

    return newPx, newPy


def apply_mouse_look(
    entity: SupportsAgent,
    dt: float,
    mouse_delta_x: float,
    mouse_delta_y: float,
    screen_center_x: float,
    screen_center_y: float,
) -> None:
    """Apply mouse look rotation to entity."""
    _ = screen_center_x
    _ = screen_center_y
    entity.rotate(-entity.cameraYawSens * 0.05 * dt * mouse_delta_x)
    entity.angleY -= 0.05 * dt * entity.cameraPitchSens * mouse_delta_y

    # Clamp vertical angle
    entity.angleY = math_helpers.clamp(
        entity.angleY,
        -renderer_config.VIEWPORT_HEIGHT,
        renderer_config.VIEWPORT_HEIGHT,
    )


def apply_keyboard_rotation(
    entity: SupportsAgent,
    dt: float,
    rotate_left: bool = False,
    rotate_right: bool = False,
    pitch_up: bool = False,
    pitch_down: bool = False,
) -> None:
    """Apply keyboard-based rotation to entity."""
    if rotate_left:
        entity.rotate(entity.cameraYawSens * dt)

    if rotate_right:
        entity.rotate(-entity.cameraYawSens * dt)

    if pitch_up:
        entity.angleY += entity.cameraPitchSens * dt

    if pitch_down:
        entity.angleY -= entity.cameraPitchSens * dt

    # Clamp vertical angle
    entity.angleY = math_helpers.clamp(
        entity.angleY,
        -renderer_config.VIEWPORT_HEIGHT,
        renderer_config.VIEWPORT_HEIGHT,
    )


def move_to_target(
    entity: SupportsAgent,
    target: HasPosition | tuple[float, float],
    dt: float,
) -> tuple[float, float]:
    """Return the movement vector that would move the entity toward the given target."""
    if isinstance(target, tuple):
        target_pos = cast(tuple[float, float], target)
    else:
        target_pos = target.get_pos()

    dx, dy = math_helpers.slope(entity.get_pos(), target_pos)
    targetDistance = math.hypot(dx, dy)

    if targetDistance > 0.5:
        # Normalize direction and scale by move speed
        move_distance = entity.moveSpeed * dt
        norm_dx = dx / targetDistance * move_distance
        norm_dy = dy / targetDistance * move_distance
        return norm_dx, norm_dy

    return 0.0, 0.0


def look_at(
    entity: SupportsAgent,
    target: HasPosition | tuple[float, float],
    dt: float,
    turn_speed: float | None = None,
) -> None:
    """Rotate the entity toward the target, optionally clamping turn speed."""
    if isinstance(target, tuple):
        target_pos = cast(tuple[float, float], target)
    else:
        target_pos = target.get_pos()

    dx, dy = math_helpers.slope(entity.get_pos(), target_pos)
    target_angle = math.atan2(dy, dx)

    # Get current entity angle from direction vector
    current_angle = math.atan2(entity.dirY, entity.dirX)

    # Calculate shortest rotation direction
    angle_diff = target_angle - current_angle
    angle_diff = (angle_diff + math.pi) % (2 * math.pi) - math.pi

    # Apply rotation
    speed = turn_speed if turn_speed is not None else entity.cameraYawSens * dt * 2
    if abs(angle_diff) < speed:
        # Rotate to exact target angle
        entity.rotate(angle_diff)
    else:
        entity.rotate(math.copysign(speed, angle_diff))
