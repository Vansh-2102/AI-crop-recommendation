from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
import random
from datetime import datetime, timedelta

market_bp = Blueprint('market', __name__)

# Mock crop data with realistic price ranges
CROP_DATA = {
    'wheat': {'base_price': 250, 'unit': 'per_quintal', 'seasonality': 'winter'},
    'rice': {'base_price': 300, 'unit': 'per_quintal', 'seasonality': 'monsoon'},
    'corn': {'base_price': 200, 'unit': 'per_quintal', 'seasonality': 'summer'},
    'sugarcane': {'base_price': 350, 'unit': 'per_ton', 'seasonality': 'year_round'},
    'cotton': {'base_price': 6000, 'unit': 'per_quintal', 'seasonality': 'summer'},
    'soybean': {'base_price': 400, 'unit': 'per_quintal', 'seasonality': 'monsoon'},
    'potato': {'base_price': 20, 'unit': 'per_kg', 'seasonality': 'winter'},
    'tomato': {'base_price': 30, 'unit': 'per_kg', 'seasonality': 'year_round'},
    'onion': {'base_price': 25, 'unit': 'per_kg', 'seasonality': 'winter'},
    'chili': {'base_price': 80, 'unit': 'per_kg', 'seasonality': 'year_round'},
    'mango': {'base_price': 40, 'unit': 'per_kg', 'seasonality': 'summer'},
    'banana': {'base_price': 25, 'unit': 'per_kg', 'seasonality': 'year_round'},
    'apple': {'base_price': 60, 'unit': 'per_kg', 'seasonality': 'winter'},
    'grapes': {'base_price': 50, 'unit': 'per_kg', 'seasonality': 'summer'},
    'pomegranate': {'base_price': 80, 'unit': 'per_kg', 'seasonality': 'winter'}
}

def get_mock_market_data():
    """Generate mock market data for all crops"""
    current_date = datetime.now()
    market_data = []
    
    for crop, data in CROP_DATA.items():
        # Add seasonal price variations
        seasonal_multiplier = get_seasonal_multiplier(data['seasonality'], current_date.month)
        
        # Add random price fluctuations
        fluctuation = random.uniform(0.8, 1.3)
        
        # Calculate current price
        current_price = round(data['base_price'] * seasonal_multiplier * fluctuation, 2)
        
        # Calculate price change from previous day
        price_change = round(random.uniform(-0.1, 0.1) * current_price, 2)
        previous_price = round(current_price - price_change, 2)
        
        # Calculate demand level
        demand_score = random.uniform(0.3, 1.0)
        if demand_score > 0.8:
            demand_level = 'high'
        elif demand_score > 0.5:
            demand_level = 'medium'
        else:
            demand_level = 'low'
        
        # Calculate supply level (inverse of demand for simplicity)
        supply_level = 'low' if demand_level == 'high' else 'high' if demand_level == 'low' else 'medium'
        
        market_data.append({
            'crop': crop,
            'current_price': current_price,
            'previous_price': previous_price,
            'price_change': price_change,
            'price_change_percent': round((price_change / previous_price) * 100, 2),
            'unit': data['unit'],
            'demand_level': demand_level,
            'supply_level': supply_level,
            'demand_score': round(demand_score, 2),
            'market_trend': 'rising' if price_change > 0 else 'falling' if price_change < 0 else 'stable',
            'seasonality': data['seasonality'],
            'last_updated': current_date.isoformat()
        })
    
    return market_data

def get_seasonal_multiplier(seasonality, current_month):
    """Calculate seasonal price multiplier based on crop seasonality"""
    if seasonality == 'winter':
        if current_month in [12, 1, 2]:
            return 1.2  # Higher prices in winter
        elif current_month in [6, 7, 8]:
            return 0.8  # Lower prices in summer
        else:
            return 1.0
    elif seasonality == 'summer':
        if current_month in [6, 7, 8]:
            return 1.2  # Higher prices in summer
        elif current_month in [12, 1, 2]:
            return 0.8  # Lower prices in winter
        else:
            return 1.0
    elif seasonality == 'monsoon':
        if current_month in [6, 7, 8, 9]:
            return 1.1  # Slightly higher in monsoon
        else:
            return 1.0
    else:  # year_round
        return 1.0

