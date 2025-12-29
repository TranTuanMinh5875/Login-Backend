from functools import wraps
from flask import request, jsonify
from src.infrastructure.services.jwt_service import JWTService

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            if auth_header.startswith('Bearer '):
                token = auth_header.split(' ')[1]
        
        if not token:
            return jsonify({'error': 'Token is missing'}), 401
        
        auth_service = JWTService()
        payload = auth_service.verify_token(token)
        
        if not payload:
            return jsonify({'error': 'Token is invalid or expired'}), 401
        
        request.user_id = int(payload['sub'])
        request.user_role = payload['role']
        request.is_guest = payload.get('is_guest', False)
        
        return f(*args, **kwargs)
    
    return decorated

def roles_required(*roles):
    def wrapper(f):
        @wraps(f)
        @token_required
        def decorated(*args, **kwargs):
            if request.user_role not in roles:
                return jsonify({
                    'error': 'Forbidden',
                    'message': f'Required roles: {roles}'
                }), 403
            return f(*args, **kwargs)
        return decorated
    return wrapper