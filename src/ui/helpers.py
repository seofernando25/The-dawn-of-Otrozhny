from __future__ import annotations

from core import colors
from core.context import get_screen
from config import renderer_config
from renderer.text import blit_surface
from ui.button import HudButton
from core.backend.api import GraphicsSurface, Sound


def _resolve_screen(screen: "GraphicsSurface | None" = None) -> "GraphicsSurface":
    """Resolve screen surface, using global screen if none provided."""
    return screen if screen is not None else get_screen()


def resolve_screen(screen: "GraphicsSurface | None" = None) -> "GraphicsSurface":
    """Public wrapper around `_resolve_screen` for external modules."""
    return _resolve_screen(screen)


def render_hud_surfaces(
    hud_viewport: "GraphicsSurface", hud_cell_surfaces: list[HudButton]
) -> None:
    """Render HUD cell surfaces onto the HUD viewport."""
    row = 0
    for cell_surface in hud_cell_surfaces:
        cell_surface.redraw()
        cell_width = cell_surface.get_width()
        blit_surface(
            hud_viewport,
            cell_surface.get_surface(),
            (
                renderer_config.HUD_CELL_OFFSET
                + renderer_config.HUD_CELL_OFFSET * row
                + row * cell_width,
                renderer_config.VIEWPORT_Y_OFFSET // 4,
            ),
        )
        row += 1


def generate_hud_surfaces(
    hud_surface: "GraphicsSurface", *, activated_sound: "Sound | None" = None
) -> list[HudButton]:
    """Generate HUD button surfaces for a HUD viewport."""
    hud_cell_surfaces: list[HudButton] = []
    hud_width, hud_height = hud_surface.get_size()
    cell_height = hud_height - renderer_config.VIEWPORT_Y_OFFSET // 2
    cell_width = (
        hud_width
        - (renderer_config.HUD_CELL_OFFSET + 1) * renderer_config.HUD_NUM_OF_CELLS
    )
    cell_width /= renderer_config.HUD_NUM_OF_CELLS
    surf_count = 0
    while surf_count < renderer_config.HUD_NUM_OF_CELLS:
        surf_count += 1
        window = HudButton(cell_width, cell_height, activated_sound=activated_sound)
        _ = window.fill(colors.NAVY_BLUE)
        hud_cell_surfaces.append(window)
    return hud_cell_surfaces


def generate_hud_viewport() -> "GraphicsSurface":
    """Generate the main HUD viewport surface."""
    from core.backend import get_backend
    
    _ = get_screen()
    hud_width = renderer_config.SCREEN_WIDTH - renderer_config.VIEWPORT_X_OFFSET * 2
    hud_height = (
        renderer_config.SCREEN_HEIGHT
        - renderer_config.VIEWPORT_HEIGHT
        - renderer_config.VIEWPORT_Y_OFFSET * 2
    )

    backend = get_backend()
    hud_viewport = backend.graphics.create_surface((hud_width, hud_height))
    hud_viewport = hud_viewport.convert()
    _ = hud_viewport.fill(colors.BLUE)
    return hud_viewport
