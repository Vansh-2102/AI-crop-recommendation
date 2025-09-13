from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
import base64
import random
from datetime import datetime

disease_bp = Blueprint('disease', __name__)

# Mock disease database
DISEASE_DATABASE = {
    'wheat': {
        'rust': {
            'name': 'Wheat Rust',
            'symptoms': ['Yellow-orange pustules on leaves', 'Reduced grain size', 'Premature leaf death'],
            'severity_levels': ['mild', 'moderate', 'severe'],
            'treatment': 'Apply fungicide containing tebuconazole or propiconazole',
            'prevention': 'Plant resistant varieties, proper crop rotation, avoid excessive nitrogen',
            'confidence': 0.85
        },
        'powdery_mildew': {
            'name': 'Powdery Mildew',
            'symptoms': ['White powdery coating on leaves', 'Stunted growth', 'Reduced yield'],
            'severity_levels': ['mild', 'moderate', 'severe'],
            'treatment': 'Apply sulfur-based fungicide or neem oil',
            'prevention': 'Ensure good air circulation, avoid overcrowding',
            'confidence': 0.78
        },
        'head_blight': {
            'name': 'Fusarium Head Blight',
            'symptoms': ['Bleached spikelets', 'Pink or orange mold on kernels', 'Shriveled grains'],
            'severity_levels': ['mild', 'moderate', 'severe'],
            'treatment': 'Apply fungicide at flowering stage',
            'prevention': 'Crop rotation, proper field sanitation',
            'confidence': 0.82
        }
    },
    'rice': {
        'blast': {
            'name': 'Rice Blast',
            'symptoms': ['Diamond-shaped lesions on leaves', 'Node infection', 'Panicle blast'],
            'severity_levels': ['mild', 'moderate', 'severe'],
            'treatment': 'Apply tricyclazole or azoxystrobin fungicide',
            'prevention': 'Plant resistant varieties, proper water management',
            'confidence': 0.88
        },
        'brown_spot': {
            'name': 'Brown Spot',
            'symptoms': ['Small brown spots on leaves', 'Yellowing of leaves', 'Reduced grain quality'],
            'severity_levels': ['mild', 'moderate', 'severe'],
            'treatment': 'Apply copper-based fungicide',
            'prevention': 'Proper fertilization, avoid water stress',
            'confidence': 0.75
        },
        'bacterial_blight': {
            'name': 'Bacterial Blight',
            'symptoms': ['Water-soaked lesions', 'Yellowing along leaf margins', 'Wilting'],
            'severity_levels': ['mild', 'moderate', 'severe'],
            'treatment': 'Apply copper-based bactericide',
            'prevention': 'Use disease-free seed, proper field drainage',
            'confidence': 0.80
        }
    },
    'corn': {
        'northern_leaf_blight': {
            'name': 'Northern Leaf Blight',
            'symptoms': ['Long elliptical lesions on leaves', 'Yellowing and death of leaves', 'Reduced yield'],
            'severity_levels': ['mild', 'moderate', 'severe'],
            'treatment': 'Apply fungicide containing azoxystrobin',
            'prevention': 'Crop rotation, tillage to bury residue',
            'confidence': 0.83
        },
        'common_rust': {
            'name': 'Common Rust',
            'symptoms': ['Small reddish-brown pustules', 'Yellowing of leaves', 'Reduced photosynthesis'],
            'severity_levels': ['mild', 'moderate', 'severe'],
            'treatment': 'Apply fungicide with triazole compounds',
            'prevention': 'Plant resistant hybrids, proper spacing',
            'confidence': 0.79
        },
        'gray_leaf_spot': {
            'name': 'Gray Leaf Spot',
            'symptoms': ['Rectangular lesions with gray centers', 'Yellow halos around spots', 'Premature death'],
            'severity_levels': ['mild', 'moderate', 'severe'],
            'treatment': 'Apply strobilurin fungicide',
            'prevention': 'Crop rotation, residue management',
            'confidence': 0.81
        }
    },
    'tomato': {
        'early_blight': {
            'name': 'Early Blight',
            'symptoms': ['Concentric rings on leaves', 'Yellowing and defoliation', 'Fruit lesions'],
            'severity_levels': ['mild', 'moderate', 'severe'],
            'treatment': 'Apply chlorothalonil or copper fungicide',
            'prevention': 'Proper spacing, avoid overhead watering',
            'confidence': 0.86
        },
        'late_blight': {
            'name': 'Late Blight',
            'symptoms': ['Water-soaked lesions', 'White mold on underside', 'Rapid plant death'],
            'severity_levels': ['mild', 'moderate', 'severe'],
            'treatment': 'Apply fungicide containing metalaxyl',
            'prevention': 'Good air circulation, avoid wet conditions',
            'confidence': 0.89
        },
        'bacterial_wilt': {
            'name': 'Bacterial Wilt',
            'symptoms': ['Wilting during hot weather', 'Brown vascular tissue', 'Plant collapse'],
            'severity_levels': ['mild', 'moderate', 'severe'],
            'treatment': 'Remove infected plants, apply copper bactericide',
            'prevention': 'Crop rotation, use resistant varieties',
            'confidence': 0.84
        }
    },
    'potato': {
        'late_blight': {
            'name': 'Late Blight',
            'symptoms': ['Dark lesions on leaves', 'White mold on underside', 'Tuber rot'],
            'severity_levels': ['mild', 'moderate', 'severe'],
            'treatment': 'Apply fungicide with metalaxyl',
            'prevention': 'Proper spacing, avoid overhead irrigation',
            'confidence': 0.87
        },
        'early_blight': {
            'name': 'Early Blight',
            'symptoms': ['Target-like lesions', 'Yellowing of leaves', 'Reduced tuber size'],
            'severity_levels': ['mild', 'moderate', 'severe'],
            'treatment': 'Apply chlorothalonil fungicide',
            'prevention': 'Crop rotation, proper fertilization',
            'confidence': 0.82
        },
        'scab': {
            'name': 'Common Scab',
            'symptoms': ['Rough, scabby patches on tubers', 'Reduced market value', 'Surface lesions'],
            'severity_levels': ['mild', 'moderate', 'severe'],
            'treatment': 'Apply sulfur or acidifying agents',
            'prevention': 'Maintain soil pH 5.0-5.2, crop rotation',
            'confidence': 0.76
        }
    }
}

