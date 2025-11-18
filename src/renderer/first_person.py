"""First-person view rendering."""
from core import colors
import pygame
from renderer import raycast
from renderer import utils
from renderer.floor import render_floor

SCREEN_WIDTH = utils.SCREEN_WIDTH
VIEWPORT_X_OFFSET = utils.VIEWPORT_X_OFFSET
VIEWPORT_HEIGHT = utils.VIEWPORT_HEIGHT


def render_first_person_canvas(entity, *, canvas=None):
    """Render first-person view to a canvas surface."""
    if canvas is None:
        canvas = pygame.Surface(
            [SCREEN_WIDTH - VIEWPORT_X_OFFSET * 2, VIEWPORT_HEIGHT]
        ).convert()
    render_first_person(canvas, entity)
    return canvas


def render_first_person(screen, entity):
    """Render the complete first-person view (walls, floor, ceiling)."""
    raycast.generate_distance_table(entity)
    screen.fill(colors.ALMOST_BLACK)
    render_floor(screen, entity)
    raycast.render_walls(screen, entity)

