from typing import Dict, List, Optional, Callable
import threading
import time
from datetime import datetime, timedelta
import json
import uuid
import numpy as np
from ai_agents import *
import tensorflow as tf  # for transparency-enhanced orchestrator

# Transparency & Explainability components
try:
    from transparency_agent import TransparencyAgent
    from enhanced_report_generator import EnhancedReportGenerator
except Exception:
    # Allow base orchestrator usage even if transparency modules are unavailable
    TransparencyAgent = None  # type: ignore
    EnhancedReportGenerator = None  # type: ignore


class WorkflowOrchestrator:
    """Orchestrates the multi-agent workflow for retinal diagnosis"""

    def __init__(self, model_path: str):
        self.agents = self.initialize_agents(model_path)
        self.workflow_history = []
        self.active_workflows = {}
        self.performance_monitor = PerformanceMonitor()

    def initialize_agents(self, model_path: str) -> Dict[AgentRole, BaseAgent]:
        """Initialize all AI agents"""
        return {
            AgentRole.DATA_PROCESSOR: DataProcessorAgent(),
            AgentRole.MODEL_SPECIALIST: ModelSpecialistAgent(model_path),
            AgentRole.DIAGNOSIS_ANALYST: DiagnosisAnalystAgent(),
            AgentRole.QUALITY_CONTROLLER: QualityControllerAgent(),
            AgentRole.REPORT_GENERATOR: ReportGeneratorAgent(),
        }

    def process_image(self, image_data, image_id: str = None) -> Dict:
        """Main workflow entry point - process a single image"""
        workflow_id = image_id or f"workflow_{uuid.uuid4().hex[:8]}"

        print(f"🚀 Starting workflow {workflow_id}")

        # Record workflow start
        self.workflow_history.append(
            {
                "workflow_id": workflow_id,
                "start_time": datetime.now(),
                "status": "started",
            }
        )

        try:
            # Step 1: Data Processing
            print("📊 Step 1: Data Processing...")
            data_processor = self.agents[AgentRole.DATA_PROCESSOR]
            processed_data = data_processor.handle_message(
                Message(
                    id=str(uuid.uuid4()),
                    type=MessageType.IMAGE_PROCESSED,
                    sender=AgentRole.WORKFLOW_COORDINATOR,
                    receiver=AgentRole.DATA_PROCESSOR,
                    content={"image_data": image_data, "image_id": workflow_id},
                    timestamp=datetime.now(),
                )
            )

            if not processed_data["quality_pass"]:
                raise Exception(
                    f"Image quality too low: {processed_data['quality_score']:.2f}"
                )

            # Step 2: Model Prediction
            print("🤖 Step 2: Model Prediction...")
            model_specialist = self.agents[AgentRole.MODEL_SPECIALIST]
            prediction_data = model_specialist.handle_message(
                Message(
                    id=str(uuid.uuid4()),
                    type=MessageType.PREDICTION_READY,
                    sender=AgentRole.DATA_PROCESSOR,
                    receiver=AgentRole.MODEL_SPECIALIST,
                    content=processed_data,
                    timestamp=datetime.now(),
                )
            )

            if not prediction_data["confidence_pass"]:
                raise Exception(
                    f"Model confidence too low: {prediction_data['model_confidence']:.2f}"
                )

            # Step 3: Diagnosis Analysis
            print("🔍 Step 3: Diagnosis Analysis...")
            diagnosis_analyst = self.agents[AgentRole.DIAGNOSIS_ANALYST]
            diagnosis_data = diagnosis_analyst.handle_message(
                Message(
                    id=str(uuid.uuid4()),
                    type=MessageType.DIAGNOSIS_COMPLETE,
                    sender=AgentRole.MODEL_SPECIALIST,
                    receiver=AgentRole.DIAGNOSIS_ANALYST,
                    content=prediction_data,
                    timestamp=datetime.now(),
                )
            )

            # Step 4: Quality Control
            print("✅ Step 4: Quality Control...")
            quality_controller = self.agents[AgentRole.QUALITY_CONTROLLER]
            quality_data = quality_controller.handle_message(
                Message(
                    id=str(uuid.uuid4()),
                    type=MessageType.QUALITY_CHECKED,
                    sender=AgentRole.DIAGNOSIS_ANALYST,
                    receiver=AgentRole.QUALITY_CONTROLLER,
                    content=diagnosis_data,
                    timestamp=datetime.now(),
                )
            )

            if not quality_data["approved"]:
                raise Exception("Quality control failed")

            # Step 5: Report Generation
            print("📄 Step 5: Report Generation...")
            report_generator = self.agents[AgentRole.REPORT_GENERATOR]
            final_report = report_generator.handle_message(
                Message(
                    id=str(uuid.uuid4()),
                    type=MessageType.REPORT_GENERATED,
                    sender=AgentRole.QUALITY_CONTROLLER,
                    receiver=AgentRole.REPORT_GENERATOR,
                    content=quality_data,
                    timestamp=datetime.now(),
                )
            )

            # Record successful completion
            self.workflow_history.append(
                {
                    "workflow_id": workflow_id,
                    "end_time": datetime.now(),
                    "status": "completed",
                    "result": final_report,
                }
            )

            print(f"✅ Workflow {workflow_id} completed successfully!")

            return final_report

        except Exception as e:
            # Record failure
            self.workflow_history.append(
                {
                    "workflow_id": workflow_id,
                    "end_time": datetime.now(),
                    "status": "failed",
                    "error": str(e),
                }
            )

            print(f"❌ Workflow {workflow_id} failed: {str(e)}")
            raise e

    def batch_process(self, image_batch: List, parallel: bool = True) -> List[Dict]:
        """Process multiple images in batch"""
        results = []

        if parallel:
            # Parallel processing using threads
            threads = []
            thread_results = {}

            def process_single(image_data, index):
                try:
                    result = self.process_image(image_data, f"batch_{index}")
                    thread_results[index] = result
                except Exception as e:
                    thread_results[index] = {"error": str(e)}

            for i, image_data in enumerate(image_batch):
                thread = threading.Thread(target=process_single, args=(image_data, i))
                threads.append(thread)
                thread.start()

            # Wait for all threads to complete
            for thread in threads:
                thread.join()

            # Collect results in order
            for i in range(len(image_batch)):
                results.append(thread_results.get(i, {"error": "Processing failed"}))

        else:
            # Sequential processing
            for i, image_data in enumerate(image_batch):
                try:
                    result = self.process_image(image_data, f"batch_{i}")
                    results.append(result)
                except Exception as e:
                    results.append({"error": str(e)})

        return results

    def get_workflow_status(self, workflow_id: str) -> Dict:
        """Get status of a specific workflow"""
        for record in reversed(self.workflow_history):
            if record["workflow_id"] == workflow_id:
                return record
        return {"status": "not_found"}

    def get_system_metrics(self) -> Dict:
        """Get comprehensive system metrics"""
        metrics = {
            "timestamp": datetime.now().isoformat(),
            "total_workflows": len(self.workflow_history),
            "successful_workflows": len(
                [w for w in self.workflow_history if w.get("status") == "completed"]
            ),
            "failed_workflows": len(
                [w for w in self.workflow_history if w.get("status") == "failed"]
            ),
            "agent_performance": {},
        }

        for role, agent in self.agents.items():
            metrics["agent_performance"][role.value] = agent.performance_metrics

        return metrics

    def export_report(self, workflow_id: str, format: str = "json") -> str:
        """Export workflow report in specified format"""
        workflow_data = self.get_workflow_status(workflow_id)

        if format == "json":
            return json.dumps(workflow_data, indent=2, default=str)
        elif format == "html":
            return self.generate_html_report(workflow_data)
        else:
            raise ValueError(f"Unsupported format: {format}")

    def generate_html_report(self, workflow_data: Dict) -> str:
        """Generate HTML report"""
        # Simplified HTML report generation
        report = workflow_data.get("result", {}).get("final_report", {})

        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>RetinaScan AI Report</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 40px; }}
                .header {{ background: #f0f8ff; padding: 20px; border-radius: 10px; }}
                .section {{ margin: 20px 0; padding: 15px; border-left: 4px solid #007acc; }}
                .urgent {{ border-left-color: #ff4444; background: #fff0f0; }}
                .recommendation {{ background: #f9f9f9; padding: 10px; margin: 5px 0; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>🩺 RetinaScan AI Diagnostic Report</h1>
                <p>Report ID: {report.get('report_id', 'N/A')}</p>
                <p>Generated: {report.get('patient_info', {}).get('processing_date', 'N/A')}</p>
            </div>

            <div class="section">
                <h2>Diagnostic Findings</h2>
                <p><strong>Primary Diagnosis:</strong> {report.get('diagnostic_findings', {}).get('primary_diagnosis', 'N/A')}</p>
                <p><strong>Confidence Level:</strong> {report.get('diagnostic_findings', {}).get('confidence_level', 'N/A')}</p>
                <p><strong>Severity Level:</strong> {report.get('diagnostic_findings', {}).get('severity_level', 'N/A')}</p>
            </div>

            <div class="section {'urgent' if report.get('clinical_assessment', {}).get('urgency_level') in ['urgent', 'emergency'] else ''}">
                <h2>Clinical Assessment</h2>
                <p><strong>Urgency Level:</strong> {report.get('clinical_assessment', {}).get('urgency_level', 'N/A')}</p>
                <p><strong>Quality Assessment:</strong> {report.get('clinical_assessment', {}).get('quality_assessment', 'N/A')}</p>
            </div>

            <div class="section">
                <h2>Recommendations</h2>
                {"".join(f'<div class="recommendation">{rec}</div>' for rec in report.get('recommendations', {}).get('immediate_actions', []))}
            </div>
        </body>
        </html>
        """

        return html


class PerformanceMonitor:
    """Monitors system performance and provides analytics"""

    def __init__(self):
        self.metrics_history = []

    def record_metric(self, metric_name: str, value: float, timestamp: datetime = None):
        """Record a performance metric"""
        self.metrics_history.append(
            {
                "metric": metric_name,
                "value": value,
                "timestamp": timestamp or datetime.now(),
            }
        )

    def get_performance_summary(self, window_minutes: int = 60) -> Dict:
        """Get performance summary for the last specified minutes"""
        cutoff_time = datetime.now() - timedelta(minutes=window_minutes)
        recent_metrics = [m for m in self.metrics_history if m["timestamp"] > cutoff_time]

        return {
            "total_operations": len(recent_metrics),
            "average_processing_time": self.calculate_average(
                recent_metrics, "processing_time"
            ),
            "success_rate": self.calculate_success_rate(recent_metrics),
            "system_throughput": len(recent_metrics) / window_minutes,  # operations per minute
        }

    def calculate_average(self, metrics: List[Dict], metric_name: str) -> float:
        """Calculate average for specific metric"""
        values = [m["value"] for m in metrics if m["metric"] == metric_name]
        return sum(values) / len(values) if values else 0.0

    def calculate_success_rate(self, metrics: List[Dict]) -> float:
        """Calculate success rate from metrics"""
        success_metrics = [m for m in metrics if m["metric"] == "success" and m["value"] == 1]
        return len(success_metrics) / len(metrics) if metrics else 0.0


# Example usage and testing
def main():
    """Example usage of the AI workflow system"""

    # Initialize orchestrator
    orchestrator = WorkflowOrchestrator("models/retina_model_final.h5")

    # Create a sample image (in practice, you'd load real images)
    sample_image = np.random.rand(512, 512, 3) * 255

    try:
        # Process single image
        print("🧪 Testing single image processing...")
        result = orchestrator.process_image(sample_image, "test_001")

        print("\n📋 Final Report:")
        print(json.dumps(result, indent=2, default=str))

        # Get system metrics
        print("\n📊 System Metrics:")
        metrics = orchestrator.get_system_metrics()
        print(json.dumps(metrics, indent=2, default=str))

        # Export report
        html_report = orchestrator.export_report("test_001", "html")
        with open("retina_report.html", "w") as f:
            f.write(html_report)
        print("\n💾 HTML report saved as 'retina_report.html'")

    except Exception as e:
        print(f"❌ Error: {str(e)}")


if __name__ == "__main__":
    main()

# Enhanced orchestrator with transparency integration
class TransparencyEnhancedOrchestrator(WorkflowOrchestrator):
    """Orchestrator with built-in transparency and explainability"""

    def __init__(self, model_path: str):
        super().__init__(model_path)

        # Load AI model for XAI
        try:
            self.model = tf.keras.models.load_model(model_path)
        except Exception:
            self.model = None

        # Initialize transparency components if available
        if TransparencyAgent and EnhancedReportGenerator and self.model is not None:
            self.transparency_agent = TransparencyAgent(self.model)
            self.enhanced_report_generator = EnhancedReportGenerator(self.model)
        else:
            self.transparency_agent = None
            self.enhanced_report_generator = None

    def _execute_report_generation(self, workflow: Dict, quality_data: Dict) -> Dict:
        """Enhanced report generation with explainability"""

        if not self.enhanced_report_generator:
            return {
                'error': 'Transparency modules unavailable',
                'clinician_report': {},
                'patient_report': {}
            }

        workflow_data = {
            'workflow_id': workflow.get('id', 'unknown'),
            'image_data': workflow.get('image_data'),
            'prediction_result': workflow.get('results', {}).get('model_prediction'),
            'quality_assessment': workflow.get('results', {}).get('data_processing'),
            'diagnosis_analysis': workflow.get('results', {}).get('diagnosis_analysis'),
            'quality_control': quality_data,
            'metadata': workflow.get('metadata', {})
        }

        enhanced_report = self.enhanced_report_generator.generate_enhanced_report(
            workflow_data,
            audience='clinician'
        )

        patient_report = self.enhanced_report_generator.generate_enhanced_report(
            workflow_data,
            audience='patient'
        )

        return {
            'clinician_report': enhanced_report,
            'patient_report': patient_report,
            'technical_details': {
                'explanation_quality': enhanced_report['explanations']['quality_metrics'],
                'uncertainty_level': enhanced_report['explanations']['technical_explanation']['uncertainty_breakdown']['level'],
                'audit_trail_available': True
            }
        }

    def get_explanation_dashboard(self, workflow_id: str) -> Dict:
        """Get explanation dashboard for a workflow"""

        if not self.transparency_agent:
            return {'error': 'Transparency modules unavailable'}
        return self.transparency_agent.generate_explanation_dashboard(workflow_id)

    def get_system_transparency_metrics(self) -> Dict:
        """Get system-wide transparency metrics"""

        if not self.transparency_agent:
            return {'error': 'Transparency modules unavailable'}

        qualities = [exp['explanation_quality'] for exp in self.transparency_agent.explanation_history]
        avg_quality = np.mean(qualities) if qualities else 0.0

        return {
            'total_explanations_generated': len(self.transparency_agent.explanation_history),
            'average_explanation_quality': float(avg_quality),
            'common_uncertainty_patterns': self.transparency_agent._identify_common_patterns(),
            'explanation_quality_trends': self.transparency_agent._get_quality_trends(),
            'system_trust_score': self._calculate_system_trust_score()
        }

    def _calculate_system_trust_score(self) -> float:
        """Calculate overall system trust score based on transparency metrics"""

        if not self.transparency_agent or not self.transparency_agent.explanation_history:
            return 0.0

        quality_scores = [exp['explanation_quality'] for exp in self.transparency_agent.explanation_history]
        avg_quality = float(np.mean(quality_scores)) if quality_scores else 0.0
        consistency = 1.0 - min(float(np.std(quality_scores)), 0.5) if quality_scores else 0.0
        good_explanations = sum(1 for q in quality_scores if q > 0.6)
        coverage = (good_explanations / len(quality_scores)) if quality_scores else 0.0

        trust_score = (avg_quality * 0.5) + (consistency * 0.3) + (coverage * 0.2)
        return float(trust_score)



