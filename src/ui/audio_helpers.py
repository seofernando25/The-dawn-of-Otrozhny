import pygame
from core import assets
from core.audio import AudioManager


def get_ui_activation_sound(
    audio_manager: AudioManager | None,
) -> pygame.mixer.Sound | None:
    """Return the UI button activation sound or None if audio_manager is None."""
    if audio_manager is None:
        return None

    audio_manager.set_ui_sound("Active_UI", "music")
    return assets.get_cached_audio("music", "Active_UI")
