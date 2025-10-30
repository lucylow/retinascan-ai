"""
Clinical Workflow Manager for RetinaScan AI
Manages end-to-end clinical workflows with EHR integration
"""
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class WorkflowStep(Enum):
    PATIENT_CHECK_IN = "patient_check_in"
    IMAGE_CAPTURE = "image_capture"
    AI_ANALYSIS = "ai_analysis"
    RESULTS_REVIEW = "results_review"
    EHR_INTEGRATION = "ehr_integration"
    REFERRAL_MANAGEMENT = "referral_management"
    FOLLOW_UP_SCHEDULING = "follow_up_scheduling"


class ClinicalWorkflowManager:
    """Manage clinical workflow integration"""
    
    def __init__(self, fhir_service, hl7_service):
        self.fhir_service = fhir_service
        self.hl7_service = hl7_service
        self.workflow_states = {}
        self.audit_log = []
    
    async def process_screening_workflow(self, patient_id: str, image_data: str, 
                                       workflow_config: Dict) -> Dict:
        """Process complete screening workflow"""
        
        workflow_id = f"workflow-{datetime.now().strftime('%Y%m%d-%H%M%S')}-{patient_id}"
        
        try:
            # Step 1: Patient context validation
            await self._log_workflow_step(workflow_id, WorkflowStep.PATIENT_CHECK_IN, "started")
            patient_data = await self._validate_patient_context(patient_id)
            await self._log_workflow_step(workflow_id, WorkflowStep.PATIENT_CHECK_IN, "completed")
            
            # Step 2: AI Analysis (simulated - would call your AI system)
            await self._log_workflow_step(workflow_id, WorkflowStep.AI_ANALYSIS, "started")
            ai_result = await self._perform_ai_analysis(image_data, patient_data)
            await self._log_workflow_step(workflow_id, WorkflowStep.AI_ANALYSIS, "completed")
            
            # Step 3: Results review
            await self._log_workflow_step(workflow_id, WorkflowStep.RESULTS_REVIEW, "started")
            reviewed_result = await self._review_results(ai_result, workflow_config)
            await self._log_workflow_step(workflow_id, WorkflowStep.RESULTS_REVIEW, "completed")
            
            # Step 4: EHR Integration
            await self._log_workflow_step(workflow_id, WorkflowStep.EHR_INTEGRATION, "started")
            ehr_result = await self._integrate_with_ehr(reviewed_result, image_data, patient_id)
            await self._log_workflow_step(workflow_id, WorkflowStep.EHR_INTEGRATION, "completed")
            
            # Step 5: Referral management if needed
            if reviewed_result.get('severity_level', 0) >= 2:
                await self._log_workflow_step(workflow_id, WorkflowStep.REFERRAL_MANAGEMENT, "started")
                referral_result = await self._manage_referral(reviewed_result, patient_data)
                await self._log_workflow_step(workflow_id, WorkflowStep.REFERRAL_MANAGEMENT, "completed")
            
            # Step 6: Follow-up scheduling
            await self._log_workflow_step(workflow_id, WorkflowStep.FOLLOW_UP_SCHEDULING, "started")
            follow_up_result = await self._schedule_follow_up(reviewed_result, patient_data)
            await self._log_workflow_step(workflow_id, WorkflowStep.FOLLOW_UP_SCHEDULING, "completed")
            
            return {
                'workflow_id': workflow_id,
                'success': True,
                'patient_data': patient_data,
                'ai_result': reviewed_result,
                'ehr_integration': ehr_result,
                'referral_created': reviewed_result.get('severity_level', 0) >= 2,
                'follow_up_scheduled': follow_up_result.get('scheduled', False),
                'completion_time': datetime.now().isoformat()
            }
            
        except Exception as e:
            await self._log_workflow_error(workflow_id, str(e))
            return {
                'workflow_id': workflow_id,
                'success': False,
                'error': str(e),
                'completion_time': datetime.now().isoformat()
            }
    
    async def _validate_patient_context(self, patient_id: str) -> Dict:
        """Validate patient context and retrieve data"""
        
        demographics = self.fhir_service.get_patient_demographics(patient_id)
        conditions = self.fhir_service.get_patient_conditions(patient_id)
        
        if not demographics:
            raise Exception("Failed to retrieve patient demographics")
        
        # Check for diabetes condition
        diabetes_conditions = [
            cond for cond in conditions 
            if any('diabetes' in cond.get('display', '').lower() 
                  or 'E11' in cond.get('code', '')  # ICD-10 for diabetes
                  for coding in cond.get('codings', []))
        ]
        
        return {
            **demographics,
            'diabetes_conditions': diabetes_conditions,
            'has_diabetes': len(diabetes_conditions) > 0
        }
    
    async def _perform_ai_analysis(self, image_data: str, patient_data: Dict) -> Dict:
        """Perform AI analysis (integrate with your AI system)"""
        
        # This would call your actual AI model
        # Returning structure compatible with your existing prediction service
        return {
            'diagnosis': 'Moderate Diabetic Retinopathy',
            'severity_level': 2,
            'confidence': 0.87,
            'quality_score': 0.92,
            'recommendation': 'Refer to ophthalmologist within 3-6 months',
            'key_findings': ['Microaneurysms', 'Hemorrhages present'],
            'risk_factors': ['Diabetes duration >5 years']
        }
    
    async def _review_results(self, ai_result: Dict, workflow_config: Dict) -> Dict:
        """Review results based on confidence and workflow rules"""
        
        confidence = ai_result.get('confidence', 0)
        severity = ai_result.get('severity_level', 0)
        
        # Auto-approval rules
        if (confidence >= workflow_config.get('auto_approve_confidence', 0.9) and 
            severity <= workflow_config.get('auto_approve_max_severity', 1)):
            
            ai_result['review_status'] = 'auto_approved'
            ai_result['reviewed_by'] = 'system'
            ai_result['review_timestamp'] = datetime.now().isoformat()
            
        else:
            # Flag for human review
            ai_result['review_status'] = 'pending_review'
            ai_result['needs_human_review'] = True
            ai_result['review_reason'] = 'Low confidence or high severity'
        
        return ai_result
    
    async def _integrate_with_ehr(self, ai_result: Dict, image_data: str, 
                                patient_id: str) -> Dict:
        """Integrate results with EHR system"""
        
        # Try FHIR first
        fhir_result = self.fhir_service.submit_ai_results_to_ehr(
            ai_result, image_data, patient_id
        )
        
        if fhir_result['success']:
            return {
                'method': 'fhir',
                'success': True,
                'observation_id': fhir_result.get('observation_id'),
                'report_id': fhir_result.get('report_id')
            }
        else:
            # Fallback to HL7 v2
            patient_data = self.fhir_service.get_patient_demographics(patient_id)
            hl7_message = self.hl7_service.create_adt_message('A08', patient_data, ai_result)
            hl7_result = self.hl7_service.send_hl7_message(hl7_message)
            
            return {
                'method': 'hl7v2',
                'success': hl7_result['success'],
                'message_control_id': hl7_result.get('message_control_id')
            }
    
    async def _manage_referral(self, ai_result: Dict, patient_data: Dict) -> Dict:
        """Manage specialist referral based on results"""
        
        severity = ai_result.get('severity_level', 0)
        
        if severity >= 3:
            priority = 'urgent'
            timeline = 'within 1 month'
        elif severity == 2:
            priority = 'semi-urgent' 
            timeline = 'within 3-6 months'
        else:
            return {'referral_created': False}
        
        # In production, would create referral order in EHR
        logger.info(f"Referral created: {priority}, timeline: {timeline}")
        
        return {
            'referral_created': True,
            'priority': priority,
            'timeline': timeline,
            'specialty': 'ophthalmology'
        }
    
    async def _schedule_follow_up(self, ai_result: Dict, patient_data: Dict) -> Dict:
        """Schedule appropriate follow-up based on results"""
        
        severity = ai_result.get('severity_level', 0)
        
        follow_up_intervals = {
            0: 12,  # No DR: 12 months
            1: 6,   # Mild: 6 months
            2: 3,   # Moderate: 3 months
            3: 1,   # Severe: 1 month
            4: 0    # PDR: immediate
        }
        
        months = follow_up_intervals.get(severity, 12)
        
        if months > 0:
            follow_up_date = datetime.now() + timedelta(days=months*30)
            
            return {
                'scheduled': True,
                'follow_up_months': months,
                'suggested_date': follow_up_date.strftime('%Y-%m-%d'),
                'reason': f"Diabetic retinopathy follow-up - {ai_result.get('diagnosis')}"
            }
        else:
            return {'scheduled': False}
    
    async def _log_workflow_step(self, workflow_id: str, step: WorkflowStep, status: str):
        """Log workflow step for audit trail"""
        
        log_entry = {
            'workflow_id': workflow_id,
            'step': step.value,
            'status': status,
            'timestamp': datetime.now().isoformat(),
            'duration': None
        }
        
        self.audit_log.append(log_entry)
        logger.info(f"Workflow {workflow_id}: {step.value} {status}")
    
    async def _log_workflow_error(self, workflow_id: str, error: str):
        """Log workflow error"""
        
        error_entry = {
            'workflow_id': workflow_id,
            'error': error,
            'timestamp': datetime.now().isoformat(),
            'severity': 'high'
        }
        
        self.audit_log.append(error_entry)
        logger.error(f"Workflow {workflow_id} error: {error}")
    
    def get_workflow_audit_trail(self, workflow_id: str) -> List[Dict]:
        """Get audit trail for specific workflow"""
        
        return [entry for entry in self.audit_log if entry.get('workflow_id') == workflow_id]
    
    def get_workflow_metrics(self, time_period: str = 'day') -> Dict:
        """Get workflow performance metrics"""
        
        now = datetime.now()
        if time_period == 'day':
            start_time = now.replace(hour=0, minute=0, second=0, microsecond=0)
        elif time_period == 'week':
            start_time = now - timedelta(days=7)
        else:  # month
            start_time = now - timedelta(days=30)
        
        period_logs = [
            entry for entry in self.audit_log
            if datetime.fromisoformat(entry['timestamp']) >= start_time
        ]
        
        completed_workflows = set(
            entry['workflow_id'] for entry in period_logs 
            if entry.get('step') == WorkflowStep.FOLLOW_UP_SCHEDULING.value and 
            entry.get('status') == 'completed'
        )
        
        failed_workflows = set(
            entry['workflow_id'] for entry in period_logs 
            if 'error' in entry
        )
        
        total_workflows = len(completed_workflows) + len(failed_workflows)
        
        return {
            'time_period': time_period,
            'total_workflows': total_workflows,
            'completed_workflows': len(completed_workflows),
            'failed_workflows': len(failed_workflows),
            'success_rate': len(completed_workflows) / total_workflows if total_workflows > 0 else 0,
            'common_errors': self._analyze_common_errors(period_logs)
        }
    
    def _analyze_common_errors(self, logs: List[Dict]) -> List[Dict]:
        """Analyze common workflow errors"""
        
        errors = [entry for entry in logs if 'error' in entry]
        error_counts = {}
        
        for error in errors:
            error_msg = error['error']
            error_counts[error_msg] = error_counts.get(error_msg, 0) + 1
        
        return [
            {'error': error, 'count': count}
            for error, count in sorted(error_counts.items(), key=lambda x: x[1], reverse=True)
        ]

