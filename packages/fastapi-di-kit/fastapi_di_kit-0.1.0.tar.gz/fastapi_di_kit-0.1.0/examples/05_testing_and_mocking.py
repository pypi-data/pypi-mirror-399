"""
Testing and Mocking Example

This example demonstrates how to test services that use dependency injection,
including mocking dependencies and overriding services for tests.
"""

import pytest
from typing import Protocol
from fastapi_di_kit import service, repository, get_container, DIContainer, Lifecycle


# Domain interfaces (ports)
class IEmailService(Protocol):
    """Email service interface."""
    def send_email(self, to: str, subject: str, body: str) -> bool:
        ...


class IUserRepository(Protocol):
    """User repository interface."""
    def get_user(self, user_id: int) -> dict:
        ...
    
    def save_user(self, user: dict) -> bool:
        ...


# Production implementations
@repository(interface=IEmailService)
class SendGridEmailService:
    """Production email service using SendGrid."""
    
    def send_email(self, to: str, subject: str, body: str) -> bool:
        # In real app, would call SendGrid API
        print(f"📧 Sending email to {to}: {subject}")
        return True


@repository(interface=IUserRepository)
class PostgresUserRepository:
    """Production user repository using PostgreSQL."""
    
    def get_user(self, user_id: int) -> dict:
        # In real app, would query database
        print(f"🗄️  Fetching user {user_id} from database")
        return {"id": user_id, "name": f"User {user_id}", "email": f"user{user_id}@example.com"}
    
    def save_user(self, user: dict) -> bool:
        print(f"🗄️  Saving user {user['id']} to database")
        return True


# Business logic service (the code we want to test)
@service()
class UserService:
    """User service with business logic."""
    
    def __init__(self, repository: IUserRepository, email: IEmailService):
        self.repository = repository
        self.email = email
    
    def register_user(self, name: str, email: str) -> dict:
        """Register a new user and send welcome email."""
        user = {
            "id": 123,
            "name": name,
            "email": email,
            "status": "active"
        }
        
        # Save to repository
        saved = self.repository.save_user(user)
        if not saved:
            raise Exception("Failed to save user")
        
        # Send welcome email
        email_sent = self.email.send_email(
            to=email,
            subject="Welcome!",
            body=f"Welcome {name}!"
        )
        
        if not email_sent:
            raise Exception("Failed to send email")
        
        return user
    
    def get_user_profile(self, user_id: int) -> dict:
        """Get user profile."""
        return self.repository.get_user(user_id)


# ============================================================================
# Mock Implementations for Testing
# ============================================================================

class MockEmailService:
    """Mock email service for testing."""
    
    def __init__(self):
        self.sent_emails = []
    
    def send_email(self, to: str, subject: str, body: str) -> bool:
        """Record email instead of sending."""
        self.sent_emails.append({
            "to": to,
            "subject": subject,
            "body": body
        })
        return True
    
    def get_sent_count(self) -> int:
        return len(self.sent_emails)


class MockUserRepository:
    """Mock user repository for testing."""
    
    def __init__(self):
        self.users = {}
        self.get_calls = []
        self.save_calls = []
    
    def get_user(self, user_id: int) -> dict:
        """Return mock user data."""
        self.get_calls.append(user_id)
        return self.users.get(user_id, {
            "id": user_id,
            "name": f"Mock User {user_id}",
            "email": f"mock{user_id}@example.com"
        })
    
    def save_user(self, user: dict) -> bool:
        """Save to in-memory dict."""
        self.save_calls.append(user)
        self.users[user["id"]] = user
        return True


class FailingEmailService:
    """Mock that simulates email failure."""
    
    def send_email(self, to: str, subject: str, body: str) -> bool:
        return False  # Always fail


# ============================================================================
# Test Examples
# ============================================================================

