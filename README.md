# AI-Based Crop Recommendation Platform

A comprehensive backend system for an AI-powered agricultural platform that provides intelligent crop recommendations, disease detection, weather analysis, and market insights.

## Features

- **User Authentication**: JWT-based secure authentication system
- **Soil Analysis**: Integration with soil data APIs for comprehensive soil analysis
- **Weather Integration**: Real-time weather data and agricultural conditions
- **Market Intelligence**: Crop price tracking and market trend analysis
- **Crop Recommendations**: AI-powered crop selection based on multiple factors
- **Disease Detection**: Computer vision-based plant disease identification
- **Multilingual Support**: Translation services for multiple languages
- **Voice Queries**: Natural language processing for voice-based interactions

## Technology Stack

- **Backend**: Flask (Python)
- **Database**: PostgreSQL with SQLAlchemy ORM
- **Authentication**: JWT (JSON Web Tokens)
- **API**: RESTful API design
- **Serialization**: Marshmallow
- **CORS**: Cross-Origin Resource Sharing support

## Installation

### Prerequisites

- Python 3.8 or higher
- PostgreSQL 12 or higher
- pip (Python package manager)

### Setup Instructions

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd deep-ai-farm
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up PostgreSQL database**
   ```bash
   # Create database
   createdb crop_recommendation
   
   # Or using psql
   psql -U postgres
   CREATE DATABASE crop_recommendation;
   ```

5. **Configure environment variables**
   Create a `.env` file in the root directory:
   ```env
   SECRET_KEY=your-secret-key-here
   JWT_SECRET_KEY=your-jwt-secret-here
   DATABASE_URL=postgresql://username:password@localhost/crop_recommendation
   FLASK_ENV=development
   ```

6. **Initialize the database**
   ```bash
   python app.py
   # The database tables will be created automatically on first run
   ```

7. **Run the application**
   ```bash
   python app.py
   ```

The API will be available at `http://localhost:5000`

## API Endpoints

### Authentication
- `POST /api/auth/register` - User registration
- `POST /api/auth/login` - User login
- `GET /api/auth/profile` - Get user profile
- `PUT /api/auth/profile` - Update user profile
- `POST /api/auth/change-password` - Change password

### Soil Data
- `GET /api/soil/{lat}/{lng}` - Get soil data for coordinates
- `GET /api/soil/farms` - Get soil data for user's farms
- `POST /api/soil/analyze` - Analyze soil data and get recommendations

### Weather Data
- `GET /api/weather/{location}` - Get weather data for location
- `GET /api/weather/forecast/{location}` - Get weather forecast
- `GET /api/weather/alerts/{location}` - Get weather alerts
- `GET /api/weather/agricultural-conditions/{location}` - Get agricultural conditions

### Market Data
- `GET /api/market/prices` - Get current market prices
- `GET /api/market/prices/{crop}` - Get detailed crop price information
- `GET /api/market/trends` - Get market trends and analysis
- `POST /api/market/recommendations` - Get market-based recommendations

### Crop Recommendations
- `POST /api/recommend/crops` - Get crop recommendations
- `GET /api/recommend/history` - Get recommendation history
- `POST /api/recommend/optimize` - Optimize recommendations with constraints

### Disease Detection
- `POST /api/disease/detect` - Detect plant diseases from images
- `POST /api/disease/detect-batch` - Batch disease detection
- `GET /api/disease/diseases/{crop_type}` - Get diseases for crop type
- `GET /api/disease/prevention-guide` - Get disease prevention guide

### Translation
- `POST /api/translate/translate` - Translate text
- `POST /api/translate/translate-batch` - Batch translation
- `GET /api/translate/languages` - Get supported languages
- `POST /api/translate/detect-language` - Detect text language
- `GET /api/translate/agricultural-terms` - Get agricultural terms
- `POST /api/translate/translate-recommendations` - Translate recommendations

### Voice Queries
- `POST /api/voice/query` - Process voice query
- `POST /api/voice/query-batch` - Process batch voice queries
- `GET /api/voice/intents` - Get supported intents
- `POST /api/voice/conversation` - Start conversation
- `POST /api/voice/conversation/{session_id}` - Continue conversation

## Database Schema

### Users Table
- `id` (Primary Key)
- `name` (String)
- `email` (String, Unique)
- `password_hash` (String)
- `location` (String)
- `farm_size` (Float)
- `preferred_language` (String)
- `created_at` (DateTime)
- `updated_at` (DateTime)

### Farms Table
- `id` (Primary Key)
- `user_id` (Foreign Key)
- `name` (String)
- `location` (String)
- `size` (Float)
- `soil_data` (JSON)
- `latitude` (Float)
- `longitude` (Float)
- `created_at` (DateTime)
- `updated_at` (DateTime)

### Plantings Table
- `id` (Primary Key)
- `farm_id` (Foreign Key)
- `crop` (String)
- `planting_date` (Date)
- `harvest_date` (Date)
- `yield_amount` (Float)
- `profit` (Float)
- `conditions` (JSON)
- `status` (String)
- `created_at` (DateTime)
- `updated_at` (DateTime)

### Recommendations Table
- `id` (Primary Key)
- `user_id` (Foreign Key)
- `location` (String)
- `soil_data` (JSON)
- `weather_data` (JSON)
- `market_data` (JSON)
- `recommendations` (JSON)
- `confidence_score` (Float)
- `created_at` (DateTime)

## Usage Examples

### User Registration
```bash
curl -X POST http://localhost:5000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "name": "John Doe",
    "email": "john@example.com",
    "password": "securepassword",
    "location": "Punjab, India",
    "farm_size": 10.5,
    "preferred_language": "en"
  }'
```

### Get Crop Recommendations
```bash
curl -X POST http://localhost:5000/api/recommend/crops \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
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
  }'
```

### Detect Plant Disease
```bash
curl -X POST http://localhost:5000/api/disease/detect \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "image_data": "base64_encoded_image_data",
    "crop_type": "wheat",
    "location": "Punjab, India"
  }'
```

## Configuration

The application uses environment variables for configuration. Key variables include:

- `SECRET_KEY`: Flask secret key
- `JWT_SECRET_KEY`: JWT signing key
- `DATABASE_URL`: PostgreSQL connection string
- `FLASK_ENV`: Environment (development/production)

## Development

### Running Tests
```bash
python -m pytest tests/
```

### Code Formatting
```bash
black .
isort .
```

### Database Migrations
```bash
# Create migration
flask db migrate -m "Description"

# Apply migration
flask db upgrade
```

## Deployment

### Using Gunicorn
```bash
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

### Using Docker
```bash
docker build -t crop-recommendation-api .
docker run -p 5000:5000 crop-recommendation-api
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

This project is licensed under the MIT License.

## Support

For support and questions, please contact the development team or create an issue in the repository.
