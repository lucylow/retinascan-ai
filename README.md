# RetinaScan AI - Backend

Backend API for diabetic retinopathy detection using deep learning and computer vision.

## Overview

RetinaScan AI is a FastAPI-based backend service that analyzes retinal fundus images to detect and classify diabetic retinopathy severity. The system uses transfer learning with MobileNetV2 or ResNet50 architectures trained on the APTOS 2019 Blindness Detection dataset.

## Features

- **AI-Powered Detection**: Deep learning model for 5-class diabetic retinopathy classification
- **Image Processing Pipeline**: Advanced preprocessing including CLAHE enhancement and border cropping
- **REST API**: FastAPI endpoints for health checks and predictions
- **Transfer Learning**: Pre-trained models with custom classification heads
- **Comprehensive Validation**: File type, size, and image quality validation
- **Detailed Responses**: Confidence scores, severity levels, and clinical recommendations

## Severity Classification

| Class | Severity Level | Description |
|-------|---------------|-------------|
| 0 | No DR | No diabetic retinopathy detected |
| 1 | Mild DR | Mild non-proliferative diabetic retinopathy |
| 2 | Moderate DR | Moderate non-proliferative diabetic retinopathy |
| 3 | Severe DR | Severe non-proliferative diabetic retinopathy |
| 4 | Proliferative DR | Proliferative diabetic retinopathy |

## Project Structure

```
retinascan-backend/
├── main.py                 # FastAPI application
├── config.py              # Configuration management
├── train_model.py         # Model training script
├── requirements.txt       # Python dependencies
├── .env.example          # Environment variables template
├── utils/
│   ├── image_processor.py # Image preprocessing utilities
│   └── model_manager.py   # Model loading and inference
├── models/               # Trained model files
└── tests/               # Unit tests
```

## Installation

### Prerequisites

- Python 3.8 or higher
- pip package manager
- Virtual environment (recommended)

### Setup

1. **Clone or extract the repository**

2. **Create virtual environment**
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Configure environment**
```bash
cp .env.example .env
# Edit .env with your configuration
```

5. **Create models directory**
```bash
mkdir -p models
```

## Usage

### Running the Server

**Development mode:**
```bash
python main.py
```

**Production mode with Uvicorn:**
```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

**With auto-reload for development:**
```bash
uvicorn main:app --reload
```

The API will be available at `http://localhost:8000`

### API Documentation

Interactive API documentation is automatically available at:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

### API Endpoints

#### Health Check
```bash
GET /health
```

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-10-28T14:35:00.000Z",
  "model_loaded": true,
  "model_info": {
    "loaded": true,
    "num_classes": 5,
    "input_shape": "(None, 224, 224, 3)"
  }
}
```

#### Predict Diabetic Retinopathy
```bash
POST /predict
Content-Type: multipart/form-data
```

**Request:**
- `file`: Image file (PNG, JPG, JPEG, BMP, TIFF)

**Response:**
```json
{
  "success": true,
  "severity_class": 2,
  "severity_level": "Moderate",
  "confidence": 0.87,
  "label": "Moderate Diabetic Retinopathy",
  "recommendation": "Moderate non-proliferative diabetic retinopathy detected. Urgent consultation with ophthalmologist recommended within 3-6 months.",
  "class_probabilities": {
    "class_0": 0.02,
    "class_1": 0.05,
    "class_2": 0.87,
    "class_3": 0.04,
    "class_4": 0.02
  },
  "timestamp": "2025-10-28T14:35:00.000Z"
}
```

### Testing with cURL

```bash
# Health check
curl http://localhost:8000/health

# Predict from image
curl -X POST "http://localhost:8000/predict" \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@/path/to/retinal_image.jpg"
```

### Testing with Python

```python
import requests

# Health check
response = requests.get("http://localhost:8000/health")
print(response.json())

# Predict
with open("retinal_image.jpg", "rb") as f:
    files = {"file": f}
    response = requests.post("http://localhost:8000/predict", files=files)
    print(response.json())
```

## Model Training

### Preparing Data

Organize your training data in the following structure:

```
data/train/
├── 0_No_DR/
│   ├── image1.jpg
│   └── image2.jpg
├── 1_Mild/
│   ├── image1.jpg
│   └── image2.jpg
├── 2_Moderate/
├── 3_Severe/
└── 4_Proliferative/
```

### Training the Model

```python
from train_model import RetinaModelTrainer

# Initialize trainer
trainer = RetinaModelTrainer(
    data_dir="data/train",
    model_architecture="mobilenetv2"  # or "resnet50"
)

# Build model
trainer.build_model()

# Train model
trainer.train(epochs=30, fine_tune_epochs=15)

