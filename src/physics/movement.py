"""
Movement utilities - shared movement logic for entities.

Consolidates collision detection, movement, and steering logic used by Player and Enemy classes.

This module provides pure calculation functions - no input reading is done here.
Input reading should be handled by the InputSystem.
"""

import math
from utils import math_helpers
from config import renderer_config


def calculate_movement_vector(
    entity,
    dt,
    move_forward=False,
    move_backward=False,
    move_left=False,
    move_right=False,
):
    """Calculate movement vector from boolean input flags."""
    newPx = 0
    newPy = 0
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
    entity,
    dt,
    mouse_delta_x,
    mouse_delta_y,
    screen_center_x,
    screen_center_y,
):
    """Apply mouse look rotation to entity."""
    entity.rotate(-entity.cameraYawSens * 0.05 * dt * mouse_delta_x)
    entity.angleY -= 0.05 * dt * entity.cameraPitchSens * mouse_delta_y
    
    # Clamp vertical angle
    entity.angleY = math_helpers.clamp(
        entity.angleY,
        -renderer_config.VIEWPORT_HEIGHT,
        renderer_config.VIEWPORT_HEIGHT,
    )


def apply_keyboard_rotation(
    entity,
    dt,
    rotate_left=False,
    rotate_right=False,
    pitch_up=False,
    pitch_down=False,
):
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


def move_to_target(entity, target, dt):
    """Return the movement vector that would move the entity toward the given target."""
    if hasattr(target, "get_pos"):
        target_pos = target.get_pos()
    else:
        target_pos = target

    dx, dy = math_helpers.slope(entity.get_pos(), target_pos)
    targetDistance = math.hypot(dx, dy)

    if targetDistance > 0.5:
        # Normalize direction and scale by move speed
        move_distance = entity.moveSpeed * dt
        norm_dx = dx / targetDistance * move_distance
        norm_dy = dy / targetDistance * move_distance
        return norm_dx, norm_dy

    return 0, 0


def look_at(entity, target, dt, turn_speed=None):
    """Rotate the entity toward the target, optionally clamping turn speed."""
    if hasattr(target, "get_pos"):
        target_pos = target.get_pos()
    else:
        target_pos = target

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
