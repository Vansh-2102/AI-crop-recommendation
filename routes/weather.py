from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
import random
from datetime import datetime, timedelta
import os
from integrations.external_apis import get_weather_api

weather_bp = Blueprint('weather', __name__)

def get_mock_weather_data(location):
    """Generate mock weather data for a location"""
    # Simulate seasonal variations
    current_month = datetime.now().month
    
    # Base temperatures by season
    if current_month in [12, 1, 2]:  # Winter
        base_temp = random.uniform(5, 20)
        precipitation_chance = 0.3
    elif current_month in [3, 4, 5]:  # Spring
        base_temp = random.uniform(15, 25)
        precipitation_chance = 0.4
    elif current_month in [6, 7, 8]:  # Summer
        base_temp = random.uniform(25, 35)
        precipitation_chance = 0.2
    else:  # Fall
        base_temp = random.uniform(10, 25)
        precipitation_chance = 0.35
    
    # Current weather
    current_temp = round(base_temp + random.uniform(-5, 5), 1)
    humidity = round(random.uniform(40, 80), 1)
    wind_speed = round(random.uniform(5, 25), 1)
    precipitation = round(random.uniform(0, 10) if random.random() < precipitation_chance else 0, 1)
    
    # 7-day forecast
    forecast = []
    for i in range(7):
        date = datetime.now() + timedelta(days=i)
        day_temp = round(base_temp + random.uniform(-8, 8), 1)
        night_temp = round(day_temp - random.uniform(5, 15), 1)
        day_precip = round(random.uniform(0, 15) if random.random() < precipitation_chance else 0, 1)
        
        forecast.append({
            'date': date.strftime('%Y-%m-%d'),
            'day_temperature': day_temp,
            'night_temperature': night_temp,
            'precipitation': day_precip,
            'humidity': round(random.uniform(30, 90), 1),
            'wind_speed': round(random.uniform(3, 30), 1),
            'conditions': random.choice(['Sunny', 'Partly Cloudy', 'Cloudy', 'Rainy', 'Thunderstorm'])
        })
    
    return {
        'location': location,
        'current': {
            'temperature': current_temp,
            'humidity': humidity,
            'wind_speed': wind_speed,
            'precipitation': precipitation,
            'conditions': random.choice(['Sunny', 'Partly Cloudy', 'Cloudy', 'Rainy']),
            'uv_index': random.randint(1, 10),
            'pressure': round(random.uniform(1000, 1030), 1)
        },
        'forecast': forecast,
        'alerts': generate_weather_alerts(current_temp, precipitation, wind_speed),
        'last_updated': datetime.now().isoformat()
    }


def get_live_weather_bundle(location: str):
    """Fetch live weather (and forecast if available) and map to our schema."""
    api = get_weather_api()
    if not getattr(api, 'api_key', None):
        return None
    current = api.get_current_weather(location)
    # current is a flat dict from integrations.external_apis. Map to our structure.
    now_iso = datetime.now().isoformat()
    current_block = {
        'temperature': current.get('temperature'),
        'humidity': current.get('humidity'),
        'wind_speed': current.get('wind_speed'),
        'precipitation': current.get('precipitation', 0),
        'conditions': current.get('conditions'),
        'uv_index': random.randint(1, 10),  # not provided by API
        'pressure': current.get('pressure')
    }
    alerts = generate_weather_alerts(
        current_block['temperature'] if current_block['temperature'] is not None else 0,
        current_block['precipitation'],
        current_block['wind_speed'] if current_block['wind_speed'] is not None else 0
    )
    # Try to get forecast; if it fails, provide empty list gracefully
    try:
        forecast_api = api.get_forecast(location, days=7)
        forecast_list = [
            {
                'date': item.get('date'),
                'day_temperature': item.get('temperature'),
                'night_temperature': max(item.get('temperature', 0) - 7, -50),
                'precipitation': item.get('precipitation', 0),
                'humidity': item.get('humidity'),
                'wind_speed': item.get('wind_speed', random.uniform(3, 30)),
                'conditions': item.get('conditions')
            }
            for item in forecast_api.get('forecast', [])
        ]
    except Exception:
        forecast_list = []
    return {
        'location': current.get('location') or location,
        'current': current_block,
        'forecast': forecast_list,
        'alerts': alerts,
        'last_updated': now_iso,
        'source_location': current.get('location'),
        'source_country': current.get('country')
    }

