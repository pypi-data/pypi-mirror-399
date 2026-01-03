"""External service adapters."""

from fastapi_di_kit import repository, Lifecycle
from ..domain.entities import User
from ..domain.ports import IEmailService


@repository(interface=IEmailService, lifecycle=Lifecycle.SINGLETON)
class ConsoleEmailService:
    """Console-based email service for demonstration."""
    
    def send_welcome_email(self, user: User) -> bool:
        """Print welcome email to console."""
        print(f"\n{'='*50}")
        print(f"📧 Sending welcome email to: {user.email}")
        print(f"   Subject: Welcome {user.name}!")
        print(f"   Body: Thank you for joining our platform.")
        print(f"{'='*50}\n")
        return True
