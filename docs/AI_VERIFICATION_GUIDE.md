# AI Verification Guide - RetinaScan

This guide helps you verify that the AI components are working properly.

## Quick Verification Steps

### 1. Verify Supabase Edge Function AI (Currently Active)

The frontend uses Supabase Edge Function which calls Lovable AI (Gemini 2.5 Flash).

**Check Configuration:**
```bash
# Check if edge function is deployed
supabase functions list

# Check logs
supabase functions logs analyze-retina --project-ref your-project-id
```

**Test via Frontend:**
1. Start the frontend: `npm run dev`
2. Upload a retinal image
3. Click "Analyze Image"
4. Check browser console for errors
5. Verify results are displayed

**Common Issues:**
- **"LOVABLE_API_KEY not configured"**: Set secret in Supabase
  ```bash
  supabase secrets set LOVABLE_API_KEY=your-key --project-ref your-project-id
  ```
- **"Configuration Required" banner**: Set environment variables in Lovable
- **Analysis fails**: Check Supabase function logs

### 2. Verify FastAPI Backend AI (Alternative)

The FastAPI backend uses TensorFlow with MobileNetV2/EfficientNet.

**Start Backend:**
```bash
# Install dependencies
pip install -r requirements.txt

# Start server
python3 main.py
```

**Test Backend:**
```bash
# Test health endpoint
curl http://localhost:8000/health

# Test model info
curl http://localhost:8000/model/info

# Test with image (replace with actual image path)
curl -X POST "http://localhost:8000/predict" \
  -F "file=@path/to/retinal_image.jpg"
```

**Or use the test script:**
```bash
python3 test_api.py http://localhost:8000 path/to/image.jpg
```

### 3. Verify Image Processing

**Test Image Processor:**
```python
from utils.image_processor import ImageProcessor

# Test file extension validation
print(ImageProcessor.validate_file_extension("test.jpg"))  # Should be True
print(ImageProcessor.validate_file_extension("test.pdf"))  # Should be False
```

### 4. Verify Model Manager

**Test Model Manager:**
```python
from utils.model_manager import model_manager

# Load model
loaded = model_manager.load_model()
print(f"Model loaded: {loaded}")

# Get model info
info = model_manager.get_model_info()
print(f"Model info: {info}")
```

## Expected Behavior

### When AI is Working Properly:

1. **Supabase Edge Function:**
   - Upload image → Image processing starts
   - Supabase function invoked successfully
   - Lovable AI Gateway called
   - Returns JSON with diagnosis
   - Results displayed with:
     - Severity class (0-4)
     - Severity level (None/Mild/Moderate/Severe/Proliferative)
     - Confidence score
     - Class probabilities
     - Structured recommendations

2. **FastAPI Backend:**
   - Model loads on startup
   - Health check returns `model_loaded: true`
   - Prediction endpoint returns proper JSON
   - Results include all required fields

## Troubleshooting

### Issue: Model Not Loading

**Symptoms:**
- FastAPI shows `model_loaded: false`
- Health check fails

**Solutions:**
1. Check if `models/retina_model.h5` exists
2. If not, the system will create a dummy model
3. To train a real model:
   ```bash
   python3 train_model.py
   ```

### Issue: Import Errors

**Symptoms:**
- `ModuleNotFoundError` when importing services
- Cannot import `PredictionService`

**Solution:**
The imports have been fixed to use absolute imports instead of relative imports.

### Issue: Image Processing Fails

**Symptoms:**
- "Image preprocessing failed" error
- "Invalid file type" error

**Solutions:**
1. Check file is supported format (PNG, JPG, JPEG, BMP, TIFF)
2. Check file size is under 16MB
3. Verify image is valid

### Issue: AI Returns Low Confidence

**Symptoms:**
- Confidence scores are very low (< 0.5)
- Results seem random

**Solutions:**
1. For Supabase AI: Check Lovable API has credits
2. For FastAPI: Train model on real data
3. Upload higher quality images
4. Check image meets quality requirements

## Verification Checklist

- [ ] Environment variables configured
- [ ] Supabase Edge Function deployed
- [ ] LOVABLE_API_KEY set in Supabase secrets
- [ ] Frontend can upload images
- [ ] Analysis completes successfully
- [ ] Results display correctly
- [ ] All fields present in response
- [ ] No errors in browser console
- [ ] No errors in Supabase logs

## Next Steps

Once verified:

1. **For Production:**
   - Train model on real dataset
   - Fine-tune hyperparameters
   - Monitor prediction quality
   - Add logging and analytics

2. **For Development:**
   - Use improved versions:
     - `services/prediction_service_improved.py`
     - `utils/model_manager_improved.py`
     - `utils/image_processor_improved.py`
   - Enable Grad-CAM visualizations
   - Add uncertainty estimation

## Quick Test Commands

```bash
# Test AI system
python3 test_ai.py

# Test API
python3 test_api.py

# Check Supabase function
supabase functions logs analyze-retina --follow

# Start backend
python3 main.py

# Start frontend
npm run dev
```

## AI Architecture

### Current Setup (Supabase + Gemini):
```
User → Frontend → Supabase Edge Function → Lovable AI (Gemini 2.5 Flash) → Results
```

### Alternative Setup (FastAPI + TensorFlow):
```
User → Frontend → FastAPI → TensorFlow Model → Results
```

Both systems are available and can be used based on your needs.

