# Integration Guide - AI Improvements

## 🚀 Quick Integration (5 Minutes)

This guide shows you how to integrate the improved AI components into your existing RetinaScan application.

---

## Option 1: Replace Files (Recommended)

### Step 1: Backup Original Files
```bash
cd retinascan-backend
mkdir backup
cp utils/model_manager.py backup/
cp utils/image_processor.py backup/
cp services/prediction_service.py backup/
cp config.py backup/
cp train_model.py backup/
```

### Step 2: Replace with Improved Versions
```bash
# Replace core files
mv utils/model_manager_improved.py utils/model_manager.py
mv utils/image_processor_improved.py utils/image_processor.py
mv services/prediction_service_improved.py services/prediction_service.py
mv config_improved.py config.py
mv train_model_improved.py train_model.py

# Update requirements
mv requirements_improved.txt requirements.txt
```

### Step 3: Update main.py

Update the response model to include new fields:

```python
class PredictionResponse(BaseModel):
    """Enhanced prediction response model"""
    success: bool
    severity_class: int
    severity_level: str
    confidence: float
    label: str
    recommendation: str
    structured_recommendation: Dict[str, str]
    class_probabilities: Dict[str, float]
    uncertainty: Dict[str, Any]  # NEW: Uncertainty metrics
    risk_stratification: Dict[str, Any]  # NEW: Risk assessment
    image_quality: Dict[str, float]  # NEW: Quality metrics
    visualization: Optional[Dict[str, str]] = None  # NEW: Grad-CAM
    timestamp: str
```

Update the predict endpoint:

```python
@app.post("/predict", response_model=PredictionResponse)
async def predict_retinopathy(file: UploadFile = File(...)):
    """
    Predict diabetic retinopathy severity from retinal fundus image
    Now with explainable AI and uncertainty estimation!
    """
    contents = await file.read()
    
    try:
        # Use improved prediction service
        prediction = await run_in_threadpool(
            PredictionService.predict_image, 
            file.filename, 
            contents,
            generate_visualization=True  # Enable Grad-CAM
        )
        
        # Format class probabilities
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
            uncertainty=prediction.get('uncertainty', {}),  # NEW
            risk_stratification=prediction.get('risk_stratification', {}),  # NEW
            image_quality=prediction.get('image_quality', {}),  # NEW
            visualization=prediction.get('visualization'),  # NEW
            timestamp=datetime.utcnow().isoformat()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in /predict: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )
```

### Step 4: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 5: Test the API
```bash
# Start the server
python main.py

# In another terminal, test the endpoint
curl -X POST "http://localhost:8000/predict" \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@test_retina_image.jpg"
```

---

## Option 2: Side-by-Side (For Testing)

Keep both versions and switch between them:

### Create a feature flag in config.py
```python
class Config:
    # ... existing config ...
    
    # Feature flags
    USE_IMPROVED_AI = os.getenv("USE_IMPROVED_AI", "true").lower() == "true"
```

### Conditional imports in main.py
```python
from config import Config

if Config.USE_IMPROVED_AI:
    from utils.model_manager_improved import model_manager
    from utils.image_processor_improved import ImageProcessor
    from services.prediction_service_improved import PredictionService
else:
    from utils.model_manager import model_manager
    from utils.image_processor import ImageProcessor
    from services.prediction_service import PredictionService
```

### Switch versions via environment variable
```bash
# Use improved version
export USE_IMPROVED_AI=true
python main.py

# Use original version
export USE_IMPROVED_AI=false
python main.py
```

---

## 🎨 Frontend Integration

### Display Grad-CAM Visualization

The API now returns a base64-encoded Grad-CAM overlay. Display it in your frontend:

#### React Example
```jsx
function PredictionResult({ prediction }) {
  return (
    <div className="prediction-result">
      <h2>Diagnosis: {prediction.label}</h2>
      <p>Confidence: {(prediction.confidence * 100).toFixed(1)}%</p>
      
      {/* NEW: Display Grad-CAM visualization */}
      {prediction.visualization && (
        <div className="visualization">
          <h3>AI Explanation</h3>
          <img 
            src={prediction.visualization.grad_cam_overlay} 
            alt="Grad-CAM Visualization"
          />
          <p className="description">
            {prediction.visualization.description}
          </p>
        </div>
      )}
      
      {/* NEW: Display uncertainty */}
      <div className="uncertainty">
        <h3>Prediction Confidence</h3>
        <p>Uncertainty: {(prediction.uncertainty.epistemic * 100).toFixed(2)}%</p>
        <p>Confidence Range: 
          {(prediction.uncertainty.confidence_interval.lower * 100).toFixed(1)}% - 
          {(prediction.uncertainty.confidence_interval.upper * 100).toFixed(1)}%
        </p>
      </div>
      
      {/* NEW: Display risk stratification */}
      <div className="risk-assessment">
        <h3>Risk Assessment</h3>
        <p className={`risk-level ${prediction.risk_stratification.risk_level}`}>
          Risk Level: {prediction.risk_stratification.risk_level}
        </p>
        {prediction.risk_stratification.requires_specialist_review && (
          <div className="alert">
            ⚠️ Specialist review recommended
          </div>
        )}
        <p>{prediction.risk_stratification.recommendation_note}</p>
      </div>
      
      {/* Existing recommendation */}
      <div className="recommendation">
        <h3>Recommendation</h3>
        <p><strong>Action:</strong> {prediction.structured_recommendation.action}</p>
        <p><strong>Urgency:</strong> {prediction.structured_recommendation.urgency}</p>
        <p><strong>Follow-up:</strong> {prediction.structured_recommendation.follow_up_time}</p>
        <p>{prediction.structured_recommendation.note}</p>
      </div>
    </div>
  );
}
```