def simulate_disease_detection(image_data, crop_type):
    """Simulate disease detection from image data"""
    # In a real implementation, this would use a trained ML model
    # For now, we'll simulate based on crop type and random factors
    
    if crop_type not in DISEASE_DATABASE:
        return None
    
    # Simulate detection with some randomness
    diseases = list(DISEASE_DATABASE[crop_type].keys())
    
    # 70% chance of detecting a disease
    if random.random() < 0.7:
        detected_disease = random.choice(diseases)
        disease_info = DISEASE_DATABASE[crop_type][detected_disease].copy()
        
        # Add some randomness to confidence
        base_confidence = disease_info['confidence']
        confidence_variation = random.uniform(-0.1, 0.1)
        disease_info['confidence'] = max(0.5, min(0.95, base_confidence + confidence_variation))
        
        # Randomly assign severity
        disease_info['detected_severity'] = random.choice(disease_info['severity_levels'])
        
        # Add image analysis metadata
        disease_info['image_analysis'] = {
            'image_size': f"{random.randint(800, 2000)}x{random.randint(600, 1500)}",
            'processing_time': round(random.uniform(0.5, 3.0), 2),
            'model_version': 'v2.1.0',
            'detection_algorithm': 'CNN-based classification'
        }
        
        return disease_info
    else:
        return {
            'name': 'No Disease Detected',
            'symptoms': ['Healthy plant appearance'],
            'severity_levels': ['healthy'],
            'treatment': 'Continue current care practices',
            'prevention': 'Maintain good growing conditions',
            'confidence': 0.85,
            'detected_severity': 'healthy',
            'image_analysis': {
                'image_size': f"{random.randint(800, 2000)}x{random.randint(600, 1500)}",
                'processing_time': round(random.uniform(0.5, 3.0), 2),
                'model_version': 'v2.1.0',
                'detection_algorithm': 'CNN-based classification'
            }
        }

