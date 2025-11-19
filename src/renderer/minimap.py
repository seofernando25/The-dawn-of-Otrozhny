import math
from typing import TYPE_CHECKING, Union
import pygame

from core import colors
from entities.enemy import Enemy
from entities.items import Collectible, Gate
from .raycast import calculate_fov_polygon

if TYPE_CHECKING:
    from entities.base import Agent
    from level.level import Level

# Cache for static minimap surfaces
_STATIC_SURFACES = {}


def _calculate_fov_points(scale_x, scale_y, current_map):
    all_fovs = []
    for enemy in current_map.grid_entities:
        if issubclass(type(enemy), Enemy):
            enemy_fov = calculate_fov_polygon(enemy)
            # Translate (x, y) coordinates into scaled map space
            enemy_fov = [(y * scale_x, x * scale_y) for x, y in enemy_fov]

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


def render_map(screen: pygame.Surface, entity: "Agent") -> None:
    if not hasattr(entity, "context") or entity.context is None:
        raise RuntimeError("Entity requires a GameContext for minimap rendering.")
    current_map: Union["Level", None] = entity.context.level
    if current_map is None:
        raise RuntimeError("GameContext.level is not set.")
    scale_x = screen.get_width() / current_map.level_width
    scale_y = screen.get_height() / current_map.level_height

    static_surface = _get_static_surface(screen, current_map, scale_x, scale_y)
    _ = screen.blit(static_surface, (0, 0))

    fov_points = calculate_fov_polygon(entity)
    # Translate (x, y) coordinates into scaled map space
    fov_points = [(y * scale_x, x * scale_y) for x, y in fov_points]

    all_fovs = _calculate_fov_points(scale_x, scale_y, current_map)

    if len(fov_points) > 2:
        pygame.draw.polygon(screen, colors.WHITE, fov_points)

    for mapped_entity in current_map.grid_entities:
        px = int(mapped_entity.px * scale_y)
        py = int(mapped_entity.py * scale_x)
        if isinstance(mapped_entity, Enemy):
            pygame.draw.circle(screen, colors.RED, [py, px], 2)
        if isinstance(mapped_entity, Collectible) and mapped_entity.collected:
            pygame.draw.circle(screen, colors.YELLOW_WHITE, [py, px], 2)

    pygame.draw.circle(
        screen, colors.WHITE, [int(entity.py * scale_x), int(entity.px * scale_y)], 2
    )

    [pygame.draw.polygon(screen, c, points) for c, points in all_fovs]

    color = colors.DARK_GRAY
    for grid_entity in current_map.grid_entities:
        if isinstance(grid_entity, Gate) and not grid_entity.open:
            pygame.draw.rect(
                screen,
                color,
                [
                    scale_x * math.floor(grid_entity.py),
                    scale_y * math.floor(grid_entity.px),
                    scale_x + 1,
                    scale_y + 1,
                ],
            )
