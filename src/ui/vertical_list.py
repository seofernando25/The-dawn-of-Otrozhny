"""Vertical list UI component."""

from collections.abc import Sequence
from typing import TYPE_CHECKING

from config import renderer_config
from core.backend import get_backend
from renderer.text import FONT_PATH, _blit_surface
from ui.button import HudButton
from ui.helpers import resolve_screen

if TYPE_CHECKING:
    from core.backend.api import GraphicsSurface


class VerticalList:
    """A vertical list of buttons."""

    def __init__(self, str_list: Sequence[str], px: int, py: int) -> None:
        self.items: list[str] = list(str_list)
        self.objects: list[HudButton] = []
        self.px: int = px
        self.py: int = py
        backend = get_backend()
        font = backend.graphics.load_font(FONT_PATH, renderer_config.HUD_CELL_TITLE_FONT_SIZE)
        for line in self.items:
            width, _ = font.size(line)
            self.objects.append(
                HudButton(
                    width, renderer_config.HUD_CELL_TITLE_FONT_SIZE, line
                )
            )

    def draw(self, screen: "GraphicsSurface | None" = None) -> None:
        """Draw the vertical list."""
        for button in self.objects:
            button.redraw()
        target_screen = resolve_screen(screen)
        for index, button in enumerate(self.objects):
            _blit_surface(
                target_screen,
                button._surface,
                (
                    self.px,
                    self.py
                    + index * renderer_config.HUD_CELL_TITLE_FONT_SIZE
                    + index * 10,
                ),
            )
