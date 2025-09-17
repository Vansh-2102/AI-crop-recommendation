from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import User, Farm, db
from integrations.external_apis import get_soil_api
import requests
import random
from datetime import datetime

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

def determine_soil_type(soil_data):
    """Determine soil type based on clay, sand, silt percentages"""
    clay = soil_data.get('clay', 30)
    sand = soil_data.get('sand', 40)
    silt = soil_data.get('silt', 30)
    
    if clay >= 40:
        return 'Clay'
    elif sand >= 70:
        return 'Sandy'
    elif silt >= 50:
        return 'Silty'
    elif 20 <= clay <= 40 and 20 <= sand <= 50 and 20 <= silt <= 50:
        return 'Loamy'
    else:
        return 'Mixed'

def determine_drainage(soil_data):
    """Determine drainage based on soil composition"""
    clay = soil_data.get('clay', 30)
    sand = soil_data.get('sand', 40)
    
    if sand >= 60:
        return 'Excellent'
    elif sand >= 40:
        return 'Good'
    elif clay >= 50:
        return 'Poor'
    else:
        return 'Moderate'

def determine_texture(soil_data):
    """Determine soil texture based on particle sizes"""
    clay = soil_data.get('clay', 30)
    sand = soil_data.get('sand', 40)
    
    if clay >= 40:
        return 'Fine'
    elif sand >= 60:
        return 'Coarse'
    else:
        return 'Medium'

def determine_fertility_rating(soil_data):
    """Determine fertility rating based on nutrients and organic matter"""
    organic_matter = soil_data.get('organic_matter', 2.0)
    nitrogen = soil_data.get('nitrogen', 0.2)
    phosphorus = soil_data.get('phosphorus', 20)
    potassium = soil_data.get('potassium', 150)
    
    score = 0
    if organic_matter >= 4.0:
        score += 1
    if nitrogen >= 0.3:
        score += 1
    if phosphorus >= 30:
        score += 1
    if potassium >= 200:
        score += 1
    
    if score >= 3:
        return 'High'
    elif score >= 2:
        return 'Medium'
    else:
        return 'Low'

def assess_nutrient_balance(nitrogen, phosphorus, potassium):
    """Assess overall nutrient balance"""
    score = 0
    if nitrogen >= 0.3:
        score += 1
    if phosphorus >= 30:
        score += 1
    if potassium >= 200:
        score += 1
    
    if score == 3:
        return 'excellent'
    elif score == 2:
        return 'good'
    elif score == 1:
        return 'fair'
    else:
        return 'poor'

def assess_organic_matter(organic_matter):
    """Assess organic matter status"""
    if organic_matter >= 5.0:
        return 'excellent'
    elif organic_matter >= 3.0:
        return 'good'
    elif organic_matter >= 2.0:
        return 'fair'
    else:
        return 'poor'

