"""Floor rendering for first-person view."""

from core import colors
from core.backend import get_backend
from core.backend.api import GraphicsSurface
from entities.base import Agent


def render_floor(screen: "GraphicsSurface", entity: "Agent") -> None:
    """Render the floor/ceiling in the first-person view."""
    backend = get_backend()
    screen_height = screen.get_height()
    screen_width = screen.get_width()
    horizon = screen_height // 2
    floor_start = horizon + entity.angleY
    floor_start = max(0, min(screen_height, floor_start))
    if floor_start >= screen_height:
        return
    backend.graphics.draw_rect(
        screen,
        colors.DARK_GRAY,
        (0, floor_start, screen_width, screen_height - floor_start),
    )
