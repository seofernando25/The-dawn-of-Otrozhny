"""HUD screen component."""
from typing import Optional
import pygame
import pygame.constants as pyConst
from config import renderer_config
from utils import math_helpers
from core import colors
from ui.helpers import (
    _generate_hud_viewport,
    _generate_hud_surfaces,
    render_hud_surfaces,
    _resolve_screen,
)


class HudScreen:
    """Main HUD screen that manages multiple HUD buttons."""
    
    def __init__(self, interactable=True, dynamic=False, *, activated_sound=None):
        self.viewPort = _generate_hud_viewport()
        self.viewPort.fill(colors.GRAY_VARIATION_2)
        self.hud_buttons = _generate_hud_surfaces(self.viewPort, activated_sound=activated_sound)
        self.interactable = interactable
        self.dynamic = dynamic
        self.selected_button = 0
        self.cursorX = self.selected_button
        # Should have created an event handler class :/
        self.onChangedButton = []

    def set_button_color(self, buttonIndex, textIndex, color):
        """Set the color of a specific text element in a button."""
        self.hud_buttons[buttonIndex].set_color(textIndex, color)

    def set_button_subtitle(self, buttonIndex, text):
        """Set the subtitle of a button."""
        self.hud_buttons[buttonIndex].set_subtitle(text)

    def set_button_title(self, buttonIndex, text):
        """Set the title of a button."""
        self.hud_buttons[buttonIndex].set_title(text)

    def set_button_text(self, buttonIndex, text):
        """Set the main text of a button."""
        self.hud_buttons[buttonIndex].set_text(text)

    def draw(self, screen: Optional[pygame.Surface] = None):
        """Draw the HUD screen."""
        if self.interactable or self.dynamic:
            self.viewPort.fill(colors.GRAY_VARIATION_2)
        render_hud_surfaces(self.viewPort, self.hud_buttons)

        if self.interactable:
            pygame.draw.rect(
                self.viewPort,
                colors.BLACK,
                [
                    int(
                        self.cursorX * (self.viewPort.get_width() / 5)
                        + renderer_config.HUD_CELL_OFFSET
                        + 5
                    ),
                    self.viewPort.get_height(),
                    100,
                    -10,
                ],
            )
        target_screen = _resolve_screen(screen)
        target_screen.blit(
            self.viewPort,
            (
                renderer_config.VIEWPORT_X_OFFSET,
                renderer_config.SCREEN_HEIGHT
                - self.viewPort.get_height()
                - renderer_config.VIEWPORT_Y_OFFSET // 4,
            ),
        )

    def change_selected_button(self, amount, change_to=False):
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

    def update(self, dt, events):
        """Update the HUD screen state."""
        if self.interactable:
            self.cursorX = math_helpers.lerp(self.cursorX, self.selected_button, dt * 15)
            for event in events:
                if event.type == pygame.KEYDOWN:
                    if event.key == pyConst.K_LEFT:
                        self.change_selected_button(-1)

                    if event.key == pyConst.K_RIGHT:
                        self.change_selected_button(1)

                    if event.key == pyConst.K_1:
                        self.change_selected_button(0, True)

                    if event.key == pyConst.K_2:
                        self.change_selected_button(1, True)

                    if event.key == pyConst.K_3:
                        self.change_selected_button(2, True)

                    if event.key == pyConst.K_4:
                        self.change_selected_button(3, True)

                    if event.key == pyConst.K_5:
                        self.change_selected_button(4, True)

                    if event.key == pyConst.K_RETURN or event.key == pyConst.K_SPACE:
                        return self.selected_button

