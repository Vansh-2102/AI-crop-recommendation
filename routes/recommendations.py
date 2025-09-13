from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import User, Recommendation, db
import random
from datetime import datetime

recommendations_bp = Blueprint('recommendations', __name__)

# Mock crop recommendation data
CROP_RECOMMENDATIONS = {
    'wheat': {
        'optimal_ph': (6.0, 7.5),
        'optimal_temp': (15, 25),
        'water_requirement': 'medium',
        'soil_type': ['loamy', 'clay'],
        'season': 'winter',
        'yield_potential': 'high',
        'market_demand': 'high',
        'profit_margin': 'medium'
    },
    'rice': {
        'optimal_ph': (5.5, 7.0),
        'optimal_temp': (20, 35),
        'water_requirement': 'high',
        'soil_type': ['clay', 'silty'],
        'season': 'monsoon',
        'yield_potential': 'high',
        'market_demand': 'high',
        'profit_margin': 'medium'
    },
    'corn': {
        'optimal_ph': (6.0, 7.0),
        'optimal_temp': (18, 27),
        'water_requirement': 'medium',
        'soil_type': ['loamy', 'sandy'],
        'season': 'summer',
        'yield_potential': 'high',
        'market_demand': 'high',
        'profit_margin': 'medium'
    },
    'sugarcane': {
        'optimal_ph': (6.0, 7.5),
        'optimal_temp': (20, 30),
        'water_requirement': 'high',
        'soil_type': ['loamy', 'clay'],
        'season': 'year_round',
        'yield_potential': 'very_high',
        'market_demand': 'medium',
        'profit_margin': 'high'
    },
    'cotton': {
        'optimal_ph': (5.8, 8.0),
        'optimal_temp': (21, 30),
        'water_requirement': 'medium',
        'soil_type': ['loamy', 'sandy'],
        'season': 'summer',
        'yield_potential': 'medium',
        'market_demand': 'high',
        'profit_margin': 'high'
    },
    'soybean': {
        'optimal_ph': (6.0, 7.0),
        'optimal_temp': (20, 30),
        'water_requirement': 'medium',
        'soil_type': ['loamy', 'sandy'],
        'season': 'monsoon',
        'yield_potential': 'medium',
        'market_demand': 'high',
        'profit_margin': 'medium'
    },
    'potato': {
        'optimal_ph': (4.8, 5.5),
        'optimal_temp': (15, 20),
        'water_requirement': 'medium',
        'soil_type': ['sandy', 'loamy'],
        'season': 'winter',
        'yield_potential': 'high',
        'market_demand': 'high',
        'profit_margin': 'medium'
    },
    'tomato': {
        'optimal_ph': (6.0, 6.8),
        'optimal_temp': (18, 25),
        'water_requirement': 'medium',
        'soil_type': ['loamy', 'sandy'],
        'season': 'year_round',
        'yield_potential': 'high',
        'market_demand': 'high',
        'profit_margin': 'high'
    },
    'mango': {
        'optimal_ph': (5.5, 7.5),
        'optimal_temp': (24, 30),
        'water_requirement': 'medium',
        'soil_type': ['loamy', 'sandy'],
        'season': 'summer',
        'yield_potential': 'high',
        'market_demand': 'high',
        'profit_margin': 'very_high'
    },
    'banana': {
        'optimal_ph': (6.0, 7.5),
        'optimal_temp': (26, 30),
        'water_requirement': 'high',
        'soil_type': ['loamy', 'clay'],
        'season': 'year_round',
        'yield_potential': 'very_high',
        'market_demand': 'high',
        'profit_margin': 'high'
    }
}

