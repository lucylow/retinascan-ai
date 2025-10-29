"""
RetinaScan AI - Real-time Monitoring Dashboard
Flask-based dashboard for monitoring the AI workflow system
"""
from flask import Flask, render_template, jsonify, request
import threading
import time
from datetime import datetime
import json
import os

app = Flask(__name__)

class RealTimeMonitor:
    """Real-time monitoring for the AI workflow system"""
    
    def __init__(self, orchestrator):
        self.orchestrator = orchestrator
        self.active_connections = set()
        self.metrics_history = []
    
    def get_live_metrics(self):
        """Get live system metrics"""
        return {
            "timestamp": datetime.now().isoformat(),
            "active_workflows": len(self.orchestrator.active_workflows),
            "system_metrics": self.orchestrator.get_system_metrics(),
            "agent_status": {
                role.value: agent.performance_metrics 
                for role, agent in self.orchestrator.agents.items()
            }
        }

monitor = None

@app.route('/')
def dashboard():
    """Main dashboard page"""
    return render_template('dashboard.html')

@app.route('/api/metrics')
def get_metrics():
    """API endpoint for system metrics"""
    if monitor:
        return jsonify(monitor.get_live_metrics())
    return jsonify({"error": "Monitor not initialized"})

@app.route('/api/workflows')
def get_workflows():
    """API endpoint for workflow history"""
    if monitor:
        return jsonify({
            "workflows": monitor.orchestrator.workflow_history[-50:]  # Last 50 workflows
        })
    return jsonify({"error": "Monitor not initialized"})

@app.route('/api/process', methods=['POST'])
def process_image():
    """API endpoint to process new image"""
    try:
        # In practice, you'd get the image from the request
        image_data = request.files.get('image')
        workflow_id = f"web_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        if not image_data:
            return jsonify({
                "success": False,
                "error": "No image provided"
            }), 400
        
        # For now, return a placeholder response
        # In production, you'd convert the image and process it
        return jsonify({
            "success": True,
            "workflow_id": workflow_id,
            "message": "Image processing endpoint - implement actual image processing here"
        })
    
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

def start_monitoring(orchestrator, host='0.0.0.0', port=5001):
    """Start the monitoring dashboard"""
    global monitor
    monitor = RealTimeMonitor(orchestrator)
    
    # Ensure templates are set up
    setup_templates()
    
    print(f"📊 Starting monitoring dashboard on http://{host}:{port}")
    app.run(host=host, port=port, debug=False)


# HTML Template for dashboard
DASHBOARD_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>RetinaScan AI Monitoring Dashboard</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        body { 
            font-family: Arial, sans-serif; 
            margin: 0; 
            padding: 20px; 
            background: #f5f5f5; 
        }
        .dashboard { 
            display: grid; 
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); 
            gap: 20px; 
        }
        .card { 
            background: white; 
            padding: 20px; 
            border-radius: 10px; 
            box-shadow: 0 2px 10px rgba(0,0,0,0.1); 
        }
        .metric { 
            font-size: 24px; 
            font-weight: bold; 
            color: #007acc; 
        }
        .agent-status { 
            display: flex; 
            justify-content: space-between; 
            margin: 10px 0; 
            padding: 8px;
            background: #f9f9f9;
            border-radius: 5px;
        }
        .status-online { color: green; }
        .status-offline { color: red; }
        h1 {
            color: #333;
            margin-bottom: 30px;
        }
        h3 {
            color: #555;
            margin-top: 0;
        }
    </style>
