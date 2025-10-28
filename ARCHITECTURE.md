# RetinaScan AI - System Architecture

## Overview

RetinaScan AI is a production-ready backend system for diabetic retinopathy detection using deep learning. The architecture follows modern best practices with clear separation of concerns, modular design, and extensibility.

## System Components

### 1. API Layer (`main.py`)

The API layer is built with FastAPI and provides RESTful endpoints for client interaction.

**Responsibilities:**
- HTTP request/response handling
- Input validation
- Error handling and formatting
- CORS configuration
- API documentation generation

**Key Endpoints:**
- `GET /` - API information
- `GET /health` - Health check and status
- `POST /predict` - Image analysis endpoint
- `GET /model/info` - Model metadata

**Design Patterns:**
- Dependency injection for model manager
- Middleware pattern for CORS
- Exception handlers for consistent error responses
- Pydantic models for request/response validation

### 2. Configuration Layer (`config.py`)

Centralized configuration management using environment variables and defaults.

**Features:**
- Environment-based configuration
- Type-safe configuration values
- Default values for development
- Diagnosis labels and recommendations
- File upload constraints

**Configuration Categories:**
- Server settings (host, port, debug)
- Model settings (path, input size, classes)
- File upload settings (size limits, allowed types)
- CORS settings (allowed origins)
- Domain settings (labels, recommendations)

### 3. Image Processing Layer (`utils/image_processor.py`)

Handles all image preprocessing and validation operations.

**Processing Pipeline:**
1. File validation (type, size, integrity)
2. Image loading and color conversion
3. Quality enhancement (contrast, sharpness, color)
4. Border cropping (remove black regions)
5. CLAHE application (contrast enhancement)
6. Resizing (224x224 with Lanczos interpolation)
7. Normalization (pixel values to [0, 1])
8. Batch dimension addition

**Key Methods:**
- `validate_file_extension()` - File type checking
- `validate_image()` - Image integrity verification
- `enhance_retinal_image()` - Quality improvement
- `apply_clahe()` - Contrast enhancement
- `crop_black_borders()` - Border removal
- `preprocess_for_model()` - Complete pipeline

**Technologies:**
- PIL/Pillow for image loading and enhancement
- OpenCV for advanced processing (CLAHE, cropping)
- NumPy for array operations

### 4. Model Management Layer (`utils/model_manager.py`)

Manages model lifecycle including loading, inference, and metadata.

**Responsibilities:**
- Model loading from disk
- Fallback model creation
- Inference execution
- Result interpretation
- Model metadata retrieval

**Key Features:**
- Lazy loading (load on first use)
- Automatic fallback to dummy model
- Transfer learning architecture
- Batch prediction support
- Comprehensive error handling

**Model Architecture (Dummy/Fallback):**
```
Input (224, 224, 3)
    ↓
MobileNetV2 Base (ImageNet weights, frozen)
    ↓
GlobalAveragePooling2D
    ↓
Dropout (0.3)
    ↓
Dense (128, ReLU)
    ↓
Dropout (0.2)
    ↓
Dense (5, Softmax)
    ↓
Output (5 classes)
```

### 5. Training Pipeline (`train_model.py`)

Complete training workflow for custom model development.

**Training Stages:**
1. **Data Loading**: Load and organize dataset
2. **Preprocessing**: Apply augmentation and normalization
3. **Model Building**: Create transfer learning architecture
4. **Initial Training**: Train with frozen base (30 epochs)
5. **Fine-tuning**: Unfreeze and train with lower LR (15 epochs)
6. **Evaluation**: Test on validation set

**Data Augmentation:**
- Rotation (±20°)
- Width/height shift (±20%)
- Horizontal and vertical flips
- Zoom (±20%)
- Shear transformation (±10%)

**Callbacks:**
- ModelCheckpoint (save best model)
- EarlyStopping (prevent overfitting)
- ReduceLROnPlateau (adaptive learning rate)

### 6. Data Preparation (`prepare_data.py`)

Utilities for organizing APTOS dataset into training-ready format.

**Features:**
- CSV-based label reading
- Automatic directory organization
- Class-based file sorting
- Validation split creation
- Dataset statistics reporting

## Data Flow

### Prediction Request Flow

```
Client Request
    ↓
FastAPI Endpoint (/predict)
    ↓
File Validation (size, type)
    ↓
Image Validation (integrity, dimensions)
    ↓
Image Preprocessing Pipeline
    ↓
Model Inference
    ↓
Result Interpretation
    ↓
JSON Response Formatting
    ↓
Client Response
```

### Startup Flow

```
Application Start
    ↓
FastAPI Initialization
    ↓
CORS Middleware Setup
    ↓
Startup Event Handler
    ↓
Model Manager Initialization
    ↓
Model Loading (or Fallback Creation)
    ↓
Ready to Accept Requests
```

## Technology Stack

