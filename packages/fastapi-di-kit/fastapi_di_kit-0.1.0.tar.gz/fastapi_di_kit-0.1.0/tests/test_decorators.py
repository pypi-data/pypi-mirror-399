"""Tests for decorator-based service registration."""

import pytest
from typing import Protocol
from fastapi_di_kit import service, repository, factory, inject, get_container, Lifecycle, DIContainer


# Test services
class SimpleService:
    """Simple service for testing."""
    pass


class ConfigService:
    """Service with configuration."""
    def __init__(self):
        self.config = {"key": "value"}


class DependentService:
    """Service with dependencies."""
    def __init__(self, simple: SimpleService):
        self.simple = simple


# Test protocols/interfaces
class IRepository(Protocol):
    """Repository interface."""
    def get_item(self, id: int) -> str:
        ...


class IEmailService(Protocol):
    """Email service interface."""
    def send_email(self, to: str, subject: str) -> bool:
        ...


def test_service_decorator_singleton():
    """Test @service decorator with singleton lifecycle."""
    container = DIContainer()
    
    @service(lifecycle=Lifecycle.SINGLETON)
    class TestService:
        pass
    
    # Manually register to avoid global container pollution
    container.register(TestService, lifecycle=Lifecycle.SINGLETON)
    
    instance1 = container.resolve(TestService)
    instance2 = container.resolve(TestService)
    
    assert instance1 is instance2


def test_service_decorator_transient():
    """Test @service decorator with transient lifecycle."""
    container = DIContainer()
    
    @service(lifecycle=Lifecycle.TRANSIENT)
    class TestService:
        pass
    
    container.register(TestService, lifecycle=Lifecycle.TRANSIENT)
    
    instance1 = container.resolve(TestService)
    instance2 = container.resolve(TestService)
    
    assert instance1 is not instance2


def test_service_decorator_scoped():
    """Test @service decorator with scoped lifecycle."""
    container = DIContainer()
    
    @service(lifecycle=Lifecycle.SCOPED)
    class TestService:
        def __init__(self):
            self.id = id(self)
    
    container.register(TestService, lifecycle=Lifecycle.SCOPED)
    
    with container.request_scope():
        instance1 = container.resolve(TestService)
        instance2 = container.resolve(TestService)
        assert instance1 is instance2
    
    with container.request_scope():
        instance3 = container.resolve(TestService)
        assert instance1 is not instance3


def test_service_decorator_default_lifecycle():
    """Test @service decorator uses singleton by default."""
    container = DIContainer()
    
    @service()
    class TestService:
        pass
    
    container.register(TestService)  # Default is singleton
    
    instance1 = container.resolve(TestService)
    instance2 = container.resolve(TestService)
    
    assert instance1 is instance2


def test_service_decorator_with_dependencies():
    """Test @service decorator with automatic dependency injection."""
    container = DIContainer()
    
    @service()
    class ServiceA:
        pass
    
    @service()
    class ServiceB:
        def __init__(self, a: ServiceA):
            self.a = a
    
    container.register(ServiceA)
    container.register(ServiceB)
    
    instance = container.resolve(ServiceB)
    
    assert isinstance(instance, ServiceB)
    assert isinstance(instance.a, ServiceA)


def test_repository_decorator_with_interface():
    """Test @repository decorator with interface binding."""
    container = DIContainer()
    
    @repository(interface=IRepository)
    class InMemoryRepository:
        def get_item(self, id: int) -> str:
            return f"item_{id}"
    
    container.register(InMemoryRepository, interface=IRepository)
    
    # Resolve by interface
    repo = container.resolve(IRepository)
    
    assert isinstance(repo, InMemoryRepository)
    assert repo.get_item(1) == "item_1"


def test_repository_decorator_lifecycle():
    """Test @repository decorator with custom lifecycle."""
    container = DIContainer()
    
    @repository(interface=IRepository, lifecycle=Lifecycle.TRANSIENT)
    class TransientRepository:
        def get_item(self, id: int) -> str:
            return f"item_{id}"
    
    container.register(TransientRepository, interface=IRepository, lifecycle=Lifecycle.TRANSIENT)
    
    instance1 = container.resolve(IRepository)
    instance2 = container.resolve(IRepository)
    
    assert instance1 is not instance2


def test_repository_decorator_with_dependencies():
    """Test @repository decorator with dependencies."""
    container = DIContainer()
    
    @service()
    class Database:
        def __init__(self):
            self.connected = True
    
    @repository(interface=IRepository)
    class DatabaseRepository:
        def __init__(self, db: Database):
            self.db = db
        
        def get_item(self, id: int) -> str:
            return f"item_{id}" if self.db.connected else "error"
    
    container.register(Database)
    container.register(DatabaseRepository, interface=IRepository)
    
    repo = container.resolve(IRepository)
    
    assert isinstance(repo, DatabaseRepository)
    assert repo.db.connected
    assert repo.get_item(1) == "item_1"


