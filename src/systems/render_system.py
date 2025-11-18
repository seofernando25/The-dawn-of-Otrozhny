"""
Render system - handles all rendering operations.
"""

import pygame
from core import colors
from core.context import GameContext
from renderer.config import get_screen
from config import renderer_config
from renderer.first_person import render_first_person_canvas
from renderer.text import message_display_L, message_display_MT


class RenderSystem:
    """
    Handles all rendering operations for the game.
    
    This system is responsible for rendering:
    - First-person view (walls, floor, ceiling)
    - Debug information (FPS, player position)
    
    Note: Minimap rendering is handled by HudSystem to maintain proper
    separation of concerns. HUD rendering is also handled by HudSystem.
    """

    def __init__(self, context: GameContext):
        self.context = context
        self._first_person_surface = None

    def render_frame(self, clock: pygame.time.Clock):
        """
        Render a complete frame including first-person view and debug info.
        
        This method renders the main game view. Minimap and HUD are rendered
        separately by HudSystem to maintain proper separation of concerns.
        
        Args:
            clock: Pygame clock for FPS display
        """
        # Screen should always be set in context, but fallback for safety
        screen = self.context.screen
        if screen is None:
            screen = get_screen()
            self.context.screen = screen
        screen.fill(colors.BLACK)
        
        player = self.context.player
        if player is None:
            return
        
        # Render first-person view
        view_port = render_first_person_canvas(
            player, canvas=self._first_person_surface
        )
        self._first_person_surface = view_port
        screen.blit(view_port, (renderer_config.VIEWPORT_X_OFFSET, renderer_config.VIEWPORT_Y_OFFSET))
        
        # Render debug info
        message_display_L(screen, f"FPS: {int(clock.get_fps())}", 15, 10, 15)
        message_display_MT(
            screen,
            f"X:{round(player.px, 2)} Y:{round(player.py, 2)}",
            renderer_config.SCREEN_WIDTH // 2,
            10,
            15,
        )

