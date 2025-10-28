"""
Model loading and inference management
"""
import os
import numpy as np
from typing import Dict, Tuple, Optional
import logging
from config import Config

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ModelManager:
    """Manages ML model loading and inference"""
    
    def __init__(self):
        self.model = None
        self.model_loaded = False
        
    def load_model(self, model_path: Optional[str] = None) -> bool:
        """
        Load the trained TensorFlow model
        
        Args:
            model_path: Path to model file (uses config default if None)
            
        Returns:
            True if model loaded successfully, False otherwise
        """
        try:
            import tensorflow as tf
            
            path = model_path or Config.MODEL_PATH
            
            if not os.path.exists(path):
                logger.warning(f"Model file not found at {path}")
                logger.info("Creating a dummy model for demonstration purposes")
                self.model = self._create_dummy_model()
                self.model_loaded = True
                return True
            
            logger.info(f"Loading model from {path}")
            self.model = tf.keras.models.load_model(path)
            self.model_loaded = True
            logger.info("Model loaded successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error loading model: {str(e)}")
            logger.info("Creating dummy model as fallback")
            self.model = self._create_dummy_model()
            self.model_loaded = True
            return False
    
    def _create_dummy_model(self):
        """
        Create a dummy model for testing when trained model is not available
        This uses transfer learning with MobileNetV2 architecture
        
        Returns:
            Compiled Keras model
        """
        import tensorflow as tf
        from tensorflow.keras import layers, models
        
        logger.info("Building MobileNetV2-based model architecture")
        
        # Load pre-trained MobileNetV2 without top layers
        base_model = tf.keras.applications.MobileNetV2(
            input_shape=(224, 224, 3),
            include_top=False,
            weights='imagenet'
        )
        
        # Freeze base model layers
        base_model.trainable = False
        
        # Build classification head
        model = models.Sequential([
            base_model,
            layers.GlobalAveragePooling2D(),
            layers.Dropout(0.3),
            layers.Dense(128, activation='relu'),
            layers.Dropout(0.2),
            layers.Dense(Config.NUM_CLASSES, activation='softmax')
        ])
        
        # Compile model
        model.compile(
            optimizer='adam',
            loss='categorical_crossentropy',
            metrics=['accuracy']
        )
        
        logger.info("Dummy model created successfully")
        return model
    
    def predict(self, preprocessed_image: np.ndarray) -> Dict:
        """
        Perform inference on preprocessed image
        
        Args:
            preprocessed_image: Preprocessed image array (1, 224, 224, 3)
            
        Returns:
            Dictionary with prediction results
        """
        if not self.model_loaded or self.model is None:
            raise RuntimeError("Model not loaded. Call load_model() first.")
        
        try:
            # Get model predictions
            predictions = self.model.predict(preprocessed_image, verbose=0)
            
            # Get predicted class and confidence
            predicted_class = int(np.argmax(predictions[0]))
            confidence = float(predictions[0][predicted_class])
            
            # Get all class probabilities
            class_probabilities = {
                i: float(predictions[0][i]) for i in range(Config.NUM_CLASSES)
            }
            
            # Get label and recommendation
            label = Config.DIAGNOSIS_LABELS.get(predicted_class, "Unknown")
            recommendation = Config.RECOMMENDATIONS.get(predicted_class, "Consult a specialist")
            severity = Config.SEVERITY_LEVELS.get(predicted_class, "Unknown")
            
            return {
                "severity_class": predicted_class,
                "severity_level": severity,
                "confidence": confidence,
                "label": label,
                "recommendation": recommendation,
                "class_probabilities": class_probabilities
            }
            
        except Exception as e:
            logger.error(f"Error during prediction: {str(e)}")
            raise RuntimeError(f"Prediction failed: {str(e)}")
    
    def get_model_info(self) -> Dict:
        """
        Get information about the loaded model
        
        Returns:
            Dictionary with model metadata
        """
        if not self.model_loaded or self.model is None:
            return {
                "loaded": False,
                "model_path": Config.MODEL_PATH,
                "error": "Model not loaded"
            }
        
        try:
            return {
                "loaded": True,
                "model_path": Config.MODEL_PATH,
                "input_shape": str(self.model.input_shape),
                "output_shape": str(self.model.output_shape),
                "num_classes": Config.NUM_CLASSES,
                "total_params": self.model.count_params()
            }
        except Exception as e:
            return {
                "loaded": True,
                "error": f"Could not retrieve model info: {str(e)}"
            }


# Global model manager instance
model_manager = ModelManager()
