"""Core dependency injection container implementation."""

import inspect
import threading
from contextlib import contextmanager
from typing import Any, Callable, Dict, Optional, Type, TypeVar, get_type_hints, Set
from contextvars import ContextVar

from .types import Lifecycle


T = TypeVar("T")

# Context variable for request-scoped services
_request_context: ContextVar[Dict[Type, Any]] = ContextVar("_request_context", default={})


class DIContainer:
    """
    Dependency injection container for managing service lifecycles and dependencies.
    
    Supports three lifecycle modes:
    - SINGLETON: One instance shared globally
    - TRANSIENT: New instance on every resolution
    - SCOPED: One instance per request scope
    """
    
    def __init__(self):
        self._services: Dict[Type, tuple[Callable, Lifecycle]] = {}
        self._singletons: Dict[Type, Any] = {}
        self._interface_bindings: Dict[Type, Type] = {}
        self._lock = threading.Lock()
    
    def register(
        self,
        service_type: Type[T],
        factory: Optional[Callable[..., T]] = None,
        lifecycle: Lifecycle = Lifecycle.SINGLETON,
        interface: Optional[Type] = None,
    ) -> None:
        """
        Register a service with the container.
        
        Args:
            service_type: The type to register
            factory: Optional factory function/class for creating instances
            lifecycle: Lifecycle management strategy
            interface: Optional interface this service implements
        """
        if factory is None:
            factory = service_type
        
        self._services[service_type] = (factory, lifecycle)
        
        # Register interface binding if provided
        if interface is not None:
            self._interface_bindings[interface] = service_type
    
    def resolve(self, service_type: Type[T]) -> T:
        """
        Resolve a service instance from the container.
        
        Args:
            service_type: The type to resolve
            
        Returns:
            An instance of the requested type
            
        Raises:
            ValueError: If the service is not registered
        """
        return self._resolve_with_stack(service_type, set())
    
    def _get_singleton(self, service_type: Type[T], factory: Callable) -> T:
        """Get or create a singleton instance."""
        if service_type not in self._singletons:
            with self._lock:
                # Double-check locking pattern
                if service_type not in self._singletons:
                    self._singletons[service_type] = self._create_instance(factory)
        return self._singletons[service_type]
    
    def _get_scoped(self, service_type: Type[T], factory: Callable) -> T:
        """Get or create a request-scoped instance."""
        scope = _request_context.get()
        
        if service_type not in scope:
            scope[service_type] = self._create_instance(factory)
            _request_context.set(scope)
        
        return scope[service_type]
    
    def _create_instance(self, factory: Callable, resolution_stack: Optional[set] = None) -> Any:
        """
        Create an instance using the factory, resolving dependencies.
        
        Supports circular dependency detection and resolution.
        
        Args:
            factory: Factory function or class to instantiate
            resolution_stack: Set tracking current resolution chain for circular detection
            
        Returns:
            New instance with dependencies injected
            
        Raises:
            ValueError: If circular dependency is detected
        """
        # Initialize resolution stack for circular dependency detection
        if resolution_stack is None:
            resolution_stack = set()
        
        # Get factory identifier
        factory_id = id(factory)
        
        # Check for circular dependency
        if factory_id in resolution_stack:
            raise ValueError(
                f"Circular dependency detected while resolving {getattr(factory, '__name__', factory)}"
            )
        
        # Add to resolution stack
        resolution_stack.add(factory_id)
        
        try:
            # Get the signature of the factory
            # If it's a class, get the __init__ signature
            if inspect.isclass(factory):
                sig = inspect.signature(factory.__init__)
                init_func = factory.__init__
            else:
                sig = inspect.signature(factory)
                init_func = factory
            
            # Try to get type hints, fall back to annotations if it fails
            try:
                type_hints = get_type_hints(init_func)
            except (NameError, AttributeError):
                # Fall back to __annotations__ for functions with forward references
                type_hints = getattr(init_func, '__annotations__', {})
            
            # Resolve dependencies for each parameter
            kwargs = {}
            for param_name, param in sig.parameters.items():
                if param_name in type_hints:
                    param_type = type_hints[param_name]
                    
                    # Handle string annotations (forward references)
                    if isinstance(param_type, str):
                        # Try to resolve the forward reference
                        for svc_type in self._services.keys():
                            if svc_type.__name__ == param_type:
                                param_type = svc_type
                                break
                    
                    # Check if it's a Lazy wrapper
                    if hasattr(param_type, '__origin__'):
                        origin = param_type.__origin__
                        # Handle Lazy[Type] syntax
                        if hasattr(origin, '__name__') and origin.__name__ == 'Lazy':
                            args = param_type.__args__
                            if args:
                                actual_type = args[0]
                                # Provide a lazy resolver
                                kwargs[param_name] = lambda t=actual_type: self.resolve(t)
                                continue
                    
                    # Skip basic types and optional parameters with defaults
                    if param_type in self._services or param_type in self._interface_bindings:
                        # Recursively resolve with updated stack
                        kwargs[param_name] = self._resolve_with_stack(param_type, resolution_stack.copy())
            
            return factory(**kwargs)
        finally:
            # Remove from resolution stack
            resolution_stack.discard(factory_id)
    
    def _resolve_with_stack(self, service_type: Type[T], resolution_stack: set) -> T:
        """
        Resolve a service with circular dependency tracking.
        
        Args:
            service_type: The type to resolve
            resolution_stack: Current resolution chain
            
        Returns:
            Resolved service instance
        """
        # Check if this is an interface with a binding
        if service_type in self._interface_bindings:
            service_type = self._interface_bindings[service_type]
        
        if service_type not in self._services:
            raise ValueError(f"Service {service_type.__name__} is not registered")
        
        factory, lifecycle = self._services[service_type]
        
        if lifecycle == Lifecycle.SINGLETON:
            # For singletons, check cache first
            if service_type in self._singletons:
                return self._singletons[service_type]
            # Create with circular detection
            instance = self._create_instance(factory, resolution_stack)
            self._singletons[service_type] = instance
            return instance
        elif lifecycle == Lifecycle.SCOPED:
            scope = _request_context.get()
            if service_type not in scope:
                instance = self._create_instance(factory, resolution_stack)
                scope[service_type] = instance
                _request_context.set(scope)
            return scope[service_type]
        else:  # TRANSIENT
            return self._create_instance(factory, resolution_stack)
    
    @contextmanager
    def request_scope(self):
        """
        Context manager for request-scoped services.
        
        Usage:
            with container.request_scope():
                service = container.resolve(MyService)
        """
        # Create a new scope
        token = _request_context.set({})
        try:
            yield
        finally:
            # Clean up the scope
            _request_context.reset(token)


# Global container instance
_container = DIContainer()


def get_container() -> DIContainer:
    """Get the global DI container instance."""
    return _container
