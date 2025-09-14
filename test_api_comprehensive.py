#!/usr/bin/env python3
"""
Comprehensive API testing script for Crop Recommendation Platform
Tests all endpoints with detailed validation and reporting
"""

import requests
import json
import time
import base64
from datetime import datetime
from typing import Dict, List, Any

class APITester:
    def __init__(self, base_url: str = "http://localhost:5000"):
        self.base_url = base_url
        self.session = requests.Session()
        self.access_token = None
        self.test_results = []
        
    def log_test(self, test_name: str, success: bool, details: str = ""):
        """Log test result"""
        result = {
            "test": test_name,
            "success": success,
            "details": details,
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}")
        if details:
            print(f"   Details: {details}")
    
    def test_health_check(self):
        """Test health check endpoint"""
        try:
            response = self.session.get(f"{self.base_url}/api/health")
            if response.status_code == 200:
                data = response.json()
                self.log_test("Health Check", True, f"Status: {data.get('status')}")
                return True
            else:
                self.log_test("Health Check", False, f"Status code: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Health Check", False, str(e))
            return False
    
    def test_user_registration(self):
        """Test user registration"""
        try:
            data = {
                "name": f"Test User {int(time.time())}",
                "email": f"test{int(time.time())}@example.com",
                "password": "testpassword123",
                "location": "Test Location",
                "farm_size": 5.0,
                "preferred_language": "en"
            }
            
            response = self.session.post(f"{self.base_url}/api/auth/register", json=data)
            if response.status_code == 201:
                result = response.json()
                self.access_token = result.get('access_token')
                self.session.headers.update({'Authorization': f'Bearer {self.access_token}'})
                self.log_test("User Registration", True, f"User ID: {result.get('user', {}).get('id')}")
                return True
            else:
                self.log_test("User Registration", False, f"Status: {response.status_code}, Response: {response.text}")
                return False
        except Exception as e:
            self.log_test("User Registration", False, str(e))
            return False
    
    def test_user_login(self):
        """Test user login"""
        try:
            data = {
                "email": "test@example.com",
                "password": "testpassword123"
            }
            
            response = self.session.post(f"{self.base_url}/api/auth/login", json=data)
            if response.status_code == 200:
                result = response.json()
                self.access_token = result.get('access_token')
                self.session.headers.update({'Authorization': f'Bearer {self.access_token}'})
                self.log_test("User Login", True, "Login successful")
                return True
            else:
                self.log_test("User Login", False, f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("User Login", False, str(e))
            return False
    
    def test_soil_data(self):
        """Test soil data endpoints"""
        try:
            # Test soil data retrieval
            response = self.session.get(f"{self.base_url}/api/soil/28.6139/77.2090")
            if response.status_code == 200:
                data = response.json()
                self.log_test("Soil Data Retrieval", True, f"pH: {data.get('soil_data', {}).get('ph')}")
            else:
                self.log_test("Soil Data Retrieval", False, f"Status: {response.status_code}")
                return False
            
            # Test soil analysis
            analysis_data = {
                "soil_data": {
                    "ph": 6.5,
                    "moisture": 0.3,
                    "organic_matter": 4.2,
                    "nitrogen": 0.3,
                    "phosphorus": 30,
                    "potassium": 200
                }
            }
            
            response = self.session.post(f"{self.base_url}/api/soil/analyze", json=analysis_data)
            if response.status_code == 200:
                data = response.json()
                self.log_test("Soil Analysis", True, f"Quality Score: {data.get('soil_quality_score')}")
            else:
                self.log_test("Soil Analysis", False, f"Status: {response.status_code}")
            
            return True
        except Exception as e:
            self.log_test("Soil Data Tests", False, str(e))
            return False
    
    def test_weather_data(self):
        """Test weather data endpoints"""
        try:
            # Test weather data
            response = self.session.get(f"{self.base_url}/api/weather/Delhi")
            if response.status_code == 200:
                data = response.json()
                self.log_test("Weather Data", True, f"Temperature: {data.get('weather', {}).get('current', {}).get('temperature')}°C")
            else:
                self.log_test("Weather Data", False, f"Status: {response.status_code}")
                return False
            
            # Test agricultural conditions
            response = self.session.get(f"{self.base_url}/api/weather/agricultural-conditions/Delhi")
            if response.status_code == 200:
                data = response.json()
                self.log_test("Agricultural Conditions", True, f"Growing Condition: {data.get('agricultural_conditions', {}).get('growing_condition')}")
            else:
                self.log_test("Agricultural Conditions", False, f"Status: {response.status_code}")
            
            return True
        except Exception as e:
            self.log_test("Weather Data Tests", False, str(e))
            return False
    
    def test_market_data(self):
        """Test market data endpoints"""
        try:
            # Test market prices
            response = self.session.get(f"{self.base_url}/api/market/prices")
            if response.status_code == 200:
                data = response.json()
                self.log_test("Market Prices", True, f"Total crops: {data.get('total_crops')}")
            else:
                self.log_test("Market Prices", False, f"Status: {response.status_code}")
                return False
            
            # Test specific crop price
            response = self.session.get(f"{self.base_url}/api/market/prices/wheat")
            if response.status_code == 200:
                data = response.json()
                self.log_test("Crop Price Details", True, f"Current Price: ₹{data.get('current_data', {}).get('current_price')}")
            else:
                self.log_test("Crop Price Details", False, f"Status: {response.status_code}")
            
            # Test market trends
            response = self.session.get(f"{self.base_url}/api/market/trends")
            if response.status_code == 200:
                data = response.json()
                self.log_test("Market Trends", True, f"Market Sentiment: {data.get('market_summary', {}).get('market_sentiment')}")
            else:
                self.log_test("Market Trends", False, f"Status: {response.status_code}")
            
            return True
        except Exception as e:
            self.log_test("Market Data Tests", False, str(e))
            return False
    
    def test_crop_recommendations(self):
        """Test crop recommendation endpoints"""
        try:
            data = {
                "location": "Punjab, India",
                "soil_data": {
                    "ph": 6.5,
                    "moisture": 0.3,
                    "organic_matter": 4.2,
                    "nitrogen": 0.3,
                    "phosphorus": 30,
                    "potassium": 200
                },
                "weather_data": {
                    "temperature": 25,
                    "humidity": 60,
                    "precipitation": 5
                },
                "farm_size": 10.5,
                "budget": 50000
            }
            
            response = self.session.post(f"{self.base_url}/api/recommend/crops", json=data)
            if response.status_code == 200:
                result = response.json()
                recommendations = result.get('recommendations', [])
                self.log_test("Crop Recommendations", True, f"Generated {len(recommendations)} recommendations")
                
                if recommendations:
                    top_crop = recommendations[0]
                    self.log_test("Top Recommendation", True, f"Crop: {top_crop.get('crop')}, Score: {top_crop.get('suitability_score')}")
            else:
                self.log_test("Crop Recommendations", False, f"Status: {response.status_code}")
                return False
            
            return True
        except Exception as e:
            self.log_test("Crop Recommendations", False, str(e))
            return False
    
    def test_disease_detection(self):
        """Test disease detection endpoints"""
        try:
            # Create a simple 1x1 pixel image for testing
            image_data = base64.b64encode(b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\nIDATx\x9cc\x00\x01\x00\x00\x05\x00\x01\r\n-\xdb\x00\x00\x00\x00IEND\xaeB`\x82').decode()
            
            data = {
                "image_data": image_data,
                "crop_type": "wheat",
                "location": "Punjab, India"
            }
            
            response = self.session.post(f"{self.base_url}/api/disease/detect", json=data)
            if response.status_code == 200:
                result = response.json()
                detection = result.get('detection_result', {})
                self.log_test("Disease Detection", True, f"Disease: {detection.get('name')}, Confidence: {detection.get('confidence')}")
            else:
                self.log_test("Disease Detection", False, f"Status: {response.status_code}")
                return False
            
            # Test disease list
            response = self.session.get(f"{self.base_url}/api/disease/diseases/wheat")
            if response.status_code == 200:
                data = response.json()
                self.log_test("Disease List", True, f"Found {data.get('total_diseases')} diseases for wheat")
            else:
                self.log_test("Disease List", False, f"Status: {response.status_code}")
            
            return True
        except Exception as e:
            self.log_test("Disease Detection", False, str(e))
            return False
    
    def test_translation(self):
        """Test translation endpoints"""
        try:
            data = {
                "text": "Hello, how is the weather today?",
                "source_language": "en",
                "target_language": "hi"
            }
            
            response = self.session.post(f"{self.base_url}/api/translate/translate", json=data)
            if response.status_code == 200:
                result = response.json()
                self.log_test("Text Translation", True, f"Translated: {result.get('translated_text')}")
            else:
                self.log_test("Text Translation", False, f"Status: {response.status_code}")
                return False
            
            # Test language detection
            data = {"text": "मौसम कैसा है आज?"}
            response = self.session.post(f"{self.base_url}/api/translate/detect-language", json=data)
            if response.status_code == 200:
                result = response.json()
                self.log_test("Language Detection", True, f"Detected: {result.get('language_name')}")
            else:
                self.log_test("Language Detection", False, f"Status: {response.status_code}")
            
            return True
        except Exception as e:
            self.log_test("Translation Tests", False, str(e))
            return False
    
    def test_voice_queries(self):
        """Test voice query endpoints"""
        try:
            data = {
                "query": "What's the weather like today?",
                "location": "Delhi, India",
                "language": "en"
            }
            
            response = self.session.post(f"{self.base_url}/api/voice/query", json=data)
            if response.status_code == 200:
                result = response.json()
                self.log_test("Voice Query", True, f"Intent: {result.get('detected_intent')}, Confidence: {result.get('confidence')}")
            else:
                self.log_test("Voice Query", False, f"Status: {response.status_code}")
                return False
            
            # Test supported intents
            response = self.session.get(f"{self.base_url}/api/voice/intents")
            if response.status_code == 200:
                data = response.json()
                self.log_test("Supported Intents", True, f"Found {len(data.get('supported_intents', []))} intents")
            else:
                self.log_test("Supported Intents", False, f"Status: {response.status_code}")
            
            return True
        except Exception as e:
            self.log_test("Voice Query Tests", False, str(e))
            return False
    
    def run_all_tests(self):
        """Run all API tests"""
        print("🚀 Starting Comprehensive API Tests...")
        print("=" * 60)
        
        # Test sequence
        tests = [
            ("Health Check", self.test_health_check),
            ("User Registration", self.test_user_registration),
            ("Soil Data", self.test_soil_data),
            ("Weather Data", self.test_weather_data),
            ("Market Data", self.test_market_data),
            ("Crop Recommendations", self.test_crop_recommendations),
            ("Disease Detection", self.test_disease_detection),
            ("Translation", self.test_translation),
            ("Voice Queries", self.test_voice_queries)
        ]
        
        passed = 0
        total = len(tests)
        
        for test_name, test_func in tests:
            print(f"\n📋 Testing {test_name}...")
            try:
                if test_func():
                    passed += 1
            except Exception as e:
                self.log_test(test_name, False, f"Exception: {str(e)}")
            print("-" * 40)
        
        # Summary
        print("\n" + "=" * 60)
        print(f"📊 Test Results: {passed}/{total} test suites passed")
        
        if passed == total:
            print("🎉 All tests passed! The API is fully functional.")
        else:
            print("❌ Some tests failed. Check the details above.")
        
        # Save detailed results
        self.save_test_results()
        
        return passed == total
    
    def save_test_results(self):
        """Save test results to file"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"test_results_{timestamp}.json"
        
        results = {
            "timestamp": datetime.now().isoformat(),
            "base_url": self.base_url,
            "total_tests": len(self.test_results),
            "passed_tests": len([r for r in self.test_results if r["success"]]),
            "failed_tests": len([r for r in self.test_results if not r["success"]]),
            "test_details": self.test_results
        }
        
        with open(filename, 'w') as f:
            json.dump(results, f, indent=2)
        
        print(f"📄 Detailed results saved to: {filename}")

def main():
    """Main function"""
    tester = APITester()
    success = tester.run_all_tests()
    exit(0 if success else 1)

if __name__ == "__main__":
    main()