@disease_bp.route('/detect', methods=['POST'])
@jwt_required()
def detect_disease():
    """Detect plant diseases from uploaded images"""
    try:
        data = request.json
        if not data:
            return jsonify({'error': 'Request data required'}), 400
        
        # Extract image data and crop type
        image_data = data.get('image_data')  # Base64 encoded image
        crop_type = data.get('crop_type', '').lower()
        location = data.get('location', '')
        
        if not image_data:
            return jsonify({'error': 'Image data is required'}), 400
        
        if not crop_type:
            return jsonify({'error': 'Crop type is required'}), 400
        
        # Validate crop type
        if crop_type not in DISEASE_DATABASE:
            return jsonify({
                'error': 'Crop type not supported',
                'supported_crops': list(DISEASE_DATABASE.keys())
            }), 400
        
        # Simulate image processing delay
        import time
        time.sleep(random.uniform(1, 3))
        
        # Detect disease
        detection_result = simulate_disease_detection(image_data, crop_type)
        
        if not detection_result:
            return jsonify({'error': 'Failed to process image'}), 500
        
        # Generate additional recommendations
        recommendations = generate_disease_recommendations(detection_result, crop_type, location)
        
        # Create response
        response = {
            'detection_result': detection_result,
            'crop_type': crop_type,
            'location': location,
            'recommendations': recommendations,
            'timestamp': datetime.now().isoformat(),
            'processing_info': {
                'model_version': 'v2.1.0',
                'processing_time': detection_result['image_analysis']['processing_time'],
                'confidence_threshold': 0.7
            }
        }
        
        return jsonify(response), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to detect disease', 'details': str(e)}), 500

