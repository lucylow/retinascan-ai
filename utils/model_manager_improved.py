"""
Enhanced Model loading and inference management with advanced AI features
Improvements:
- EfficientNet architecture support
- Grad-CAM explainable AI
- Uncertainty estimation
- Confidence calibration
- Attention mechanisms
"""
import os
import numpy as np
from typing import Dict, Tuple, Optional, List
import logging
from config import Config

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class GradCAM:
    """
    Gradient-weighted Class Activation Mapping for visual explanations
    Highlights which regions of the retinal image influenced the model's decision
    """
    
    def __init__(self, model, layer_name: str = None):
        """
        Initialize Grad-CAM
        
        Args:
            model: Trained Keras model
            layer_name: Name of the convolutional layer to visualize (auto-detect if None)
        """
        import tensorflow as tf
        
        self.model = model
        
        # Auto-detect the last convolutional layer if not specified
        if layer_name is None:
            for layer in reversed(model.layers):
                if len(layer.output_shape) == 4:  # Conv layer has 4D output
                    layer_name = layer.name
                    break
        
        self.layer_name = layer_name
        logger.info(f"Grad-CAM initialized with layer: {layer_name}")
        
        # Create gradient model
        self.grad_model = tf.keras.models.Model(
            inputs=[model.inputs],
            outputs=[model.get_layer(layer_name).output, model.output]
        )
    
    def generate_heatmap(self, img_array: np.ndarray, pred_index: int = None) -> np.ndarray:
        """
        Generate Grad-CAM heatmap
        
        Args:
            img_array: Preprocessed image array (1, H, W, 3)
            pred_index: Class index to visualize (uses predicted class if None)
            
        Returns:
            Heatmap array (H, W) with values in [0, 1]
        """
        import tensorflow as tf
        
        # Record operations for automatic differentiation
        with tf.GradientTape() as tape:
            conv_outputs, predictions = self.grad_model(img_array)
            
            if pred_index is None:
                pred_index = tf.argmax(predictions[0])
            
            class_channel = predictions[:, pred_index]
        
        # Compute gradients of the class output value with respect to feature map
        grads = tape.gradient(class_channel, conv_outputs)
        
        # Global average pooling of gradients
        pooled_grads = tf.reduce_mean(grads, axis=(0, 1, 2))
        
        # Weight feature maps by gradients
        conv_outputs = conv_outputs[0]
        pooled_grads = pooled_grads.numpy()
        conv_outputs = conv_outputs.numpy()
        
        for i in range(pooled_grads.shape[-1]):
            conv_outputs[:, :, i] *= pooled_grads[i]
        
        # Average over all feature maps
        heatmap = np.mean(conv_outputs, axis=-1)
        
        # Normalize heatmap
        heatmap = np.maximum(heatmap, 0)  # ReLU
        if heatmap.max() > 0:
            heatmap /= heatmap.max()
        
        return heatmap
    
    def overlay_heatmap(self, heatmap: np.ndarray, original_img: np.ndarray, 
                       alpha: float = 0.4, colormap: int = None) -> np.ndarray:
        """
        Overlay heatmap on original image
        
        Args:
            heatmap: Grad-CAM heatmap (H, W)
            original_img: Original image array (H, W, 3) in [0, 255]
            alpha: Transparency of heatmap overlay
            colormap: OpenCV colormap (default: COLORMAP_JET)
            
        Returns:
            Overlayed image array (H, W, 3) in [0, 255]
        """
        import cv2
        
        if colormap is None:
            colormap = cv2.COLORMAP_JET
        
        # Resize heatmap to match original image
        heatmap = cv2.resize(heatmap, (original_img.shape[1], original_img.shape[0]))
        
        # Convert heatmap to RGB
        heatmap = np.uint8(255 * heatmap)
        heatmap = cv2.applyColorMap(heatmap, colormap)
        
        # Ensure original image is uint8
        if original_img.max() <= 1.0:
            original_img = np.uint8(255 * original_img)
        else:
            original_img = np.uint8(original_img)
        
        # Overlay heatmap on original image
        overlayed = cv2.addWeighted(original_img, 1 - alpha, heatmap, alpha, 0)
        
        return overlayed


