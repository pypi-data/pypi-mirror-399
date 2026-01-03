"""
Async Services Example

This example demonstrates how to use async services with fastapi-di-kit.
Async services are useful for I/O-bound operations like database queries,
API calls, file operations, etc.
"""

import asyncio
from fastapi import FastAPI, Depends
from fastapi_di_kit import service, Inject, setup_di_middleware, Lifecycle


# Async database service
@service()
class AsyncDatabase:
    """Async database service."""
    
    def __init__(self):
        self.connected = False
        self.connection_pool = None
        print("✓ AsyncDatabase initialized")
    
    async def connect(self):
        """Async connection initialization."""
        print("🔌 Connecting to database...")
        await asyncio.sleep(0.1)  # Simulate connection time
        self.connected = True
        self.connection_pool = {"pool": "active"}
        print("✓ Database connected")
    
    async def query(self, sql: str) -> dict:
        """Execute async query."""
        if not self.connected:
            await self.connect()
        
        await asyncio.sleep(0.05)  # Simulate query time
        return {"result": f"Data for: {sql}", "rows": 42}


# Async cache service
@service()
class AsyncRedisCache:
    """Async Redis cache service."""
    
    def __init__(self):
        self.cache = {}
        print("✓ AsyncRedisCache initialized")
    
    async def get(self, key: str) -> str | None:
        """Get value from cache."""
        await asyncio.sleep(0.01)  # Simulate network I/O
        return self.cache.get(key)
    
    async def set(self, key: str, value: str, ttl: int = 60):
        """Set value in cache."""
        await asyncio.sleep(0.01)  # Simulate network I/O
        self.cache[key] = value
        print(f"✓ Cached {key} = {value}")


# Async external API service
@service()
class AsyncWeatherAPI:
    """Async external weather API client."""
    
    async def get_weather(self, city: str) -> dict:
        """Fetch weather data asynchronously."""
        print(f"🌤️  Fetching weather for {city}...")
        await asyncio.sleep(0.2)  # Simulate API call
        
        return {
            "city": city,
            "temperature": 72,
            "condition": "Sunny",
            "humidity": 45
        }


# Business logic service using async dependencies
@service()
class WeatherService:
    """Weather service with async dependencies."""
    
    def __init__(
        self,
        db: AsyncDatabase,
        cache: AsyncRedisCache,
        weather_api: AsyncWeatherAPI
    ):
        self.db = db
        self.cache = cache
        self.weather_api = weather_api
        print("✓ WeatherService initialized with async dependencies")
    
    async def get_weather(self, city: str) -> dict:
        """
        Get weather with caching and database logging.
        Demonstrates async operations in business logic.
        """
        cache_key = f"weather:{city}"
        
        # Try cache first
        cached = await self.cache.get(cache_key)
        if cached:
            print(f"✨ Cache hit for {city}")
            return {"city": city, "data": cached, "source": "cache"}
        
        # Fetch from API
        weather_data = await self.weather_api.get_weather(city)
        
        # Cache the result
        await self.cache.set(cache_key, str(weather_data))
        
        # Log to database
        await self.db.query(f"INSERT INTO weather_log VALUES ('{city}', '{weather_data}')")
        
        return {"city": city, "data": weather_data, "source": "api"}


# Create FastAPI app
app = FastAPI()
setup_di_middleware(app)


@app.get("/weather/{city}")
async def get_weather(
    city: str,
    service: WeatherService = Depends(Inject[WeatherService])
):
    """
    Async FastAPI endpoint using async services.
    
    The DI container automatically resolves async dependencies.
    """
    result = await service.get_weather(city)
    return result


@app.get("/weather-parallel")
async def get_weather_parallel(
    service: WeatherService = Depends(Inject[WeatherService])
):
    """
    Demonstrate parallel async operations.
    
    Fetch weather for multiple cities concurrently.
    """
    cities = ["New York", "London", "Tokyo"]
    
    # Execute all requests in parallel
    tasks = [service.get_weather(city) for city in cities]
    results = await asyncio.gather(*tasks)
    
    return {"cities": results}


# Request-scoped async service
@service(lifecycle=Lifecycle.SCOPED)
class AsyncRequestContext:
    """Request-scoped async context."""
    
    def __init__(self):
        self.request_id = id(self)
        self.metadata = {}
        print(f"✓ AsyncRequestContext created (instance {self.request_id})")
    
    async def load_user_data(self, user_id: int):
        """Simulate loading user data."""
        await asyncio.sleep(0.05)
        self.metadata["user_id"] = user_id
        self.metadata["loaded"] = True


@app.get("/user/{user_id}")
async def get_user(
    user_id: int,
    ctx: AsyncRequestContext = Depends(Inject[AsyncRequestContext])
):
    """
    Endpoint demonstrating scoped async service.
    
    The context is unique per request.
    """
    await ctx.load_user_data(user_id)
    
    return {
        "request_id": ctx.request_id,
        "user_id": ctx.metadata.get("user_id"),
        "loaded": ctx.metadata.get("loaded")
    }


# Standalone async example without FastAPI
async def standalone_async_example():
    """Example of using async services without FastAPI."""
    print("=" * 60)
    print("Standalone Async Example")
    print("=" * 60)
    print()
    
    from fastapi_di_kit import get_container
    
    container = get_container()
    
    # Resolve async services
    weather_service = container.resolve(WeatherService)
    
    # Use async methods
    print("Fetching weather for San Francisco...")
    result = await weather_service.get_weather("San Francisco")
    print(f"Result: {result}")
    print()
    
    print("Fetching again (should be cached)...")
    result2 = await weather_service.get_weather("San Francisco")
    print(f"Result: {result2}")
    print()


def main():
    """Main entry point."""
    print("=" * 60)
    print("Async Services Example - fastapi-di-kit")
    print("=" * 60)
    print()
    
    # Option 1: Run FastAPI server
    print("Starting FastAPI server with async endpoints...")
    print()
    print("Try these commands in another terminal:")
    print("  curl http://localhost:8000/weather/London")
    print("  curl http://localhost:8000/weather-parallel")
    print("  curl http://localhost:8000/user/123")
    print()
    print("=" * 60)
    print()
    
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
    
    # Option 2: Run standalone example (uncomment below)
    # asyncio.run(standalone_async_example())


if __name__ == "__main__":
    main()
