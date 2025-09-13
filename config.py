import os
from datetime import timedelta

class Config:
    """Base configuration class"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-secret-key-change-in-production'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'postgresql://username:password@localhost/crop_recommendation'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or 'jwt-secret-string-change-in-production'
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=24)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)
    
    # External API configurations (mock)
    SOIL_API_URL = os.environ.get('SOIL_API_URL') or 'https://mock-soil-api.com'
    WEATHER_API_URL = os.environ.get('WEATHER_API_URL') or 'https://mock-weather-api.com'
    MARKET_API_URL = os.environ.get('MARKET_API_URL') or 'https://mock-market-api.com'
    
    # ML Model configurations
    DISEASE_MODEL_PATH = os.environ.get('DISEASE_MODEL_PATH') or 'models/disease_classifier.pkl'
    CROP_RECOMMENDATION_MODEL_PATH = os.environ.get('CROP_RECOMMENDATION_MODEL_PATH') or 'models/crop_recommender.pkl'
    
    # File upload configurations
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER') or 'uploads'
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'tiff'}
    
    # Translation service configuration
    TRANSLATION_SERVICE = os.environ.get('TRANSLATION_SERVICE') or 'mock'  # mock, google, azure
    GOOGLE_TRANSLATE_API_KEY = os.environ.get('GOOGLE_TRANSLATE_API_KEY')
    AZURE_TRANSLATE_KEY = os.environ.get('AZURE_TRANSLATE_KEY')
    
    # Voice processing configuration
    VOICE_PROCESSING_SERVICE = os.environ.get('VOICE_PROCESSING_SERVICE') or 'mock'  # mock, azure, google
    AZURE_SPEECH_KEY = os.environ.get('AZURE_SPEECH_KEY')
    GOOGLE_SPEECH_KEY = os.environ.get('GOOGLE_SPEECH_KEY')
    
    # Rate limiting
    RATELIMIT_STORAGE_URL = os.environ.get('RATELIMIT_STORAGE_URL') or 'memory://'
    
    # Logging
    LOG_LEVEL = os.environ.get('LOG_LEVEL') or 'INFO'
    LOG_FILE = os.environ.get('LOG_FILE') or 'app.log'

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL') or 'postgresql://username:password@localhost/crop_recommendation_dev'

class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'postgresql://username:password@localhost/crop_recommendation_prod'

class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('TEST_DATABASE_URL') or 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False

# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
