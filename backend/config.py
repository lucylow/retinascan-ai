import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Configuration class for Flask application"""
    
    # Flask Configuration
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-2023')
    DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'
    
    # File Upload Configuration
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'bmp', 'tiff'}
    
    # Model Configuration
    MODEL_PATH = os.getenv('MODEL_PATH', 'models/retina_model.h5')
    IMAGE_SIZE = (224, 224)
    
    # CORS Configuration
    CORS_ORIGINS = os.getenv('CORS_ORIGINS', 'http://localhost:3000,http://localhost:5173,http://localhost:8080').split(',')
    
    # Diagnosis Configuration
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