# Evaluate
trainer.evaluate()
```

### Using Pre-trained Models

If you don't have a trained model, the system automatically creates a dummy model using MobileNetV2 with ImageNet weights for demonstration purposes. For production use, you should train on actual diabetic retinopathy data.

## Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `HOST` | `0.0.0.0` | Server host address |
| `PORT` | `8000` | Server port |
| `DEBUG` | `False` | Debug mode |
| `MODEL_PATH` | `models/retina_model.h5` | Path to trained model |
| `CORS_ORIGINS` | `http://localhost:3000` | Allowed CORS origins |
| `MAX_UPLOAD_SIZE` | `16777216` | Max file size in bytes (16MB) |

### Model Configuration

Edit `config.py` to customize:
- Image input size
- Number of classes
- Diagnosis labels and recommendations
- Allowed file extensions

## Image Processing Pipeline

The system applies the following preprocessing steps:

1. **Validation**: Check file type, size, and image integrity
2. **Color Conversion**: Convert to RGB if needed
3. **Enhancement**: Apply contrast, sharpness, and color enhancement
4. **Border Cropping**: Remove black borders from fundus images
5. **CLAHE**: Contrast Limited Adaptive Histogram Equalization
6. **Resizing**: Resize to 224x224 pixels using Lanczos interpolation
7. **Normalization**: Scale pixel values to [0, 1]
8. **Batching**: Add batch dimension for model input

## Deployment

### Docker Deployment

Create a `Dockerfile`:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

Build and run:
```bash
docker build -t retinascan-backend .
docker run -p 8000:8000 retinascan-backend
```

### Production Deployment

For production, use Gunicorn with Uvicorn workers:

```bash
pip install gunicorn
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

## Architecture

The backend follows a modular architecture with clear separation of concerns:

- **API Layer** (`main.py`): FastAPI routes and request handling
- **Configuration** (`config.py`): Centralized configuration management
- **Image Processing** (`utils/image_processor.py`): Image preprocessing and validation
- **Model Management** (`utils/model_manager.py`): Model loading and inference
- **Training** (`train_model.py`): Model training pipeline

## Technology Stack

- **Framework**: FastAPI 0.104.1
- **ML Framework**: TensorFlow 2.13.0
- **Image Processing**: OpenCV, Pillow
- **Server**: Uvicorn (ASGI server)
- **Data Handling**: NumPy, scikit-learn

## Performance Considerations

- Model inference typically takes 100-500ms per image
- Preprocessing adds 50-100ms overhead
- Use GPU for faster inference in production
- Consider model quantization for edge deployment
- Implement caching for frequently accessed predictions

## Error Handling

The API returns standardized error responses:

```json
{
  "success": false,
  "error": "Error message",
  "detail": "Detailed error information",
  "timestamp": "2025-10-28T14:35:00.000Z"
}
```

Common error codes:
- `400`: Invalid file type, size, or image format
- `500`: Model inference or server error

## Extending the Backend

### Adding New Endpoints

```python
@app.post("/batch-predict")
async def batch_predict(files: List[UploadFile] = File(...)):
    # Implement batch prediction
    pass
```

### Custom Preprocessing

Extend `ImageProcessor` class in `utils/image_processor.py`:

```python
@staticmethod
def custom_enhancement(image_array: np.ndarray) -> np.ndarray:
    # Your custom preprocessing
    return enhanced_image
```

### Multi-Model Ensemble

Modify `ModelManager` to load multiple models and combine predictions.

## Troubleshooting

### Model Not Loading

- Check `MODEL_PATH` in `.env`
- Ensure model file exists in `models/` directory
- Check file permissions
- Review logs for specific error messages

### Image Processing Errors

- Verify image file is not corrupted
- Check image dimensions (min 100x100, max 5000x5000)
- Ensure file format is supported
- Try converting image to RGB format

### Performance Issues

- Enable GPU support for TensorFlow
- Reduce image size if processing is slow
- Use model quantization
- Implement request queuing for high load

## Dataset Information

The model is designed to be trained on the **APTOS 2019 Blindness Detection** dataset:
- Available on Kaggle
- ~3,662 retinal fundus images
- 5 severity classes (0-4)
- High-resolution color images

## License

This project is provided as foundational code for educational and development purposes.

## Contributing

This is a foundational codebase designed to be extended. Key areas for enhancement:

- Model accuracy improvements
- Additional preprocessing techniques
- Batch prediction support
- Real-time monitoring and logging
- Integration with medical imaging standards (DICOM)
- Multi-language support
- Advanced analytics and reporting

## Support

For questions or issues:
1. Check API documentation at `/docs`
2. Review logs for error messages
3. Verify configuration in `.env`
4. Test with sample images

## Acknowledgments

- APTOS 2019 Blindness Detection dataset
- TensorFlow and Keras teams
- FastAPI framework
- OpenCV community

---

**Note**: This is a foundational backend implementation. For production medical use, ensure compliance with relevant healthcare regulations (HIPAA, FDA, etc.) and conduct thorough clinical validation.
