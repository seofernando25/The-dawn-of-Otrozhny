"""
Movement utilities - shared movement logic for entities.

Consolidates collision detection, movement, and steering logic used by Player and Enemy classes.
"""

import math
import pygame
import mathHelpers
from renderer import config as renderer_settings


def get_input_movement(entity, dt, kb, mouse_enabled=False):
    """Return the (dx, dy) displacement computed from keyboard and optional mouse look input."""
    newPx = 0
    newPy = 0
    angle = math.atan2(-entity.dirY, entity.dirX)

    # Mouse look (if enabled)
    if mouse_enabled:
        mouse_pos = pygame.mouse.get_pos()
        pygame.mouse.set_pos(
            [
                renderer_settings.SCREEN_WIDTH // 2,
                renderer_settings.SCREEN_HEIGHT // 2,
            ]
        )
        mouseDeltaX = mouse_pos[0] - renderer_settings.SCREEN_WIDTH // 2
        entity.rotate(-entity.cameraYawSens * 0.05 * dt * mouseDeltaX)

        entity.angleY -= (
            0.05
            * dt
            * entity.cameraPitchSens
            * (mouse_pos[1] - renderer_settings.SCREEN_HEIGHT // 2)
        )

    # Clamp vertical angle
    entity.angleY = mathHelpers.clamp(
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

    dx, dy = mathHelpers.slope(entity.get_pos(), target_pos)
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

    dx, dy = mathHelpers.slope(entity.get_pos(), target_pos)
    target_angle = math.atan2(dy, dx)

    # Calculate shortest rotation direction
    angle_diff = target_angle - entity.angle
    angle_diff = (angle_diff + math.pi) % (2 * math.pi) - math.pi

    # Apply rotation
    speed = turn_speed if turn_speed is not None else entity.cameraYawSens * dt * 2
    if abs(angle_diff) < speed:
        entity.angle = target_angle
    else:
        entity.rotate(math.copysign(speed, angle_diff))
