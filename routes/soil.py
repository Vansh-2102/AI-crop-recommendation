from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import User, Farm, db
import requests
import random

soil_bp = Blueprint('soil', __name__)

def get_mock_soil_data(latitude, longitude):
    """Generate mock soil data based on coordinates"""
    # Simulate different soil types based on coordinates
    base_ph = 6.5 + (latitude * 0.01) + (longitude * 0.005)
    base_moisture = 0.3 + (latitude * 0.001) + (longitude * 0.002)
    
    soil_data = {
        'ph': round(base_ph + random.uniform(-0.5, 0.5), 2),
        'moisture': round(base_moisture + random.uniform(-0.1, 0.1), 3),
        'organic_matter': round(random.uniform(2.0, 8.0), 2),
        'nitrogen': round(random.uniform(0.1, 0.5), 3),
        'phosphorus': round(random.uniform(10, 50), 1),
        'potassium': round(random.uniform(100, 400), 1),
        'calcium': round(random.uniform(1000, 5000), 1),
        'magnesium': round(random.uniform(100, 500), 1),
        'soil_type': random.choice(['Clay', 'Sandy', 'Loamy', 'Silty']),
        'drainage': random.choice(['Poor', 'Moderate', 'Good', 'Excellent']),
        'texture': random.choice(['Fine', 'Medium', 'Coarse']),
        'depth': round(random.uniform(30, 150), 1),
        'fertility_rating': random.choice(['Low', 'Medium', 'High']),
        'last_updated': '2024-01-15T10:30:00Z'
    }
    
    return soil_data

