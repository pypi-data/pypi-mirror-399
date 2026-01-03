"""Main application entry point."""

from fastapi import FastAPI
import uvicorn

# Import infrastructure adapters to trigger registration
from infrastructure.repositories import InMemoryUserRepository
from infrastructure.external_services import ConsoleEmailService
# Import domain services to trigger registration
from domain.services import UserService

from api.routes import router
from fastapi_di_kit import setup_di_middleware


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    app = FastAPI(
        title="Hexagonal Architecture Example",
        description="Demonstrating fastapi-di-kit with hexagonal architecture",
        version="0.1.0"
    )
    
    # Setup DI middleware for request-scoped services
    setup_di_middleware(app)
    
    # Register routes
    app.include_router(router)
    
    return app


app = create_app()


if __name__ == "__main__":
    print("\n🚀 Starting Hexagonal Architecture Example")
    print("📝 Try these endpoints:")
    print("   POST http://localhost:8000/users")
    print("   GET  http://localhost:8000/users/{id}")
    print("   GET  http://localhost:8000/users\n")
    
    uvicorn.run(app, host="0.0.0.0", port=8000)
