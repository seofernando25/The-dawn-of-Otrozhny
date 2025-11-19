import copy
from collections.abc import Sequence
from typing import Callable, TypeVar, cast, override

import pygame

from core import assets
from core.audio import AudioManager
from core.context import GameContext, build_game_context
from core.game_state import GameState
from config import renderer_config
from entities.player import Player
from level.loader import LevelObject, load_level_object, list_maps
from level.level import Level
from renderer.text import message_display_L
from scenes.loop_runner import SceneHandler, run_scene_with_hud
from ui import MapSelectionScreen

from .game_loop import run_game_loop


def pre_load_assets() -> None:
    """Pre-load all sprite assets for the game to avoid load times."""
    pack_names: list[str] = list(assets.list_asset_packs())
    for pack_name in pack_names:
        _ = assets.get_sprite(pack_name, 0)

    default_pack = assets.ASSETS_DIR / "Sprites"
    if default_pack.exists():
        _ = assets.get_sprite("", 0)


def _build_map_grid(
    hud: MapSelectionScreen,
    map_list: list[tuple[str, str]],
) -> list[list[LevelObject | None]]:
    """Populate HUD buttons with map previews and cached level objects."""
    actual_map_list: list[list[LevelObject | None]] = [
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


def _create_game_context_from_map(
    map_obj: LevelObject,
    audio_manager: AudioManager,
) -> GameContext | None:
    """Create a GameContext from a map object."""
    working_map = copy.deepcopy(map_obj)

    player = next((x for x in working_map.grid_entities if isinstance(x, Player)), None)
    if player is None:
        return None

    context = build_game_context(
        player=player, level=None, audio_manager_service=audio_manager
    )
    _ = Level.load(working_map, context=context)
    return context


_OverrideFunc = TypeVar("_OverrideFunc", bound=Callable[..., object])

try:
    from typing import override
except ImportError:  # pragma: no cover

    def override(func: _OverrideFunc, /) -> _OverrideFunc:
        return func


class MapSelectionScene(SceneHandler):
    """Scene handler for the map selection screen."""

    def __init__(
        self,
        hud: MapSelectionScreen,
        actual_map_list: list[list[LevelObject | None]],
        audio_manager: AudioManager,
    ):
        self.hud: MapSelectionScreen = hud
        self.actual_map_list: list[list[LevelObject | None]] = actual_map_list
        self.audio_manager: AudioManager = audio_manager
        self.result: GameState | None = None

    @override
    def handle_events(
        self,
        events: list[pygame.event.Event],
        keys_pressed: Sequence[bool],
    ) -> bool:
        _ = keys_pressed
        for event in events:
            if event.type == pygame.QUIT:
                self.result = GameState.Quit
                return True
            if event.type == pygame.KEYDOWN:
                key = cast(int, event.key)
                if key == pygame.K_RETURN:
                    map_obj = self.actual_map_list[self.hud.selected_button_x][
                        self.hud.selected_button_y
                    ]
                    if map_obj is not None:
                        context = _create_game_context_from_map(
                            map_obj, self.audio_manager
                        )
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
                if key == pygame.K_q:
                    self.result = GameState.Menu
                    return True
        return False

    @override
    def update(self, delta_time: float) -> None:
        """No additional per-frame update logic required."""
        pass

    @override
    def draw(self, screen: pygame.Surface) -> None:
        """Draw helper text over the HUD-controlled map grid."""
        message_display_L(
            screen,
            'Press "q" to go back',
            renderer_config.VIEWPORT_X_OFFSET,
            renderer_config.VIEWPORT_Y_OFFSET,
            renderer_config.HUD_CELL_TITLE_FONT_SIZE,
        )


def setup_game(audio_manager: AudioManager) -> GameState:
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
