"""
Unified loop runner system - provides a common base for all screen loops.

All loops follow the same pattern: while not done → handle events → draw → tick.
This module provides a reusable implementation.
"""

from collections.abc import Sequence
from typing import Protocol

import pygame

from core import colors
from core.game_state import GameState


class HudLike(Protocol):
    def update(
        self, delta_time: float, events: Sequence[pygame.event.Event]
    ) -> GameState | int | None: ...

    def draw(self, screen: pygame.Surface) -> None: ...


class SceneHandler(Protocol):
    """Protocol for scene handlers that can be run by the loop runner."""

    def handle_events(
        self,
        events: list[pygame.event.Event],
        keys_pressed: Sequence[bool],
    ) -> bool:
        """Handle pygame events. Return True to quit."""
        ...

    def update(self, delta_time: float) -> None:
        """Update game logic."""
        ...

    def draw(self, screen: pygame.Surface) -> None:
        """Draw the scene."""
        ...


class SimpleSceneHandler:
    """Base class for simple scenes that just handle quit events."""

    def handle_events(
        self, events: list[pygame.event.Event], keys_pressed: Sequence[bool]
    ) -> bool:
        """Handle basic quit events and return True if should quit."""
        _ = keys_pressed
        for event in events:
            if event.type == pygame.QUIT:
                return True
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    return True
        return False

    def update(self, delta_time: float) -> None:
        """Default empty update method."""
        _ = delta_time
        pass


def run_scene(
    scene_handler: SceneHandler,
    clock: pygame.time.Clock | None = None,
    bg_color: tuple[int, int, int] = colors.BLACK,
) -> bool:
    """Run a scene via the unified loop pattern and return False when it requests to quit."""
    if clock is None:
        clock = pygame.time.Clock()

    done = False
    while not done:
        delta_time = clock.get_time() / 1000
        events = pygame.event.get()
        keys_pressed = pygame.key.get_pressed()

        if scene_handler.handle_events(events, keys_pressed):
            return False

        scene_handler.update(delta_time)

        screen = pygame.display.get_surface()
        if screen is None:
            raise RuntimeError("pygame display surface is not initialized")
        _ = screen.fill(bg_color)
        scene_handler.draw(screen)
        pygame.display.flip()

        _ = clock.tick()

    return True


def run_scene_with_hud(
    scene_handler: SceneHandler,
    hud: HudLike,
    clock: pygame.time.Clock | None = None,
    bg_color: tuple[int, int, int] = colors.BLACK,
) -> bool | GameState:
    """Run a HUD-enabled scene loop and return False when the handler or HUD requests exit."""
    if clock is None:
        clock = pygame.time.Clock()

    done = False
    while not done:
        delta_time = clock.get_time() / 1000
        events = pygame.event.get()
        keys_pressed = pygame.key.get_pressed()

        result = hud.update(delta_time, events)
        if result is not None:
            if isinstance(result, GameState):
                return result
            # After checking it's not None and not GameState, it must be int
            return GameState(result)

        if scene_handler.handle_events(events, keys_pressed):
            return False

        scene_handler.update(delta_time)

        screen = pygame.display.get_surface()
        if screen is None:
            raise RuntimeError("pygame display surface is not initialized")
        _ = screen.fill(bg_color)
        scene_handler.draw(screen)

        hud.draw(screen)

        pygame.display.flip()
        _ = clock.tick()

    return True