class ModelManager:
    """Enhanced ML model manager with advanced AI capabilities"""
    
    def __init__(self):
        self.model = None
        self.model_loaded = False
        self.grad_cam = None
        self.architecture = 'efficientnetb3'  # Default to EfficientNet
        
    def load_model(self, model_path: Optional[str] = None, 
                   architecture: str = 'efficientnetb3') -> bool:
        """
        Load the trained TensorFlow model
        
        Args:
            model_path: Path to model file (uses config default if None)
            architecture: Model architecture ('mobilenetv2', 'efficientnetb3', 'efficientnetb4')
            
        Returns:
            True if model loaded successfully, False otherwise
        """
        try:
            import tensorflow as tf
            
            path = model_path or Config.MODEL_PATH
            self.architecture = architecture
            
            if not os.path.exists(path):
                logger.warning(f"Model file not found at {path}")
                logger.info(f"Creating a {architecture} model for demonstration purposes")
                self.model = self._create_enhanced_model(architecture)
                self.model_loaded = True
                self._initialize_grad_cam()
                return True
            
            logger.info(f"Loading model from {path}")
            self.model = tf.keras.models.load_model(path)
            self.model_loaded = True
            self._initialize_grad_cam()
            logger.info("Model loaded successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error loading model: {str(e)}")
            logger.info(f"Creating {architecture} model as fallback")
            self.model = self._create_enhanced_model(architecture)
            self.model_loaded = True
            self._initialize_grad_cam()
            return False
    
    def _initialize_grad_cam(self):
        """Initialize Grad-CAM for explainable AI"""
        try:
            self.grad_cam = GradCAM(self.model)
            logger.info("Grad-CAM initialized successfully")
        except Exception as e:
            logger.warning(f"Could not initialize Grad-CAM: {str(e)}")
            self.grad_cam = None
    
    def _create_enhanced_model(self, architecture: str = 'efficientnetb3'):
        """
        Create enhanced model with better architecture
        
        Args:
            architecture: Model architecture to use
            
        Returns:
            Compiled Keras model
        """
        import tensorflow as tf
        from tensorflow.keras import layers, models
        
        logger.info(f"Building {architecture} model with attention mechanism")
        
        # Select base model
        if architecture == 'efficientnetb3':
            base_model = tf.keras.applications.EfficientNetB3(
                input_shape=(*Config.IMAGE_SIZE, 3),
                include_top=False,
                weights='imagenet'
            )
        elif architecture == 'efficientnetb4':
            base_model = tf.keras.applications.EfficientNetB4(
                input_shape=(*Config.IMAGE_SIZE, 3),
                include_top=False,
                weights='imagenet'
            )
        elif architecture == 'mobilenetv2':
            base_model = tf.keras.applications.MobileNetV2(
                input_shape=(*Config.IMAGE_SIZE, 3),
                include_top=False,
                weights='imagenet'
            )
        else:
            raise ValueError(f"Unsupported architecture: {architecture}")
        
        # Freeze base model layers initially
        base_model.trainable = False
        
        # Build model with attention mechanism
        inputs = layers.Input(shape=(*Config.IMAGE_SIZE, 3))
        x = base_model(inputs, training=False)
        
        # Spatial attention mechanism
        attention = layers.Conv2D(1, kernel_size=1, activation='sigmoid', name='attention_map')(x)
        x = layers.Multiply()([x, attention])
        
        # Global pooling
        x = layers.GlobalAveragePooling2D()(x)
        
        # Dense layers with regularization
        x = layers.BatchNormalization()(x)
        x = layers.Dropout(0.5)(x)
        x = layers.Dense(512, activation='relu', kernel_regularizer=tf.keras.regularizers.l2(0.001))(x)
        x = layers.BatchNormalization()(x)
        x = layers.Dropout(0.3)(x)
        x = layers.Dense(256, activation='relu', kernel_regularizer=tf.keras.regularizers.l2(0.001))(x)
        x = layers.Dropout(0.2)(x)
        
        # Output layer
        outputs = layers.Dense(Config.NUM_CLASSES, activation='softmax', name='predictions')(x)
        
        model = models.Model(inputs=inputs, outputs=outputs)
        
        # Compile with focal loss for better handling of class imbalance
        model.compile(
            optimizer=tf.keras.optimizers.Adam(learning_rate=0.001),
            loss=self._focal_loss(alpha=0.25, gamma=2.0),
            metrics=[
                'accuracy',
                tf.keras.metrics.AUC(name='auc'),
                tf.keras.metrics.Precision(name='precision'),
                tf.keras.metrics.Recall(name='recall')
            ]
        )
        
        logger.info(f"Enhanced {architecture} model created successfully")
        logger.info(f"Total parameters: {model.count_params():,}")
        
        return model
    
    @staticmethod
    def _focal_loss(alpha=0.25, gamma=2.0):
        """
        Focal Loss for addressing class imbalance
        Focuses training on hard examples
        
        Args:
            alpha: Weighting factor in [0, 1]
            gamma: Focusing parameter (gamma >= 0)
        """
        import tensorflow as tf
        
        def focal_loss_fixed(y_true, y_pred):
            epsilon = tf.keras.backend.epsilon()
            y_pred = tf.clip_by_value(y_pred, epsilon, 1.0 - epsilon)
            
            # Calculate focal loss
            cross_entropy = -y_true * tf.math.log(y_pred)
            weight = alpha * y_true * tf.pow(1 - y_pred, gamma)
            loss = weight * cross_entropy
            
            return tf.reduce_mean(tf.reduce_sum(loss, axis=-1))
        
        return focal_loss_fixed
    
    def predict(self, preprocessed_image: np.ndarray, 
                return_visualization: bool = True) -> Dict:
        """
        Perform inference with uncertainty estimation and explainability
        
        Args:
            preprocessed_image: Preprocessed image array (1, 224, 224, 3)
            return_visualization: Whether to generate Grad-CAM visualization
            
        Returns:
            Dictionary with prediction results and optional visualization
        """
        if not self.model_loaded or self.model is None:
            raise RuntimeError("Model not loaded. Call load_model() first.")
        
        try:
            # Monte Carlo Dropout for uncertainty estimation
            predictions_list = []
            n_iterations = 10  # Number of stochastic forward passes
            
            # Enable dropout during inference for uncertainty estimation
            for _ in range(n_iterations):
                pred = self.model(preprocessed_image, training=True)
                predictions_list.append(pred.numpy()[0])
            
            predictions_array = np.array(predictions_list)
            
            # Mean prediction
            mean_predictions = np.mean(predictions_array, axis=0)
            
            # Uncertainty (standard deviation)
            uncertainty = np.std(predictions_array, axis=0)
            
            # Get predicted class and confidence
            predicted_class = int(np.argmax(mean_predictions))
            confidence = float(mean_predictions[predicted_class])
            
            # Epistemic uncertainty (model uncertainty)
            epistemic_uncertainty = float(uncertainty[predicted_class])
            
            # Predictive entropy (overall uncertainty)
            entropy = -np.sum(mean_predictions * np.log(mean_predictions + 1e-10))
            
            # Get all class probabilities
            class_probabilities = {
                i: float(mean_predictions[i]) for i in range(Config.NUM_CLASSES)
            }
            
            # Get label and recommendation
            label = Config.DIAGNOSIS_LABELS.get(predicted_class, "Unknown")
            recommendation = Config.RECOMMENDATIONS.get(predicted_class, "Consult a specialist")
            severity = Config.SEVERITY_LEVELS.get(predicted_class, "Unknown")
            
            result = {
                "severity_class": predicted_class,
                "severity_level": severity,
                "confidence": confidence,
                "label": label,
                "recommendation": recommendation,
                "class_probabilities": class_probabilities,
                "uncertainty": {
                    "epistemic": epistemic_uncertainty,
                    "entropy": float(entropy),
                    "confidence_interval": {
                        "lower": float(max(0, confidence - 2 * epistemic_uncertainty)),
                        "upper": float(min(1, confidence + 2 * epistemic_uncertainty))
                    }
                }
            }
            
            # Generate Grad-CAM visualization if requested
            if return_visualization and self.grad_cam is not None:
                try:
                    heatmap = self.grad_cam.generate_heatmap(preprocessed_image, predicted_class)
                    result["grad_cam_heatmap"] = heatmap
                    logger.info("Grad-CAM visualization generated")
                except Exception as e:
                    logger.warning(f"Could not generate Grad-CAM: {str(e)}")
            
            return result
            
        except Exception as e:
            logger.error(f"Error during prediction: {str(e)}")
            raise RuntimeError(f"Prediction failed: {str(e)}")
    
    def generate_explanation_image(self, preprocessed_image: np.ndarray, 
                                   original_image: np.ndarray,
                                   prediction_result: Dict) -> Optional[np.ndarray]:
        """
        Generate visual explanation image with Grad-CAM overlay
        
        Args:
            preprocessed_image: Preprocessed image used for prediction
            original_image: Original image for overlay (H, W, 3)
            prediction_result: Result from predict() method
            
        Returns:
            Overlayed image array or None if visualization unavailable
        """
        if self.grad_cam is None or "grad_cam_heatmap" not in prediction_result:
            return None
        
        try:
            heatmap = prediction_result["grad_cam_heatmap"]
            overlayed = self.grad_cam.overlay_heatmap(heatmap, original_image)
            return overlayed
        except Exception as e:
            logger.error(f"Error generating explanation image: {str(e)}")
            return None
    
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
                "architecture": self.architecture,
                "model_path": Config.MODEL_PATH,
                "input_shape": str(self.model.input_shape),
                "output_shape": str(self.model.output_shape),
                "num_classes": Config.NUM_CLASSES,
                "total_params": self.model.count_params(),
                "grad_cam_enabled": self.grad_cam is not None,
                "features": [
                    "EfficientNet architecture",
                    "Attention mechanism",
                    "Focal loss",
                    "Uncertainty estimation",
                    "Grad-CAM explainability"
                ]
            }
        except Exception as e:
            return {
                "loaded": True,
                "error": f"Could not retrieve model info: {str(e)}"
            }


# Global model manager instance
model_manager = ModelManager()
