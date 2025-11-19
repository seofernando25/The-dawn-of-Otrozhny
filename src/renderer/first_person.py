"""First-person view rendering."""

from typing import TYPE_CHECKING

from core import colors
from core.backend import get_backend
from config import renderer_config
from renderer import raycast
from renderer.floor import render_floor
from entities.base import Agent

if TYPE_CHECKING:
    from core.backend.api import GraphicsSurface

SCREEN_WIDTH = renderer_config.SCREEN_WIDTH
VIEWPORT_X_OFFSET = renderer_config.VIEWPORT_X_OFFSET
VIEWPORT_HEIGHT = renderer_config.VIEWPORT_HEIGHT


def render_first_person_canvas(
    entity: Agent, *, canvas: "GraphicsSurface | None" = None
) -> "GraphicsSurface":
    """Render first-person view to a canvas surface."""
    backend = get_backend()
    if canvas is None:
        canvas = backend.graphics.create_surface(
            (SCREEN_WIDTH - VIEWPORT_X_OFFSET * 2, VIEWPORT_HEIGHT)
        )
        canvas = canvas.convert()
    render_first_person(canvas, entity)
    return canvas


def render_first_person(screen: "GraphicsSurface", entity: Agent) -> None:
    """Render the complete first-person view (walls, floor, ceiling)."""
    raycast.generate_distance_table(entity)
    screen.fill(colors.ALMOST_BLACK)
    render_floor(screen, entity)
    raycast.render_walls(screen, entity)
