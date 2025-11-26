from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
import random
import re
import hashlib
from datetime import datetime

# Import live/mock helpers from existing feature routes to ground answers in real data
try:
    # Weather helpers
    from routes.weather import get_live_weather_bundle, get_mock_weather_data
except Exception:  # pragma: no cover - fallback if module path changes
    get_live_weather_bundle = None
    get_mock_weather_data = None

try:
    # Soil helpers (mock generator good enough if no lat/lng provided)
    from routes.soil import get_mock_soil_data
except Exception:
    get_mock_soil_data = None

try:
    # Market helpers
    from routes.market import get_mock_market_data
except Exception:
    get_mock_market_data = None

try:
    # Recommendation scoring utilities
    from routes.recommendations import (
        CROP_RECOMMENDATIONS,
        calculate_crop_suitability,
        estimate_yield,
        estimate_cost,
    )
except Exception:
    CROP_RECOMMENDATIONS = {}
    def calculate_crop_suitability(*args, **kwargs):
        return 0, []
    def estimate_yield(*args, **kwargs):
        return 0
    def estimate_cost(*args, **kwargs):
        return 0

voice_bp = Blueprint('voice', __name__)

# Mock voice query patterns and responses
VOICE_PATTERNS = {
    'weather': {
        'patterns': [
            r'weather|temperature|rain|sunny|cloudy|humidity',
            r'what.*weather|how.*weather|weather.*like',
            r'rain.*today|sunny.*today|cloudy.*today',
            # Hindi keywords
            r'मौसम|बारिश|तापमान|धूप|बादल|आर्द्रता',
        ],
        'response_type': 'weather_query'
    },
    'soil': {
        'patterns': [
            r'soil|ph|moisture|nutrient|fertilizer',
            r'what.*soil|soil.*condition|soil.*quality',
            r'ph.*level|moisture.*level|nutrient.*level',
            r'मिट्टी|उर्वरक|नमी|अम्लता'
        ],
        'response_type': 'soil_query'
    },
    'crop': {
        'patterns': [
            r'crop|plant|grow|harvest|yield',
            r'what.*crop|which.*crop|best.*crop',
            r'plant.*now|grow.*now|harvest.*when',
            r'फसल|उगाऊँ|बोऊँ|कटाई'
        ],
        'response_type': 'crop_query'
    },
    'disease': {
        'patterns': [
            r'disease|sick|infected|pest|problem',
            r'what.*wrong|plant.*sick|leaf.*spot',
            r'disease.*plant|pest.*control|treatment',
            r'रोग|बीमारी|कीट|इलाज'
        ],
        'response_type': 'disease_query'
    },
    'market': {
        'patterns': [
            r'price|market|sell|buy|cost',
            r'what.*price|how.*much|market.*price',
            r'sell.*crop|buy.*seed|price.*today',
            r'कीमत|भाव|बाजार'
        ],
        'response_type': 'market_query'
    },
    'recommendation': {
        'patterns': [
            r'recommend|suggest|advice|help',
            r'what.*do|how.*grow|best.*way',
            r'recommend.*crop|suggest.*fertilizer'
        ],
        'response_type': 'recommendation_query'
    }
}

def extract_location_from_query(query_text: str) -> str | None:
    """Best-effort extraction of a city/location mentioned in the query.
    Examples handled: 'weather in Meerut', 'market price for wheat in Agra', 'rain at Pune today'.
    Returns the capitalized location token(s) if found, else None.
    """
    try:
        text = (query_text or '').strip()
        # Common prepositions that introduce locations
        match = re.search(r"\b(?:in|at|for|near)\s+([a-zA-Z][a-zA-Z\s'-]{2,})\b", text, flags=re.IGNORECASE)
        if match:
            # Trim trailing question words or today/tomorrow, etc.
            candidate = match.group(1)
            candidate = re.sub(r"\b(today|tomorrow|now|please|currently)\b", "", candidate, flags=re.IGNORECASE)
            candidate = candidate.strip(" ?!.,")
            # Keep up to 3 words (e.g., New Delhi, Los Angeles)
            parts = [p for p in re.split(r"\s+", candidate) if p]
            if parts:
                parts = parts[:3]
                return " ".join(w[:1].upper() + w[1:] for w in parts)
    except Exception:
        pass
    return None

