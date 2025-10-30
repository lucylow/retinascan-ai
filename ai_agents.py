import uuid
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import numpy as np
from tensorflow import keras
import cv2
import json


class AgentRole(Enum):
    DATA_PROCESSOR = "data_processor"
    MODEL_SPECIALIST = "model_specialist"
    DIAGNOSIS_ANALYST = "diagnosis_analyst"
    QUALITY_CONTROLLER = "quality_controller"
    REPORT_GENERATOR = "report_generator"
    WORKFLOW_COORDINATOR = "workflow_coordinator"


class MessageType(Enum):
    IMAGE_PROCESSED = "image_processed"
    PREDICTION_READY = "prediction_ready"
    DIAGNOSIS_COMPLETE = "diagnosis_complete"
    QUALITY_CHECKED = "quality_checked"
    REPORT_GENERATED = "report_generated"
    ERROR_OCCURRED = "error_occurred"


@dataclass
class Message:
    id: str
    type: MessageType
    sender: AgentRole
    receiver: AgentRole
    content: Dict[str, Any]
    timestamp: datetime
    priority: int = 1


class BaseAgent:
    """Base class for all AI agents"""

    def __init__(self, role: AgentRole, agent_id: str = None):
        self.role = role
        self.agent_id = agent_id or f"{role.value}_{uuid.uuid4().hex[:8]}"
        self.message_queue = []
        self.performance_metrics = {
            "tasks_processed": 0,
            "success_rate": 0.0,
            "average_processing_time": 0.0,
        }

    def receive_message(self, message: Message):
        """Receive and queue messages"""
        self.message_queue.append(message)
        print(f"🔔 {self.agent_id} received message: {message.type.value}")

    def process_next_message(self):
        """Process the next message in queue"""
        if self.message_queue:
            message = self.message_queue.pop(0)
            return self.handle_message(message)
        return None

    def handle_message(self, message: Message):
        """Handle incoming message - to be implemented by subclasses"""
        raise NotImplementedError

    def send_message(self, receiver: "BaseAgent", message_type: MessageType, content: Dict):
        """Send message to another agent"""
        message = Message(
            id=str(uuid.uuid4()),
            type=message_type,
            sender=self.role,
            receiver=receiver.role,
            content=content,
            timestamp=datetime.now(),
        )
        receiver.receive_message(message)

    def update_metrics(self, success: bool, processing_time: float):
        """Update agent performance metrics"""
        self.performance_metrics["tasks_processed"] += 1
        if success:
            current_success = self.performance_metrics["success_rate"]
            total_tasks = self.performance_metrics["tasks_processed"]
            self.performance_metrics["success_rate"] = (
                (current_success * (total_tasks - 1) + 1) / total_tasks
            )

        current_avg = self.performance_metrics["average_processing_time"]
        total_tasks = self.performance_metrics["tasks_processed"]
        self.performance_metrics["average_processing_time"] = (
            (current_avg * (total_tasks - 1) + processing_time) / total_tasks
        )


