"""Helper functions for UI audio setup."""
from typing import Optional
import pygame

from core import assets
from audio_manager import AudioManager


def get_ui_activation_sound(audio_manager: Optional[AudioManager]) -> Optional[pygame.mixer.Sound]:
    """
    Get the UI button activation sound, setting it up in the audio manager if needed.
    
    This helper consolidates the common pattern of setting up UI sounds for buttons.
    
    Args:
        audio_manager: The audio manager instance. If None, returns None.
        
    Returns:
        The cached UI activation sound, or None if audio_manager is None.
    """
    if audio_manager is None:
        return None
    
    audio_manager.set_ui_sound("Active_UI", "Music")
    return assets.get_cached_audio("Music", "Active_UI")

