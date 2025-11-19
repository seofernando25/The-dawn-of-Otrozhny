"""
Tutorial loop module - displays tutorial tabs with briefing/map editor/items/enemy status/help.
"""

from collections.abc import Sequence
from typing import override

from config import renderer_config
from renderer.text import message_display_L
from scenes.loop_runner import SceneHandler
from ui import HudScreen, menu_tabs
from core.backend.api import Event, GraphicsSurface


class TutorialScene(SceneHandler):
    """Scene handler for the tutorial screen."""

    def __init__(self):
        self.hud: HudScreen = HudScreen()
        self.hud.set_button_text(0, "Briefing")
        self.hud.set_button_text(1, "Map Editor")
        self.hud.set_button_text(2, "Items")
        self.hud.set_button_text(3, "Enemy Status")
        self.hud.set_button_text(4, "?")

    @override
    def handle_events(
        self, events: list["Event"], keys_pressed: Sequence[bool]
    ) -> bool:
        _ = keys_pressed
        from core.backend.api import QUIT, KEYDOWN, K_q

        """Handle quit events."""
        for event in events:
            if event.type == QUIT:
                return True
            elif event.type == KEYDOWN:
                if hasattr(event, "key") and event.key == K_q:
                    return True
        return False

    @override
    def update(self, delta_time: float) -> None:
        """No update logic for tutorial."""
        pass

    @override
    def draw(self, screen: "GraphicsSurface") -> None:
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

        _ = self.hud.update(0, [])  # Update HUD visuals
        self.hud.draw(screen)

        message_display_L(
            screen,
            'Press "q" to go back',
            renderer_config.VIEWPORT_X_OFFSET,
            renderer_config.VIEWPORT_Y_OFFSET,
            renderer_config.HUD_CELL_TITLE_FONT_SIZE,
        )


def run_tutorial_loop():
    """Run the tutorial screen loop."""
    from scenes.loop_runner import run_scene_with_hud

    scene = TutorialScene()
    return run_scene_with_hud(scene, scene.hud)
