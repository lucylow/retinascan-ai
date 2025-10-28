"""
Enhanced RetinaScan AI - Prediction Service
Improvements:
- Grad-CAM visualization support
- Uncertainty estimation
- Enhanced recommendations with risk stratification
- Image quality metrics in response
- Visual explanation generation
"""
import logging
import base64
import io
from typing import Dict, Any, Tuple
import numpy as np
import cv2

from fastapi import HTTPException

from ..config import Config
from ..utils.image_processor_improved import ImageProcessor
from ..utils.model_manager_improved import model_manager

logger = logging.getLogger(__name__)


class PredictionService:
    """
    Enhanced service class for end-to-end prediction with explainability
    """
    
    @staticmethod
    def _validate_file(filename: str, contents: bytes):
        """Validates file extension and size."""
        # Validate file extension
        if not ImageProcessor.validate_file_extension(filename):
            raise HTTPException(
                status_code=400,
                detail=f"Invalid file type. Allowed types: {', '.join(Config.ALLOWED_EXTENSIONS)}"
            )
        
        # Validate file size
        if len(contents) > Config.MAX_UPLOAD_SIZE:
            raise HTTPException(
                status_code=400,
                detail=f"File too large. Maximum size: {Config.MAX_UPLOAD_SIZE / (1024*1024):.2f}MB"
            )

    @staticmethod
    def _validate_image_integrity(contents: bytes):
        """Validates the integrity and quality of the image content."""
        is_valid, error_msg = ImageProcessor.validate_image(contents)
        if not is_valid:
            raise HTTPException(status_code=400, detail=error_msg)

    @staticmethod
    def _preprocess_image(contents: bytes) -> Tuple[Any, Any]:
        """
        Preprocesses the image for model inference
        
        Returns:
            Tuple of (preprocessed_image, original_image)
        """
        try:
            return ImageProcessor.preprocess_for_model(contents, use_ben_graham=True)
        except Exception as e:
            logger.error(f"Image preprocessing failed: {str(e)}")
            raise HTTPException(
                status_code=400,
                detail=f"Image preprocessing failed: {str(e)}"
            )

    @staticmethod
    def _encode_image_to_base64(image_array: np.ndarray) -> str:
        """
        Encode image array to base64 string for API response
        
        Args:
            image_array: Image array (H, W, 3)
            
        Returns:
            Base64 encoded string
        """
        try:
            # Convert RGB to BGR for OpenCV
            if len(image_array.shape) == 3:
                image_bgr = cv2.cvtColor(image_array, cv2.COLOR_RGB2BGR)
            else:
                image_bgr = image_array
            
            # Encode to PNG
            success, buffer = cv2.imencode('.png', image_bgr)
            if not success:
                raise ValueError("Failed to encode image")
            
            # Convert to base64
            base64_str = base64.b64encode(buffer).decode('utf-8')
            return f"data:image/png;base64,{base64_str}"
            
        except Exception as e:
            logger.error(f"Image encoding failed: {str(e)}")
            return None

    @staticmethod
    def _get_risk_stratification(severity_level: str, confidence: float, 
                                 uncertainty: Dict) -> Dict[str, Any]:
        """
        Enhanced risk stratification based on severity, confidence, and uncertainty
        
        Args:
            severity_level: Predicted severity level
            confidence: Prediction confidence
            uncertainty: Uncertainty metrics
            
        Returns:
            Risk stratification dictionary
        """
        # Base risk levels
        risk_map = {
            "None": "Low",
            "Mild": "Medium",
            "Moderate": "High",
            "Severe": "Critical",
            "Proliferative": "Emergency"
        }
        
        base_risk = risk_map.get(severity_level, "Unknown")
        
        # Adjust risk based on confidence and uncertainty
        epistemic_uncertainty = uncertainty.get('epistemic', 0)
        entropy = uncertainty.get('entropy', 0)
        
        # High uncertainty increases risk
        if epistemic_uncertainty > 0.15 or entropy > 1.0:
            uncertainty_flag = "High"
            recommendation_note = "Due to high prediction uncertainty, recommend professional verification."
        elif epistemic_uncertainty > 0.08 or entropy > 0.5:
            uncertainty_flag = "Medium"
            recommendation_note = "Moderate prediction uncertainty detected. Consider follow-up screening."
        else:
            uncertainty_flag = "Low"
            recommendation_note = "Prediction is confident and reliable."
        
        # Low confidence increases risk
        if confidence < 0.6:
            confidence_flag = "Low"
            recommendation_note += " Low confidence suggests borderline case."
        elif confidence < 0.8:
            confidence_flag = "Medium"
        else:
            confidence_flag = "High"
        
        return {
            "risk_level": base_risk,
            "confidence_flag": confidence_flag,
            "uncertainty_flag": uncertainty_flag,
            "recommendation_note": recommendation_note,
            "requires_specialist_review": (
                base_risk in ["High", "Critical", "Emergency"] or 
                confidence < 0.7 or 
                epistemic_uncertainty > 0.12
            )
        }

    @staticmethod
    def predict_image(filename: str, contents: bytes, 
                     generate_visualization: bool = True) -> Dict[str, Any]:
        """
        Performs the full prediction pipeline with explainability
        
        Args:
            filename: The name of the uploaded file
            contents: The binary content of the file
            generate_visualization: Whether to generate Grad-CAM visualization
            
        Returns:
            A dictionary containing the prediction results with visualizations
        """
        # 1. Validation
        PredictionService._validate_file(filename, contents)
        PredictionService._validate_image_integrity(contents)
        
        logger.info(f"Processing image: {filename}")
        
        # Get image quality metrics
        _, _, quality_metrics = ImageProcessor.assess_image_quality(contents)
        
        # 2. Preprocessing
        preprocessed_image, original_image = PredictionService._preprocess_image(contents)
        
        # 3. Prediction with uncertainty estimation
        try:
            prediction = model_manager.predict(
                preprocessed_image, 
                return_visualization=generate_visualization
            )
        except Exception as e:
            logger.error(f"Model prediction failed: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Prediction failed: {str(e)}"
            )
        
        # 4. Enhanced structured recommendation
        prediction['structured_recommendation'] = PredictionService._get_structured_recommendation(
            prediction['severity_level']
        )
        
        # 5. Risk stratification
        prediction['risk_stratification'] = PredictionService._get_risk_stratification(
            prediction['severity_level'],
            prediction['confidence'],
            prediction.get('uncertainty', {})
        )
        
        # 6. Add image quality metrics
        prediction['image_quality'] = quality_metrics
        
        # 7. Generate Grad-CAM visualization if available
        if generate_visualization and 'grad_cam_heatmap' in prediction:
            try:
                # Generate explanation image
                explanation_image = model_manager.generate_explanation_image(
                    preprocessed_image,
                    original_image,
                    prediction
                )
                
                if explanation_image is not None:
                    # Encode to base64
                    explanation_base64 = PredictionService._encode_image_to_base64(explanation_image)
                    if explanation_base64:
                        prediction['visualization'] = {
                            'grad_cam_overlay': explanation_base64,
                            'description': 'Highlighted regions show areas that influenced the AI decision. Warmer colors (red/yellow) indicate higher importance.'
                        }
                        logger.info("Grad-CAM visualization generated successfully")
                
                # Remove raw heatmap from response (keep only base64 image)
                del prediction['grad_cam_heatmap']
                
            except Exception as e:
                logger.warning(f"Could not generate visualization: {str(e)}")
        
        logger.info(
            f"Prediction complete - Level: {prediction['severity_level']}, "
            f"Confidence: {prediction['confidence']:.2%}, "
            f"Uncertainty: {prediction.get('uncertainty', {}).get('epistemic', 0):.4f}"
        )
        
        return prediction

    @staticmethod
    def _get_structured_recommendation(severity_level: str) -> Dict[str, str]:
        """
        Generates a structured, actionable recommendation based on the severity level
        
        Args:
            severity_level: Predicted severity level
            
        Returns:
            Structured recommendation dictionary
        """
        recommendations = Config.DIAGNOSIS_RECOMMENDATIONS.get(severity_level, {})
        
        # Default recommendation structure for safety
        default_rec = {
            "action": "Consult a specialist immediately.",
            "urgency": "High",
            "follow_up_time": "Immediate",
            "note": "The system could not provide a specific recommendation. Please consult a healthcare professional immediately."
        }
        
        # Return structured recommendation
        if recommendations:
            return {
                "action": recommendations.get("action", default_rec["action"]),
                "urgency": recommendations.get("urgency", default_rec["urgency"]),
                "follow_up_time": recommendations.get("follow_up_time", default_rec["follow_up_time"]),
                "note": recommendations.get("note", "")
            }
        
        return default_rec