### Core Framework
- **FastAPI**: Modern, high-performance web framework
- **Uvicorn**: ASGI server for production deployment
- **Pydantic**: Data validation and settings management

### Machine Learning
- **TensorFlow/Keras**: Deep learning framework
- **Transfer Learning**: MobileNetV2/ResNet50 architectures
- **ImageNet Weights**: Pre-trained feature extraction

### Image Processing
- **OpenCV**: Advanced computer vision operations
- **Pillow (PIL)**: Image loading and basic operations
- **NumPy**: Numerical array operations

### Development Tools
- **Python 3.8+**: Modern Python features
- **Type Hints**: Static type checking
- **Logging**: Comprehensive logging system

## Design Principles

### 1. Separation of Concerns
Each module has a single, well-defined responsibility:
- API layer handles HTTP
- Image processor handles preprocessing
- Model manager handles ML operations
- Config handles settings

### 2. Modularity
Components are loosely coupled and can be modified independently:
- Swap image processing algorithms
- Change model architecture
- Update API endpoints
- Modify configuration

### 3. Extensibility
Easy to extend with new features:
- Add new endpoints
- Implement batch processing
- Support additional image formats
- Integrate new models

### 4. Error Handling
Comprehensive error handling at every layer:
- Input validation errors (400)
- Processing errors (400)
- Model errors (500)
- Consistent error response format

### 5. Configuration Management
Environment-based configuration:
- Development defaults
- Production overrides
- No hardcoded values
- Easy deployment

## Security Considerations

### Input Validation
- File type whitelist
- File size limits
- Image integrity checks
- Dimension validation

### CORS Configuration
- Configurable allowed origins
- Credential handling
- Method restrictions

### Error Messages
- No sensitive information leakage
- Generic error messages for clients
- Detailed logging for developers

## Performance Optimization

### Model Loading
- Load once at startup
- Keep in memory for fast inference
- No per-request loading overhead

### Image Processing
- Efficient NumPy operations
- Optimized OpenCV algorithms
- Minimal memory allocation

### API Response
- Async request handling
- Non-blocking I/O operations
- Fast JSON serialization

## Scalability Considerations

### Horizontal Scaling
- Stateless API design
- No session storage
- Load balancer compatible

### Vertical Scaling
- GPU support for model inference
- Multi-worker deployment
- Async processing

### Caching Opportunities
- Model weights (loaded once)
- Preprocessing parameters
- Configuration values

## Deployment Architecture

### Development
```
Developer Machine
    ↓
Python Virtual Environment
    ↓
Uvicorn (single worker, auto-reload)
    ↓
Local Testing
```

### Production
```
Load Balancer
    ↓
Multiple Gunicorn Workers
    ↓
Uvicorn ASGI Workers
    ↓
FastAPI Application
    ↓
TensorFlow Model (GPU)
```

### Containerized
```
Docker Container
    ↓
Python 3.11 Slim Base
    ↓
Application Code + Dependencies
    ↓
Uvicorn Server
    ↓
Exposed Port 8000
```

## Monitoring and Logging

### Logging Levels
- **INFO**: Startup, model loading, predictions
- **WARNING**: Model fallback, missing files
- **ERROR**: Processing failures, model errors

### Metrics to Monitor
- Request count and rate
- Response time (p50, p95, p99)
- Error rate by type
- Model inference time
- Memory usage
- CPU/GPU utilization

### Health Checks
- `/health` endpoint for load balancers
- Model loaded status
- Startup time tracking

## Future Enhancements

### Planned Features
1. **Batch Processing**: Multiple images in single request
2. **Async Processing**: Background job queue
3. **Result Caching**: Cache predictions by image hash
4. **Model Versioning**: Support multiple model versions
5. **A/B Testing**: Compare model performance
6. **Explainability**: Grad-CAM visualization
7. **Metrics Dashboard**: Real-time monitoring
8. **Database Integration**: Store predictions and history

### Integration Opportunities
1. **DICOM Support**: Medical imaging standard
2. **HL7/FHIR**: Healthcare data exchange
3. **EHR Integration**: Electronic health records
4. **Telemedicine Platforms**: Remote consultations
5. **Mobile Apps**: iOS/Android clients

## Testing Strategy

### Unit Tests
- Image processor functions
- Model manager methods
- Configuration loading
- Utility functions

### Integration Tests
- API endpoint testing
- End-to-end prediction flow
- Error handling scenarios

### Performance Tests
- Load testing with multiple requests
- Memory leak detection
- Inference time benchmarking

## Documentation

### API Documentation
- Auto-generated Swagger UI
- ReDoc alternative view
- Request/response examples

### Code Documentation
- Docstrings for all functions
- Type hints for parameters
- Inline comments for complex logic

### User Documentation
- README.md for overview
- QUICKSTART.md for getting started
- ARCHITECTURE.md (this file) for deep dive

---

This architecture provides a solid foundation for building a production-grade diabetic retinopathy detection system while maintaining flexibility for future enhancements and integrations.
