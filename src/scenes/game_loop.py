import datetime
from collections.abc import Sequence
from typing import override

from config import renderer_config
from core.context import GameContext, get_screen
from core.game_state import GameState
from scenes.loop_runner import SceneHandler, run_scene
from systems import GameplaySystem, HudSystem, InputSystem, RenderSystem
from core.backend import get_backend

from core.backend.api import Event, GraphicsSurface


def run_game_loop(context: GameContext) -> GameState:
    """
    Main game loop using separated systems for input, gameplay, rendering, and HUD.

    The loop is organized into distinct systems:
    - InputSystem: Processes user input
    - GameplaySystem: Updates entities and checks win/lose conditions
    - HudSystem: Manages HUD updates
    - RenderSystem: Handles all rendering operations
    """
    # Initialize systems
    input_system = InputSystem(context)
    gameplay_system = GameplaySystem(context)
    hud_system = HudSystem(context)
    render_system = RenderSystem(context)

    # Initialize gameplay
    gameplay_system.initialize()

    # Timing
    backend = get_backend()
    clock = backend.clock

    while True:
        delta_time = clock.get_time() / 1000
        events = backend.input.get_events()
        keys_pressed = backend.input.get_pressed_keys()

        # Process input (handles all player input and game-level input)
        input_result = input_system.process_input(events, keys_pressed, delta_time)
        if input_result is not None:
            return input_result

        # Update HUD (needs events for button interactions)
        hud_result = hud_system.update(delta_time, events)
        if hud_result is not None:
            return GameState(hud_result)

        # Update gameplay
        # Note: Player input is now handled by InputSystem above
        gameplay_result = gameplay_system.update(delta_time, events)
        if gameplay_result is not None:
            _, time = gameplay_result
            # Game ended - show post-game screen
            won = time is not None
            elapsed_time = time if time is not None else 0.0
            return post_game_loop(won=won, time=elapsed_time)

        # Render frame
        # Screen should always be set in context, but fallback for safety
        screen = context.screen
        if screen is None:
            screen = get_screen()
            context.screen = screen

        # Render main game view (first-person, debug info)
        render_system.render_frame(clock)

        # Render minimap (handled by render system)
        minimap_surface = hud_system.get_minimap_surface()
        render_system.render_minimap(minimap_surface)

        # Render HUD overlay
        hud_system.draw(screen)

        backend.graphics.flip()
        _ = clock.tick()


class PostGameScene(SceneHandler):
    """Scene handler for the post-game summary screen."""

    def __init__(self, won: bool, time_seconds: float):
        self.won: bool = won
        self.elapsed_time: datetime.timedelta | None = (
            datetime.timedelta(seconds=time_seconds) if won else None
        )
        self.msg: str = "You won" if won else "You lost"
        self.msg_accumulated: float = 0.0

    @override
    def handle_events(
        self,
        events: list["Event"],
        keys_pressed: Sequence[bool],
    ) -> bool:
        from core.backend.api import KEYDOWN, QUIT, K_q
        for event in events:
            if hasattr(event, "type") and event.type == QUIT:
                return True
            if hasattr(event, "type") and event.type == KEYDOWN:
                if hasattr(event, "key") and event.key == K_q:
                    return True
        return False

    @override
    def update(self, delta_time: float) -> None:
        self.msg_accumulated += delta_time * 5
        if self.msg_accumulated > len(self.msg):
            self.msg_accumulated = len(self.msg)

    @override
    def draw(self, screen: "GraphicsSurface") -> None:
        from renderer.text import message_display_MT, message_display_L

        message_display_MT(
            screen,
            self.msg[: int(self.msg_accumulated)],
            renderer_config.SCREEN_WIDTH // 2,
            100,
            30,
        )
        message_display_L(
            screen,
            'Press "q" to go back',
            renderer_config.VIEWPORT_X_OFFSET,
            renderer_config.VIEWPORT_Y_OFFSET,
            renderer_config.HUD_CELL_TITLE_FONT_SIZE,
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
                renderer_config.SCREEN_WIDTH // 2,
                150,
                30,
            )


def post_game_loop(won: bool, time: float = 0.0) -> GameState:
    """Show the win/lose summary screen and return GameState.Menu to go back to menu."""
    scene = PostGameScene(won, time)
    _ = run_scene(scene)
    return GameState.Menu
