from __future__ import annotations

from typing import cast

import pygame

from core.context import GameContext
from entities.enemy_state import EnemyStateManager
from entities.player import Player
from entities.status import EnemyStatus
from level.level import Level
from ui import HudScreen
from ui.button import HudButton


class HudSystem:
    """Manages HUD updates and rendering."""

    def __init__(self, context: GameContext):
        self.context: GameContext = context
        # Get UI sound from audio manager for button activation sounds
        from ui.audio_helpers import get_ui_activation_sound

        activated_sound = get_ui_activation_sound(context.audio)
        self.hud: HudScreen = HudScreen(
            interactable=False, activated_sound=activated_sound
        )
        self._cache: dict[str, object | None] = {
            "keys": None,
            "status_subtitle": None,
            "status_color": None,
            "status_time": None,
            "collectibles": None,
            "health": None,
        }
        self._initialize_hud()

        # Cache minimap surface reference for cleaner access
        # The last HUD button is used for the minimap
        self._minimap_surface: HudButton = self.hud.hud_buttons[-1]

    def _initialize_hud(self):
        """Initialize HUD labels and settings."""
        self.hud.set_button_title(0, "Health")
        self.hud.set_button_title(1, "Stars")
        self.hud.set_button_subtitle(1, "Found")
        self.hud.set_button_title(2, "Keys")
        self.hud.set_button_title(3, "Status")

        # Allow Loop to control hud button surface draw calls
        self.hud.hud_buttons[-1].protected = False

    def update(
        self,
        delta_time: float,
        events: list[pygame.event.Event],
    ) -> int | None:
        """Update HUD with current game state."""
        result = self.hud.update(delta_time, events)
        if result is not None:
            return result

        player_obj = cast(Player | None, self.context.player)
        if player_obj is None:
            return None
        player = player_obj

        current_map_obj = cast(Level | None, self.context.level)
        if current_map_obj is None:
            return None
        current_map = current_map_obj

        enemy_state_obj = cast(EnemyStateManager | None, self.context.enemy_state)
        if enemy_state_obj is None:
            return None
        enemy_state = enemy_state_obj

        # Update HUD values with caching
        self._update_keys(player.keys)
        self._update_enemy_status(enemy_state.status, enemy_state.status_time_left)
        self._update_collectibles(
            current_map.num_of_collected, current_map.num_of_collectibles
        )
        self._update_health(player.health)

        return None

    def _update_health(self, health: float | int) -> None:
        """Update health value with caching."""
        new_value = int(health)
        if self._cache["health"] != new_value:
            self._cache["health"] = new_value
            self.hud.set_button_text(0, str(new_value))

    def _update_keys(self, keys: int):
        """Update key count with caching."""
        if self._cache["keys"] != keys:
            self._cache["keys"] = keys
            self.hud.set_button_text(2, str(keys))

    def _update_enemy_status(self, status: EnemyStatus, time_left: float):
        """Update enemy status display with caching."""
        status_title = status.value[0]
        status_color = status.value[1]

        if self._cache["status_subtitle"] != status_title:
            self._cache["status_subtitle"] = status_title
            self.hud.set_button_subtitle(3, self._cache["status_subtitle"])

        if self._cache["status_color"] != status_color:
            self._cache["status_color"] = status_color
            self.hud.set_button_color(3, 1, self._cache["status_color"])

        display_time = round(time_left, 2)
        if self._cache["status_time"] != display_time:
            self._cache["status_time"] = display_time
            self.hud.set_button_text(3, f"{display_time:.2f}")

    def _update_collectibles(self, collected: int, total: int):
        """Update collectible count with caching."""
        collectibles_text = f"{collected} of {total}"
        if self._cache["collectibles"] != collectibles_text:
            self._cache["collectibles"] = collectibles_text
            self.hud.set_button_text(1, self._cache["collectibles"])

    def get_minimap_surface(self) -> HudButton:
        """Get the minimap surface for rendering."""
        return self._minimap_surface

    def draw(self, screen: pygame.Surface) -> None:
        """Draw the HUD to the screen."""
        self.hud.draw(screen)
