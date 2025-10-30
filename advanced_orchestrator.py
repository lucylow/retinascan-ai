import uuid
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass
import threading
import queue
import numpy as np
from abc import ABC
import time


class WorkflowState(Enum):
    PENDING = "pending"
    RUNNING = "running"
    PAUSED = "paused"
    AWAITING_HUMAN_INPUT = "awaiting_human_input"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class HumanInterventionType(Enum):
    DIAGNOSIS_REVIEW = "diagnosis_review"
    QUALITY_OVERRIDE = "quality_override"
    UNCERTAIN_CASE = "uncertain_case"
    EMERGENCY_FLAG = "emergency_flag"
    DATA_QUALITY_ISSUE = "data_quality_issue"


@dataclass
class HumanInterventionRequest:
    id: str
    workflow_id: str
    intervention_type: HumanInterventionType
    context: Dict[str, Any]
    priority: int
    timestamp: datetime
    required_actions: List[str]
    timeout_minutes: int = 30


@dataclass
class HumanInterventionResponse:
    request_id: str
    workflow_id: str
    approved: bool
    comments: str
    overrides: Dict[str, Any]
    timestamp: datetime
    reviewed_by: str


class RoutingRule:
    """Defines routing rules for workflow decisions"""

    def __init__(self, name: str, condition: Callable, target_agent: str, priority: int = 1):
        self.name = name
        self.condition = condition
        self.target_agent = target_agent
        self.priority = priority

    def evaluate(self, context: Dict) -> bool:
        try:
            return self.condition(context)
        except Exception:
            return False


