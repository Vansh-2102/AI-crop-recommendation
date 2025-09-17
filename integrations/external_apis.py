"""
External API integrations for real data sources
Replace mock implementations with actual API calls
"""

import requests
import os
from typing import Dict, Any, Optional, Tuple
import logging
import time

logger = logging.getLogger(__name__)

# Load environment variables from a .env file if present
try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass

class WeatherAPI:
    """OpenWeatherMap API integration"""
    
    def __init__(self):
        # Prefer env variable to avoid hardcoding keys
        self.api_key = os.getenv("OPENWEATHER_API_KEY")
        # Use HTTPS endpoint
        self.base_url = "https://api.openweathermap.org/data/2.5"
    
    def get_current_weather(self, location: str) -> Dict[str, Any]:
        """Get current weather data"""
        try:
            params = {
                'q': location,
                'appid': self.api_key,
                'units': 'metric'
            }
            response = requests.get(f"{self.base_url}/weather", params=params, timeout=15)
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
            response = requests.get(f"{self.base_url}/forecast", params=params, timeout=15)
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
        # Correct SoilGrids v2.0 base URL
        self.base_url = "https://rest.isric.org/soilgrids/v2.0"
        self.session = requests.Session()
        self.session.headers.update({
            'Accept': 'application/json',
            'User-Agent': 'AI-crop-recommendation/1.0 (+https://example.local)'
        })
        # Simple in-memory cache to reduce rate limits: {(lat,lng,prop): value}
        self._cache: Dict[Tuple[float, float, str], float] = {}
    
    def get_soil_data(self, lat: float, lng: float) -> Dict[str, Any]:
        """Get soil data from SoilGrids"""
        try:
            # Use only properties known to be available in SoilGrids v2.0
            # Some nutrients (nitrogen/phosphorus/potassium) are not provided directly.
            properties = ['phh2o', 'soc', 'clay', 'sand', 'silt', 'bdod', 'cec']
            
            soil_data = {}
            for prop in properties:
                try:
                    cache_key = (round(lat, 4), round(lng, 4), prop)
                    if cache_key in self._cache:
                        soil_data[prop] = self._cache[cache_key]
                        continue

                    url = f"{self.base_url}/properties/query"
                    params = {
                        'lon': lng,
                        'lat': lat,
                        'property': prop,
                        'depth': '0-5cm',
                        'value': 'mean'
                    }

                    # Basic retry with exponential backoff for 429/5xx
                    delay = 0.5
                    for attempt in range(4):
                        response = self.session.get(url, params=params, timeout=12)
                        if response.status_code in (429, 500, 502, 503, 504):
                            time.sleep(delay)
                            delay *= 2
                            continue
                        response.raise_for_status()
                        break

                    data = response.json()
                    parsed_value = self._parse_soilgrids_value(data)
                    if parsed_value is not None:
                        soil_data[prop] = parsed_value
                        self._cache[cache_key] = parsed_value
                except Exception as e:
                    logger.warning(f"Failed to get {prop}: {e}")
                    continue
            
            # Derive rough NPK estimates from SOC and texture if direct values unavailable
            soc = soil_data.get('soc', 2.0)
            clay_pct = soil_data.get('clay', 30)
            sand_pct = soil_data.get('sand', 40)
            # Very rough heuristics (placeholder):
            estimated_nitrogen = round(max(0.05, min(0.6, soc * 0.1)), 3)
            estimated_phosphorus = round(max(5, min(60, 10 + clay_pct * 0.3)), 1)
            estimated_potassium = round(max(50, min(400, 100 + (100 - sand_pct) * 3)), 0)

            # Convert to our format (baseline from SoilGrids)
            result = {
                'ph': soil_data.get('phh2o', 6.5),
                'organic_matter': soc,
                'nitrogen': estimated_nitrogen,
                'phosphorus': estimated_phosphorus,
                'potassium': estimated_potassium,
                'clay': clay_pct,
                'sand': sand_pct,
                'silt': soil_data.get('silt', 30),
                'bulk_density': soil_data.get('bdod', 1.3),
                'cec': soil_data.get('cec', 15)
            }

            # Optional enrichment: data.gov.in soil moisture dataset
            try:
                data_gov = DataGovInSoilMoistureAPI()
                if data_gov.resource_id:
                    moisture_data = data_gov.get_daily_soil_moisture(limit=1)
                    records = moisture_data.get('records') or moisture_data.get('data') or []
                    if records:
                        rec = records[0]
                        # Try common field names
                        for key in ('soil_moisture', 'moisture', 'vwc', 'sm'):
                            if key in rec and isinstance(rec[key], (int, float, str)):
                                try:
                                    result['soil_moisture'] = float(rec[key])
                                except Exception:
                                    pass
                                break
            except Exception as e:
                logger.debug(f"Soil moisture enrichment (data.gov.in) skipped: {e}")

            # Optional enrichment: Agromonitoring polygon soil
            try:
                agmo = AgromonitoringSoilAPI()
                polygon_id = os.getenv('AGROMONITORING_POLYGON_ID')
                if agmo.api_key and polygon_id:
                    ag = agmo.get_soil_by_polygon(polygon_id)
                    if isinstance(ag, dict):
                        if 'moisture' in ag and isinstance(ag['moisture'], (int, float)):
                            result['soil_moisture'] = ag['moisture']
                        if 't0' in ag and isinstance(ag['t0'], (int, float)):
                            result['surface_temperature'] = ag['t0']
            except Exception as e:
                logger.debug(f"Soil enrichment (agromonitoring) skipped: {e}")

            return result
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

    def _parse_soilgrids_value(self, data: Dict[str, Any]) -> Optional[float]:
        """Parse SoilGrids v2.0 response to a single float value.
        SoilGrids often returns under properties.layers[].depths[].values with
        statistics keys like Q0.5/mean. We'll try a few common paths.
        """
        try:
            # Newer structure: properties.layers[0].depths[0].values
            layers = data.get('properties', {}).get('layers', [])
            if layers:
                depths = layers[0].get('depths', [])
                if depths:
                    values = depths[0].get('values', {})
                    # Prefer mean, then median (Q0.5), else any numeric
                    for key in ('mean', 'Q0.5', 'M', 'median'):
                        if key in values and isinstance(values[key], (int, float)):
                            return float(values[key])
                    # Fallback: first numeric value
                    for v in values.values():
                        if isinstance(v, (int, float)):
                            return float(v)
            # Older simplified structure that code previously assumed
            if 'properties' in data and isinstance(data['properties'], list) and data['properties']:
                prop0 = data['properties'][0]
                if isinstance(prop0, dict):
                    for key in ('mean', 'Q0.5', 'value'):
                        if key in prop0 and isinstance(prop0[key], (int, float)):
                            return float(prop0[key])
        except Exception as e:
            logger.debug(f"SoilGrids parse error: {e}")
        return None

