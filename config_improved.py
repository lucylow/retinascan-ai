"""
Enhanced configuration module for RetinaScan AI Backend
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Application configuration"""
    
    # Base paths
    BASE_DIR = Path(__file__).parent
    MODEL_DIR = BASE_DIR / "models"
    
    # Server configuration
    HOST = os.getenv("HOST", "0.0.0.0")
    PORT = int(os.getenv("PORT", 8000))
    DEBUG = os.getenv("DEBUG", "False").lower() == "true"
    
    # File upload configuration
    MAX_UPLOAD_SIZE = 16 * 1024 * 1024  # 16MB
    ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "bmp", "tiff"}
    
    # Model configuration
    MODEL_PATH = os.getenv("MODEL_PATH", str(MODEL_DIR / "retina_model.h5"))
    IMAGE_SIZE = (224, 224)
    NUM_CLASSES = 5
    
    # CORS configuration
    CORS_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:3000,http://localhost:5173").split(",")
    
    # Diagnosis labels and recommendations
    DIAGNOSIS_LABELS = {
        0: "No Diabetic Retinopathy",
        1: "Mild Diabetic Retinopathy",
        2: "Moderate Diabetic Retinopathy",
        3: "Severe Diabetic Retinopathy",
        4: "Proliferative Diabetic Retinopathy"
    }
    
    RECOMMENDATIONS = {
        0: "No signs of diabetic retinopathy detected. Continue regular annual eye screenings.",
        1: "Mild non-proliferative diabetic retinopathy detected. Recommend follow-up with ophthalmologist in 6-12 months.",
        2: "Moderate non-proliferative diabetic retinopathy detected. Urgent consultation with ophthalmologist recommended within 3-6 months.",
        3: "Severe non-proliferative diabetic retinopathy detected. Immediate ophthalmologist consultation recommended within 1 month.",
        4: "Proliferative diabetic retinopathy detected. Emergency ophthalmologist consultation required immediately."
    }
    
    SEVERITY_LEVELS = {
        0: "None",
        1: "Mild",
        2: "Moderate",
        3: "Severe",
        4: "Proliferative"
    }

    # Structured recommendations for enhanced 'Real World Impact' and 'Uniqueness of Idea'
    DIAGNOSIS_RECOMMENDATIONS = {
        "None": {
            "action": "Routine annual eye exam.",
            "urgency": "Low",
            "follow_up_time": "12 months",
            "note": "No signs of Diabetic Retinopathy detected. Maintain good diabetes control."
        },
        "Mild": {
            "action": "Consult with an ophthalmologist for monitoring.",
            "urgency": "Medium",
            "follow_up_time": "6-12 months",
            "note": "Early signs detected. Strict blood sugar and blood pressure control is crucial."
        },
        "Moderate": {
            "action": "Immediate referral to a retinal specialist.",
            "urgency": "High",
            "follow_up_time": "3-6 months",
            "note": "Significant changes observed. Specialist consultation is required to discuss treatment options."
        },
        "Severe": {
            "action": "Urgent referral to a retinal specialist for potential intervention (e.g., laser treatment or injections).",
            "urgency": "Critical",
            "follow_up_time": "Within 1 month",
            "note": "Advanced stage of the disease. Immediate specialist care is necessary to prevent vision loss."
        },
        "Proliferative": {
            "action": "Emergency consultation with a retinal specialist.",
            "urgency": "Emergency",
            "follow_up_time": "Within 1 week",
            "note": "Most advanced stage. High risk of severe vision loss. Immediate intervention is mandatory."
        }
    }
