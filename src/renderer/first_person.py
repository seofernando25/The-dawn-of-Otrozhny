"""First-person view rendering."""

from core import colors
import pygame
from renderer import raycast
from config import renderer_config
from renderer.floor import render_floor
from entities.base import Agent

SCREEN_WIDTH = renderer_config.SCREEN_WIDTH
VIEWPORT_X_OFFSET = renderer_config.VIEWPORT_X_OFFSET
VIEWPORT_HEIGHT = renderer_config.VIEWPORT_HEIGHT


def render_first_person_canvas(
    entity: Agent, *, canvas: pygame.Surface | None = None
) -> pygame.Surface:
    """Render first-person view to a canvas surface."""
    if canvas is None:
        canvas = pygame.Surface(
            [SCREEN_WIDTH - VIEWPORT_X_OFFSET * 2, VIEWPORT_HEIGHT]
        ).convert()
    render_first_person(canvas, entity)
    return canvas


def render_first_person(screen: pygame.Surface, entity: Agent) -> None:
    """Render the complete first-person view (walls, floor, ceiling)."""
    raycast.generate_distance_table(entity)
    _ = screen.fill(colors.ALMOST_BLACK)
    render_floor(screen, entity)
    raycast.render_walls(screen, entity)
