"""Integration tests with FastAPI."""

import pytest
from fastapi import FastAPI, Depends
from fastapi.testclient import TestClient
from fastapi_di_kit import service, Inject, setup_di_middleware, Lifecycle, get_container


@service(lifecycle=Lifecycle.SINGLETON)
class Counter:
    """Simple counter service for testing."""
    def __init__(self):
        self.count = 0
    
    def increment(self):
        self.count += 1
        return self.count


@service(lifecycle=Lifecycle.SCOPED)
class RequestContext:
    """Request-scoped context for testing."""
    def __init__(self):
        self.request_id = id(self)


def test_inject_dependency():
    """Test that Inject[] works in FastAPI routes."""
    app = FastAPI()
    setup_di_middleware(app)
    
    @app.get("/count")
    def get_count(counter: Counter = Depends(Inject[Counter])):
        return {"count": counter.increment()}
    
    client = TestClient(app)
    
    # First request
    response1 = client.get("/count")
    assert response1.json() == {"count": 1}
    
    # Second request (singleton should maintain state)
    response2 = client.get("/count")
    assert response2.json() == {"count": 2}


def test_scoped_isolation():
    """Test  that scoped services are isolated per request."""
    app = FastAPI()
    setup_di_middleware(app)
    
    @app.get("/context")
    def get_context(ctx: RequestContext = Depends(Inject[RequestContext])):
        return {"request_id": ctx.request_id}
    
    client = TestClient(app)
    
    # Two requests should have different contexts
    response1 = client.get("/context")
    response2 = client.get("/context")
    
    assert response1.json()["request_id"] != response2.json()["request_id"]


def test_multiple_injections():
    """Test multiple dependencies injected in one route."""
    app = FastAPI()
    setup_di_middleware(app)
    
    @app.get("/multi")
    def multi_inject(
        counter: Counter = Depends(Inject[Counter]),
        ctx: RequestContext = Depends(Inject[RequestContext])
    ):
        return {
            "count": counter.increment(),
            "request_id": ctx.request_id
        }
    
    client = TestClient(app)
    
    response = client.get("/multi")
    data = response.json()
    
    assert "count" in data
    assert "request_id" in data


def test_without_middleware():
    """Test that DI works even without middleware for non-scoped services."""
    app = FastAPI()
    # Not setting up middleware
    
    @app.get("/count")
    def get_count(counter: Counter = Depends(Inject[Counter])):
        return {"count": counter.increment()}
    
    client = TestClient(app)
    
    response = client.get("/count")
    assert response.status_code == 200

