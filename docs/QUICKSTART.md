# RetinaScan AI - Quick Start Guide

Get up and running with the RetinaScan AI backend in minutes.

## Prerequisites

- Python 3.8 or higher
- pip package manager
- 2GB+ free disk space
- Internet connection (for downloading dependencies)

## Installation (5 minutes)

### Step 1: Set Up Virtual Environment

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
# On Linux/Mac:
source venv/bin/activate
# On Windows:
venv\Scripts\activate
```

### Step 2: Install Dependencies

```bash
pip install -r requirements.txt
```

This will install all required packages including TensorFlow, FastAPI, and image processing libraries.

### Step 3: Configure Environment

```bash
# Copy environment template
cp .env.example .env

# Edit .env if needed (optional for quick start)
```

## Running the Server (1 minute)

### Start the API Server

```bash
python main.py
```

You should see output like:
```
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Loading ML model...
INFO:     Model loaded successfully
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000
```

The API is now running at `http://localhost:8000`

## Testing the API (2 minutes)

### Option 1: Interactive API Documentation

Open your browser and visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

You can test all endpoints directly from the browser interface.

### Option 2: Command Line Testing

**Test health endpoint:**
```bash
curl http://localhost:8000/health
```

**Test prediction (with your own retinal image):**
```bash
curl -X POST "http://localhost:8000/predict" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@/path/to/your/retinal_image.jpg"
```

### Option 3: Python Test Script

```bash
python test_api.py
```

This runs a comprehensive test suite of all endpoints.

### Option 4: Example Client

```bash
python example_client.py
```

Demonstrates how to use the API from Python code.

## Understanding the Response

When you send an image for prediction, you'll get a response like:

```json
{
  "success": true,
  "severity_class": 2,
  "severity_level": "Moderate",
  "confidence": 0.87,
  "label": "Moderate Diabetic Retinopathy",
  "recommendation": "Moderate non-proliferative diabetic retinopathy detected...",
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

**Key Fields:**
- `severity_class`: Numeric class (0-4)
- `severity_level`: Human-readable severity
- `confidence`: Model confidence (0-1)
- `label`: Full diagnosis label
- `recommendation`: Clinical recommendation
- `class_probabilities`: Probability for each class

## Next Steps

### Using Your Own Model

1. Train a model using `train_model.py`
2. Save it to `models/retina_model.h5`
3. Restart the server

### Integrating with Your Frontend

The API is ready to be consumed by any frontend:

**JavaScript/React Example:**
```javascript
const formData = new FormData();
formData.append('file', imageFile);

const response = await fetch('http://localhost:8000/predict', {
  method: 'POST',
  body: formData
});

const result = await response.json();
console.log(result);
```

**Python Example:**
```python
import requests

with open('retinal_image.jpg', 'rb') as f:
    files = {'file': f}
    response = requests.post('http://localhost:8000/predict', files=files)
    result = response.json()
    print(result)
```

### Deployment

**Docker:**
```bash
docker build -t retinascan-backend .
docker run -p 8000:8000 retinascan-backend
```

**Docker Compose:**
```bash
docker-compose up
```

**Production Server:**
```bash
pip install gunicorn
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

## Common Issues

### Port Already in Use
```bash
# Change port in .env file
PORT=8001

# Or specify when running
uvicorn main:app --port 8001
```

### Model Not Loading
- The system creates a dummy model automatically if no trained model exists
- This is normal for initial testing
- Train your own model for production use

### Image Upload Fails
- Check file size (max 16MB)
- Verify file format (PNG, JPG, JPEG, BMP, TIFF)
- Ensure image is valid and not corrupted

### Dependencies Installation Issues
```bash
# Upgrade pip first
pip install --upgrade pip

# Install dependencies one by one if batch fails
pip install fastapi uvicorn tensorflow numpy pillow opencv-python-headless
```

## File Structure Overview

```
retinascan-backend/
├── main.py              # Main API application
├── config.py           # Configuration
├── train_model.py      # Model training
├── prepare_data.py     # Data preparation
├── test_api.py         # API tests
├── example_client.py   # Usage examples
├── requirements.txt    # Dependencies
├── utils/
│   ├── image_processor.py  # Image preprocessing
│   └── model_manager.py    # Model management
└── models/             # Trained models go here
```

## Getting Help

1. Check the full README.md for detailed documentation
2. Visit API docs at http://localhost:8000/docs
3. Review example_client.py for usage patterns
4. Check logs for error messages

## Development Workflow

1. **Start server**: `python main.py`
2. **Make changes**: Edit code files
3. **Restart server**: Stop (Ctrl+C) and start again
4. **Test changes**: Use test_api.py or browser

For auto-reload during development:
```bash
uvicorn main:app --reload
```

## Production Checklist

- [ ] Train model on real dataset
- [ ] Set DEBUG=False in .env
- [ ] Configure CORS_ORIGINS for your frontend
- [ ] Use production server (Gunicorn)
- [ ] Set up HTTPS/SSL
- [ ] Implement authentication if needed
- [ ] Set up monitoring and logging
- [ ] Configure backup for model files

---

**You're all set!** The backend is ready to detect diabetic retinopathy from retinal images.

For detailed documentation, see [README.md](README.md)
