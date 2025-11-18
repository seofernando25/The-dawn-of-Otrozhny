"""Common context containers for gameplay and editor subsystems.

These dataclasses help us thread shared services explicitly instead of
relying on hidden globals. They are deliberately lightweight so callers
can construct them inside setup routines and pass them down the stack.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
from typing import TYPE_CHECKING, Optional, Protocol, runtime_checkable

import pygame

if TYPE_CHECKING:  # typing-only imports
    from audio_manager import AudioManager
    from entities.player import Player
    from core.level import Level
    from level_editor.editor import GridManager
    from core.enemy_state import EnemyStateManager


@runtime_checkable
class SupportsClose(Protocol):
    """Subset of pygame objects that expose ``quit`` or ``close``."""

    def quit(self) -> None: ...


@dataclass
class BaseContext:
    """Base container for shared services."""

    screen: pygame.Surface
    audio: "AudioManager"

    def with_override(self, **kwargs: object) -> "BaseContext":
        """Return a shallow copy with the provided overrides."""
        return replace(self, **kwargs)


@dataclass
class GameContext(BaseContext):
    """Aggregates runtime state for the main gameplay loops."""

    player: Optional["Player"] = None
    level: Optional["Level"] = None
    clock: Optional[pygame.time.Clock] = None
    enemy_state: Optional["EnemyStateManager"] = None

    def update_level(self, level: "Level") -> None:
        """Swap the active level reference."""
        self.level = level

    def update_player(self, player: "Player") -> None:
        """Swap the active player reference."""
        self.player = player

    def ensure_enemy_state(self) -> "EnemyStateManager":
        """Get or create the enemy state manager."""
        if self.enemy_state is None:
            from core.enemy_state import EnemyStateManager
            self.enemy_state = EnemyStateManager()
        return self.enemy_state


@dataclass
class EditorContext(BaseContext):
    """Context wrapper dedicated to the level editor."""

    grid_manager: Optional["GridManager"] = None

    def ensure_grid_manager(self, manager: "GridManager") -> "GridManager":
        """Set and return the grid manager, enabling fluent initialization."""
        self.grid_manager = manager
        return manager


def build_game_context(
    *,
    player: "Player",
    level: Optional["Level"] = None,
    screen: Optional[pygame.Surface] = None,
    audio_manager_service: "AudioManager",
    clock: Optional[pygame.time.Clock] = None,
    enemy_state: Optional["EnemyStateManager"] = None,
) -> GameContext:
    """Factory helper that creates a GameContext with required dependencies.
    
    Note: player and audio_manager_service are required. screen will be created
    if not provided. enemy_state will be created if not provided.
    """
    from renderer.config import get_screen
    from core.enemy_state import EnemyStateManager

    if player is None:
        raise ValueError("player is required for GameContext")
    if audio_manager_service is None:
        raise ValueError("audio_manager_service is required for GameContext")
    
    screen = screen or get_screen()
    if enemy_state is None:
        enemy_state = EnemyStateManager()
    
    ctx = GameContext(
        screen=screen,
        audio=audio_manager_service,
        player=player,
        level=level,
        clock=clock,
        enemy_state=enemy_state,
    )
    return ctx


def build_editor_context(
    *,
    screen: Optional[pygame.Surface] = None,
    audio_manager_service: "AudioManager",
    grid_manager: Optional["GridManager"] = None,
) -> EditorContext:
    """Factory helper for editor-specific tooling."""
    from renderer.config import get_screen

    if audio_manager_service is None:
        raise ValueError("audio_manager_service is required for EditorContext")
    
    screen = screen or get_screen()
    ctx = EditorContext(screen=screen, audio=audio_manager_service, grid_manager=grid_manager)
    return ctx

