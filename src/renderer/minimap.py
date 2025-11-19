import math
from typing import Callable

from core import colors
from core.backend import get_backend
from entities.enemy import Enemy
from entities.items import Collectible, Gate
from renderer.text import blit_surface
from .raycast import calculate_fov_polygon

from core.backend.api import GraphicsSurface
from entities.base import Agent
from level.level import Level
from level.loader import LevelObject

# Cache for static minimap surfaces
_STATIC_SURFACES: dict[tuple[int, tuple[int, int]], "GraphicsSurface"] = {}


def _calculate_fov_points(
    scale_x: float, scale_y: float, current_map: "Level"
) -> list[
    tuple[tuple[int, int, int] | tuple[int, int, int, int], list[tuple[float, float]]]
]:
    all_fovs: list[
        tuple[
            tuple[int, int, int] | tuple[int, int, int, int], list[tuple[float, float]]
        ]
    ] = []
    for enemy in current_map.grid_entities:
        if isinstance(enemy, Enemy):  # Enemy is a subclass of Agent
            enemy_fov = calculate_fov_polygon(enemy)
            # Translate (x, y) coordinates into scaled map space
            enemy_fov = [(y * scale_x, x * scale_y) for x, y in enemy_fov]

            color: tuple[int, int, int] | tuple[int, int, int, int] = (
                colors.ALMOST_BLACK
            )
            if enemy.canSeePlayer:
                color = colors.RED
            all_fovs.append((color, enemy_fov))
    return all_fovs


def draw_grid(
    surface: "GraphicsSurface",
    level_map: "Level | LevelObject",
    scale_x: float,
    scale_y: float,
    color_fn: Callable[
        [int, int, int], tuple[int, int, int] | tuple[int, int, int, int] | None
    ],
) -> None:
    backend = get_backend()
    for x in range(level_map.level_width):
        for y in range(level_map.level_height):
            color = color_fn(x, y, level_map.grid[x][y])
            if color is None:
                continue
            # Convert RGBA to RGB if needed (ColorValue only supports RGB)
            rgb_color: tuple[int, int, int]
            if len(color) == 4:
                rgb_color = (color[0], color[1], color[2])  # Strip alpha
            else:
                rgb_color = color
            backend.graphics.draw_rect(
                surface, rgb_color, (scale_x * y, scale_y * x, scale_x + 1, scale_y + 1)
            )


def _build_static_surface(
    screen: "GraphicsSurface",
    level_map: "Level | LevelObject",
    scale_x: float,
    scale_y: float,
) -> "GraphicsSurface":
    backend = get_backend()
    surface = backend.graphics.create_surface(screen.get_size())
    surface = surface.convert()
    draw_grid(
        surface,
        level_map,
        scale_x,
        scale_y,
        lambda _x, _y, value: (
            colors.GRAY_VARIATION_3 if value != 0 else colors.DARK_GRAY
        ),
    )
    return surface


def _get_static_surface(
    screen: "GraphicsSurface",
    level_map: "Level | LevelObject",
    scale_x: float,
    scale_y: float,
) -> "GraphicsSurface":
    signature = (id(level_map), screen.get_size())
    surface = _STATIC_SURFACES.get(signature)
    if surface is None:
        surface = _build_static_surface(screen, level_map, scale_x, scale_y)
        _STATIC_SURFACES[signature] = surface
    return surface


def render_map(screen: "GraphicsSurface", entity: "Agent") -> None:
    backend = get_backend()
    if not hasattr(entity, "context") or entity.context is None:
        raise RuntimeError("Entity requires a GameContext for minimap rendering.")
    current_map: Level | None = entity.context.level
    if current_map is None:
        raise RuntimeError("GameContext.level is not set.")
    width, height = screen.get_size()
    scale_x = width / current_map.level_width
    scale_y = height / current_map.level_height

    static_surface = _get_static_surface(screen, current_map, scale_x, scale_y)
    blit_surface(screen, static_surface, (0, 0))

    fov_points = calculate_fov_polygon(entity)
    # Translate (x, y) coordinates into scaled map space
    fov_points = [(y * scale_x, x * scale_y) for x, y in fov_points]

    all_fovs = _calculate_fov_points(scale_x, scale_y, current_map)

    if len(fov_points) > 2:
        backend.graphics.draw_polygon(screen, colors.WHITE, fov_points)

    for mapped_entity in current_map.grid_entities:
        px = int(mapped_entity.px * scale_y)
        py = int(mapped_entity.py * scale_x)
        if isinstance(mapped_entity, Enemy):
            backend.graphics.draw_circle(screen, colors.RED, (py, px), 2)
        if isinstance(mapped_entity, Collectible) and mapped_entity.collected:
            backend.graphics.draw_circle(screen, colors.YELLOW_WHITE, (py, px), 2)

    backend.graphics.draw_circle(
        screen, colors.WHITE, (int(entity.py * scale_x), int(entity.px * scale_y)), 2
    )

    for c, points in all_fovs:
        # Convert RGBA to RGB if needed (ColorValue only supports RGB)
        rgb_color: tuple[int, int, int]
        if len(c) == 4:
            rgb_color = (c[0], c[1], c[2])  # Strip alpha
        else:
            rgb_color = c
        backend.graphics.draw_polygon(screen, rgb_color, points)

    color = colors.DARK_GRAY
    for grid_entity in current_map.grid_entities:
        if isinstance(grid_entity, Gate) and not grid_entity.open:
            backend.graphics.draw_rect(
                screen,
                color,
                (
                    scale_x * math.floor(grid_entity.py),
                    scale_y * math.floor(grid_entity.px),
                    scale_x + 1,
                    scale_y + 1,
                ),
            )