def extract_crop_from_query(query_text: str) -> str | None:
    """Extract a crop/commodity name from the query if present."""
    try:
        text = (query_text or '').lower()
        # Known crops from market/recommendations
        known = [
            'wheat','rice','corn','sugarcane','cotton','soybean','potato','tomato',
            'onion','chili','mango','banana','apple','grapes','pomegranate'
        ]
        for crop in known:
            if re.search(rf"\b{re.escape(crop)}\b", text):
                return crop
        # Hindi common names quick map
        hindi_map = {
            'गेहूं': 'wheat', 'चावल': 'rice', 'मक्का': 'corn', 'गन्ना': 'sugarcane',
            'कपास': 'cotton', 'सोयाबीन': 'soybean', 'आलू': 'potato', 'टमाटर': 'tomato',
            'प्याज': 'onion', 'मिर्च': 'chili', 'आम': 'mango', 'केला': 'banana',
            'सेब': 'apple', 'अंगूर': 'grapes', 'अनार': 'pomegranate'
        }
        for h, eng in hindi_map.items():
            if h in text:
                return eng
    except Exception:
        pass
    return None

def process_voice_query(query_text, user_location=''):
    """Process voice query and determine intent"""
    query_lower = query_text.lower()
    
    # Detect intent based on patterns
    detected_intents = []
    for intent, data in VOICE_PATTERNS.items():
        for pattern in data['patterns']:
            if re.search(pattern, query_lower):
                detected_intents.append({
                    'intent': intent,
                    'response_type': data['response_type'],
                    'confidence': random.uniform(0.7, 0.95)
                })
                break
    
    # If no intent detected, classify as general query
    if not detected_intents:
        detected_intents.append({
            'intent': 'general',
            'response_type': 'general_query',
            'confidence': 0.5
        })
    
    # Sort by confidence
    detected_intents.sort(key=lambda x: x['confidence'], reverse=True)
    
    return detected_intents[0]  # Return highest confidence intent

