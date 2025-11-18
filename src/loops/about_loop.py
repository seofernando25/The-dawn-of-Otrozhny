"""
About loop module - displays the about screen with animated text.
"""

import pygame
from renderer.text import message_display, message_display_L
from config import renderer_config
from loops.loop_runner import SceneHandler


class AboutScene(SceneHandler):
    """Scene handler for the about screen."""

    def __init__(self):
        self.sub_title_size = 1
        self.second_sub_title_size = 1

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
        """Update text animation states."""
        self.sub_title_size += delta_time * 10
        if self.sub_title_size > 20:
            self.sub_title_size = 20

        if self.sub_title_size >= 20:
            self.second_sub_title_size += delta_time * 10
            if self.second_sub_title_size > 20:
                self.second_sub_title_size = 1
                self.sub_title_size = 1

    def draw(self, screen):
        """Draw the about screen content."""
        if self.sub_title_size < 20:
            message_display(
                screen,
                "Made By Fernando Nogueira",
                renderer_config.SCREEN_WIDTH // 2,
                renderer_config.VIEWPORT_Y_OFFSET,
                20,
            )
            message_display(
                screen,
                "with some help from the internet",
                renderer_config.SCREEN_WIDTH // 2,
                renderer_config.VIEWPORT_Y_OFFSET * 2,
                int(self.sub_title_size),
            )
        else:
            message_display(
                screen,
                "Made By Stack Overflow",
                renderer_config.SCREEN_WIDTH // 2,
                renderer_config.VIEWPORT_Y_OFFSET,
                20,
            )
            message_display(
                screen,
                "not really",
                renderer_config.SCREEN_WIDTH - 50,
                renderer_config.VIEWPORT_Y_OFFSET,
                8,
            )
            message_display(
                screen,
                "with some help from fernando",
                renderer_config.SCREEN_WIDTH // 2,
                renderer_config.VIEWPORT_Y_OFFSET * 2,
                int(self.second_sub_title_size),
            )

        message_display_L(
            screen,
            'Press "q" to go back',
            renderer_config.VIEWPORT_X_OFFSET,
            renderer_config.SCREEN_HEIGHT - renderer_config.VIEWPORT_Y_OFFSET,
            renderer_config.HUD_CELL_TITLE_FONT_SIZE,
        )


def run_about_loop():
    """Run the about screen loop."""
    from loops.loop_runner import run_scene

    scene = AboutScene()
    return run_scene(scene)
