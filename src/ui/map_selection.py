"""Map selection screen component."""
from typing import List, Optional
import pygame
from renderer import utils as renderer_utils
from utils import math_helpers
from core import colors
from ui.button import HudButton
from ui.helpers import _resolve_screen


class MapSelectionScreen(pygame.Surface):
    """Screen for selecting maps in a grid layout."""
    
    def __init__(self):
        pygame.Surface.__init__(self, (renderer_utils.SCREEN_WIDTH, renderer_utils.SCREEN_HEIGHT))
        self.hud_buttons: List[List[HudButton]] = [
            [HudButton(100, 100, text=str((x, y))) for y in range(3)] for x in range(5)
        ]
        self.selected_button_x = 0
        self.selected_button_y = 0
        self._pointer_x = 100
        self._pointer_y = 150
        for column in self.hud_buttons:
            for button in column:
                button.redraw()
                button.protected = False

    def draw(self, screen: Optional[pygame.Surface] = None):
        """Draw the map selection screen."""
        self.fill(colors.BLACK)
        for x in range(5):
            for y in range(3):
                self.blit(
                    self.hud_buttons[x][y],
                    (
                        50 + x * 100 + x * renderer_utils.HUD_CELL_OFFSET,
                        100 + y * 100 + y * renderer_utils.HUD_CELL_OFFSET,
                    ),
                )

        pygame.draw.circle(
            self, colors.WHITE, (int(self._pointer_x), int(self._pointer_y)), 10
        )
        _resolve_screen(screen).blit(self, (0, 0))

    def update(self, dt, events, screen: Optional[pygame.Surface] = None):
        """Update the map selection screen state."""
        pos = (
            100
            + self.selected_button_x * 100
            + self.selected_button_x * renderer_utils.HUD_CELL_OFFSET,
            150
            + self.selected_button_y * 100
            + self.selected_button_y * renderer_utils.HUD_CELL_OFFSET,
        )
        self._pointer_x = math_helpers.lerp(self._pointer_x, pos[0], dt * 10)
        self._pointer_y = math_helpers.lerp(self._pointer_y, pos[1], dt * 10)

        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    self.change_selected_button(-1)
                elif event.key == pygame.K_RIGHT:
                    self.change_selected_button(1)
                elif event.key == pygame.K_UP:
                    self.change_selected_button(-1, False)
                elif event.key == pygame.K_DOWN:
                    self.change_selected_button(1, False)
        self.draw(screen)

    def change_selected_button(self, amount, change_x=True):
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

