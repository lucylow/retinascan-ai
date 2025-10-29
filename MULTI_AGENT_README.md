# RetinaScan AI - Multi-Agent Workflow System

## Overview

This directory contains a comprehensive multi-agent AI workflow system for RetinaScan AI. The system uses specialized AI agents that work together to process retinal images and generate detailed diagnostic reports.

## Architecture

### 🤖 Agents

1. **DataProcessorAgent** - Handles image preprocessing and quality assessment
2. **ModelSpecialistAgent** - Performs model inference and predictions
3. **DiagnosisAnalystAgent** - Provides clinical context and recommendations
4. **QualityControllerAgent** - Validates results and ensures quality standards
5. **ReportGeneratorAgent** - Generates comprehensive diagnostic reports

### 🔄 Workflow

```
Image Input
    ↓
Data Processor (preprocessing, quality check)
    ↓
Model Specialist (AI prediction)
    ↓
Diagnosis Analyst (clinical context)
    ↓
Quality Controller (validation)
    ↓
Report Generator (final report)
    ↓
Complete Diagnostic Report
```

## Files

- **ai_agents.py** - All agent class definitions
- **workflow_orchestrator.py** - Main orchestrator that coordinates agents
- **monitoring_dashboard.py** - Flask-based real-time monitoring dashboard
- **quick_integration.py** - Quick start demo script

## Quick Start

### Basic Usage

```python
from workflow_orchestrator import WorkflowOrchestrator
import numpy as np

# Initialize orchestrator
orchestrator = WorkflowOrchestrator("models/retina_model_final.h5")

# Process an image (numpy array)
image = np.random.rand(512, 512, 3) * 255  # Replace with actual image
result = orchestrator.process_image(image, "image_001")

# Access the final report
report = result["final_report"]
print(f"Diagnosis: {report['diagnostic_findings']['primary_diagnosis']}")
```

### Run Demo

```bash
python quick_integration.py
```

### Start Monitoring Dashboard

```python
from workflow_orchestrator import WorkflowOrchestrator
from monitoring_dashboard import start_monitoring

orchestrator = WorkflowOrchestrator("models/retina_model_final.h5")
start_monitoring(orchestrator, port=5001)
# Dashboard available at http://localhost:5001
```

## Features

### ✨ Key Features

1. **Multi-Agent Architecture** - Specialized agents for each task
2. **Workflow Orchestration** - Coordinated processing pipeline
3. **Quality Control** - Automated validation at each step
4. **Real-time Monitoring** - Live performance tracking
5. **Report Generation** - Comprehensive diagnostic reports
6. **Error Handling** - Robust error management
7. **Performance Analytics** - System-wide metrics

### 📊 Monitoring

The monitoring dashboard provides:
- System overview (total workflows, success rate)
- Agent status and performance metrics
- Workflow performance charts
- Recent workflow history

### 📄 Report Export

Reports can be exported in multiple formats:
- JSON (machine-readable)
- HTML (human-readable)

```python
# Export as JSON
json_report = orchestrator.export_report("workflow_id", format="json")

# Export as HTML
html_report = orchestrator.export_report("workflow_id", format="html")
```

## Integration with Existing System

The multi-agent system can be integrated with your existing FastAPI backend:

```python
from workflow_orchestrator import WorkflowOrchestrator
import cv2
import numpy as np

# Initialize once (can be a global variable)
orchestrator = WorkflowOrchestrator("models/retina_model_final.h5")

# In your FastAPI endpoint
@app.post("/predict/ai-agent")
async def predict_with_agents(file: UploadFile = File(...)):
    contents = await file.read()
    
    # Convert to numpy array
    nparr = np.frombuffer(contents, np.uint8)
    image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    
    # Process with multi-agent system
    result = orchestrator.process_image(image, file.filename)
    
    return result["final_report"]
```

## Performance

### Metrics Tracked

- Tasks processed per agent
- Success rate per agent
- Average processing time per agent
- Overall system throughput
- Workflow completion rate

### Batch Processing

Process multiple images in parallel:

```python
images = [image1, image2, image3]
results = orchestrator.batch_process(images, parallel=True)
```

## Agent Responsibilities

| Agent | Responsibility |
|-------|---------------|
| Data Processor | Image preprocessing, quality assessment |
| Model Specialist | AI model inference, prediction |
| Diagnosis Analyst | Clinical context, recommendations |
| Quality Controller | Validation, quality assurance |
| Report Generator | Comprehensive report creation |

## Dependencies

All dependencies are listed in `requirements.txt`:
- tensorflow (for model inference)
- opencv-python-headless (for image processing)
- numpy (for array operations)
- flask (for monitoring dashboard - optional)

## Notes

- The system will create a mock model if the actual model file is not found
- All agents track their own performance metrics
- The workflow history is maintained for monitoring and debugging
- Quality thresholds can be adjusted in each agent class

## Example Output

```json
{
  "final_report": {
    "report_id": "RETINA_abc123",
    "patient_info": {
      "image_id": "demo_1",
      "processing_date": "2024-01-15 10:30:00"
    },
    "diagnostic_findings": {
      "primary_diagnosis": "Moderate Diabetic Retinopathy",
      "severity_level": 2,
      "confidence_level": "High",
      "confidence_score": 0.85
    },
    "clinical_assessment": {
      "urgency_level": "high",
      "risk_factors": ["Hemorrhages", "Cotton wool spots"],
      "quality_assessment": "85.0%"
    },
    "recommendations": {
      "immediate_actions": [
        "Urgent ophthalmologist consultation",
        "Consider laser treatment"
      ],
      "follow_up_timeline": "3-6 months"
    }
  }
}
```

## Troubleshooting

### Model Not Found
If the model file is missing, the system will automatically create a mock model for demonstration purposes.

### Image Quality Issues
If image quality is too low, the workflow will fail at the Data Processor stage. Adjust `quality_threshold` in `DataProcessorAgent` if needed.

### Dashboard Not Starting
Ensure Flask is installed: `pip install flask`

## Future Enhancements

- [ ] Agent communication via message queue (Redis/RabbitMQ)
- [ ] Distributed agent execution
- [ ] Advanced error recovery mechanisms
- [ ] Agent learning from feedback
- [ ] Integration with medical databases

