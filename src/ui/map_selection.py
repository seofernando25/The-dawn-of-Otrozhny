from collections.abc import Sequence

from config import renderer_config
from core import colors
from core.backend import get_backend
from core.game_state import GameState
from renderer.text import blit_surface
from utils import math_helpers
from ui.button import HudButton
from ui.helpers import resolve_screen
from core.backend.api import Event, GraphicsSurface, K_DOWN, K_LEFT, K_RIGHT, K_UP, KEYDOWN, Sound


class MapSelectionScreen:
    """Screen for selecting maps in a grid layout."""

    def __init__(self, *, activated_sound: "Sound | None" = None):
        backend = get_backend()
        self._surface = backend.graphics.create_surface(
            (renderer_config.SCREEN_WIDTH, renderer_config.SCREEN_HEIGHT)
        )
        self.hud_buttons: list[list[HudButton]] = [
            [
                HudButton(100, 100, text=str((x, y)), activated_sound=activated_sound)
                for y in range(3)
            ]
            for x in range(5)
        ]
        self.selected_button_x: int = 0
        self.selected_button_y: int = 0
        self._pointer_x: float = 100
        self._pointer_y: float = 150
        for column in self.hud_buttons:
            for button in column:
                button.redraw()
                button.protected = False

    def draw(self, screen: "GraphicsSurface | None" = None) -> None:
        """Draw the map selection screen."""
        backend = get_backend()
        _ = self._surface.fill(colors.BLACK)
        for x in range(5):
            for y in range(3):
                blit_surface(
                    self._surface,
                    self.hud_buttons[x][y].get_surface(),
                    (
                        50 + x * 100 + x * renderer_config.HUD_CELL_OFFSET,
                        100 + y * 100 + y * renderer_config.HUD_CELL_OFFSET,
                    ),
                )

        backend.graphics.draw_circle(
            self._surface, colors.WHITE, (int(self._pointer_x), int(self._pointer_y)), 10
        )
        target_screen = resolve_screen(screen)
        blit_surface(target_screen, self._surface, (0, 0))

    def update(
        self,
        delta_time: float,
        events: Sequence["Event"],
    ) -> GameState | int | None:
        """Update the map selection screen state."""
        pos = (
            100
            + self.selected_button_x * 100
            + self.selected_button_x * renderer_config.HUD_CELL_OFFSET,
            150
            + self.selected_button_y * 100
            + self.selected_button_y * renderer_config.HUD_CELL_OFFSET,
        )
        self._pointer_x = math_helpers.lerp(self._pointer_x, pos[0], delta_time * 10)
        self._pointer_y = math_helpers.lerp(self._pointer_y, pos[1], delta_time * 10)

        for event in events:
            if event.type == KEYDOWN and event.key is not None:
                key = event.key
                if key == K_LEFT:
                    self.change_selected_button(-1)
                elif key == K_RIGHT:
                    self.change_selected_button(1)
                elif key == K_UP:
                    self.change_selected_button(-1, False)
                elif key == K_DOWN:
                    self.change_selected_button(1, False)
        self.draw()
        return None

    def change_selected_button(self, amount: int, change_x: bool = True) -> None:
        """Change the currently selected button in the grid."""
        self.hud_buttons[self.selected_button_x][self.selected_button_y].set_active(
            False
        )
        if change_x:
            self.selected_button_x += amount
            if self.selected_button_x < 0:
                self.change_selected_button(-1, False)
                self.selected_button_x = 4
            elif self.selected_button_x > 4:
                self.selected_button_x = 0
                self.change_selected_button(1, False)
        else:
            self.selected_button_y += amount
            if self.selected_button_y < 0:
                self.selected_button_y = 2
            elif self.selected_button_y > 2:
                self.selected_button_y = 0
        self.hud_buttons[self.selected_button_x][self.selected_button_y].set_active(
            True
        )