@disease_bp.route('/detect-batch', methods=['POST'])
@jwt_required()
def detect_disease_batch():
    """Detect diseases from multiple images in batch"""
    try:
        data = request.json
        if not data:
            return jsonify({'error': 'Request data required'}), 400
        
        images = data.get('images', [])
        if not images:
            return jsonify({'error': 'Images array is required'}), 400
        
        if len(images) > 10:
            return jsonify({'error': 'Maximum 10 images allowed per batch'}), 400
        
        results = []
        
        for i, image_info in enumerate(images):
            try:
                image_data = image_info.get('image_data')
                crop_type = image_info.get('crop_type', '').lower()
                location = image_info.get('location', '')
                
                if not image_data or not crop_type:
                    results.append({
                        'index': i,
                        'error': 'Missing image_data or crop_type',
                        'success': False
                    })
                    continue
                
                # Detect disease
                detection_result = simulate_disease_detection(image_data, crop_type)
                
                if detection_result:
                    results.append({
                        'index': i,
                        'success': True,
                        'detection_result': detection_result,
                        'crop_type': crop_type,
                        'location': location
                    })
                else:
                    results.append({
                        'index': i,
                        'error': 'Failed to process image',
                        'success': False
                    })
                    
            except Exception as e:
                results.append({
                    'index': i,
                    'error': str(e),
                    'success': False
                })
        
        return jsonify({
            'batch_results': results,
            'total_images': len(images),
            'successful_detections': len([r for r in results if r.get('success', False)]),
            'timestamp': datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to process batch detection', 'details': str(e)}), 500

@disease_bp.route('/diseases/<crop_type>', methods=['GET'])
@jwt_required()
def get_crop_diseases(crop_type):
    """Get list of diseases for a specific crop type"""
    try:
        crop_type = crop_type.lower()
        
        if crop_type not in DISEASE_DATABASE:
            return jsonify({
                'error': 'Crop type not supported',
                'supported_crops': list(DISEASE_DATABASE.keys())
            }), 404
        
        diseases = []
        for disease_key, disease_info in DISEASE_DATABASE[crop_type].items():
            diseases.append({
                'disease_key': disease_key,
                'name': disease_info['name'],
                'symptoms': disease_info['symptoms'],
                'severity_levels': disease_info['severity_levels'],
                'prevention': disease_info['prevention']
            })
        
        return jsonify({
            'crop_type': crop_type,
            'diseases': diseases,
            'total_diseases': len(diseases),
            'timestamp': datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to fetch crop diseases', 'details': str(e)}), 500

@disease_bp.route('/prevention-guide', methods=['GET'])
@jwt_required()
def get_prevention_guide():
    """Get general disease prevention guide"""
    try:
        guide = {
            'general_prevention': [
                'Use disease-free seeds and planting material',
                'Practice crop rotation to break disease cycles',
                'Maintain proper plant spacing for good air circulation',
                'Avoid overhead watering to reduce leaf wetness',
                'Remove and destroy infected plant debris',
                'Keep fields clean and weed-free',
                'Monitor plants regularly for early disease signs',
                'Use resistant varieties when available'
            ],
            'soil_management': [
                'Maintain proper soil pH for your crops',
                'Ensure good drainage to prevent waterlogging',
                'Add organic matter to improve soil health',
                'Avoid excessive nitrogen fertilization',
                'Practice proper tillage to bury crop residues'
            ],
            'water_management': [
                'Water at the base of plants, not overhead',
                'Water early in the day to allow leaves to dry',
                'Avoid overwatering or underwatering',
                'Use drip irrigation when possible',
                'Monitor soil moisture levels regularly'
            ],
            'chemical_control': [
                'Apply fungicides preventively before disease appears',
                'Follow label instructions carefully',
                'Rotate different fungicide classes to prevent resistance',
                'Apply at recommended intervals and rates',
                'Consider organic alternatives when possible'
            ],
            'monitoring': [
                'Inspect plants weekly during growing season',
                'Look for early symptoms like spots, wilting, or discoloration',
                'Take photos of suspicious symptoms for identification',
                'Keep records of disease occurrences and treatments',
                'Consult with agricultural extension services when needed'
            ]
        }
        
        return jsonify({
            'prevention_guide': guide,
            'last_updated': '2024-01-15',
            'timestamp': datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to fetch prevention guide', 'details': str(e)}), 500

def generate_disease_recommendations(detection_result, crop_type, location):
    """Generate recommendations based on disease detection"""
    recommendations = []
    
    disease_name = detection_result['name']
    severity = detection_result.get('detected_severity', 'mild')
    confidence = detection_result.get('confidence', 0.8)
    
    # Immediate action recommendations
    if severity in ['moderate', 'severe']:
        recommendations.append({
            'priority': 'high',
            'type': 'immediate_action',
            'title': 'Immediate Treatment Required',
            'description': f'{disease_name} detected with {severity} severity. Take immediate action to prevent spread.',
            'actions': [
                'Apply recommended treatment immediately',
                'Isolate affected plants if possible',
                'Monitor surrounding plants closely',
                'Consider removing severely infected plants'
            ]
        })
    
    # Treatment recommendations
    if disease_name != 'No Disease Detected':
        recommendations.append({
            'priority': 'high' if severity == 'severe' else 'medium',
            'type': 'treatment',
            'title': 'Treatment Plan',
            'description': f'Recommended treatment for {disease_name}',
            'actions': [
                detection_result['treatment'],
                'Follow up with additional applications as needed',
                'Monitor treatment effectiveness',
                'Adjust treatment if no improvement in 7-10 days'
            ]
        })
    
    # Prevention recommendations
    recommendations.append({
        'priority': 'medium',
        'type': 'prevention',
        'title': 'Prevention Measures',
        'description': 'Steps to prevent future disease outbreaks',
        'actions': [
            detection_result['prevention'],
            'Implement regular monitoring schedule',
            'Consider crop rotation for next season',
            'Maintain optimal growing conditions'
        ]
    })
    
    # Monitoring recommendations
    recommendations.append({
        'priority': 'low',
        'type': 'monitoring',
        'title': 'Ongoing Monitoring',
        'description': 'Continue monitoring for disease progression',
        'actions': [
            'Check plants every 2-3 days',
            'Take photos to track disease progression',
            'Document treatment effectiveness',
            'Report any new symptoms immediately'
        ]
    })
    
    return recommendations
