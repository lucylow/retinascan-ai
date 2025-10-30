from flask import Flask, render_template, jsonify, request, Response
import json
import threading
from datetime import datetime
from advanced_orchestrator import AdvancedWorkflowOrchestrator, HumanInterventionType
import numpy as np
import os


app = Flask(__name__)

# Global orchestrator instance
orchestrator = None


class HITLDashboard:
    """Human-in-the-loop dashboard for managing interventions"""

    def __init__(self, orchestrator: AdvancedWorkflowOrchestrator):
        self.orchestrator = orchestrator
        self.dashboard_data = {
            "workflows": [],
            "pending_interventions": [],
            "system_metrics": {},
            "recent_activity": [],
        }

    def update_dashboard_data(self):
        self.dashboard_data["workflows"] = self.orchestrator.get_all_workflows()
        self.dashboard_data["pending_interventions"] = self.orchestrator.get_pending_interventions()
        self.dashboard_data["system_metrics"] = self._calculate_system_metrics()
        if len(self.dashboard_data["recent_activity"]) > 50:
            self.dashboard_data["recent_activity"] = self.dashboard_data["recent_activity"][-50:]

    def _calculate_system_metrics(self):
        workflows = self.dashboard_data["workflows"]
        if not workflows:
            return {
                "total_workflows": 0,
                "completed": 0,
                "pending_human": 0,
                "failed": 0,
                "success_rate": 0,
                "avg_processing_time": 0,
                "human_intervention_rate": 0,
            }

        total = len(workflows)
        completed = len([w for w in workflows if w.get("state") == "completed"])  # value strings in orchestrator
        pending_human = len([w for w in workflows if w.get("state") == "awaiting_human_input"])  # noqa
        failed = len([w for w in workflows if w.get("state") == "failed"])  # noqa
        avg_processing_time = self._calculate_avg_processing_time(workflows)

        return {
            "total_workflows": total,
            "completed": completed,
            "pending_human": pending_human,
            "failed": failed,
            "success_rate": completed / total if total > 0 else 0,
            "avg_processing_time": avg_processing_time,
            "human_intervention_rate": pending_human / total if total > 0 else 0,
        }

    def _calculate_avg_processing_time(self, workflows):
        completed_times = []
        for wf in workflows:
            if wf.get("state") == "completed" and "created_at" in wf and "updated_at" in wf:
                created = wf["created_at"]
                updated = wf["updated_at"]
                if isinstance(created, str):
                    created = datetime.fromisoformat(created.replace("Z", "+00:00"))
                if isinstance(updated, str):
                    updated = datetime.fromisoformat(updated.replace("Z", "+00:00"))
                processing_time = (updated - created).total_seconds()
                completed_times.append(processing_time)
        return sum(completed_times) / len(completed_times) if completed_times else 0


@app.route("/")
def dashboard():
    return render_template("advanced_dashboard.html")


@app.route("/api/dashboard-data")
def get_dashboard_data():
    dashboard.update_dashboard_data()
    # Convert dataclass objects if present in interventions
    interventions = dashboard.dashboard_data["pending_interventions"]
    interventions_json = [
        {
            "id": i.id,
            "workflow_id": i.workflow_id,
            "type": i.intervention_type.value,
            "priority": i.priority,
            "timestamp": i.timestamp.isoformat(),
            "required_actions": i.required_actions,
            "context": i.context,
        }
        for i in interventions
    ]
    data = dict(dashboard.dashboard_data)
    data["pending_interventions"] = interventions_json
    return jsonify(data)


@app.route("/api/workflow/<workflow_id>")
def get_workflow_details(workflow_id):
    workflow = orchestrator.get_workflow_status(workflow_id)
    if workflow:
        # Ensure datetimes are JSON serializable
        def dt_to_str(v):
            return v.isoformat() if isinstance(v, datetime) else v

        serializable = {k: dt_to_str(v) for k, v in workflow.items()}
        return jsonify(serializable)
    return jsonify({"error": "Workflow not found"}), 404


@app.route("/api/interventions/pending")
def get_pending_interventions():
    interventions = orchestrator.get_pending_interventions()
    return jsonify(
        [
            {
                "id": i.id,
                "workflow_id": i.workflow_id,
                "type": i.intervention_type.value,
                "priority": i.priority,
                "timestamp": i.timestamp.isoformat(),
                "required_actions": i.required_actions,
                "context": i.context,
            }
            for i in interventions
        ]
    )


