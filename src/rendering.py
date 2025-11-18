# Making this file was a nightmare to write
# it's a little bit messy but I hope you
# can handle it
# The most used function is at
# line 337 render_first_person
import math

import colors
import pygame
from entities.items import Gate
from entities.player import Player
from renderer import config as renderer_settings
from renderer import minimap
from renderer import raycast

SCREEN_WIDTH = renderer_settings.SCREEN_WIDTH
SCREEN_HEIGHT = renderer_settings.SCREEN_HEIGHT
SCREEN_SIZE = renderer_settings.SCREEN_SIZE

FLAGS = renderer_settings.FLAGS


def get_screen():
    return renderer_settings.get_screen()


VIEWPORT_HEIGHT = renderer_settings.VIEWPORT_HEIGHT
VIEWPORT_X_OFFSET = renderer_settings.VIEWPORT_X_OFFSET
VIEWPORT_Y_OFFSET = renderer_settings.VIEWPORT_Y_OFFSET

DEPTH = renderer_settings.DEPTH

RAY_ANGLE_STEP = renderer_settings.RAY_ANGLE_STEP

MAP_SCALE = 4

_MAP_PREVIEW_CACHE = {}

HUD_NUM_OF_CELLS = renderer_settings.HUD_NUM_OF_CELLS
HUD_CELL_SIZE = renderer_settings.HUD_CELL_SIZE
HUD_CELL_OFFSET = renderer_settings.HUD_CELL_OFFSET
HUD_CELL_TITLE_OFFSET = renderer_settings.HUD_CELL_TITLE_OFFSET
HUD_CELL_TITLE_FONT_SIZE = renderer_settings.HUD_CELL_TITLE_FONT_SIZE
HUD_CELL_OTHER_FONT_SIZE = renderer_settings.HUD_CELL_OTHER_FONT_SIZE


generate_distance_table = raycast.generate_distance_table
_calculate_entities_in_sight = raycast._calculate_entities_in_sight


def render_floor(screen, entity):
    screen_height = screen.get_height()
    screen_width = screen.get_width()
    horizon = screen_height // 2
    floor_start = horizon + entity.angleY
    floor_start = max(0, min(screen_height, floor_start))
    if floor_start >= screen_height:
        return
    screen.fill(colors.DARK_GRAY, [(0, floor_start),
                                   (screen_width, screen_height - floor_start)])


cached_first_person_canvas = None


def render_first_person_canvas(entity):
    global cached_first_person_canvas
    if cached_first_person_canvas is not None:
        render_first_person(cached_first_person_canvas, entity)
        return cached_first_person_canvas
    else:
        cached_first_person_canvas = pygame.Surface(
            [SCREEN_WIDTH - VIEWPORT_X_OFFSET * 2,
             VIEWPORT_HEIGHT]).convert()
        return render_first_person_canvas(entity)


def render_first_person(screen, entity):
    # Render 3d view
    # Clear Screen
    raycast.generate_distance_table(entity)
    screen.fill(colors.ALMOST_BLACK)
    # Draw Floor/ Ceiling
    render_floor(screen, entity)
    # Draw Walls
    raycast.render_walls(screen, entity)
    # Draw Weapon
    # todo  <= I won't. Tts a stealth game!


def draw_map_preview(screen, map_obj, cache_key=None):
    signature = (cache_key or getattr(map_obj, "map_name", None)
                 or getattr(map_obj, "name", None) or id(map_obj),
                 screen.get_size())
    cached_surface = _MAP_PREVIEW_CACHE.get(signature)
    if cached_surface is None:
        preview = pygame.Surface(screen.get_size()).convert()
        preview.fill(colors.GRAY)
        scale_x = preview.get_width()/map_obj.level_width
        scale_y = preview.get_height()/map_obj.level_height
        minimap.draw_grid(
            preview,
            map_obj,
            scale_x,
            scale_y,
            lambda _x, _y, value: colors.GRAY_VARIATION_3 if value != 0 else None)

        color = colors.DARK_GRAY
        for e in map_obj.grid_entities:
            if issubclass(type(e), Gate):
                pygame.draw.rect(preview,
                                 color,
                                 [scale_x * math.floor(e.py),
                                  scale_y * math.floor(e.px),
                                  scale_x + 1,
                                  scale_y + 1])
            if issubclass(type(e), Player):
                pygame.draw.rect(preview,
                                 colors.WHITE,
                                 [scale_x * math.floor(e.py),
                                  scale_y * math.floor(e.px),
                                  scale_x + 1,
                                  scale_y + 1])
        cached_surface = preview
        _MAP_PREVIEW_CACHE[signature] = cached_surface

    screen.blit(cached_surface, (0, 0))
