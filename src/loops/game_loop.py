"""
Game loop module - handles the main game loop using separated systems.
"""

import datetime
import pygame

from core.game_state import GameState
from loops.loop_runner import SceneHandler, run_scene
from core.context import GameContext
from systems import InputSystem, GameplaySystem, RenderSystem, HudSystem
from config import renderer_config
from renderer.config import get_screen


def run_game_loop(context: GameContext):
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
    clock = pygame.time.Clock()
    
    while True:
        delta_time = clock.get_time() / 1000
        events = pygame.event.get()
        keys_pressed = pygame.key.get_pressed()
        
        # Process input (handles all player input and game-level input)
        input_result = input_system.process_input(events, keys_pressed, delta_time)
        if input_result is not None:
            return input_result
        
        # Update HUD (needs events for button interactions)
        hud_result = hud_system.update(delta_time, events)
        if hud_result is not None:
            return hud_result
        
        # Update gameplay
        # Note: Player input is now handled by InputSystem above
        gameplay_result = gameplay_system.update(delta_time, events)
        if gameplay_result is not None:
            game_state, time = gameplay_result
            if game_state == GameState.Play:
                # Game ended - show post-game screen
                won = time is not None
                return post_game_loop(won=won, time=time if won else 0)
        
        # Render frame
        # Screen should always be set in context, but fallback for safety
        screen = context.screen
        if screen is None:
            screen = get_screen()
            context.screen = screen
        
        # Render main game view (first-person, debug info)
        render_system.render_frame(clock)
        
        # Render minimap (handled by HUD system)
        hud_system.render_minimap(context.player)
        
        # Render HUD overlay
        hud_system.draw(screen)
        
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


def post_game_loop(won, time=0):
    """Show the win/lose summary screen and return GameState.Menu to go back to menu."""
    scene = PostGameScene(won, time)
    run_scene(scene)
    return GameState.Menu
