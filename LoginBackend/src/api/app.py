from flask import Flask
from flask_cors import CORS
from .v1.routes.auth_routes import auth_bp
from .v1.routes.kitchen_routes import kitchen_bp
from src.infrastructure.database.session import db
from src.infrastructure.config.settings import settings
import datetime

def create_app():
    app = Flask(__name__)
    
    app.config['SQLALCHEMY_DATABASE_URI'] = settings.DATABASE_URL
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = settings.JWT_SECRET_KEY
    
    db.init_app(app)
    
    CORS(app, 
         resources={r"/api/*": {"origins": settings.FRONTEND_URL}},
         supports_credentials=True
    )
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(kitchen_bp)
    
    with app.app_context():
        db.create_all()
        print(f"Database initialized at: {settings.DATABASE_PATH}")
        
        from src.infrastructure.database.models import UserModel
        from src.infrastructure.services.bcrypt_service import BcryptService
        
        if UserModel.query.count() == 0:
            print("Creating initial test users...")
            test_users = [
                {
                    'email': 'user@example.com',
                    'username': 'Regular User',
                    'password': 'Password123',
                    'role': 'user',
                    'is_verified': True
                },
                {
                    'email': 'admin@example.com',
                    'username': 'System Admin',
                    'password': 'AdminPass123',
                    'role': 'admin',
                    'is_verified': True
                },
                {
                    'email': 'staff@restaurant.com',
                    'username': 'Restaurant Staff',
                    'password': 'StaffPass123',
                    'role': 'restaurant_staff',
                    'is_verified': True
                }
            ]
            
            for user_data in test_users:
                hashed_password = BcryptService.hash_password(user_data['password'])
                new_user = UserModel(
                    email=user_data['email'],
                    username=user_data['username'],
                    password_hash=hashed_password,
                    role=user_data['role'],
                    is_verified=user_data['is_verified']
                )
                db.session.add(new_user)
            
            db.session.commit()
            print("Test users created!")
            print("Test credentials:")
            print("User: user@example.com / Password123")
            print("Admin: admin@example.com / AdminPass123")
            print("Staff: staff@restaurant.com / StaffPass123")
    
    @app.route('/')
    def home():
        return {
            'message': 'Restaurant Management API',
            'version': '1.0.0',
            'endpoints': {
                'auth': '/api/v1/auth/*',
                'kitchen': '/api/v1/kitchen/*',
                'health': '/health'
            }
        }
    
    @app.route('/health')
    def health_check():
        return {
            'status': 'healthy',
            'service': 'restaurant-api',
            'database': 'connected',
            'timestamp': datetime.datetime.now().isoformat()
        }
    
    return app