class DataGovInSoilMoistureAPI:
    """data.gov.in Soil Moisture dataset integration (requires resource id).
    Configure with env:
      - DATA_GOV_IN_API_KEY (defaults to widely shared demo key)
      - SOIL_MOISTURE_RESOURCE_ID (UUID of the dataset resource)
    """
    def __init__(self):
        self.api_key = os.getenv('DATA_GOV_IN_API_KEY', '579b464db66ec23bdd00000196ac63a1726549244a60dd461653af65')
        self.resource_id = os.getenv('SOIL_MOISTURE_RESOURCE_ID')
        self.base_url = 'https://api.data.gov.in/resource'

    def get_daily_soil_moisture(self, limit: int = 25, state: Optional[str] = None, district: Optional[str] = None, date: Optional[str] = None) -> Dict[str, Any]:
        try:
            if not self.resource_id:
                return {'configured': False, 'reason': 'SOIL_MOISTURE_RESOURCE_ID not set', 'records': []}
            params = {
                'api-key': self.api_key,
                'format': 'json',
                'limit': str(limit)
            }
            # Common field names vary by dataset; try generic filters
            if state:
                params['filters[state]'] = state
            if district:
                params['filters[district]'] = district
            if date:
                # Many datasets use date/observation_date fields
                params['filters[date]'] = date
            url = f"{self.base_url}/{self.resource_id}"
            resp = requests.get(url, params=params, timeout=20)
            resp.raise_for_status()
            data = resp.json()
            if isinstance(data, dict) and ('records' in data or 'data' in data):
                return data
            return {'configured': True, 'records': []}
        except Exception as e:
            logger.error(f"DataGovIn Soil Moisture API error: {e}")
            return {'configured': bool(self.resource_id), 'records': []}

