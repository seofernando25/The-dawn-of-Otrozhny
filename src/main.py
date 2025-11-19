from pathlib import Path
import sys

from core import assets
from core.audio import AudioManager
from core.backend import get_backend
from level_editor import editor as levelEditor
from core.game_state import GameState
from scenes import about_loop, menu_loop, setup_game, tutorial_loop
from core.bootstrap import initialize_backend, get_or_initialize_backend, shutdown_backend

BASE_DIR = Path(__file__).resolve().parent.parent


def pre_close():
    """Clean up resources before exiting."""
    shutdown_backend()


def pre_init(audio: AudioManager):
    """Pre-load audio assets and UI sounds."""
    # Set up UI sound for buttons (used throughout the application)
    _ = audio.set_ui_sound("Active_UI", "music")
    # Pre-load music tracks to avoid loading delays during gameplay
    _ = assets.get_cached_audio("music", "Menu")
    _ = assets.get_cached_audio("music", "Game")


def main_loop():
    """Main orchestration loop that wires all menu/game/editor scenes."""
    # Create AudioManager instance (no singleton pattern)
    audio = AudioManager()

    backend = initialize_backend("pygame")
    # Initialize display mode before loading textures (required for convert/convert_alpha)
    from config import renderer_config
    backend.graphics.set_display_mode(renderer_config.SCREEN_SIZE)
    backend.input.set_allowed_events(["QUIT", "KEYDOWN", "KEYUP"])
    backend.graphics.set_caption("The dawn of Otrozhny")
    logo_path = BASE_DIR / "assets/icon.png"
    logo = backend.graphics.load_texture(str(logo_path))
    backend.graphics.set_icon(logo)

    pre_init(audio)

    clock = backend.clock
    done = False
    current_music = None

    def ensure_music(track_name: str):
        nonlocal current_music
        if current_music is not None and current_music == track_name:
            return
        audio.stop_music()
        _ = audio.play_music(track_name, "music")
        current_music = track_name

    ensure_music("Menu")

    while not done:
        state = menu_loop.run_menu_loop()
        if state != GameState.Menu:
            audio.stop_music()

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
            _ = about_loop.run_about_loop()
            ensure_music("Menu")
            continue

        if state == GameState.Edit:
            while state == GameState.Edit:
                # We need to pass the actual pygame clock for editorLoop as it's expecting pygame specific object
                # Let's handle this differently - first let's just pass None for now and handle the editor later
                state = levelEditor.editorLoop(clock, audio)  # This might need special handling
            ensure_music("Menu")
            if state == GameState.Quit:
                done = True
            continue

        if state == GameState.Tutorial:
            _ = tutorial_loop.run_tutorial_loop()
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
        backend = get_backend()
        backend.quit()
        profiler.disable()
        stream = io.StringIO()
        stats = pstats.Stats(profiler, stream=stream).sort_stats("cumtime")
        _ = stats.print_stats()
        with open("profile_stats.log", "w", encoding="utf-8") as out_file:
            _ = out_file.write(stream.getvalue())
    else:
        main_loop()
