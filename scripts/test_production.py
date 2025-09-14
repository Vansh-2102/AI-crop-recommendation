#!/usr/bin/env python3
"""
Production API Testing Script
Tests all endpoints in production environment
"""

import requests
import json
import time
import sys
from datetime import datetime
from typing import Dict, List, Any

class ProductionAPITester:
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
            response = self.session.get(f"{self.base_url}/api/health", timeout=10)
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
    
    def test_user_registration_and_login(self):
        """Test user registration and login"""
        try:
            # Register user
            data = {
                "name": f"Production Test User {int(time.time())}",
                "email": f"prodtest{int(time.time())}@example.com",
                "password": "testpassword123",
                "location": "Production Test Location",
                "farm_size": 5.0,
                "preferred_language": "en"
            }
            
            response = self.session.post(f"{self.base_url}/api/auth/register", json=data, timeout=10)
            if response.status_code == 201:
                result = response.json()
                self.access_token = result.get('access_token')
                self.session.headers.update({'Authorization': f'Bearer {self.access_token}'})
                self.log_test("User Registration", True, f"User ID: {result.get('user', {}).get('id')}")
            else:
                self.log_test("User Registration", False, f"Status: {response.status_code}")
                return False
            
            # Test login
            login_data = {
                "email": data["email"],
                "password": data["password"]
            }
            
            response = self.session.post(f"{self.base_url}/api/auth/login", json=login_data, timeout=10)
            if response.status_code == 200:
                self.log_test("User Login", True, "Login successful")
                return True
            else:
                self.log_test("User Login", False, f"Status: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("User Authentication", False, str(e))
            return False
    
    def test_core_apis(self):
        """Test core API endpoints"""
        try:
            # Test soil data
            response = self.session.get(f"{self.base_url}/api/soil/28.6139/77.2090", timeout=10)
            if response.status_code == 200:
                self.log_test("Soil Data API", True, "Soil data retrieved successfully")
            else:
                self.log_test("Soil Data API", False, f"Status: {response.status_code}")
            
            # Test weather data
            response = self.session.get(f"{self.base_url}/api/weather/Delhi", timeout=10)
            if response.status_code == 200:
                self.log_test("Weather Data API", True, "Weather data retrieved successfully")
            else:
                self.log_test("Weather Data API", False, f"Status: {response.status_code}")
            
            # Test market data
            response = self.session.get(f"{self.base_url}/api/market/prices", timeout=10)
            if response.status_code == 200:
                self.log_test("Market Data API", True, "Market data retrieved successfully")
            else:
                self.log_test("Market Data API", False, f"Status: {response.status_code}")
            
            return True
            
        except Exception as e:
            self.log_test("Core APIs", False, str(e))
            return False
    
    def test_crop_recommendations(self):
        """Test crop recommendation API"""
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
            
            response = self.session.post(f"{self.base_url}/api/recommend/crops", json=data, timeout=15)
            if response.status_code == 200:
                result = response.json()
                recommendations = result.get('recommendations', [])
                self.log_test("Crop Recommendations", True, f"Generated {len(recommendations)} recommendations")
                return True
            else:
                self.log_test("Crop Recommendations", False, f"Status: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Crop Recommendations", False, str(e))
            return False
    
    def test_disease_detection(self):
        """Test disease detection API"""
        try:
            # Create a simple 1x1 pixel image for testing
            import base64
            image_data = base64.b64encode(b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\nIDATx\x9cc\x00\x01\x00\x00\x05\x00\x01\r\n-\xdb\x00\x00\x00\x00IEND\xaeB`\x82').decode()
            
            data = {
                "image_data": image_data,
                "crop_type": "wheat",
                "location": "Punjab, India"
            }
            
            response = self.session.post(f"{self.base_url}/api/disease/detect", json=data, timeout=15)
            if response.status_code == 200:
                result = response.json()
                detection = result.get('detection_result', {})
                self.log_test("Disease Detection", True, f"Disease: {detection.get('name')}, Confidence: {detection.get('confidence')}")
                return True
            else:
                self.log_test("Disease Detection", False, f"Status: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Disease Detection", False, str(e))
            return False
    
    def test_translation(self):
        """Test translation API"""
        try:
            data = {
                "text": "Hello, how is the weather today?",
                "source_language": "en",
                "target_language": "hi"
            }
            
            response = self.session.post(f"{self.base_url}/api/translate/translate", json=data, timeout=10)
            if response.status_code == 200:
                result = response.json()
                self.log_test("Translation", True, f"Translated: {result.get('translated_text')}")
                return True
            else:
                self.log_test("Translation", False, f"Status: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Translation", False, str(e))
            return False
    
    def test_voice_queries(self):
        """Test voice query API"""
        try:
            data = {
                "query": "What's the weather like today?",
                "location": "Delhi, India",
                "language": "en"
            }
            
            response = self.session.post(f"{self.base_url}/api/voice/query", json=data, timeout=10)
            if response.status_code == 200:
                result = response.json()
                self.log_test("Voice Query", True, f"Intent: {result.get('detected_intent')}, Confidence: {result.get('confidence')}")
                return True
            else:
                self.log_test("Voice Query", False, f"Status: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Voice Query", False, str(e))
            return False
    
    def test_performance(self):
        """Test API performance"""
        try:
            start_time = time.time()
            
            # Test multiple concurrent requests
            import concurrent.futures
            
            def make_request():
                response = self.session.get(f"{self.base_url}/api/health", timeout=5)
                return response.status_code == 200
            
            with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
                futures = [executor.submit(make_request) for _ in range(20)]
                results = [future.result() for future in concurrent.futures.as_completed(futures)]
            
            end_time = time.time()
            duration = end_time - start_time
            success_rate = sum(results) / len(results) * 100
            
            self.log_test("Performance Test", success_rate > 90, f"Success rate: {success_rate:.1f}%, Duration: {duration:.2f}s")
            return success_rate > 90
            
        except Exception as e:
            self.log_test("Performance Test", False, str(e))
            return False
    
    def run_all_tests(self):
        """Run all production tests"""
        print("🚀 Starting Production API Tests...")
        print("=" * 60)
        
        tests = [
            ("Health Check", self.test_health_check),
            ("User Authentication", self.test_user_registration_and_login),
            ("Core APIs", self.test_core_apis),
            ("Crop Recommendations", self.test_crop_recommendations),
            ("Disease Detection", self.test_disease_detection),
            ("Translation", self.test_translation),
            ("Voice Queries", self.test_voice_queries),
            ("Performance", self.test_performance)
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
        print(f"📊 Production Test Results: {passed}/{total} test suites passed")
        
        if passed == total:
            print("🎉 All production tests passed! The API is fully functional.")
        else:
            print("❌ Some tests failed. Check the details above.")
        
        # Save results
        self.save_test_results()
        
        return passed == total
    
    def save_test_results(self):
        """Save test results to file"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"production_test_results_{timestamp}.json"
        
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
    base_url = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:5000"
    tester = ProductionAPITester(base_url)
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
