"""
Unified loop runner system - provides a common base for all screen loops.

All loops follow the same pattern: while not done → handle events → draw → tick.
This module provides a reusable implementation.
"""

from collections.abc import Sequence
from typing import TYPE_CHECKING, Protocol

from core import colors
from core.backend import get_backend
from core.game_state import GameState

if TYPE_CHECKING:
    from core.backend.api import GraphicsSurface, Clock, Event
else:
    # For runtime, we'll use the backend's event type
    Event = object

# Removed _unwrap_surface - we now use GraphicsSurface directly


class HudLike(Protocol):
    def update(
        self, delta_time: float, events: Sequence[Event]
    ) -> GameState | int | None: ...

    def draw(self, screen: "GraphicsSurface") -> None: ...


class SceneHandler(Protocol):
    """Protocol for scene handlers that can be run by the loop runner."""

    def handle_events(
        self,
        events: list[Event],
        keys_pressed: Sequence[bool],
    ) -> bool:
        """Handle events. Return True to quit."""
        ...

    def update(self, delta_time: float) -> None:
        """Update game logic."""
        ...

    def draw(self, screen: "GraphicsSurface") -> None:
        """Draw the scene."""
        ...


class SimpleSceneHandler:
    """Base class for simple scenes that just handle quit events."""

    def handle_events(
        self, events: list[Event], keys_pressed: Sequence[bool]
    ) -> bool:
        """Handle basic quit events and return True if should quit."""
        _ = keys_pressed
        from core.backend.api import QUIT, KEYDOWN
        from core.backend.api import K_q
        for event in events:
            if event.type == QUIT:
                return True
            elif event.type == KEYDOWN and event.key is not None:
                if event.key == K_q:
                    return True
        return False

    def update(self, delta_time: float) -> None:
        """Default empty update method."""
        _ = delta_time
        pass


def run_scene(
    scene_handler: SceneHandler,
    clock: "Clock | None" = None,
    bg_color: tuple[int, int, int] = colors.BLACK,
) -> bool:
    """Run a scene via the unified loop pattern and return False when it requests to quit."""
    backend = get_backend()
    if clock is None:
        clock = backend.clock

    done = False
    while not done:
        delta_time = clock.get_time() / 1000
        events = backend.input.get_events()
        keys_pressed = backend.input.get_pressed_keys()

        if scene_handler.handle_events(events, keys_pressed):
            return False

        scene_handler.update(delta_time)

        screen = backend.graphics.get_display_surface()
        if screen is None:
            raise RuntimeError("Display surface is not initialized")
        screen.fill(bg_color)
        scene_handler.draw(screen)
        backend.graphics.flip()

        _ = clock.tick()

    return True


def run_scene_with_hud(
    scene_handler: SceneHandler,
    hud: HudLike,
    clock: "Clock | None" = None,
    bg_color: tuple[int, int, int] = colors.BLACK,
) -> bool | GameState:
    """Run a HUD-enabled scene loop and return False when the handler or HUD requests exit."""
    backend = get_backend()
    if clock is None:
        clock = backend.clock

    done = False
    while not done:
        delta_time = clock.get_time() / 1000
        events = backend.input.get_events()
        keys_pressed = backend.input.get_pressed_keys()

        result = hud.update(delta_time, events)
        if result is not None:
            if isinstance(result, GameState):
                return result
            # After checking it's not None and not GameState, it must be int
            return GameState(result)

        if scene_handler.handle_events(events, keys_pressed):
            return False

        scene_handler.update(delta_time)

        screen = backend.graphics.get_display_surface()
        if screen is None:
            raise RuntimeError("Display surface is not initialized")
        screen.fill(bg_color)
        scene_handler.draw(screen)

        hud.draw(screen)

        backend.graphics.flip()
        _ = clock.tick()

    return True
