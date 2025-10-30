"""
RetinaScan AI - Backend API
FastAPI application for diabetic retinopathy detection
"""
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Dict, Optional, List
import logging
from datetime import datetime

from config import Config
from utils.image_processor import ImageProcessor
from utils.model_manager import model_manager
from services.prediction_service import PredictionService
from fastapi.concurrency import run_in_threadpool
from services.visualization_service import AIVisualizationService

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)
# Global services
viz_service: Optional[AIVisualizationService] = None

# Initialize FastAPI app
app = FastAPI(
    title="RetinaScan AI API",
    description="Backend API for diabetic retinopathy detection using deep learning",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=Config.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Response models
class HealthResponse(BaseModel):
    """Health check response model"""
    status: str
    timestamp: str
    model_loaded: bool
    model_info: Optional[Dict] = None


class PredictionResponse(BaseModel):
    """Prediction response model"""
    success: bool
    severity_class: int
    severity_level: str
    confidence: float
    label: str
    recommendation: str
    structured_recommendation: Dict[str, str] # New field for enhanced real-world impact
    class_probabilities: Dict[str, float]
    timestamp: str


class ErrorResponse(BaseModel):
    """Error response model"""
    success: bool
    error: str
    detail: Optional[str] = None
    timestamp: str


# Startup event
@app.on_event("startup")
async def startup_event():
    """Load model on application startup"""
    logger.info("Starting RetinaScan AI Backend...")
    logger.info("Loading ML model...")
    
    global viz_service
    success = model_manager.load_model()
    
    if success:
        logger.info("Model loaded successfully")
    else:
        logger.warning("Model loading failed, using fallback")
    
    # Initialize visualization service with the loaded Keras model
    try:
        viz_service = AIVisualizationService(model_manager.model)
        logger.info("Visualization service initialized")
    except Exception as e:
        logger.warning(f"Visualization service initialization failed: {e}")

    logger.info("Application startup complete")


# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on application shutdown"""
    logger.info("Shutting down RetinaScan AI Backend...")


# API Endpoints
@app.get("/", response_model=Dict)
async def root():
    """Root endpoint with API information"""
    return {
        "name": "RetinaScan AI API",
        "version": "1.0.0",
        "description": "Backend API for diabetic retinopathy detection",
        "endpoints": {
            "health": "/health",
            "predict": "/predict (POST)",
            "docs": "/docs"
        }
    }


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """
    Health check endpoint
    Returns server status and model information
    """
    model_info = model_manager.get_model_info()
    
    return HealthResponse(
        status="healthy",
        timestamp=datetime.utcnow().isoformat(),
        model_loaded=model_manager.model_loaded,
        model_info=model_info
    )


@app.post("/predict", response_model=PredictionResponse)
async def predict_retinopathy(file: UploadFile = File(...)):
    """
    Predict diabetic retinopathy severity from retinal fundus image
    
    Args:
        file: Uploaded image file (PNG, JPG, JPEG, BMP, TIFF)
        
    Returns:
        Prediction results with severity classification and structured recommendations
    """
    # Read file contents asynchronously for better performance
    contents = await file.read()
    
    try:
        # Delegate all core logic to the service layer for better separation of concerns
        # Use run_in_threadpool to run the CPU-bound prediction logic synchronously 
        # in a separate thread, preventing the main event loop from blocking.
        prediction = await run_in_threadpool(
            PredictionService.predict_image, 
            file.filename, 
            contents
        )
        
        # Format class probabilities for response
        formatted_probs = {
            f"class_{k}": v for k, v in prediction['class_probabilities'].items()
        }
        
        return PredictionResponse(
            success=True,
            severity_class=prediction['severity_class'],
            severity_level=prediction['severity_level'],
            confidence=prediction['confidence'],
            label=prediction['label'],
            recommendation=prediction['recommendation'],
            structured_recommendation=prediction['structured_recommendation'],
            class_probabilities=formatted_probs,
            timestamp=datetime.utcnow().isoformat()
        )
        
    except HTTPException:
        # Re-raise HTTPExceptions raised by the service layer
        raise
    except Exception as e:
        logger.error(f"Unexpected error in /predict: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )


@app.get("/model/info")
async def get_model_info():
    """Get detailed model information"""
    return model_manager.get_model_info()


# Error handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Custom HTTP exception handler"""
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(
            success=False,
            error=exc.detail,
            timestamp=datetime.utcnow().isoformat()
        ).dict()
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """General exception handler"""
    logger.error(f"Unhandled exception: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content=ErrorResponse(
            success=False,
            error="Internal server error",
            detail=str(exc),
            timestamp=datetime.utcnow().isoformat()
        ).dict()
    )


# Enhanced endpoints with visualizations
@app.post("/predict/detailed")
async def predict_with_visualization(file: UploadFile = File(...)):
    """
    Enhanced prediction endpoint returning GradCAM-derived visualizations.
    """
    if viz_service is None:
        raise HTTPException(status_code=503, detail="Visualization service unavailable")

    contents = await file.read()
    try:
        # Reuse core prediction flow
        prediction = await run_in_threadpool(
            PredictionService.predict_image,
            file.filename,
            contents,
        )

        # Preprocess for model to get the image tensor
        img_array = await run_in_threadpool(ImageProcessor.preprocess_for_model, contents)

        # Build heatmap and lesion detections
        heatmap_bgr, _ = viz_service.generate_gradcam_heatmap(
            img_array, pred_index=prediction["severity_class"]
        )
        lesions = viz_service.detect_lesion_regions(heatmap_bgr, threshold=0.5)

        # Confidence chart expects dict[str,float]
        # Our base response uses class_probabilities as {int: float}
        class_probs = {f"class_{k}": v for k, v in prediction["class_probabilities"].items()}
        chart_b64 = viz_service.create_confidence_chart(
            class_probs,
            ["No DR", "Mild NPDR", "Moderate NPDR", "Severe NPDR", "PDR"],
        )

        # Compose overlay figure
        original_rgb = (img_array[0] * 255).astype("uint8")
        overlay_b64 = viz_service.create_attention_map_overlay(original_rgb, heatmap_bgr, lesions)

        return JSONResponse(
            {
                "success": True,
                "prediction": {
                    **prediction,
                    "class_probabilities": class_probs,
                },
                "visualizations": {
                    "confidence_chart": f"data:image/png;base64,{chart_b64}",
                    "attention_map": f"data:image/png;base64,{overlay_b64}",
                    "lesion_count": len(lesions),
                    "detected_lesions": lesions[:10],
                },
                "explainability": {
                    "method": "GradCAM",
                    "last_conv_layer": viz_service.last_conv_layer_name,
                    "note": "Heatmap highlights regions contributing most to prediction.",
                },
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/analyze/temporal")
async def analyze_temporal_progression(patient_history: List[Dict]):
    """Return temporal progression chart based on history records."""
    if viz_service is None:
        raise HTTPException(status_code=503, detail="Visualization service unavailable")
    try:
        chart_b64 = viz_service.create_temporal_progression_chart(patient_history)
        return JSONResponse(
            {
                "success": True,
                "progression_chart": f"data:image/png;base64,{chart_b64}",
                "trend_analysis": {
                    "progression_detected": bool(
                        patient_history[-1]["severity_class"] > patient_history[0]["severity_class"]
                    ),
                    "total_examinations": len(patient_history),
                    "current_severity": patient_history[-1]["severity_class"],
                },
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=Config.HOST,
        port=Config.PORT,
        reload=Config.DEBUG
    )
