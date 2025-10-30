# RetinaScan AI

<div align="center">

**AI-powered diabetic retinopathy detection from retinal fundus images**

[Features](#-features) • [Tech Stack](#-technology-stack) • [Quick Start](#-quick-start) • [Architecture](#-architecture) • [Deployment](#-deployment)

</div>

---

## 🎯 Overview

RetinaScan AI is a full-stack application that uses deep learning and computer vision to detect and classify diabetic retinopathy severity from retinal fundus images. The system provides accurate, fast, and detailed diagnosis reports with clinical recommendations.

### What is Diabetic Retinopathy?

Diabetic Retinopathy (DR) is a diabetes complication that affects the eyes. It's caused by damage to blood vessels in the light-sensitive tissue at the back of the eye (retina). Early detection is crucial for preventing vision loss.

## ✨ Features

- **🤖 AI-Powered Analysis**: Deep learning models (MobileNetV2, ResNet50) trained on APTOS 2019 dataset
- **🔬 5-Class Classification**: Precise severity detection from No DR to Proliferative DR
- **⚡ Real-time Processing**: Fast inference with GPU acceleration support
- **🖼️ Advanced Image Processing**: CLAHE enhancement, border cropping, quality optimization
- **📊 Detailed Reports**: Severity scores, confidence levels, and structured clinical recommendations
- **🌐 Full-Stack Architecture**: Modern React frontend + FastAPI backend + Supabase integration
- **🚀 Production Ready**: Docker support, health checks, error handling, and monitoring
- **📱 Beautiful UI**: Responsive design with Tailwind CSS and shadcn/ui components

## 📋 Severity Classification

| Class | Severity Level | Description |
|-------|---------------|-------------|
| 0 | **No DR** | No diabetic retinopathy detected |
| 1 | **Mild NPDR** | Mild non-proliferative diabetic retinopathy |
| 2 | **Moderate NPDR** | Moderate non-proliferative diabetic retinopathy |
| 3 | **Severe NPDR** | Severe non-proliferative diabetic retinopathy |
| 4 | **PDR** | Proliferative diabetic retinopathy |

## 🏗️ Technology Stack

### Backend
- **Framework**: FastAPI (high-performance async Python web framework)
- **ML Framework**: TensorFlow 2.13.0 with Keras
- **Architectures**: MobileNetV2, ResNet50 (transfer learning)
- **Image Processing**: OpenCV, Pillow
- **Server**: Uvicorn (ASGI server)
- **Validation**: Pydantic

### Frontend
- **Framework**: React 18 with TypeScript
- **Build Tool**: Vite
- **Styling**: Tailwind CSS
- **UI Components**: shadcn/ui + Radix UI
- **State Management**: React Query
- **Icons**: Lucide React

### Infrastructure
- **Backend API**: FastAPI on Uvicorn
- **Edge Functions**: Supabase Edge Functions (Deno)
- **AI Gateway**: Lovable AI (alternative analysis pipeline)
- **Containerization**: Docker + Docker Compose

## 🚀 Quick Start

### Prerequisites

- Python 3.8+ (for backend)
- Node.js 18+ (for frontend)
- npm or yarn
- 2GB+ free disk space

### Option 1: Local Development (Full Stack)

#### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/retinascan-ai.git
cd retinascan-ai
```

#### 2. Set Up Backend

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create models directory
mkdir -p models
```

#### 3. Set Up Frontend

```bash
# Install dependencies
npm install

# Start development server
npm run dev
```

#### 4. Run Backend

```bash
# Start API server
python main.py
```

The backend will be available at `http://localhost:8000`  
The frontend will be available at `http://localhost:5173`

### Option 2: Docker Deployment

```bash
# Build and run with Docker Compose
docker-compose up

# Or build individual container
docker build -t retinascan-backend .
docker run -p 8000:8000 retinascan-backend
```

## 📁 Project Structure

```
retinascan-ai/
├── src/                          # Frontend source (Lovable workspace)
│   ├── components/               # React components
│   │   ├── ImageUpload.tsx      # Image upload interface
│   │   ├── DiagnosisResult.tsx  # Results display
│   │   ├── ConfigWarning.tsx    # Configuration alerts
│   │   └── ui/                  # shadcn/ui components
│   ├── pages/                   # Page components
│   │   └── Index.tsx            # Main application page
│   ├── hooks/                   # Custom React hooks
│   ├── lib/                     # Utility functions
│   ├── integrations/            # Third-party integrations
│   │   └── supabase/           # Supabase client
│   ├── App.tsx                  # Root component
│   ├── main.tsx                 # Entry point
│   └── README.md                # Frontend documentation
│
├── supabase/                     # Supabase configuration
│   └── functions/
│       └── analyze-retina/      # Edge function for AI analysis
│           └── index.ts         # Lovable AI integration
│
├── services/                     # Backend services
│   └── prediction_service.py   # Prediction logic
│
├── utils/                        # Utility modules
│   ├── image_processor.py      # Image preprocessing
│   └── model_manager.py         # Model loading/inference
│
├── models/                       # Trained model files
│   └── retina_model.h5          # Saved model (after training)
│
├── main.py                       # FastAPI application entry
├── config.py                     # Configuration management
├── train_model.py                # Model training script
├── prepare_data.py               # Data preparation utilities
├── requirements.txt              # Python dependencies
├── package.json                  # Node.js dependencies
├── Dockerfile                    # Docker configuration
├── docker-compose.yml            # Docker Compose setup
├── vite.config.ts                # Vite configuration
├── tailwind.config.ts            # Tailwind CSS configuration
└── tsconfig.json                 # TypeScript configuration
```

> 📖 **For detailed file navigation and Lovable setup, see [LOVABLE_FILE_STRUCTURE.md](LOVABLE_FILE_STRUCTURE.md)**

## 🧪 Usage

### API Endpoints

#### Health Check
```bash
GET /health
```
Returns server status and model information.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-01-20T10:30:00Z",
  "model_loaded": true,
  "model_info": {
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
  "recommendation": "Moderate non-proliferative diabetic retinopathy detected...",
  "structured_recommendation": {
    "action": "Immediate referral to a retinal specialist.",
    "urgency": "High",
    "follow_up_time": "3-6 months",
    "note": "Significant changes observed. Specialist consultation is required..."
  },
  "class_probabilities": {
    "class_0": 0.02,
    "class_1": 0.05,
    "class_2": 0.87,
    "class_3": 0.04,
    "class_4": 0.02
  },
  "timestamp": "2025-01-20T10:30:00Z"
}
```

### Testing the API

#### With cURL
```bash
# Health check
curl http://localhost:8000/health

# Predict from image
curl -X POST "http://localhost:8000/predict" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@/path/to/retinal_image.jpg"
```

#### With Python
```python
import requests

# Health check
response = requests.get("http://localhost:8000/health")
print(response.json())

# Predict
with open("retinal_image.jpg", "rb") as f:
    files = {"file": f}
    response = requests.post(
        "http://localhost:8000/predict", 
        files=files
    )
    print(response.json())
```

#### Interactive Documentation
Visit the auto-generated API docs:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 🏛️ Architecture

### System Components

#### 1. **API Layer** (`main.py`)
- FastAPI application with async endpoints
- Request validation and error handling
- CORS middleware configuration
- Health check and monitoring

#### 2. **Image Processing** (`utils/image_processor.py`)
Advanced preprocessing pipeline:
1. File validation (type, size, integrity)
2. Color conversion (RGB normalization)
3. Quality enhancement (contrast, sharpness)
4. Border cropping (remove black regions)
5. CLAHE application (adaptive histogram equalization)
6. Resizing (224×224 with Lanczos interpolation)
7. Normalization (pixel values to [0, 1])
8. Batch dimension addition

#### 3. **Model Management** (`utils/model_manager.py`)
- Lazy model loading
- Fallback dummy model creation
- Inference execution
- Result interpretation
- Model metadata retrieval

#### 4. **Frontend** (`src/`)
- React components with TypeScript
- Image upload with drag-and-drop
- Real-time analysis with progress indicators
- Responsive result display with UI animations
- Toast notifications

#### 5. **Edge Functions** (`supabase/functions/`)
- Supabase Edge Functions with Deno
- Lovable AI integration for alternative analysis
- Structured recommendation generation

### Model Architecture

```
Input Image (224, 224, 3)
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
Output: 5 classes (0-4 severity)
```

### Data Flow

```
Client Upload
    ↓
Frontend Validation
    ↓
Supabase Edge Function (or Backend API)
    ↓
Image Preprocessing Pipeline
    ↓
Model Inference
    ↓
Result Interpretation
    ↓
Structured Response with Recommendations
    ↓
Client Display
```

## 🧠 Model Training

### Preparing Data

Organize your training data:

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

### Training Process

```python
from train_model import RetinaModelTrainer

# Initialize trainer
trainer = RetinaModelTrainer(
    data_dir="data/train",
    model_architecture="mobilenetv2"  # or "resnet50"
)

# Build and train
trainer.build_model()
trainer.train(epochs=30, fine_tune_epochs=15)
trainer.evaluate()

# Save model
trainer.model.save("models/retina_model.h5")
```

### Dataset

The model is trained on the **APTOS 2019 Blindness Detection** dataset:
- Available on [Kaggle](https://www.kaggle.com/c/aptos2019-blindness-detection)
- ~3,662 retinal fundus images
- 5 severity classes (0-4)
- High-resolution color images

## 🚢 Deployment

### Production Backend with Gunicorn

```bash
pip install gunicorn
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

### Docker Deployment

```bash
# Build image
docker build -t retinascan-backend .

# Run container
docker run -d \
  -p 8000:8000 \
  -v $(pwd)/models:/app/models \
  retinascan-backend
```

### Frontend Build

```bash
# Build for production
npm run build

# Preview production build
npm run preview

# Output in dist/ directory
```

### Environment Configuration

Create a `.env` file:

```env
# Server Configuration
HOST=0.0.0.0
PORT=8000
DEBUG=False

# Model Configuration
MODEL_PATH=models/retina_model.h5

# CORS Configuration
CORS_ORIGINS=http://localhost:3000,https://yourdomain.com

# File Upload Limits
MAX_UPLOAD_SIZE=16777216  # 16MB

# Supabase (for Edge Functions)
SUPABASE_URL=your_supabase_url
LOVABLE_API_KEY=your_lovable_api_key
```

## 🔧 Configuration

### Backend Settings

Edit `config.py` to customize:
- Image input size
- Number of classes
- Diagnosis labels and recommendations
- Allowed file extensions
- File size limits

### Frontend Settings

Edit `src/lib/config.ts` to customize:
- API endpoints
- Upload limits
- UI configuration

## 📊 Performance

- **Inference Time**: 100-500ms per image (CPU)
- **Inference Time**: 50-200ms per image (GPU)
- **Preprocessing Overhead**: 50-100ms
- **Total Latency**: 150-600ms end-to-end

### Optimization Tips

- Use GPU for faster inference
- Enable model quantization for edge deployment
- Implement caching for frequently accessed predictions
- Use CDN for static frontend assets

## 🐛 Troubleshooting

### Model Not Loading
```bash
# Check model file exists
ls -lh models/retina_model.h5

# Verify permissions
chmod 644 models/retina_model.h5

# Review logs for errors
python main.py
```

### Image Upload Fails
- Check file size (max 16MB)
- Verify file format (PNG, JPG, JPEG, BMP, TIFF)
- Ensure image dimensions (min 100×100, max 5000×5000)
- Validate image is not corrupted

### Frontend Issues
```bash
# Clear node modules and reinstall
rm -rf node_modules package-lock.json
npm install

# Clear build cache
rm -rf dist

# Check TypeScript errors
npm run build
```

## 📚 Documentation

- [Quick Start Guide](QUICKSTART.md) - Get started in 5 minutes
- [Architecture Details](ARCHITECTURE.md) - Deep dive into system design
- [Deployment Guide](DEPLOYMENT_GUIDE.md) - Production deployment instructions
- [Integration Guide](INTEGRATION_GUIDE.md) - Frontend-backend integration
- [Lovable File Structure](LOVABLE_FILE_STRUCTURE.md) - File organization for Lovable development
- [Lovable Setup Guide](LOVABLE_SETUP.md) - Lovable-specific setup instructions

## 🤝 Contributing

This project is open to contributions. Areas for enhancement:

- Model accuracy improvements
- Additional preprocessing techniques
- Batch prediction support
- Real-time monitoring and logging
- DICOM medical imaging support
- Multi-language support
- Advanced analytics and reporting
- WebRTC for real-time video analysis

## ⚠️ Disclaimer

**This tool is for research and educational purposes only.**

- Always consult a qualified healthcare professional for medical diagnosis
- Not intended for use in clinical decision-making
- Results should not replace professional medical advice
- Ensure compliance with relevant healthcare regulations (HIPAA, FDA, etc.)
- Conduct thorough clinical validation before production use

## 📄 License

This project is provided as foundational code for educational and development purposes.

## 🙏 Acknowledgments

- [APTOS 2019 Blindness Detection](https://www.kaggle.com/c/aptos2019-blindness-detection) dataset
- [TensorFlow](https://www.tensorflow.org/) and Keras teams
- [FastAPI](https://fastapi.tiangolo.com/) framework
- [OpenCV](https://opencv.org/) community
- [Supabase](https://supabase.com/) for edge functions
- [Lovable](https://lovable.dev/) for AI integration

---

<div align="center">

**Built with ❤️ for early detection of diabetic retinopathy**

[Report Bug](https://github.com/yourusername/retinascan-ai/issues) • [Request Feature](https://github.com/yourusername/retinascan-ai/issues)

</div>
