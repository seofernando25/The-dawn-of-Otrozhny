"""
Movement utilities - shared movement logic for entities.

Consolidates collision detection, movement, and steering logic used by Player and Enemy classes.
"""

import math
import pygame
from utils import math_helpers
from renderer import config as renderer_settings


def get_input_movement(
    entity,
    dt,
    kb,
    mouse_enabled=False,
    screen_size=None,
):
    """Return the (dx, dy) displacement computed from keyboard and optional mouse look input."""
    newPx = 0
    newPy = 0
    angle = math.atan2(-entity.dirY, entity.dirX)
    if screen_size is None:
        screen_size = renderer_settings.SCREEN_SIZE
    screen_width, screen_height = screen_size

    # Mouse look (if enabled)
    if mouse_enabled:
        mouse_pos = pygame.mouse.get_pos()
        pygame.mouse.set_pos(
            [
                screen_width // 2,
                screen_height // 2,
            ]
        )
        mouseDeltaX = mouse_pos[0] - screen_width // 2
        entity.rotate(-entity.cameraYawSens * 0.05 * dt * mouseDeltaX)

        entity.angleY -= (
            0.05
            * dt
            * entity.cameraPitchSens
            * (mouse_pos[1] - screen_height // 2)
        )

    # Clamp vertical angle
    entity.angleY = math_helpers.clamp(
        entity.angleY,
        -renderer_settings.VIEWPORT_HEIGHT,
        renderer_settings.VIEWPORT_HEIGHT,
    )

    # Keyboard rotation
    if kb[pygame.K_LEFT]:
        entity.rotate(entity.cameraYawSens * dt)

    if kb[pygame.K_RIGHT]:
        entity.rotate(-entity.cameraYawSens * dt)

    if kb[pygame.K_UP]:
        entity.angleY += entity.cameraPitchSens * dt

    if kb[pygame.K_DOWN]:
        entity.angleY -= entity.cameraPitchSens * dt

    # Movement input
    if kb[pygame.K_d]:
        newPx -= math.sin(angle) * 2 * dt
        newPy -= math.cos(angle) * 2 * dt

    if kb[pygame.K_a]:
        newPx += math.sin(angle) * entity.moveSpeed * dt
        newPy += math.cos(angle) * entity.moveSpeed * dt

    if kb[pygame.K_w]:
        newPx += math.cos(angle) * entity.moveSpeed * dt
        newPy -= math.sin(angle) * entity.moveSpeed * dt

    if kb[pygame.K_s]:
        newPx -= math.cos(angle) * entity.moveSpeed * dt
        newPy += math.sin(angle) * entity.moveSpeed * dt

    return newPx, newPy


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
