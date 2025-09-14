# 🚀 Crop Recommendation Platform - Complete Deployment Guide

## 📋 Overview

This guide provides comprehensive instructions for deploying and managing the AI-based crop recommendation platform in production.

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   Nginx         │    │   Backend API   │
│   (React)       │◄───┤   (Reverse      │◄───┤   (Flask)       │
│   Port: 3000    │    │    Proxy)       │    │   Port: 5000    │
└─────────────────┘    │   Port: 80/443  │    └─────────────────┘
                       └─────────────────┘             │
                                                       │
┌─────────────────┐    ┌─────────────────┐            │
│   PostgreSQL    │    │   Redis         │◄───────────┘
│   Port: 5432    │    │   Port: 6379    │
└─────────────────┘    └─────────────────┘
```

## 🚀 Quick Start

### 1. Development Setup

```bash
# Clone and setup
cd "D:\deep ai farm"

# Install dependencies
pip install -r requirements.txt

# Start development server
python app.py
```

### 2. Production Deployment

```bash
# Make deployment script executable
chmod +x scripts/deploy.sh

# Run deployment
./scripts/deploy.sh
```

## 📁 Project Structure

```
D:\deep ai farm\
├── app.py                          # Main Flask application
├── models.py                       # Database models
├── config.py                       # Configuration settings
├── requirements.txt                # Python dependencies
├── docker-compose.prod.yml         # Production Docker setup
├── nginx.conf                      # Nginx configuration
├── postman_collection.json         # API testing collection
├── test_api_comprehensive.py       # Comprehensive API tests
├── scripts/                        # Deployment scripts
│   ├── deploy.sh                   # Production deployment
│   └── test_production.py          # Production testing
├── integrations/                   # External API integrations
│   └── external_apis.py            # Real API implementations
├── ml_models/                      # Machine learning models
│   └── crop_recommendation_model.py # ML model implementations
├── frontend/                       # React frontend
│   ├── package.json               # Frontend dependencies
│   └── src/                       # React source code
└── routes/                        # API route modules
    ├── auth.py                    # Authentication
    ├── soil.py                    # Soil analysis
    ├── weather.py                 # Weather data
    ├── market.py                  # Market data
    ├── recommendations.py         # Crop recommendations
    ├── disease.py                 # Disease detection
    ├── translate.py               # Translation
    └── voice.py                   # Voice queries
```

## 🔧 Configuration

### Environment Variables

Create `.env.production` file:

```env
# Database
POSTGRES_DB=crop_recommendation
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_secure_password

# Security
SECRET_KEY=your-super-secret-key-change-in-production
JWT_SECRET_KEY=your-jwt-secret-key-change-in-production

# External APIs (optional)
OPENWEATHER_API_KEY=your_openweather_api_key
GOOGLE_TRANSLATE_API_KEY=your_google_translate_key
MARKET_API_KEY=your_market_api_key
DISEASE_DETECTION_API_KEY=your_disease_detection_key

# Monitoring
GRAFANA_PASSWORD=your_grafana_password
```

## 🧪 Testing

### 1. Development Testing

```bash
# Run comprehensive tests
python test_api_comprehensive.py

# Run specific test
python test_api.py
```

### 2. Production Testing

```bash
# Test production deployment
python scripts/test_production.py

# Test with custom URL
python scripts/test_production.py http://your-domain.com
```

### 3. Postman Testing

1. Import `postman_collection.json` into Postman
2. Set environment variables:
   - `base_url`: `http://localhost:5000`
   - `access_token`: (will be set automatically after login)

## 🌐 API Endpoints

### Authentication
- `POST /api/auth/register` - User registration
- `POST /api/auth/login` - User login
- `GET /api/auth/profile` - Get user profile
- `PUT /api/auth/profile` - Update user profile

### Soil Analysis
- `GET /api/soil/{lat}/{lng}` - Get soil data
- `GET /api/soil/farms` - Get farm soil data
- `POST /api/soil/analyze` - Analyze soil data

### Weather Data
- `GET /api/weather/{location}` - Get weather data
- `GET /api/weather/forecast/{location}` - Get weather forecast
- `GET /api/weather/agricultural-conditions/{location}` - Get agricultural conditions