def generate_weather_alerts(temp, precip, wind):
    """Generate weather alerts based on conditions"""
    alerts = []
    
    if temp > 35:
        alerts.append({
            'type': 'heat_warning',
            'severity': 'high',
            'message': 'Extreme heat warning. Take precautions for crops and livestock.',
            'recommendation': 'Increase irrigation and provide shade if possible.'
        })
    elif temp < 0:
        alerts.append({
            'type': 'frost_warning',
            'severity': 'high',
            'message': 'Frost warning. Protect sensitive crops.',
            'recommendation': 'Cover crops or use frost protection methods.'
        })
    
    if precip > 20:
        alerts.append({
            'type': 'heavy_rain',
            'severity': 'medium',
            'message': 'Heavy rainfall expected. Monitor drainage.',
            'recommendation': 'Ensure proper drainage and avoid overwatering.'
        })
    
    if wind > 20:
        alerts.append({
            'type': 'high_wind',
            'severity': 'medium',
            'message': 'High wind conditions. Secure loose items.',
            'recommendation': 'Check crop supports and greenhouse structures.'
        })
    
    return alerts

@weather_bp.route('/<location>', methods=['GET'])
@jwt_required()
def get_weather_data(location):
    """Get weather data for a specific location"""
    try:
        # Validate location parameter
        if not location or len(location.strip()) == 0:
            return jsonify({'error': 'Location parameter is required'}), 400

        # Prefer live weather when API key is present; fallback to mock
        live_bundle = get_live_weather_bundle(location)
        if live_bundle:
            return jsonify({
                'weather': {
                    'location': live_bundle['location'],
                    'current': live_bundle['current'],
                    'forecast': live_bundle['forecast'],
                    'alerts': live_bundle['alerts'],
                    'last_updated': live_bundle['last_updated']
                },
                'source': 'openweathermap',
                'timestamp': live_bundle['last_updated']
            }), 200

        # Fallback to mock data
        weather_data = get_mock_weather_data(location)
        return jsonify({
            'weather': weather_data,
            'source': 'mock_weather_api',
            'timestamp': weather_data['last_updated']
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to fetch weather data', 'details': str(e)}), 500

@weather_bp.route('/forecast/<location>', methods=['GET'])
@jwt_required()
def get_weather_forecast(location):
    """Get extended weather forecast for a location"""
    try:
        days = request.args.get('days', 7, type=int)
        if days < 1 or days > 30:
            return jsonify({'error': 'Days parameter must be between 1 and 30'}), 400

        # Try live forecast first
        live_bundle = get_live_weather_bundle(location)
        if live_bundle and live_bundle['forecast']:
            return jsonify({
                'location': live_bundle['location'],
                'forecast_days': days,
                'forecast': live_bundle['forecast'][:days],
                'source': 'openweathermap',
                'timestamp': live_bundle['last_updated']
            }), 200

        # Fallback to mock
        weather_data = get_mock_weather_data(location)
        weather_data['forecast'] = weather_data['forecast'][:days]
        return jsonify({
            'location': location,
            'forecast_days': days,
            'forecast': weather_data['forecast'],
            'source': 'mock_weather_api',
            'timestamp': weather_data['last_updated']
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to fetch weather forecast', 'details': str(e)}), 500

@weather_bp.route('/alerts/<location>', methods=['GET'])
@jwt_required()
def get_weather_alerts(location):
    """Get weather alerts for a location"""
    try:
        # Prefer live current conditions for alert generation
        live_bundle = get_live_weather_bundle(location)
        if live_bundle:
            return jsonify({
                'location': live_bundle['location'],
                'alerts': live_bundle['alerts'],
                'alert_count': len(live_bundle['alerts']),
                'timestamp': live_bundle['last_updated']
            }), 200
        weather_data = get_mock_weather_data(location)
        
        return jsonify({
            'location': location,
            'alerts': weather_data['alerts'],
            'alert_count': len(weather_data['alerts']),
            'timestamp': weather_data['last_updated']
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to fetch weather alerts', 'details': str(e)}), 500

@weather_bp.route('/agricultural-conditions/<location>', methods=['GET'])
@jwt_required()
def get_agricultural_conditions(location):
    """Get agricultural-specific weather conditions"""
    try:
        live_bundle = get_live_weather_bundle(location)
        if live_bundle:
            current = live_bundle['current']
            last_updated = live_bundle['last_updated']
            source = 'openweathermap'
        else:
            weather_data = get_mock_weather_data(location)
            current = weather_data['current']
            last_updated = weather_data['last_updated']
            source = 'mock_weather_api'
        
        # Calculate agricultural indices
        growing_degree_days = max(0, current['temperature'] - 10)  # Base temperature of 10°C
        chill_hours = max(0, 10 - current['temperature']) if current['temperature'] < 10 else 0
        
        # Determine growing conditions
        if current['temperature'] < 5:
            growing_condition = 'dormant'
        elif current['temperature'] < 15:
            growing_condition = 'slow_growth'
        elif current['temperature'] < 30:
            growing_condition = 'optimal'
        else:
            growing_condition = 'stress'
        
        # Irrigation recommendations
        if current['precipitation'] > 5:
            irrigation_need = 'none'
        elif current['precipitation'] > 2:
            irrigation_need = 'light'
        elif current['humidity'] < 50:
            irrigation_need = 'moderate'
        else:
            irrigation_need = 'heavy'
        
        agricultural_conditions = {
            'location': location,
            'growing_degree_days': round(growing_degree_days, 1),
            'chill_hours': round(chill_hours, 1),
            'growing_condition': growing_condition,
            'irrigation_need': irrigation_need,
            'soil_moisture_index': round(random.uniform(0.2, 0.8), 2),
            'pest_risk': 'low' if current['temperature'] < 20 else 'medium' if current['temperature'] < 30 else 'high',
            'disease_risk': 'low' if current['humidity'] < 60 else 'medium' if current['humidity'] < 80 else 'high',
            'harvest_readiness': 'not_ready' if current['temperature'] < 15 else 'ready' if current['temperature'] > 25 else 'monitor',
            'recommendations': generate_agricultural_recommendations(current, growing_condition, irrigation_need)
        }
        
        return jsonify({
            'agricultural_conditions': agricultural_conditions,
            'weather_summary': current,
            'source': source,
            'timestamp': last_updated
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to fetch agricultural conditions', 'details': str(e)}), 500

def generate_agricultural_recommendations(current_weather, growing_condition, irrigation_need):
    """Generate agricultural recommendations based on weather conditions"""
    recommendations = []
    
    if growing_condition == 'dormant':
        recommendations.append({
            'type': 'seasonal',
            'priority': 'low',
            'message': 'Crops are in dormant phase due to low temperatures.',
            'action': 'Focus on soil preparation and planning for next season.'
        })
    elif growing_condition == 'slow_growth':
        recommendations.append({
            'type': 'growth',
            'priority': 'medium',
            'message': 'Slow growth due to cool temperatures.',
            'action': 'Consider using row covers or greenhouses to increase temperature.'
        })
    elif growing_condition == 'stress':
        recommendations.append({
            'type': 'heat_stress',
            'priority': 'high',
            'message': 'High temperatures may cause heat stress.',
            'action': 'Increase irrigation frequency and provide shade if possible.'
        })
    
    if irrigation_need == 'heavy':
        recommendations.append({
            'type': 'irrigation',
            'priority': 'high',
            'message': 'High irrigation need due to low precipitation.',
            'action': 'Schedule regular irrigation sessions.'
        })
    elif irrigation_need == 'none':
        recommendations.append({
            'type': 'irrigation',
            'priority': 'low',
            'message': 'Adequate moisture from recent precipitation.',
            'action': 'Monitor soil moisture and avoid overwatering.'
        })
    
    if current_weather['humidity'] > 80:
        recommendations.append({
            'type': 'disease_prevention',
            'priority': 'medium',
            'message': 'High humidity increases disease risk.',
            'action': 'Ensure good air circulation and consider fungicide applications.'
        })
    
    return recommendations