class DataProcessorAgent(BaseAgent):
    """Handles image preprocessing and quality assessment"""

    def __init__(self):
        super().__init__(AgentRole.DATA_PROCESSOR)
        self.quality_threshold = 0.7

    def handle_message(self, message: Message):
        start_time = datetime.now()

        try:
            if message.type == MessageType.IMAGE_PROCESSED:
                # This agent initiates the workflow
                image_data = message.content["image_data"]
                image_id = message.content["image_id"]

                # Preprocess image
                processed_data = self.preprocess_image(image_data)

                # Assess quality
                quality_score = self.assess_image_quality(processed_data)

                processing_time = (datetime.now() - start_time).total_seconds()
                self.update_metrics(True, processing_time)

                return {
                    "processed_image": processed_data,
                    "quality_score": quality_score,
                    "image_id": image_id,
                    "quality_pass": quality_score >= self.quality_threshold,
                }

        except Exception as e:
            processing_time = (datetime.now() - start_time).total_seconds()
            self.update_metrics(False, processing_time)
            raise e

    def preprocess_image(self, image_data):
        """Advanced image preprocessing"""
        # Convert to RGB if necessary
        if len(image_data.shape) == 3 and image_data.shape[2] == 3:
            image_rgb = cv2.cvtColor(image_data, cv2.COLOR_BGR2RGB)
        else:
            image_rgb = image_data

        # Resize
        image_resized = cv2.resize(image_rgb, (224, 224))

        # Apply CLAHE for contrast enhancement
        lab = cv2.cvtColor(image_resized, cv2.COLOR_RGB2LAB)
        lab_planes = list(cv2.split(lab))
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        lab_planes[0] = clahe.apply(lab_planes[0])
        lab = cv2.merge(lab_planes)
        image_enhanced = cv2.cvtColor(lab, cv2.COLOR_LAB2RGB)

        # Normalize
        image_normalized = image_enhanced.astype("float32") / 255.0

        return image_normalized

    def assess_image_quality(self, image_data):
        """Assess image quality for diagnosis"""
        # Calculate image sharpness (variance of Laplacian)
        gray = cv2.cvtColor((image_data * 255).astype("uint8"), cv2.COLOR_RGB2GRAY)
        sharpness = cv2.Laplacian(gray, cv2.CV_64F).var()

        # Calculate brightness and contrast
        brightness = np.mean(gray)
        contrast = np.std(gray)

        # Normalize scores
        sharpness_score = min(sharpness / 1000, 1.0)  # Normalize to 0-1
        brightness_score = 1 - abs(brightness - 127) / 127  # Ideal around 127
        contrast_score = min(contrast / 80, 1.0)  # Normalize to 0-1

        # Combined quality score
        quality_score = (
            sharpness_score * 0.4 + brightness_score * 0.3 + contrast_score * 0.3
        )

        return quality_score


class ModelSpecialistAgent(BaseAgent):
    """Handles model inference and prediction"""

    def __init__(self, model_path: str):
        super().__init__(AgentRole.MODEL_SPECIALIST)
        self.model = self.load_model(model_path)
        self.confidence_threshold = 0.6

    def handle_message(self, message: Message):
        start_time = datetime.now()

        try:
            if hasattr(message, "content") and "processed_image" in message.content:
                processed_image = message.content["processed_image"]
                image_id = message.content["image_id"]

                # Make prediction
                prediction_result = self.predict(processed_image)

                processing_time = (datetime.now() - start_time).total_seconds()
                self.update_metrics(True, processing_time)

                return {
                    "prediction_result": prediction_result,
                    "image_id": image_id,
                    "model_confidence": prediction_result["confidence"],
                    "confidence_pass": prediction_result["confidence"]
                    >= self.confidence_threshold,
                }

        except Exception as e:
            processing_time = (datetime.now() - start_time).total_seconds()
            self.update_metrics(False, processing_time)
            raise e

    def load_model(self, model_path):
        """Load the trained model"""
        try:
            return keras.models.load_model(model_path)
        except Exception as e:
            print(f"Error loading model: {e}")
            # Return a mock model for demonstration
            return self.create_mock_model()

    def create_mock_model(self):
        """Create mock model for demonstration purposes"""
        # This would be your actual trained model in production
        model = keras.Sequential(
            [
                keras.layers.Input(shape=(224, 224, 3)),
                keras.layers.Conv2D(32, 3, activation="relu"),
                keras.layers.GlobalAveragePooling2D(),
                keras.layers.Dense(5, activation="softmax"),
            ]
        )
        model.compile(optimizer="adam", loss="categorical_crossentropy")
        return model

    def predict(self, processed_image):
        """Make prediction using the model"""
        # Add batch dimension
        image_batch = np.expand_dims(processed_image, axis=0)

        # Get prediction
        predictions = self.model.predict(image_batch, verbose=0)
        predicted_class = np.argmax(predictions[0])
        confidence = float(np.max(predictions[0]))

        # Class names
        class_names = [
            "No Diabetic Retinopathy",
            "Mild Diabetic Retinopathy",
            "Moderate Diabetic Retinopathy",
            "Severe Diabetic Retinopathy",
            "Proliferative Diabetic Retinopathy",
        ]

        # All probabilities
        probabilities = {
            class_names[i]: float(predictions[0][i]) for i in range(len(class_names))
        }

        return {
            "diagnosis": class_names[predicted_class],
            "severity_level": int(predicted_class),
            "confidence": confidence,
            "probabilities": probabilities,
        }


