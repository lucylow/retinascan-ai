# RetinaScan AI - Flask Backend

Flask-based backend API for diabetic retinopathy detection using deep learning.

## Project Structure

```
backend/
├── app.py                  # Main Flask application
├── model_loader.py         # Model loading and prediction
├── image_processor.py      # Image preprocessing
├── config.py               # Configuration settings
├── requirements.txt        # Python dependencies
├── Procfile               # Heroku deployment config
├── runtime.txt            # Python version
├── .env                   # Environment variables
└── models/                # Trained model files
    └── retina_model.h5
```

## Setup

### 1. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 2. Configure Environment

Copy `.env` file and update with your settings:

```env
SECRET_KEY=your-secret-key-here
DEBUG=True
MODEL_PATH=models/retina_model.h5
CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
```

### 3. Run Locally

```bash
python app.py
```

The server will start at `http://localhost:5000`

## API Endpoints

### Health Check
```bash
GET /api/health
```

### Model Information
```bash
GET /api/model/info
```

### Prediction
```bash
POST /api/predict
Content-Type: multipart/form-data
Body: image file
```

### Batch Prediction
```bash
POST /api/predict/batch
Content-Type: multipart/form-data
Body: images[] files (max 10)
```

### Diagnosis Information
```bash
GET /api/diagnosis/info
```

## Usage Examples

### Testing with curl

```bash
# Health check
curl http://localhost:5000/api/health

# Model info
curl http://localhost:5000/api/model/info

# Single prediction
curl -X POST -F "image=@retina_image.jpg" http://localhost:5000/api/predict

# Batch prediction
curl -X POST -F "images[]=@image1.jpg" -F "images[]=@image2.jpg" http://localhost:5000/api/predict/batch
```

### Expected Response Format

```json
{
  "success": true,
  "diagnosis": "Moderate Diabetic Retinopathy",
  "severity_level": 2,
  "confidence": 0.87,
  "probabilities": {
    "No Diabetic Retinopathy": 0.05,
    "Mild Diabetic Retinopathy": 0.08,
    "Moderate Diabetic Retinopathy": 0.87,
    "Severe Diabetic Retinopathy": 0.00,
    "Proliferative Diabetic Retinopathy": 0.00
  },
  "recommendation": "Moderate non-proliferative diabetic retinopathy detected. Urgent consultation with ophthalmologist recommended within 3-6 months.",
  "timestamp": "2023-10-27T10:30:00.123456",
  "filename": "retina_image.jpg"
}
```

## Deployment

### Heroku Deployment

```bash
heroku create your-app-name
git add .
git commit -m "Deploy RetinaScan AI backend"
git push heroku main
```

## Technology Stack

- **Flask**: Web framework
- **TensorFlow/Keras**: Deep learning
- **OpenCV**: Image processing
- **Pillow**: Image manipulation
- **Gunicorn**: Production WSGI server

