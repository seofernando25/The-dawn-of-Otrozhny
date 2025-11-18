"""Helper functions for UI components."""
from typing import Optional
import pygame
import rendering as renderer
import colors
from ui.button import HudButton


def _resolve_screen(screen: Optional[pygame.Surface] = None) -> pygame.Surface:
    """Resolve screen surface, using global screen if none provided."""
    return screen if screen is not None else renderer.get_screen()


def render_hud_surfaces(hud_viewport, hud_cell_surfaces):
    """Render HUD cell surfaces onto the HUD viewport."""
    row = 0
    for cell_surface in hud_cell_surfaces:
        cell_surface.redraw()
        hud_viewport.blit(
            cell_surface,
            (
                renderer.HUD_CELL_OFFSET
                + renderer.HUD_CELL_OFFSET * row
                + row * cell_surface.get_width(),
                renderer.VIEWPORT_Y_OFFSET // 4,
            ),
        )
        row += 1


def _generate_hud_surfaces(hud_surface):
    """Generate HUD button surfaces for a HUD viewport."""
    hud_cell_surfaces = []
    cell_height = hud_surface.get_height() - renderer.VIEWPORT_Y_OFFSET // 2
    cell_width = (
        hud_surface.get_width()
        - (renderer.HUD_CELL_OFFSET + 1) * renderer.HUD_NUM_OF_CELLS
    )
    cell_width /= renderer.HUD_NUM_OF_CELLS
    surf_count = 0
    while surf_count < renderer.HUD_NUM_OF_CELLS:
        surf_count += 1
        window = HudButton(cell_width, cell_height)
        window.fill(colors.NAVY_BLUE)
        hud_cell_surfaces.append(window)
    return hud_cell_surfaces


def _generate_hud_viewport():
    """Generate the main HUD viewport surface."""
    renderer.get_screen()
    hud_width = renderer.SCREEN_WIDTH - renderer.VIEWPORT_X_OFFSET * 2
    hud_height = (
        renderer.SCREEN_HEIGHT
        - renderer.VIEWPORT_HEIGHT
        - renderer.VIEWPORT_Y_OFFSET * 2
    )

    hud_viewport = pygame.Surface([hud_width, hud_height]).convert()
    hud_viewport.fill(colors.BLUE)
    return hud_viewport