</head>
<body>
    <h1>🩺 RetinaScan AI - Live Monitoring Dashboard</h1>
    
    <div class="dashboard">
        <div class="card">
            <h3>System Overview</h3>
            <div id="system-metrics">Loading...</div>
        </div>
        
        <div class="card">
            <h3>Agent Status</h3>
            <div id="agent-status">Loading...</div>
        </div>
        
        <div class="card">
            <h3>Workflow Performance</h3>
            <canvas id="performance-chart" width="400" height="200"></canvas>
        </div>
        
        <div class="card">
            <h3>Recent Workflows</h3>
            <div id="recent-workflows">Loading...</div>
        </div>
    </div>

    <script>
        // Update metrics every 3 seconds
        setInterval(updateDashboard, 3000);
        
        let performanceChart = null;
        
        async function updateDashboard() {
            try {
                const response = await fetch('/api/metrics');
                const data = await response.json();
                
                if (data.error) {
                    document.getElementById('system-metrics').innerHTML = '<p>Error: ' + data.error + '</p>';
                    return;
                }
                
                const metrics = data.system_metrics;
                const total = metrics.total_workflows || 1;
                const success = metrics.successful_workflows || 0;
                const successRate = total > 0 ? (success / total * 100).toFixed(1) : 0;
                
                // Update system metrics
                document.getElementById('system-metrics').innerHTML = `
                    <div>Total Workflows: <span class="metric">${total}</span></div>
                    <div>Success Rate: <span class="metric">${successRate}%</span></div>
                    <div>Active Workflows: <span class="metric">${data.active_workflows || 0}</span></div>
                    <div>Failed Workflows: <span class="metric">${metrics.failed_workflows || 0}</span></div>
                `;
                
                // Update agent status
                let agentHtml = '';
                if (data.agent_status) {
                    for (const [agent, metrics] of Object.entries(data.agent_status)) {
                        const agentName = agent.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase());
                        agentHtml += `
                            <div class="agent-status">
                                <span>${agentName}:</span>
                                <span class="status-online">${metrics.tasks_processed || 0} tasks</span>
                            </div>
                        `;
                    }
                }
                document.getElementById('agent-status').innerHTML = agentHtml || '<p>No agent data available</p>';
                
                // Update performance chart
                updatePerformanceChart(metrics);
                
            } catch (error) {
                console.error('Error updating dashboard:', error);
                document.getElementById('system-metrics').innerHTML = '<p>Error loading metrics</p>';
            }
        }
        
        async function updateRecentWorkflows() {
            try {
                const response = await fetch('/api/workflows');
                const data = await response.json();
                
                if (data.workflows) {
                    const recent = data.workflows.slice(-10).reverse();
                    let html = '<ul style="list-style: none; padding: 0;">';
                    recent.forEach(wf => {
                        const status = wf.status || 'unknown';
                        const statusIcon = status === 'completed' ? '✅' : status === 'failed' ? '❌' : '⏳';
                        html += `<li style="padding: 5px 0;">${statusIcon} ${wf.workflow_id || 'Unknown'} - ${status}</li>`;
                    });
                    html += '</ul>';
                    document.getElementById('recent-workflows').innerHTML = html;
                }
            } catch (error) {
                console.error('Error updating workflows:', error);
            }
        }
        
        function updatePerformanceChart(metrics) {
            const ctx = document.getElementById('performance-chart');
            if (!ctx) return;
            
            if (!performanceChart) {
                performanceChart = new Chart(ctx, {
                    type: 'bar',
                    data: {
                        labels: ['Total', 'Successful', 'Failed'],
                        datasets: [{
                            label: 'Workflows',
                            data: [
                                metrics.total_workflows || 0,
                                metrics.successful_workflows || 0,
                                metrics.failed_workflows || 0
                            ],
                            backgroundColor: ['#007acc', '#28a745', '#dc3545']
                        }]
                    },
                    options: {
                        responsive: true,
                        scales: {
                            y: {
                                beginAtZero: true
                            }
                        }
                    }
                });
            } else {
                performanceChart.data.datasets[0].data = [
                    metrics.total_workflows || 0,
                    metrics.successful_workflows || 0,
                    metrics.failed_workflows || 0
                ];
                performanceChart.update();
            }
        }
        
        // Initial load
        updateDashboard();
        setInterval(updateRecentWorkflows, 5000);
        updateRecentWorkflows();
    </script>
</body>
</html>
"""

# Ensure templates directory exists and save HTML
def setup_templates():
    """Setup templates directory with dashboard HTML"""
    templates_dir = os.path.join(os.path.dirname(__file__), 'templates')
    os.makedirs(templates_dir, exist_ok=True)
    
    dashboard_path = os.path.join(templates_dir, 'dashboard.html')
    with open(dashboard_path, 'w') as f:
        f.write(DASHBOARD_HTML)
    
    print(f"📁 Dashboard template saved to {dashboard_path}")

if __name__ == "__main__":
    setup_templates()
    print("✅ Dashboard template setup complete")