def generate_voice_response(intent_data, query_text, user_location=''):
    """Generate appropriate response based on detected intent"""
    intent = intent_data['intent']
    confidence = intent_data['confidence']
    
    if intent == 'weather':
        # Try live bundle first; fallback to mock to avoid failures
        location_from_query = extract_location_from_query(query_text)
        location = location_from_query or user_location or 'Delhi'
        weather_bundle = None
        if callable(get_live_weather_bundle):
            try:
                weather_bundle = get_live_weather_bundle(location)
            except Exception:
                weather_bundle = None
        if not weather_bundle and callable(get_mock_weather_data):
            try:
                weather_bundle = get_mock_weather_data(location)
            except Exception:
                weather_bundle = None

        if weather_bundle:
            # Normalize shape: live bundle already in unified schema; mock uses same keys
            current = weather_bundle.get('current') or weather_bundle
            temp = current.get('temperature')
            hum = current.get('humidity')
            cond = (current.get('conditions') or 'Unknown').lower()
            wind = current.get('wind_speed')
            summary = (
                f"Weather in {location}: {cond.capitalize()} {temp}°C, "
                f"humidity {hum}%, wind {wind} km/h."
            )
            advisory = (
                " Irrigation: moderate needed." if hum < 50 else
                " Irrigation: light or none required."
            )
            return {
                'response_type': 'weather_query',
                'response_text': summary + advisory,
                'action_required': False,
                'follow_up_questions': [
                    "Would you like a 7-day forecast?",
                    "Need agricultural conditions for irrigation planning?",
                ],
            }
        # If everything fails, fall back to a safe generic sentence
        return {
            'response_type': 'weather_query',
            'response_text': 'I could not fetch live weather right now. Please try again shortly.',
            'action_required': False,
        }
    
    elif intent == 'soil':
        # Use mock soil generator with a default lat/lng if none provided
        soil_summary = None
        if callable(get_mock_soil_data):
            try:
                # Default to Delhi approx coords when we lack GPS
                soil = get_mock_soil_data(28.6139, 77.2090)
                soil_summary = (
                    f"Soil pH {soil['ph']}, moisture {round(soil['moisture']*100)}%, "
                    f"type {soil['soil_type']}, fertility {soil['fertility_rating'].lower()}."
                )
            except Exception:
                soil_summary = None
        return {
            'response_type': 'soil_query',
            'response_text': soil_summary or 'I could not assess soil right now. Try again later.',
            'action_required': False,
            'follow_up_questions': [
                'Do you want fertilizer recommendations?',
                'Should I analyze your soil details if you provide pH and moisture?',
            ],
        }
    
    elif intent == 'crop':
        # Build a quick recommendation grounded in soil/weather/market utilities
        location = user_location or 'Delhi'
        # Weather (live/mock)
        weather_bundle = None
        if callable(get_live_weather_bundle):
            try:
                weather_bundle = get_live_weather_bundle(location)
            except Exception:
                weather_bundle = None
        if not weather_bundle and callable(get_mock_weather_data):
            weather_bundle = get_mock_weather_data(location)
        current_temp = (weather_bundle or {}).get('current', {}).get('temperature', 25)
        # Soil (mock)
        soil = get_mock_soil_data(28.6139, 77.2090) if callable(get_mock_soil_data) else {'ph': 6.5, 'moisture': 0.3, 'soil_type': 'loamy'}
        # Market (mock)
        market = get_mock_market_data() if callable(get_mock_market_data) else []

        scored = []
        for crop in (CROP_RECOMMENDATIONS or {}).keys():
            score, factors = calculate_crop_suitability(crop, soil, {'temperature': current_temp}, market)
            if score > 30:
                scored.append((crop, score, factors))
        scored.sort(key=lambda x: x[1], reverse=True)
        top = scored[:3]
        if top:
            parts = [f"{c} ({s}% suitability)" for c, s, _ in top]
            summary = "Best crops now: " + ", ".join(parts) + "."
            return {
                'response_type': 'crop_query',
                'response_text': summary,
                'action_required': True,
                'action_type': 'crop_recommendation',
                'follow_up_questions': [
                    'Should I open the AI Recommendations page?',
                    'Do you want details for a specific crop?',
                ],
            }
        return {
            'response_type': 'crop_query',
            'response_text': 'I could not compute crop suitability right now.',
            'action_required': False,
        }
    
    elif intent == 'disease':
        return {
            'response_type': 'disease_query',
            'response_text': f"I can help you identify plant diseases. Please upload a photo of the affected plant, and I'll analyze it for common diseases like rust, blight, or fungal infections. Early detection is key to effective treatment.",
            'action_required': True,
            'action_type': 'disease_detection',
            'follow_up_questions': [
                "Can you describe the symptoms you're seeing?",
                "Would you like general disease prevention tips?"
            ]
        }
    
    elif intent == 'market':
        # Use query-mentioned location if present for contextual message, though
        # current mock market generator is pan-India; this mostly improves phrasing.
        location_from_query = extract_location_from_query(query_text)
        crop_from_query = extract_crop_from_query(query_text)
        data = get_mock_market_data()[:] if callable(get_mock_market_data) else []
        if data:
            if crop_from_query:
                filtered = [d for d in data if d['crop'] == crop_from_query]
                if filtered:
                    d = filtered[0]
                    summary = (
                        f"{crop_from_query.capitalize()} price"
                        + (f" near {location_from_query}" if location_from_query else "")
                        + f": ₹{d['current_price']} {d['unit'].replace('_',' ')} (trend {d['market_trend']}, demand {d['demand_level']})."
                    )
                    return {
                        'response_type': 'market_query',
                        'response_text': summary,
                        'action_required': False,
                        'follow_up_questions': ['Want detailed price chart for this crop?'],
                    }
            # Take top 3 by demand then trend
            data.sort(key=lambda x: (x['demand_level'] == 'high', x['market_trend'] == 'rising', x['price_change_percent']), reverse=True)
            top = data[:3]
            msg = ", ".join([f"{d['crop']} ₹{d['current_price']}/{d['unit'].replace('_',' ')}" for d in top])
            if location_from_query:
                summary = f"Market highlights near {location_from_query}: {msg}."
            else:
                summary = f"Market highlights: {msg}."
        else:
            summary = 'I could not fetch market data right now.'
        return {
            'response_type': 'market_query',
            'response_text': summary,
            'action_required': False,
            'follow_up_questions': [
                'Want detailed prices for a specific crop?',
                'Should I open the Market page?',
            ],
        }
    
    elif intent == 'recommendation':
        return {
            'response_type': 'recommendation_query',
            'response_text': f"I'd be happy to provide personalized recommendations! To give you the best advice, I'll need to analyze your soil data, weather conditions, and market prices. This will help me suggest the most profitable crops for your farm.",
            'action_required': True,
            'action_type': 'full_recommendation',
            'follow_up_questions': [
                "What's your farm size and location?",
                "Do you have any specific crop preferences?"
            ]
        }
    
    else:  # general query
        return {
            'response_type': 'general_query',
            'response_text': f"I'm here to help with your farming needs! I can assist with weather information, soil analysis, crop recommendations, disease detection, market prices, and more. What would you like to know?",
            'action_required': False,
            'follow_up_questions': [
                "What's your main farming concern today?",
                "How can I help improve your crop yield?"
            ]
        }

