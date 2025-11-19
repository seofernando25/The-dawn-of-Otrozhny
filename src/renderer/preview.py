"""Map preview rendering for level selection."""

from collections.abc import Hashable
import math

import pygame

from core import colors
from entities.items import Gate
from entities.player import Player
from level.loader import LevelObject
from renderer import minimap

# Cache for map previews
_MAP_PREVIEW_CACHE: dict[tuple[Hashable, tuple[int, int]], pygame.Surface] = {}


def draw_map_preview(
    screen: pygame.Surface,
    map_obj: LevelObject,
    cache_key: Hashable | None = None,
) -> None:
    """Draw a preview of a map on the given screen surface."""
    signature = (
        cache_key or id(map_obj),
        screen.get_size(),
    )
    cached_surface = _MAP_PREVIEW_CACHE.get(signature)
    if cached_surface is None:
        preview = pygame.Surface(screen.get_size()).convert()
        _ = preview.fill(colors.GRAY)
        scale_x = preview.get_width() / map_obj.level_width
        scale_y = preview.get_height() / map_obj.level_height
        minimap.draw_grid(
            preview,
            map_obj,
            scale_x,
            scale_y,
            lambda _x, _y, value: colors.GRAY_VARIATION_3 if value != 0 else None,
        )

        color = colors.DARK_GRAY
        for e in map_obj.grid_entities:
            if isinstance(e, Gate):
                _ = pygame.draw.rect(
                    preview,
                    color,
                    [
                        scale_x * math.floor(e.py),
                        scale_y * math.floor(e.px),
                        scale_x + 1,
                        scale_y + 1,
                    ],
                )
            if isinstance(e, Player):
                _ = pygame.draw.rect(
                    preview,
                    colors.WHITE,
                    [
                        scale_x * math.floor(e.py),
                        scale_y * math.floor(e.px),
                        scale_x + 1,
                        scale_y + 1,
                    ],
                )
        cached_surface = preview
        _MAP_PREVIEW_CACHE[signature] = cached_surface

    _ = screen.blit(cached_surface, (0, 0))
