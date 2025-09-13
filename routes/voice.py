from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
import random
import re
from datetime import datetime

voice_bp = Blueprint('voice', __name__)

# Mock voice query patterns and responses
VOICE_PATTERNS = {
    'weather': {
        'patterns': [
            r'weather|temperature|rain|sunny|cloudy|humidity',
            r'what.*weather|how.*weather|weather.*like',
            r'rain.*today|sunny.*today|cloudy.*today'
        ],
        'response_type': 'weather_query'
    },
    'soil': {
        'patterns': [
            r'soil|ph|moisture|nutrient|fertilizer',
            r'what.*soil|soil.*condition|soil.*quality',
            r'ph.*level|moisture.*level|nutrient.*level'
        ],
        'response_type': 'soil_query'
    },
    'crop': {
        'patterns': [
            r'crop|plant|grow|harvest|yield',
            r'what.*crop|which.*crop|best.*crop',
            r'plant.*now|grow.*now|harvest.*when'
        ],
        'response_type': 'crop_query'
    },
    'disease': {
        'patterns': [
            r'disease|sick|infected|pest|problem',
            r'what.*wrong|plant.*sick|leaf.*spot',
            r'disease.*plant|pest.*control|treatment'
        ],
        'response_type': 'disease_query'
    },
    'market': {
        'patterns': [
            r'price|market|sell|buy|cost',
            r'what.*price|how.*much|market.*price',
            r'sell.*crop|buy.*seed|price.*today'
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
        return {
            'response_type': 'weather_query',
            'response_text': f"Based on your location, the current weather is sunny with a temperature of 25°C. Humidity is at 60% and there's a 20% chance of rain today. Perfect conditions for most crops!",
            'action_required': False,
            'follow_up_questions': [
                "Would you like a 7-day weather forecast?",
                "Do you need weather alerts for your crops?"
            ]
        }
    
    elif intent == 'soil':
        return {
            'response_type': 'soil_query',
            'response_text': f"Your soil analysis shows pH level of 6.5, which is optimal for most crops. Moisture content is at 30% and nutrient levels are good. I recommend adding organic matter to improve soil structure.",
            'action_required': False,
            'follow_up_questions': [
                "Would you like specific fertilizer recommendations?",
                "Do you need help with soil testing?"
            ]
        }
    
    elif intent == 'crop':
        return {
            'response_type': 'crop_query',
            'response_text': f"Based on your soil conditions and current season, I recommend planting wheat, rice, or corn. These crops are well-suited for your area and have good market demand. Would you like detailed growing instructions?",
            'action_required': True,
            'action_type': 'crop_recommendation',
            'follow_up_questions': [
                "Which crop interests you most?",
                "Do you need planting schedule information?"
            ]
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
        return {
            'response_type': 'market_query',
            'response_text': f"Current market prices are looking good! Wheat is at ₹2,500 per quintal, rice at ₹3,000, and corn at ₹2,000. Prices have been stable with slight upward trends. Good time to plan your harvest and sales.",
            'action_required': False,
            'follow_up_questions': [
                "Would you like price forecasts for specific crops?",
                "Do you need help with market timing?"
            ]
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
