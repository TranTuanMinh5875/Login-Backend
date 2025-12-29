from flask import Flask
from flask_cors import CORS
from src.api.v1.routes.auth_routes import auth_bp
from src.infrastructure.database.session import db
from src.infrastructure.config.settings import settings

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
    
    with app.app_context():
        db.create_all()
    
    @app.route('/health')
    def health_check():
        return {'status': 'healthy', 'service': 'auth-api'}
    
    return app