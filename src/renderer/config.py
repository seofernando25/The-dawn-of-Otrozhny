"""
Renderer screen management.

This module provides screen initialization and management functions.
All renderer configuration constants are in config.renderer_config.

Note: Prefer using context.screen when available. This module provides
fallback functions for code that doesn't have access to context (e.g., menu rendering).
"""

import pygame
from config import renderer_config


def get_screen():
    """
    Get or create the main pygame screen surface.
    
    Note: This is a fallback for code without context access.
    Prefer using context.screen when available.
    """
    screen = pygame.display.get_surface()
    if screen is None:
        screen = pygame.display.set_mode(renderer_config.SCREEN_SIZE, renderer_config.FLAGS)
        screen.set_alpha(None)
    return screen


def reset_screen():
    """
    Dispose of the screen so tests/demos can recreate it.
    
    Note: This is mainly for testing. In normal operation, the screen
    is managed by pygame.display and doesn't need explicit disposal.
    """
    # Screen is managed by pygame.display, no explicit cleanup needed
    pass
