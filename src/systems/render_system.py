from typing import TYPE_CHECKING, cast

from config import renderer_config
from core import colors
from core.backend import get_backend
from core.context import GameContext, get_screen
from entities.player import Player
from renderer import minimap as renderer_minimap
from renderer.first_person import render_first_person_canvas
from renderer.text import message_display_L, message_display_MT

if TYPE_CHECKING:
    from core.backend.api import Clock, GraphicsSurface


class RenderSystem:
    """Handles all rendering operations for the game."""

    def __init__(self, context: GameContext):
        self.context: GameContext = context
        self._first_person_surface: "GraphicsSurface | None" = None

    def render_frame(self, clock: "Clock") -> None:
        """Render a complete frame including first-person view and debug info."""
        # Screen should always be set in context, but fallback for safety
        screen = self.context.screen
        if screen is None:
            screen = get_screen()
            self.context.screen = screen
        _ = screen.fill(colors.BLACK)

        player_obj = cast(Player | None, self.context.player)
        if player_obj is None:
            return
        player = player_obj

        # Render first-person view
        view_port = render_first_person_canvas(
            player, canvas=self._first_person_surface
        )
        self._first_person_surface = view_port
        _ = screen.blit(
            view_port,
            (renderer_config.VIEWPORT_X_OFFSET, renderer_config.VIEWPORT_Y_OFFSET),
        )

        # Render debug info
        message_display_L(screen, f"FPS: {int(clock.get_fps())}", 15, 10, 15)
        message_display_MT(
            screen,
            f"X:{round(float(player.px), 2)} Y:{round(float(player.py), 2)}",
            renderer_config.SCREEN_WIDTH // 2,
            10,
            15,
        )

    def render_minimap(self, minimap_surface: "GraphicsSurface") -> None:
        """Render the minimap to the provided surface."""
        player_obj = cast(Player | None, self.context.player)
        if player_obj is None:
            return
        player = player_obj
        renderer_minimap.render_map(minimap_surface, player)