@soil_bp.route('/<float:lat>/<float:lng>', methods=['GET'])
@jwt_required()
def get_soil_data(lat, lng):
    """Get soil data for given coordinates"""
    try:
        # Validate coordinates
        if not (-90 <= lat <= 90) or not (-180 <= lng <= 180):
            return jsonify({'error': 'Invalid coordinates'}), 400
        
        # Get mock soil data
        soil_data = get_mock_soil_data(lat, lng)
        
        # Store soil data in user's farm if they have one at this location
        current_user_id = int(get_jwt_identity())
        user = User.query.get(current_user_id)
        
        if user:
            # Check if user has a farm near these coordinates (within 0.01 degrees)
            farm = Farm.query.filter(
                Farm.user_id == current_user_id,
                Farm.latitude.between(lat - 0.01, lat + 0.01),
                Farm.longitude.between(lng - 0.01, lng + 0.01)
            ).first()
            
            if farm:
                farm.set_soil_data(soil_data)
                db.session.commit()
        
        return jsonify({
            'coordinates': {'latitude': lat, 'longitude': lng},
            'soil_data': soil_data,
            'source': 'mock_soilgrids_api',
            'timestamp': soil_data['last_updated']
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to fetch soil data', 'details': str(e)}), 500

@soil_bp.route('/farms', methods=['GET'])
@jwt_required()
def get_farm_soil_data():
    """Get soil data for all user's farms"""
    try:
        current_user_id = int(get_jwt_identity())
        farms = Farm.query.filter_by(user_id=current_user_id).all()
        
        farm_soil_data = []
        for farm in farms:
            if farm.latitude and farm.longitude:
                soil_data = get_mock_soil_data(farm.latitude, farm.longitude)
                farm_soil_data.append({
                    'farm_id': farm.id,
                    'farm_name': farm.name,
                    'location': farm.location,
                    'coordinates': {
                        'latitude': farm.latitude,
                        'longitude': farm.longitude
                    },
                    'soil_data': soil_data
                })
        
        return jsonify({
            'farms': farm_soil_data,
            'count': len(farm_soil_data)
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to fetch farm soil data', 'details': str(e)}), 500

@soil_bp.route('/analyze', methods=['POST'])
@jwt_required()
def analyze_soil():
    """Analyze soil data and provide recommendations"""
    try:
        data = request.json
        if not data or 'soil_data' not in data:
            return jsonify({'error': 'Soil data required'}), 400
        
        soil_data = data['soil_data']
        
        # Basic soil analysis
        analysis = {
            'ph_status': 'optimal' if 6.0 <= soil_data.get('ph', 0) <= 7.5 else 'needs_adjustment',
            'moisture_status': 'adequate' if 0.2 <= soil_data.get('moisture', 0) <= 0.4 else 'needs_attention',
            'fertility_level': soil_data.get('fertility_rating', 'Medium').lower(),
            'recommendations': []
        }
        
        # pH recommendations
        ph = soil_data.get('ph', 7.0)
        if ph < 6.0:
            analysis['recommendations'].append({
                'type': 'ph_adjustment',
                'priority': 'high',
                'message': 'Soil pH is too acidic. Consider adding lime to raise pH.',
                'action': 'Apply 2-4 tons of agricultural lime per acre'
            })
        elif ph > 7.5:
            analysis['recommendations'].append({
                'type': 'ph_adjustment',
                'priority': 'medium',
                'message': 'Soil pH is too alkaline. Consider adding sulfur or organic matter.',
                'action': 'Apply elemental sulfur or compost to lower pH'
            })
        
        # Nutrient recommendations
        nitrogen = soil_data.get('nitrogen', 0.3)
        phosphorus = soil_data.get('phosphorus', 30)
        potassium = soil_data.get('potassium', 200)
        
        if nitrogen < 0.2:
            analysis['recommendations'].append({
                'type': 'nutrient_deficiency',
                'priority': 'high',
                'message': 'Low nitrogen levels detected.',
                'action': 'Apply nitrogen-rich fertilizer or organic matter'
            })
        
        if phosphorus < 20:
            analysis['recommendations'].append({
                'type': 'nutrient_deficiency',
                'priority': 'medium',
                'message': 'Low phosphorus levels detected.',
                'action': 'Apply phosphorus-rich fertilizer or bone meal'
            })
        
        if potassium < 150:
            analysis['recommendations'].append({
                'type': 'nutrient_deficiency',
                'priority': 'medium',
                'message': 'Low potassium levels detected.',
                'action': 'Apply potassium-rich fertilizer or wood ash'
            })
        
        # Moisture recommendations
        moisture = soil_data.get('moisture', 0.3)
        if moisture < 0.2:
            analysis['recommendations'].append({
                'type': 'irrigation',
                'priority': 'high',
                'message': 'Soil moisture is low.',
                'action': 'Increase irrigation frequency or amount'
            })
        elif moisture > 0.4:
            analysis['recommendations'].append({
                'type': 'drainage',
                'priority': 'medium',
                'message': 'Soil moisture is high.',
                'action': 'Improve drainage or reduce irrigation'
            })
        
        return jsonify({
            'analysis': analysis,
            'soil_quality_score': calculate_soil_quality_score(soil_data),
            'timestamp': '2024-01-15T10:30:00Z'
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to analyze soil data', 'details': str(e)}), 500

def calculate_soil_quality_score(soil_data):
    """Calculate overall soil quality score (0-100)"""
    score = 0
    
    # pH score (0-25 points)
    ph = soil_data.get('ph', 7.0)
    if 6.0 <= ph <= 7.5:
        score += 25
    elif 5.5 <= ph <= 8.0:
        score += 15
    else:
        score += 5
    
    # Moisture score (0-20 points)
    moisture = soil_data.get('moisture', 0.3)
    if 0.2 <= moisture <= 0.4:
        score += 20
    elif 0.15 <= moisture <= 0.45:
        score += 15
    else:
        score += 5
    
    # Organic matter score (0-20 points)
    organic_matter = soil_data.get('organic_matter', 4.0)
    if organic_matter >= 5.0:
        score += 20
    elif organic_matter >= 3.0:
        score += 15
    else:
        score += 10
    
    # Nutrient score (0-35 points)
    nitrogen = soil_data.get('nitrogen', 0.3)
    phosphorus = soil_data.get('phosphorus', 30)
    potassium = soil_data.get('potassium', 200)
    
    if nitrogen >= 0.3 and phosphorus >= 30 and potassium >= 200:
        score += 35
    elif nitrogen >= 0.2 and phosphorus >= 20 and potassium >= 150:
        score += 25
    else:
        score += 15
    
    return min(score, 100)
