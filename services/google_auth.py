"""
Google OAuth authentication service
"""
import os
import json
import requests
from flask import current_app, url_for
from google.auth.transport import requests as google_requests
from google.oauth2 import id_token
from authlib.integrations.flask_client import OAuth
from models import User, db


class GoogleAuthService:
    """Service for handling Google OAuth authentication"""
    
    def __init__(self, app=None):
        self.oauth = OAuth()
        if app:
            self.init_app(app)
    
    def init_app(self, app):
        """Initialize Google OAuth with Flask app"""
        self.oauth.init_app(app)
        
        # Check if Google OAuth credentials are configured
        client_id = app.config.get('GOOGLE_CLIENT_ID')
        client_secret = app.config.get('GOOGLE_CLIENT_SECRET')
        
        if not client_id or not client_secret:
            app.logger.warning("Google OAuth credentials not configured. Google login will not work.")
            self.google = None
            return
        
        # Register Google OAuth client using OIDC discovery (avoids deprecated URLs)
        # The prior authorize_url (o/oauth2/auth) causes 404 errors on Google; use v2 discovery instead.
        self.google = self.oauth.register(
            name='google',
            client_id=client_id,
            client_secret=client_secret,
            server_metadata_url=app.config.get('GOOGLE_DISCOVERY_URL'),
            client_kwargs={
                'scope': 'openid email profile',
                'prompt': 'consent',
                'access_type': 'offline'
            }
        )
    
    def get_authorization_url(self, redirect_uri):
        """Get Google OAuth authorization URL"""
        if self.google is None:
            current_app.logger.error("Google OAuth not configured. Please set GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET environment variables.")
            return None
            
        try:
            return self.google.authorize_redirect(redirect_uri)
        except Exception as e:
            current_app.logger.error(f"Error getting Google authorization URL: {e}")
            return None
    
    def verify_token(self, token):
        """Verify Google ID token and return user info"""
        try:
            # Verify the token
            idinfo = id_token.verify_oauth2_token(
                token, 
                google_requests.Request(), 
                current_app.config.get('GOOGLE_CLIENT_ID')
            )
            
            # Check if token is valid
            if idinfo['iss'] not in ['accounts.google.com', 'https://accounts.google.com']:
                raise ValueError('Wrong issuer.')
            
            return {
                'google_id': idinfo['sub'],
                'email': idinfo['email'],
                'name': idinfo['name'],
                'profile_picture': idinfo.get('picture'),
                'email_verified': idinfo.get('email_verified', False)
            }
            
        except ValueError as e:
            current_app.logger.error(f"Invalid Google token: {e}")
            return None
        except Exception as e:
            current_app.logger.error(f"Error verifying Google token: {e}")
            return None
    
    def get_user_info_from_code(self, code, redirect_uri):
        """Exchange authorization code for user info"""
        try:
            # Exchange code for token
            token = self.google.authorize_access_token(redirect_uri=redirect_uri)
            if not token:
                return None

            # Fetch OIDC userinfo using the access token
            resp = self.google.get('userinfo')
            if not resp:
                return None
            user_info = resp.json()
            if not isinstance(user_info, dict):
                return None

            return {
                'google_id': user_info.get('sub') or user_info.get('id'),
                'email': user_info.get('email'),
                'name': user_info.get('name'),
                'profile_picture': user_info.get('picture'),
                'email_verified': user_info.get('email_verified', False)
            }
            
        except Exception as e:
            current_app.logger.error(f"Error getting user info from Google code: {e}")
            return None
    
    def create_or_update_user(self, google_user_info):
        """Create or update user from Google OAuth info"""
        try:
            # Check if user exists by Google ID
            user = User.query.filter_by(google_id=google_user_info['google_id']).first()
            
            if user:
                # Update existing user
                user.name = google_user_info['name']
                user.profile_picture = google_user_info.get('profile_picture')
                user.updated_at = db.func.now()
            else:
                # Check if user exists by email
                user = User.query.filter_by(email=google_user_info['email']).first()
                
                if user:
                    # Link existing account with Google
                    user.google_id = google_user_info['google_id']
                    user.profile_picture = google_user_info.get('profile_picture')
                    user.auth_provider = 'google'
                    user.updated_at = db.func.now()
                else:
                    # Create new user
                    user = User(
                        name=google_user_info['name'],
                        email=google_user_info['email'],
                        google_id=google_user_info['google_id'],
                        profile_picture=google_user_info.get('profile_picture'),
                        auth_provider='google',
                        preferred_language='en'
                    )
                    db.session.add(user)
            
            db.session.commit()
            return user
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error creating/updating Google user: {e}")
            return None


# Global instance
google_auth_service = GoogleAuthService()


