"""Tests for lazy loading functionality."""

import pytest
from fastapi_di_kit import service, Lazy, get_container, Lifecycle, DIContainer


class HeavyService:
    """Heavy service that is expensive to initialize."""
    
    def __init__(self):
        self.initialized = True
        self.call_count = 0
    
    def process(self) -> str:
        self.call_count += 1
        return "processed"


class LightService:
    """Light service that uses lazy loading for heavy dependency."""
    
    def __init__(self, heavy: Lazy[HeavyService]):
        self.heavy_factory = heavy
        self.initialized = True
    
    def do_work_without_heavy(self) -> str:
        return "light work"
    
    def do_work_with_heavy(self) -> str:
        heavy = self.heavy_factory()
        return heavy.process()


class ChainedService:
    """Service with multiple lazy dependencies."""
    
    def __init__(self, lazy1: Lazy[HeavyService], lazy2: Lazy[LightService]):
        self.lazy1 = lazy1
        self.lazy2 = lazy2


def test_lazy_basic_usage():
    """Test basic lazy loading functionality."""
    call_count = 0
    
    def factory():
        nonlocal call_count
        call_count += 1
        return HeavyService()
    
    lazy = Lazy(factory)
    
    # Not called yet
    assert call_count == 0
    
    # Call once
    instance1 = lazy()
    assert call_count == 1
    assert isinstance(instance1, HeavyService)
    
    # Cached, not called again
    instance2 = lazy()
    assert call_count == 1
    assert instance1 is instance2


def test_lazy_value_property():
    """Test lazy loading via .value property."""
    call_count = 0
    
    def factory():
        nonlocal call_count
        call_count += 1
        return HeavyService()
    
    lazy = Lazy(factory)
    
    assert call_count == 0
    
    instance1 = lazy.value
    assert call_count == 1
    
    instance2 = lazy.value
    assert call_count == 1
    assert instance1 is instance2


def test_lazy_with_container():
    """Test lazy loading integrated with DI container."""
    container = DIContainer()
    
    container.register(HeavyService)
    
    # Create lazy wrapper manually
    lazy = Lazy(lambda: container.resolve(HeavyService))
    
    instance = lazy()
    
    assert isinstance(instance, HeavyService)
    assert instance.initialized


def test_lazy_in_service_dependency():
    """Test lazy loading as a service dependency."""
    container = DIContainer()
    
    # Track if HeavyService was created
    heavy_created = []
    
    def heavy_factory():
        service = HeavyService()
        heavy_created.append(service)
        return service
    
    container.register(HeavyService, factory=heavy_factory)
    
    # Register LightService with Lazy dependency
    # Note: We need to manually handle Lazy in dependencies
    def light_factory():
        lazy_heavy = Lazy(lambda: container.resolve(HeavyService))
        return LightService(lazy_heavy)
    
    container.register(LightService, factory=light_factory)
    
    # Resolve LightService - HeavyService should NOT be created yet
    light = container.resolve(LightService)
    assert len(heavy_created) == 0
    
    # Do work without heavy
    result = light.do_work_without_heavy()
    assert result == "light work"
    assert len(heavy_created) == 0  # Still not created
    
    # Now use heavy service
    result = light.do_work_with_heavy()
    assert result == "processed"
    assert len(heavy_created) == 1  # Now created


def test_lazy_with_singleton():
    """Test lazy loading with singleton lifecycle."""
    container = DIContainer()
    
    container.register(HeavyService, lifecycle=Lifecycle.SINGLETON)
    
    lazy1 = Lazy(lambda: container.resolve(HeavyService))
    lazy2 = Lazy(lambda: container.resolve(HeavyService))
    
    instance1 = lazy1()
    instance2 = lazy2()
    
    # Both should resolve to same singleton
    assert instance1 is instance2


def test_lazy_with_transient():
    """Test lazy loading with transient lifecycle."""
    container = DIContainer()
    
    container.register(HeavyService, lifecycle=Lifecycle.TRANSIENT)
    
    lazy1 = Lazy(lambda: container.resolve(HeavyService))
    lazy2 = Lazy(lambda: container.resolve(HeavyService))
    
    instance1 = lazy1()
    instance2 = lazy2()
    
    # Different instances from transient
    assert instance1 is not instance2


def test_lazy_caching():
    """Test that lazy caches the instance after first call."""
    container = DIContainer()
    
    container.register(HeavyService, lifecycle=Lifecycle.TRANSIENT)
    
    lazy = Lazy(lambda: container.resolve(HeavyService))
    
    instance1 = lazy()
    instance1.custom_attr = "test"
    
    instance2 = lazy()
    
    # Same instance from cache, even though service is transient
    assert instance1 is instance2
    assert hasattr(instance2, 'custom_attr')
    assert instance2.custom_attr == "test"


def test_lazy_multiple_in_chain():
    """Test multiple lazy dependencies in a chain."""
    container = DIContainer()
    
    container.register(HeavyService)
    
    def light_factory():
        lazy_heavy = Lazy(lambda: container.resolve(HeavyService))
        return LightService(lazy_heavy)
    
    container.register(LightService, factory=light_factory)
    
    def chained_factory():
        lazy1 = Lazy(lambda: container.resolve(HeavyService))
        lazy2 = Lazy(lambda: container.resolve(LightService))
        return ChainedService(lazy1, lazy2)
    
    container.register(ChainedService, factory=chained_factory)
    
    chained = container.resolve(ChainedService)
    
    # Services not created yet
    assert chained.lazy1 is not None
    assert chained.lazy2 is not None
    
    # Resolve first lazy
    service1 = chained.lazy1()
    assert isinstance(service1, HeavyService)
    
    # Resolve second lazy
    service2 = chained.lazy2()
    assert isinstance(service2, LightService)


def test_lazy_callable_and_property():
    """Test both callable and property access work the same."""
    call_count = 0
    
    def factory():
        nonlocal call_count
        call_count += 1
        return HeavyService()
    
    lazy = Lazy(factory)
    
    # Access via callable
    instance1 = lazy()
    assert call_count == 1
    
    # Access via property should return same cached instance
    instance2 = lazy.value
    assert call_count == 1
    assert instance1 is instance2
    
    # Mix and match
    instance3 = lazy()
    instance4 = lazy.value
    assert call_count == 1
    assert instance1 is instance3 is instance4


def test_lazy_performance_benefit():
    """Test that lazy loading provides performance benefit."""
    expensive_calls = []
    
    def expensive_factory():
        # Simulate expensive initialization
        expensive_calls.append(1)
        return HeavyService()
    
    lazy = Lazy(expensive_factory)
    
    # Create 10 instances that have the lazy dependency
    services = []
    for i in range(10):
        services.append(LightService(lazy))
    
    # Expensive service not created yet
    assert len(expensive_calls) == 0
    
    # Only when we actually use it
    services[0].do_work_with_heavy()
    assert len(expensive_calls) == 1
    
    # And it's cached for all uses
    services[1].do_work_with_heavy()
    services[2].do_work_with_heavy()
    assert len(expensive_calls) == 1


def test_lazy_with_exceptions():
    """Test lazy loading behavior with exceptions in factory."""
    call_count = 0
    
    def failing_factory():
        nonlocal call_count
        call_count += 1
        raise ValueError("Factory failed")
    
    lazy = Lazy(failing_factory)
    
    # First call raises exception (not caught by Lazy)
    try:
        lazy()
        # If we get here, check what was returned
        # The current Lazy implementation doesn't handle exceptions specially
    except ValueError:
        # Expected - exception propagated
        pass
    
    assert call_count == 1
