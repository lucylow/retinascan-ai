from flask import Flask, request, jsonify, session
from flask_cors import CORS
import logging
import os
from datetime import datetime

# Import custom modules
from config import Config
from image_processor import ImageProcessor
from model_loader import RetinaModel

# Import EHR integration services
from services.fhir_integration import FHIRIntegrationService, FHIRConfig
from services.hl7_integration import HL7v2Integration, HL7MessageBuilder
from services.clinical_workflow import ClinicalWorkflowManager
from services.ehr_config import EHRConfig, DEPLOYMENT_CONFIG

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

# Global EHR services
fhir_service = None
hl7_service = None
workflow_manager = None

@app.before_first_request
def initialize_model():
    """Initialize the model before first request"""
    global retina_model
    try:
        retina_model = RetinaModel()
        logger.info("Retina model initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize model: {str(e)}")
        raise

def initialize_ehr_services():
    """Initialize EHR integration services"""
    global fhir_service, hl7_service, workflow_manager
    
    if fhir_service is None:
        try:
            # Load EHR configuration
            ehr_config = EHRConfig.from_env()
            
            # Initialize FHIR service
            fhir_config = FHIRConfig(
                fhir_base_url=ehr_config.fhir_base_url,
                client_id=ehr_config.fhir_client_id,
                client_secret=ehr_config.fhir_client_secret,
                auth_url=ehr_config.fhir_auth_url,
                token_url=ehr_config.fhir_token_url,
                redirect_uri=ehr_config.fhir_redirect_uri
            )
            fhir_service = FHIRIntegrationService(fhir_config)
            
            # Initialize HL7 service
            hl7_service = HL7v2Integration(
                host=ehr_config.hl7_host,
                port=ehr_config.hl7_port,
                use_tls=ehr_config.hl7_use_tls
            )
            
            # Initialize workflow manager
            workflow_manager = ClinicalWorkflowManager(fhir_service, hl7_service)
            
            logger.info("EHR integration services initialized successfully")
        except Exception as e:
            logger.warning(f"EHR services not initialized: {str(e)}")
            logger.info("Application will continue without EHR integration")

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

# EHR Integration Endpoints
@app.route('/api/ehr/patient/<patient_id>', methods=['GET'])
def get_patient_info(patient_id):
    """Get patient demographics from EHR"""
    initialize_ehr_services()
    
    if not fhir_service:
        return jsonify({
            "success": False,
            "error": "EHR integration not configured"
        }), 503
    
    try:
        demographics = fhir_service.get_patient_demographics(patient_id)
        if demographics:
            return jsonify({
                "success": True,
                "patient": demographics
            })
        else:
            return jsonify({
                "success": False,
                "error": "Patient not found"
            }), 404
    except Exception as e:
        logger.error(f"Error fetching patient info: {str(e)}")
        return jsonify({
            "success": False,
            "error": "Failed to fetch patient information"
        }), 500

@app.route('/api/ehr/patient/<patient_id>/conditions', methods=['GET'])
def get_patient_conditions(patient_id):
    """Get patient conditions from EHR"""
    initialize_ehr_services()
    
    if not fhir_service:
        return jsonify({
            "success": False,
            "error": "EHR integration not configured"
        }), 503
    
    try:
        conditions = fhir_service.get_patient_conditions(patient_id)
        return jsonify({
            "success": True,
            "conditions": conditions
        })
    except Exception as e:
        logger.error(f"Error fetching conditions: {str(e)}")
        return jsonify({
            "success": False,
            "error": "Failed to fetch conditions"
        }), 500

@app.route('/api/ehr/submit-results', methods=['POST'])
def submit_results_to_ehr():
    """Submit AI results to EHR"""
    initialize_ehr_services()
    
    if not fhir_service:
        return jsonify({
            "success": False,
            "error": "EHR integration not configured"
        }), 503
    
    try:
        data = request.json
        ai_result = data.get('ai_result')
        image_data = data.get('image_data', '')
        patient_id = data.get('patient_id')
        
        if not ai_result or not patient_id:
            return jsonify({
                "success": False,
                "error": "Missing required fields: ai_result or patient_id"
            }), 400
        
        result = fhir_service.submit_ai_results_to_ehr(
            ai_result, image_data, patient_id
        )
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error submitting results: {str(e)}")
        return jsonify({
            "success": False,
            "error": "Failed to submit results to EHR"
        }), 500

@app.route('/api/ehr/workflow', methods=['POST'])
def process_workflow():
    """Process complete clinical workflow"""
    initialize_ehr_services()
    
    if not workflow_manager:
        return jsonify({
            "success": False,
            "error": "EHR integration not configured"
        }), 503
    
    try:
        data = request.json
        patient_id = data.get('patient_id')
        image_data = data.get('image_data', '')
        workflow_config = data.get('workflow_config', {})
        
        if not patient_id:
            return jsonify({
                "success": False,
                "error": "Missing required field: patient_id"
            }), 400
        
        # If no specific workflow config, use default from EHR config
        if not workflow_config:
            ehr_config = EHRConfig.from_env()
            workflow_config = ehr_config.to_workflow_config()
        
        # Run workflow (in production this would be async)
        import asyncio
        result = asyncio.run(
            workflow_manager.process_screening_workflow(
                patient_id, image_data, workflow_config
            )
        )
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error processing workflow: {str(e)}")
        return jsonify({
            "success": False,
            "error": "Failed to process workflow"
        }), 500

@app.route('/api/ehr/workflow/<workflow_id>/audit', methods=['GET'])
def get_workflow_audit(workflow_id):
    """Get audit trail for a workflow"""
    initialize_ehr_services()
    
    if not workflow_manager:
        return jsonify({
            "success": False,
            "error": "EHR integration not configured"
        }), 503
    
    try:
        audit_trail = workflow_manager.get_workflow_audit_trail(workflow_id)
        return jsonify({
            "success": True,
            "audit_trail": audit_trail
        })
    except Exception as e:
        logger.error(f"Error fetching audit trail: {str(e)}")
        return jsonify({
            "success": False,
            "error": "Failed to fetch audit trail"
        }), 500

@app.route('/api/ehr/metrics', methods=['GET'])
def get_workflow_metrics():
    """Get workflow performance metrics"""
    initialize_ehr_services()
    
    if not workflow_manager:
        return jsonify({
            "success": False,
            "error": "EHR integration not configured"
        }), 503
    
    try:
        time_period = request.args.get('period', 'day')
        metrics = workflow_manager.get_workflow_metrics(time_period)
        return jsonify({
            "success": True,
            "metrics": metrics
        })
    except Exception as e:
        logger.error(f"Error fetching metrics: {str(e)}")
        return jsonify({
            "success": False,
            "error": "Failed to fetch metrics"
        }), 500

if __name__ == '__main__':
    # Initialize model before running
    initialize_model()
    
    # Run Flask app
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=app.config['DEBUG'])