@app.route("/api/interventions/respond", methods=["POST"])
def submit_intervention_response():
    data = request.json or {}
    required_fields = ["request_id", "approved", "reviewer"]
    if not all(field in data for field in required_fields):
        return jsonify({"error": "Missing required fields"}), 400
    try:
        orchestrator.submit_human_response(
            request_id=data["request_id"],
            approved=bool(data["approved"]),
            comments=data.get("comments", ""),
            overrides=data.get("overrides", {}),
            reviewer=data["reviewer"],
        )
        dashboard.dashboard_data["recent_activity"].insert(
            0,
            {
                "timestamp": datetime.now().isoformat(),
                "type": "human_response",
                "message": f"{data['reviewer']} {'approved' if data['approved'] else 'rejected'} intervention {data['request_id']}",
                "workflow_id": data.get("workflow_id", "unknown"),
            },
        )
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/workflow/submit", methods=["POST"])
def submit_new_workflow():
    try:
        mock_image = np.random.rand(512, 512, 3) * 255
        payload = request.json or {}
        metadata = {
            "source": "web_dashboard",
            "submitted_by": payload.get("submitted_by", "anonymous"),
            "priority": payload.get("priority", 1),
        }
        workflow_id = orchestrator.submit_workflow(image_data=mock_image, metadata=metadata)
        dashboard.dashboard_data["recent_activity"].insert(
            0,
            {
                "timestamp": datetime.now().isoformat(),
                "type": "workflow_submitted",
                "message": f"New workflow submitted: {workflow_id}",
                "workflow_id": workflow_id,
            },
        )
        return jsonify({"workflow_id": workflow_id, "success": True})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/system/override", methods=["POST"])
def system_override():
    data = request.json or {}
    action = data.get("action")
    # Placeholder for system controls
    return jsonify({"success": True, "action": action})


@app.route("/api/events")
def event_stream():
    def generate_events():
        while True:
            dashboard.update_dashboard_data()
            data = {
                "workflows_count": len(dashboard.dashboard_data["workflows"]),
                "pending_interventions": len(dashboard.dashboard_data["pending_interventions"]),
                "system_metrics": dashboard.dashboard_data["system_metrics"],
                "timestamp": datetime.now().isoformat(),
            }
            yield f"data: {json.dumps(data)}\n\n"
            threading.Event().wait(2)

    return Response(generate_events(), mimetype="text/event-stream")


def init_dashboard(orch_instance, host="0.0.0.0", port=5002):
    global orchestrator, dashboard
    orchestrator = orch_instance
    dashboard = HITLDashboard(orchestrator)
    _ensure_template_written()
    print(f"🚀 Starting Advanced HITL Dashboard on http://{host}:{port}")
    app.run(host=host, port=port, debug=False, use_reloader=False)


