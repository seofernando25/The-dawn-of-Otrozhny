"""Common context containers for gameplay and editor subsystems.

These dataclasses help us thread shared services explicitly instead of
relying on hidden globals. They are deliberately lightweight so callers
can construct them inside setup routines and pass them down the stack.
"""

from __future__ import annotations

from dataclasses import dataclass, field, replace
from typing import TYPE_CHECKING, Dict, Optional, Protocol, runtime_checkable

import pygame

if TYPE_CHECKING:  # typing-only imports
    from audio_manager import AudioManager
    from entities.player import Player
    from core.level import Level
    from level_editor.editor import GridManager


@runtime_checkable
class SupportsClose(Protocol):
    """Subset of pygame objects that expose ``quit`` or ``close``."""

    def quit(self) -> None: ...


@dataclass
class BaseContext:
    """Base container for shared services."""

    screen: pygame.Surface
    audio: "AudioManager"
    services: Dict[str, object] = field(default_factory=dict)

    def with_override(self, **kwargs: object) -> "BaseContext":
        """Return a shallow copy with the provided overrides."""
        return replace(self, **kwargs)


@dataclass
class GameContext(BaseContext):
    """Aggregates runtime state for the main gameplay loops."""

    player: Optional["Player"] = None
    level: Optional["Level"] = None
    clock: Optional[pygame.time.Clock] = None

    def update_level(self, level: "Level") -> None:
        """Swap the active level reference."""
        self.level = level
        self.services["level"] = level

    def update_player(self, player: "Player") -> None:
        """Swap the active player reference."""
        self.player = player
        self.services["player"] = player


@dataclass
class EditorContext(BaseContext):
    """Context wrapper dedicated to the level editor."""

    grid_manager: Optional["GridManager"] = None

    def ensure_grid_manager(self, manager: "GridManager") -> "GridManager":
        """Set and return the grid manager, enabling fluent initialization."""
        self.grid_manager = manager
        self.services["grid_manager"] = manager
        return manager


def build_game_context(
    *,
    player: "Player",
    level: Optional["Level"] = None,
    screen: Optional[pygame.Surface] = None,
    audio_manager_service: Optional["AudioManager"] = None,
    clock: Optional[pygame.time.Clock] = None,
) -> GameContext:
    """Factory helper that fills defaults from existing globals.
    
    Note: player is required but made optional in the dataclass to satisfy
    Python's dataclass field ordering requirements (required fields can't
    follow default fields from parent classes).
    """
    from audio_manager import AudioManager
    from renderer import config as renderer_config

    if player is None:
        raise ValueError("player is required for GameContext")
    
    screen = screen or renderer_config.get_screen()
    audio_manager_service = audio_manager_service or AudioManager.get_instance()
    ctx = GameContext(
        screen=screen,
        audio=audio_manager_service,
        player=player,
        level=level,
        clock=clock,
    )
    if level is not None:
        ctx.services.update({"level": level, "player": player, "clock": clock})
    else:
        ctx.services.update({"player": player, "clock": clock})
    return ctx


def build_editor_context(
    *,
    screen: Optional[pygame.Surface] = None,
    audio_manager_service: Optional["AudioManager"] = None,
    grid_manager: Optional["GridManager"] = None,
) -> EditorContext:
    """Factory helper for editor-specific tooling."""
    from audio_manager import AudioManager
    from renderer import config as renderer_config

    screen = screen or renderer_config.get_screen()
    audio_manager_service = audio_manager_service or AudioManager.get_instance()
    ctx = EditorContext(screen=screen, audio=audio_manager_service, grid_manager=grid_manager)
    if grid_manager is not None:
        ctx.services["grid_manager"] = grid_manager
    return ctx

