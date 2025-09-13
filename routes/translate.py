from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
import random

translate_bp = Blueprint('translate', __name__)

# Mock translation data for agricultural terms
AGRICULTURAL_TERMS = {
    'en': {
        'soil': 'soil', 'crop': 'crop', 'fertilizer': 'fertilizer',
        'irrigation': 'irrigation', 'harvest': 'harvest', 'yield': 'yield',
        'pest': 'pest', 'disease': 'disease', 'weather': 'weather',
        'planting': 'planting', 'seeding': 'seeding', 'watering': 'watering',
        'ph': 'pH', 'moisture': 'moisture', 'temperature': 'temperature',
        'humidity': 'humidity', 'rainfall': 'rainfall', 'sunlight': 'sunlight'
    },
    'hi': {
        'soil': 'मिट्टी', 'crop': 'फसल', 'fertilizer': 'उर्वरक',
        'irrigation': 'सिंचाई', 'harvest': 'फसल कटाई', 'yield': 'उपज',
        'pest': 'कीट', 'disease': 'रोग', 'weather': 'मौसम',
        'planting': 'रोपण', 'seeding': 'बीजारोपण', 'watering': 'पानी देना',
        'ph': 'पीएच', 'moisture': 'नमी', 'temperature': 'तापमान',
        'humidity': 'आर्द्रता', 'rainfall': 'वर्षा', 'sunlight': 'सूर्य का प्रकाश'
    },
    'es': {
        'soil': 'suelo', 'crop': 'cultivo', 'fertilizer': 'fertilizante',
        'irrigation': 'riego', 'harvest': 'cosecha', 'yield': 'rendimiento',
        'pest': 'plaga', 'disease': 'enfermedad', 'weather': 'clima',
        'planting': 'siembra', 'seeding': 'siembra', 'watering': 'riego',
        'ph': 'pH', 'moisture': 'humedad', 'temperature': 'temperatura',
        'humidity': 'humedad', 'rainfall': 'lluvia', 'sunlight': 'luz solar'
    },
    'fr': {
        'soil': 'sol', 'crop': 'culture', 'fertilizer': 'engrais',
        'irrigation': 'irrigation', 'harvest': 'récolte', 'yield': 'rendement',
        'pest': 'ravageur', 'disease': 'maladie', 'weather': 'temps',
        'planting': 'plantation', 'seeding': 'semis', 'watering': 'arrosage',
        'ph': 'pH', 'moisture': 'humidité', 'temperature': 'température',
        'humidity': 'humidité', 'rainfall': 'précipitations', 'sunlight': 'lumière du soleil'
    },
    'de': {
        'soil': 'Boden', 'crop': 'Ernte', 'fertilizer': 'Dünger',
        'irrigation': 'Bewässerung', 'harvest': 'Ernte', 'yield': 'Ertrag',
        'pest': 'Schädling', 'disease': 'Krankheit', 'weather': 'Wetter',
        'planting': 'Pflanzung', 'seeding': 'Aussaat', 'watering': 'Bewässerung',
        'ph': 'pH', 'moisture': 'Feuchtigkeit', 'temperature': 'Temperatur',
        'humidity': 'Luftfeuchtigkeit', 'rainfall': 'Niederschlag', 'sunlight': 'Sonnenlicht'
    },
    'zh': {
        'soil': '土壤', 'crop': '作物', 'fertilizer': '肥料',
        'irrigation': '灌溉', 'harvest': '收获', 'yield': '产量',
        'pest': '害虫', 'disease': '疾病', 'weather': '天气',
        'planting': '种植', 'seeding': '播种', 'watering': '浇水',
        'ph': 'pH值', 'moisture': '湿度', 'temperature': '温度',
        'humidity': '湿度', 'rainfall': '降雨', 'sunlight': '阳光'
    }
}

# Supported languages
SUPPORTED_LANGUAGES = {
    'en': 'English',
    'hi': 'Hindi',
    'es': 'Spanish',
    'fr': 'French',
    'de': 'German',
    'zh': 'Chinese'
}

