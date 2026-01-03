"""
fastapi-di-kit: A simple, powerful dependency injection library for FastAPI.

Supports hexagonal architecture with easy service registration and lifecycle management.
"""

__version__ = "0.1.0"

from .container import DIContainer, get_container
from .decorators import service, repository, factory, inject
from .fastapi_integration import Inject, DIMiddleware, setup_di_middleware
from .types import Lifecycle
from .lazy import Lazy

__all__ = [
    # Core
    "DIContainer",
    "get_container",
    # Decorators
    "service",
    "repository",
    "factory",
    "inject",
    # FastAPI Integration
    "Inject",
    "DIMiddleware",
    "setup_di_middleware",
    # Types
    "Lifecycle",
    "Lazy",
]

