from pathlib import Path
import sys

import pygame

from core import assets
from core.audio import AudioManager
from level_editor import editor as levelEditor
from core.game_state import GameState
from loops import about_loop, menu_loop, setup_game, tutorial_loop

BASE_DIR = Path(__file__).resolve().parent


def pre_close():
    """Clean up resources before exiting."""
    pygame.quit()


def pre_init(audio: AudioManager):
    """Pre-load audio assets and UI sounds."""
    # Set up UI sound for buttons (used throughout the application)
    audio.set_ui_sound("Active_UI", "music")
    # Pre-load music tracks to avoid loading delays during gameplay
    assets.get_cached_audio("music", "Menu")
    assets.get_cached_audio("music", "Game")


def main_loop():
    """Main orchestration loop that wires all menu/game/editor scenes."""
    # Create AudioManager instance (no singleton pattern)
    audio = AudioManager()
    
    pygame.init()
    pygame.event.set_allowed([pygame.QUIT, pygame.KEYDOWN, pygame.KEYUP])
    pygame.display.set_caption("The dawn of Otrozhny")
    logo_path = BASE_DIR / "assets/icon.png"
    logo = pygame.image.load(str(logo_path))
    pygame.display.set_icon(logo)

    pre_init(audio)

    clock = pygame.time.Clock()
    done = False
    current_music = None

    def ensure_music(track_name: str):
        nonlocal current_music
        if current_music == track_name:
            return
        audio.play_music(track_name, "music")
        current_music = track_name

    ensure_music("Menu")

    while not done:
        state = menu_loop.run_menu_loop()

        if state == GameState.Quit:
            done = True
            continue

        if state == GameState.Play:
            ensure_music("Game")
            state = setup_game.setup_game(audio)
            if state == GameState.Quit:
                done = True
            else:
                ensure_music("Menu")
            continue

        if state == GameState.About:
            about_loop.run_about_loop()
            ensure_music("Menu")
            continue

        if state == GameState.Edit:
            while state == GameState.Edit:
                state = levelEditor.editorLoop(clock, audio)
            ensure_music("Menu")
            if state == GameState.Quit:
                done = True
            continue

        if state == GameState.Tutorial:
            tutorial_loop.run_tutorial_loop()
            ensure_music("Menu")
            continue

    pre_close()


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[-1] == "PLOG":
        import cProfile
        import io
        import pstats

        print("Profiling...")
        profiler = cProfile.Profile()
        profiler.enable()
        main_loop()
        pygame.quit()
        profiler.disable()
        stream = io.StringIO()
        stats = pstats.Stats(profiler, stream=stream).sort_stats("cumtime")
        stats.print_stats()
        with open("profile_stats.log", "w", encoding="utf-8") as out_file:
            out_file.write(stream.getvalue())
    else:
        main_loop()
