# Multi-Agent AI Dashboard - Backend API Integration

## Overview

The frontend dashboard expects the following API endpoints to be available. Add these to your FastAPI backend (`main.py`) to enable full functionality.

## Required Endpoints

### 1. Health Check
```python
@app.get("/ai-agent/health")
async def ai_agent_health():
    """Health check for AI agent system"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat()
    }
```

### 2. Process Image (Multi-Agent Workflow)
```python
from workflow_orchestrator import WorkflowOrchestrator
import cv2
import numpy as np

# Initialize orchestrator (can be a global variable)
ai_orchestrator = WorkflowOrchestrator("models/retina_model_final.h5")

@app.post("/ai-agent/process")
async def process_image_ai_agents(
    file: UploadFile = File(...),
    workflow_id: str = None
):
    """
    Process image through multi-agent AI workflow
    """
    contents = await file.read()
    
    # Convert to numpy array
    nparr = np.frombuffer(contents, np.uint8)
    image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    
    if image is None:
        raise HTTPException(status_code=400, detail="Invalid image")
    
    # Process with multi-agent system
    workflow_id = workflow_id or f"web_{int(time.time())}"
    result = await run_in_threadpool(
        ai_orchestrator.process_image,
        image,
        workflow_id
    )
    
    return result
```

### 3. Get System Metrics
```python
@app.get("/ai-agent/metrics")
async def get_ai_agent_metrics():
    """Get system metrics for AI agents"""
    metrics = ai_orchestrator.get_system_metrics()
    return metrics
```

### 4. Get Agent Statuses
```python
@app.get("/ai-agent/agents")
async def get_agent_statuses():
    """Get status of all AI agents"""
    agents = []
    for role, agent in ai_orchestrator.agents.items():
        agents.append({
            "role": role.value,
            "agentId": agent.agent_id,
            "performance": {
                "tasksProcessed": agent.performance_metrics["tasks_processed"],
                "successRate": agent.performance_metrics["success_rate"],
                "avgProcessingTime": agent.performance_metrics["average_processing_time"]
            },
            "status": "online",  # Can be enhanced with actual status tracking
            "currentTask": None  # Can be enhanced to track current tasks
        })
    return agents
```

### 5. Get Workflow Status
```python
@app.get("/ai-agent/workflow/{workflow_id}")
async def get_workflow_status(workflow_id: str):
    """Get status of a specific workflow"""
    workflow_data = ai_orchestrator.get_workflow_status(workflow_id)
    
    if workflow_data.get("status") == "not_found":
        raise HTTPException(status_code=404, detail="Workflow not found")
    
    # Format response for frontend
    return {
        "id": workflow_data.get("workflow_id"),
        "status": workflow_data.get("status"),
        "progress": calculate_workflow_progress(workflow_data),
        "currentStep": get_current_step(workflow_data),
        "startTime": workflow_data.get("start_time"),
        "endTime": workflow_data.get("end_time"),
        "result": workflow_data.get("result"),
        "error": workflow_data.get("error")
    }

def calculate_workflow_progress(workflow_data):
    """Calculate progress percentage"""
    status = workflow_data.get("status", "started")
    if status == "completed":
        return 100
    elif status == "failed":
        return 0
    elif status == "running":
        # Estimate based on workflow stage
        return 50
    return 0

def get_current_step(workflow_data):
    """Get current workflow step"""
    status = workflow_data.get("status", "started")
    step_map = {
        "started": "Data Processing",
        "running": "AI Analysis",
        "completed": "Report Generation",
        "failed": "Error"
    }
    return step_map.get(status, "Unknown")
```

### 6. Get Recent Workflows
```python
@app.get("/ai-agent/workflows")
async def get_recent_workflows(limit: int = 50):
    """Get recent workflows"""
    workflows = ai_orchestrator.workflow_history[-limit:]
    
    formatted_workflows = []
    for wf in workflows:
        formatted_workflows.append({
            "id": wf.get("workflow_id"),
            "status": wf.get("status"),
            "progress": calculate_workflow_progress(wf),
            "currentStep": get_current_step(wf),
            "startTime": wf.get("start_time"),
            "endTime": wf.get("end_time"),
            "result": wf.get("result"),
            "error": wf.get("error")
        })
    
    return formatted_workflows
```

## Complete Integration Example

Add this to your `main.py`:

