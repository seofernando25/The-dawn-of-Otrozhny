"""
Game loop module - handles the main game loop with updated HUD, timing, and win/lose conditions.
"""

import datetime
import pygame

import colors
import rendering as renderer
from renderer.text import message_display_L, message_display_MT
import ui
from entities.base import EnemyStatus
from renderer import minimap as renderer_minimap
from core.game_state import GameState
from loops.loop_runner import SceneHandler, run_scene
from core.context import GameContext


class HudController:
    """Centralized HUD controller for managing and caching HUD values."""

    def __init__(self, hud_screen):
        self.hud = hud_screen
        # Cache for avoiding redundant updates
        self._cache = {
            "keys": None,
            "status_subtitle": None,
            "status_color": None,
            "status_time": None,
            "collectibles": None,
            "health": None,
        }

    def update_health(self, health):
        """Update health value with caching."""
        if self._cache["health"] != int(health):
            self._cache["health"] = int(health)
            self.hud.set_button_text(0, self._cache["health"])

    def update_keys(self, keys):
        """Update key count with caching."""
        if self._cache["keys"] != keys:
            self._cache["keys"] = keys
            self.hud.set_button_text(2, self._cache["keys"])

    def update_enemy_status(self, status, time_left):
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
            self.hud.set_button_text(3, self._cache["status_time"])

    def update_collectibles(self, collected, total):
        """Update collectible count with caching."""
        collectibles_text = f"{collected} of {total}"
        if self._cache["collectibles"] != collectibles_text:
            self._cache["collectibles"] = collectibles_text
            self.hud.set_button_text(1, self._cache["collectibles"])


def run_game_loop(context: GameContext):
    """
    Main game loop handling player movement, entity updates, rendering, and game state.

    Returns:
        GameState: The next game state (Quit or continue playing).
    """
    # Initialize HUD
    hud = ui.HudScreen(interactable=False)
    hud.set_button_title(0, "Health")
    hud.set_button_title(1, "Stars")
    hud.set_button_subtitle(1, "Found")
    hud.set_button_title(2, "Keys")
    hud.set_button_title(3, "Status")

    # Allow Loop to control hud button surface draw calls
    hud.hud_buttons[-1].protected = False

    # Setup player
    player = context.player
    if player is None:
        raise RuntimeError("GameContext.player is not set.")

    player.keys = 0
    
    # Get or ensure enemy state manager is initialized
    enemy_state = context.ensure_enemy_state()
    enemy_state.reset()

    # Timing
    time = 0
    quit_intent = False
    clock = pygame.time.Clock()

    # Initialize HUD controller
    hud_controller = HudController(hud)

    while not quit_intent:
        delta_time = clock.get_time() / 1000
        events = pygame.event.get()
        hud.update(delta_time, events)
        kb = pygame.key.get_pressed()

        if kb[pygame.K_q]:
            return GameState.Menu

        time += delta_time

        # Check win/lose conditions
        if player.health <= 0:
            enemy_state.reset()
            return post_game_loop(won=False)

        current_map = context.level
        if current_map is None:
            raise RuntimeError("GameContext.level is not set.")
        if current_map.num_of_collected == current_map.num_of_collectibles:
            return post_game_loop(won=True, time=time)

        # Update shared enemy state (once per frame, before individual enemy updates)
        enemy_state.update(delta_time)

        # Update entities
        for entity in current_map.grid_entities:
            entity.update(delta_time, events)

        # Update HUD values through controller
        hud_controller.update_keys(player.keys)
        hud_controller.update_enemy_status(
            enemy_state.status, enemy_state.status_time_left
        )
        hud_controller.update_collectibles(
            current_map.num_of_collected, current_map.num_of_collectibles
        )
        hud_controller.update_health(player.health)

        # Rendering
        screen = context.screen or renderer.get_screen()
        screen.fill(colors.BLACK)

        # 3D View Rendering
        view_port = renderer.render_first_person_canvas(
            player, canvas=context.services.get("first_person_surface")
        )
        context.services["first_person_surface"] = view_port
        screen.blit(view_port, (renderer.VIEWPORT_X_OFFSET, renderer.VIEWPORT_Y_OFFSET))

        # Minimap
        renderer_minimap.render_map(hud.hud_buttons[-1], player)

        # Draw HUD
        hud.draw(screen)

        # Debug info
        message_display_L(screen, f"FPS: {int(clock.get_fps())}", 15, 10, 15)
        message_display_MT(
            screen,
            f"X:{round(player.px, 2)} Y:{round(player.py, 2)}",
            renderer.SCREEN_WIDTH // 2,
            10,
            15,
        )

        pygame.display.flip()
        clock.tick()

    return GameState.Quit


class PostGameScene(SceneHandler):
    """Scene handler for the post-game summary screen."""

    def __init__(self, won, time_seconds):
        self.won = won
        self.elapsed_time = datetime.timedelta(seconds=time_seconds) if won else None
        self.msg = "You won" if won else "You lost"
        self.msg_accumulated = 0

    def handle_events(self, events, keys_pressed):
        for event in events:
            if event.type == pygame.QUIT:
                return True
            if event.type == pygame.KEYDOWN and event.key == pygame.K_q:
                return True
        return False

    def update(self, delta_time):
        self.msg_accumulated += delta_time * 5
        if self.msg_accumulated > len(self.msg):
            self.msg_accumulated = len(self.msg)

    def draw(self, screen):
        from renderer.text import message_display_MT, message_display_L
        message_display_MT(
            screen,
            self.msg[: int(self.msg_accumulated)],
            renderer.SCREEN_WIDTH // 2,
            100,
            30,
        )
        message_display_L(
            screen,
            'Press "q" to go back',
            renderer.VIEWPORT_X_OFFSET,
            renderer.VIEWPORT_Y_OFFSET,
            renderer.HUD_CELL_TITLE_FONT_SIZE,
        )

        if self.won and self.elapsed_time is not None:
            time_str = (
                f"{self.elapsed_time.seconds // 60}."
                f"{self.elapsed_time.seconds % 60}."
                f"{round(self.elapsed_time.microseconds / 1000)}"
            )
            message_display_MT(
                screen,
                time_str,
                renderer.SCREEN_WIDTH // 2,
                150,
                30,
            )


def post_game_loop(won, time=0):
    """Show the win/lose summary screen and return GameState.Menu to go back to menu."""
    scene = PostGameScene(won, time)
    run_scene(scene)
    return GameState.Menu
