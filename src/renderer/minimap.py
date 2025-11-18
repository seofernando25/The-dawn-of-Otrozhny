import math

import pygame

from core import colors
from entities.enemy import Enemy
from entities.items import Collectible, Gate
from .raycast import calculate_fov_polygon
from .utils import translate_to_map, get_static_surfaces_cache

_STATIC_SURFACES = get_static_surfaces_cache()


def _calculate_fov_points(scale_x, scale_y, current_map):
    all_fovs = []
    for enemy in current_map.grid_entities:
        if issubclass(type(enemy), Enemy):
            enemy_fov = calculate_fov_polygon(enemy)
            enemy_fov = translate_to_map(enemy_fov, scale_x, scale_y)

            color = colors.ALMOST_BLACK
            if enemy.canSeePlayer:
                color = colors.RED
            all_fovs.append((color, enemy_fov))
    return all_fovs


def draw_grid(surface, level_map, scale_x, scale_y, color_fn):
    for x in range(level_map.level_width):
        for y in range(level_map.level_height):
            color = color_fn(x, y, level_map.grid[x][y])
            if color is None:
                continue
            pygame.draw.rect(
                surface, color, [scale_x * y, scale_y * x, scale_x + 1, scale_y + 1]
            )


def _build_static_surface(screen, level_map, scale_x, scale_y):
    surface = pygame.Surface(screen.get_size()).convert()
    draw_grid(
        surface,
        level_map,
        scale_x,
        scale_y,
        lambda _x, _y, value: colors.GRAY_VARIATION_3
        if value != 0
        else colors.DARK_GRAY,
    )
    return surface


def _get_static_surface(screen, level_map, scale_x, scale_y):
    signature = (id(level_map), screen.get_size())
    surface = _STATIC_SURFACES.get(signature)
    if surface is None:
        surface = _build_static_surface(screen, level_map, scale_x, scale_y)
        _STATIC_SURFACES[signature] = surface
    return surface


def render_map(screen, entity):
    if not hasattr(entity, "context") or entity.context is None:
        raise RuntimeError("Entity requires a GameContext for minimap rendering.")
    current_map = entity.context.level
    if current_map is None:
        raise RuntimeError("GameContext.level is not set.")
    scale_x = screen.get_width() / current_map.level_width
    scale_y = screen.get_height() / current_map.level_height

    static_surface = _get_static_surface(screen, current_map, scale_x, scale_y)
    screen.blit(static_surface, (0, 0))

    fov_points = calculate_fov_polygon(entity)
    fov_points = translate_to_map(fov_points, scale_x, scale_y)

    all_fovs = _calculate_fov_points(scale_x, scale_y, current_map)

    if len(fov_points) > 2:
        pygame.draw.polygon(screen, colors.WHITE, fov_points)

    for enemy in current_map.grid_entities:
        px = int(enemy.px * scale_y)
        py = int(enemy.py * scale_x)
        if issubclass(type(enemy), Enemy):
            pygame.draw.circle(screen, colors.RED, [py, px], 2)
        if issubclass(type(enemy), Collectible) and enemy.collected:
            pygame.draw.circle(screen, colors.YELLOW_WHITE, [py, px], 2)

    pygame.draw.circle(
        screen, colors.WHITE, [int(entity.py * scale_x), int(entity.px * scale_y)], 2
    )

    [pygame.draw.polygon(screen, c, points) for c, points in all_fovs]

    color = colors.DARK_GRAY
    for e in current_map.grid_entities:
        if issubclass(type(e), Gate) and not e.open:
            pygame.draw.rect(
                screen,
                color,
                [
                    scale_x * math.floor(e.py),
                    scale_y * math.floor(e.px),
                    scale_x + 1,
                    scale_y + 1,
                ],
            )
