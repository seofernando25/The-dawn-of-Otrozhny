"""
Setup game module - handles level selection and asset preloading.
"""

import pygame

import assets
import gameIO
import levelData
import rendering as renderer
import textDraw
import ui
from gameState import GameState
from loops.loop_runner import SceneHandler, run_scene_with_hud

from .game_loop import run_game_loop


def pre_load_assets():
    """Pre-load all sprite assets for the game to avoid load times."""
    for pack in assets.list_asset_packs():
        assets.get_sprite(pack, 0)

    default_pack = assets.ASSETS_DIR / "Sprites"
    if default_pack.exists():
        assets.get_sprite("", 0)


def _build_map_grid(hud, map_list):
    """Populate HUD buttons with map previews and cached level objects."""
    actual_map_list = [
        [None for _ in range(len(hud.hud_buttons[0]))]
        for _ in range(len(hud.hud_buttons))
    ]

    available_maps = list(map_list)

    for px, button_list in enumerate(hud.hud_buttons):
        for py, button in enumerate(button_list):
            if not available_maps:
                break
            map_path, _ = available_maps.pop()
            map_obj = gameIO.load_level_object(map_path)
            actual_map_list[px][py] = map_obj
            renderer.draw_map_preview(button, map_obj, cache_key=map_path)
            button.redraw()

    return actual_map_list


class MapSelectionScene(SceneHandler):
    """Scene handler for the map selection screen."""

    def __init__(self, hud, actual_map_list):
        self.hud = hud
        self.actual_map_list = actual_map_list
        self.result = None

    def handle_events(self, events, keys_pressed):
        for event in events:
            if event.type == pygame.QUIT:
                self.result = GameState.Quit
                return True
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    map_obj = self.actual_map_list[self.hud.selected_button_x][
                        self.hud.selected_button_y
                    ]
                    if map_obj is not None:
                        levelData.Level.load(map_obj)
                        self.result = run_game_loop()
                    else:
                        self.result = GameState.Menu
                    return True
                if event.key == pygame.K_q:
                    self.result = GameState.Menu
                    return True
        return False

    def update(self, delta_time):
        """No additional per-frame update logic required."""
        pass

    def draw(self, screen):
        """Draw helper text over the HUD-controlled map grid."""
        textDraw.message_display_L(
            screen,
            'Press "q" to go back',
            renderer.VIEWPORT_X_OFFSET,
            renderer.VIEWPORT_Y_OFFSET,
            renderer.HUD_CELL_TITLE_FONT_SIZE,
        )


def setup_game():
    """
    Set up the game by preloading assets and showing level selection.

    Returns:
        GameState: The result of the setup process (Menu or Quit).
    """
    pre_load_assets()

    map_list = gameIO.list_maps()
    hud = ui.MapSelectionScreen()
    actual_map_list = _build_map_grid(hud, map_list)

    scene = MapSelectionScene(hud, actual_map_list)
    run_result = run_scene_with_hud(scene, hud)

    if isinstance(run_result, GameState):
        return run_result
    if scene.result is not None:
        return scene.result
    return GameState.Menu
