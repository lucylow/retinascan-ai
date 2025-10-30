from flask import Flask, render_template, jsonify, request
import threading
import time
from datetime import datetime
import json

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
            },
        }


monitor = None


@app.route("/")
def dashboard():
    """Main dashboard page"""
    return render_template("dashboard.html")


@app.route("/api/metrics")
def get_metrics():
    """API endpoint for system metrics"""
    if monitor:
        return jsonify(monitor.get_live_metrics())
    return jsonify({"error": "Monitor not initialized"})


@app.route("/api/workflows")
def get_workflows():
    """API endpoint for workflow history"""
    if monitor:
        return jsonify({"workflows": monitor.orchestrator.workflow_history[-50:]})
    return jsonify({"error": "Monitor not initialized"})


@app.route("/api/process", methods=["POST"])
def process_image():
    """API endpoint to process new image"""
    try:
        # In practice, you'd get the image from the request
        image_data = request.files.get("image")
        workflow_id = f"web_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        # Process image (you'd need to convert the image data)
        result = monitor.orchestrator.process_image(None, workflow_id)

        return jsonify({"success": True, "workflow_id": workflow_id, "result": result})

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


def start_monitoring(orchestrator, host="0.0.0.0", port=5001):
    """Start the monitoring dashboard"""
    global monitor
    monitor = RealTimeMonitor(orchestrator)

    print(f"📊 Starting monitoring dashboard on http://{host}:{port}")
    app.run(host=host, port=port, debug=False)


# ---- Clinics API (simple in-memory directory with geo filtering) ----
# Example starter data; replace with DB/registry integration later
CLINICS = [
    {
        "id": "c1",
        "name": "City Eye Clinic",
        "address": "123 Vision St",
        "phone": "+1 555-123-4567",
        "latitude": 37.7749,
        "longitude": -122.4194,
        "hours": "Mon-Fri 8:00-17:00",
        "insuranceAccepted": ["Aetna", "BCBS"],
        "languagesSpoken": ["English", "Spanish"],
        "bookingUrl": "https://example.com/book/c1",
    },
    {
        "id": "c2",
        "name": "Retina Specialists Center",
        "address": "456 Macula Ave",
        "phone": "+1 555-222-3344",
        "latitude": 37.7849,
        "longitude": -122.4094,
        "hours": "Mon-Sat 9:00-18:00",
        "insuranceAccepted": ["Kaiser", "United"],
        "languagesSpoken": ["English", "Chinese"],
        "bookingUrl": "https://example.com/book/c2",
    },
]

from math import radians, sin, cos, asin, sqrt


def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculate the great circle distance between two points in km"""
    R = 6371.0
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat / 2) ** 2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon / 2) ** 2
    c = 2 * asin(sqrt(a))
    return R * c


@app.route("/api/clinics")
def list_clinics():
    try:
        lat = request.args.get("lat", type=float)
        lng = request.args.get("lng", type=float)
        radius = request.args.get("radius", default=50.0, type=float)  # km
        insurance = request.args.get("insurance")
        language = request.args.get("language")

        results = []
        for c in CLINICS:
            if insurance and insurance not in c.get("insuranceAccepted", []):
                continue
            if language and language not in c.get("languagesSpoken", []):
                continue

            distance = None
            if lat is not None and lng is not None:
                distance = haversine_km(lat, lng, c["latitude"], c["longitude"])
                if distance > radius:
                    continue
            results.append({**c, "distance_km": round(distance, 2) if distance is not None else None})

        # Sort by distance if available
        results.sort(key=lambda x: x["distance_km"] if x["distance_km"] is not None else 1e9)
        return jsonify({"clinics": results})
    except Exception as e:
        return jsonify({"error": str(e)}), 400


# HTML Template (dashboard.html)
DASHBOARD_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>RetinaScan AI Monitoring Dashboard</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        body { font-family: Arial, sans-serif; margin: 0; padding: 20px; background: #f5f5f5; }
        .dashboard { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; }
        .card { background: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        .metric { font-size: 24px; font-weight: bold; color: #007acc; }
        .agent-status { display: flex; justify-content: space-between; margin: 10px 0; }
        .status-online { color: green; }
        .status-offline { color: red; }
    </style>
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <meta charset="UTF-8" />
    <link rel="icon" href="data:," />
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

        async function updateDashboard() {
            try {
                const response = await fetch('/api/metrics');
                const data = await response.json();

                // Update system metrics
                const total = data.system_metrics.total_workflows || 0;
                const succ = data.system_metrics.successful_workflows || 0;
                const rate = total ? (succ / total * 100).toFixed(1) : '0.0';
                document.getElementById('system-metrics').innerHTML = `
                    <div>Total Workflows: <span class="metric">${total}</span></div>
                    <div>Success Rate: <span class="metric">${rate}%</span></div>
                    <div>Active Workflows: <span class="metric">${data.active_workflows}</span></div>
                `;

                // Update agent status
                let agentHtml = '';
                for (const [agent, metrics] of Object.entries(data.agent_status)) {
                    agentHtml += `
                        <div class="agent-status">
                            <span>${agent}:</span>
                            <span class="status-online">${metrics.tasks_processed} tasks</span>
                        </div>
                    `;
                }
                document.getElementById('agent-status').innerHTML = agentHtml;

            } catch (error) {
                console.error('Error updating dashboard:', error);
            }
        }

        // Initial load
        updateDashboard();
    </script>
</body>
</html>
"""

# Save the HTML template
with open("templates/dashboard.html", "w") as f:
    f.write(DASHBOARD_HTML)