ADVANCED_DASHBOARD_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>RetinaScan AI - Human-in-the-Loop Dashboard</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        :root {
            --primary: #007acc;
            --secondary: #6c757d;
            --success: #28a745;
            --warning: #ffc107;
            --danger: #dc3545;
            --dark: #343a40;
        }
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 0; padding: 20px; background: #f8f9fa; }
        .dashboard-header { background: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); margin-bottom: 20px; }
        .metrics-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; margin-bottom: 20px; }
        .metric-card { background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); text-align: center; }
        .metric-value { font-size: 24px; font-weight: bold; margin: 10px 0; }
        .intervention-panel { background: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); margin-bottom: 20px; }
        .intervention-item { border: 1px solid #e9ecef; border-radius: 8px; padding: 15px; margin: 10px 0; background: #f8f9fa; }
        .intervention-priority { display: inline-block; padding: 4px 8px; border-radius: 4px; color: white; font-size: 12px; font-weight: bold; }
        .priority-high { background: var(--danger); }
        .priority-medium { background: var(--warning); color: var(--dark); }
        .priority-low { background: var(--success); }
        .action-buttons { margin-top: 10px; }
        .btn { padding: 8px 16px; border: none; border-radius: 4px; cursor: pointer; margin-right: 8px; }
        .btn-approve { background: var(--success); color: white; }
        .btn-reject { background: var(--danger); color: white; }
        .btn-details { background: var(--secondary); color: white; }
        .workflow-list { max-height: 400px; overflow-y: auto; }
        .workflow-item { border-left: 4px solid var(--primary); padding: 10px; margin: 5px 0; background: white; border-radius: 0 4px 4px 0; }
        .status-badge { padding: 4px 8px; border-radius: 4px; font-size: 12px; font-weight: bold; }
        .status-running { background: #d4edda; color: #155724; }
        .status-pending { background: #fff3cd; color: #856404; }
        .status-completed { background: #d1ecf1; color: #0c5460; }
        .status-failed { background: #f8d7da; color: #721c24; }
    </style>
    </head>
<body>
    <div class="dashboard-header">
        <h1>🩺 RetinaScan AI - Human-in-the-Loop Dashboard</h1>
        <p>Real-time monitoring and intervention management</p>
    </div>

    <div class="metrics-grid" id="metrics-grid"></div>

    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px;">
        <div class="intervention-panel">
            <h3>🔄 Pending Human Interventions</h3>
            <div id="pending-interventions"><p>Loading interventions...</p></div>
        </div>
        <div class="intervention-panel">
            <h3>📋 Recent Workflows</h3>
            <div class="workflow-list" id="workflow-list"><p>Loading workflows...</p></div>
        </div>
    </div>

    <div class="intervention-panel">
        <h3>📊 System Activity</h3>
        <div id="recent-activity"><p>Loading activity...</p></div>
    </div>

    <script>
        let currentData = {};
        const eventSource = new EventSource('/api/events');
        eventSource.onmessage = function(event) {
            const data = JSON.parse(event.data);
            currentData = data;
            updateDashboard(data);
        };

        function updateDashboard(data) {
            updateMetrics(data.system_metrics || {});
            fetch('/api/interventions/pending').then(r => r.json()).then(updateInterventions);
        }

        function updateMetrics(metrics) {
            const metricsGrid = document.getElementById('metrics-grid');
            if (!metrics.total_workflows) {
                metricsGrid.innerHTML = '<p>No data available</p>';
                return;
            }
            metricsGrid.innerHTML = `
                <div class="metric-card">
                    <div>Total Workflows</div>
                    <div class="metric-value">${metrics.total_workflows}</div>
                    <div>All Time</div>
                </div>
                <div class="metric-card">
                    <div>Success Rate</div>
                    <div class="metric-value" style="color: ${metrics.success_rate > 0.8 ? 'var(--success)' : 'var(--warning)'}">${(metrics.success_rate * 100).toFixed(1)}%</div>
                    <div>Completion Rate</div>
                </div>
                <div class="metric-card">
                    <div>Pending Human Review</div>
                    <div class="metric-value" style="color: ${metrics.pending_human > 0 ? 'var(--warning)' : 'var(--success)'}">${metrics.pending_human}</div>
                    <div>Awaiting Input</div>
                </div>
                <div class="metric-card">
                    <div>Avg Processing Time</div>
                    <div class="metric-value">${(metrics.avg_processing_time || 0).toFixed(1)}s</div>
                    <div>Per Workflow</div>
                </div>`;
        }

        function updateInterventions(interventions) {
            const container = document.getElementById('pending-interventions');
            if (!interventions || interventions.length === 0) {
                container.innerHTML = '<p>No pending interventions</p>';
                return;
            }
            container.innerHTML = interventions.map(intervention => `
                <div class="intervention-item">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <div>
                            <strong>${intervention.type.toUpperCase()}</strong>
                            <span class="intervention-priority ${getPriorityClass(intervention.priority)}">Priority ${intervention.priority}</span>
                        </div>
                        <div style="font-size: 12px; color: #666;">${new Date(intervention.timestamp).toLocaleTimeString()}</div>
                    </div>
                    <div style="margin: 8px 0;"><strong>Workflow:</strong> ${intervention.workflow_id}</div>
                    <div style="margin: 8px 0;"><strong>Required Actions:</strong> ${intervention.required_actions.join(', ')}</div>
                    <div class="action-buttons">
                        <button class="btn btn-approve" onclick="respondToIntervention('${intervention.id}', true)">✅ Approve</button>
                        <button class="btn btn-reject" onclick="respondToIntervention('${intervention.id}', false)">❌ Reject</button>
                    </div>
                </div>`).join('');
        }

        function getPriorityClass(priority) {
            if (priority >= 3) return 'priority-high';
            if (priority >= 2) return 'priority-medium';
            return 'priority-low';
        }

        function respondToIntervention(requestId, approved) {
            const reviewer = prompt('Enter your name/reviewer ID:');
            if (!reviewer) return;
            const comments = approved ? 'Approved via dashboard' : 'Rejected via dashboard - requires modification';
            fetch('/api/interventions/respond', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ request_id: requestId, approved: approved, comments: comments, reviewer: reviewer })
            }).then(r => r.json()).then(data => {
                if (data.success) {
                    alert('Response submitted successfully!');
                } else {
                    alert('Error: ' + data.error);
                }
            });
        }

        fetch('/api/dashboard-data').then(r => r.json()).then(data => { currentData = data; updateDashboard(data); });
    </script>
</body>
</html>
"""


def _ensure_template_written():
    os.makedirs("templates", exist_ok=True)
    with open(os.path.join("templates", "advanced_dashboard.html"), "w") as f:
        f.write(ADVANCED_DASHBOARD_HTML)


if __name__ == "__main__":
    orch = AdvancedWorkflowOrchestrator("models/retina_model_final.h5")
    init_dashboard(orch, host="0.0.0.0", port=5002)


