import pygame

from core import assets
from core.io import load_level_object, list_maps
from core.level import Level
from config import renderer_config
from renderer.text import message_display_L
from ui import MapSelectionScreen
from core.context import build_game_context
from entities.player import Player
from core.game_state import GameState
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
            map_obj = load_level_object(map_path)
            actual_map_list[px][py] = map_obj
            from renderer.preview import draw_map_preview
            draw_map_preview(button, map_obj, cache_key=map_path)
            button.redraw()

    return actual_map_list


def _create_game_context_from_map(map_obj, audio_manager):
    """Create a GameContext from a map object."""
    player = next((x for x in map_obj.grid_entities if isinstance(x, Player)), None)
    if player is None:
        return None
    
    context = build_game_context(player=player, level=None, audio_manager_service=audio_manager)
    Level.load(map_obj, context=context)
    return context


class MapSelectionScene(SceneHandler):
    """Scene handler for the map selection screen."""

    def __init__(self, hud, actual_map_list, audio_manager):
        self.hud = hud
        self.actual_map_list = actual_map_list
        self.audio_manager = audio_manager
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
                        context = _create_game_context_from_map(map_obj, self.audio_manager)
                        if context is None:
                            self.result = GameState.Menu
                            return True
                        result = run_game_loop(context)
                        if result == GameState.Quit:
                            self.result = GameState.Quit
                            return True
                        # Any other result (e.g., GameState.Menu) means stay in selector
                        continue
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
        message_display_L(
            screen,
            'Press "q" to go back',
            renderer_config.VIEWPORT_X_OFFSET,
            renderer_config.VIEWPORT_Y_OFFSET,
            renderer_config.HUD_CELL_TITLE_FONT_SIZE,
        )


def setup_game(audio_manager):
    """Set up the game by preloading assets and showing level selection."""
    pre_load_assets()

    map_list = list_maps()
    # Get UI sound from audio manager for button activation sounds
    from ui.audio_helpers import get_ui_activation_sound
    activated_sound = get_ui_activation_sound(audio_manager)
    hud = MapSelectionScreen(activated_sound=activated_sound)
    actual_map_list = _build_map_grid(hud, map_list)

    scene = MapSelectionScene(hud, actual_map_list, audio_manager)
    run_result = run_scene_with_hud(scene, hud)

    if isinstance(run_result, GameState):
        return run_result
    if scene.result is not None:
        return scene.result
    return GameState.Menu
