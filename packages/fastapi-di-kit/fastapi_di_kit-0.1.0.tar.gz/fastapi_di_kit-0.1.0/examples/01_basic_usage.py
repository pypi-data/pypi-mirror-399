"""
Basic Usage Example

This example demonstrates the fundamental features of fastapi-di-kit:
- Service registration with @service decorator
- Automatic dependency injection
- Manual resolution from container
"""

from fastapi_di_kit import service, get_container


# Step 1: Define your services with the @service decorator
@service()
class DatabaseService:
    """Simulates a database connection."""
    
    def __init__(self):
        self.connected = True
        print("✓ DatabaseService initialized")
    
    def query(self, sql: str) -> str:
        return f"Query result: {sql}"


@service()
class UserRepository:
    """Repository for user data - automatically gets DatabaseService injected."""
    
    def __init__(self, db: DatabaseService):
        self.db = db
        print("✓ UserRepository initialized with DatabaseService")
    
    def get_user(self, user_id: int) -> dict:
        result = self.db.query(f"SELECT * FROM users WHERE id={user_id}")
        return {"id": user_id, "data": result}


@service()
class UserService:
    """Business logic service - automatically gets UserRepository injected."""
    
    def __init__(self, repository: UserRepository):
        self.repository = repository
        print("✓ UserService initialized with UserRepository")
    
    def find_user(self, user_id: int) -> dict:
        return self.repository.get_user(user_id)


def main():
    print("=" * 60)
    print("Basic Usage Example - fastapi-di-kit")
    print("=" * 60)
    print()
    
    # Step 2: Get the global DI container
    container = get_container()
    
    print("Resolving UserService...")
    print("(Dependencies will be automatically injected)\n")
    
    # Step 3: Resolve services - dependencies are automatically injected!
    user_service = container.resolve(UserService)
    
    print()
    print("Using the service:")
    user = user_service.find_user(42)
    print(f"Found user: {user}")
    
    print()
    print("=" * 60)
    print("Key Points:")
    print("=" * 60)
    print("1. @service() decorator automatically registers the class")
    print("2. Dependencies are resolved based on type hints")
    print("3. Default lifecycle is SINGLETON (same instance reused)")
    print("4. No manual wiring needed!")
    print()
    
    # Demonstrate singleton behavior
    print("Demonstrating SINGLETON lifecycle:")
    user_service2 = container.resolve(UserService)
    print(f"Same instance? {user_service is user_service2}")
    print()


if __name__ == "__main__":
    main()
