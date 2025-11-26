from flask import Blueprint, request, jsonify, redirect, url_for, session
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from models import User, db
from marshmallow import Schema, fields, ValidationError
from services.google_auth import google_auth_service
import re

auth_bp = Blueprint('auth', __name__)

# Validation schemas
class UserRegistrationSchema(Schema):
    name = fields.Str(required=True, validate=lambda x: len(x) >= 2)
    email = fields.Email(required=True)
    password = fields.Str(allow_none=True, validate=lambda x: x is None or len(x) >= 6)
    location = fields.Str(allow_none=True)
    farm_size = fields.Float(allow_none=True, validate=lambda x: x is None or x > 0)
    phone = fields.Str(allow_none=True)
    farming_experience = fields.Int(allow_none=True, validate=lambda x: x is None or x >= 0)
    crops = fields.List(fields.Str(), allow_none=True)
    preferred_language = fields.Str(load_default='en')

class UserLoginSchema(Schema):
    email = fields.Email(required=True)
    password = fields.Str(required=True)

registration_schema = UserRegistrationSchema()
login_schema = UserLoginSchema()

@auth_bp.route('/register', methods=['POST'])
def register():
    """Register a new user"""
    try:
        data = registration_schema.load(request.json)
    except ValidationError as err:
        return jsonify({'error': 'Validation error', 'details': err.messages}), 400
    
    # Check if user already exists
    if User.query.filter_by(email=data['email']).first():
        return jsonify({'error': 'User already exists with this email'}), 409
    
    # Create new user
    user = User(
        name=data['name'],
        email=data['email'],
        location=data.get('location'),
        farm_size=data.get('farm_size'),
        phone=data.get('phone'),
        farming_experience=data.get('farming_experience'),
        preferred_language=data.get('preferred_language', 'en')
    )
    if data.get('crops'):
        user.set_crops(data['crops'])
    
    # Set password only if provided (for local auth)
    if data.get('password'):
        user.set_password(data['password'])
    
    try:
        db.session.add(user)
        db.session.commit()
        
        # Create access token
        access_token = create_access_token(identity=str(user.id))
        
        return jsonify({
            'message': 'User registered successfully',
            'access_token': access_token,
            'user': user.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to create user', 'details': str(e)}), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    """Login user and return JWT token"""
    try:
        data = login_schema.load(request.json)
    except ValidationError as err:
        return jsonify({'error': 'Validation error', 'details': err.messages}), 400
    
    # Find user
    user = User.query.filter_by(email=data['email']).first()
    
    if not user:
        return jsonify({'error': 'Invalid email or password'}), 401
    
    # Check if user is Google OAuth user
    if user.auth_provider == 'google':
        return jsonify({'error': 'Please use Google Sign-In for this account'}), 401
    
    # Check password for local users
    if not user.check_password(data['password']):
        return jsonify({'error': 'Invalid email or password'}), 401
    
    # Create access token
    access_token = create_access_token(identity=str(user.id))
    
    return jsonify({
        'message': 'Login successful',
        'access_token': access_token,
        'user': user.to_dict()
    }), 200

@auth_bp.route('/profile', methods=['GET'])
@jwt_required()
def get_profile():
    """Get current user profile"""
    current_user_id = int(get_jwt_identity())
    user = User.query.get(current_user_id)
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    return jsonify({
        'user': user.to_dict()
    }), 200

@auth_bp.route('/profile', methods=['PUT'])
@jwt_required()
def update_profile():
    """Update user profile"""
    current_user_id = int(get_jwt_identity())
    user = User.query.get(current_user_id)
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    data = request.json or {}
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    if 'name' in data and data['name']:
        user.name = data['name'].strip()
    
    if 'email' in data and data['email']:
        new_email = data['email'].strip().lower()
        if new_email != user.email:
            if User.query.filter(User.email == new_email, User.id != user.id).first():
                return jsonify({'error': 'Email is already in use by another account'}), 400
            user.email = new_email
    
    if 'phone' in data:
        user.phone = data['phone'].strip() if data['phone'] else None
    
    if 'location' in data:
        user.location = data['location'].strip() if data['location'] else None
    
    farm_size_value = data.get('farm_size', data.get('farmSize'))
    if farm_size_value is not None:
        try:
            farm_size_float = float(farm_size_value)
            if farm_size_float < 0:
                return jsonify({'error': 'Farm size must be a positive number'}), 400
            user.farm_size = farm_size_float
        except (ValueError, TypeError):
            return jsonify({'error': 'Farm size must be a number'}), 400
    
    experience_value = data.get('farming_experience', data.get('experience'))
    if experience_value is not None:
        try:
            experience = float(experience_value)
            if experience < 0:
                return jsonify({'error': 'Experience must be a positive number'}), 400
            user.farming_experience = int(experience)
        except (ValueError, TypeError):
            return jsonify({'error': 'Experience must be a number'}), 400
    
    if 'crops' in data:
        crops_value = data['crops']
        if isinstance(crops_value, list):
            user.set_crops(crops_value)
        elif isinstance(crops_value, str):
            user.set_crops([crops_value])
        else:
            return jsonify({'error': 'Crops must be a list of crop names'}), 400
    
    if 'preferred_language' in data:
        user.preferred_language = data['preferred_language']
    
    try:
        db.session.commit()
        return jsonify({
            'message': 'Profile updated successfully',
            'user': user.to_dict()
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to update profile', 'details': str(e)}), 500

@auth_bp.route('/change-password', methods=['POST'])
@jwt_required()
def change_password():
    """Change user password"""
    current_user_id = int(get_jwt_identity())
    user = User.query.get(current_user_id)
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    data = request.json
    if not data or 'current_password' not in data or 'new_password' not in data:
        return jsonify({'error': 'Current password and new password required'}), 400
    
    # Verify current password
    if not user.check_password(data['current_password']):
        return jsonify({'error': 'Current password is incorrect'}), 401
    
    # Validate new password
    if len(data['new_password']) < 6:
        return jsonify({'error': 'New password must be at least 6 characters long'}), 400
    
    # Update password
    user.set_password(data['new_password'])
    
    try:
        db.session.commit()
        return jsonify({'message': 'Password changed successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to change password', 'details': str(e)}), 500

# Google OAuth routes
@auth_bp.route('/google/login', methods=['GET'])
def google_login():
    """Initiate Google OAuth login"""
    try:
        redirect_uri = url_for('auth.google_callback', _external=True)
        redirect_response = google_auth_service.get_authorization_url(redirect_uri)
        if redirect_response is None:
            return jsonify({
                'error': 'Google OAuth not configured',
                'message': 'Please set up Google OAuth credentials in your environment variables',
                'instructions': {
                    'step1': 'Go to Google Cloud Console: https://console.cloud.google.com/',
                    'step2': 'Create OAuth 2.0 credentials',
                    'step3': 'Set GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET environment variables',
                    'step4': 'Add http://localhost:5000/api/auth/google/callback as authorized redirect URI'
                }
            }), 500
        return redirect_response
    except Exception as e:
        return jsonify({'error': 'Failed to initiate Google login', 'details': str(e)}), 500

@auth_bp.route('/google/callback', methods=['GET'])
def google_callback():
    """Handle Google OAuth callback"""
    try:
        code = request.args.get('code')
        if not code:
            return jsonify({'error': 'Authorization code not provided'}), 400
        
        redirect_uri = url_for('auth.google_callback', _external=True)
        google_user_info = google_auth_service.get_user_info_from_code(code, redirect_uri)
        
        if not google_user_info:
            return jsonify({'error': 'Failed to get user info from Google'}), 400
        
        # Create or update user
        user = google_auth_service.create_or_update_user(google_user_info)
        if not user:
            return jsonify({'error': 'Failed to create or update user'}), 500
        
        # Create access token
        access_token = create_access_token(identity=str(user.id))
        
        return jsonify({
            'message': 'Google login successful',
            'access_token': access_token,
            'user': user.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Google authentication failed', 'details': str(e)}), 500

@auth_bp.route('/google/verify', methods=['POST'])
def google_verify_token():
    """Verify Google ID token (for frontend integration)"""
    try:
        data = request.json
        if not data or 'token' not in data:
            return jsonify({'error': 'Google ID token required'}), 400
        
        google_user_info = google_auth_service.verify_token(data['token'])
        if not google_user_info:
            return jsonify({'error': 'Invalid Google token'}), 401
        
        # Create or update user
        user = google_auth_service.create_or_update_user(google_user_info)
        if not user:
            return jsonify({'error': 'Failed to create or update user'}), 500
        
        # Create access token
        access_token = create_access_token(identity=str(user.id))
        
        return jsonify({
            'message': 'Google token verification successful',
            'access_token': access_token,
            'user': user.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Google token verification failed', 'details': str(e)}), 500
