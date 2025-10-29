from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import logging
import os
from datetime import datetime
import json

# Import custom modules
from config import Config
from image_processor import ImageProcessor
from model_loader import RetinaModel

# Initialize logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(name)s %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
app.config.from_object(Config)

# Initialize CORS
CORS(app, origins=app.config['CORS_ORIGINS'])

# Global model instance
retina_model = None

def initialize_model():
    """Initialize the model before first request"""
    global retina_model
    try:
        retina_model = RetinaModel()
        logger.info("Retina model initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize model: {str(e)}")
        raise

# Initialize model on startup
initialize_model()

# Error handlers
@app.errorhandler(413)
def too_large(e):
    return jsonify({
        "success": False,
        "error": "File too large. Maximum size is 16MB."
    }), 413

@app.errorhandler(400)
def bad_request(e):
    return jsonify({
        "success": False,
        "error": "Bad request"
    }), 400

@app.errorhandler(500)
def internal_error(e):
    return jsonify({
        "success": False,
        "error": "Internal server error"
    }), 500

# Health check endpoint
@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    model_status = "loaded" if retina_model and retina_model.model else "not loaded"
    
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "model_status": model_status,
        "version": "1.0.0"
    })

# Model info endpoint
@app.route('/api/model/info', methods=['GET'])
def model_info():
    """Get information about the loaded model"""
    if not retina_model:
        return jsonify({
            "success": False,
            "error": "Model not initialized"
        }), 503
    
    try:
        model_info = retina_model.get_model_info()
        return jsonify({
            "success": True,
            "model_info": model_info
        })
    except Exception as e:
        logger.error(f"Error getting model info: {str(e)}")
        return jsonify({
            "success": False,
            "error": "Failed to get model information"
        }), 500

# Prediction endpoint
@app.route('/api/predict', methods=['POST'])
def predict():
    """
    Main prediction endpoint
    Expects: multipart/form-data with 'image' file
    Returns: JSON with prediction results
    """
    # Check if model is loaded
    if not retina_model:
        return jsonify({
            "success": False,
            "error": "Model not initialized. Please try again later."
        }), 503
    
    # Check if image file is present
    if 'image' not in request.files:
        return jsonify({
            "success": False,
            "error": "No image file provided. Please upload an image."
        }), 400
    
    image_file = request.files['image']
    
    # Check if file is selected
    if image_file.filename == '':
        return jsonify({
            "success": False,
            "error": "No file selected"
        }), 400
    
    # Validate file type
    if not ImageProcessor.allowed_file(image_file.filename):
        return jsonify({
            "success": False,
            "error": f"Invalid file type. Allowed types: {', '.join(Config.ALLOWED_EXTENSIONS)}"
        }), 400
    
    try:
        # Process the image
        logger.info(f"Processing image: {image_file.filename}")
        processed_image = ImageProcessor.preprocess_image(image_file)
        
        # Make prediction
        prediction_result = retina_model.predict(processed_image)
        
        # Add metadata
        prediction_result.update({
            "success": True,
            "timestamp": datetime.utcnow().isoformat(),
            "filename": image_file.filename
        })
        
        logger.info(f"Prediction completed: {prediction_result['diagnosis']} "
                   f"(confidence: {prediction_result['confidence']:.2f})")
        
        return jsonify(prediction_result)
        
    except ValueError as e:
        logger.error(f"Image processing error: {str(e)}")
        return jsonify({
            "success": False,
            "error": f"Image processing error: {str(e)}"
        }), 400
        
    except RuntimeError as e:
        logger.error(f"Prediction error: {str(e)}")
        return jsonify({
            "success": False,
            "error": f"Prediction failed: {str(e)}"
        }), 500
        
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return jsonify({
            "success": False,
            "error": "An unexpected error occurred. Please try again."
        }), 500

# Batch prediction endpoint
@app.route('/api/predict/batch', methods=['POST'])
def batch_predict():
    """
    Batch prediction endpoint for multiple images
    Expects: multipart/form-data with multiple 'images[]' files
    """
    if not retina_model:
        return jsonify({
            "success": False,
            "error": "Model not initialized"
        }), 503
    
    if 'images[]' not in request.files:
        return jsonify({
            "success": False,
            "error": "No images provided"
        }), 400
    
    image_files = request.files.getlist('images[]')
    
    if len(image_files) > 10:  # Limit batch size
        return jsonify({
            "success": False,
            "error": "Too many images. Maximum 10 images per batch."
        }), 400
    
    results = []
    errors = []
    
    for image_file in image_files:
        if image_file.filename == '':
            continue
            
        if not ImageProcessor.allowed_file(image_file.filename):
            errors.append(f"Invalid file type: {image_file.filename}")
            continue
        
        try:
            processed_image = ImageProcessor.preprocess_image(image_file)
            prediction_result = retina_model.predict(processed_image)
            prediction_result['filename'] = image_file.filename
            results.append(prediction_result)
            
        except Exception as e:
            errors.append(f"Error processing {image_file.filename}: {str(e)}")
    
    return jsonify({
        "success": True,
        "total_processed": len(results),
        "results": results,
        "errors": errors,
        "timestamp": datetime.utcnow().isoformat()
    })

# Diagnosis information endpoint
@app.route('/api/diagnosis/info', methods=['GET'])
def diagnosis_info():
    """Get information about different diagnosis levels"""
    return jsonify({
        "success": True,
        "diagnosis_levels": Config.DIAGNOSIS_LABELS,
        "recommendations": Config.RECOMMENDATIONS,
        "description": "Diabetic Retinopathy Severity Scale (0-4)"
    })

if __name__ == '__main__':
    # Run Flask app
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=app.config['DEBUG'])

