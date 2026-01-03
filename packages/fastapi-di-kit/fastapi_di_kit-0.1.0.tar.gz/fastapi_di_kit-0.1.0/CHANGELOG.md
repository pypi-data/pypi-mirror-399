# Changelog

All notable changes to fastapi-di-kit will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.0] - 2025-12-31

### Added
- Initial release of fastapi-di-kit
- Core dependency injection container with lifecycle management
- Support for SINGLETON, TRANSIENT, and SCOPED lifecycles
- Decorator-based service registration (`@service`, `@repository`, `@factory`)
- FastAPI integration with `Inject[T]` and middleware
- Lazy loading support with `Lazy[T]`
- Circular dependency detection
- Interface-to-implementation binding for hexagonal architecture
- Async service support
- Comprehensive test suite (49 tests)
- Full documentation with 6 practical examples
- Hexagonal architecture example application

### Documentation
- Complete README with feature overview and API reference
- 6 numbered examples demonstrating all features
- Example-specific README with running instructions
- Inline code documentation and docstrings

[Unreleased]: https://github.com/tonlls1999/fastapi-di-kit/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/tonlls1999/fastapi-di-kit/releases/tag/v0.1.0
