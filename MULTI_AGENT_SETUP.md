# Multi-Agent System Setup Guide

## ✅ Installation

All dependencies are included in `requirements.txt`. Install them with:

```bash
pip install -r requirements.txt
```

**New dependencies added:**
- `flask==3.0.0` - For the monitoring dashboard

## 🚀 Quick Start

### 1. Run the Demo

```bash
python quick_integration.py
```

This will:
- Initialize all AI agents
- Process sample images through the workflow
- Display system performance metrics

### 2. Start Monitoring Dashboard

```python
from workflow_orchestrator import WorkflowOrchestrator
from monitoring_dashboard import start_monitoring

# Initialize orchestrator
orchestrator = WorkflowOrchestrator("models/retina_model_final.h5")

# Start dashboard (runs in main thread)
start_monitoring(orchestrator, port=5001)
```

Then visit: http://localhost:5001

### 3. Integrate with FastAPI

Add a new endpoint to your `main.py`:

```python
from workflow_orchestrator import WorkflowOrchestrator
import cv2
import numpy as np

# Initialize once (global variable)
ai_orchestrator = WorkflowOrchestrator("models/retina_model_final.h5")

@app.post("/predict/ai-agent")
async def predict_with_ai_agents(file: UploadFile = File(...)):
    """
    Predict using multi-agent AI workflow system
    """
    contents = await file.read()
    
    # Convert to numpy array
    nparr = np.frombuffer(contents, np.uint8)
    image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    
    if image is None:
        raise HTTPException(status_code=400, detail="Invalid image")
    
    # Process with multi-agent system
    result = await run_in_threadpool(
        ai_orchestrator.process_image,
        image,
        file.filename
    )
    
    return result["final_report"]
```

## 📁 Files Created

1. **ai_agents.py** (650+ lines)
   - BaseAgent class
   - DataProcessorAgent
   - ModelSpecialistAgent
   - DiagnosisAnalystAgent
   - QualityControllerAgent
   - ReportGeneratorAgent

2. **workflow_orchestrator.py** (340+ lines)
   - WorkflowOrchestrator class
   - PerformanceMonitor class
   - Batch processing support
   - Report export (JSON/HTML)

3. **monitoring_dashboard.py** (305+ lines)
   - Flask-based dashboard
   - Real-time metrics API
   - Agent status monitoring
   - Workflow history tracking

4. **quick_integration.py**
   - Demo script
   - Usage examples

## 🔧 Configuration

### Model Path
Default: `models/retina_model_final.h5`

If model not found, system creates a mock model for demonstration.

### Quality Thresholds
Located in each agent class:
- **DataProcessorAgent**: `quality_threshold = 0.7`
- **ModelSpecialistAgent**: `confidence_threshold = 0.6`
- **QualityControllerAgent**: Various quality standards

### Dashboard Port
Default: `5001`

Change in `start_monitoring(orchestrator, port=YOUR_PORT)`

## 📊 Usage Examples

### Process Single Image

```python
from workflow_orchestrator import WorkflowOrchestrator
import numpy as np

orchestrator = WorkflowOrchestrator("models/retina_model_final.h5")
image = np.random.rand(512, 512, 3) * 255
result = orchestrator.process_image(image, "test_001")

# Access results
report = result["final_report"]
diagnosis = report["diagnostic_findings"]["primary_diagnosis"]
confidence = report["diagnostic_findings"]["confidence_score"]
```

### Batch Processing

```python
images = [image1, image2, image3]
results = orchestrator.batch_process(images, parallel=True)

for i, result in enumerate(results):
    if "error" not in result:
        print(f"Image {i}: {result['final_report']['diagnostic_findings']['primary_diagnosis']}")
```

### Export Reports

```python
# JSON export
json_report = orchestrator.export_report("workflow_id", format="json")

# HTML export (saves to file)
html_report = orchestrator.export_report("workflow_id", format="html")
with open("report.html", "w") as f:
    f.write(html_report)
```

### System Metrics

```python
metrics = orchestrator.get_system_metrics()

print(f"Total workflows: {metrics['total_workflows']}")
print(f"Success rate: {metrics['successful_workflows'] / metrics['total_workflows']:.1%}")

# Agent-specific metrics
for agent_name, perf in metrics["agent_performance"].items():
    print(f"{agent_name}: {perf['tasks_processed']} tasks, "
          f"{perf['success_rate']:.1%} success rate")
```

## 🧪 Testing

### Test Imports

```python
# Test all modules can be imported
python3 -c "from ai_agents import *; from workflow_orchestrator import WorkflowOrchestrator; from monitoring_dashboard import start_monitoring; print('✅ All imports successful')"
```

### Test Workflow

```python
from workflow_orchestrator import WorkflowOrchestrator
import numpy as np

orchestrator = WorkflowOrchestrator("models/retina_model_final.h5")
test_image = np.random.rand(224, 224, 3) * 255

try:
    result = orchestrator.process_image(test_image, "test")
    print("✅ Workflow test successful!")
    print(f"Diagnosis: {result['final_report']['diagnostic_findings']['primary_diagnosis']}")
except Exception as e:
    print(f"❌ Error: {e}")
```

## 🐛 Troubleshooting

### Import Errors
- Ensure all files are in the project root
- Check Python path includes project directory
- Verify all dependencies are installed

### Model Loading Errors
- System will automatically use mock model if real model not found
- Check model file path in WorkflowOrchestrator initialization

### Dashboard Not Loading
- Ensure Flask is installed: `pip install flask`
- Check port 5001 is not in use
- Verify templates directory exists (created automatically)

### Image Processing Errors
- Ensure OpenCV is installed: `pip install opencv-python-headless`
- Check image format is supported (numpy array with shape (H, W, 3))
- Verify image values are in correct range (0-255)

## 📈 Performance

### Typical Processing Times
- Data Processing: ~0.1-0.5 seconds
- Model Prediction: ~0.5-2.0 seconds (depends on model)
- Diagnosis Analysis: <0.1 seconds
- Quality Control: <0.1 seconds
- Report Generation: <0.1 seconds

**Total workflow time: ~1-3 seconds per image**

### Optimization Tips
- Use batch processing for multiple images
- Enable parallel processing for batches
- Cache model loading (already done in orchestrator)
- Use GPU if available (TensorFlow will auto-detect)

## 🔗 Integration Points

### With Existing FastAPI Backend
The multi-agent system complements your existing `/predict` endpoint:
- Existing endpoint: Direct model prediction
- New AI-agent endpoint: Full workflow with quality control and clinical analysis

### With Frontend
The dashboard is separate but can be integrated:
- Add link to dashboard in frontend navigation
- Use API endpoints for metrics visualization
- Display agent performance in admin panel

## 📝 Notes

- All agents maintain their own performance metrics
- Workflow history is stored in memory (consider persistence for production)
- Quality thresholds can be adjusted per agent
- Mock model is used if real model file not found (for demonstration)

## 🎯 Next Steps

1. **Production Deployment**
   - Add database persistence for workflow history
   - Implement message queue for agent communication
   - Add authentication to dashboard
   - Set up logging and error tracking

2. **Enhancements**
   - Agent learning from feedback
   - Distributed agent execution
   - Integration with medical databases
   - Advanced error recovery

3. **Integration**
   - Connect with existing FastAPI endpoints
   - Add frontend visualization
   - Set up automated monitoring
   - Implement alerting system

---

**For detailed API documentation, see MULTI_AGENT_README.md**

