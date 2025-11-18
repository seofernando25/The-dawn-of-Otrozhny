"""
Tutorial loop module - displays tutorial tabs with briefing/map editor/items/enemy status/help.
"""
import pygame
import menuTabs
import textDraw
import rendering as renderer
from loops.loop_runner import SceneHandler


class TutorialScene(SceneHandler):
    """Scene handler for the tutorial screen."""

    def __init__(self):
        import ui
        self.hud = ui.HudScreen()
        self.hud.set_button_text(0, "Briefing")
        self.hud.set_button_text(1, "Map Editor")
        self.hud.set_button_text(2, "Items")
        self.hud.set_button_text(3, "Enemy Status")
        self.hud.set_button_text(4, "?")
        self.hud.draw()

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
            menuTabs.render_tutorial_tab_4()
        if self.hud.selected_button == 1:
            menuTabs.render_tutorial_tab_2()
        if self.hud.selected_button == 2:
            menuTabs.render_tutorial_tab_3()
        if self.hud.selected_button == 3:
            menuTabs.render_tutorial_tab_1()
        if self.hud.selected_button == 4:
            menuTabs.render_tutorial_tab_5()

        self.hud.update(0, [])  # Update HUD visuals
        self.hud.draw()

        textDraw.message_display_L(
            screen, "Press \"q\" to go back",
            renderer.VIEWPORT_X_OFFSET,
            renderer.VIEWPORT_Y_OFFSET,
            renderer.HUD_CELL_TITLE_FONT_SIZE)


def run_tutorial_loop():
    """
    Run the tutorial screen loop.

    Returns:
        bool: Always returns False (quit to menu).
    """
    from loops.loop_runner import run_scene_with_hud

    scene = TutorialScene()
    return run_scene_with_hud(scene, scene.hud)