@market_bp.route('/prices', methods=['GET'])
@jwt_required()
def get_market_prices():
    """Get current market prices for all crops"""
    try:
        crop_filter = request.args.get('crop')
        sort_by = request.args.get('sort', 'crop')  # crop, price, change
        order = request.args.get('order', 'asc')  # asc, desc
        
        market_data = get_mock_market_data()
        
        # Filter by crop if specified
        if crop_filter:
            market_data = [item for item in market_data if crop_filter.lower() in item['crop'].lower()]
        
        # Sort data
        if sort_by == 'price':
            market_data.sort(key=lambda x: x['current_price'], reverse=(order == 'desc'))
        elif sort_by == 'change':
            market_data.sort(key=lambda x: x['price_change_percent'], reverse=(order == 'desc'))
        else:  # sort by crop name
            market_data.sort(key=lambda x: x['crop'], reverse=(order == 'desc'))
        
        return jsonify({
            'market_data': market_data,
            'total_crops': len(market_data),
            'filters_applied': {
                'crop': crop_filter,
                'sort_by': sort_by,
                'order': order
            },
            'timestamp': datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to fetch market prices', 'details': str(e)}), 500

@market_bp.route('/prices/<crop>', methods=['GET'])
@jwt_required()
def get_crop_price(crop):
    """Get detailed price information for a specific crop"""
    try:
        if crop.lower() not in CROP_DATA:
            return jsonify({'error': 'Crop not found'}), 404
        
        market_data = get_mock_market_data()
        crop_data = next(item for item in market_data if item['crop'] == crop.lower())
        
        # Generate historical price data (last 30 days)
        historical_prices = []
        base_price = crop_data['current_price']
        
        for i in range(30):
            date = datetime.now() - timedelta(days=i)
            # Add some variation to historical prices
            variation = random.uniform(0.9, 1.1)
            historical_price = round(base_price * variation, 2)
            
            historical_prices.append({
                'date': date.strftime('%Y-%m-%d'),
                'price': historical_price
            })
        
        # Reverse to get chronological order
        historical_prices.reverse()
        
        # Generate price forecast (next 7 days)
        forecast_prices = []
        for i in range(1, 8):
            date = datetime.now() + timedelta(days=i)
            # Add trend-based variation
            trend_factor = 1 + (crop_data['price_change_percent'] / 100) * (i / 7)
            variation = random.uniform(0.95, 1.05)
            forecast_price = round(base_price * trend_factor * variation, 2)
            
            forecast_prices.append({
                'date': date.strftime('%Y-%m-%d'),
                'price': forecast_price
            })
        
        return jsonify({
            'crop': crop.lower(),
            'current_data': crop_data,
            'historical_prices': historical_prices,
            'price_forecast': forecast_prices,
            'analysis': {
                'avg_price_30d': round(sum(p['price'] for p in historical_prices) / len(historical_prices), 2),
                'price_volatility': calculate_volatility(historical_prices),
                'trend_direction': 'upward' if crop_data['price_change'] > 0 else 'downward' if crop_data['price_change'] < 0 else 'stable',
                'recommendation': get_price_recommendation(crop_data)
            },
            'timestamp': datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to fetch crop price data', 'details': str(e)}), 500

@market_bp.route('/trends', methods=['GET'])
@jwt_required()
def get_market_trends():
    """Get overall market trends and analysis"""
    try:
        market_data = get_mock_market_data()
        
        # Calculate market statistics
        total_crops = len(market_data)
        rising_crops = len([item for item in market_data if item['price_change'] > 0])
        falling_crops = len([item for item in market_data if item['price_change'] < 0])
        stable_crops = total_crops - rising_crops - falling_crops
        
        # Find top performers
        top_gainers = sorted(market_data, key=lambda x: x['price_change_percent'], reverse=True)[:5]
        top_losers = sorted(market_data, key=lambda x: x['price_change_percent'])[:5]
        
        # High demand crops
        high_demand_crops = [item for item in market_data if item['demand_level'] == 'high']
        
        # Market insights
        insights = generate_market_insights(market_data)
        
        return jsonify({
            'market_summary': {
                'total_crops': total_crops,
                'rising_crops': rising_crops,
                'falling_crops': falling_crops,
                'stable_crops': stable_crops,
                'market_sentiment': 'positive' if rising_crops > falling_crops else 'negative' if falling_crops > rising_crops else 'neutral'
            },
            'top_performers': {
                'gainers': top_gainers,
                'losers': top_losers
            },
            'high_demand_crops': high_demand_crops,
            'market_insights': insights,
            'timestamp': datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to fetch market trends', 'details': str(e)}), 500

@market_bp.route('/recommendations', methods=['POST'])
@jwt_required()
def get_market_recommendations():
    """Get market-based recommendations for crop selection"""
    try:
        data = request.json
        if not data:
            return jsonify({'error': 'Request data required'}), 400
        
        location = data.get('location', '')
        farm_size = data.get('farm_size', 1)  # in acres
        budget = data.get('budget', 10000)  # in currency
        season = data.get('season', 'current')
        
        market_data = get_mock_market_data()
        
        # Filter crops by season if specified
        if season != 'current':
            market_data = [item for item in market_data if item['seasonality'] == season]
        
        # Calculate recommendations based on market conditions
        recommendations = []
        
        for crop_data in market_data:
            score = 0
            reasons = []
            
            # Price trend score
            if crop_data['market_trend'] == 'rising':
                score += 30
                reasons.append('Price is rising')
            elif crop_data['market_trend'] == 'stable':
                score += 20
                reasons.append('Price is stable')
            
            # Demand score
            if crop_data['demand_level'] == 'high':
                score += 25
                reasons.append('High demand')
            elif crop_data['demand_level'] == 'medium':
                score += 15
                reasons.append('Medium demand')
            
            # Supply score (low supply = higher price potential)
            if crop_data['supply_level'] == 'low':
                score += 20
                reasons.append('Low supply')
            elif crop_data['supply_level'] == 'medium':
                score += 10
                reasons.append('Medium supply')
            
            # Budget consideration
            estimated_cost = crop_data['current_price'] * (farm_size * 10)  # Rough estimate
            if estimated_cost <= budget:
                score += 15
                reasons.append('Within budget')
            elif estimated_cost <= budget * 1.5:
                score += 5
                reasons.append('Slightly over budget')
            
            if score > 0:
                recommendations.append({
                    'crop': crop_data['crop'],
                    'score': score,
                    'current_price': crop_data['current_price'],
                    'unit': crop_data['unit'],
                    'estimated_cost': round(estimated_cost, 2),
                    'reasons': reasons,
                    'market_trend': crop_data['market_trend'],
                    'demand_level': crop_data['demand_level']
                })
        
        # Sort by score
        recommendations.sort(key=lambda x: x['score'], reverse=True)
        
        return jsonify({
            'recommendations': recommendations[:10],  # Top 10
            'filters': {
                'location': location,
                'farm_size': farm_size,
                'budget': budget,
                'season': season
            },
            'timestamp': datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to generate market recommendations', 'details': str(e)}), 500

def calculate_volatility(historical_prices):
    """Calculate price volatility from historical data"""
    if len(historical_prices) < 2:
        return 0
    
    prices = [p['price'] for p in historical_prices]
    mean_price = sum(prices) / len(prices)
    variance = sum((price - mean_price) ** 2 for price in prices) / len(prices)
    return round((variance ** 0.5) / mean_price * 100, 2)

def get_price_recommendation(crop_data):
    """Generate price-based recommendation"""
    if crop_data['market_trend'] == 'rising' and crop_data['demand_level'] == 'high':
        return 'Consider selling soon - prices are rising with high demand'
    elif crop_data['market_trend'] == 'falling' and crop_data['demand_level'] == 'low':
        return 'Consider waiting - prices are falling with low demand'
    elif crop_data['demand_level'] == 'high':
        return 'Good time to sell - high demand in market'
    else:
        return 'Monitor market conditions - mixed signals'

def generate_market_insights(market_data):
    """Generate market insights and analysis"""
    insights = []
    
    # Overall market sentiment
    rising_count = len([item for item in market_data if item['price_change'] > 0])
    total_count = len(market_data)
    
    if rising_count / total_count > 0.6:
        insights.append({
            'type': 'market_sentiment',
            'message': 'Market is showing positive sentiment with majority of crops showing price increases',
            'impact': 'positive'
        })
    elif rising_count / total_count < 0.4:
        insights.append({
            'type': 'market_sentiment',
            'message': 'Market is showing negative sentiment with majority of crops showing price decreases',
            'impact': 'negative'
        })
    
    # High demand crops
    high_demand = [item for item in market_data if item['demand_level'] == 'high']
    if len(high_demand) > 3:
        insights.append({
            'type': 'demand_analysis',
            'message': f'Multiple crops ({len(high_demand)}) showing high demand - good selling opportunity',
            'impact': 'positive'
        })
    
    # Price volatility
    volatile_crops = [item for item in market_data if abs(item['price_change_percent']) > 5]
    if len(volatile_crops) > 5:
        insights.append({
            'type': 'volatility_warning',
            'message': 'High price volatility detected in multiple crops - exercise caution',
            'impact': 'warning'
        })
    
    return insights
