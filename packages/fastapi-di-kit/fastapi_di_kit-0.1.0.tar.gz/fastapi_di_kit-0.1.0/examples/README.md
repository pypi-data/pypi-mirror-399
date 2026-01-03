# Examples

This directory contains practical examples demonstrating all features of fastapi-di-kit.

## Running Examples

Each example is a standalone Python script that can be run directly:

```bash
# From the repository root
uv run python examples/01_basic_usage.py
```

Or using standard Python:

```bash
cd examples
python 01_basic_usage.py
```

## Example List

### 01. Basic Usage
**File:** [`01_basic_usage.py`](01_basic_usage.py)

**Demonstrates:**
- Service registration with `@service` decorator
- Automatic dependency injection
- Manual resolution from container
- Singleton lifecycle (default)

**Key Concepts:**
- How to define services
- How dependencies are automatically resolved based on type hints
- How to use the DI container

---

### 02. Lifecycle Management
**File:** [`02_lifecycle_management.py`](02_lifecycle_management.py)

**Demonstrates:**
- SINGLETON lifecycle (one instance globally)
- TRANSIENT lifecycle (new instance every time)
- SCOPED lifecycle (one instance per request)
- Using `setup_di_middleware` for request-scoped services

**Key Concepts:**
- Different lifecycle modes and when to use each
- How scoped services work with FastAPI middleware
- Performance implications of different lifecycles

**Requires:** FastAPI server (runs on http://localhost:8000)

---

### 03. Lazy Loading
**File:** [`03_lazy_loading.py`](03_lazy_loading.py)

**Demonstrates:**
- Using `Lazy[T]` to defer expensive initialization
- Performance benefits of lazy loading
- Lazy caching behavior
- When to use lazy loading

**Key Concepts:**
- Deferring dependency resolution until needed
- Breaking circular dependencies
- Improving startup performance

---

### 04. Factory Functions
**File:** [`04_factory_functions.py`](04_factory_functions.py)

**Demonstrates:**
- `@factory` decorator for complex initialization
- Factory functions with dependencies
- Runtime configuration (environment variables)
- Conditional service creation (dev/prod switching)

**Key Concepts:**
- When to use factories vs constructors
- Creating services with external dependencies
- Environment-based configuration

---

### 05. Testing and Mocking
**File:** [`05_testing_and_mocking.py`](05_testing_and_mocking.py)

**Demonstrates:**
- Creating mock implementations
- Isolated test containers
- Overriding services for testing
- pytest integration patterns

**Key Concepts:**
- How to test services with DI
- Creating and using mocks
- Avoiding global state in tests

---

### 06. Async Services
**File:** [`06_async_services.py`](06_async_services.py)

**Demonstrates:**
- Async service definitions
- Async methods in services
- Using async services in FastAPI
- Parallel async operations
- Async with different lifecycles

**Key Concepts:**
- How DI works with async/await
- Async database and API clients
- Request-scoped async services

**Requires:** FastAPI server (runs on http://localhost:8000)

---

### Hexagonal Architecture App
**Directory:** [`hexagonal_app/`](hexagonal_app/)

**Demonstrates:**
- Complete hexagonal architecture implementation
- Port/adapter pattern
- Domain-driven design with DI
- Repository pattern with interface binding

**Key Concepts:**
- Separating domain from infrastructure
- Using `@repository` decorator
- Interface-to-implementation binding
- Clean architecture with fastapi-di-kit

**To Run:**
```bash
cd examples/hexagonal_app
uv run python main.py
```

**Requires:** FastAPI server (runs on http://localhost:8000)

---

## Tips

1. **Start Simple:** Begin with `01_basic_usage.py` to understand fundamentals
2. **Learn Lifecycles:** `02_lifecycle_management.py` is crucial for production apps
3. **Optimize:** Use `03_lazy_loading.py` patterns for expensive dependencies
4. **Configure:** Apply `04_factory_functions.py` patterns for runtime configuration
5. **Test:** Follow `05_testing_and_mocking.py` patterns for testable code
6. **Async:** Use `06_async_services.py` patterns for I/O-bound operations

## Dependencies

Most examples require:
- `fastapi`
- `uvicorn` (for web examples)

Install with:
```bash
uv add fastapi uvicorn
```

Or:
```bash
pip install fastapi uvicorn
```

## Questions?

See the main [README](../README.md) for API reference and additional documentation.