### Market Data
- `GET /api/market/prices` - Get market prices
- `GET /api/market/prices/{crop}` - Get crop price details
- `GET /api/market/trends` - Get market trends
- `POST /api/market/recommendations` - Get market recommendations

### Crop Recommendations
- `POST /api/recommend/crops` - Get crop recommendations
- `GET /api/recommend/history` - Get recommendation history
- `POST /api/recommend/optimize` - Optimize recommendations

### Disease Detection
- `POST /api/disease/detect` - Detect plant diseases
- `GET /api/disease/diseases/{crop_type}` - Get crop diseases
- `GET /api/disease/prevention-guide` - Get prevention guide

### Translation
- `POST /api/translate/translate` - Translate text
- `GET /api/translate/languages` - Get supported languages
- `POST /api/translate/detect-language` - Detect language

### Voice Queries
- `POST /api/voice/query` - Process voice query
- `GET /api/voice/intents` - Get supported intents
- `POST /api/voice/conversation` - Start conversation

## 🐳 Docker Commands

### Development
```bash
# Start development environment
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### Production
```bash
# Deploy to production
docker-compose -f docker-compose.prod.yml up -d

# Scale services
docker-compose -f docker-compose.prod.yml up -d --scale api=3

# Update services
docker-compose -f docker-compose.prod.yml up -d --build
```

## 📊 Monitoring

### Grafana Dashboard
- URL: `http://localhost:3001`
- Username: `admin`
- Password: (set in environment variables)

### Prometheus Metrics
- URL: `http://localhost:9090`

### Application Logs
```bash
# View all logs
docker-compose logs -f

# View specific service logs
docker-compose logs -f api
docker-compose logs -f db
```

## 🔒 Security

### SSL/HTTPS Setup
1. Place SSL certificates in `ssl/` directory
2. Update `nginx.conf` to enable HTTPS
3. Restart nginx service

### Rate Limiting
- API endpoints: 10 requests/second
- Login endpoint: 5 requests/minute

### Security Headers
- X-Frame-Options: DENY
- X-Content-Type-Options: nosniff
- X-XSS-Protection: 1; mode=block
- Strict-Transport-Security: enabled

## 🚀 Scaling

### Horizontal Scaling
```bash
# Scale API service
docker-compose -f docker-compose.prod.yml up -d --scale api=5

# Scale with load balancer
# Add nginx upstream configuration for multiple API instances
```

### Database Scaling
- Use PostgreSQL read replicas
- Implement connection pooling
- Add Redis clustering

## 🔧 Maintenance

### Database Backup
```bash
# Backup database
docker-compose exec db pg_dump -U postgres crop_recommendation > backup.sql

# Restore database
docker-compose exec -T db psql -U postgres crop_recommendation < backup.sql
```

### Log Rotation
```bash
# Configure logrotate for application logs
# Logs are stored in ./logs/ directory
```

### Updates
```bash
# Update application
git pull origin main
docker-compose -f docker-compose.prod.yml up -d --build

# Update dependencies
pip install -r requirements.txt --upgrade
```

## 🆘 Troubleshooting

### Common Issues

1. **Database Connection Failed**
   - Check PostgreSQL service status
   - Verify connection string
   - Check firewall settings

2. **API Not Responding**
   - Check API service logs
   - Verify port availability
   - Check nginx configuration

3. **Frontend Not Loading**
   - Check React build
   - Verify nginx proxy settings
   - Check browser console for errors

### Debug Commands
```bash
# Check service status
docker-compose ps

# Check service health
docker-compose exec api curl http://localhost:5000/api/health

# View detailed logs
docker-compose logs --tail=100 api

# Access service shell
docker-compose exec api bash
```

## 📞 Support

For issues and questions:
1. Check the logs first
2. Review this documentation
3. Run the test suite
4. Check GitHub issues

## 🎉 Success!

Your AI-based crop recommendation platform is now fully deployed and ready for production use!

### Quick Verification
```bash
# Test all endpoints
python test_api_comprehensive.py

# Check production status
python scripts/test_production.py
```

**All systems are operational! 🚀**
