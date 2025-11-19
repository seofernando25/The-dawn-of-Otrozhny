"""
Bootstrap module for backend initialization.

This module provides centralized initialization and configuration of the backend system.
"""

from typing import TYPE_CHECKING

from core.backend import get_backend, set_backend
from core.backend.pygame_backend import PygameBackend

if TYPE_CHECKING:
    from core.backend.api import Backend


def initialize_backend(backend_type: str = "pygame") -> "Backend":
    """
    Initialize and return the specified backend.
    
    Args:
        backend_type: Type of backend to initialize ("pygame" is currently the only option)
        
    Returns:
        Initialized backend instance
    """
    if backend_type == "pygame":
        backend = PygameBackend()
        set_backend(backend)
        backend.init()
        return backend
    else:
        raise ValueError(f"Unknown backend type: {backend_type}")


def get_or_initialize_backend() -> "Backend":
    """
    Get the current backend or initialize it if it doesn't exist.
    
    Returns:
        Backend instance
    """
    return get_backend()


def shutdown_backend():
    """
    Clean up and shut down the current backend.
    """
    backend = get_backend()
    backend.quit()