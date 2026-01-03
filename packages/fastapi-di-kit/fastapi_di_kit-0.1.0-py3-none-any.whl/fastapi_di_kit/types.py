"""Type definitions and enums for fastapi-di-kit."""

from enum import Enum
from typing import Protocol, TypeVar, Type, Any


class Lifecycle(str, Enum):
    """Service lifecycle management options."""
    
    SINGLETON = "singleton"  # Single instance shared across all requests
    TRANSIENT = "transient"  # New instance created every time
    SCOPED = "scoped"  # Single instance per request scope


T = TypeVar("T")
ServiceType = TypeVar("ServiceType")


class ServiceProvider(Protocol):
    """Protocol for objects that can provide service instances."""
    
    def get_instance(self) -> Any:
        """Get an instance of the service."""
        ...
