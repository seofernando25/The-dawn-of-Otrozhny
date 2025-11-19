"""HUD screen component."""

from collections.abc import Callable, Sequence

from config import renderer_config
from core import colors
from core.backend import get_backend
from renderer.text import blit_surface
from utils import math_helpers
from ui.button import HudButton
from ui.helpers import (
    generate_hud_viewport,
    generate_hud_surfaces,
    render_hud_surfaces,
    resolve_screen,
)

from core.backend.api import (
    Event,
    GraphicsSurface,
    K_1,
    K_2,
    K_3,
    K_4,
    K_5,
    K_LEFT,
    K_RETURN,
    K_RIGHT,
    K_SPACE,
    KEYDOWN,
    Sound,
)


class HudScreen:
    """Main HUD screen that manages multiple HUD buttons."""

    def __init__(
        self,
        *,
        interactable: bool = True,
        dynamic: bool = False,
        activated_sound: Sound | None = None,
    ):
        self.viewPort = generate_hud_viewport()
        _ = self.viewPort.fill(colors.GRAY_VARIATION_2)
        self.hud_buttons: list[HudButton] = generate_hud_surfaces(
            self.viewPort, activated_sound=activated_sound
        )
        self.interactable: bool = interactable
        self.dynamic: bool = dynamic
        self.selected_button: int = 0
        self.cursorX: float = float(self.selected_button)
        # Should have created an event handler class :/
        self.onChangedButton: list[Callable[[], None]] = []

    def set_button_color(
        self, buttonIndex: int, textIndex: int, color: colors.ColorValue
    ) -> None:
        """Set the color of a specific text element in a button."""
        self.hud_buttons[buttonIndex].set_color(textIndex, color)

    def set_button_subtitle(self, buttonIndex: int, text: str) -> None:
        """Set the subtitle of a button."""
        self.hud_buttons[buttonIndex].set_subtitle(text)

    def set_button_title(self, buttonIndex: int, text: str) -> None:
        """Set the title of a button."""
        self.hud_buttons[buttonIndex].set_title(text)

    def set_button_text(self, buttonIndex: int, text: str) -> None:
        """Set the main text of a button."""
        self.hud_buttons[buttonIndex].set_text(text)

    def draw(self, screen: GraphicsSurface | None = None) -> None:
        """Draw the HUD screen."""
        backend = get_backend()
        if self.interactable or self.dynamic:
            _ = self.viewPort.fill(colors.GRAY_VARIATION_2)
        render_hud_surfaces(self.viewPort, self.hud_buttons)

        if self.interactable:
            width, height = self.viewPort.get_size()
            backend.graphics.draw_rect(
                self.viewPort,
                colors.BLACK,
                (
                    int(
                        self.cursorX * (width / 5) + renderer_config.HUD_CELL_OFFSET + 5
                    ),
                    height,
                    100,
                    -10,
                ),
            )
        target_screen = resolve_screen(screen)
        blit_surface(
            target_screen,
            self.viewPort,
            (
                renderer_config.VIEWPORT_X_OFFSET,
                renderer_config.SCREEN_HEIGHT
                - self.viewPort.get_height()
                - renderer_config.VIEWPORT_Y_OFFSET // 4,
            ),
        )

    def change_selected_button(self, amount: int, change_to: bool = False) -> None:
        """Change the currently selected button."""
        for x in self.onChangedButton:
            x()

        self.hud_buttons[self.selected_button].set_active(False)
        self.selected_button += amount
        if change_to:
            self.selected_button = amount
        if self.selected_button < 0:
            self.selected_button = renderer_config.HUD_NUM_OF_CELLS - 1
        elif self.selected_button > renderer_config.HUD_NUM_OF_CELLS - 1:
            self.selected_button = 0
        self.hud_buttons[self.selected_button].set_active(True)

    def update(self, delta_time: float, events: Sequence["Event"]) -> int | None:
        """Update the HUD screen state."""

        if self.interactable:
            self.cursorX = math_helpers.lerp(
                self.cursorX, self.selected_button, delta_time * 15
            )
            for event in events:
                if event.type == KEYDOWN and event.key is not None:
                    key = event.key
                    if key == K_LEFT:
                        self.change_selected_button(-1)

                    if key == K_RIGHT:
                        self.change_selected_button(1)

                    if key == K_1:
                        self.change_selected_button(0, True)

                    if key == K_2:
                        self.change_selected_button(1, True)

                    if key == K_3:
                        self.change_selected_button(2, True)

                    if key == K_4:
                        self.change_selected_button(3, True)

                    if key == K_5:
                        self.change_selected_button(4, True)

                    if key == K_RETURN or key == K_SPACE:
                        return self.selected_button
