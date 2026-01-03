"""FastAPI integration for dependency injection."""

from typing import Any, Callable, Type, TypeVar
from fastapi import Depends, Request
from starlette.middleware.base import BaseHTTPMiddleware

from .container import get_container


T = TypeVar("T")


class _InjectMarker:
    """Internal marker class for dependency injection."""
    
    def __init__(self, service_type: Type[T]):
        self.service_type = service_type
    
    def __class_getitem__(cls, service_type: Type[T]) -> Callable:
        """
        Enable Inject[ServiceType] syntax.
        
        Usage:
            @app.get("/users")
            def get_users(service: Annotated[UserService, Inject[UserService]]):
                ...
                
            Or simpler with Depends:
            @app.get("/users")
            def get_users(service = Depends(Inject[UserService])):
                ...
        """
        def dependency() -> T:
            container = get_container()
            return container.resolve(service_type)
        
        return dependency


# Public API
Inject = _InjectMarker


class DIMiddleware(BaseHTTPMiddleware):
    """
    Middleware for managing request-scoped dependencies.
    
    This middleware ensures that request-scoped services are properly
    initialized and cleaned up for each request.
    """
    
    async def dispatch(self, request: Request, call_next):
        """Handle each request with a new DI scope."""
        container = get_container()
        
        with container.request_scope():
            response = await call_next(request)
        
        return response


def setup_di_middleware(app):
    """
    Set up dependency injection middleware for a FastAPI app.
    
    Usage:
        app = FastAPI()
        setup_di_middleware(app)
    """
    app.add_middleware(DIMiddleware)
