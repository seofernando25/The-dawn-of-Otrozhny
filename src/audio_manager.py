"""
Audio manager - unified API for audio playback.

Abstracts pygame.mixer calls into a simple audio.play(sound_id) API.
Provides caching and centralized audio management.
"""

import logging
from typing import Optional, Tuple
import pygame
import assets
import audio

LOGGER = logging.getLogger(__name__)


class AudioManager:
    """
    Centralized audio management system.

    Provides a clean API for playing sounds throughout the game.
    """

    def __init__(self):
        self._channels = {}
        self._active_ui_sound = None
        audio.ensure_initialized()

    def play_sound(
        self,
        sound_id: str,
        pack: str = "Assets",
        volume: Optional[Tuple[float, float]] = None,
        force: bool = False,
    ) -> Optional[pygame.mixer.Channel]:
        """Play a sound from the requested pack and return the mixer channel if one was available."""
        try:
            sound = assets.get_audio(pack, sound_id)
            if sound is None:
                LOGGER.warning(f"Sound not found: {pack}/{sound_id}")
                return None

            channel = audio.ensure_channel()
            if channel is None:
                return None

            # Store channel for this sound ID for potential interruption
            self._channels[sound_id] = channel

            return audio.play_sound(sound, channel=channel, volume=volume, force=force)
        except Exception as e:
            LOGGER.error(f"Failed to play sound {pack}/{sound_id}: {e}")
            return None

    def play_music(
        self, music_id: str, pack: str = "Music"
    ) -> Optional[pygame.mixer.Channel]:
        """Play looping background music and return the dedicated music channel if successful."""
        try:
            music = assets.get_cached_audio(pack, music_id)
            if music is None:
                LOGGER.warning(f"Music not found: {pack}/{music_id}")
                return None

            channel = audio.ensure_channel(self._get_music_channel())
            if channel is None:
                return None

            return audio.play_sound(music, channel=channel, force=True)
        except Exception as e:
            LOGGER.error(f"Failed to play music {pack}/{music_id}: {e}")
            return None

    def set_ui_sound(self, ui_sound_id: str, pack: str = "Music"):
        """Cache the UI sound effect that will be played by play_ui_sound."""
        self._active_ui_sound = assets.get_cached_audio(pack, ui_sound_id)

    def play_ui_sound(self) -> Optional[pygame.mixer.Channel]:
        """Play the previously configured UI sound effect and return its channel if any."""
        if self._active_ui_sound is None:
            return None

        return audio.play_sound(self._active_ui_sound, force=True)

    def stop_sound(self, sound_id: str):
        """Stop the channel currently associated with the given sound identifier."""
        channel = self._channels.get(sound_id)
        if channel:
            channel.stop()

    def stop_music(self):
        """Stop background music."""
        channel = self._get_music_channel()
        if channel:
            channel.stop()

    def _get_music_channel(self) -> Optional[pygame.mixer.Channel]:
        """Get or create the dedicated music channel."""
        if not hasattr(self, "_music_channel"):
            self._music_channel = audio.ensure_channel()
        return self._music_channel

    # Singleton pattern
    _instance = None

    @classmethod
    def get_instance(cls) -> "AudioManager":
        """Get the singleton AudioManager instance."""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance


# Global convenience functions
def play_sound(
    sound_id: str,
    pack: str = "Assets",
    volume: Optional[Tuple[float, float]] = None,
    force: bool = False,
) -> Optional[pygame.mixer.Channel]:
    """Convenience wrapper around AudioManager.play_sound."""
    return AudioManager.get_instance().play_sound(sound_id, pack, volume, force)


def play_music(music_id: str, pack: str = "Music") -> Optional[pygame.mixer.Channel]:
    """Play music using the global audio manager."""
    return AudioManager.get_instance().play_music(music_id, pack)


def set_ui_sound(ui_sound_id: str, pack: str = "Music"):
    """Set the active UI sound."""
    AudioManager.get_instance().set_ui_sound(ui_sound_id, pack)


def play_ui_sound() -> Optional[pygame.mixer.Channel]:
    """Play the active UI sound."""
    return AudioManager.get_instance().play_ui_sound()


def stop_sound(sound_id: str):
    """Stop a specific sound."""
    AudioManager.get_instance().stop_sound(sound_id)


def stop_music():
    """Stop background music."""
    AudioManager.get_instance().stop_music()
