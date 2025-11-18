"""
Game loop module - handles the main game loop with updated HUD, timing, and win/lose conditions.
"""
import datetime
import pygame

import colors
import levelData
import rendering as renderer
import textDraw
import ui
from entities.enemies import Enemy, EnemyStatus
from entities.player import Player
from renderer import minimap as renderer_minimap
from gameState import GameState


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


def run_game_loop():
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
    try:
        player = Player.require_instance()
    except RuntimeError:
        return GameState.Quit

    player.keys = 0
    Enemy.enemy_status = EnemyStatus.Normal
    Enemy.enemy_status_time_left = 0

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
            return GameState.Quit

        time += delta_time

        # Check win/lose conditions
        if player.health <= 0:
            Enemy.enemy_status = EnemyStatus.Normal
            Enemy.enemy_status_time_left = 0
            return post_game_loop(won=False)

        current_map = levelData.require_current_map()
        if current_map.num_of_collected == current_map.num_of_collectibles:
            return post_game_loop(won=True, time=time)

        # Update entities
        for entity in current_map.grid_entities:
            entity.update(delta_time, events)

        # Update HUD values through controller
        hud_controller.update_keys(player.keys)
        hud_controller.update_enemy_status(Enemy.enemy_status, Enemy.enemy_status_time_left)
        hud_controller.update_collectibles(current_map.num_of_collected, current_map.num_of_collectibles)
        hud_controller.update_health(player.health)

        # Rendering
        screen = renderer.get_screen()
        screen.fill(colors.BLACK)

        # 3D View Rendering
        view_port = renderer.render_first_person_canvas(player)
        screen.blit(view_port, (renderer.VIEWPORT_X_OFFSET, renderer.VIEWPORT_Y_OFFSET))

        # Minimap
        renderer_minimap.render_map(hud.hud_buttons[-1], player)

        # Draw HUD
        hud.draw()

        # Debug info
        textDraw.message_display_L(screen, f"FPS: {int(clock.get_fps())}", 15, 10, 15)
        textDraw.message_display_MT(
            screen,
            f"X:{round(player.px, 2)} Y:{round(player.py, 2)}",
            renderer.SCREEN_WIDTH // 2, 10, 15
        )

        pygame.display.flip()
        clock.tick()

    return GameState.Quit


def post_game_loop(won, time=0):
    """Show the win/lose summary screen and always return GameState.Quit."""
    done = False

    if won:
        elapsed_time = datetime.timedelta(seconds=time)
        msg = "You won"
    else:
        msg = "You lost"
        elapsed_time = None

    msg_accumulated = 0
    clock = pygame.time.Clock()

    while not done:
        delta_time = clock.get_time() / 1000
        events = pygame.event.get()

        for event in events:
            if event.type == pygame.QUIT:
                return GameState.Quit
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    return GameState.Quit

        msg_accumulated += delta_time * 5
        if msg_accumulated > len(msg):
            msg_accumulated = len(msg)

        # Rendering
        screen = renderer.get_screen()
        screen.fill(colors.BLACK)

        textDraw.message_display_MT(screen, msg[:int(msg_accumulated)], renderer.SCREEN_WIDTH // 2, 100, 30)
        textDraw.message_display_L(screen, "Press \"q\" to go back",
                                   renderer.VIEWPORT_X_OFFSET, renderer.VIEWPORT_Y_OFFSET,
                                   renderer.HUD_CELL_TITLE_FONT_SIZE)

        if won and elapsed_time is not None:
            time_str = f"{elapsed_time.seconds // 60}.{elapsed_time.seconds % 60}.{round(elapsed_time.microseconds / 1000)}"
            textDraw.message_display_MT(screen, time_str, renderer.SCREEN_WIDTH // 2, 150, 30)

        pygame.display.update()
        clock.tick()

    return GameState.Quit
