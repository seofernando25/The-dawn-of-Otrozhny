from collections.abc import Sequence
from typing import cast

import pygame
import pygame.constants as pyConst

from config import renderer_config
from core.context import GameContext
from core.game_state import GameState
from entities.player import Player
from physics import movement


class InputSystem:
    """Handles all input processing and returns game state changes."""

    def __init__(self, context: GameContext):
        self.context: GameContext = context

    def process_input(
        self,
        events: list[pygame.event.Event],
        keys_pressed: Sequence[bool],
        delta_time: float,
    ) -> GameState | None:
        """Process all input and return a GameState if input requests a state change."""
        # Process game-level input first
        game_state = self._process_game_input(events, keys_pressed)
        if game_state is not None:
            return game_state

        # Process player input if player exists
        if self.context.player is not None:
            self._process_player_input(events, keys_pressed, delta_time)

        return None

    def _process_game_input(
        self,
        events: list[pygame.event.Event],
        keys_pressed: Sequence[bool],
    ) -> GameState | None:
        """Process game-level input like quit and menu."""
        # Check for quit to menu
        if keys_pressed[pygame.K_q]:
            return GameState.Menu

        # Check for window close
        for event in events:
            if event.type == pygame.QUIT:
                return GameState.Quit

        return None

    def _process_player_input(
        self,
        events: list[pygame.event.Event],
        keys_pressed: Sequence[bool],
        delta_time: float,
    ) -> None:
        """Process all player input including movement, rotation, and mouse look."""
        player_obj = cast(Player | None, self.context.player)
        if player_obj is None:
            return
        player = player_obj

        # Handle ESC key for mouse toggle
        for event in events:
            if event.type == pyConst.KEYDOWN:
                key = cast(int, event.key)
                if key == pyConst.K_ESCAPE:
                    self._toggle_mouse_look(player)

        # Update mouse visibility and grab state
        _ = pygame.mouse.set_visible(not player.mouseEnable)
        _ = pygame.event.set_grab(player.mouseEnable)

        # Get screen size for mouse calculations
        screen_surface = self.context.screen
        if screen_surface is not None:
            screen_size = screen_surface.get_size()
        else:
            screen_size = renderer_config.SCREEN_SIZE

        screen_width, screen_height = screen_size
        screen_center_x = screen_width // 2
        screen_center_y = screen_height // 2

        # Handle mouse look if enabled
        if player.mouseEnable:
            mouse_pos = pygame.mouse.get_pos()
            mouse_delta_x = mouse_pos[0] - screen_center_x
            mouse_delta_y = mouse_pos[1] - screen_center_y

            # Reset mouse to center
            pygame.mouse.set_pos([screen_center_x, screen_center_y])

            # Apply mouse look rotation
            movement.apply_mouse_look(
                player,
                delta_time,
                mouse_delta_x,
                mouse_delta_y,
                screen_center_x,
                screen_center_y,
            )
        else:
            # Handle keyboard rotation when mouse look is disabled
            movement.apply_keyboard_rotation(
                player,
                delta_time,
                rotate_left=keys_pressed[pygame.K_LEFT],
                rotate_right=keys_pressed[pygame.K_RIGHT],
                pitch_up=keys_pressed[pygame.K_UP],
                pitch_down=keys_pressed[pygame.K_DOWN],
            )

        # Calculate movement vector from keyboard input
        newPx, newPy = movement.calculate_movement_vector(
            player,
            delta_time,
            move_forward=keys_pressed[pygame.K_w],
            move_backward=keys_pressed[pygame.K_s],
            move_left=keys_pressed[pygame.K_a],
            move_right=keys_pressed[pygame.K_d],
        )

        # Apply movement to player
        player.move(newPx, newPy, delta_time)

    def _toggle_mouse_look(self, player: Player) -> None:
        """Toggle mouse look mode and reset mouse to center."""
        player.mouseEnable = not player.mouseEnable

        # Reset mouse to center when toggling
        screen_surface = self.context.screen
        if screen_surface is not None:
            screen_size = screen_surface.get_size()
        else:
            screen_size = renderer_config.SCREEN_SIZE

        screen_width, screen_height = screen_size
        pygame.mouse.set_pos([screen_width // 2, screen_height // 2])
