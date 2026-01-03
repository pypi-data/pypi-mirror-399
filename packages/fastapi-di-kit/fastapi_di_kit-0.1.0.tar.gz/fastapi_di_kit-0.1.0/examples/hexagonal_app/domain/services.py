"""Use cases / business logic depending only on port interfaces."""

from typing import Optional
from fastapi_di_kit import service, Lifecycle
from .entities import User
from .ports import IUserRepository, IEmailService


@service(lifecycle=Lifecycle.SINGLETON)
class UserService:
    """Business logic for user management."""
    
    def __init__(self, repository: IUserRepository, email_service: IEmailService):
        self.repository = repository
        self.email_service = email_service
        self._next_id = 1
    
    def create_user(self, name: str, email: str) -> User:
        """
        Create a new user and send welcome email.
        
        This is a use case that orchestrates domain logic and external services.
        """
        user = User(id=self._next_id, name=name, email=email)
        self._next_id += 1
        
        # Save user
        saved_user = self.repository.save(user)
        
        # Send welcome email
        self.email_service.send_welcome_email(saved_user)
        
        return saved_user
    
    def get_user(self, user_id: int) -> Optional[User]:
        """Retrieve a user by ID."""
        return self.repository.get_by_id(user_id)
    
    def list_users(self) -> list[User]:
        """List all users."""
        return self.repository.get_all()