def test_user_registration_success():
    """Test successful user registration with mocks."""
    print("\n" + "=" * 60)
    print("Test 1: User Registration Success")
    print("=" * 60)
    
    # Create isolated container for this test
    container = DIContainer()
    
    # Register mocks instead of real implementations
    mock_email = MockEmailService()
    mock_repo = MockUserRepository()
    
    container.register(IEmailService, factory=lambda: mock_email)
    container.register(IUserRepository, factory=lambda: mock_repo)
    container.register(UserService)
    
    # Test the service
    user_service = container.resolve(UserService)
    result = user_service.register_user("John Doe", "john@example.com")
    
    # Assertions
    assert result["name"] == "John Doe"
    assert result["email"] == "john@example.com"
    assert mock_repo.save_calls[0]["name"] == "John Doe"
    assert mock_email.get_sent_count() == 1
    assert mock_email.sent_emails[0]["to"] == "john@example.com"
    
    print("✅ Test passed!")
    print(f"   - User saved: {mock_repo.save_calls[0]['name']}")
    print(f"   - Email sent to: {mock_email.sent_emails[0]['to']}")


def test_user_registration_email_failure():
    """Test user registration when email fails."""
    print("\n" + "=" * 60)
    print("Test 2: User Registration Email Failure")
    print("=" * 60)
    
    container = DIContainer()
    
    # Use failing email mock
    container.register(IEmailService, factory=lambda: FailingEmailService())
    container.register(IUserRepository, factory=lambda: MockUserRepository())
    container.register(UserService)
    
    user_service = container.resolve(UserService)
    
    # Should raise exception when email fails
    try:
        user_service.register_user("Jane Doe", "jane@example.com")
        assert False, "Should have raised exception"
    except Exception as e:
        assert "Failed to send email" in str(e)
        print(f"✅ Test passed! Correctly raised: {e}")


def test_get_user_profile():
    """Test getting user profile."""
    print("\n" + "=" * 60)
    print("Test 3: Get User Profile")
    print("=" * 60)
    
    container = DIContainer()
    
    # Setup mocks
    mock_repo = MockUserRepository()
    mock_repo.users[42] = {
        "id": 42,
        "name": "Test User",
        "email": "test@example.com"
    }
    
    container.register(IUserRepository, factory=lambda: mock_repo)
    container.register(IEmailService, factory=lambda: MockEmailService())
    container.register(UserService)
    
    # Test
    user_service = container.resolve(UserService)
    profile = user_service.get_user_profile(42)
    
    assert profile["id"] == 42
    assert profile["name"] == "Test User"
    assert len(mock_repo.get_calls) == 1
    
    print("✅ Test passed!")
    print(f"   - Repository called {len(mock_repo.get_calls)} time(s)")
    print(f"   - Profile: {profile}")


def test_with_pytest():
    """Example of how these would work with pytest."""
    print("\n" + "=" * 60)
    print("Pytest Integration Example")
    print("=" * 60)
    print("""
In a real test file (test_user_service.py):

    @pytest.fixture
    def container():
        \"\"\"Create fresh container for each test.\"\"\"
        container = DIContainer()
        
        # Register mocks
        container.register(IEmailService, factory=lambda: MockEmailService())
        container.register(IUserRepository, factory=lambda: MockUserRepository())
        container.register(UserService)
        
        return container
    
    def test_user_registration(container):
        service = container.resolve(UserService)
        result = service.register_user("Test", "test@example.com")
        assert result["name"] == "Test"
    """)
    print("=" * 60)


def main():
    """Run all test examples."""
    print("=" * 60)
    print("Testing and Mocking Example - fastapi-di-kit")
    print("=" * 60)
    print("\nDemonstrating how to test services with DI:\n")
    
    # Run example tests
    test_user_registration_success()
    test_user_registration_email_failure()
    test_get_user_profile()
    test_with_pytest()
    
    print("\n" + "=" * 60)
    print("Key Testing Benefits:")
    print("=" * 60)
    print("✓ Easy to mock dependencies")
    print("✓ Isolated test containers")
    print("✓ No global state pollution")
    print("✓ Test specific scenarios (success/failure)")
    print("✓ No need for complex setup/teardown")
    print("=" * 60)
    print()


if __name__ == "__main__":
    main()
