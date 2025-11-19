"""
Menu loop module - handles the main menu with fractal background and other effects.
"""

from collections.abc import Sequence
from typing import TYPE_CHECKING, override

from ui import HudScreen
from renderer import effects as otherEffects
from renderer.text import _blit_surface, message_display_MT
from config import renderer_config
from scenes.loop_runner import SceneHandler
from core.game_state import GameState
from core.backend import get_backend

if TYPE_CHECKING:
    from core.backend.api import GraphicsSurface, Event
else:
    Event = object


class MenuScene(SceneHandler):
    """Scene handler for the main menu."""

    def __init__(self):
        self.hud: HudScreen = HudScreen()
        self.hud.set_button_text(0, "Play")
        self.hud.set_button_text(1, "Editor")
        self.hud.set_button_text(2, "Tutorial")
        self.hud.set_button_text(3, "About")
        self.hud.set_button_text(4, "Exit")

        self.fractal: otherEffects.ChaosObject = otherEffects.ChaosObject(
            (
                renderer_config.SCREEN_WIDTH // 2,
                (renderer_config.SCREEN_HEIGHT // 2) + 15,
            ),
            225,
            3,
        )
        self.star_field: otherEffects.StarField = otherEffects.StarField(
            (renderer_config.SCREEN_WIDTH, renderer_config.SCREEN_HEIGHT)
        )

        # Connect fractal speed to HUD button changes
        self.hud.onChangedButton.append(self.star_field.change_speed)

        backend = get_backend()
        backend.input.set_mouse_visible(True)
        backend.input.set_event_grab(False)

    @override
    def handle_events(
        self, events: list[Event], keys_pressed: Sequence[bool]
    ) -> bool:
        """Handle quit and keyboard events."""
        from core.backend.api import QUIT, KEYDOWN, K_p
        for event in events:
            if event.type == QUIT:
                return True
            elif event.type == KEYDOWN and event.key is not None:
                if event.key == K_p:  # Secret quit key
                    return True
        return False

    @override
    def update(self, delta_time: float) -> None:
        """Update menu animations."""
        for _ in range(10):
            self.fractal.update()

        self.star_field.update(delta_time)

        if self.hud.selected_button == GameState.Quit.value:
            self.star_field.speed += delta_time * 75
            if self.star_field.speed > 100:
                self.star_field.speed = 100

    @override
    def draw(self, screen: "GraphicsSurface") -> None:
        """Draw the menu screen."""
        self.star_field.draw()
        _blit_surface(screen, self.star_field._surface, (0, 0))

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
