"""
Demo script showing Human-in-the-Loop scenarios for RetinaScan AI
"""

import numpy as np
import time
from datetime import datetime
from advanced_orchestrator import AdvancedWorkflowOrchestrator


def run_demo_scenarios():
    print("🚀 RetinaScan AI - Human-in-the-Loop Demo")
    print("=" * 60)

    orchestrator = AdvancedWorkflowOrchestrator("models/retina_model_final.h5")

    print("\n📋 Scenario 1: Normal Case")
    print("-" * 30)
    normal_image = create_mock_image(quality=0.9)
    workflow_id = orchestrator.submit_workflow(
        normal_image, "normal_case_001", metadata={"patient_age": 45, "diabetes_years": 5}
    )
    wait_for_completion(orchestrator, workflow_id)

    print("\n📋 Scenario 2: Low Quality Image")
    print("-" * 30)
    low_quality_image = create_mock_image(quality=0.3)
    workflow_id = orchestrator.submit_workflow(
        low_quality_image,
        "low_quality_001",
        metadata={"patient_age": 65, "diabetes_years": 15},
    )
    time.sleep(3)
    show_pending_interventions(orchestrator)
    interventions = orchestrator.get_pending_interventions()
    if interventions:
        intervention = interventions[0]
        print(f"\n✅ Manually approving quality intervention...")
        orchestrator.submit_human_response(
            intervention.id,
            approved=True,
            comments="Image quality acceptable for emergency screening",
            reviewer="demo_doctor",
        )
    wait_for_completion(orchestrator, workflow_id)

    print("\n📋 Scenario 3: High Severity Case")
    print("-" * 30)
    emergency_image = create_mock_image(quality=0.8)
    workflow_id = orchestrator.submit_workflow(
        emergency_image,
        "emergency_case_001",
        metadata={"patient_age": 72, "diabetes_years": 25, "emergency_contact": "provided"},
    )
    time.sleep(5)
    show_workflow_status(orchestrator, workflow_id)

    print("\n📋 Scenario 4: Uncertain Diagnosis")
    print("-" * 30)
    uncertain_image = create_mock_image(quality=0.7)
    workflow_id = orchestrator.submit_workflow(
        uncertain_image, "uncertain_case_001", metadata={"patient_age": 38, "diabetes_years": 2}
    )
    time.sleep(3)
    show_pending_interventions(orchestrator)

    print("\n📊 System Performance Metrics")
    print("-" * 30)
    show_system_metrics(orchestrator)

    print("\n🔄 Waiting for all workflows to complete...")
    time.sleep(10)

    print("\n🎯 Demo Complete - Final Status")
    print("=" * 60)
    show_system_metrics(orchestrator)

    orchestrator.stop()


def create_mock_image(quality=0.8):
    return np.random.rand(512, 512, 3) * 255


def wait_for_completion(orchestrator, workflow_id, timeout=30):
    start_time = time.time()
    while time.time() - start_time < timeout:
        workflow = orchestrator.get_workflow_status(workflow_id)
        if workflow:
            state = workflow.get("state")
            if state in ["completed", "failed"]:
                print(f"   Workflow {workflow_id}: {state}")
                return workflow
            elif state == "awaiting_human_input":
                print(f"   Workflow {workflow_id}: Awaiting human input")
                return workflow
        time.sleep(1)
    print(f"   Workflow {workflow_id}: Timeout")
    return None


def show_pending_interventions(orchestrator):
    interventions = orchestrator.get_pending_interventions()
    if interventions:
        print(f"\n🔄 Pending Human Interventions: {len(interventions)}")
        for i, intervention in enumerate(interventions, 1):
            print(
                f"   {i}. {intervention.intervention_type.value} - Priority {intervention.priority}"
            )
            print(f"      Workflow: {intervention.workflow_id}")
            print(f"      Required: {', '.join(intervention.required_actions)}")
    else:
        print("\n✅ No pending human interventions")


def show_workflow_status(orchestrator, workflow_id):
    workflow = orchestrator.get_workflow_status(workflow_id)
    if workflow:
        print(f"\n📋 Workflow: {workflow_id}")
        print(f"   State: {workflow.get('state')}")
        print(f"   Current Step: {workflow.get('current_step')}")
        print(f"   Human Interventions: {len(workflow.get('human_interventions', []))}")
        if workflow.get("results"):
            if "emergency_report" in workflow["results"]:
                report = workflow["results"]["emergency_report"]
                print(f"   🚨 EMERGENCY: {report.get('diagnosis')}")
            elif "final_report" in workflow["results"]:
                report = workflow["results"]["final_report"]
                diagnosis = report.get("diagnostic_findings", {})
                print(
                    f"   Diagnosis: {diagnosis.get('primary_diagnosis', 'Unknown')}"
                )


def show_system_metrics(orchestrator):
    workflows = orchestrator.get_all_workflows()
    if not workflows:
        print("   No workflows processed")
        return
    total = len(workflows)
    completed = len([w for w in workflows if w.get("state") == "completed"])
    pending = len([w for w in workflows if w.get("state") == "awaiting_human_input"])  # noqa
    failed = len([w for w in workflows if w.get("state") == "failed"])  # noqa
    human_interventions = sum(len(w.get("human_interventions", [])) for w in workflows)
    print(f"   Total Workflows: {total}")
    print(f"   Completed: {completed} ({completed/total*100:.1f}%)")
    print(f"   Awaiting Human: {pending} ({pending/total*100:.1f}%)")
    print(f"   Failed: {failed} ({failed/total*100:.1f}%)")
    print(f"   Human Interventions: {human_interventions}")
    print(f"   Intervention Rate: {human_interventions/total*100:.1f}%")


def start_dashboard_in_background(orchestrator):
    import threading
    from hitl_dashboard import init_dashboard

    def start_dashboard():
        init_dashboard(orchestrator, port=5002)

    dashboard_thread = threading.Thread(target=start_dashboard)
    dashboard_thread.daemon = True
    dashboard_thread.start()
    print("📊 HITL Dashboard starting on http://localhost:5002")
    return dashboard_thread


if __name__ == "__main__":
    orchestrator = AdvancedWorkflowOrchestrator("models/retina_model_final.h5")
    dashboard_thread = start_dashboard_in_background(orchestrator)
    time.sleep(3)
    run_demo_scenarios()


