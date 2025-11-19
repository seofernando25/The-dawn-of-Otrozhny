"""
Unified loop runner system - provides a common base for all screen loops.

All loops follow the same pattern: while not done → handle events → draw → tick.
This module provides a reusable implementation.
"""

import pygame
from core import colors
from typing import Protocol, Optional
from core.game_state import GameState


class SceneHandler(Protocol):
    """Protocol for scene handlers that can be run by the loop runner."""

    def handle_events(self, events: list[pygame.event.Event], keys_pressed: tuple) -> bool:
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

    def handle_events(self, events, keys_pressed):
        """Handle basic quit events and return True if should quit."""
        for event in events:
            if event.type == pygame.QUIT:
                return True
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    return True
        return False

    def update(self, delta_time: float) -> None:
        """Default empty update method."""
        pass


def run_scene(
    scene_handler: SceneHandler,
    clock: Optional[pygame.time.Clock] = None,
    bg_color=colors.BLACK,
):
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
        screen.fill(bg_color)
        scene_handler.draw(screen)
        pygame.display.flip()

        clock.tick()

    return True


def run_scene_with_hud(
    scene_handler: SceneHandler,
    hud,
    clock: Optional[pygame.time.Clock] = None,
    bg_color=colors.BLACK,
):
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
            if isinstance(result, int) and 0 <= result <= 4:
                return GameState(result)
            return result

        if scene_handler.handle_events(events, keys_pressed):
            return False

        scene_handler.update(delta_time)

        screen = pygame.display.get_surface()
        if screen is None:
            raise RuntimeError("pygame display surface is not initialized")
        screen.fill(bg_color)
        scene_handler.draw(screen)

        hud.draw(screen)

        pygame.display.flip()
        clock.tick()

    return True
