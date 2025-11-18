"""Map preview rendering for level selection."""
import math
from core import colors
import pygame
from entities.items import Gate
from entities.player import Player
from renderer import minimap

# Cache for map previews
_MAP_PREVIEW_CACHE = {}


def draw_map_preview(screen, map_obj, cache_key=None):
    """Draw a preview of a map on the given screen surface."""
    signature = (
        cache_key or id(map_obj),
        screen.get_size(),
    )
    cached_surface = _MAP_PREVIEW_CACHE.get(signature)
    if cached_surface is None:
        preview = pygame.Surface(screen.get_size()).convert()
        preview.fill(colors.GRAY)
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
            if issubclass(type(e), Gate):
                pygame.draw.rect(
                    preview,
                    color,
                    [
                        scale_x * math.floor(e.py),
                        scale_y * math.floor(e.px),
                        scale_x + 1,
                        scale_y + 1,
                    ],
                )
            if issubclass(type(e), Player):
                pygame.draw.rect(
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

    screen.blit(cached_surface, (0, 0))