class HumanInTheLoopManager:
    """Manages human intervention points in the workflow"""

    def __init__(self):
        self.pending_requests: Dict[str, HumanInterventionRequest] = {}
        self.responses: Dict[str, HumanInterventionResponse] = {}
        self.human_reviewers = ["dr_smith", "dr_jones", "tech_specialist"]
        self.auto_approve_rules = self._setup_auto_approve_rules()

    def _setup_auto_approve_rules(self):
        return [
            lambda ctx: ctx.get("confidence", 0) > 0.9 and ctx.get("severity", 0) < 2,
            lambda ctx: ctx.get("quality_score", 0) > 0.8 and ctx.get("previous_approvals", 0) > 5,
        ]

    def request_intervention(
        self,
        workflow_id: str,
        intervention_type: HumanInterventionType,
        context: Dict,
        priority: int = 1,
    ) -> str:
        request_id = f"HITL_{uuid.uuid4().hex[:8]}"

        request = HumanInterventionRequest(
            id=request_id,
            workflow_id=workflow_id,
            intervention_type=intervention_type,
            context=context,
            priority=priority,
            timestamp=datetime.now(),
            required_actions=self._get_required_actions(intervention_type),
        )

        # Check auto-approval before queuing
        if self._check_auto_approval(context):
            # Place in pending first so auto_approve can resolve it consistently
            self.pending_requests[request_id] = request
            self.auto_approve(request_id, "system_auto_approval")
            return request_id

        self.pending_requests[request_id] = request
        self._notify_reviewers(request)
        return request_id

    def _get_required_actions(self, intervention_type: HumanInterventionType) -> List[str]:
        actions = {
            HumanInterventionType.DIAGNOSIS_REVIEW: [
                "Review AI diagnosis",
                "Confirm or override severity",
                "Provide clinical notes",
            ],
            HumanInterventionType.QUALITY_OVERRIDE: [
                "Assess image quality",
                "Approve despite low quality",
                "Provide reason for override",
            ],
            HumanInterventionType.UNCERTAIN_CASE: [
                "Review uncertain findings",
                "Provide expert opinion",
                "Suggest additional tests",
            ],
            HumanInterventionType.EMERGENCY_FLAG: [
                "Verify emergency condition",
                "Contact patient if needed",
                "Escalate to senior doctor",
            ],
        }
        return actions.get(intervention_type, ["Review case"])

    def _check_auto_approval(self, context: Dict) -> bool:
        return any(rule(context) for rule in self.auto_approve_rules)

    def _notify_reviewers(self, request: HumanInterventionRequest):
        print(f"🔔 HITL Notification: {request.intervention_type.value}")
        print(f"   Workflow: {request.workflow_id}")
        print(f"   Priority: {request.priority}")
        print(f"   Required Actions: {', '.join(request.required_actions)}")

        # Simulate human response after delay
        delay = 2.0 if request.priority >= 3 else 5.0
        threading.Timer(delay, self._simulate_human_response, [request.id]).start()

    def _simulate_human_response(self, request_id: str):
        if request_id not in self.pending_requests:
            return
        request = self.pending_requests[request_id]

        if request.context.get("severity", 0) >= 3:
            response = HumanInterventionResponse(
                request_id=request_id,
                workflow_id=request.workflow_id,
                approved=True,
                comments="Emergency case confirmed. Proceed immediately.",
                overrides={},
                timestamp=datetime.now(),
                reviewed_by="dr_smith",
            )
        else:
            import random

            approved = random.choice([True, False])
            response = HumanInterventionResponse(
                request_id=request_id,
                workflow_id=request.workflow_id,
                approved=approved,
                comments="Reviewed and " + ("approved" if approved else "requires modification"),
                overrides={"severity_override": random.randint(0, 2)} if not approved else {},
                timestamp=datetime.now(),
                reviewed_by=random.choice(self.human_reviewers),
            )

        self.submit_response(response)

    def submit_response(self, response: HumanInterventionResponse):
        if response.request_id in self.pending_requests:
            self.responses[response.request_id] = response
            del self.pending_requests[response.request_id]
            print(f"✅ Human Response Received: {response.reviewed_by}")
            print(f"   Approved: {response.approved}")
            print(f"   Comments: {response.comments}")

    def get_response(self, request_id: str, timeout: int = 30) -> Optional[HumanInterventionResponse]:
        start_time = time.time()
        while time.time() - start_time < timeout:
            if request_id in self.responses:
                return self.responses[request_id]
            time.sleep(0.5)
        return None

    def get_pending_requests(self) -> List[HumanInterventionRequest]:
        return list(self.pending_requests.values())

    def auto_approve(self, request_id: str, reason: str):
        if request_id in self.pending_requests:
            request = self.pending_requests[request_id]
            response = HumanInterventionResponse(
                request_id=request_id,
                workflow_id=request.workflow_id,
                approved=True,
                comments=f"Auto-approved: {reason}",
                overrides={},
                timestamp=datetime.now(),
                reviewed_by="system_auto_approval",
            )
            self.submit_response(response)


