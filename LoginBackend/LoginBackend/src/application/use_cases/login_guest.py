from typing import Optional
from dataclasses import dataclass
from datetime import datetime
from ...domain.entities.user import User, UserRole, AuthProvider
from ...domain.repositories.user_repository import UserRepository
from ...application.interfaces.auth_service import AuthService

@dataclass
class LoginGuestResponse:
    success: bool
    access_token: Optional[str] = None
    user: Optional[User] = None
    error_message: Optional[str] = None

class LoginGuestUseCase:
    def __init__(
        self, 
        user_repository: UserRepository,
        auth_service: AuthService
    ):
        self.user_repository = user_repository
        self.auth_service = auth_service
    
    def execute(self) -> LoginGuestResponse:
        try:
            timestamp = int(datetime.now().timestamp())
            guest_email = f"guest_{timestamp}@example.com"
            guest_username = f"Guest_{timestamp % 1000000}"
            
            guest_user = User(
                email=guest_email,
                username=guest_username,
                password_hash=None,
                role=UserRole.GUEST,
                provider=AuthProvider.LOCAL
            )
            
            saved_user = self.user_repository.save(guest_user)
            
            access_token = self.auth_service.create_access_token(
                user_id=saved_user.id,
                role=saved_user.role.value,
                expires_minutes=120,
                is_guest=True
            )
            
            return LoginGuestResponse(
                success=True,
                access_token=access_token,
                user=saved_user
            )
            
        except Exception as e:
            return LoginGuestResponse(
                success=False,
                error_message=str(e)
            )