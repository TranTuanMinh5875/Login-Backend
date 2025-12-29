from flask import Blueprint, request, jsonify
from src.api.v1.controllers.auth_controller import AuthController
from src.api.middleware.auth_middleware import token_required, roles_required

auth_bp = Blueprint('auth', __name__, url_prefix='/api/v1/auth')

@auth_bp.route('/login', methods=['POST'])
def login():
    return AuthController.login()

@auth_bp.route('/register', methods=['POST'])
def register():
    return AuthController.register()

@auth_bp.route('/guest', methods=['POST'])
def login_as_guest():
    return AuthController.login_as_guest()

@auth_bp.route('/quick-login', methods=['POST'])
def quick_login():
    return AuthController.quick_login()

@auth_bp.route('/me', methods=['GET'])
@token_required
def get_current_user():
    return AuthController.get_current_user()

@auth_bp.route('/logout', methods=['POST'])
@token_required
def logout():
    return {"message": "Logged out successfully"}, 200

@auth_bp.route('/admin-only', methods=['GET'])
@roles_required('admin')
def admin_only():
    return {"message": "Welcome Admin!", "user_id": request.user_id}, 200

@auth_bp.route('/restaurant-staff-only', methods=['GET'])
@roles_required('restaurant_staff')
def restaurant_staff_only():
    return {"message": "Welcome Restaurant Staff!", "user_id": request.user_id}, 200

@auth_bp.route('/user-only', methods=['GET'])
@roles_required('user')
def user_only():
    return {"message": "Welcome User!", "user_id": request.user_id}, 200

@auth_bp.route('/guest-only', methods=['GET'])
@roles_required('guest')
def guest_only():
    return {"message": "Welcome Guest!", "user_id": request.user_id, "is_guest": request.is_guest}, 200

@auth_bp.route('/forgot-password', methods=['POST'])
def forgot_password():
    email = request.json.get('email')
    if not email:
        return {"error": "Email is required"}, 400
    return {"message": f"Password reset email sent to {email}"}, 200

@auth_bp.route('/reset-password/<token>', methods=['POST'])
def reset_password(token):
    new_password = request.json.get('new_password')
    if not new_password:
        return {"error": "New password is required"}, 400
    return {"message": "Password reset successful"}, 200

@auth_bp.route('/create-admin', methods=['POST'])
@roles_required('admin')
def create_admin_account():
    from ....infrastructure.repositories.user_repositories_impl import UserRepositoryImpl
    from ....infrastructure.services.jwt_service import JWTService
    from ....application.use_cases.register_user import RegisterUserUseCase, RegisterUserRequest
    from ....domain.entities.user import UserRole
    
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    username = data.get('username')
    
    if not email or not password:
        return {"error": "Email and password are required"}, 400
    
    user_repo = UserRepositoryImpl()
    auth_service = JWTService()
    
    use_case = RegisterUserUseCase(user_repo, auth_service)
    request_data = RegisterUserRequest(
        email=email,
        password=password,
        username=username,
        role=UserRole.ADMIN,
        register_as_customer=False
    )
    
    result = use_case.execute(request_data)
    
    if not result.success:
        return {"error": result.error_message}, 400
    
    return {
        "message": "Admin account created successfully",
        "user": {
            "id": result.user.id,
            "email": result.user.email,
            "username": result.user.username,
            "role": result.user.role.value
        }
    }, 201

@auth_bp.route('/create-restaurant-staff', methods=['POST'])
@roles_required('admin')
def create_restaurant_staff_account():
    from ....infrastructure.repositories.user_repositories_impl import UserRepositoryImpl
    from ....infrastructure.services.jwt_service import JWTService
    from ....application.use_cases.register_user import RegisterUserUseCase, RegisterUserRequest
    from ....domain.entities.user import UserRole
    
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    username = data.get('username')
    
    if not email or not password:
        return {"error": "Email and password are required"}, 400
    
    user_repo = UserRepositoryImpl()
    auth_service = JWTService()
    
    use_case = RegisterUserUseCase(user_repo, auth_service)
    request_data = RegisterUserRequest(
        email=email,
        password=password,
        username=username,
        role=UserRole.RESTAURANT_STAFF,
        register_as_customer=False
    )
    
    result = use_case.execute(request_data)
    
    if not result.success:
        return {"error": result.error_message}, 400
    
    return {
        "message": "Restaurant staff account created successfully",
        "user": {
            "id": result.user.id,
            "email": result.user.email,
            "username": result.user.username,
            "role": result.user.role.value
        }
    }, 201