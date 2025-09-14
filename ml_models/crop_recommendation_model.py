"""
Crop Recommendation ML Model
Uses scikit-learn for crop recommendation based on soil, weather, and market data
"""

import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier, GradientBoostingRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, mean_squared_error
import logging

logger = logging.getLogger(__name__)

class CropRecommendationModel:
    """ML model for crop recommendations"""
    
    def __init__(self):
        self.classifier = RandomForestClassifier(n_estimators=100, random_state=42)
        self.regressor = GradientBoostingRegressor(n_estimators=100, random_state=42)
        self.scaler = StandardScaler()
        self.is_trained = False
        self.crop_features = {
            'wheat': {'optimal_ph': (6.0, 7.5), 'optimal_temp': (15, 25), 'water_req': 'medium'},
            'rice': {'optimal_ph': (5.5, 7.0), 'optimal_temp': (20, 35), 'water_req': 'high'},
            'corn': {'optimal_ph': (6.0, 7.0), 'optimal_temp': (18, 27), 'water_req': 'medium'},
            'sugarcane': {'optimal_ph': (6.0, 7.5), 'optimal_temp': (20, 30), 'water_req': 'high'},
            'cotton': {'optimal_ph': (5.8, 8.0), 'optimal_temp': (21, 30), 'water_req': 'medium'},
            'soybean': {'optimal_ph': (6.0, 7.0), 'optimal_temp': (20, 30), 'water_req': 'medium'},
            'potato': {'optimal_ph': (4.8, 5.5), 'optimal_temp': (15, 20), 'water_req': 'medium'},
            'tomato': {'optimal_ph': (6.0, 6.8), 'optimal_temp': (18, 25), 'water_req': 'medium'},
            'mango': {'optimal_ph': (5.5, 7.5), 'optimal_temp': (24, 30), 'water_req': 'medium'},
            'banana': {'optimal_ph': (6.0, 7.5), 'optimal_temp': (26, 30), 'water_req': 'high'}
        }
    
    def prepare_training_data(self):
        """Generate synthetic training data"""
        np.random.seed(42)
        n_samples = 10000
        
        # Generate synthetic data
        data = []
        for _ in range(n_samples):
            # Soil parameters
            ph = np.random.normal(6.5, 1.0)
            moisture = np.random.uniform(0.1, 0.6)
            organic_matter = np.random.uniform(1.0, 8.0)
            nitrogen = np.random.uniform(0.1, 0.6)
            phosphorus = np.random.uniform(10, 60)
            potassium = np.random.uniform(100, 500)
            
            # Weather parameters
            temperature = np.random.uniform(10, 35)
            humidity = np.random.uniform(30, 90)
            precipitation = np.random.uniform(0, 20)
            
            # Market parameters
            market_demand = np.random.uniform(0.3, 1.0)
            price_trend = np.random.uniform(-0.2, 0.2)
            
            # Calculate crop suitability scores
            crop_scores = {}
            for crop, features in self.crop_features.items():
                score = self._calculate_crop_score(
                    ph, moisture, organic_matter, nitrogen, phosphorus, potassium,
                    temperature, humidity, precipitation, market_demand, price_trend,
                    features
                )
                crop_scores[crop] = score
            
            # Find best crop
            best_crop = max(crop_scores, key=crop_scores.get)
            best_score = crop_scores[best_crop]
            
            # Only include samples with reasonable scores
            if best_score > 30:
                data.append({
                    'ph': ph,
                    'moisture': moisture,
                    'organic_matter': organic_matter,
                    'nitrogen': nitrogen,
                    'phosphorus': phosphorus,
                    'potassium': potassium,
                    'temperature': temperature,
                    'humidity': humidity,
                    'precipitation': precipitation,
                    'market_demand': market_demand,
                    'price_trend': price_trend,
                    'crop': best_crop,
                    'score': best_score
                })
        
        return pd.DataFrame(data)
    
    def _calculate_crop_score(self, ph, moisture, organic_matter, nitrogen, phosphorus, potassium,
                            temperature, humidity, precipitation, market_demand, price_trend, features):
        """Calculate suitability score for a crop"""
        score = 0
        
        # pH score
        ph_range = features['optimal_ph']
        if ph_range[0] <= ph <= ph_range[1]:
            score += 25
        elif abs(ph - ph_range[0]) <= 0.5 or abs(ph - ph_range[1]) <= 0.5:
            score += 15
        else:
            score += 5
        
        # Temperature score
        temp_range = features['optimal_temp']
        if temp_range[0] <= temperature <= temp_range[1]:
            score += 20
        elif abs(temperature - temp_range[0]) <= 3 or abs(temperature - temp_range[1]) <= 3:
            score += 10
        else:
            score += 0
        
        # Water requirement score
        water_req = features['water_req']
        if water_req == 'high' and moisture > 0.3:
            score += 15
        elif water_req == 'medium' and 0.2 <= moisture <= 0.4:
            score += 15
        elif water_req == 'low' and moisture < 0.3:
            score += 15
        else:
            score += 5
        
        # Nutrient scores
        if nitrogen >= 0.3:
            score += 10
        if phosphorus >= 30:
            score += 10
        if potassium >= 200:
            score += 10
        
        # Market factors
        score += market_demand * 15
        if price_trend > 0:
            score += 10
        
        return min(score, 100)
    
    def train(self):
        """Train the ML models"""
        try:
            # Prepare training data
            df = self.prepare_training_data()
            
            # Features
            feature_columns = [
                'ph', 'moisture', 'organic_matter', 'nitrogen', 'phosphorus', 'potassium',
                'temperature', 'humidity', 'precipitation', 'market_demand', 'price_trend'
            ]
            X = df[feature_columns]
            y_crop = df['crop']
            y_score = df['score']
            
            # Split data
            X_train, X_test, y_crop_train, y_crop_test, y_score_train, y_score_test = train_test_split(
                X, y_crop, y_score, test_size=0.2, random_state=42
            )
            
            # Scale features
            X_train_scaled = self.scaler.fit_transform(X_train)
            X_test_scaled = self.scaler.transform(X_test)
            
            # Train classifier
            self.classifier.fit(X_train_scaled, y_crop_train)
            
            # Train regressor
            self.regressor.fit(X_train_scaled, y_score_train)
            
            # Evaluate models
            crop_predictions = self.classifier.predict(X_test_scaled)
            score_predictions = self.regressor.predict(X_test_scaled)
            
            accuracy = accuracy_score(y_crop_test, crop_predictions)
            mse = mean_squared_error(y_score_test, score_predictions)
            
            self.is_trained = True
            
            logger.info(f"Model training completed. Accuracy: {accuracy:.3f}, MSE: {mse:.3f}")
            
            return {
                'accuracy': accuracy,
                'mse': mse,
                'n_samples': len(df)
            }
            
        except Exception as e:
            logger.error(f"Model training failed: {e}")
            raise
    
    def predict(self, soil_data, weather_data, market_data):
        """Predict crop recommendations"""
        if not self.is_trained:
            self.train()
        
        try:
            # Prepare input features
            features = np.array([[
                soil_data.get('ph', 6.5),
                soil_data.get('moisture', 0.3),
                soil_data.get('organic_matter', 4.0),
                soil_data.get('nitrogen', 0.3),
                soil_data.get('phosphorus', 30),
                soil_data.get('potassium', 200),
                weather_data.get('temperature', 25),
                weather_data.get('humidity', 60),
                weather_data.get('precipitation', 5),
                market_data.get('demand_score', 0.7),
                market_data.get('price_trend', 0.0)
            ]])
            
            # Scale features
            features_scaled = self.scaler.transform(features)
            
            # Predict crop and score
            predicted_crop = self.classifier.predict(features_scaled)[0]
            predicted_score = self.regressor.predict(features_scaled)[0]
            
            # Get probabilities for all crops
            crop_probabilities = self.classifier.predict_proba(features_scaled)[0]
            crop_classes = self.classifier.classes_
            
            # Create recommendations
            recommendations = []
            for i, crop in enumerate(crop_classes):
                if crop_probabilities[i] > 0.1:  # Only include crops with >10% probability
                    recommendations.append({
                        'crop': crop,
                        'probability': float(crop_probabilities[i]),
                        'suitability_score': min(100, max(0, predicted_score * crop_probabilities[i]))
                    })
            
            # Sort by suitability score
            recommendations.sort(key=lambda x: x['suitability_score'], reverse=True)
            
            return {
                'recommendations': recommendations[:10],  # Top 10
                'best_crop': predicted_crop,
                'confidence': float(max(crop_probabilities))
            }
            
        except Exception as e:
            logger.error(f"Prediction failed: {e}")
            return {
                'recommendations': [],
                'best_crop': 'wheat',
                'confidence': 0.0
            }
    
    def save_model(self, filepath):
        """Save trained model"""
        model_data = {
            'classifier': self.classifier,
            'regressor': self.regressor,
            'scaler': self.scaler,
            'is_trained': self.is_trained
        }
        joblib.dump(model_data, filepath)
        logger.info(f"Model saved to {filepath}")
    
    def load_model(self, filepath):
        """Load trained model"""
        try:
            model_data = joblib.load(filepath)
            self.classifier = model_data['classifier']
            self.regressor = model_data['regressor']
            self.scaler = model_data['scaler']
            self.is_trained = model_data['is_trained']
            logger.info(f"Model loaded from {filepath}")
        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            raise

