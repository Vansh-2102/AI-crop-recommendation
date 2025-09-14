"""
External API integrations for real data sources
Replace mock implementations with actual API calls
"""

import requests
import os
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

class WeatherAPI:
    """OpenWeatherMap API integration"""
    
    def __init__(self):
        self.api_key = os.getenv('OPENWEATHER_API_KEY')
        self.base_url = "http://api.openweathermap.org/data/2.5"
    
    def get_current_weather(self, location: str) -> Dict[str, Any]:
        """Get current weather data"""
        try:
            params = {
                'q': location,
                'appid': self.api_key,
                'units': 'metric'
            }
            response = requests.get(f"{self.base_url}/weather", params=params)
            response.raise_for_status()
            
            data = response.json()
            return {
                'temperature': data['main']['temp'],
                'humidity': data['main']['humidity'],
                'pressure': data['main']['pressure'],
                'wind_speed': data['wind']['speed'],
                'conditions': data['weather'][0]['description'],
                'location': data['name'],
                'country': data['sys']['country']
            }
        except Exception as e:
            logger.error(f"Weather API error: {e}")
            return self._get_fallback_weather()
    
    def get_forecast(self, location: str, days: int = 7) -> Dict[str, Any]:
        """Get weather forecast"""
        try:
            params = {
                'q': location,
                'appid': self.api_key,
                'units': 'metric',
                'cnt': days * 8  # 8 forecasts per day (3-hour intervals)
            }
            response = requests.get(f"{self.base_url}/forecast", params=params)
            response.raise_for_status()
            
            data = response.json()
            return {
                'forecast': [
                    {
                        'date': item['dt_txt'],
                        'temperature': item['main']['temp'],
                        'humidity': item['main']['humidity'],
                        'precipitation': item.get('rain', {}).get('3h', 0),
                        'conditions': item['weather'][0]['description']
                    }
                    for item in data['list']
                ]
            }
        except Exception as e:
            logger.error(f"Weather forecast API error: {e}")
            return {'forecast': []}
    
    def _get_fallback_weather(self) -> Dict[str, Any]:
        """Fallback weather data when API fails"""
        return {
            'temperature': 25,
            'humidity': 60,
            'pressure': 1013,
            'wind_speed': 5,
            'conditions': 'Clear sky',
            'location': 'Unknown',
            'country': 'Unknown'
        }

class SoilAPI:
    """SoilGrids API integration"""
    
    def __init__(self):
        self.base_url = "https://rest.isric.org/soilgrids/v2.0"
    
    def get_soil_data(self, lat: float, lng: float) -> Dict[str, Any]:
        """Get soil data from SoilGrids"""
        try:
            # SoilGrids properties
            properties = [
                'phh2o', 'soc', 'nitrogen', 'phosphorus', 'potassium',
                'clay', 'sand', 'silt', 'bdod', 'cec'
            ]
            
            soil_data = {}
            for prop in properties:
                try:
                    url = f"{self.base_url}/properties/query"
                    params = {
                        'lon': lng,
                        'lat': lat,
                        'property': prop,
                        'depth': '0-5cm',
                        'value': 'mean'
                    }
                    response = requests.get(url, params=params)
                    response.raise_for_status()
                    
                    data = response.json()
                    if 'properties' in data and data['properties']:
                        soil_data[prop] = data['properties'][0]['mean']
                except Exception as e:
                    logger.warning(f"Failed to get {prop}: {e}")
                    continue
            
            # Convert to our format
            return {
                'ph': soil_data.get('phh2o', 6.5),
                'organic_matter': soil_data.get('soc', 2.0),
                'nitrogen': soil_data.get('nitrogen', 0.2),
                'phosphorus': soil_data.get('phosphorus', 20),
                'potassium': soil_data.get('potassium', 150),
                'clay': soil_data.get('clay', 30),
                'sand': soil_data.get('sand', 40),
                'silt': soil_data.get('silt', 30),
                'bulk_density': soil_data.get('bdod', 1.3),
                'cec': soil_data.get('cec', 15)
            }
        except Exception as e:
            logger.error(f"Soil API error: {e}")
            return self._get_fallback_soil_data()
    
    def _get_fallback_soil_data(self) -> Dict[str, Any]:
        """Fallback soil data when API fails"""
        return {
            'ph': 6.5,
            'organic_matter': 2.0,
            'nitrogen': 0.2,
            'phosphorus': 20,
            'potassium': 150,
            'clay': 30,
            'sand': 40,
            'silt': 30,
            'bulk_density': 1.3,
            'cec': 15
        }

