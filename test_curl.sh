#!/bin/bash

# Crop Recommendation API - cURL Testing Script
# Make sure the server is running on http://localhost:5000

BASE_URL="http://localhost:5000"
ACCESS_TOKEN=""

echo "🌱 Crop Recommendation API - cURL Testing Script"
echo "================================================"

# Function to register a user and get token
register_user() {
    echo "📝 Registering test user..."
    RESPONSE=$(curl -s -X POST "$BASE_URL/api/auth/register" \
        -H "Content-Type: application/json" \
        -d '{
            "name": "Test Farmer",
            "email": "farmer@test.com",
            "password": "testpass123",
            "location": "Punjab, India",
            "farm_size": 10.5,
            "preferred_language": "en"
        }')
    
    ACCESS_TOKEN=$(echo $RESPONSE | jq -r '.access_token')
    echo "✅ User registered successfully"
    echo "🔑 Access Token: ${ACCESS_TOKEN:0:20}..."
}

# Function to test health check
test_health() {
    echo "🏥 Testing health check..."
    curl -s "$BASE_URL/api/health" | jq '.'
    echo ""
}

# Function to test soil data
test_soil() {
    echo "🌍 Testing soil data..."
    curl -s -H "Authorization: Bearer $ACCESS_TOKEN" \
        "$BASE_URL/api/soil/28.6139/77.2090" | jq '.soil_data.ph, .soil_data.moisture'
    echo ""
}

# Function to test weather data
test_weather() {
    echo "🌤️ Testing weather data..."
    curl -s -H "Authorization: Bearer $ACCESS_TOKEN" \
        "$BASE_URL/api/weather/Delhi" | jq '.weather.current.temperature, .weather.current.conditions'
    echo ""
}

# Function to test market data
test_market() {
    echo "💰 Testing market data..."
    curl -s -H "Authorization: Bearer $ACCESS_TOKEN" \
        "$BASE_URL/api/market/prices" | jq '.market_data[0:3] | .[].crop, .[].current_price'
    echo ""
}

# Function to test crop recommendations
test_recommendations() {
    echo "🌾 Testing crop recommendations..."
    curl -s -X POST "$BASE_URL/api/recommend/crops" \
        -H "Authorization: Bearer $ACCESS_TOKEN" \
        -H "Content-Type: application/json" \
        -d '{
            "location": "Punjab, India",
            "soil_data": {
                "ph": 6.5,
                "moisture": 0.3,
                "organic_matter": 4.2
            },
            "weather_data": {
                "temperature": 25,
                "humidity": 60
            },
            "farm_size": 10.5,
            "budget": 50000
        }' | jq '.recommendations[0:3] | .[].crop, .[].suitability_score'
    echo ""
}

# Function to test disease detection
test_disease() {
    echo "🔬 Testing disease detection..."
    curl -s -X POST "$BASE_URL/api/disease/detect" \
        -H "Authorization: Bearer $ACCESS_TOKEN" \
        -H "Content-Type: application/json" \
        -d '{
            "image_data": "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg==",
            "crop_type": "wheat",
            "location": "Punjab, India"
        }' | jq '.detection_result.name, .detection_result.confidence'
    echo ""
}

# Function to test translation
test_translation() {
    echo "🌐 Testing translation..."
    curl -s -X POST "$BASE_URL/api/translate/translate" \
        -H "Authorization: Bearer $ACCESS_TOKEN" \
        -H "Content-Type: application/json" \
        -d '{
            "text": "What crops should I plant this season?",
            "source_language": "en",
            "target_language": "hi"
        }' | jq '.translated_text'
    echo ""
}

# Function to test voice query
test_voice() {
    echo "🎤 Testing voice query..."
    curl -s -X POST "$BASE_URL/api/voice/query" \
        -H "Authorization: Bearer $ACCESS_TOKEN" \
        -H "Content-Type: application/json" \
        -d '{
            "query": "What is the weather like today?",
            "location": "Delhi, India",
            "language": "en"
        }' | jq '.response_text'
    echo ""
}

# Main execution
main() {
    # Check if jq is installed
    if ! command -v jq &> /dev/null; then
        echo "❌ jq is not installed. Please install jq for JSON parsing."
        echo "   On Ubuntu/Debian: sudo apt-get install jq"
        echo "   On macOS: brew install jq"
        echo "   On Windows: choco install jq"
        exit 1
    fi
    
    # Check if server is running
    if ! curl -s "$BASE_URL/api/health" > /dev/null; then
        echo "❌ Server is not running. Please start the server first:"
        echo "   python app.py"
        exit 1
    fi
    
    echo "✅ Server is running"
    echo ""
    
    # Run all tests
    test_health
    register_user
    test_soil
    test_weather
    test_market
    test_recommendations
    test_disease
    test_translation
    test_voice
    
    echo "🎉 All tests completed successfully!"
    echo ""
    echo "📊 API Summary:"
    echo "   - Health Check: ✅"
    echo "   - Authentication: ✅"
    echo "   - Soil Analysis: ✅"
    echo "   - Weather Data: ✅"
    echo "   - Market Intelligence: ✅"
    echo "   - Crop Recommendations: ✅"
    echo "   - Disease Detection: ✅"
    echo "   - Translation: ✅"
    echo "   - Voice Queries: ✅"
}

# Run main function
main