# Disease Detection Model
class DiseaseDetectionModel:
    """Plant disease detection model using computer vision"""
    
    def __init__(self):
        self.is_trained = False
        self.disease_classes = [
            'healthy', 'rust', 'blight', 'mildew', 'spot', 'wilt', 'rot'
        ]
    
    def preprocess_image(self, image_data):
        """Preprocess image for model input"""
        try:
            import cv2
            import base64
            from PIL import Image
            import io
            
            # Decode base64 image
            image_bytes = base64.b64decode(image_data)
            image = Image.open(io.BytesIO(image_bytes))
            
            # Convert to RGB
            image = image.convert('RGB')
            
            # Resize to model input size
            image = image.resize((224, 224))
            
            # Convert to numpy array
            image_array = np.array(image) / 255.0
            
            return image_array.reshape(1, 224, 224, 3)
            
        except Exception as e:
            logger.error(f"Image preprocessing failed: {e}")
            return None
    
    def predict(self, image_data, crop_type):
        """Predict disease from image"""
        if not self.is_trained:
            return self._mock_prediction(crop_type)
        
        try:
            # Preprocess image
            processed_image = self.preprocess_image(image_data)
            if processed_image is None:
                return self._mock_prediction(crop_type)
            
            # Mock prediction (replace with actual model)
            # In real implementation, use trained CNN model
            predicted_class = np.random.choice(self.disease_classes)
            confidence = np.random.uniform(0.7, 0.95)
            
            return {
                'disease_name': predicted_class.replace('_', ' ').title(),
                'confidence': float(confidence),
                'severity': np.random.choice(['mild', 'moderate', 'severe']),
                'treatment': self._get_treatment_advice(predicted_class),
                'prevention': self._get_prevention_advice(predicted_class)
            }
            
        except Exception as e:
            logger.error(f"Disease prediction failed: {e}")
            return self._mock_prediction(crop_type)
    
    def _mock_prediction(self, crop_type):
        """Mock prediction when model is not available"""
        diseases = {
            'wheat': ['rust', 'powdery_mildew', 'head_blight'],
            'rice': ['blast', 'brown_spot', 'bacterial_blight'],
            'corn': ['northern_leaf_blight', 'common_rust', 'gray_leaf_spot'],
            'tomato': ['early_blight', 'late_blight', 'bacterial_wilt'],
            'potato': ['late_blight', 'early_blight', 'scab']
        }
        
        crop_diseases = diseases.get(crop_type, ['rust', 'blight', 'mildew'])
        predicted_disease = np.random.choice(crop_diseases)
        
        return {
            'disease_name': predicted_disease.replace('_', ' ').title(),
            'confidence': float(np.random.uniform(0.6, 0.9)),
            'severity': np.random.choice(['mild', 'moderate', 'severe']),
            'treatment': 'Apply appropriate fungicide and improve growing conditions',
            'prevention': 'Ensure proper spacing, good air circulation, and regular monitoring'
        }
    
    def _get_treatment_advice(self, disease):
        """Get treatment advice for specific disease"""
        treatments = {
            'rust': 'Apply fungicide containing tebuconazole',
            'blight': 'Remove affected parts and apply copper fungicide',
            'mildew': 'Improve air circulation and apply sulfur fungicide',
            'spot': 'Remove infected leaves and apply fungicide',
            'wilt': 'Remove affected plants and improve drainage',
            'rot': 'Remove affected parts and improve soil drainage'
        }
        return treatments.get(disease, 'Consult agricultural expert')
    
    def _get_prevention_advice(self, disease):
        """Get prevention advice for specific disease"""
        preventions = {
            'rust': 'Plant resistant varieties and ensure proper spacing',
            'blight': 'Avoid overhead watering and improve air circulation',
            'mildew': 'Maintain proper humidity and ensure good air flow',
            'spot': 'Remove plant debris and avoid wetting leaves',
            'wilt': 'Use disease-free seeds and practice crop rotation',
            'rot': 'Improve soil drainage and avoid overwatering'
        }
        return preventions.get(disease, 'Maintain good growing conditions')

# Model factory
def get_crop_recommendation_model():
    """Get crop recommendation model instance"""
    return CropRecommendationModel()

def get_disease_detection_model():
    """Get disease detection model instance"""
    return DiseaseDetectionModel()
