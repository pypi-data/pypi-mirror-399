"""Decorators for automatic service registration."""

from typing import Any, Callable, Optional, Type, TypeVar

from .container import get_container
from .types import Lifecycle


T = TypeVar("T")


def service(
    lifecycle: Lifecycle = Lifecycle.SINGLETON,
    interface: Optional[Type] = None,
) -> Callable[[Type[T]], Type[T]]:
    """
    Decorator to register a class as a service.
    
    Args:
        lifecycle: Lifecycle management strategy (default: SINGLETON)
        interface: Optional interface this service implements
        
    Usage:
        @service()
        class MyService:
            pass
            
        @service(lifecycle=Lifecycle.TRANSIENT)
        class AnotherService:
            pass
    """
    def decorator(cls: Type[T]) -> Type[T]:
        container = get_container()
        container.register(cls, lifecycle=lifecycle, interface=interface)
        return cls
    return decorator


def repository(
    interface: Type,
    lifecycle: Lifecycle = Lifecycle.SINGLETON,
) -> Callable[[Type[T]], Type[T]]:
    """
    Decorator to register a repository implementation.
    
    This is a specialized version of @service that requires an interface.
    Useful for hexagonal architecture's port/adapter pattern.
    
    Args:
        interface: The interface (port) this repository implements
        lifecycle: Lifecycle management strategy (default: SINGLETON)
        
    Usage:
        class IUserRepository(Protocol):
            def get_user(self, id: int) -> User: ...
        
        @repository(interface=IUserRepository)
        class InMemoryUserRepository:
            def get_user(self, id: int) -> User:
                ...
    """
    def decorator(cls: Type[T]) -> Type[T]:
        container = get_container()
        container.register(cls, lifecycle=lifecycle, interface=interface)
        return cls
    return decorator


def factory(
    service_type: Type[T],
    lifecycle: Lifecycle = Lifecycle.TRANSIENT,
) -> Callable[[Callable[..., T]], Callable[..., T]]:
    """
    Decorator to register a factory function.
    
    Args:
        service_type: The type that this factory produces
        lifecycle: Lifecycle management strategy (default: TRANSIENT)
        
    Usage:
        @factory(service_type=DatabaseConnection)
        def create_db_connection() -> DatabaseConnection:
            return DatabaseConnection(url="...")
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        container = get_container()
        container.register(service_type, factory=func, lifecycle=lifecycle)
        return func
    return decorator


def inject(func: Callable) -> Callable:
    """
    Decorator to mark a function for dependency injection.
    
    Note: This is optional - the container uses type hints by default.
    This decorator is mainly for clarity and future extensibility.
    
    Usage:
        @inject
        def my_function(service: MyService):
            pass
    """
    # For now, this is a no-op marker
    # Future versions could add additional metadata
    return func
