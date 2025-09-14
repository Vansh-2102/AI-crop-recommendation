# 🔑 External API Keys Configuration Guide

## Required API Keys for Production

### 1. OpenWeatherMap API (Weather Data)
**Purpose**: Real-time weather data and forecasts

**Setup Steps**:
1. Go to [OpenWeatherMap](https://openweathermap.org/api)
2. Sign up for a free account
3. Get your API key from the dashboard
4. Add to environment: `OPENWEATHER_API_KEY=your_api_key_here`

**Free Tier**: 1,000 calls/day, 60 calls/minute

### 2. Google Translate API (Translation)
**Purpose**: Multilingual support for farmers

**Setup Steps**:
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Enable the Cloud Translation API
3. Create credentials (API key)
4. Add to environment: `GOOGLE_TRANSLATE_API_KEY=your_api_key_here`

**Free Tier**: 500,000 characters/month

### 3. Agricultural Market Data API
**Purpose**: Real crop prices and market trends

**Options**:
- **AgriMarket API**: https://agrimarket.com/api
- **Commodity API**: https://commodity-api.com
- **Custom Market Data**: Integrate with local agricultural boards

**Setup**:
1. Choose your preferred market data provider
2. Sign up and get API credentials
3. Add to environment: `MARKET_API_KEY=your_api_key_here`

### 4. Plant Disease Detection API
**Purpose**: AI-powered disease identification

**Options**:
- **PlantNet API**: https://plantnet.org/api
- **Plant.id API**: https://plant.id/api
- **Custom ML Model**: Deploy your own model

**Setup**:
1. Choose your preferred service
2. Get API credentials
3. Add to environment: `DISEASE_DETECTION_API_KEY=your_api_key_here`

## Environment Configuration

Update your `env.production` file:

```env
# External API Keys
OPENWEATHER_API_KEY=your_openweather_api_key_here
GOOGLE_TRANSLATE_API_KEY=your_google_translate_api_key_here
MARKET_API_KEY=your_market_api_key_here
DISEASE_DETECTION_API_KEY=your_disease_detection_api_key_here

# Optional: Additional APIs
SOILGRIDS_API_KEY=your_soilgrids_key_here
SENTINEL_API_KEY=your_sentinel_key_here
```

## Testing API Integration

After adding API keys, test the integration:

```bash
# Test weather API
python -c "
from integrations.external_apis import get_weather_api
api = get_weather_api()
data = api.get_current_weather('Delhi')
print('Weather:', data)
"

# Test translation API
python -c "
from integrations.external_apis import get_translation_api
api = get_translation_api()
result = api.translate_text('Hello', 'en', 'hi')
print('Translation:', result)
"
```

## Fallback Strategy

The system includes fallback mechanisms:
- If external APIs fail, mock data is used
- Graceful degradation ensures service availability
- Logging helps identify API issues

## Cost Optimization

1. **Caching**: Implement Redis caching for API responses
2. **Rate Limiting**: Respect API rate limits
3. **Batch Requests**: Combine multiple requests when possible
4. **Free Tiers**: Start with free tiers and scale up

## Security Best Practices

1. **Environment Variables**: Never commit API keys to code
2. **Rotation**: Regularly rotate API keys
3. **Monitoring**: Monitor API usage and costs
4. **Backup APIs**: Have multiple providers for critical services