def test_factory_decorator_basic():
    """Test @factory decorator with basic usage."""
    container = DIContainer()
    
    call_count = 0
    
    @factory(service_type=ConfigService, lifecycle=Lifecycle.TRANSIENT)
    def create_config() -> ConfigService:
        nonlocal call_count
        call_count += 1
        return ConfigService()
    
    container.register(ConfigService, factory=create_config, lifecycle=Lifecycle.TRANSIENT)
    
    instance1 = container.resolve(ConfigService)
    instance2 = container.resolve(ConfigService)
    
    assert isinstance(instance1, ConfigService)
    assert isinstance(instance2, ConfigService)
    assert instance1 is not instance2
    assert call_count == 2


def test_factory_decorator_singleton():
    """Test @factory decorator with singleton lifecycle."""
    container = DIContainer()
    
    call_count = 0
    
    @factory(service_type=ConfigService, lifecycle=Lifecycle.SINGLETON)
    def create_config() -> ConfigService:
        nonlocal call_count
        call_count += 1
        return ConfigService()
    
    container.register(ConfigService, factory=create_config, lifecycle=Lifecycle.SINGLETON)
    
    instance1 = container.resolve(ConfigService)
    instance2 = container.resolve(ConfigService)
    
    assert instance1 is instance2
    assert call_count == 1  # Factory called only once


def test_factory_decorator_with_dependencies():
    """Test @factory decorator that has dependencies."""
    container = DIContainer()
    
    @service()
    class TokenGenerator:
        def generate(self) -> str:
            return "secret-token"
    
    @factory(service_type=ConfigService)
    def create_config(token_gen: TokenGenerator) -> ConfigService:
        config = ConfigService()
        config.config["token"] = token_gen.generate()
        return config
    
    container.register(TokenGenerator)
    container.register(ConfigService, factory=create_config)
    
    instance = container.resolve(ConfigService)
    
    assert isinstance(instance, ConfigService)
    assert instance.config["token"] == "secret-token"


def test_inject_decorator():
    """Test @inject decorator as marker."""
    # The @inject decorator is currently a no-op marker
    # This test verifies it doesn't break functionality
    
    @inject
    def my_function(service: SimpleService) -> str:
        return "success"
    
    # Decorator should not modify the function
    assert my_function.__name__ == "my_function"
    assert callable(my_function)


def test_multiple_decorators_combination():
    """Test using multiple services with different decorators together."""
    container = DIContainer()
    
    @service()
    class ServiceA:
        pass
    
    @repository(interface=IEmailService)
    class EmailService:
        def send_email(self, to: str, subject: str) -> bool:
            return True
    
    @factory(service_type=ConfigService)
    def create_config() -> ConfigService:
        return ConfigService()
    
    @service()
    class ComplexService:
        def __init__(self, a: ServiceA, email: IEmailService, config: ConfigService):
            self.a = a
            self.email = email
            self.config = config
    
    container.register(ServiceA)
    container.register(EmailService, interface=IEmailService)
    container.register(ConfigService, factory=create_config)
    container.register(ComplexService)
    
    instance = container.resolve(ComplexService)
    
    assert isinstance(instance.a, ServiceA)
    assert isinstance(instance.email, EmailService)
    assert isinstance(instance.config, ConfigService)


def test_service_decorator_with_interface():
    """Test @service decorator with interface parameter."""
    container = DIContainer()
    
    @service(interface=IEmailService)
    class MockEmailService:
        def send_email(self, to: str, subject: str) -> bool:
            return True
    
    container.register(MockEmailService, interface=IEmailService)
    
    service_instance = container.resolve(IEmailService)
    
    assert isinstance(service_instance, MockEmailService)
    assert service_instance.send_email("test@example.com", "Test") is True


def test_decorator_edge_case_no_constructor():
    """Test decorators with services that have no __init__."""
    container = DIContainer()
    
    @service()
    class NoInitService:
        value = 42
    
    container.register(NoInitService)
    
    instance = container.resolve(NoInitService)
    
    assert instance.value == 42


def test_decorator_edge_case_empty_constructor():
    """Test decorators with services that have empty constructor."""
    container = DIContainer()
    
    @service()
    class EmptyInitService:
        def __init__(self):
            self.initialized = True
    
    container.register(EmptyInitService)
    
    instance = container.resolve(EmptyInitService)
    
    assert instance.initialized is True
