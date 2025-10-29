import tensorflow as tf
import numpy as np
import logging
from config import Config
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RetinaModel:
    """Handles loading and prediction using the trained retina model"""
    
    def __init__(self):
        self.model = None
        self.load_model()
    
    def load_model(self):
        """Load the trained TensorFlow model"""
        try:
            model_path = Config.MODEL_PATH
            
            # Check if model file exists
            if not os.path.exists(model_path):
                logger.warning(f"Model file not found at {model_path}. Using mock model for demonstration.")
                self.model = self._create_mock_model()
                return
            
            # Load the actual model
            self.model = tf.keras.models.load_model(model_path)
            logger.info("Retina model loaded successfully")
            
        except Exception as e:
            logger.error(f"Error loading model: {str(e)}")
            logger.info("Falling back to mock model")
            self.model = self._create_mock_model()
    
    def _create_mock_model(self):
        """Create a mock model for demonstration purposes"""
        # This is a simple CNN that would be replaced with your trained model
        model = tf.keras.Sequential([
            tf.keras.layers.Conv2D(32, (3, 3), activation='relu', input_shape=(224, 224, 3)),
            tf.keras.layers.MaxPooling2D(2, 2),
            tf.keras.layers.Conv2D(64, (3, 3), activation='relu'),
            tf.keras.layers.MaxPooling2D(2, 2),
            tf.keras.layers.Conv2D(128, (3, 3), activation='relu'),
            tf.keras.layers.MaxPooling2D(2, 2),
            tf.keras.layers.Flatten(),
            tf.keras.layers.Dense(512, activation='relu'),
            tf.keras.layers.Dense(5, activation='softmax')
        ])
        
        # Compile with dummy weights
        model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])
        return model
    
    def predict(self, processed_image):
        """
        Make prediction on processed image
        Args:
            processed_image: Preprocessed image array
        Returns:
            Dictionary with prediction results
        """
        try:
            # Make prediction
            predictions = self.model.predict(processed_image)
            predicted_class = np.argmax(predictions[0])
            confidence = float(np.max(predictions[0]))
            
            # Get all class probabilities
            class_probabilities = {
                Config.DIAGNOSIS_LABELS[i]: float(predictions[0][i]) 
                for i in range(len(Config.DIAGNOSIS_LABELS))
            }
            
            return {
                'diagnosis': Config.DIAGNOSIS_LABELS[predicted_class],
                'severity_level': int(predicted_class),
                'confidence': confidence,
                'probabilities': class_probabilities,
                'recommendation': Config.RECOMMENDATIONS[predicted_class],
            }
            
        except Exception as e:
            logger.error(f"Error during prediction: {str(e)}")
            raise RuntimeError(f"Prediction failed: {str(e)}")
    
    def get_model_info(self):
        """Get information about the loaded model"""
        if self.model is None:
            return {"error": "Model not loaded"}
        
        return {
            "model_loaded": True,
            "input_shape": str(self.model.input_shape),
            "output_shape": str(self.model.output_shape),
            "layers": len(self.model.layers)
        }