class AdvancedWorkflowOrchestrator:
    """Advanced orchestrator with dynamic routing and human-in-the-loop"""

    def __init__(self, model_path: str):
        from ai_agents import (
            DataProcessorAgent,
            ModelSpecialistAgent,
            DiagnosisAnalystAgent,
            QualityControllerAgent,
            ReportGeneratorAgent,
        )

        self.agents = {
            "data_processor": DataProcessorAgent(),
            "model_specialist": ModelSpecialistAgent(model_path),
            "diagnosis_analyst": DiagnosisAnalystAgent(),
            "quality_controller": QualityControllerAgent(),
            "report_generator": ReportGeneratorAgent(),
        }

        self.hitl_manager = HumanInTheLoopManager()
        self.workflows: Dict[str, Dict] = {}
        self.routing_rules = self._setup_routing_rules()
        self.workflow_queue = queue.Queue()
        self.is_running = True

        self.processor_thread = threading.Thread(target=self._process_workflows)
        self.processor_thread.daemon = True
        self.processor_thread.start()

    def _setup_routing_rules(self) -> List[RoutingRule]:
        def high_severity_rule(context):
            return context.get("severity_level", 0) >= 3

        def low_confidence_rule(context):
            return context.get("confidence", 0) < 0.6

        def quality_issue_rule(context):
            return context.get("quality_score", 0) < 0.7

        def emergency_rule(context):
            return context.get("severity_level", 0) == 4

        return [
            RoutingRule("Emergency Case", emergency_rule, "emergency_protocol", priority=10),
            RoutingRule("High Severity", high_severity_rule, "priority_review", priority=5),
            RoutingRule("Low Confidence", low_confidence_rule, "extended_analysis", priority=3),
            RoutingRule("Quality Issues", quality_issue_rule, "quality_review", priority=2),
        ]

    def _evaluate_routing_rules(self, context: Dict) -> List[str]:
        applicable = []
        for rule in sorted(self.routing_rules, key=lambda x: x.priority, reverse=True):
            if rule.evaluate(context):
                applicable.append(rule.target_agent)
        return applicable

    def submit_workflow(self, image_data, image_id: str = None, metadata: Dict = None) -> str:
        workflow_id = image_id or f"workflow_{uuid.uuid4().hex[:8]}"
        workflow = {
            "id": workflow_id,
            "state": WorkflowState.PENDING.value,
            "image_data": image_data,
            "metadata": metadata or {},
            "current_step": "initial",
            "results": {},
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
            "routing_decisions": [],
            "human_interventions": [],
        }
        self.workflows[workflow_id] = workflow
        self.workflow_queue.put(workflow_id)
        print(f"🚀 Submitted workflow: {workflow_id}")
        return workflow_id

    def _process_workflows(self):
        while self.is_running:
            try:
                workflow_id = self.workflow_queue.get(timeout=1)
                self._execute_workflow(workflow_id)
            except queue.Empty:
                continue

    def _execute_workflow(self, workflow_id: str):
        workflow = self.workflows[workflow_id]
        try:
            workflow["state"] = WorkflowState.RUNNING.value
            workflow["updated_at"] = datetime.now()
            print(f"🔄 Processing workflow: {workflow_id}")

            # Step 1: Data Processing
            workflow["current_step"] = "data_processing"
            processed_data = self._execute_data_processing(workflow)

            if not processed_data["quality_pass"]:
                intervention_id = self._request_quality_intervention(workflow, processed_data)
                if not self._wait_for_human_response(workflow, intervention_id):
                    workflow["state"] = WorkflowState.FAILED.value
                    return

            # Step 2: Model Prediction
            workflow["current_step"] = "model_prediction"
            prediction_data = self._execute_model_prediction(workflow, processed_data)

            routing_targets = self._evaluate_routing_rules(
                {
                    "severity_level": prediction_data["prediction_result"]["severity_level"],
                    "confidence": prediction_data.get("model_confidence", 0),
                    "quality_score": processed_data.get("quality_score", 0),
                }
            )
            workflow["routing_decisions"] = routing_targets

            if "emergency_protocol" in routing_targets:
                self._execute_emergency_protocol(workflow, prediction_data)
                return

            if (not prediction_data["confidence_pass"]) or ("priority_review" in routing_targets):
                intervention_id = self._request_diagnosis_intervention(workflow, prediction_data)
                if not self._wait_for_human_response(workflow, intervention_id):
                    workflow["state"] = WorkflowState.FAILED.value
                    return

            # Step 3: Diagnosis Analysis
            workflow["current_step"] = "diagnosis_analysis"
            diagnosis_data = self._execute_diagnosis_analysis(workflow, prediction_data)

            # Step 4: Quality Control
            workflow["current_step"] = "quality_control"
            quality_data = self._execute_quality_control(workflow, diagnosis_data)

            if not quality_data["approved"]:
                intervention_id = self._request_quality_control_intervention(workflow, quality_data)
                if not self._wait_for_human_response(workflow, intervention_id):
                    workflow["state"] = WorkflowState.FAILED.value
                    return

            # Step 5: Report Generation
            workflow["current_step"] = "report_generation"
            final_report = self._execute_report_generation(workflow, quality_data)
            workflow["results"] = final_report
            workflow["state"] = WorkflowState.COMPLETED.value
            workflow["updated_at"] = datetime.now()
            print(f"✅ Workflow completed: {workflow_id}")

        except Exception as e:
            workflow["state"] = WorkflowState.FAILED.value
            workflow["error"] = str(e)
            workflow["updated_at"] = datetime.now()
            print(f"❌ Workflow failed: {workflow_id} - {str(e)}")

    def _execute_data_processing(self, workflow: Dict) -> Dict:
        agent = self.agents["data_processor"]
        message_content = {
            "image_data": workflow["image_data"],
            "image_id": workflow["id"],
            "metadata": workflow["metadata"],
        }
        result = agent.handle_message(type("MockMessage", (), {"content": message_content})())
        workflow.setdefault("results", {}).setdefault("data_processing", result)
        return result

    def _execute_model_prediction(self, workflow: Dict, processed_data: Dict) -> Dict:
        agent = self.agents["model_specialist"]
        result = agent.handle_message(type("MockMessage", (), {"content": processed_data})())
        workflow["results"]["model_prediction"] = result
        return result

    def _execute_diagnosis_analysis(self, workflow: Dict, prediction_data: Dict) -> Dict:
        agent = self.agents["diagnosis_analyst"]
        result = agent.handle_message(type("MockMessage", (), {"content": prediction_data})())
        workflow["results"]["diagnosis_analysis"] = result
        return result

    def _execute_quality_control(self, workflow: Dict, diagnosis_data: Dict) -> Dict:
        agent = self.agents["quality_controller"]
        result = agent.handle_message(type("MockMessage", (), {"content": diagnosis_data})())
        workflow["results"]["quality_control"] = result
        return result

    def _execute_report_generation(self, workflow: Dict, quality_data: Dict) -> Dict:
        agent = self.agents["report_generator"]
        result = agent.handle_message(type("MockMessage", (), {"content": quality_data})())
        return result

    def _request_quality_intervention(self, workflow: Dict, processed_data: Dict) -> str:
        context = {
            "workflow_id": workflow["id"],
            "quality_score": processed_data["quality_score"],
            "quality_threshold": 0.7,
            "step": "data_processing",
            "image_metadata": workflow.get("metadata", {}),
        }
        intervention_id = self.hitl_manager.request_intervention(
            workflow["id"], HumanInterventionType.QUALITY_OVERRIDE, context, priority=2
        )
        workflow["human_interventions"].append(
            {
                "intervention_id": intervention_id,
                "type": HumanInterventionType.QUALITY_OVERRIDE.value,
                "requested_at": datetime.now(),
            }
        )
        workflow["state"] = WorkflowState.AWAITING_HUMAN_INPUT.value
        return intervention_id

    def _request_diagnosis_intervention(self, workflow: Dict, prediction_data: Dict) -> str:
        context = {
            "workflow_id": workflow["id"],
            "diagnosis": prediction_data["prediction_result"]["diagnosis"],
            "confidence": prediction_data["model_confidence"],
            "severity": prediction_data["prediction_result"]["severity_level"],
            "probabilities": prediction_data["prediction_result"]["probabilities"],
            "step": "model_prediction",
            "routing_decisions": workflow.get("routing_decisions", []),
        }
        priority = 3 if context["severity"] >= 3 else 1
        intervention_id = self.hitl_manager.request_intervention(
            workflow["id"], HumanInterventionType.DIAGNOSIS_REVIEW, context, priority=priority
        )
        workflow["human_interventions"].append(
            {
                "intervention_id": intervention_id,
                "type": HumanInterventionType.DIAGNOSIS_REVIEW.value,
                "requested_at": datetime.now(),
            }
        )
        workflow["state"] = WorkflowState.AWAITING_HUMAN_INPUT.value
        return intervention_id

    def _request_quality_control_intervention(self, workflow: Dict, quality_data: Dict) -> str:
        context = {
            "workflow_id": workflow["id"],
            "quality_checks": quality_data["validation_result"]["checks_performed"],
            "overall_approval": quality_data["approved"],
            "quality_score": quality_data["validation_result"].get("quality_score", 0),
            "step": "quality_control",
        }
        intervention_id = self.hitl_manager.request_intervention(
            workflow["id"], HumanInterventionType.QUALITY_OVERRIDE, context, priority=2
        )
        workflow["human_interventions"].append(
            {
                "intervention_id": intervention_id,
                "type": HumanInterventionType.QUALITY_OVERRIDE.value,
                "requested_at": datetime.now(),
            }
        )
        workflow["state"] = WorkflowState.AWAITING_HUMAN_INPUT.value
        return intervention_id

    def _execute_emergency_protocol(self, workflow: Dict, prediction_data: Dict):
        print(f"🚨 EMERGENCY PROTOCOL ACTIVATED for {workflow['id']}")
        context = {
            "workflow_id": workflow["id"],
            "diagnosis": prediction_data["prediction_result"]["diagnosis"],
            "severity": prediction_data["prediction_result"]["severity_level"],
            "confidence": prediction_data["model_confidence"],
            "emergency": True,
        }
        intervention_id = self.hitl_manager.request_intervention(
            workflow["id"], HumanInterventionType.EMERGENCY_FLAG, context, priority=10
        )
        response = self.hitl_manager.get_response(intervention_id, timeout=10)
        if response and response.approved:
            emergency_report = {
                "emergency": True,
                "diagnosis": prediction_data["prediction_result"]["diagnosis"],
                "severity_level": prediction_data["prediction_result"]["severity_level"],
                "timestamp": datetime.now().isoformat(),
                "human_reviewed": True,
                "reviewed_by": response.reviewed_by,
                "actions": [
                    "IMMEDIATE_MEDICAL_ATTENTION_REQUIRED",
                    "CONTACT_PATIENT",
                    "ALERT_EMERGENCY_SERVICES",
                ],
            }
            workflow["results"] = {"emergency_report": emergency_report}
            workflow["state"] = WorkflowState.COMPLETED.value
        else:
            workflow["state"] = WorkflowState.FAILED.value
            workflow["error"] = "Emergency case not approved by human"

    def _wait_for_human_response(self, workflow: Dict, intervention_id: str, timeout: int = 30) -> bool:
        response = self.hitl_manager.get_response(intervention_id, timeout)
        if response:
            workflow["human_interventions"][-1]["response"] = {
                "approved": response.approved,
                "comments": response.comments,
                "overrides": response.overrides,
                "reviewed_by": response.reviewed_by,
                "timestamp": response.timestamp.isoformat(),
            }
            workflow["human_interventions"][-1]["responded_at"] = datetime.now()
            workflow["state"] = WorkflowState.RUNNING.value
            if response.overrides:
                workflow.setdefault("results", {}).setdefault("human_overrides", {}).update(
                    response.overrides
                )
            return response.approved
        else:
            workflow["state"] = WorkflowState.FAILED.value
            workflow["error"] = "Human response timeout"
            return False

    def get_workflow_status(self, workflow_id: str) -> Optional[Dict]:
        return self.workflows.get(workflow_id)

    def get_all_workflows(self) -> List[Dict]:
        return list(self.workflows.values())

    def get_pending_interventions(self) -> List[HumanInterventionRequest]:
        return self.hitl_manager.get_pending_requests()

    def submit_human_response(
        self,
        request_id: str,
        approved: bool,
        comments: str = "",
        overrides: Dict = None,
        reviewer: str = "manual_reviewer",
    ):
        # Lookup workflow_id from pending if available
        workflow_id = ""
        if request_id in self.hitl_manager.pending_requests:
            workflow_id = self.hitl_manager.pending_requests[request_id].workflow_id
        resp = HumanInterventionResponse(
            request_id=request_id,
            workflow_id=workflow_id,
            approved=approved,
            comments=comments,
            overrides=overrides or {},
            timestamp=datetime.now(),
            reviewed_by=reviewer,
        )
        self.hitl_manager.submit_response(resp)

    def stop(self):
        self.is_running = False
        if self.processor_thread.is_alive():
            self.processor_thread.join(timeout=5)


