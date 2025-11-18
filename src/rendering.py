"""Rendering module - provides unified access to rendering functionality.

This module re-exports constants and functions from the renderer package
for backward compatibility.
"""
from renderer import config as renderer_settings
from renderer import raycast
from renderer import utils
from renderer.first_person import render_first_person, render_first_person_canvas
from renderer.preview import draw_map_preview

# Re-export constants for backward compatibility
SCREEN_WIDTH = utils.SCREEN_WIDTH
SCREEN_HEIGHT = utils.SCREEN_HEIGHT
SCREEN_SIZE = utils.SCREEN_SIZE

FLAGS = renderer_settings.FLAGS


def get_screen():
    """Get the main screen surface."""
    return renderer_settings.get_screen()


VIEWPORT_HEIGHT = utils.VIEWPORT_HEIGHT
VIEWPORT_X_OFFSET = utils.VIEWPORT_X_OFFSET
VIEWPORT_Y_OFFSET = utils.VIEWPORT_Y_OFFSET

DEPTH = utils.DEPTH

RAY_ANGLE_STEP = utils.RAY_ANGLE_STEP

MAP_SCALE = utils.MAP_SCALE

HUD_NUM_OF_CELLS = utils.HUD_NUM_OF_CELLS
HUD_CELL_SIZE = utils.HUD_CELL_SIZE
HUD_CELL_OFFSET = utils.HUD_CELL_OFFSET
HUD_CELL_TITLE_OFFSET = utils.HUD_CELL_TITLE_OFFSET
HUD_CELL_TITLE_FONT_SIZE = utils.HUD_CELL_TITLE_FONT_SIZE
HUD_CELL_OTHER_FONT_SIZE = utils.HUD_CELL_OTHER_FONT_SIZE

# Re-export functions for backward compatibility
generate_distance_table = raycast.generate_distance_table
_calculate_entities_in_sight = raycast._calculate_entities_in_sight
