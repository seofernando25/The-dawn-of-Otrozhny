"""Vertical list UI component."""
from typing import Optional
import pygame
import rendering as renderer
from renderer.text import FONT_PATH
from ui.button import HudButton
from ui.helpers import _resolve_screen


class VerticalList:
    """A vertical list of buttons."""
    
    def __init__(self, str_list, px, py):
        self.items = str_list
        self.objects = []
        self.px = px
        self.py = py
        font = pygame.font.Font(FONT_PATH, renderer.HUD_CELL_TITLE_FONT_SIZE)
        for line in str_list:
            self.objects.append(
                HudButton(font.size(line)[0], renderer.HUD_CELL_TITLE_FONT_SIZE, line)
            )

    def draw(self, screen: Optional[pygame.Surface] = None):
        """Draw the vertical list."""
        for buttons in self.objects:
            buttons.redraw()
        target_screen = _resolve_screen(screen)
        for x in range(len(self.objects)):
            target_screen.blit(
                self.objects[x],
                (self.px, self.py + x * renderer.HUD_CELL_TITLE_FONT_SIZE + x * 10),
            )