#### CSS for Visualization
```css
.visualization {
  margin: 20px 0;
  padding: 15px;
  border: 2px solid #4CAF50;
  border-radius: 8px;
}

.visualization img {
  max-width: 100%;
  height: auto;
  border-radius: 4px;
}

.visualization .description {
  margin-top: 10px;
  font-size: 14px;
  color: #666;
}

.risk-level {
  padding: 10px;
  border-radius: 4px;
  font-weight: bold;
}

.risk-level.Low { background-color: #4CAF50; color: white; }
.risk-level.Medium { background-color: #FFC107; color: black; }
.risk-level.High { background-color: #FF9800; color: white; }
.risk-level.Critical { background-color: #F44336; color: white; }
.risk-level.Emergency { background-color: #D32F2F; color: white; }
```

---

## 📊 API Response Example

### Before (Original)
```json
{
  "success": true,
  "severity_class": 2,
  "severity_level": "Moderate",
  "confidence": 0.87,
  "label": "Moderate Diabetic Retinopathy",
  "recommendation": "Urgent consultation recommended...",
  "structured_recommendation": {
    "action": "Immediate referral to a retinal specialist.",
    "urgency": "High",
    "follow_up_time": "3-6 months",
    "note": "Significant changes observed..."
  },
  "class_probabilities": {
    "class_0": 0.02,
    "class_1": 0.08,
    "class_2": 0.87,
    "class_3": 0.02,
    "class_4": 0.01
  },
  "timestamp": "2025-10-28T15:30:00Z"
}
```

### After (Improved)
```json
{
  "success": true,
  "severity_class": 2,
  "severity_level": "Moderate",
  "confidence": 0.87,
  "label": "Moderate Diabetic Retinopathy",
  "recommendation": "Urgent consultation recommended...",
  "structured_recommendation": {
    "action": "Immediate referral to a retinal specialist.",
    "urgency": "High",
    "follow_up_time": "3-6 months",
    "note": "Significant changes observed..."
  },
  "class_probabilities": {
    "class_0": 0.02,
    "class_1": 0.08,
    "class_2": 0.87,
    "class_3": 0.02,
    "class_4": 0.01
  },
  "uncertainty": {
    "epistemic": 0.05,
    "entropy": 0.42,
    "confidence_interval": {
      "lower": 0.77,
      "upper": 0.97
    }
  },
  "risk_stratification": {
    "risk_level": "High",
    "confidence_flag": "High",
    "uncertainty_flag": "Low",
    "recommendation_note": "Prediction is confident and reliable.",
    "requires_specialist_review": true
  },
  "image_quality": {
    "sharpness": 127.5,
    "brightness": 98.3,
    "contrast": 45.2
  },
  "visualization": {
    "grad_cam_overlay": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAA...",
    "description": "Highlighted regions show areas that influenced the AI decision. Warmer colors (red/yellow) indicate higher importance."
  },
  "timestamp": "2025-10-28T15:30:00Z"
}
```

---

## 🧪 Testing Checklist

After integration, verify:

- [ ] API starts without errors
- [ ] `/health` endpoint returns model info with new features
- [ ] `/predict` accepts image uploads
- [ ] Response includes all new fields
- [ ] Grad-CAM visualization is generated
- [ ] Uncertainty metrics are present
- [ ] Risk stratification works correctly
- [ ] Image quality assessment rejects bad images
- [ ] Frontend displays visualizations correctly

---

## 🐛 Troubleshooting

### Issue: Import errors
**Solution**: Make sure all files are in the correct directories:
```
retinascan-backend/
├── utils/
│   ├── model_manager.py (improved version)
│   └── image_processor.py (improved version)
├── services/
│   └── prediction_service.py (improved version)
├── config.py (improved version)
└── main.py (updated)
```

### Issue: TensorFlow errors
**Solution**: Ensure TensorFlow 2.15.0 is installed:
```bash
pip install tensorflow==2.15.0
```

### Issue: Grad-CAM not generating
**Solution**: Check that the model has convolutional layers:
```python
# In model_manager.py, verify grad_cam initialization
if self.grad_cam is None:
    logger.warning("Grad-CAM not initialized")
```

### Issue: High memory usage
**Solution**: Reduce Monte Carlo iterations for uncertainty:
```python
# In model_manager.py, line ~120
n_iterations = 5  # Reduce from 10 to 5
```

---

## 📚 Additional Resources

- **AI_IMPROVEMENTS.md**: Detailed explanation of all AI enhancements
- **API Documentation**: Visit `/docs` endpoint for interactive API docs
- **TensorBoard**: Monitor training with `tensorboard --logdir=logs/fit`

---

## 🎉 You're Done!

Your RetinaScan AI is now powered by:
- ✅ EfficientNet architecture
- ✅ Grad-CAM explainability
- ✅ Uncertainty estimation
- ✅ Advanced preprocessing
- ✅ Risk stratification

**Ready to win the hackathon! 🏆**