class DiagnosisAnalystAgent(BaseAgent):
    """Analyzes predictions and provides clinical context"""

    def __init__(self):
        super().__init__(AgentRole.DIAGNOSIS_ANALYST)
        self.clinical_guidelines = self.load_clinical_guidelines()

    def handle_message(self, message: Message):
        start_time = datetime.now()

        try:
            if hasattr(message, "content") and "prediction_result" in message.content:
                prediction_result = message.content["prediction_result"]
                image_id = message.content["image_id"]

                # Analyze diagnosis
                analysis = self.analyze_diagnosis(prediction_result)

                processing_time = (datetime.now() - start_time).total_seconds()
                self.update_metrics(True, processing_time)

                return {
                    "diagnosis_analysis": analysis,
                    "image_id": image_id,
                    "prediction_result": prediction_result,
                }

        except Exception as e:
            processing_time = (datetime.now() - start_time).total_seconds()
            self.update_metrics(False, processing_time)
            raise e

    def load_clinical_guidelines(self):
        """Load clinical guidelines for diagnosis"""
        return {
            0: {
                "urgency": "low",
                "follow_up": "12 months",
                "recommendations": ["Continue annual screening", "Maintain blood sugar control"],
                "risk_factors": ["None detected"],
            },
            1: {
                "urgency": "medium",
                "follow_up": "6-12 months",
                "recommendations": ["Consult ophthalmologist", "Optimize glycemic control"],
                "risk_factors": ["Microaneurysms present"],
            },
            2: {
                "urgency": "high",
                "follow_up": "3-6 months",
                "recommendations": [
                    "Urgent ophthalmologist consultation",
                    "Consider laser treatment",
                ],
                "risk_factors": ["Hemorrhages", "Cotton wool spots"],
            },
            3: {
                "urgency": "urgent",
                "follow_up": "1 month",
                "recommendations": [
                    "Immediate specialist care",
                    "Laser treatment likely needed",
                ],
                "risk_factors": ["Venous beading", "IRMAs"],
            },
            4: {
                "urgency": "emergency",
                "follow_up": "Immediate",
                "recommendations": ["Emergency care required", "Possible vitrectomy"],
                "risk_factors": ["Neovascularization", "Vitreous hemorrhage"],
            },
        }

    def analyze_diagnosis(self, prediction_result):
        """Provide clinical analysis of the diagnosis"""
        severity = prediction_result["severity_level"]
        confidence = prediction_result["confidence"]

        guidelines = self.clinical_guidelines.get(severity, {})

        analysis = {
            "clinical_diagnosis": prediction_result["diagnosis"],
            "severity_level": severity,
            "confidence_level": self.get_confidence_level(confidence),
            "urgency": guidelines.get("urgency", "unknown"),
            "recommended_follow_up": guidelines.get("follow_up", "unknown"),
            "clinical_recommendations": guidelines.get("recommendations", []),
            "identified_risk_factors": guidelines.get("risk_factors", []),
            "confidence_score": confidence,
            "timestamp": datetime.now().isoformat(),
        }

        return analysis

    def get_confidence_level(self, confidence):
        """Convert numerical confidence to descriptive level"""
        if confidence >= 0.9:
            return "Very High"
        elif confidence >= 0.8:
            return "High"
        elif confidence >= 0.7:
            return "Moderate"
        elif confidence >= 0.6:
            return "Low"
        else:
            return "Very Low"


class QualityControllerAgent(BaseAgent):
    """Controls quality and validates results"""

    def __init__(self):
        super().__init__(AgentRole.QUALITY_CONTROLLER)
        self.quality_standards = {
            "min_confidence": 0.6,
            "min_quality_score": 0.7,
            "max_processing_time": 30.0,  # seconds
        }

    def handle_message(self, message: Message):
        start_time = datetime.now()

        try:
            # Validate different types of results
            if hasattr(message, "content"):
                validation_result = self.validate_results(message.content)

                processing_time = (datetime.now() - start_time).total_seconds()
                self.update_metrics(True, processing_time)

                return {
                    "validation_result": validation_result,
                    "content": message.content,
                    "approved": validation_result["overall_approval"],
                }

        except Exception as e:
            processing_time = (datetime.now() - start_time).total_seconds()
            self.update_metrics(False, processing_time)
            raise e

    def validate_results(self, content):
        """Validate the quality of results from all agents"""
        checks = []

        # Check image quality
        if "quality_score" in content:
            quality_pass = (
                content["quality_score"] >= self.quality_standards["min_quality_score"]
            )
            checks.append(("Image Quality", quality_pass, content["quality_score"]))

        # Check model confidence
        if "model_confidence" in content:
            confidence_pass = (
                content["model_confidence"] >= self.quality_standards["min_confidence"]
            )
            checks.append(("Model Confidence", confidence_pass, content["model_confidence"]))

        # Check diagnosis completeness
        if "diagnosis_analysis" in content:
            diagnosis = content["diagnosis_analysis"]
            completeness_pass = all(
                [
                    diagnosis.get("clinical_diagnosis"),
                    diagnosis.get("urgency"),
                    diagnosis.get("clinical_recommendations"),
                ]
            )
            checks.append(("Diagnosis Completeness", completeness_pass, 1.0 if completeness_pass else 0.0))

        # Calculate overall approval
        overall_approval = all(check[1] for check in checks) if checks else False

        return {
            "checks_performed": checks,
            "overall_approval": overall_approval,
            "quality_score": sum(check[2] for check in checks) / len(checks) if checks else 0.0,
            "timestamp": datetime.now().isoformat(),
        }


