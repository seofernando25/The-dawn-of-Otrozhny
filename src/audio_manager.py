"""
Unified audio management system.

Provides both low-level pygame.mixer operations and high-level game audio management.
This module consolidates the functionality previously split between audio.py and audio_manager.py.
"""

import logging
from typing import Optional, Sequence, Tuple, Union

import pygame
from core import assets

LOGGER = logging.getLogger(__name__)

# Low-level pygame mixer state
_INITIALIZED = False


# ============================================================================
# Low-level pygame mixer operations
# ============================================================================

def ensure_initialized() -> bool:
    """Ensure pygame.mixer is initialized."""
    global _INITIALIZED
    if _INITIALIZED and pygame.mixer.get_init():
        return True
    try:
        if not pygame.mixer.get_init():
            pygame.mixer.pre_init(44100, -16, 2, 512)
            pygame.mixer.init()
        _INITIALIZED = True
    except pygame.error as exc:
        LOGGER.warning("Unable to initialize audio: %s", exc)
        _INITIALIZED = False
    return _INITIALIZED


def ensure_channel(
    channel: Optional[pygame.mixer.Channel] = None,
) -> Optional[pygame.mixer.Channel]:
    """Get or create a pygame mixer channel."""
    if not ensure_initialized():
        return None
    if channel is not None:
        return channel
    return pygame.mixer.find_channel(True)


def _normalize_volume(
    volume: Union[None, float, Sequence[float]],
) -> Optional[Tuple[float, float]]:
    """Normalize volume to a tuple of (left, right) channels."""
    if volume is None:
        return None
    if isinstance(volume, Sequence):
        if len(volume) == 2:
            return (float(volume[0]), float(volume[1]))
        if len(volume) == 1:
            return (float(volume[0]), float(volume[0]))
    return (float(volume), float(volume))


def play_sound_low_level(
    sound: Optional[pygame.mixer.Sound],
    *,
    channel: Optional[pygame.mixer.Channel] = None,
    loops: int = 0,
    maxtime: int = 0,
    fade_ms: int = 0,
    volume: Union[None, float, Sequence[float]] = None,
    force: bool = False,
) -> Optional[pygame.mixer.Channel]:
    """Low-level function to play a pygame Sound object."""
    if sound is None:
        return channel
    channel = ensure_channel(channel)
    if channel is None:
        return None
    if channel.get_busy() and not force:
        return channel
    channel.play(sound, loops=loops, maxtime=maxtime, fade_ms=fade_ms)
    normalized_volume = _normalize_volume(volume)
    if normalized_volume is not None:
        channel.set_volume(*normalized_volume)
    return channel


# ============================================================================
# High-level game audio management
# ============================================================================

class AudioManager:
    """
    Centralized audio management system.

    Provides a clean API for playing sounds throughout the game.
    """

    def __init__(self):
        self._channels = {}
        self._active_ui_sound = None
        ensure_initialized()

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

            channel = ensure_channel()
            if channel is None:
                return None

            # Store channel for this sound ID for potential interruption
            self._channels[sound_id] = channel

            return play_sound_low_level(sound, channel=channel, volume=volume, force=force)
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

            channel = ensure_channel(self._get_music_channel())
            if channel is None:
                return None

            return play_sound_low_level(music, channel=channel, force=True)
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

        return play_sound_low_level(self._active_ui_sound, force=True)

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
            self._music_channel = ensure_channel()
        return self._music_channel
