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
    """Render first-person view to a canvas surface.
    
    Args:
        entity: The entity (player) to render from
        canvas: Optional canvas surface to render to. If None, creates a new one.
    
    Returns:
        The canvas surface with the rendered first-person view.
    """
    if canvas is None:
        canvas = pygame.Surface(
            [SCREEN_WIDTH - VIEWPORT_X_OFFSET * 2, VIEWPORT_HEIGHT]
        ).convert()
    render_first_person(canvas, entity)
    return canvas


def render_first_person(screen, entity):
    """Render the complete first-person view (walls, floor, ceiling).
    
    Args:
        screen: The surface to render to
        entity: The entity (player) to render from
    """
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

