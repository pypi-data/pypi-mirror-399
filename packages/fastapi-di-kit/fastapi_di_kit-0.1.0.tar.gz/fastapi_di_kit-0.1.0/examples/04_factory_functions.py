"""
Factory Functions Example

This example demonstrates how to use factory functions to create
services with complex initialization logic or external dependencies.

Use cases:
- Database connections with configuration
- External API clients
- Services that need runtime configuration
"""

import os
from typing import Optional
from fastapi_di_kit import factory, service, get_container, Lifecycle


# Configuration class
class DatabaseConfig:
    """Database configuration."""
    
    def __init__(self, host: str, port: int, database: str):
        self.host = host
        self.port = port
        self.database = database
        self.connection_string = f"{host}:{port}/{database}"


# Database connection class
class DatabaseConnection:
    """Database connection that needs configuration."""
    
    def __init__(self, config: DatabaseConfig):
        self.config = config
        self.connected = False
        print(f"✓ DatabaseConnection created for {config.connection_string}")
    
    def connect(self):
        """Simulate connecting to database."""
        self.connected = True
        print(f"✓ Connected to {self.config.connection_string}")
    
    def query(self, sql: str) -> str:
        if not self.connected:
            return "Error: Not connected"
        return f"Result from {self.config.database}: {sql}"


# Example 1: Basic factory function
@factory(service_type=DatabaseConfig, lifecycle=Lifecycle.SINGLETON)
def create_database_config() -> DatabaseConfig:
    """
    Factory function that creates configuration from environment variables.
    This allows runtime configuration without hardcoding values.
    """
    print("⚙️  Creating DatabaseConfig from environment...")
    
    # In real app, use os.getenv() with defaults
    host = os.getenv("DB_HOST", "localhost")
    port = int(os.getenv("DB_PORT", "5432"))
    database = os.getenv("DB_NAME", "myapp")
    
    return DatabaseConfig(host, port, database)


# Example 2: Factory with dependencies
@factory(service_type=DatabaseConnection, lifecycle=Lifecycle.SINGLETON)
def create_database_connection(config: DatabaseConfig) -> DatabaseConnection:
    """
    Factory function that depends on other services.
    The DI container automatically resolves and injects the config.
    """
    print("⚙️  Creating DatabaseConnection with config...")
    
    connection = DatabaseConnection(config)
    connection.connect()  # Initialize the connection
    
    return connection


# External API client
class WeatherAPIClient:
    """Client for external weather API."""
    
    def __init__(self, api_key: str, base_url: str):
        self.api_key = api_key
        self.base_url = base_url
        print(f"✓ WeatherAPIClient created for {base_url}")
    
    def get_weather(self, city: str) -> str:
        return f"Weather in {city}: Sunny (API key: {self.api_key[:8]}...)"


# Example 3: Factory for external services
@factory(service_type=WeatherAPIClient, lifecycle=Lifecycle.SINGLETON)
def create_weather_client() -> WeatherAPIClient:
    """
    Factory for external API clients.
    Useful when you need API keys or complex initialization.
    """
    print("⚙️  Creating WeatherAPIClient...")
    
    # In real app, load from secure config/secrets
    api_key = os.getenv("WEATHER_API_KEY", "demo-api-key-12345")
    base_url = "https://api.weather.example.com"
    
    return WeatherAPIClient(api_key, base_url)


# Service that uses factory-created dependencies
@service()
class WeatherService:
    """Business logic service using factory-created dependencies."""
    
    def __init__(self, db: DatabaseConnection, weather_api: WeatherAPIClient):
        self.db = db
        self.weather_api = weather_api
        print("✓ WeatherService initialized with factory-created dependencies")
    
    def get_and_store_weather(self, city: str) -> dict:
        """Get weather and store in database."""
        weather = self.weather_api.get_weather(city)
        db_result = self.db.query(f"INSERT INTO weather_cache VALUES ('{city}', '{weather}')")
        
        return {
            "city": city,
            "weather": weather,
            "stored": db_result
        }


# Example 4: Conditional factory based on environment
class CacheService:
    """Cache service interface."""
    
    def get(self, key: str) -> Optional[str]:
        raise NotImplementedError
    
    def set(self, key: str, value: str):
        raise NotImplementedError


class RedisCacheService(CacheService):
    """Production Redis cache."""
    
    def __init__(self):
        print("✓ RedisCacheService initialized (production)")
    
    def get(self, key: str) -> Optional[str]:
        return f"redis_value_{key}"
    
    def set(self, key: str, value: str):
        pass


class InMemoryCacheService(CacheService):
    """Development in-memory cache."""
    
    def __init__(self):
        self.cache = {}
        print("✓ InMemoryCacheService initialized (development)")
    
    def get(self, key: str) -> Optional[str]:
        return self.cache.get(key)
    
    def set(self, key: str, value: str):
        self.cache[key] = value


@factory(service_type=CacheService, lifecycle=Lifecycle.SINGLETON)
def create_cache_service() -> CacheService:
    """
    Conditional factory - returns different implementations based on environment.
    Perfect for dev/prod switching!
    """
    environment = os.getenv("APP_ENV", "development")
    
    print(f"⚙️  Creating cache service for {environment} environment...")
    
    if environment == "production":
        return RedisCacheService()
    else:
        return InMemoryCacheService()


def main():
    print("=" * 60)
    print("Factory Functions Example - fastapi-di-kit")
    print("=" * 60)
    print()
    
    container = get_container()
    
    print("Example 1: Basic factory with configuration")
    print("-" * 60)
    config = container.resolve(DatabaseConfig)
    print(f"Config: {config.connection_string}")
    print()
    
    print("Example 2: Factory with dependencies")
    print("-" * 60)
    db_connection = container.resolve(DatabaseConnection)
    result = db_connection.query("SELECT * FROM users")
    print(f"Query result: {result}")
    print()
    
    print("Example 3: External API client factory")
    print("-" * 60)
    weather_client = container.resolve(WeatherAPIClient)
    weather = weather_client.get_weather("San Francisco")
    print(f"Weather: {weather}")
    print()
    
    print("Example 4: Using factory-created services together")
    print("-" * 60)
    weather_service = container.resolve(WeatherService)
    result = weather_service.get_and_store_weather("New York")
    print(f"Result: {result}")
    print()
    
    print("Example 5: Conditional factory (environment-based)")
    print("-" * 60)
    cache = container.resolve(CacheService)
    cache.set("test_key", "test_value")
    value = cache.get("test_key")
    print(f"Cache type: {type(cache).__name__}")
    print(f"Cached value: {value}")
    print()
    
    print("=" * 60)
    print("Key Benefits of Factory Functions:")
    print("=" * 60)
    print("✓ Complex initialization logic")
    print("✓ Runtime configuration (env vars, secrets)")
    print("✓ Conditional service creation")
    print("✓ External dependencies setup")
    print("✓ Proper resource initialization")
    print("=" * 60)
    print()


if __name__ == "__main__":
    main()
