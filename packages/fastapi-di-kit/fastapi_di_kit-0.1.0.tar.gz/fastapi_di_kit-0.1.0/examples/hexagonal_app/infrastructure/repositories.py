"""Concrete repository adapters implementing port interfaces."""

from typing import Optional
from fastapi_di_kit import repository, Lifecycle
from ..domain.entities import User
from ..domain.ports import IUserRepository


@repository(interface=IUserRepository, lifecycle=Lifecycle.SINGLETON)
class InMemoryUserRepository:
    """In-memory implementation of user repository."""
    
    def __init__(self):
        self._users: dict[int, User] = {}
    
    def get_by_id(self, user_id: int) -> Optional[User]:
        """Retrieve a user by ID."""
        return self._users.get(user_id)
    
    def save(self, user: User) -> User:
        """Save a user and return the saved instance."""
        self._users[user.id] = user
        return user
    
    def get_all(self) -> list[User]:
        """Get all users."""
        return list(self._users.values())
