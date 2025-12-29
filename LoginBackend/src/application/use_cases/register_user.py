from typing import Optional
from dataclasses import dataclass
from ...domain.entities.user import User, UserRole, AuthProvider
from ...domain.value_objects.email import Email
from ...domain.value_objects.password import Password
from ...domain.repositories.user_repository import UserRepository
from ...application.interfaces.auth_service import AuthService

@dataclass
class RegisterUserRequest:
    email: str
    password: str
    username: Optional[str] = None
    role: UserRole = UserRole.USER
    register_as_customer: bool = True

@dataclass
class RegisterUserResponse:
    success: bool
    access_token: Optional[str] = None
    user: Optional[User] = None
    error_message: Optional[str] = None

class RegisterUserUseCase:
    def __init__(
        self, 
        user_repository: UserRepository,
        auth_service: AuthService
    ):
        self.user_repository = user_repository
        self.auth_service = auth_service
    
    def execute(self, request: RegisterUserRequest) -> RegisterUserResponse:
        try:
            email_obj = Email(value=request.email)
            
            password_obj = Password(value=request.password)
            
            existing_user = self.user_repository.find_by_email(email_obj.value)
            if existing_user:
                return RegisterUserResponse(
                    success=False,
                    error_message="Email already registered"
                )
            
            if request.register_as_customer:
                final_role = UserRole.USER
            else:
                final_role = request.role
            
            password_hash = self.auth_service.hash_password(password_obj.value)
            
            new_user = User(
                email=email_obj.value,
                username=request.username,
                password_hash=password_hash,
                role=final_role,
                provider=AuthProvider.LOCAL
            )
            
            saved_user = self.user_repository.save(new_user)
            
            access_token = self.auth_service.create_access_token(
                user_id=saved_user.id,
                role=saved_user.role.value
            )
            
            return RegisterUserResponse(
                success=True,
                access_token=access_token,
                user=saved_user
            )
            
        except ValueError as e:
            return RegisterUserResponse(
                success=False,
                error_message=str(e)
            )
        except Exception as e:
            return RegisterUserResponse(
                success=False,
                error_message="Registration failed"
            )