"""Lazy loading support for dependency injection."""

from typing import TypeVar, Generic, Callable, Optional


T = TypeVar("T")


class Lazy(Generic[T]):
    """
    Lazy wrapper for delayed dependency resolution.
    
    Usage:
        @service()
        class MyService:
            def __init__(self, heavy_service: Lazy[HeavyService]):
                self._heavy_service_factory = heavy_service
            
            def do_work(self):
                # Only resolve when needed
                heavy = self._heavy_service_factory()
                heavy.process()
    """
    
    def __init__(self, factory: Callable[[], T]):
        self._factory = factory
        self._instance: Optional[T] = None
        self._initialized = False
    
    def __call__(self) -> T:
        """Get the lazy-loaded instance."""
        if not self._initialized:
            self._instance = self._factory()
            self._initialized = True
        return self._instance
    
    @property
    def value(self) -> T:
        """Get the lazy-loaded instance via property."""
        return self()