class ReportGeneratorAgent(BaseAgent):
    """Generates comprehensive reports"""

    def __init__(self):
        super().__init__(AgentRole.REPORT_GENERATOR)
        self.report_templates = self.load_report_templates()

    def handle_message(self, message: Message):
        start_time = datetime.now()

        try:
            if hasattr(message, "content") and "validation_result" in message.content:
                content = message.content["content"]
                validation = message.content["validation_result"]

                # Generate report
                report = self.generate_report(content, validation)

                processing_time = (datetime.now() - start_time).total_seconds()
                self.update_metrics(True, processing_time)

                return {
                    "final_report": report,
                    "image_id": content.get("image_id", "unknown"),
                    "report_timestamp": datetime.now().isoformat(),
                }

        except Exception as e:
            processing_time = (datetime.now() - start_time).total_seconds()
            self.update_metrics(False, processing_time)
            raise e

    def load_report_templates(self):
        """Load report templates for different severity levels"""
        return {
            "low": "Routine follow-up recommended.",
            "medium": "Specialist consultation advised.",
            "high": "Urgent ophthalmology referral needed.",
            "urgent": "Immediate medical attention required.",
            "emergency": "Emergency care essential.",
        }

    def generate_report(self, content, validation):
        """Generate comprehensive diagnostic report"""

        diagnosis_analysis = content.get("diagnosis_analysis", {})
        prediction_result = content.get("prediction_result", {})

        report = {
            "report_id": f"RETINA_{uuid.uuid4().hex[:8]}",
            "patient_info": {
                "image_id": content.get("image_id", "unknown"),
                "processing_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            },
            "diagnostic_findings": {
                "primary_diagnosis": diagnosis_analysis.get("clinical_diagnosis", "Unknown"),
                "severity_level": diagnosis_analysis.get("severity_level", -1),
                "confidence_level": diagnosis_analysis.get("confidence_level", "Unknown"),
                "confidence_score": prediction_result.get("confidence", 0.0),
            },
            "clinical_assessment": {
                "urgency_level": diagnosis_analysis.get("urgency", "unknown"),
                "risk_factors": diagnosis_analysis.get("identified_risk_factors", []),
                "quality_assessment": f"{validation.get('quality_score', 0) * 100:.1f}%",
            },
            "recommendations": {
                "immediate_actions": diagnosis_analysis.get("clinical_recommendations", []),
                "follow_up_timeline": diagnosis_analysis.get("recommended_follow_up", "Unknown"),
                "additional_notes": self.get_additional_notes(diagnosis_analysis),
            },
            "technical_details": {
                "image_quality_score": content.get("quality_score", 0.0),
                "model_confidence": content.get("model_confidence", 0.0),
                "processing_validation": "PASS" if validation.get("overall_approval") else "FAIL",
                "validation_checks": validation.get("checks_performed", []),
            },
        }

        return report

    def get_additional_notes(self, diagnosis_analysis):
        """Get additional clinical notes based on diagnosis"""
        severity = diagnosis_analysis.get("severity_level", 0)

        notes = {
            0: ["Maintain regular eye screenings", "Continue diabetes management"],
            1: ["Monitor for vision changes", "Consider nutritional supplements"],
            2: ["Prepare for possible laser treatment", "Monitor blood pressure"],
            3: ["High risk of vision loss", "Immediate intervention needed"],
            4: ["Surgical intervention likely required", "High priority emergency care"],
        }

        return notes.get(severity, ["Consult with healthcare provider"])


