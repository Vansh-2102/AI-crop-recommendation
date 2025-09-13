#!/usr/bin/env python3
"""
Startup script for the Crop Recommendation API
"""

import os
import sys
from app import app, db

def create_tables():
    """Create database tables"""
    try:
        with app.app_context():
            db.create_all()
            print("✓ Database tables created successfully")
    except Exception as e:
        print(f"✗ Error creating database tables: {e}")
        sys.exit(1)

def main():
    """Main startup function"""
    print("Starting Crop Recommendation API...")
    print("=" * 50)
    
    # Set environment variables if not set
    if not os.environ.get('SECRET_KEY'):
        os.environ['SECRET_KEY'] = 'dev-secret-key-change-in-production'
        print("⚠️  Using default SECRET_KEY (change in production)")
    
    if not os.environ.get('JWT_SECRET_KEY'):
        os.environ['JWT_SECRET_KEY'] = 'dev-jwt-secret-change-in-production'
        print("⚠️  Using default JWT_SECRET_KEY (change in production)")
    
    if not os.environ.get('DATABASE_URL'):
        os.environ['DATABASE_URL'] = 'sqlite:///crop_recommendation.db'
        print("⚠️  Using SQLite database (change to PostgreSQL in production)")
    
    # Create database tables
    create_tables()
    
    # Start the application
    print("=" * 50)
    print("🚀 Starting Flask development server...")
    print("📍 API available at: http://localhost:5000")
    print("📚 API documentation: http://localhost:5000/api/health")
    print("🛑 Press Ctrl+C to stop the server")
    print("=" * 50)
    
    try:
        app.run(debug=True, host='0.0.0.0', port=5000)
    except KeyboardInterrupt:
        print("\n👋 Server stopped by user")
    except Exception as e:
        print(f"\n❌ Server error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
