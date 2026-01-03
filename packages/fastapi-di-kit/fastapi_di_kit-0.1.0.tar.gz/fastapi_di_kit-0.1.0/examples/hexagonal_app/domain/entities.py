"""Domain entities - pure business objects with no external dependencies."""

from dataclasses import dataclass


@dataclass
class User:
    """User entity representing a user in the system."""
    
    id: int
    name: str
    email: str
    
    def __str__(self) -> str:
        return f"User(id={self.id}, name='{self.name}', email='{self.email}')"
