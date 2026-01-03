# Contributing to fastapi-di-kit

Thank you for your interest in contributing to fastapi-di-kit! 

## Development Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/tonlls1999/fastapi-di-kit.git
   cd fastapi-di-kit
   ```

2. **Install dependencies with uv**
   ```bash
   uv sync
   ```

3. **Run tests**
   ```bash
   uv run pytest tests/ -v
   ```

## Running Examples

```bash
# Basic examples
uv run python examples/01_basic_usage.py

# FastAPI examples (starts server on localhost:8000)
uv run python examples/02_lifecycle_management.py
```

## Project Structure

```
fastapi-di-kit/
├── src/fastapi_di_kit/    # Core library code
├── tests/                  # Test suite
├── examples/               # Usage examples
├── pyproject.toml          # Project configuration
└── README.md              # Documentation
```

## Code Style

- Follow PEP 8 guidelines
- Use type hints for all function signatures
- Add docstrings to public APIs
- Keep functions focused and testable

## Pull Request Process

1. Create a new branch for your feature/fix
2. Add tests for new functionality
3. Ensure all tests pass
4. Update documentation as needed
5. Submit a pull request with a clear description

## Testing

All new features must include tests:
```bash
uv run pytest tests/ -v --cov=src/fastapi_di_kit
```

## Questions?

Feel free to open an issue for any questions or suggestions!
