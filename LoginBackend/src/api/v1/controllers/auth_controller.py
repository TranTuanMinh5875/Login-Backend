from flask import jsonify, request
from typing import Dict, Any
import json
from ....application.use_cases.login_with_role import LoginWithRoleUseCase, LoginWithRoleRequest
from ....application.use_cases.register_user import RegisterUserUseCase, RegisterUserRequest
from ....application.use_cases.login_guest import LoginGuestUseCase
from ....infrastructure.repositories.user_repositories_impl import UserRepositoryImpl
from ....infrastructure.services.jwt_service import JWTService
from ....domain.entities.user import UserRole
from ..schemas.auth_schemas import (
    LoginRequest, RegisterRequest, TokenResponse, 
    UserResponse, ErrorResponse, UserRole as SchemaUserRole
)

class AuthController:
    
    @staticmethod
    def login() -> Dict[str, Any]:
        try:
            login_data = LoginRequest(**request.get_json())
            
            user_repo = UserRepositoryImpl()
            auth_service = JWTService()
            
            role_mapping = {
                SchemaUserRole.USER: UserRole.USER,
                SchemaUserRole.ADMIN: UserRole.ADMIN,
                SchemaUserRole.RESTAURANT_STAFF: UserRole.RESTAURANT_STAFF,
                SchemaUserRole.GUEST: UserRole.GUEST
            }
            
            domain_role = role_mapping[login_data.role]
            
            use_case = LoginWithRoleUseCase(user_repo, auth_service)
            request_data = LoginWithRoleRequest(
                email=login_data.email,
                password=login_data.password,
                role=domain_role,
                remember_me=login_data.remember_me
            )
            
            result = use_case.execute(request_data)
            
            if not result.success:
                return jsonify(ErrorResponse(
                    error="authentication_failed",
                    message=result.error_message
                ).dict()), 401
            
            token_response = TokenResponse(
                access_token=result.access_token,
                refresh_token=result.refresh_token,
                expires_in=1440 if not login_data.remember_me else 10080,
                user={
                    "id": result.user.id,
                    "email": result.user.email,
                    "username": result.user.username,
                    "role": result.user.role.value
                }
            )
            
            return jsonify(token_response.dict()), 200
            
        except Exception as e:
            return jsonify(ErrorResponse(
                error="server_error",
                message=str(e)
            ).dict()), 500
    
    @staticmethod
    def register() -> Dict[str, Any]:
        try:
            register_data = RegisterRequest(**request.get_json())
            
            user_repo = UserRepositoryImpl()
            auth_service = JWTService()
            
            role_mapping = {
                SchemaUserRole.USER: UserRole.USER,
                SchemaUserRole.ADMIN: UserRole.ADMIN,
                SchemaUserRole.RESTAURANT_STAFF: UserRole.RESTAURANT_STAFF,
                SchemaUserRole.GUEST: UserRole.GUEST
            }
            
            domain_role = role_mapping[register_data.role]
            
            # IMPORTANT: Customers can only register as USER
            # Even if they try to register as ADMIN or RESTAURANT_STAFF,
            # they will be registered as USER
            if domain_role != UserRole.USER:
                return jsonify(ErrorResponse(
                    error="registration_failed",
                    message="Customers can only register as regular users"
                ).dict()), 400
            
            use_case = RegisterUserUseCase(user_repo, auth_service)
            request_data = RegisterUserRequest(
                email=register_data.email,
                password=register_data.password,
                username=register_data.username,
                role=UserRole.USER,  # Force USER role for customer registration
                register_as_customer=True
            )
            
            result = use_case.execute(request_data)
            
            if not result.success:
                return jsonify(ErrorResponse(
                    error="registration_failed",
                    message=result.error_message
                ).dict()), 400
            
            token_response = TokenResponse(
                access_token=result.access_token,
                expires_in=1440,
                user={
                    "id": result.user.id,
                    "email": result.user.email,
                    "username": result.user.username,
                    "role": result.user.role.value
                }
            )
            
            return jsonify(token_response.dict()), 201
            
        except Exception as e:
            return jsonify(ErrorResponse(
                error="server_error",
                message=str(e)
            ).dict()), 500
    
    @staticmethod
    def login_as_guest() -> Dict[str, Any]:
        try:
            user_repo = UserRepositoryImpl()
            auth_service = JWTService()
            
            use_case = LoginGuestUseCase(user_repo, auth_service)
            result = use_case.execute()
            
            if not result.success:
                return jsonify(ErrorResponse(
                    error="guest_login_failed",
                    message=result.error_message
                ).dict()), 400
            
            token_response = TokenResponse(
                access_token=result.access_token,
                expires_in=120,
                user={
                    "id": result.user.id,
                    "email": result.user.email,
                    "username": result.user.username,
                    "role": result.user.role.value,
                    "is_guest": True
                }
            )
            
            return jsonify(token_response.dict()), 200
            
        except Exception as e:
            return jsonify(ErrorResponse(
                error="server_error",
                message=str(e)
            ).dict()), 500
    
    @staticmethod
    def get_current_user() -> Dict[str, Any]:
        try:
            auth_header = request.headers.get('Authorization')
            if not auth_header or not auth_header.startswith('Bearer '):
                return jsonify(ErrorResponse(
                    error="unauthorized",
                    message="No token provided"
                ).dict()), 401
            
            token = auth_header.split(' ')[1]
            auth_service = JWTService()
            payload = auth_service.verify_token(token)
            
            if not payload:
                return jsonify(ErrorResponse(
                    error="unauthorized",
                    message="Invalid token"
                ).dict()), 401
            
            user_repo = UserRepositoryImpl()
            user = user_repo.find_by_id(int(payload['sub']))
            
            if not user:
                return jsonify(ErrorResponse(
                    error="not_found",
                    message="User not found"
                ).dict()), 404
            
            user_response = UserResponse(
                id=user.id,
                email=user.email,
                username=user.username,
                role=user.role.value,
                is_active=user.is_active,
                created_at=user.created_at.isoformat() if user.created_at else None
            )
            
            return jsonify(user_response.dict()), 200
            
        except Exception as e:
            return jsonify(ErrorResponse(
                error="server_error",
                message=str(e)
            ).dict()), 500
    
    @staticmethod
    def quick_login() -> Dict[str, Any]:
        try:
            data = request.get_json()
            role = data.get('role', 'user')
            
            test_accounts = {
                'user': {'email': 'user@example.com', 'password': 'Password123'},
                'admin': {'email': 'admin@example.com', 'password': 'AdminPass123'},
                'restaurant_staff': {'email': 'staff@restaurant.com', 'password': 'StaffPass123'},
                'guest': None
            }
            
            if role == 'guest':
                return AuthController.login_as_guest()
            
            if role not in test_accounts:
                return jsonify(ErrorResponse(
                    error="invalid_role",
                    message=f"Role must be one of: {list(test_accounts.keys())}"
                ).dict()), 400
            
            test_account = test_accounts[role]
            request._cached_data = json.dumps({
                'email': test_account['email'],
                'password': test_account['password'],
                'role': role,
                'remember_me': False
            })
            
            return AuthController.login()
            
        except Exception as e:
            return jsonify(ErrorResponse(
                error="server_error",
                message=str(e)
            ).dict()), 500