"""
Backend abstraction module for pygame independence.

This module provides access to the backend implementation through singletons
that can be easily swapped out for different backends.
"""

from core.backend.api import Backend, GraphicsSurface, InputBackend, AudioBackend, Clock

# Global backend instance
_backend: Backend | None = None


def get_backend() -> Backend:
    """Get the current backend instance."""
    global _backend
    if _backend is None:
        # Import here to avoid circular dependencies
        from core.backend.pygame_backend import PygameBackend

        _backend = PygameBackend()
        _backend.init()
    return _backend


def get_audio() -> AudioBackend:
    """Get the audio backend."""
    return get_backend().audio


def get_clock() -> Clock:
    """Get the clock backend."""
    return get_backend().clock


def set_backend(backend: Backend) -> None:
    """Set a custom backend instance."""
    global _backend
    _backend = backend
