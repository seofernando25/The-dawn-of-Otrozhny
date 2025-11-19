"""
Bootstrap module for backend initialization.

This module provides centralized initialization and configuration of the backend system.
"""

from core.backend import get_backend, set_backend
from core.backend.pygame_backend import PygameBackend
from core.backend.api import Backend


def initialize_backend(backend_type: str = "pygame") -> Backend:
    """
    Initialize and return the specified backend.

    Args:
        backend_type: Type of backend to initialize ("pygame" is currently the only option)

    Returns:
        Backend
    """
    if backend_type == "pygame":
        backend = PygameBackend()
        set_backend(backend)
        backend.init()
        return backend
    else:
        raise ValueError(f"Unknown backend type: {backend_type}")


def shutdown_backend():
    """
    Clean up and shut down the current backend.
    """
    backend = get_backend()
    backend.quit()
