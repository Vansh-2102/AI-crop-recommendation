from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import json

# This will be initialized in app.py
db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    location = db.Column(db.String(200))
    farm_size = db.Column(db.Float)  # in acres
    preferred_language = db.Column(db.String(10), default='en')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    farms = db.relationship('Farm', backref='owner', lazy=True)
    recommendations = db.relationship('Recommendation', backref='user', lazy=True)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'location': self.location,
            'farm_size': self.farm_size,
            'preferred_language': self.preferred_language,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class Farm(db.Model):
    __tablename__ = 'farms'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    location = db.Column(db.String(200), nullable=False)
    size = db.Column(db.Float, nullable=False)  # in acres
    soil_data = db.Column(db.Text)  # JSON string
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    plantings = db.relationship('Planting', backref='farm', lazy=True)
    
    def get_soil_data(self):
        if self.soil_data:
            return json.loads(self.soil_data)
        return {}
    
    def set_soil_data(self, data):
        self.soil_data = json.dumps(data)
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'name': self.name,
            'location': self.location,
            'size': self.size,
            'soil_data': self.get_soil_data(),
            'latitude': self.latitude,
            'longitude': self.longitude,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class Planting(db.Model):
    __tablename__ = 'plantings'
    
    id = db.Column(db.Integer, primary_key=True)
    farm_id = db.Column(db.Integer, db.ForeignKey('farms.id'), nullable=False)
    crop = db.Column(db.String(100), nullable=False)
    planting_date = db.Column(db.Date)
    harvest_date = db.Column(db.Date)
    yield_amount = db.Column(db.Float)  # in kg
    profit = db.Column(db.Float)  # in currency
    conditions = db.Column(db.Text)  # JSON string for growing conditions
    status = db.Column(db.String(20), default='active')  # active, completed, failed
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def get_conditions(self):
        if self.conditions:
            return json.loads(self.conditions)
        return {}
    
    def set_conditions(self, data):
        self.conditions = json.dumps(data)
    
    def to_dict(self):
        return {
            'id': self.id,
            'farm_id': self.farm_id,
            'crop': self.crop,
            'planting_date': self.planting_date.isoformat() if self.planting_date else None,
            'harvest_date': self.harvest_date.isoformat() if self.harvest_date else None,
            'yield_amount': self.yield_amount,
            'profit': self.profit,
            'conditions': self.get_conditions(),
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class Recommendation(db.Model):
    __tablename__ = 'recommendations'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    location = db.Column(db.String(200), nullable=False)
    soil_data = db.Column(db.Text)  # JSON string
    weather_data = db.Column(db.Text)  # JSON string
    market_data = db.Column(db.Text)  # JSON string
    recommendations = db.Column(db.Text)  # JSON string
    confidence_score = db.Column(db.Float)  # 0-1
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def get_soil_data(self):
        if self.soil_data:
            return json.loads(self.soil_data)
        return {}
    
    def set_soil_data(self, data):
        self.soil_data = json.dumps(data)
    
    def get_weather_data(self):
        if self.weather_data:
            return json.loads(self.weather_data)
        return {}
    
    def set_weather_data(self, data):
        self.weather_data = json.dumps(data)
    
    def get_market_data(self):
        if self.market_data:
            return json.loads(self.market_data)
        return {}
    
    def set_market_data(self, data):
        self.market_data = json.dumps(data)
    
    def get_recommendations(self):
        if self.recommendations:
            return json.loads(self.recommendations)
        return []
    
    def set_recommendations(self, data):
        self.recommendations = json.dumps(data)
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'location': self.location,
            'soil_data': self.get_soil_data(),
            'weather_data': self.get_weather_data(),
            'market_data': self.get_market_data(),
            'recommendations': self.get_recommendations(),
            'confidence_score': self.confidence_score,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