def calculate_crop_suitability(crop, soil_data, weather_data, market_data):
    """Calculate suitability score for a crop based on various factors"""
    score = 0
    factors = []
    
    # Soil pH suitability
    ph = soil_data.get('ph', 7.0)
    optimal_ph_range = CROP_RECOMMENDATIONS[crop]['optimal_ph']
    if optimal_ph_range[0] <= ph <= optimal_ph_range[1]:
        score += 25
        factors.append('Optimal soil pH')
    elif abs(ph - optimal_ph_range[0]) <= 0.5 or abs(ph - optimal_ph_range[1]) <= 0.5:
        score += 15
        factors.append('Good soil pH')
    else:
        score += 5
        factors.append('Suboptimal soil pH')
    
    # Temperature suitability
    temp = weather_data.get('temperature', 25)
    optimal_temp_range = CROP_RECOMMENDATIONS[crop]['optimal_temp']
    if optimal_temp_range[0] <= temp <= optimal_temp_range[1]:
        score += 20
        factors.append('Optimal temperature')
    elif abs(temp - optimal_temp_range[0]) <= 3 or abs(temp - optimal_temp_range[1]) <= 3:
        score += 10
        factors.append('Acceptable temperature')
    else:
        score += 0
        factors.append('Suboptimal temperature')
    
    # Soil type suitability
    soil_type = soil_data.get('soil_type', 'loamy').lower()
    if soil_type in CROP_RECOMMENDATIONS[crop]['soil_type']:
        score += 15
        factors.append('Suitable soil type')
    else:
        score += 5
        factors.append('Less suitable soil type')
    
    # Water requirement match
    moisture = soil_data.get('moisture', 0.3)
    water_req = CROP_RECOMMENDATIONS[crop]['water_requirement']
    if water_req == 'high' and moisture > 0.3:
        score += 15
        factors.append('Good moisture for high water requirement')
    elif water_req == 'medium' and 0.2 <= moisture <= 0.4:
        score += 15
        factors.append('Good moisture for medium water requirement')
    elif water_req == 'low' and moisture < 0.3:
        score += 15
        factors.append('Good moisture for low water requirement')
    else:
        score += 5
        factors.append('Moisture may need adjustment')
    
    # Market demand
    crop_market_data = next((item for item in market_data if item['crop'] == crop), None)
    if crop_market_data:
        if crop_market_data['demand_level'] == 'high':
            score += 15
            factors.append('High market demand')
        elif crop_market_data['demand_level'] == 'medium':
            score += 10
            factors.append('Medium market demand')
        else:
            score += 5
            factors.append('Low market demand')
        
        # Price trend
        if crop_market_data['market_trend'] == 'rising':
            score += 10
            factors.append('Rising prices')
        elif crop_market_data['market_trend'] == 'stable':
            score += 5
            factors.append('Stable prices')
    
    return min(score, 100), factors

