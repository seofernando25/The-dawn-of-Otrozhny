"""Vertical list UI component."""

from collections.abc import Sequence

import pygame

from config import renderer_config
from renderer.text import FONT_PATH
from ui.button import HudButton
from ui.helpers import resolve_screen


class VerticalList:
    """A vertical list of buttons."""

    def __init__(self, str_list: Sequence[str], px: int, py: int) -> None:
        self.items: list[str] = list(str_list)
        self.objects: list[HudButton] = []
        self.px: int = px
        self.py: int = py
        font = pygame.font.Font(FONT_PATH, renderer_config.HUD_CELL_TITLE_FONT_SIZE)
        for line in self.items:
            self.objects.append(
                HudButton(
                    font.size(line)[0], renderer_config.HUD_CELL_TITLE_FONT_SIZE, line
                )
            )

    def draw(self, screen: pygame.Surface | None = None) -> None:
        """Draw the vertical list."""
        for button in self.objects:
            button.redraw()
        target_screen = resolve_screen(screen)
        for index, button in enumerate(self.objects):
            _ = target_screen.blit(
                button,
                (
                    self.px,
                    self.py
                    + index * renderer_config.HUD_CELL_TITLE_FONT_SIZE
                    + index * 10,
                ),
            )
