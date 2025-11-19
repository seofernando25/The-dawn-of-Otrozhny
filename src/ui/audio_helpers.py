from core import assets
from core.audio import AudioManager
from core.backend import get_backend
from core.backend.api import Sound


def get_ui_activation_sound(
    audio_manager: AudioManager | None,
) -> "Sound | None":
    """Return the UI button activation sound or None if audio_manager is None."""
    if audio_manager is None:
        return None

    # Get the file path and load it using the backend abstraction
    filenames = assets.list_asset_files("music", "Active_UI")
    if not filenames:
        return None

    backend = get_backend()
    return backend.audio.load_sound(filenames[0])
