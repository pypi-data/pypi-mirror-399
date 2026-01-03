"""Unit tests for the DI container."""

import pytest
from fastapi_di_kit import DIContainer, Lifecycle


class SimpleService:
    """Simple service for testing."""
    pass


class ServiceWithDependency:
    """Service that depends on another service."""
    def __init__(self, simple: SimpleService):
        self.simple = simple


class CircularA:
    """Service A that depends on B (circular dependency test)."""
    def __init__(self, b: 'CircularB'):
        self.b = b


class CircularB:
    """Service B that depends on A (circular dependency test)."""
    def __init__(self, a: CircularA):
        self.a = a


def test_singleton_lifecycle():
    """Test that singleton services return the same instance."""
    container = DIContainer()
    container.register(SimpleService, lifecycle=Lifecycle.SINGLETON)
    
    instance1 = container.resolve(SimpleService)
    instance2 = container.resolve(SimpleService)
    
    assert instance1 is instance2


def test_transient_lifecycle():
    """Test that transient services return different instances."""
    container = DIContainer()
    container.register(SimpleService, lifecycle=Lifecycle.TRANSIENT)
    
    instance1 = container.resolve(SimpleService)
    instance2 = container.resolve(SimpleService)
    
    assert instance1 is not instance2


def test_scoped_lifecycle():
    """Test that scoped services return same instance within a scope."""
    container = DIContainer()
    container.register(SimpleService, lifecycle=Lifecycle.SCOPED)
    
    with container.request_scope():
        instance1 = container.resolve(SimpleService)
        instance2 = container.resolve(SimpleService)
        assert instance1 is instance2
    
    # New scope should have different instance
    with container.request_scope():
        instance3 = container.resolve(SimpleService)
        assert instance1 is not instance3


def test_dependency_injection():
    """Test that dependencies are automatically injected."""
    container = DIContainer()
    container.register(SimpleService)
    container.register(ServiceWithDependency)
    
    service = container.resolve(ServiceWithDependency)
    
    assert isinstance(service, ServiceWithDependency)
    assert isinstance(service.simple, SimpleService)


def test_interface_binding():
    """Test interface-to-implementation binding."""
    from typing import Protocol
    
    class IService(Protocol):
        def do_work(self) -> str: ...
    
    class ConcreteService:
        def do_work(self) -> str:
            return "work done"
    
    container = DIContainer()
    container.register(ConcreteService, interface=IService)
    
    service = container.resolve(IService)
    
    assert isinstance(service, ConcreteService)
    assert service.do_work() == "work done"


def test_circular_dependency_detection():
    """Test that circular dependencies are detected and raise error."""
    container = DIContainer()
    container.register(CircularA)
    container.register(CircularB)
    
    with pytest.raises(ValueError, match="Circular dependency detected"):
        container.resolve(CircularA)


def test_unregistered_service_error():
    """Test that resolving unregistered service raises error."""
    container = DIContainer()
    
    with pytest.raises(ValueError, match="is not registered"):
        container.resolve(SimpleService)


def test_factory_function():
    """Test factory function registration."""
    container = DIContainer()
    
    call_count = 0
    
    def factory() -> SimpleService:
        nonlocal call_count
        call_count += 1
        return SimpleService()
    
    container.register(SimpleService, factory=factory, lifecycle=Lifecycle.TRANSIENT)
    
    container.resolve(SimpleService)
    container.resolve(SimpleService)
    
    assert call_count == 2  # Factory called twice for transient
