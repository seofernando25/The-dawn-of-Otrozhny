import logging
from typing import Optional, Sequence, Tuple, Union

import pygame

LOGGER = logging.getLogger(__name__)
_INITIALIZED = False


def ensure_initialized() -> bool:
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
    if not ensure_initialized():
        return None
    if channel is not None:
        return channel
    return pygame.mixer.find_channel(True)


def _normalize_volume(
    volume: Union[None, float, Sequence[float]],
) -> Optional[Tuple[float, float]]:
    if volume is None:
        return None
    if isinstance(volume, Sequence):
        if len(volume) == 2:
            return (float(volume[0]), float(volume[1]))
        if len(volume) == 1:
            return (float(volume[0]), float(volume[0]))
    return (float(volume), float(volume))


def play_sound(
    sound: Optional[pygame.mixer.Sound],
    *,
    channel: Optional[pygame.mixer.Channel] = None,
    loops: int = 0,
    maxtime: int = 0,
    fade_ms: int = 0,
    volume: Union[None, float, Sequence[float]] = None,
    force: bool = False,
) -> Optional[pygame.mixer.Channel]:
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
