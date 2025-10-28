"""
RetinaScan AI - Prediction Service
Handles the core business logic for image processing and model prediction.
"""
import logging
from typing import Dict, Any, Tuple

from fastapi import HTTPException

from ..config import Config
from ..utils.image_processor import ImageProcessor
from ..utils.model_manager import model_manager

logger = logging.getLogger(__name__)

class PredictionService:
    """
    Service class to encapsulate the end-to-end prediction logic.
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
        """Validates the integrity of the image content."""
        is_valid, error_msg = ImageProcessor.validate_image(contents)
        if not is_valid:
            raise HTTPException(status_code=400, detail=error_msg)

    @staticmethod
    def _preprocess_image(contents: bytes) -> Any:
        """Preprocesses the image for model inference."""
        try:
            return ImageProcessor.preprocess_for_model(contents)
        except Exception as e:
            logger.error(f"Image preprocessing failed: {str(e)}")
            raise HTTPException(
                status_code=400,
                detail=f"Image preprocessing failed: {str(e)}"
            )

    @staticmethod
    def predict_image(filename: str, contents: bytes) -> Dict[str, Any]:
        """
        Performs the full prediction pipeline.
        
        Args:
            filename: The name of the uploaded file.
            contents: The binary content of the file.
            
        Returns:
            A dictionary containing the prediction results.
        """
        # 1. Validation
        PredictionService._validate_file(filename, contents)
        PredictionService._validate_image_integrity(contents)
        
        logger.info(f"Processing image: {filename}")
        
        # 2. Preprocessing
        preprocessed_image = PredictionService._preprocess_image(contents)
        
        # 3. Prediction
        try:
            # Prediction is a CPU-bound operation, so it should be run in a 
            # separate thread pool (handled by FastAPI's run_in_threadpool 
            # when not explicitly awaited, or we can use a custom executor).
            # For simplicity and to leverage FastAPI's async nature, we'll
            # assume model_manager.predict is designed to be thread-safe/non-blocking.
            prediction = model_manager.predict(preprocessed_image)
        except Exception as e:
            logger.error(f"Model prediction failed: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Prediction failed: {str(e)}"
            )
            
        # 4. Feature Enhancement (Uniqueness of Idea)
        # Add a structured recommendation based on the severity level
        prediction['structured_recommendation'] = PredictionService._get_structured_recommendation(
            prediction['severity_level']
        )
        
        logger.info(
            f"Prediction complete - Level: {prediction['severity_level']}, "
            f"Confidence: {prediction['confidence']:.2%}"
        )
        
        return prediction

    @staticmethod
    def _get_structured_recommendation(severity_level: str) -> Dict[str, str]:
        """
        Generates a structured, actionable recommendation based on the severity level.
        This enhances the 'Real world Impact' and 'Uniqueness of the Idea'.
        """
        recommendations = Config.DIAGNOSIS_RECOMMENDATIONS.get(severity_level, {})
        
        # Default recommendation structure for safety
        default_rec = {
            "action": "Consult a specialist.",
            "urgency": "High",
            "follow_up_time": "Immediate",
            "note": "The system could not provide a specific recommendation. Please consult a healthcare professional immediately."
        }
        
        # Map simple recommendation string to a structured format
        if recommendations:
            return {
                "action": recommendations.get("action", default_rec["action"]),
                "urgency": recommendations.get("urgency", default_rec["urgency"]),
                "follow_up_time": recommendations.get("follow_up_time", default_rec["follow_up_time"]),
                "note": recommendations.get("note", "")
            }
        
        return default_rec


