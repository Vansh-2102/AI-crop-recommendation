from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_marshmallow import Marshmallow
from flask_cors import CORS
import os
from datetime import timedelta

# Initialize Flask app
app = Flask(__name__)

# Configuration
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your-secret-key-here')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///crop_recommendation.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY', 'jwt-secret-string')
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=24)

# Initialize extensions
jwt = JWTManager()
ma = Marshmallow()
CORS(app)

# Import models and db
from models import User, Farm, Planting, Recommendation, db

# Initialize extensions with app
db.init_app(app)
jwt.init_app(app)
ma.init_app(app)

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

# Initialize database on startup
create_tables()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
