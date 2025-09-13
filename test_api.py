#!/usr/bin/env python3
"""
Simple test script to verify the API endpoints are working
"""

import requests
import json
import time

BASE_URL = "http://localhost:5000"

def test_health_check():
    """Test health check endpoint"""
    print("Testing health check...")
    try:
        response = requests.get(f"{BASE_URL}/api/health")
        if response.status_code == 200:
            print("✓ Health check passed")
            return True
        else:
            print(f"✗ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ Health check failed: {e}")
        return False

def test_user_registration():
    """Test user registration"""
    print("Testing user registration...")
    try:
        data = {
            "name": "Test User",
            "email": f"test{int(time.time())}@example.com",
            "password": "testpassword123",
            "location": "Test Location",
            "farm_size": 5.0,
            "preferred_language": "en"
        }
        
        response = requests.post(f"{BASE_URL}/api/auth/register", json=data)
        if response.status_code == 201:
            print("✓ User registration passed")
            return response.json().get('access_token')
        else:
            print(f"✗ User registration failed: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"✗ User registration failed: {e}")
        return None

def test_soil_data(token):
    """Test soil data endpoint"""
    print("Testing soil data...")
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(f"{BASE_URL}/api/soil/28.6139/77.2090", headers=headers)
        if response.status_code == 200:
            print("✓ Soil data test passed")
            return True
        else:
            print(f"✗ Soil data test failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ Soil data test failed: {e}")
        return False

def test_weather_data(token):
    """Test weather data endpoint"""
    print("Testing weather data...")
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(f"{BASE_URL}/api/weather/Delhi", headers=headers)
        if response.status_code == 200:
            print("✓ Weather data test passed")
            return True
        else:
            print(f"✗ Weather data test failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ Weather data test failed: {e}")
        return False

def test_market_data(token):
    """Test market data endpoint"""
    print("Testing market data...")
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(f"{BASE_URL}/api/market/prices", headers=headers)
        if response.status_code == 200:
            print("✓ Market data test passed")
            return True
        else:
            print(f"✗ Market data test failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ Market data test failed: {e}")
        return False

def test_crop_recommendations(token):
    """Test crop recommendations endpoint"""
    print("Testing crop recommendations...")
    try:
        headers = {"Authorization": f"Bearer {token}"}
        data = {
            "location": "Delhi, India",
            "soil_data": {
                "ph": 6.5,
                "moisture": 0.3,
                "organic_matter": 4.2
            },
            "weather_data": {
                "temperature": 25,
                "humidity": 60
            },
            "farm_size": 5.0,
            "budget": 25000
        }
        
        response = requests.post(f"{BASE_URL}/api/recommend/crops", json=data, headers=headers)
        if response.status_code == 200:
            print("✓ Crop recommendations test passed")
            return True
        else:
            print(f"✗ Crop recommendations test failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ Crop recommendations test failed: {e}")
        return False

def test_disease_detection(token):
    """Test disease detection endpoint"""
    print("Testing disease detection...")
    try:
        headers = {"Authorization": f"Bearer {token}"}
        data = {
            "image_data": "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg==",  # 1x1 pixel PNG
            "crop_type": "wheat",
            "location": "Delhi, India"
        }
        
        response = requests.post(f"{BASE_URL}/api/disease/detect", json=data, headers=headers)
        if response.status_code == 200:
            print("✓ Disease detection test passed")
            return True
        else:
            print(f"✗ Disease detection test failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ Disease detection test failed: {e}")
        return False

def test_translation(token):
    """Test translation endpoint"""
    print("Testing translation...")
    try:
        headers = {"Authorization": f"Bearer {token}"}
        data = {
            "text": "Hello, how is the weather today?",
            "source_language": "en",
            "target_language": "hi"
        }
        
        response = requests.post(f"{BASE_URL}/api/translate/translate", json=data, headers=headers)
        if response.status_code == 200:
            print("✓ Translation test passed")
            return True
        else:
            print(f"✗ Translation test failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ Translation test failed: {e}")
        return False

def test_voice_query(token):
    """Test voice query endpoint"""
    print("Testing voice query...")
    try:
        headers = {"Authorization": f"Bearer {token}"}
        data = {
            "query": "What's the weather like today?",
            "location": "Delhi, India",
            "language": "en"
        }
        
        response = requests.post(f"{BASE_URL}/api/voice/query", json=data, headers=headers)
        if response.status_code == 200:
            print("✓ Voice query test passed")
            return True
        else:
            print(f"✗ Voice query test failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ Voice query test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("Starting API tests...")
    print("=" * 50)
    
    # Test health check first
    if not test_health_check():
        print("Health check failed. Make sure the server is running.")
        return
    
    # Register a test user and get token
    token = test_user_registration()
    if not token:
        print("User registration failed. Cannot continue with other tests.")
        return
    
    print("=" * 50)
    
    # Run other tests
    tests = [
        test_soil_data,
        test_weather_data,
        test_market_data,
        test_crop_recommendations,
        test_disease_detection,
        test_translation,
        test_voice_query
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test(token):
            passed += 1
        print("-" * 30)
    
    print("=" * 50)
    print(f"Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! The API is working correctly.")
    else:
        print("❌ Some tests failed. Check the output above for details.")

if __name__ == "__main__":
    main()
