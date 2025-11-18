"""
Renderer utilities - shared cache system and math helpers for rendering modules.
"""

import numpy as np
from renderer import config as renderer_settings

# Shared caches for renderer modules
_MAP_PREVIEW_CACHE = {}
_STATIC_SURFACES = {}

# Constants (consolidated from multiple files)
SCREEN_WIDTH = renderer_settings.SCREEN_WIDTH
SCREEN_HEIGHT = renderer_settings.SCREEN_HEIGHT
SCREEN_SIZE = renderer_settings.SCREEN_SIZE
VIEWPORT_HEIGHT = renderer_settings.VIEWPORT_HEIGHT
VIEWPORT_X_OFFSET = renderer_settings.VIEWPORT_X_OFFSET
VIEWPORT_Y_OFFSET = renderer_settings.VIEWPORT_Y_OFFSET

HUD_NUM_OF_CELLS = renderer_settings.HUD_NUM_OF_CELLS
HUD_CELL_SIZE = renderer_settings.HUD_CELL_SIZE
HUD_CELL_OFFSET = renderer_settings.HUD_CELL_OFFSET
HUD_CELL_TITLE_OFFSET = renderer_settings.HUD_CELL_TITLE_OFFSET
HUD_CELL_TITLE_FONT_SIZE = renderer_settings.HUD_CELL_TITLE_FONT_SIZE
HUD_CELL_OTHER_FONT_SIZE = renderer_settings.HUD_CELL_OTHER_FONT_SIZE

RAY_ANGLE_STEP = renderer_settings.RAY_ANGLE_STEP
DEPTH = renderer_settings.DEPTH

MAP_SCALE = 4


def get_map_preview_cache():
    """Get the shared map preview cache."""
    return _MAP_PREVIEW_CACHE


def get_static_surfaces_cache():
    """Get the shared static surfaces cache."""
    return _STATIC_SURFACES


def get_numpy_grid(current_map):
    """Return the cached numpy grid for a level, creating it on first access."""
    grid_np = getattr(current_map, "grid_np", None)
    if grid_np is None or not isinstance(grid_np, np.ndarray):
        grid_np = np.array(current_map.grid, dtype=np.int16)
        current_map.grid_np = grid_np
    return grid_np


def translate_to_map(coord_list, scale_x, scale_y):
    """Translate (x, y) coordinates into scaled map space."""
    new_coord_list = []
    for x, y in coord_list:
        new_coord_list.append((y * scale_x, x * scale_y))
    return new_coord_list
