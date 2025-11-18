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
from renderer import utils

SCREEN_WIDTH = utils.SCREEN_WIDTH
SCREEN_HEIGHT = utils.SCREEN_HEIGHT
SCREEN_SIZE = utils.SCREEN_SIZE

FLAGS = renderer_settings.FLAGS


def get_screen():
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
    screen.fill(
        colors.DARK_GRAY,
        [(0, floor_start), (screen_width, screen_height - floor_start)],
    )


def render_first_person_canvas(entity, *, canvas=None):
    if canvas is None:
        canvas = pygame.Surface(
            [SCREEN_WIDTH - VIEWPORT_X_OFFSET * 2, VIEWPORT_HEIGHT]
        ).convert()
    render_first_person(canvas, entity)
    return canvas


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
    signature = (
        cache_key or id(map_obj),
        screen.get_size(),
    )
    cache = utils.get_map_preview_cache()
    cached_surface = cache.get(signature)
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
        cache[signature] = cached_surface

    screen.blit(cached_surface, (0, 0))
