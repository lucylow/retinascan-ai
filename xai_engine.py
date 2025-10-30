import base64
from dataclasses import dataclass
from io import BytesIO
from typing import Any, Dict, List, Tuple

import cv2
import numpy as np
import tensorflow as tf

import matplotlib

# Use non-interactive backend for server environments
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns  # noqa: F401 (kept for potential future use/consistency)


@dataclass
class ExplanationResult:
    """Comprehensive explanation results"""
    confidence_scores: Dict[str, float]
    feature_importance: Dict[str, float]
    heatmap_data: str  # Base64 encoded
    decision_factors: List[Dict[str, Any]]
    clinical_evidence: List[Dict[str, Any]]
    uncertainty_metrics: Dict[str, float]
    alternative_diagnoses: List[Dict[str, Any]]


class XAIEngine:
    """Explainable AI Engine for transparent decision-making"""

    def __init__(self, model):
        self.model = model
        self.feature_descriptions = self._load_feature_descriptions()
        self.clinical_evidence_db = self._load_clinical_evidence()

    def _load_feature_descriptions(self):
        """Load medical descriptions of retinal features"""
        return {
            'microaneurysms': {
                'description': 'Small red dots representing dilated capillaries',
                'clinical_significance': 'Earliest sign of diabetic retinopathy',
                'appearance': 'Round, red dots 15-60 microns in diameter',
                'severity_implication': 'Mild non-proliferative DR'
            },
            'hemorrhages': {
                'description': 'Larger red spots from ruptured blood vessels',
                'clinical_significance': 'Progressive vascular damage',
                'appearance': 'Flame-shaped or blot-shaped red lesions',
                'severity_implication': 'Moderate to severe DR'
            },
            'cotton_wool_spots': {
                'description': 'White fluffy patches indicating nerve fiber layer infarction',
                'clinical_significance': 'Retinal ischemia',
                'appearance': 'White, fluffy lesions with fuzzy edges',
                'severity_implication': 'Moderate to severe DR'
            },
            'hard_exudates': {
                'description': 'Yellow-white deposits of lipid and protein',
                'clinical_significance': 'Chronic vascular leakage',
                'appearance': 'Yellow, waxy lesions with sharp margins',
                'severity_implication': 'Chronic edema'
            },
            'neovascularization': {
                'description': 'Abnormal new blood vessel growth',
                'clinical_significance': 'Advanced proliferative DR',
                'appearance': 'Fine, irregular vessels on retina or optic disc',
                'severity_implication': 'Proliferative DR - High risk'
            }
        }

    def _load_clinical_evidence(self):
        """Load evidence-based clinical guidelines"""
        return {
            'mild_dr': {
                'criteria': ['Microaneurysms present'],
                'evidence_level': 'Strong',
                'references': ['ETDRS Study Group, 1991'],
                'treatment_guidelines': ['Annual screening', 'Glycemic control']
            },
            'moderate_dr': {
                'criteria': ['Microaneurysms', 'Hemorrhages', 'Cotton wool spots'],
                'evidence_level': 'Strong',
                'references': ['AAO Preferred Practice Pattern, 2019'],
                'treatment_guidelines': ['6-12 month follow-up', 'Consider laser treatment']
            },
            'severe_dr': {
                'criteria': ['Extensive hemorrhages', 'Venous beading', 'IRMAs'],
                'evidence_level': 'Strong',
                'references': ['DRCR.net Protocol S, 2015'],
                'treatment_guidelines': ['Prompt laser treatment', 'Close monitoring']
            },
            'pdr': {
                'criteria': ['Neovascularization', 'Vitreous hemorrhage'],
                'evidence_level': 'Strong',
                'references': ['DRCR.net Protocol S, 2015'],
                'treatment_guidelines': ['Immediate laser treatment', 'Anti-VEGF therapy']
            }
        }

    def generate_grad_cam_heatmap(self, image, layer_name='conv5_block3_out'):
        """Generate Grad-CAM heatmap for visual explanations"""

        grad_model = tf.keras.models.Model(
            inputs=[self.model.inputs],
            outputs=[self.model.get_layer(layer_name).output, self.model.output]
        )

        with tf.GradientTape() as tape:
            conv_outputs, predictions = grad_model(image)
            class_idx = tf.argmax(predictions[0])
            loss = predictions[:, class_idx]

        grads = tape.gradient(loss, conv_outputs)
        pooled_grads = tf.reduce_mean(grads, axis=(0, 1, 2))

        conv_outputs = conv_outputs[0]
        heatmap = tf.reduce_mean(tf.multiply(pooled_grads, conv_outputs), axis=-1)

        heatmap = tf.maximum(heatmap, 0)
        heatmap /= tf.reduce_max(heatmap)

        return heatmap.numpy()

    def generate_explanation(self, image, prediction, original_image, patient_context=None):
        """Generate comprehensive explanation for AI decision"""

        heatmap = self.generate_grad_cam_heatmap(image)
        feature_importance = self._analyze_feature_importance(heatmap, original_image)
        decision_factors = self._extract_decision_factors(prediction, feature_importance)
        uncertainty_metrics = self._calculate_uncertainty(prediction)
        alternative_diagnoses = self._generate_alternative_diagnoses(prediction)
        clinical_evidence = self._generate_clinical_evidence(prediction, decision_factors)
        heatmap_viz = self._create_heatmap_visualization(original_image, heatmap)

        return ExplanationResult(
            confidence_scores=prediction['probabilities'],
            feature_importance=feature_importance,
            heatmap_data=heatmap_viz,
            decision_factors=decision_factors,
            clinical_evidence=clinical_evidence,
            uncertainty_metrics=uncertainty_metrics,
            alternative_diagnoses=alternative_diagnoses
        )

    def _analyze_feature_importance(self, heatmap, original_image):
        """Analyze which retinal features contributed to decision"""

        feature_scores = {}

        h, w = heatmap.shape
        regions = {
            'macula_region': heatmap[h//3:2*h//3, w//3:2*w//3],
            'optic_disc_region': heatmap[:h//3, :w//3],
            'temporal_region': heatmap[h//3:2*h//3, 2*w//3:],
            'nasal_region': heatmap[h//3:2*h//3, :w//3],
            'superior_region': heatmap[:h//3, w//3:2*w//3],
            'inferior_region': heatmap[2*h//3:, w//3:2*w//3]
        }

        for region_name, region_heatmap in regions.items():
            feature_scores[region_name] = float(np.mean(region_heatmap))

        clinical_feature_importance = {
            'microaneurysms': feature_scores['macula_region'] * 0.8,
            'hemorrhages': max(feature_scores['superior_region'], feature_scores['inferior_region']),
            'cotton_wool_spots': feature_scores['optic_disc_region'] * 0.6,
            'hard_exudates': feature_scores['macula_region'] * 0.7,
            'neovascularization': feature_scores['optic_disc_region'] * 0.9
        }

        return clinical_feature_importance

    def _extract_decision_factors(self, prediction, feature_importance):
        """Extract key factors that influenced the decision"""

        factors = []
        severity = prediction['severity_level']
        confidence = prediction['confidence']

        factors.append({
            'factor': 'Primary Diagnosis',
            'value': prediction['diagnosis'],
            'influence': 'High',
            'explanation': f"Model identified features consistent with {prediction['diagnosis']}",
            'confidence': confidence
        })

        top_features = sorted(feature_importance.items(), key=lambda x: x[1], reverse=True)[:3]

        for feature, score in top_features:
            if score > 0.1:
                feature_info = self.feature_descriptions.get(feature, {})
                factors.append({
                    'factor': feature.replace('_', ' ').title(),
                    'value': f'Detected (score: {score:.2f})',
                    'influence': 'High' if score > 0.5 else 'Medium',
                    'explanation': feature_info.get('description', 'Feature detected in retinal image'),
                    'clinical_significance': feature_info.get('clinical_significance', '')
                })

        if confidence < 0.7:
            factors.append({
                'factor': 'Decision Confidence',
                'value': f'Moderate ({confidence:.1%})',
                'influence': 'Medium',
                'explanation': 'Lower confidence suggests potential uncertainty; human review recommended',
                'clinical_significance': 'May require additional imaging or expert consultation'
            })

        if severity >= 3:
            factors.append({
                'factor': 'Disease Severity',
                'value': 'High',
                'influence': 'Critical',
                'explanation': 'Advanced disease stage detected requiring immediate attention',
                'clinical_significance': 'Urgent intervention needed to prevent vision loss'
            })

        return factors

    def _calculate_uncertainty(self, prediction):
        """Calculate various uncertainty metrics"""

        probabilities = list(prediction['probabilities'].values())

        entropy = -sum(p * np.log(p + 1e-10) for p in probabilities)
        max_entropy = np.log(len(probabilities))
        normalized_entropy = entropy / max_entropy

        sorted_probs = sorted(probabilities, reverse=True)
        confidence_gap = sorted_probs[0] - sorted_probs[1] if len(sorted_probs) > 1 else 1.0

        return {
            'prediction_entropy': float(normalized_entropy),
            'confidence_gap': float(confidence_gap),
            'top_class_confidence': float(prediction['confidence']),
            'uncertainty_level': 'Low' if normalized_entropy < 0.3 else 'Medium' if normalized_entropy < 0.6 else 'High'
        }

    def _generate_alternative_diagnoses(self, prediction):
        """Generate alternative possible diagnoses"""

        probabilities = prediction['probabilities']
        sorted_diagnoses = sorted(probabilities.items(), key=lambda x: x[1], reverse=True)

        alternatives = []
        for i, (diagnosis, prob) in enumerate(sorted_diagnoses[1:4]):
            if prob > 0.1:
                alternatives.append({
                    'diagnosis': diagnosis,
                    'probability': prob,
                    'confidence': 'High' if prob > 0.3 else 'Medium' if prob > 0.15 else 'Low',
                    'reasoning': self._get_alternative_reasoning(diagnosis, prediction)
                })

        return alternatives

    def _get_alternative_reasoning(self, alternative_diagnosis, prediction):
        """Provide reasoning for alternative diagnoses"""

        reasoning_map = {
            'No Diabetic Retinopathy': 'Minimal retinal changes detected',
            'Mild Diabetic Retinopathy': 'Early microvascular changes present',
            'Moderate Diabetic Retinopathy': 'Multiple hemorrhages and/or cotton wool spots',
            'Severe Diabetic Retinopathy': 'Extensive retinal changes without neovascularization',
            'Proliferative Diabetic Retinopathy': 'Signs of neovascularization detected'
        }

        return reasoning_map.get(alternative_diagnosis, 'Similar retinal features present')

    def _generate_clinical_evidence(self, prediction, decision_factors):
        """Generate evidence-based clinical support"""

        severity_level = prediction['severity_level']
        evidence_key = ['mild_dr', 'moderate_dr', 'severe_dr', 'pdr'][min(severity_level, 3)]

        evidence = self.clinical_evidence_db.get(evidence_key, {})

        clinical_evidence = []

        for criterion in evidence.get('criteria', []):
            clinical_evidence.append({
                'type': 'Diagnostic Criterion',
                'content': criterion,
                'met': any(criterion.lower() in factor['factor'].lower() for factor in decision_factors),
                'importance': 'Required'
            })

        clinical_evidence.append({
            'type': 'Evidence Level',
            'content': f"{evidence.get('evidence_level', 'Not specified')} evidence",
            'met': True,
            'importance': 'Validation'
        })

        for ref in evidence.get('references', []):
            clinical_evidence.append({
                'type': 'Clinical Reference',
                'content': ref,
                'met': True,
                'importance': 'Supporting'
            })

        return clinical_evidence

    def _create_heatmap_visualization(self, original_image, heatmap):
        """Create heatmap visualization overlay"""

        heatmap_resized = cv2.resize(heatmap, (original_image.shape[1], original_image.shape[0]))

        heatmap_colored = np.uint8(255 * heatmap_resized)
        heatmap_colored = cv2.applyColorMap(heatmap_colored, cv2.COLORMAP_JET)

        # Ensure original image is in BGR uint8
        if original_image.dtype != np.uint8:
            original_uint8 = np.clip(original_image, 0, 255).astype(np.uint8)
        else:
            original_uint8 = original_image

        superimposed = cv2.addWeighted(original_uint8, 0.6, heatmap_colored, 0.4, 0)

        plt.figure(figsize=(12, 4))

        plt.subplot(1, 3, 1)
        plt.imshow(cv2.cvtColor(original_uint8, cv2.COLOR_BGR2RGB))
        plt.title('Original Retinal Image')
        plt.axis('off')

        plt.subplot(1, 3, 2)
        plt.imshow(heatmap_resized, cmap='jet')
        plt.title('AI Attention Heatmap')
        plt.axis('off')
        plt.colorbar()

        plt.subplot(1, 3, 3)
        plt.imshow(cv2.cvtColor(superimposed, cv2.COLOR_BGR2RGB))
        plt.title('AI Explanation Overlay')
        plt.axis('off')

        buffer = BytesIO()
        plt.tight_layout()
        plt.savefig(buffer, format='png', dpi=150, bbox_inches='tight')
        buffer.seek(0)

        image_base64 = base64.b64encode(buffer.getvalue()).decode()
        plt.close()

        return f"data:image/png;base64,{image_base64}"

    def generate_patient_explanation(self, explanation_result, language='english'):
        """Generate patient-friendly explanation"""

        diagnosis = next((f['value'] for f in explanation_result.decision_factors
                          if f['factor'] == 'Primary Diagnosis'), 'Unknown')

        patient_explanation = {
            'main_message': self._get_patient_main_message(diagnosis),
            'what_this_means': self._get_what_this_means(diagnosis),
            'next_steps': self._get_patient_next_steps(diagnosis),
            'key_findings': self._simplify_findings(explanation_result.decision_factors),
            'urgency_level': self._get_patient_urgency(diagnosis),
            'questions_for_doctor': self._get_patient_questions(diagnosis)
        }

        return patient_explanation

    def _get_patient_main_message(self, diagnosis):
        """Get main message for patient"""

        messages = {
            'No Diabetic Retinopathy': "Good news! No signs of diabetic eye disease were found.",
            'Mild Diabetic Retinopathy': "Early signs of diabetic eye changes were detected.",
            'Moderate Diabetic Retinopathy': "Moderate diabetic eye changes were found.",
            'Severe Diabetic Retinopathy': "Significant diabetic eye changes requiring attention were detected.",
            'Proliferative Diabetic Retinopathy': "Advanced diabetic eye disease requiring immediate care was found."
        }

        return messages.get(diagnosis, "Your retinal screening results are ready.")

    def _get_what_this_means(self, diagnosis):
        """Explain what the diagnosis means in simple terms"""

        explanations = {
            'No Diabetic Retinopathy': "Your retina appears healthy with no damage from diabetes. Continue with regular annual screenings.",
            'Mild Diabetic Retinopathy': "Small changes in your retina's blood vessels were found. These are early warning signs.",
            'Moderate Diabetic Retinopathy': "More noticeable changes are present. Some blood vessels may be blocked or leaking.",
            'Severe Diabetic Retinopathy': "Many blood vessels are blocked, reducing blood flow to the retina.",
            'Proliferative Diabetic Retinopathy': "Your retina is growing new, fragile blood vessels that can bleed and cause vision loss."
        }

        return explanations.get(diagnosis, "Please consult with your eye doctor for detailed explanation.")

    def _get_patient_next_steps(self, diagnosis):
        """Provide clear next steps for patients"""

        steps = {
            'No Diabetic Retinopathy': [
                "Continue annual eye screenings",
                "Maintain good blood sugar control",
                "Schedule next screening in 12 months"
            ],
            'Mild Diabetic Retinopathy': [
                "Consult with an eye specialist within 6-12 months",
                "Optimize diabetes management",
                "Monitor for vision changes"
            ],
            'Moderate Diabetic Retinopathy': [
                "See an ophthalmologist within 3-6 months",
                "Discuss treatment options",
                "Consider more frequent monitoring"
            ],
            'Severe Diabetic Retinopathy': [
                "Urgent ophthalmology consultation within 1 month",
                "Prepare for possible laser treatment",
                "Close monitoring essential"
            ],
            'Proliferative Diabetic Retinopathy': [
                "EMERGENCY: See eye specialist immediately",
                "Laser treatment likely needed",
                "High risk of vision loss without treatment"
            ]
        }

        return steps.get(diagnosis, ["Consult with your healthcare provider"])

    def _simplify_findings(self, decision_factors):
        """Simplify medical findings for patients"""

        simplified = []
        for factor in decision_factors[:3]:
            if factor['factor'] != 'Primary Diagnosis':
                simple_desc = factor['explanation'].split('.')[0]
                simplified.append({
                    'finding': factor['factor'],
                    'description': simple_desc,
                    'significance': factor.get('clinical_significance', '')
                })

        return simplified

    def _get_patient_urgency(self, diagnosis):
        """Determine urgency level for patient communication"""

        urgency_map = {
            'No Diabetic Retinopathy': 'Routine',
            'Mild Diabetic Retinopathy': 'Non-urgent',
            'Moderate Diabetic Retinopathy': 'Semi-urgent',
            'Severe Diabetic Retinopathy': 'Urgent',
            'Proliferative Diabetic Retinopathy': 'Emergency'
        }

        return urgency_map.get(diagnosis, 'Consult doctor')

    def _get_patient_questions(self, diagnosis):
        """Suggest questions patients should ask their doctor"""

        questions = {
            'No Diabetic Retinopathy': [
                "How often should I get screened?",
                "What can I do to prevent eye problems?"
            ],
            'Mild Diabetic Retinopathy': [
                "What do these early changes mean?",
                "Should I make any lifestyle changes?",
                "When should I come back for follow-up?"
            ],
            'Moderate Diabetic Retinopathy': [
                "What treatments are available?",
                "Will this affect my vision?",
                "How can I slow the progression?"
            ],
            'Severe Diabetic Retinopathy': [
                "What is the risk to my vision?",
                "What treatment do I need now?",
                "How quickly should I be treated?"
            ],
            'Proliferative Diabetic Retinopathy': [
                "What is the immediate risk to my sight?",
                "What emergency treatments are available?",
                "What are the treatment success rates?"
            ]
        }

        return questions.get(diagnosis, [
            "What does this diagnosis mean?",
            "What are my next steps?"
        ])