@recommendations_bp.route('/crops', methods=['POST'])
@jwt_required()
def get_crop_recommendations():
    """Get crop recommendations based on soil, weather, and market data"""
    try:
        data = request.json
        if not data:
            return jsonify({'error': 'Request data required'}), 400
        
        # Extract parameters
        location = data.get('location', '')
        soil_data = data.get('soil_data', {})
        weather_data = data.get('weather_data', {})
        market_data = data.get('market_data', [])
        farm_size = data.get('farm_size', 1)
        budget = data.get('budget', 10000)
        preferences = data.get('preferences', {})
        
        # If no market data provided, generate mock data
        if not market_data:
            from routes.market import get_mock_market_data
            market_data = get_mock_market_data()
        
        # Calculate recommendations for each crop
        recommendations = []
        
        for crop in CROP_RECOMMENDATIONS.keys():
            suitability_score, factors = calculate_crop_suitability(
                crop, soil_data, weather_data, market_data
            )
            
            if suitability_score > 30:  # Only recommend crops with reasonable suitability
                # Get market data for this crop
                crop_market = next((item for item in market_data if item['crop'] == crop), None)
                
                # Calculate estimated profit
                estimated_yield = estimate_yield(crop, farm_size, suitability_score)
                estimated_cost = estimate_cost(crop, farm_size)
                estimated_revenue = estimated_yield * (crop_market['current_price'] if crop_market else 100)
                estimated_profit = estimated_revenue - estimated_cost
                
                # Calculate confidence score
                confidence = calculate_confidence(suitability_score, factors, crop_market)
                
                recommendations.append({
                    'crop': crop,
                    'suitability_score': suitability_score,
                    'confidence': confidence,
                    'estimated_yield': estimated_yield,
                    'estimated_cost': estimated_cost,
                    'estimated_revenue': estimated_revenue,
                    'estimated_profit': estimated_profit,
                    'profit_margin': round((estimated_profit / estimated_revenue) * 100, 2) if estimated_revenue > 0 else 0,
                    'factors': factors,
                    'market_data': crop_market,
                    'growing_requirements': CROP_RECOMMENDATIONS[crop],
                    'recommendation': get_recommendation_text(suitability_score, confidence, factors)
                })
        
        # Sort by suitability score and confidence
        recommendations.sort(key=lambda x: (x['suitability_score'] + x['confidence']) / 2, reverse=True)
        
        # Filter by budget if specified
        if budget > 0:
            recommendations = [rec for rec in recommendations if rec['estimated_cost'] <= budget * 1.2]
        
        # Store recommendation in database
        current_user_id = int(get_jwt_identity())
        recommendation_record = Recommendation(
            user_id=current_user_id,
            location=location,
            soil_data=soil_data,
            weather_data=weather_data,
            market_data=market_data,
            recommendations=recommendations[:10],  # Store top 10
            confidence_score=recommendations[0]['confidence'] if recommendations else 0
        )
        
        try:
            db.session.add(recommendation_record)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            # Continue even if database storage fails
        
        return jsonify({
            'recommendations': recommendations[:10],  # Return top 10
            'total_crops_analyzed': len(CROP_RECOMMENDATIONS),
            'filters_applied': {
                'location': location,
                'farm_size': farm_size,
                'budget': budget,
                'preferences': preferences
            },
            'timestamp': datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to generate crop recommendations', 'details': str(e)}), 500

@recommendations_bp.route('/history', methods=['GET'])
@jwt_required()
def get_recommendation_history():
    """Get user's recommendation history"""
    try:
        current_user_id = int(get_jwt_identity())
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        
        recommendations = Recommendation.query.filter_by(user_id=current_user_id)\
            .order_by(Recommendation.created_at.desc())\
            .paginate(page=page, per_page=per_page, error_out=False)
        
        return jsonify({
            'recommendations': [rec.to_dict() for rec in recommendations.items],
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': recommendations.total,
                'pages': recommendations.pages,
                'has_next': recommendations.has_next,
                'has_prev': recommendations.has_prev
            },
            'timestamp': datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to fetch recommendation history', 'details': str(e)}), 500

@recommendations_bp.route('/optimize', methods=['POST'])
@jwt_required()
def optimize_recommendations():
    """Optimize recommendations based on additional constraints"""
    try:
        data = request.json
        if not data:
            return jsonify({'error': 'Request data required'}), 400
        
        # Get base recommendations
        base_recommendations = data.get('recommendations', [])
        constraints = data.get('constraints', {})
        
        # Apply constraints
        optimized = []
        
        for rec in base_recommendations:
            score_adjustment = 0
            adjustments = []
            
            # Labor constraint
            if 'labor_availability' in constraints:
                labor = constraints['labor_availability']
                if labor == 'low' and rec['crop'] in ['sugarcane', 'cotton']:  # Labor intensive crops
                    score_adjustment -= 20
                    adjustments.append('High labor requirement')
                elif labor == 'high':
                    score_adjustment += 10
                    adjustments.append('Good labor availability')
            
            # Water constraint
            if 'water_availability' in constraints:
                water = constraints['water_availability']
                water_req = rec['growing_requirements']['water_requirement']
                if water == 'low' and water_req == 'high':
                    score_adjustment -= 25
                    adjustments.append('High water requirement')
                elif water == 'high' and water_req == 'high':
                    score_adjustment += 15
                    adjustments.append('Good water availability')
            
            # Equipment constraint
            if 'equipment_available' in constraints:
                equipment = constraints['equipment_available']
                if equipment == 'basic' and rec['crop'] in ['sugarcane', 'cotton']:
                    score_adjustment -= 15
                    adjustments.append('Requires specialized equipment')
                elif equipment == 'advanced':
                    score_adjustment += 10
                    adjustments.append('Good equipment availability')
            
            # Market access constraint
            if 'market_access' in constraints:
                market_access = constraints['market_access']
                if market_access == 'poor' and rec['market_data']['demand_level'] == 'high':
                    score_adjustment -= 10
                    adjustments.append('High demand but poor market access')
                elif market_access == 'good':
                    score_adjustment += 5
                    adjustments.append('Good market access')
            
            # Apply adjustments
            rec['suitability_score'] = max(0, min(100, rec['suitability_score'] + score_adjustment))
            rec['optimization_adjustments'] = adjustments
            rec['optimized_score'] = rec['suitability_score']
            
            if rec['suitability_score'] > 20:  # Only include viable recommendations
                optimized.append(rec)
        
        # Re-sort by optimized score
        optimized.sort(key=lambda x: x['optimized_score'], reverse=True)
        
        return jsonify({
            'optimized_recommendations': optimized,
            'constraints_applied': constraints,
            'optimization_summary': {
                'total_recommendations': len(base_recommendations),
                'viable_after_optimization': len(optimized),
                'average_score_improvement': sum(rec.get('optimization_adjustments', []) for rec in optimized)
            },
            'timestamp': datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to optimize recommendations', 'details': str(e)}), 500

def estimate_yield(crop, farm_size, suitability_score):
    """Estimate crop yield based on farm size and suitability"""
    base_yield_per_acre = {
        'wheat': 3000, 'rice': 4000, 'corn': 3500, 'sugarcane': 80000,
        'cotton': 500, 'soybean': 2000, 'potato': 25000, 'tomato': 50000,
        'mango': 8000, 'banana': 30000
    }
    
    base_yield = base_yield_per_acre.get(crop, 2000)
    suitability_factor = suitability_score / 100
    return round(base_yield * farm_size * suitability_factor, 2)

def estimate_cost(crop, farm_size):
    """Estimate farming cost for a crop"""
    base_cost_per_acre = {
        'wheat': 15000, 'rice': 20000, 'corn': 18000, 'sugarcane': 25000,
        'cotton': 22000, 'soybean': 16000, 'potato': 30000, 'tomato': 35000,
        'mango': 40000, 'banana': 25000
    }
    
    base_cost = base_cost_per_acre.get(crop, 20000)
    return round(base_cost * farm_size, 2)

def calculate_confidence(suitability_score, factors, market_data):
    """Calculate confidence score for recommendation"""
    confidence = suitability_score * 0.6  # Base confidence from suitability
    
    # Factor in market data
    if market_data:
        if market_data['demand_level'] == 'high':
            confidence += 10
        elif market_data['demand_level'] == 'medium':
            confidence += 5
        
        if market_data['market_trend'] == 'rising':
            confidence += 5
    
    # Factor in number of positive factors
    positive_factors = len([f for f in factors if 'Optimal' in f or 'Good' in f or 'Suitable' in f])
    confidence += positive_factors * 2
    
    return min(confidence, 100)

def get_recommendation_text(suitability_score, confidence, factors):
    """Generate human-readable recommendation text"""
    if suitability_score >= 80 and confidence >= 80:
        return f"Highly recommended crop with {suitability_score}% suitability and {confidence}% confidence. {', '.join(factors[:3])}."
    elif suitability_score >= 60 and confidence >= 60:
        return f"Good choice with {suitability_score}% suitability and {confidence}% confidence. {', '.join(factors[:2])}."
    elif suitability_score >= 40:
        return f"Moderate recommendation with {suitability_score}% suitability. Consider soil improvements. {', '.join(factors[:2])}."
    else:
        return f"Not recommended due to low suitability ({suitability_score}%). Requires significant soil/condition improvements."
