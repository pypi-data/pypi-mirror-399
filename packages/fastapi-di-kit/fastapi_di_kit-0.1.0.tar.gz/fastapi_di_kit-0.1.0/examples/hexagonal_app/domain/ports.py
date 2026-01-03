"""Port interfaces defining contracts between domain and infrastructure."""

from typing import Protocol, Optional
from .entities import User


class IUserRepository(Protocol):
    """Port for user data persistence."""
    
    def get_by_id(self, user_id: int) -> Optional[User]:
        """Retrieve a user by ID."""
        ...
    
    def save(self, user: User) -> User:
        """Save a user and return the saved instance."""
        ...
    
    def get_all(self) -> list[User]:
        """Get all users."""
        ...


class IEmailService(Protocol):
    """Port for email notifications."""
    
    def send_welcome_email(self, user: User) -> bool:
        """Send a welcome email to a user."""
        ...
