"""
About loop module - displays the about screen with animated text.
"""
import pygame
import textDraw
import rendering as renderer
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
            textDraw.message_display(screen,
                                     "Made By Fernando Nogueira",
                                     renderer.SCREEN_WIDTH // 2,
                                     renderer.VIEWPORT_Y_OFFSET, 20)
            textDraw.message_display(screen,
                                     "with some help from the internet",
                                     renderer.SCREEN_WIDTH // 2,
                                     renderer.VIEWPORT_Y_OFFSET * 2,
                                     int(self.sub_title_size))
        else:
            textDraw.message_display(screen, "Made By Stack Overflow",
                                     renderer.SCREEN_WIDTH // 2,
                                     renderer.VIEWPORT_Y_OFFSET, 20)
            textDraw.message_display(screen, "not really",
                                     renderer.SCREEN_WIDTH - 50,
                                     renderer.VIEWPORT_Y_OFFSET, 8)
            textDraw.message_display(
                screen,
                "with some help from fernando",
                renderer.SCREEN_WIDTH // 2,
                renderer.VIEWPORT_Y_OFFSET * 2,
                int(self.second_sub_title_size))

        textDraw.message_display_L(
            screen, "Press \"q\" to go back",
            renderer.VIEWPORT_X_OFFSET,
            renderer.SCREEN_HEIGHT - renderer.VIEWPORT_Y_OFFSET,
            renderer.HUD_CELL_TITLE_FONT_SIZE)


def run_about_loop():
    """
    Run the about screen loop.

    Returns:
        bool: Always returns False (quit to menu).
    """
    from loops.loop_runner import run_scene

    scene = AboutScene()
    return run_scene(scene)