```python
from workflow_orchestrator import WorkflowOrchestrator
import cv2
import numpy as np
import time
from datetime import datetime
from fastapi import HTTPException, UploadFile, File
from fastapi.concurrency import run_in_threadpool

# Initialize AI orchestrator (can be a module-level variable)
ai_orchestrator = WorkflowOrchestrator("models/retina_model_final.h5")

@app.get("/ai-agent/health")
async def ai_agent_health():
    """Health check for AI agent system"""
    try:
        # Quick check if orchestrator is initialized
        metrics = ai_orchestrator.get_system_metrics()
        return {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "agents_initialized": len(ai_orchestrator.agents)
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }

@app.post("/ai-agent/process")
async def process_image_ai_agents(
    file: UploadFile = File(...),
    workflow_id: str = None
):
    """Process image through multi-agent AI workflow"""
    contents = await file.read()
    
    # Convert to numpy array
    nparr = np.frombuffer(contents, np.uint8)
    image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    
    if image is None:
        raise HTTPException(status_code=400, detail="Invalid image format")
    
    # Process with multi-agent system
    workflow_id = workflow_id or f"web_{int(time.time())}"
    
    try:
        result = await run_in_threadpool(
            ai_orchestrator.process_image,
            image,
            workflow_id
        )
        return result
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Processing failed: {str(e)}"
        )

@app.get("/ai-agent/metrics")
async def get_ai_agent_metrics():
    """Get system metrics for AI agents"""
    return ai_orchestrator.get_system_metrics()

@app.get("/ai-agent/agents")
async def get_agent_statuses():
    """Get status of all AI agents"""
    agents = []
    for role, agent in ai_orchestrator.agents.items():
        agents.append({
            "role": role.value,
            "agentId": agent.agent_id,
            "performance": {
                "tasksProcessed": agent.performance_metrics.get("tasks_processed", 0),
                "successRate": agent.performance_metrics.get("success_rate", 0.0),
                "avgProcessingTime": agent.performance_metrics.get("average_processing_time", 0.0)
            },
            "status": "online",
            "currentTask": None
        })
    return agents

@app.get("/ai-agent/workflow/{workflow_id}")
async def get_workflow_status(workflow_id: str):
    """Get status of a specific workflow"""
    workflow_data = ai_orchestrator.get_workflow_status(workflow_id)
    
    if workflow_data.get("status") == "not_found":
        raise HTTPException(status_code=404, detail="Workflow not found")
    
    # Calculate progress and step
    status = workflow_data.get("status", "started")
    progress = 100 if status == "completed" else (0 if status == "failed" else 50)
    
    step_map = {
        "started": "Data Processing",
        "running": "AI Analysis",
        "completed": "Report Generation",
        "failed": "Error"
    }
    current_step = step_map.get(status, "Unknown")
    
    return {
        "id": workflow_data.get("workflow_id"),
        "status": status,
        "progress": progress,
        "currentStep": current_step,
        "startTime": workflow_data.get("start_time"),
        "endTime": workflow_data.get("end_time"),
        "result": workflow_data.get("result"),
        "error": workflow_data.get("error")
    }

@app.get("/ai-agent/workflows")
async def get_recent_workflows(limit: int = 50):
    """Get recent workflows"""
    workflows = ai_orchestrator.workflow_history[-limit:]
    
    formatted_workflows = []
    for wf in workflows:
        status = wf.get("status", "started")
        progress = 100 if status == "completed" else (0 if status == "failed" else 50)
        
        step_map = {
            "started": "Data Processing",
            "running": "AI Analysis",
            "completed": "Report Generation",
            "failed": "Error"
        }
        current_step = step_map.get(status, "Unknown")
        
        formatted_workflows.append({
            "id": wf.get("workflow_id"),
            "status": status,
            "progress": progress,
            "currentStep": current_step,
            "startTime": wf.get("start_time"),
            "endTime": wf.get("end_time"),
            "result": wf.get("result"),
            "error": wf.get("error")
        })
    
    return formatted_workflows
```

## Environment Variables

Add to your `.env` file or environment:

```bash
# Frontend needs this to connect to backend
VITE_API_BASE_URL=http://localhost:8000
```

Or in production:
```bash
VITE_API_BASE_URL=https://your-api-domain.com
```

## CORS Configuration

Ensure CORS is enabled in your FastAPI app:

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],  # Add your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## Testing

Test the endpoints:

```bash
# Health check
curl http://localhost:8000/ai-agent/health

# Get metrics
curl http://localhost:8000/ai-agent/metrics

# Get agents
curl http://localhost:8000/ai-agent/agents

# Get workflows
curl http://localhost:8000/ai-agent/workflows
```

## Frontend Integration

The frontend is already configured to use these endpoints. Just ensure:

1. Backend is running on the port specified in `VITE_API_BASE_URL`
2. CORS is properly configured
3. All endpoints are implemented as shown above

Access the dashboard at: `http://localhost:5173/ai-agents` (or your frontend URL)