@soil_bp.route('/<float:lat>/<float:lng>', methods=['GET'])
@jwt_required()
def get_soil_data(lat, lng):
    """Get soil data for given coordinates"""
    try:
        # Validate coordinates
        if not (-90 <= lat <= 90) or not (-180 <= lng <= 180):
            return jsonify({'error': 'Invalid coordinates'}), 400
        
        # Try live soil API first, fallback to mock
        try:
            soil_api = get_soil_api()
            live_soil_data = soil_api.get_soil_data(lat, lng)
            
            # Convert live data to our format
            soil_data = {
                'ph': live_soil_data.get('ph', 6.5),
                'moisture': live_soil_data.get('soil_moisture', 0.3),
                'organic_matter': live_soil_data.get('organic_matter', 2.0),
                'nitrogen': live_soil_data.get('nitrogen', 0.2),
                'phosphorus': live_soil_data.get('phosphorus', 20),
                'potassium': live_soil_data.get('potassium', 150),
                'calcium': live_soil_data.get('calcium', 2000),
                'magnesium': live_soil_data.get('magnesium', 200),
                'clay': live_soil_data.get('clay', 30),
                'sand': live_soil_data.get('sand', 40),
                'silt': live_soil_data.get('silt', 30),
                'bulk_density': live_soil_data.get('bulk_density', 1.3),
                'cec': live_soil_data.get('cec', 15),
                'surface_temperature': live_soil_data.get('surface_temperature'),
                'soil_type': determine_soil_type(live_soil_data),
                'drainage': determine_drainage(live_soil_data),
                'texture': determine_texture(live_soil_data),
                'depth': 100.0,  # Default depth
                'fertility_rating': determine_fertility_rating(live_soil_data),
                'last_updated': datetime.now().isoformat()
            }
            source = 'live_soilgrids_api'
        except Exception as e:
            # Fallback to mock data
            soil_data = get_mock_soil_data(lat, lng)
            source = 'mock_soilgrids_api'
        
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
            'source': source,
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
    """Analyze soil data and provide recommendations based on user input"""
    try:
        data = request.json
        if not data or 'soil_data' not in data:
            return jsonify({'error': 'Soil data required'}), 400
        
        soil_data = data['soil_data']
        
        # Enhanced soil analysis with more detailed assessment
        ph = soil_data.get('ph', 7.0)
        moisture = soil_data.get('moisture', 0.3)
        organic_matter = soil_data.get('organic_matter', 2.0)
        nitrogen = soil_data.get('nitrogen', 0.2)
        phosphorus = soil_data.get('phosphorus', 20)
        potassium = soil_data.get('potassium', 150)
        clay = soil_data.get('clay', 30)
        sand = soil_data.get('sand', 40)
        silt = soil_data.get('silt', 30)
        
        # Determine soil properties from user input
        soil_type = determine_soil_type(soil_data)
        drainage = determine_drainage(soil_data)
        texture = determine_texture(soil_data)
        fertility_rating = determine_fertility_rating(soil_data)
        
        # Comprehensive analysis
        analysis = {
            'ph_status': 'optimal' if 6.0 <= ph <= 7.5 else 'needs_adjustment',
            'moisture_status': 'adequate' if 0.2 <= moisture <= 0.4 else 'needs_attention',
            'fertility_level': fertility_rating.lower(),
            'soil_type': soil_type,
            'drainage': drainage,
            'texture': texture,
            'nutrient_balance': assess_nutrient_balance(nitrogen, phosphorus, potassium),
            'organic_matter_status': assess_organic_matter(organic_matter),
            'recommendations': []
        }
        
        # pH recommendations
        if ph < 6.0:
            analysis['recommendations'].append({
                'type': 'ph_adjustment',
                'priority': 'high',
                'message': f'Soil pH is too acidic ({ph:.1f}). Consider adding lime to raise pH.',
                'action': 'Apply 2-4 tons of agricultural lime per acre',
                'target_ph': '6.5-7.0'
            })
        elif ph > 7.5:
            analysis['recommendations'].append({
                'type': 'ph_adjustment',
                'priority': 'medium',
                'message': f'Soil pH is too alkaline ({ph:.1f}). Consider adding sulfur or organic matter.',
                'action': 'Apply elemental sulfur or compost to lower pH',
                'target_ph': '6.5-7.0'
            })
        else:
            analysis['recommendations'].append({
                'type': 'ph_maintenance',
                'priority': 'low',
                'message': f'Soil pH is optimal ({ph:.1f}). Maintain current levels.',
                'action': 'Continue current pH management practices'
            })
        
        # Nutrient recommendations
        if nitrogen < 0.2:
            analysis['recommendations'].append({
                'type': 'nutrient_deficiency',
                'priority': 'high',
                'message': f'Low nitrogen levels detected ({nitrogen:.2f}%).',
                'action': 'Apply nitrogen-rich fertilizer (urea, ammonium nitrate) or organic matter',
                'target_range': '0.3-0.5%'
            })
        elif nitrogen > 0.5:
            analysis['recommendations'].append({
                'type': 'nutrient_excess',
                'priority': 'medium',
                'message': f'High nitrogen levels detected ({nitrogen:.2f}%).',
                'action': 'Reduce nitrogen application and focus on other nutrients'
            })
        
        if phosphorus < 20:
            analysis['recommendations'].append({
                'type': 'nutrient_deficiency',
                'priority': 'medium',
                'message': f'Low phosphorus levels detected ({phosphorus} ppm).',
                'action': 'Apply phosphorus-rich fertilizer (superphosphate, bone meal)',
                'target_range': '30-50 ppm'
            })
        elif phosphorus > 60:
            analysis['recommendations'].append({
                'type': 'nutrient_excess',
                'priority': 'low',
                'message': f'High phosphorus levels detected ({phosphorus} ppm).',
                'action': 'Reduce phosphorus application'
            })
        
        if potassium < 150:
            analysis['recommendations'].append({
                'type': 'nutrient_deficiency',
                'priority': 'medium',
                'message': f'Low potassium levels detected ({potassium} ppm).',
                'action': 'Apply potassium-rich fertilizer (potash, wood ash)',
                'target_range': '200-300 ppm'
            })
        elif potassium > 400:
            analysis['recommendations'].append({
                'type': 'nutrient_excess',
                'priority': 'low',
                'message': f'High potassium levels detected ({potassium} ppm).',
                'action': 'Reduce potassium application'
            })
        
        # Organic matter recommendations
        if organic_matter < 2.0:
            analysis['recommendations'].append({
                'type': 'organic_matter',
                'priority': 'high',
                'message': f'Low organic matter content ({organic_matter:.1f}%).',
                'action': 'Add compost, manure, or cover crops to improve soil structure',
                'target_range': '3-5%'
            })
        elif organic_matter > 8.0:
            analysis['recommendations'].append({
                'type': 'organic_matter',
                'priority': 'low',
                'message': f'Very high organic matter content ({organic_matter:.1f}%).',
                'action': 'Monitor for potential nutrient imbalances'
            })
        
        # Moisture recommendations
        if moisture < 0.2:
            analysis['recommendations'].append({
                'type': 'irrigation',
                'priority': 'high',
                'message': f'Soil moisture is low ({moisture:.1%}).',
                'action': 'Increase irrigation frequency or amount',
                'target_range': '20-40%'
            })
        elif moisture > 0.4:
            analysis['recommendations'].append({
                'type': 'drainage',
                'priority': 'medium',
                'message': f'Soil moisture is high ({moisture:.1%}).',
                'action': 'Improve drainage or reduce irrigation',
                'target_range': '20-40%'
            })
        
        # Soil type specific recommendations
        if soil_type == 'Clay':
            analysis['recommendations'].append({
                'type': 'soil_management',
                'priority': 'medium',
                'message': 'Clay soil detected. Focus on improving drainage and aeration.',
                'action': 'Add sand or organic matter, avoid over-tilling when wet'
            })
        elif soil_type == 'Sandy':
            analysis['recommendations'].append({
                'type': 'soil_management',
                'priority': 'medium',
                'message': 'Sandy soil detected. Focus on water retention and nutrient holding.',
                'action': 'Add organic matter and use frequent, light irrigation'
            })
        
        # Drainage recommendations
        if drainage == 'Poor':
            analysis['recommendations'].append({
                'type': 'drainage_improvement',
                'priority': 'high',
                'message': 'Poor drainage detected. This can lead to root problems.',
                'action': 'Install drainage systems or create raised beds'
            })
        
        return jsonify({
            'analysis': analysis,
            'soil_quality_score': calculate_soil_quality_score(soil_data),
            'summary': generate_soil_summary(analysis, soil_data),
            'timestamp': datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to analyze soil data', 'details': str(e)}), 500

def calculate_soil_quality_score(soil_data):
    """Calculate overall soil quality score (0-100) based on user input"""
    score = 0
    
    # pH score (0-25 points)
    ph = soil_data.get('ph', 7.0)
    if 6.0 <= ph <= 7.5:
        score += 25
    elif 5.5 <= ph <= 8.0:
        score += 15
    elif 5.0 <= ph <= 9.0:
        score += 10
    else:
        score += 5
    
    # Moisture score (0-20 points)
    moisture = soil_data.get('moisture', 0.3)
    if 0.2 <= moisture <= 0.4:
        score += 20
    elif 0.15 <= moisture <= 0.45:
        score += 15
    elif 0.1 <= moisture <= 0.5:
        score += 10
    else:
        score += 5
    
    # Organic matter score (0-20 points)
    organic_matter = soil_data.get('organic_matter', 2.0)
    if organic_matter >= 5.0:
        score += 20
    elif organic_matter >= 3.0:
        score += 15
    elif organic_matter >= 2.0:
        score += 10
    else:
        score += 5
    
    # Nutrient balance score (0-35 points)
    nitrogen = soil_data.get('nitrogen', 0.2)
    phosphorus = soil_data.get('phosphorus', 20)
    potassium = soil_data.get('potassium', 150)
    
    nutrient_score = 0
    if 0.2 <= nitrogen <= 0.5:
        nutrient_score += 1
    if 20 <= phosphorus <= 60:
        nutrient_score += 1
    if 150 <= potassium <= 400:
        nutrient_score += 1
    
    if nutrient_score == 3:
        score += 35
    elif nutrient_score == 2:
        score += 25
    elif nutrient_score == 1:
        score += 15
    else:
        score += 5
    
    return min(score, 100)

def generate_soil_summary(analysis, soil_data):
    """Generate a summary of soil analysis results"""
    ph = soil_data.get('ph', 7.0)
    fertility = analysis['fertility_level']
    soil_type = analysis['soil_type']
    quality_score = calculate_soil_quality_score(soil_data)
    
    if quality_score >= 80:
        overall_status = 'excellent'
        status_message = 'Your soil is in excellent condition for crop production.'
    elif quality_score >= 60:
        overall_status = 'good'
        status_message = 'Your soil is in good condition with some areas for improvement.'
    elif quality_score >= 40:
        overall_status = 'fair'
        status_message = 'Your soil needs attention to improve crop productivity.'
    else:
        overall_status = 'poor'
        status_message = 'Your soil requires significant improvement for optimal crop growth.'
    
    return {
        'overall_status': overall_status,
        'status_message': status_message,
        'quality_score': quality_score,
        'key_characteristics': {
            'ph_level': f"{ph:.1f}",
            'fertility': fertility,
            'soil_type': soil_type,
            'drainage': analysis['drainage']
        },
        'priority_actions': [rec for rec in analysis['recommendations'] if rec['priority'] == 'high'],
        'total_recommendations': len(analysis['recommendations'])
    }
