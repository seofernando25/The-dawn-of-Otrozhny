import logging
from collections.abc import Sequence
from core import assets
from core.backend import get_backend
from core.backend.api import Channel, Sound

LOGGER = logging.getLogger(__name__)


# ============================================================================
# Low-level audio backend operations
# ============================================================================


class _MixerState:
    """Encapsulates audio backend initialization state."""

    def __init__(self):
        self._initialized = False

    def ensure_initialized(self) -> bool:
        """Ensure audio backend is initialized."""
        if self._initialized:
            backend = get_backend()
            if backend.audio.get_init():
                return True
        try:
            backend = get_backend()
            if not backend.audio.get_init():
                backend.audio.pre_init(44100, -16, 2, 512)
                backend.audio.init()
            self._initialized = True
        except Exception as exc:
            LOGGER.warning("Unable to initialize audio: %s", exc)
            self._initialized = False
        return self._initialized

    def ensure_channel(
        self, channel: "Channel | None" = None
    ) -> "Channel | None":
        """Get or create an audio channel."""
        if not self.ensure_initialized():
            return None
        if channel is not None:
            return channel
        backend = get_backend()
        return backend.audio.find_channel(force=True)


# Global mixer state instance (encapsulated, not a bare global)
_MIXER_STATE = _MixerState()


def ensure_initialized() -> bool:
    """Ensure audio backend is initialized."""
    return _MIXER_STATE.ensure_initialized()


def ensure_channel(
    channel: "Channel | None" = None,
) -> "Channel | None":
    """Get or create an audio channel."""
    return _MIXER_STATE.ensure_channel(channel)


VolumeInput = None | float | int | Sequence[float]


def _normalize_volume(volume: VolumeInput) -> tuple[float, float] | None:
    """Normalize volume to a tuple of (left, right) channels."""
    if volume is None:
        return None
    if isinstance(volume, Sequence):
        values = [float(v) for v in volume]
        if not values:
            return None
        if len(values) == 1:
            return (values[0], values[0])
        return (values[0], values[1])
    scalar = float(volume)
    return (scalar, scalar)


def play_sound_low_level(
    sound: "Sound | None",
    *,
    channel: "Channel | None" = None,
    loops: int = 0,
    maxtime: int = 0,
    fade_ms: int = 0,
    volume: None | float | Sequence[float] = None,
    force: bool = False,
) -> "Channel | None":
    """Low-level function to play a Sound object using the backend abstraction."""
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
        self._channels: dict[str, "Channel"] = {}
        self._active_ui_sound: "Sound | None" = None
        self._mixer_state: _MixerState = _MixerState()
        self._music_channel: "Channel | None" = None
        result = self._mixer_state.ensure_initialized()
        _ = result  # Suppress unused call result

    def play_sound(
        self,
        sound_id: str,
        pack: str = "assets",
        volume: tuple[float, float] | None = None,
        force: bool = False,
    ) -> "Channel | None":
        """Play a sound from the requested pack and return the audio channel if one was available."""
        try:
            sound = assets.get_audio(pack, sound_id)
            if sound is None:
                LOGGER.warning(f"Sound not found: {pack}/{sound_id}")
                return None

            channel = self._mixer_state.ensure_channel()
            if channel is None:
                return None

            # Store channel for this sound ID for potential interruption
            self._channels[sound_id] = channel

            return play_sound_low_level(
                sound, channel=channel, volume=volume, force=force
            )
        except Exception as e:
            LOGGER.error(f"Failed to play sound {pack}/{sound_id}: {e}")
            return None

    def play_music(
        self, music_id: str, pack: str = "music"
    ) -> "Channel | None":
        """Play looping background music and return the dedicated music channel if successful."""
        try:
            music = assets.get_cached_audio(pack, music_id)
            if music is None:
                LOGGER.warning(f"Music not found: {pack}/{music_id}")
                return None

            channel = self._mixer_state.ensure_channel(self._get_music_channel())
            if channel is None:
                return None

            return play_sound_low_level(music, channel=channel, force=True)
        except Exception as e:
            LOGGER.error(f"Failed to play music {pack}/{music_id}: {e}")
            return None

    def set_ui_sound(self, ui_sound_id: str, pack: str = "music"):
        """Cache the UI sound effect that will be played by play_ui_sound."""
        self._active_ui_sound = assets.get_cached_audio(pack, ui_sound_id)

    def play_ui_sound(self) -> "Channel | None":
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

    def _get_music_channel(self) -> "Channel | None":
        """Get or create the dedicated music channel."""
        channel = getattr(self, "_music_channel", None)
        if channel is None:
            channel = self._mixer_state.ensure_channel()
            if channel is not None:
                self._music_channel = channel
        return channel
