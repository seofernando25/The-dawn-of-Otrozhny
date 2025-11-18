"""
Tutorial loop module - displays tutorial tabs with briefing/map editor/items/enemy status/help.
"""

import pygame
from ui import menu_tabs
from renderer.text import message_display_L
from renderer import utils as renderer_utils
from loops.loop_runner import SceneHandler
from ui import HudScreen


class TutorialScene(SceneHandler):
    """Scene handler for the tutorial screen."""

    def __init__(self):
        self.hud = HudScreen()
        self.hud.set_button_text(0, "Briefing")
        self.hud.set_button_text(1, "Map Editor")
        self.hud.set_button_text(2, "Items")
        self.hud.set_button_text(3, "Enemy Status")
        self.hud.set_button_text(4, "?")

    def handle_events(self, events, keys_pressed):
        """Handle quit events."""
        for event in events:
            if event.type == pygame.QUIT:
                return True
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    return True
        return False

    def update(self, delta_time):
        """No update logic for tutorial."""
        pass

    def draw(self, screen):
        """Draw tutorial content based on selected tab."""
        if self.hud.selected_button == 0:
            menu_tabs.render_tutorial_tab_4()
        if self.hud.selected_button == 1:
            menu_tabs.render_tutorial_tab_2()
        if self.hud.selected_button == 2:
            menu_tabs.render_tutorial_tab_3()
        if self.hud.selected_button == 3:
            menu_tabs.render_tutorial_tab_1()
        if self.hud.selected_button == 4:
            menu_tabs.render_tutorial_tab_5()

        self.hud.update(0, [])  # Update HUD visuals
        self.hud.draw(screen)

        message_display_L(
            screen,
            'Press "q" to go back',
            renderer_utils.VIEWPORT_X_OFFSET,
            renderer_utils.VIEWPORT_Y_OFFSET,
            renderer_utils.HUD_CELL_TITLE_FONT_SIZE,
        )


def run_tutorial_loop():
    """
    Run the tutorial screen loop.

    Returns:
        bool: Always returns False (quit to menu).
    """
    from loops.loop_runner import run_scene_with_hud

    scene = TutorialScene()
    return run_scene_with_hud(scene, scene.hud)