def mock_translate_text(text, source_lang, target_lang):
    """Mock translation function - in real implementation, use Google Translate API or similar"""
    # Simple mock translation based on agricultural terms
    if source_lang == target_lang:
        return text
    
    # Check if text contains agricultural terms
    translated_text = text
    for term, translations in AGRICULTURAL_TERMS.items():
        if term == source_lang and target_lang in translations:
            for en_term, translation in translations.items():
                if en_term in text.lower():
                    translated_text = translated_text.replace(en_term, translation)
    
    # Add some mock translation indicators
    if target_lang == 'hi':
        translated_text = f"[Hindi] {translated_text}"
    elif target_lang == 'es':
        translated_text = f"[Spanish] {translated_text}"
    elif target_lang == 'fr':
        translated_text = f"[French] {translated_text}"
    elif target_lang == 'de':
        translated_text = f"[German] {translated_text}"
    elif target_lang == 'zh':
        translated_text = f"[Chinese] {translated_text}"
    
    return translated_text

@translate_bp.route('/translate', methods=['POST'])
@jwt_required()
def translate_text():
    """Translate text from one language to another"""
    try:
        data = request.json
        if not data:
            return jsonify({'error': 'Request data required'}), 400
        
        text = data.get('text', '').strip()
        source_lang = data.get('source_language', 'en').lower()
        target_lang = data.get('target_language', 'en').lower()
        
        if not text:
            return jsonify({'error': 'Text to translate is required'}), 400
        
        if source_lang not in SUPPORTED_LANGUAGES:
            return jsonify({
                'error': 'Unsupported source language',
                'supported_languages': list(SUPPORTED_LANGUAGES.keys())
            }), 400
        
        if target_lang not in SUPPORTED_LANGUAGES:
            return jsonify({
                'error': 'Unsupported target language',
                'supported_languages': list(SUPPORTED_LANGUAGES.keys())
            }), 400
        
        # Mock translation
        translated_text = mock_translate_text(text, source_lang, target_lang)
        
        # Calculate confidence score (mock)
        confidence = random.uniform(0.75, 0.95)
        
        return jsonify({
            'original_text': text,
            'translated_text': translated_text,
            'source_language': source_lang,
            'target_language': target_lang,
            'confidence': round(confidence, 2),
            'character_count': len(text),
            'translation_service': 'mock_translator_v1.0',
            'timestamp': '2024-01-15T10:30:00Z'
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to translate text', 'details': str(e)}), 500

@translate_bp.route('/translate-batch', methods=['POST'])
@jwt_required()
def translate_batch():
    """Translate multiple texts in batch"""
    try:
        data = request.json
        if not data:
            return jsonify({'error': 'Request data required'}), 400
        
        texts = data.get('texts', [])
        source_lang = data.get('source_language', 'en').lower()
        target_lang = data.get('target_language', 'en').lower()
        
        if not texts:
            return jsonify({'error': 'Texts array is required'}), 400
        
        if len(texts) > 50:
            return jsonify({'error': 'Maximum 50 texts allowed per batch'}), 400
        
        if source_lang not in SUPPORTED_LANGUAGES or target_lang not in SUPPORTED_LANGUAGES:
            return jsonify({
                'error': 'Unsupported language',
                'supported_languages': list(SUPPORTED_LANGUAGES.keys())
            }), 400
        
        results = []
        
        for i, text in enumerate(texts):
            if not text or not text.strip():
                results.append({
                    'index': i,
                    'error': 'Empty text',
                    'success': False
                })
                continue
            
            try:
                translated_text = mock_translate_text(text.strip(), source_lang, target_lang)
                confidence = random.uniform(0.75, 0.95)
                
                results.append({
                    'index': i,
                    'success': True,
                    'original_text': text.strip(),
                    'translated_text': translated_text,
                    'confidence': round(confidence, 2)
                })
                
            except Exception as e:
                results.append({
                    'index': i,
                    'error': str(e),
                    'success': False
                })
        
        successful_translations = len([r for r in results if r.get('success', False)])
        
        return jsonify({
            'batch_results': results,
            'total_texts': len(texts),
            'successful_translations': successful_translations,
            'source_language': source_lang,
            'target_language': target_lang,
            'translation_service': 'mock_translator_v1.0',
            'timestamp': '2024-01-15T10:30:00Z'
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to process batch translation', 'details': str(e)}), 500

@translate_bp.route('/languages', methods=['GET'])
@jwt_required()
def get_supported_languages():
    """Get list of supported languages"""
    try:
        return jsonify({
            'supported_languages': SUPPORTED_LANGUAGES,
            'total_languages': len(SUPPORTED_LANGUAGES),
            'default_language': 'en',
            'timestamp': '2024-01-15T10:30:00Z'
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to fetch supported languages', 'details': str(e)}), 500

@translate_bp.route('/detect-language', methods=['POST'])
@jwt_required()
def detect_language():
    """Detect the language of the input text"""
    try:
        data = request.json
        if not data:
            return jsonify({'error': 'Request data required'}), 400
        
        text = data.get('text', '').strip()
        if not text:
            return jsonify({'error': 'Text is required for language detection'}), 400
        
        # Mock language detection based on character patterns
        detected_lang = 'en'  # Default to English
        
        # Simple heuristics for language detection
        if any(char in text for char in 'मिट्टीफसलउर्वरकसिंचाई'):
            detected_lang = 'hi'  # Hindi
        elif any(char in text for char in 'ñáéíóúü'):
            detected_lang = 'es'  # Spanish
        elif any(char in text for char in 'àâäéèêëïîôùûüÿç'):
            detected_lang = 'fr'  # French
        elif any(char in text for char in 'äöüß'):
            detected_lang = 'de'  # German
        elif any(char in text for char in '的土壤作物肥料灌溉'):
            detected_lang = 'zh'  # Chinese
        
        confidence = random.uniform(0.8, 0.95)
        
        return jsonify({
            'text': text,
            'detected_language': detected_lang,
            'language_name': SUPPORTED_LANGUAGES[detected_lang],
            'confidence': round(confidence, 2),
            'character_count': len(text),
            'detection_service': 'mock_detector_v1.0',
            'timestamp': '2024-01-15T10:30:00Z'
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to detect language', 'details': str(e)}), 500

@translate_bp.route('/agricultural-terms', methods=['GET'])
@jwt_required()
def get_agricultural_terms():
    """Get agricultural terms in different languages"""
    try:
        language = request.args.get('language', 'en').lower()
        
        if language not in SUPPORTED_LANGUAGES:
            return jsonify({
                'error': 'Unsupported language',
                'supported_languages': list(SUPPORTED_LANGUAGES.keys())
            }), 400
        
        terms = AGRICULTURAL_TERMS.get(language, {})
        
        return jsonify({
            'language': language,
            'language_name': SUPPORTED_LANGUAGES[language],
            'agricultural_terms': terms,
            'total_terms': len(terms),
            'timestamp': '2024-01-15T10:30:00Z'
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to fetch agricultural terms', 'details': str(e)}), 500

@translate_bp.route('/translate-recommendations', methods=['POST'])
@jwt_required()
def translate_recommendations():
    """Translate crop recommendations to target language"""
    try:
        data = request.json
        if not data:
            return jsonify({'error': 'Request data required'}), 400
        
        recommendations = data.get('recommendations', [])
        target_lang = data.get('target_language', 'en').lower()
        
        if not recommendations:
            return jsonify({'error': 'Recommendations array is required'}), 400
        
        if target_lang not in SUPPORTED_LANGUAGES:
            return jsonify({
                'error': 'Unsupported target language',
                'supported_languages': list(SUPPORTED_LANGUAGES.keys())
            }), 400
        
        translated_recommendations = []
        
        for rec in recommendations:
            translated_rec = rec.copy()
            
            # Translate key text fields
            if 'crop' in rec:
                translated_rec['crop'] = mock_translate_text(rec['crop'], 'en', target_lang)
            
            if 'recommendation' in rec:
                translated_rec['recommendation'] = mock_translate_text(rec['recommendation'], 'en', target_lang)
            
            if 'factors' in rec and isinstance(rec['factors'], list):
                translated_rec['factors'] = [mock_translate_text(factor, 'en', target_lang) for factor in rec['factors']]
            
            if 'growing_requirements' in rec:
                growing_req = rec['growing_requirements'].copy()
                for key, value in growing_req.items():
                    if isinstance(value, str):
                        growing_req[key] = mock_translate_text(value, 'en', target_lang)
                translated_rec['growing_requirements'] = growing_req
            
            translated_recommendations.append(translated_rec)
        
        return jsonify({
            'original_recommendations': recommendations,
            'translated_recommendations': translated_recommendations,
            'target_language': target_lang,
            'total_recommendations': len(recommendations),
            'translation_service': 'mock_translator_v1.0',
            'timestamp': '2024-01-15T10:30:00Z'
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to translate recommendations', 'details': str(e)}), 500