class MarketAPI:
    """Agricultural market data API integration"""
    
    def __init__(self):
        self.api_key = os.getenv('MARKET_API_KEY')
        self.base_url = os.getenv('MARKET_API_URL', 'https://api.agri-market.com')
    
    def get_crop_prices(self, crop: Optional[str] = None) -> Dict[str, Any]:
        """Get crop prices from market API"""
        try:
            headers = {'Authorization': f'Bearer {self.api_key}'} if self.api_key else {}
            
            if crop:
                url = f"{self.base_url}/prices/{crop}"
            else:
                url = f"{self.base_url}/prices"
            
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            
            return response.json()
        except Exception as e:
            logger.error(f"Market API error: {e}")
            return self._get_fallback_market_data()
    
    def get_market_trends(self) -> Dict[str, Any]:
        """Get market trends and analysis"""
        try:
            headers = {'Authorization': f'Bearer {self.api_key}'} if self.api_key else {}
            response = requests.get(f"{self.base_url}/trends", headers=headers)
            response.raise_for_status()
            
            return response.json()
        except Exception as e:
            logger.error(f"Market trends API error: {e}")
            return {'trends': [], 'analysis': {}}
    
    def _get_fallback_market_data(self) -> Dict[str, Any]:
        """Fallback market data when API fails"""
        return {
            'prices': [
                {
                    'crop': 'wheat',
                    'price': 2500,
                    'unit': 'per_quintal',
                    'change': 2.5
                }
            ],
            'trends': {
                'market_sentiment': 'neutral',
                'volatility': 'low'
            }
        }

class TranslationAPI:
    """Google Translate API integration"""
    
    def __init__(self):
        self.api_key = os.getenv('GOOGLE_TRANSLATE_API_KEY')
        self.base_url = "https://translation.googleapis.com/language/translate/v2"
    
    def translate_text(self, text: str, source_lang: str, target_lang: str) -> Dict[str, Any]:
        """Translate text using Google Translate"""
        try:
            params = {
                'key': self.api_key,
                'q': text,
                'source': source_lang,
                'target': target_lang,
                'format': 'text'
            }
            
            response = requests.post(self.base_url, params=params)
            response.raise_for_status()
            
            data = response.json()
            translated_text = data['data']['translations'][0]['translatedText']
            
            return {
                'translated_text': translated_text,
                'confidence': 0.95,
                'source_language': source_lang,
                'target_language': target_lang
            }
        except Exception as e:
            logger.error(f"Translation API error: {e}")
            return {
                'translated_text': f"[{target_lang.upper()}] {text}",
                'confidence': 0.5,
                'source_language': source_lang,
                'target_language': target_lang
            }
    
    def detect_language(self, text: str) -> Dict[str, Any]:
        """Detect language of text"""
        try:
            url = "https://translation.googleapis.com/language/translate/v2/detect"
            params = {
                'key': self.api_key,
                'q': text
            }
            
            response = requests.post(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            detection = data['data']['detections'][0][0]
            
            return {
                'detected_language': detection['language'],
                'confidence': detection['confidence']
            }
        except Exception as e:
            logger.error(f"Language detection API error: {e}")
            return {
                'detected_language': 'en',
                'confidence': 0.5
            }

class DiseaseDetectionAPI:
    """Plant disease detection API integration"""
    
    def __init__(self):
        self.api_key = os.getenv('DISEASE_DETECTION_API_KEY')
        self.base_url = os.getenv('DISEASE_DETECTION_API_URL', 'https://api.plant-disease.com')
    
    def detect_disease(self, image_data: str, crop_type: str) -> Dict[str, Any]:
        """Detect plant disease from image"""
        try:
            headers = {'Authorization': f'Bearer {self.api_key}'} if self.api_key else {}
            
            data = {
                'image': image_data,
                'crop_type': crop_type,
                'format': 'base64'
            }
            
            response = requests.post(f"{self.base_url}/detect", json=data, headers=headers)
            response.raise_for_status()
            
            result = response.json()
            return {
                'disease_name': result.get('disease', 'No disease detected'),
                'confidence': result.get('confidence', 0.8),
                'severity': result.get('severity', 'mild'),
                'treatment': result.get('treatment', 'Consult agricultural expert'),
                'prevention': result.get('prevention', 'Maintain good growing conditions')
            }
        except Exception as e:
            logger.error(f"Disease detection API error: {e}")
            return {
                'disease_name': 'Detection failed',
                'confidence': 0.0,
                'severity': 'unknown',
                'treatment': 'Unable to process image',
                'prevention': 'Please try again with a clearer image'
            }

# Factory function to get API instances
def get_weather_api() -> WeatherAPI:
    return WeatherAPI()

def get_soil_api() -> SoilAPI:
    return SoilAPI()

def get_market_api() -> MarketAPI:
    return MarketAPI()

def get_translation_api() -> TranslationAPI:
    return TranslationAPI()

def get_disease_detection_api() -> DiseaseDetectionAPI:
    return DiseaseDetectionAPI()
