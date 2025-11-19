from dataclasses import dataclass
from importlib import import_module
from typing import Any

from core.audio import AudioManager
from core.backend import get_backend

from core.backend.api import GraphicsSurface, Clock

EnemyStateManager = Any
Player = Any
Level = Any
GridManager = Any


def _build_enemy_state() -> "EnemyStateManager":
    module = import_module("entities.enemy_state")
    enemy_state_cls = getattr(module, "EnemyStateManager")
    return enemy_state_cls()


def get_screen():
    """Get or create the main screen surface using the backend."""
    backend = get_backend()
    screen = backend.graphics.get_display_surface()
    screen.set_alpha(None)
    return screen


@dataclass
class BaseContext:
    """Base container for shared services."""

    screen: "GraphicsSurface | None"
    audio: "AudioManager"


@dataclass
class GameContext(BaseContext):
    """Aggregates runtime state for the main gameplay loops."""

    player: Any | None = None
    level: Any | None = None
    clock: Clock | None = None
    enemy_state: EnemyStateManager | None = None

    def update_level(self, level: Any) -> None:
        """Swap the active level reference."""
        self.level = level

    def update_player(self, player: Any) -> None:
        """Swap the active player reference."""
        self.player = player

    def ensure_enemy_state(self) -> EnemyStateManager:
        """Get or create the enemy state manager."""
        if self.enemy_state is None:
            self.enemy_state = _build_enemy_state()
        return self.enemy_state


@dataclass
class EditorContext(BaseContext):
    """Context wrapper dedicated to the level editor."""

    grid_manager: Any | None = None

    def ensure_grid_manager(self, manager: GridManager) -> GridManager:
        """Set and return the grid manager, enabling fluent initialization."""
        self.grid_manager = manager
        return manager


def build_game_context(
    *,
    player: Any,
    level: Any | None = None,
    screen: GraphicsSurface | None = None,
    audio_manager_service: AudioManager,
    clock: Clock | None = None,
    enemy_state: Any | None = None,
) -> GameContext:
    """Create a GameContext with required dependencies."""
    if player is None:
        raise ValueError("player is required for GameContext")

    screen = screen or get_screen()
    if enemy_state is None:
        enemy_state = _build_enemy_state()

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
    screen: GraphicsSurface | None = None,
    audio_manager_service: AudioManager,
    grid_manager: Any | None = None,
) -> EditorContext:
    """Factory helper for editor-specific tooling."""

    screen = screen or get_screen()
    ctx = EditorContext(
        screen=screen, audio=audio_manager_service, grid_manager=grid_manager
    )
    return ctx
