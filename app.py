from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_marshmallow import Marshmallow
from flask_cors import CORS
from sqlalchemy import inspect, text
import os
from datetime import timedelta
from dotenv import load_dotenv

# Load environment variables from .env file (if present)
load_dotenv()

# Initialize Flask app
app = Flask(__name__)

# Configuration
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
# Force SQLite for development - ignore any PostgreSQL DATABASE_URL
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///crop_recommendation.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY', 'dev-jwt-secret-change-in-production')
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=24)

# Google OAuth Configuration
# Prefer environment variables; fall back to the client you provided for local dev
app.config['GOOGLE_CLIENT_ID'] = os.environ.get('GOOGLE_CLIENT_ID', '314683354771-85tbs0n3ko4ve3j6hufjnr0gqe1katr4.apps.googleusercontent.com')
app.config['GOOGLE_CLIENT_SECRET'] = os.environ.get('GOOGLE_CLIENT_SECRET', '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')
app.config['GOOGLE_DISCOVERY_URL'] = "https://accounts.google.com/.well-known/openid_configuration"

# Initialize extensions
jwt = JWTManager()
ma = Marshmallow()
CORS(app)

# Import models and db
from models import User, Farm, Planting, Recommendation, db
from services.google_auth import google_auth_service

# Initialize extensions with app
db.init_app(app)
jwt.init_app(app)
ma.init_app(app)
google_auth_service.init_app(app)

# Import routes
from routes.auth import auth_bp
from routes.soil import soil_bp
from routes.weather import weather_bp
from routes.market import market_bp
from routes.recommendations import recommendations_bp
from routes.disease import disease_bp
from routes.translate import translate_bp
from routes.voice import voice_bp

# Register blueprints
app.register_blueprint(auth_bp, url_prefix='/api/auth')
app.register_blueprint(soil_bp, url_prefix='/api/soil')
app.register_blueprint(weather_bp, url_prefix='/api/weather')
app.register_blueprint(market_bp, url_prefix='/api/market')
app.register_blueprint(recommendations_bp, url_prefix='/api/recommend')
app.register_blueprint(disease_bp, url_prefix='/api/disease')
app.register_blueprint(translate_bp, url_prefix='/api/translate')
app.register_blueprint(voice_bp, url_prefix='/api/voice')

# Error handlers
@app.errorhandler(400)
def bad_request(error):
    return jsonify({'error': 'Bad request', 'message': str(error)}), 400

@app.errorhandler(401)
def unauthorized(error):
    return jsonify({'error': 'Unauthorized', 'message': 'Authentication required'}), 401

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Not found', 'message': 'Resource not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error', 'message': 'An unexpected error occurred'}), 500

# Health check endpoint
@app.route('/api/health')
def health_check():
    return jsonify({
        'status': 'healthy',
        'message': 'Crop Recommendation API is running',
        'version': '1.0.0'
    })

# Create database tables
def create_tables():
    with app.app_context():
        db.create_all()

def ensure_user_table_columns():
    """Add new profile columns to the users table if they are missing (for existing SQLite DBs)."""
    with app.app_context():
        inspector = inspect(db.engine)
        if 'users' not in inspector.get_table_names():
            return
        existing_columns = {col['name'] for col in inspector.get_columns('users')}
        alterations = []
        if 'phone' not in existing_columns:
            alterations.append("ALTER TABLE users ADD COLUMN phone VARCHAR(20)")
        if 'farming_experience' not in existing_columns:
            alterations.append("ALTER TABLE users ADD COLUMN farming_experience INTEGER")
        if 'crops' not in existing_columns:
            alterations.append("ALTER TABLE users ADD COLUMN crops TEXT")
        if alterations:
            for statement in alterations:
                db.session.execute(text(statement))
            # Initialize new TEXT column with empty JSON array for consistency
            db.session.execute(text("UPDATE users SET crops = '[]' WHERE crops IS NULL"))
            db.session.commit()

# Initialize database on startup
create_tables()
ensure_user_table_columns()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000, load_dotenv=False)
