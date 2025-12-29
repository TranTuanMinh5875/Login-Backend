from typing import Optional
from dataclasses import dataclass
from ...domain.entities.user import User, UserRole
from ...domain.repositories.user_repository import UserRepository
from ...application.interfaces.auth_service import AuthService

@dataclass
class LoginWithRoleRequest:
    email: str
    password: str
    role: UserRole
    remember_me: bool = False

@dataclass
class LoginWithRoleResponse:
    success: bool
    access_token: Optional[str] = None
    refresh_token: Optional[str] = None
    user: Optional[User] = None
    error_message: Optional[str] = None

class LoginWithRoleUseCase:
    def __init__(
        self, 
        user_repository: UserRepository,
        auth_service: AuthService
    ):
        self.user_repository = user_repository
        self.auth_service = auth_service
    
    def execute(self, request: LoginWithRoleRequest) -> LoginWithRoleResponse:
        user = self.user_repository.find_by_email(request.email)
        if not user:
            return LoginWithRoleResponse(
                success=False,
                error_message="Invalid email or password"
            )
        
        if user.role != request.role:
            return LoginWithRoleResponse(
                success=False,
                error_message=f"User is not registered as {request.role.value}"
            )
        
        if not user.is_active:
            return LoginWithRoleResponse(
                success=False,
                error_message="Account is deactivated"
            )
        
        if not self.auth_service.verify_password(request.password, user.password_hash):
            return LoginWithRoleResponse(
                success=False,
                error_message="Invalid email or password"
            )
        
        self.user_repository.update_last_login(user.id)
        
        token_expiry = 7 * 24 * 60 if request.remember_me else 24 * 60
        access_token = self.auth_service.create_access_token(
            user_id=user.id,
            role=user.role.value,
            expires_minutes=token_expiry
        )
        
        refresh_token = self.auth_service.create_refresh_token(user_id=user.id)
        
        return LoginWithRoleResponse(
            success=True,
            access_token=access_token,
            refresh_token=refresh_token,
            user=user
        )