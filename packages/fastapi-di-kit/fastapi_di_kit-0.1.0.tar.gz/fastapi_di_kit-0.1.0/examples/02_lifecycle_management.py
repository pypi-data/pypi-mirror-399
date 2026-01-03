"""
Lifecycle Management Example

This example demonstrates the three lifecycle modes in fastapi-di-kit:
- SINGLETON: One instance shared globally
- TRANSIENT: New instance every time
- SCOPED: One instance per request/scope
"""

from fastapi import FastAPI, Depends
from fastapi_di_kit import service, Inject, setup_di_middleware, Lifecycle


# SINGLETON: One instance for the entire application
@service(lifecycle=Lifecycle.SINGLETON)
class ConfigService:
    """Configuration service - shared across all requests."""
    
    def __init__(self):
        self.config = {
            "app_name": "MyApp",
            "version": "1.0.0"
        }
        self.instance_id = id(self)
        print(f"✓ ConfigService created (instance {self.instance_id})")


# TRANSIENT: New instance every time it's requested
@service(lifecycle=Lifecycle.TRANSIENT)
class RequestLogger:
    """Logger that creates a new instance for each injection."""
    
    def __init__(self):
        self.instance_id = id(self)
        self.logs = []
        print(f"✓ RequestLogger created (instance {self.instance_id})")
    
    def log(self, message: str):
        self.logs.append(message)


# SCOPED: One instance per HTTP request
@service(lifecycle=Lifecycle.SCOPED)
class RequestContext:
    """Request context - unique per HTTP request."""
    
    def __init__(self):
        self.instance_id = id(self)
        self.metadata = {}
        print(f"✓ RequestContext created (instance {self.instance_id})")
    
    def set(self, key: str, value: str):
        self.metadata[key] = value
    
    def get(self, key: str) -> str:
        return self.metadata.get(key, "")


# Service that uses all three lifecycle types
@service()
class ProcessingService:
    """Service that demonstrates interaction with different lifecycles."""
    
    def __init__(
        self,
        config: ConfigService,
        logger: RequestLogger,
        context: RequestContext
    ):
        self.config = config
        self.logger = logger
        self.context = context


# Create FastAPI app
app = FastAPI()
setup_di_middleware(app)  # Required for SCOPED services


@app.get("/demo")
def demo_endpoint(
    config: ConfigService = Depends(Inject[ConfigService]),
    logger: RequestLogger = Depends(Inject[RequestLogger]),
    context: RequestContext = Depends(Inject[RequestContext])
):
    """
    Endpoint demonstrating different lifecycles.
    
    - config: Same instance across all requests (SINGLETON)
    - logger: New instance for each dependency injection (TRANSIENT)
    - context: Same instance within this request, different across requests (SCOPED)
    """
    context.set("user_id", "123")
    logger.log("Processing request")
    
    return {
        "app_name": config.config["app_name"],
        "config_instance_id": config.instance_id,
        "logger_instance_id": logger.instance_id,
        "context_instance_id": context.instance_id,
        "context_user_id": context.get("user_id")
    }


@app.get("/demo2")
def demo_endpoint_2(
    config: ConfigService = Depends(Inject[ConfigService]),
    logger1: RequestLogger = Depends(Inject[RequestLogger]),
    logger2: RequestLogger = Depends(Inject[RequestLogger]),
    context: RequestContext = Depends(Inject[RequestContext])
):
    """
    Another endpoint showing:
    - ConfigService: Same instance as /demo (SINGLETON)
    - logger1 and logger2: Different instances (TRANSIENT)
    - context: Different from /demo but same within this request (SCOPED)
    """
    context.set("endpoint", "demo2")
    
    return {
        "config_instance_id": config.instance_id,
        "logger1_instance_id": logger1.instance_id,
        "logger2_instance_id": logger2.instance_id,
        "loggers_are_different": logger1.instance_id != logger2.instance_id,
        "context_instance_id": context.instance_id,
        "context_endpoint": context.get("endpoint")
    }


def main():
    print("=" * 60)
    print("Lifecycle Management Example - fastapi-di-kit")
    print("=" * 60)
    print()
    print("This example demonstrates three lifecycle modes:")
    print("  • SINGLETON: One instance globally")
    print("  • TRANSIENT: New instance every time")
    print("  • SCOPED: One instance per request")
    print()
    print("Starting FastAPI server...")
    print("Try these commands in another terminal:")
    print()
    print("  curl http://localhost:8000/demo")
    print("  curl http://localhost:8000/demo2")
    print()
    print("Observe the instance IDs to see lifecycle behavior!")
    print("=" * 60)
    print()
    
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)


if __name__ == "__main__":
    main()
