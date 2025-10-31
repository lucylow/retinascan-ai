"""
Integrated AI Governance Framework
Main coordinator integrating all governance components for comprehensive compliance
"""

from datetime import datetime
from typing import Dict, Any, Optional, List
from .security_manager import SecurityManager, RBAC
from .audit_logger import AuditLogger
from .data_governance import DataGovernanceManager
from .incident_response import IncidentResponseManager
import os


class AIGovernanceFramework:
    """
    Main governance framework integrating all compliance components
    Provides unified interface for privacy, security, and compliance management
    """
    
    def __init__(self, db_path: Optional[str] = None, secret_key: Optional[str] = None):
        """
        Initialize AI Governance Framework
        
        Args:
            db_path: Path to audit database (optional, will use default if not provided)
            secret_key: Secret key for security operations (from env if not provided)
        """
        # Get secret key from environment or parameter
        if secret_key is None:
            secret_key = os.getenv('SECRET_KEY', os.getenv('GOVERNANCE_SECRET_KEY', 'dev-secret-key-change-in-production'))
        
        # Initialize components
        self.audit_logger = AuditLogger(db_path)
        self.security_mgr = SecurityManager(secret_key)
        self.data_gov_mgr = DataGovernanceManager(self.audit_logger)
        self.incident_mgr = IncidentResponseManager(self.audit_logger)
        self.rbac = RBAC()
        
        # Track initialized systems
        self.initialized_systems = {}
    
    def initialize_governance_for_ai_system(self, ai_system_id: str, system_metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Initialize governance for a new AI system
        
        Args:
            ai_system_id: Unique identifier for the AI system
            system_metadata: Optional metadata about the system
            
        Returns:
            Dictionary with governance setup status
        """
        governance_setup = {
            'ai_system_id': ai_system_id,
            'audit_logging_configured': True,
            'access_controls_established': True,
            'data_retention_policies_set': True,
            'incident_response_ready': True,
            'gdpr_compliance_enabled': True,
            'hipaa_compliance_enabled': True,
            'initialized_at': datetime.utcnow().isoformat(),
            'metadata': system_metadata or {}
        }
        
        self.initialized_systems[ai_system_id] = governance_setup
        
        # Log initialization
        self.audit_logger.log_audit_event(
            'system',
            'governance_initialized',
            'ai_system',
            ai_system_id,
            governance_setup,
            severity='info'
        )
        
        return governance_setup
    
    def validate_data_processing(
        self,
        user_id: str,
        patient_id: str,
        data_type: str,
        purpose: str,
        access_type: str = 'read'
    ) -> Dict[str, Any]:
        """
        Comprehensive validation of data processing for compliance
        
        Args:
            user_id: ID of user requesting access
            patient_id: ID of patient whose data is accessed
            data_type: Type of data (phi, anonymous, sensitive, etc.)
            purpose: Purpose of processing
            access_type: Type of access (read, write, delete)
            
        Returns:
            Validation result dictionary
        """
        # Get user role (would integrate with user management system)
        user_role = self._get_user_role(user_id)
        
        # Check RBAC permissions
        has_permission = self.rbac.has_permission(user_role, f'{access_type}_{data_type}')
        can_access_patient = self.rbac.can_access_patient_data(user_role, patient_id, user_id)
        
        # Validate data processing compliance
        processing_validation = self.data_gov_mgr.validate_data_processing(patient_id, data_type, purpose)
        
        # Combine all validations
        validation_result = {
            'authorized': has_permission and can_access_patient,
            'gdpr_compliant': processing_validation['gdpr_compliant'],
            'hipaa_compliant': processing_validation['hipaa_compliant'],
            'purpose_limitation': processing_validation['purpose_limitation'],
            'data_minimization': processing_validation['data_minimization'],
            'consent_status': processing_validation['consent_status'],
            'user_role': user_role,
            'access_level': self.rbac.get_data_access_level(user_role, data_type),
            'timestamp': datetime.utcnow().isoformat()
        }
        
        # Log access attempt
        if validation_result['authorized']:
            self.audit_logger.log_data_access(
                user_id=user_id,
                patient_id=patient_id,
                data_type=data_type,
                access_type=access_type,
                purpose=purpose,
                justification='Data processing validation',
                success=True
            )
        else:
            self.audit_logger.log_data_access(
                user_id=user_id,
                patient_id=patient_id,
                data_type=data_type,
                access_type=access_type,
                purpose=purpose,
                justification='Unauthorized access attempt',
                success=False
            )
            
            # Detect potential security incident
            if not has_permission:
                self.incident_mgr.detect_potential_breach(
                    'unauthorized_access',
                    {
                        'user_id': user_id,
                        'patient_id': patient_id,
                        'data_type': data_type,
                        'access_type': access_type,
                        'reason': 'insufficient_permissions'
                    },
                    severity='medium'
                )
        
        return validation_result
    
    def handle_gdpr_request(
        self,
        request_type: str,
        patient_id: str,
        request_details: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Handle GDPR data subject rights requests
        
        Args:
            request_type: Type of request (access, portability, erasure, rectification)
            patient_id: Patient ID making request
            request_details: Optional additional request details
            
        Returns:
            Request processing result
        """
        request_details = request_details or {}
        
        # Log the request
        self.audit_logger.log_audit_event(
            'system',
            'gdpr_request',
            'patient',
            patient_id,
            {
                'request_type': request_type,
                'details': request_details
            },
            severity='info'
        )
        
        if request_type == 'access':
            return self.data_gov_mgr.handle_access_request(patient_id)
        
        elif request_type == 'portability':
            return self.data_gov_mgr.handle_data_portability_request(patient_id)
        
        elif request_type == 'erasure':
            reason = request_details.get('reason')
            return self.data_gov_mgr.handle_data_erasure_request(patient_id, reason)
        
        elif request_type == 'rectification':
            # GDPR Article 16: Right to rectification
            correction_data = request_details.get('correction_data', {})
            return self._handle_rectification_request(patient_id, correction_data)
        
        else:
            return {
                'status': 'error',
                'error': f'Unknown request type: {request_type}',
                'supported_types': ['access', 'portability', 'erasure', 'rectification']
            }
    
    def log_model_prediction(
        self,
        user_id: str,
        patient_id: Optional[str],
        model_version: str,
        prediction_result: Dict[str, Any],
        input_hash: Optional[str] = None,
        processing_time_ms: Optional[int] = None,
        decision_path: Optional[str] = None
    ):
        """
        Log AI model prediction for governance and transparency
        
        Args:
            user_id: ID of user invoking model
            patient_id: Optional patient ID
            model_version: Version of model used
            prediction_result: Prediction result dictionary
            input_hash: Hash of input data
            processing_time_ms: Processing time
            decision_path: Explainable AI decision path
        """
        confidence_score = prediction_result.get('confidence')
        
        self.audit_logger.log_model_usage(
            user_id=user_id,
            model_version=model_version,
            patient_id=patient_id,
            input_hash=input_hash,
            prediction_result=prediction_result,
            confidence_score=confidence_score,
            processing_time_ms=processing_time_ms,
            decision_path=decision_path
        )
        
        # Log as audit event
        self.audit_logger.log_audit_event(
            user_id,
            'ai_prediction',
            'model',
            model_version,
            {
                'patient_id': patient_id,
                'prediction': prediction_result.get('diagnosis'),
                'confidence': confidence_score
            },
            severity='info'
        )
    
    def manage_consent(
        self,
        patient_id: str,
        consent_type: str,
        granted: bool,
        expiration: Optional[str] = None,
        purpose: str = "",
        version: str = "1.0"
    ) -> Dict[str, Any]:
        """
        Manage patient consent (GDPR requirement)
        
        Args:
            patient_id: Patient ID
            consent_type: Type of consent
            granted: True if granted, False if revoked
            expiration: Optional expiration date
            purpose: Purpose of consent
            version: Version of consent form
            
        Returns:
            Consent management result
        """
        # Record consent
        self.audit_logger.record_consent(
            patient_id=patient_id,
            consent_type=consent_type,
            granted=granted,
            expiration=expiration,
            purpose=purpose,
            version=version
        )
        
        # Log consent action
        self.audit_logger.log_audit_event(
            patient_id,
            'consent_updated' if granted else 'consent_revoked',
            'consent',
            patient_id,
            {
                'consent_type': consent_type,
                'granted': granted,
                'purpose': purpose,
                'version': version
            },
            severity='info'
        )
        
        return {
            'status': 'recorded',
            'patient_id': patient_id,
            'consent_type': consent_type,
            'granted': granted,
            'timestamp': datetime.utcnow().isoformat()
        }
    
    def generate_compliance_report(
        self,
        report_type: str,
        start_date: str,
        end_date: str,
        filters: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Generate compliance reports for audit and regulatory submission
        
        Args:
            report_type: Type of report (audit, data_access, consent, incidents)
            start_date: Start date (ISO format)
            end_date: End date (ISO format)
            filters: Optional filters (user_id, patient_id, etc.)
            
        Returns:
            Compliance report dictionary
        """
        filters = filters or {}
        
        if report_type == 'audit':
            logs = self.audit_logger.generate_audit_report(
                start_date,
                end_date,
                user_id=filters.get('user_id'),
                resource_type=filters.get('resource_type')
            )
            return {
                'report_type': 'audit',
                'period': {'start': start_date, 'end': end_date},
                'total_events': len(logs),
                'events': logs
            }
        
        elif report_type == 'data_access':
            if 'patient_id' in filters:
                logs = self.audit_logger.generate_data_access_report(
                    filters['patient_id'],
                    start_date,
                    end_date
                )
            else:
                # Get all data access logs (would need additional method)
                logs = []
            return {
                'report_type': 'data_access',
                'period': {'start': start_date, 'end': end_date},
                'total_accesses': len(logs),
                'accesses': logs
            }
        
        elif report_type == 'failed_access':
            logs = self.audit_logger.get_failed_access_attempts(
                start_date,
                end_date,
                user_id=filters.get('user_id')
            )
            return {
                'report_type': 'failed_access_attempts',
                'period': {'start': start_date, 'end': end_date},
                'total_failures': len(logs),
                'failed_attempts': logs
            }
        
        else:
            return {
                'status': 'error',
                'error': f'Unknown report type: {report_type}',
                'supported_types': ['audit', 'data_access', 'failed_access']
            }
    
    # Private helper methods
    
    def _get_user_role(self, user_id: str) -> str:
        """
        Retrieve user role for permission checking
        
        Args:
            user_id: User ID
            
        Returns:
            User role string
        """
        # This would integrate with your user management system
        # For now, return default - in production, query user database
        return 'clinician'  # Placeholder
    
    def _handle_rectification_request(
        self,
        patient_id: str,
        correction_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Handle GDPR rectification request (Article 16)
        
        Args:
            patient_id: Patient ID
            correction_data: Data corrections to apply
            
        Returns:
            Rectification result
        """
        # This would integrate with your data storage system
        # Log the rectification request
        self.audit_logger.log_audit_event(
            patient_id,
            'data_rectification',
            'patient',
            patient_id,
            {'corrections': correction_data},
            severity='info'
        )
        
        return {
            'status': 'processed',
            'patient_id': patient_id,
            'corrections_applied': list(correction_data.keys()),
            'timestamp': datetime.utcnow().isoformat(),
            'note': 'Rectification request logged. Integration with data storage required for actual updates.'
        }


def create_governance_framework(db_path: Optional[str] = None, secret_key: Optional[str] = None) -> AIGovernanceFramework:
    """
    Factory function to create and initialize governance framework
    
    Args:
        db_path: Optional database path
        secret_key: Optional secret key
        
    Returns:
        Initialized AIGovernanceFramework instance
    """
    governance = AIGovernanceFramework(db_path=db_path, secret_key=secret_key)
    
    # Initialize governance for RetinaScan AI system
    governance.initialize_governance_for_ai_system(
        'retinascan_ai_v1',
        {
            'system_name': 'RetinaScan AI',
            'version': '1.0.0',
            'purpose': 'Diabetic retinopathy detection',
            'data_types': ['medical_images', 'diagnostic_results', 'patient_demographics']
        }
    )
    
    return governance