@voice_bp.route('/query', methods=['POST'])
@jwt_required()
def process_voice_query_endpoint():
    """Process voice query and return intelligent response"""
    try:
        data = request.json
        if not data:
            return jsonify({'error': 'Request data required'}), 400
        
        query_text = data.get('query', '').strip()
        user_location = data.get('location', '')
        language = data.get('language', 'en').lower()
        
        if not query_text:
            return jsonify({'error': 'Query text is required'}), 400
        
        # Process the query
        intent_data = process_voice_query(query_text, user_location)
        
        # Generate response
        response = generate_voice_response(intent_data, query_text, user_location)
        
        # Add metadata
        response.update({
            'query': query_text,
            'detected_intent': intent_data['intent'],
            'confidence': intent_data['confidence'],
            'language': language,
            'user_location': user_location,
            'processing_time': round(random.uniform(0.5, 2.0), 2),
            'timestamp': datetime.now().isoformat()
        })
        
        return jsonify(response), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to process voice query', 'details': str(e)}), 500

@voice_bp.route('/query-batch', methods=['POST'])
@jwt_required()
def process_voice_query_batch():
    """Process multiple voice queries in batch"""
    try:
        data = request.json
        if not data:
            return jsonify({'error': 'Request data required'}), 400
        
        queries = data.get('queries', [])
        user_location = data.get('location', '')
        language = data.get('language', 'en').lower()
        
        if not queries:
            return jsonify({'error': 'Queries array is required'}), 400
        
        if len(queries) > 10:
            return jsonify({'error': 'Maximum 10 queries allowed per batch'}), 400
        
        results = []
        
        for i, query_text in enumerate(queries):
            if not query_text or not query_text.strip():
                results.append({
                    'index': i,
                    'error': 'Empty query',
                    'success': False
                })
                continue
            
            try:
                # Process the query
                intent_data = process_voice_query(query_text.strip(), user_location)
                
                # Generate response
                response = generate_voice_response(intent_data, query_text.strip(), user_location)
                
                # Add metadata
                response.update({
                    'query': query_text.strip(),
                    'detected_intent': intent_data['intent'],
                    'confidence': intent_data['confidence'],
                    'language': language,
                    'user_location': user_location,
                    'processing_time': round(random.uniform(0.5, 2.0), 2),
                    'timestamp': datetime.now().isoformat()
                })
                
                results.append({
                    'index': i,
                    'success': True,
                    'response': response
                })
                
            except Exception as e:
                results.append({
                    'index': i,
                    'error': str(e),
                    'success': False
                })
        
        successful_queries = len([r for r in results if r.get('success', False)])
        
        return jsonify({
            'batch_results': results,
            'total_queries': len(queries),
            'successful_queries': successful_queries,
            'user_location': user_location,
            'language': language,
            'timestamp': datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to process batch voice queries', 'details': str(e)}), 500

@voice_bp.route('/intents', methods=['GET'])
@jwt_required()
def get_supported_intents():
    """Get list of supported voice query intents"""
    try:
        intents = []
        for intent, data in VOICE_PATTERNS.items():
            intents.append({
                'intent': intent,
                'response_type': data['response_type'],
                'description': get_intent_description(intent),
                'example_queries': get_example_queries(intent)
            })
        
        return jsonify({
            'supported_intents': intents,
            'total_intents': len(intents),
            'timestamp': datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to fetch supported intents', 'details': str(e)}), 500

@voice_bp.route('/conversation', methods=['POST'])
@jwt_required()
def start_conversation():
    """Start a conversational session for voice queries"""
    try:
        data = request.json
        if not data:
            return jsonify({'error': 'Request data required'}), 400
        
        user_location = data.get('location', '')
        language = data.get('language', 'en').lower()
        context = data.get('context', {})
        
        # Generate conversation starter
        conversation_starter = {
            'session_id': f"conv_{random.randint(10000, 99999)}",
            'greeting': f"Hello! I'm your AI farming assistant. I can help you with weather updates, soil analysis, crop recommendations, disease detection, market prices, and more. What would you like to know about your farm today?",
            'suggested_queries': [
                "What's the weather like today?",
                "How is my soil condition?",
                "What crops should I plant?",
                "Check market prices for my crops",
                "Help me identify plant diseases"
            ],
            'user_location': user_location,
            'language': language,
            'context': context,
            'timestamp': datetime.now().isoformat()
        }
        
        return jsonify(conversation_starter), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to start conversation', 'details': str(e)}), 500

@voice_bp.route('/conversation/<session_id>', methods=['POST'])
@jwt_required()
def continue_conversation(session_id):
    """Continue a conversational session"""
    try:
        data = request.json
        if not data:
            return jsonify({'error': 'Request data required'}), 400
        
        query_text = data.get('query', '').strip()
        context = data.get('context', {})
        
        if not query_text:
            return jsonify({'error': 'Query text is required'}), 400
        
        # Process the query with context
        intent_data = process_voice_query(query_text, context.get('location', ''))
        
        # Generate contextual response
        response = generate_voice_response(intent_data, query_text, context.get('location', ''))
        
        # Add conversation context
        response.update({
            'session_id': session_id,
            'query': query_text,
            'detected_intent': intent_data['intent'],
            'confidence': intent_data['confidence'],
            'context': context,
            'conversation_turn': context.get('turn_count', 1) + 1,
            'timestamp': datetime.now().isoformat()
        })
        
        return jsonify(response), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to continue conversation', 'details': str(e)}), 500

def get_intent_description(intent):
    """Get description for an intent"""
    descriptions = {
        'weather': 'Get weather information and forecasts for your location',
        'soil': 'Analyze soil conditions, pH, moisture, and nutrient levels',
        'crop': 'Get crop recommendations and growing advice',
        'disease': 'Identify plant diseases and get treatment recommendations',
        'market': 'Check crop prices and market conditions',
        'recommendation': 'Get personalized farming recommendations',
        'general': 'General farming questions and assistance'
    }
    return descriptions.get(intent, 'General farming assistance')

def get_example_queries(intent):
    """Get example queries for an intent"""
    examples = {
        'weather': [
            "What's the weather like today?",
            "Will it rain tomorrow?",
            "What's the temperature and humidity?"
        ],
        'soil': [
            "How is my soil condition?",
            "What's the pH level of my soil?",
            "Do I need to add fertilizer?"
        ],
        'crop': [
            "What crops should I plant?",
            "When should I harvest my wheat?",
            "How much water do my crops need?"
        ],
        'disease': [
            "My plants look sick, what's wrong?",
            "I see spots on my leaves",
            "Help me identify this plant disease"
        ],
        'market': [
            "What are the current crop prices?",
            "When should I sell my harvest?",
            "Is it a good time to buy seeds?"
        ],
        'recommendation': [
            "What should I do to improve my farm?",
            "Give me farming advice for this season",
            "How can I increase my crop yield?"
        ],
        'general': [
            "Help me with my farm",
            "What can you do for me?",
            "I need farming assistance"
        ]
    }
    return examples.get(intent, ["How can I help you?"])