class AgromonitoringSoilAPI:
    """Agromonitoring soil API integration (polygon-based).
    Configure with env AGROMONITORING_API_KEY and pass polygon id.
    """
    def __init__(self):
        self.api_key = os.getenv('AGROMONITORING_API_KEY')
        self.base_url = 'http://api.agromonitoring.com/agro/1.0'

    def get_soil_by_polygon(self, polygon_id: str) -> Dict[str, Any]:
        try:
            if not self.api_key:
                return {'error': 'AGROMONITORING_API_KEY not set'}
            url = f"{self.base_url}/soil"
            params = {'polyid': polygon_id, 'appid': self.api_key}
            r = requests.get(url, params=params, timeout=20)
            r.raise_for_status()
            return r.json()
        except Exception as e:
            logger.error(f"Agromonitoring soil API error: {e}")
            return {'error': 'failed', 'details': str(e)}
    
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
        # Prefer env vars; fallback to provided key if present
        self.api_key = os.getenv('DATA_GOV_IN_API_KEY', '579b464db66ec23bdd00000196ac63a1726549244a60dd461653af65')
        # Default to Agmarknet daily prices resource id (public)
        self.resource_id = os.getenv('AGMARKNET_RESOURCE_ID', '9ef84268-d588-465a-a308-a864a43d0070')
        # Correct API base for data.gov.in
        self.base_url = 'https://api.data.gov.in/resource'
    def get_crop_prices(self, crop: Optional[str] = None, limit: int = 25, state: Optional[str] = None, market: Optional[str] = None) -> Dict[str, Any]:
        """Get crop prices from data.gov.in Agmarknet resource.
        Filters: crop (commodity), state, market; returns JSON structure from API.
        """
        try:
            params = {
                'api-key': self.api_key,
                'format': 'json',
                'limit': str(limit)
            }

            # Build resource URL
            url = f"{self.base_url}/{self.resource_id}"

            # Map our filters to dataset fields (common Agmarknet fields)
            # commodity, state, district, market
            if crop:
                params['filters[commodity]'] = crop
            if state:
                params['filters[state]'] = state
            if market:
                params['filters[market]'] = market

            response = requests.get(url, params=params, timeout=20)
            response.raise_for_status()
            data = response.json()

            # Return as-is if structure looks correct; else fallback
            if isinstance(data, dict) and ('records' in data or 'data' in data):
                return data
            return self._get_fallback_market_data()
        except Exception as e:
            logger.error(f"Market API error: {e}")
            return self._get_fallback_market_data()
    
    def get_market_trends(self) -> Dict[str, Any]:
        """Get market trends and analysis.
        Note: data.gov.in does not expose a generic /trends endpoint. This
        method now returns a safe placeholder derived from recent prices.
        """
        try:
            sample = self.get_crop_prices(limit=10)
            records = sample.get('records') or sample.get('data') or []
            return {
                'trends': records[:10],
                'analysis': {
                    'count': len(records),
                    'source': 'data.gov.in'
                }
            }
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
