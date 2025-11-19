"""
Menu loop module - handles the main menu with fractal background and other effects.
"""

import pygame
from ui import HudScreen
from renderer import effects as otherEffects
from renderer.text import message_display_MT
from config import renderer_config
from scenes.loop_runner import SceneHandler
from core.game_state import GameState


class MenuScene(SceneHandler):
    """Scene handler for the main menu."""

    def __init__(self):
        self.hud = HudScreen()
        self.hud.set_button_text(0, "Play")
        self.hud.set_button_text(1, "Editor")
        self.hud.set_button_text(2, "Tutorial")
        self.hud.set_button_text(3, "About")
        self.hud.set_button_text(4, "Exit")

        self.fractal = otherEffects.ChaosObject(
            (renderer_config.SCREEN_WIDTH // 2, (renderer_config.SCREEN_HEIGHT // 2) + 15), 225, 3
        )
        self.star_field = otherEffects.StarField((renderer_config.SCREEN_WIDTH, renderer_config.SCREEN_HEIGHT))

        # Connect fractal speed to HUD button changes
        self.hud.onChangedButton.append(self.star_field.change_speed)

        pygame.mouse.set_visible(True)
        pygame.event.set_grab(False)

    def handle_events(self, events, keys_pressed):
        """Handle quit and keyboard events."""
        for event in events:
            if event.type == pygame.QUIT:
                return True
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p:  # Secret quit key
                    return True
        return False

    def update(self, delta_time):
        """Update menu animations."""
        for _ in range(10):
            self.fractal.update()

        self.star_field.update(delta_time)

        if self.hud.selected_button == GameState.Quit.value:
            self.star_field.speed += delta_time * 75
            if self.star_field.speed > 100:
                self.star_field.speed = 100

    def draw(self, screen):
        """Draw the menu screen."""
        self.star_field.draw()
        screen.blit(self.star_field, (0, 0))
        self.fractal.draw(screen)

        message_display_MT(
            screen, "The dawn of Otrozhny", renderer_config.SCREEN_WIDTH // 2, 100, 30
        )
        message_display_MT(
            screen, "Containment breach", renderer_config.SCREEN_WIDTH // 2, 150, 30
        )


def run_menu_loop():
    """Run the main menu loop."""
    from scenes.loop_runner import run_scene_with_hud

    scene = MenuScene()
    return run_scene_with_hud(scene, scene.hud)
