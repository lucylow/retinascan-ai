"""
Data Governance Manager
Handles GDPR data subject rights, consent management, and data lifecycle
"""

from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
from .audit_logger import AuditLogger
import json
import hashlib


class DataGovernanceManager:
    """
    Manages data lifecycle and GDPR individual rights requests
    Implements data minimization, retention, and subject rights
    """
    
    def __init__(self, audit_logger: AuditLogger):
        """
        Initialize DataGovernanceManager
        
        Args:
            audit_logger: AuditLogger instance for logging operations
        """
        self.audit_logger = audit_logger
        # GDPR retention periods (in days) - configurable per data type
        self.retention_periods = {
            'medical_records': 2555,  # 7 years (common medical record retention)
            'diagnostic_images': 1825,  # 5 years
            'ai_predictions': 365,  # 1 year
            'audit_logs': 2555,  # 7 years (HIPAA requirement)
            'consent_records': 2555,  # 7 years
            'anonymized_research': None  # Indefinite if properly anonymized
        }
    
    def handle_data_erasure_request(self, patient_id: str, reason: Optional[str] = None) -> Dict[str, Any]:
        """
        Handle GDPR Right to Erasure (Right to be Forgotten)
        
        Note: For medical records, complete deletion may not be legally permissible.
        This implementation pseudonymizes/anonymizes data while retaining medical integrity.
        
        Args:
            patient_id: Patient ID requesting erasure
            reason: Optional reason for erasure request
            
        Returns:
            Dictionary with erasure status and actions taken
        """
        # Check for valid legal basis to deny complete erasure (medical records)
        # GDPR Article 17(3) allows exceptions for health data
        
        erasure_actions = []
        
        # 1. Anonymize demographics while retaining medical value
        demographics_result = self._anonymize_demographics(patient_id)
        erasure_actions.append({
            'action': 'anonymize_demographics',
            'status': 'completed',
            'result': demographics_result
        })
        
        # 2. Remove direct contact information
        contact_result = self._remove_contact_information(patient_id)
        erasure_actions.append({
            'action': 'remove_contact_information',
            'status': 'completed',
            'result': contact_result
        })
        
        # 3. Retain medical records in anonymized form (legally required)
        medical_result = self._retain_medical_records_anonymized(patient_id)
        erasure_actions.append({
            'action': 'anonymize_medical_records',
            'status': 'completed',
            'result': medical_result,
            'note': 'Medical records retained in anonymized form per GDPR Article 17(3)'
        })
        
        # 4. Revoke all active consents
        consent_revocation = self._revoke_all_consents(patient_id)
        erasure_actions.append({
            'action': 'revoke_consents',
            'status': 'completed',
            'result': consent_revocation
        })
        
        # Log the erasure request
        self.audit_logger.log_audit_event(
            'system',
            'data_erasure_request',
            'patient',
            patient_id,
            {
                'actions_taken': erasure_actions,
                'timestamp': datetime.utcnow().isoformat(),
                'reason': reason
            },
            severity='info'
        )
        
        # Record consent revocation for GDPR compliance
        self.audit_logger.record_consent(
            patient_id,
            'data_processing',
            granted=False,
            purpose='erasure_request',
            version='1.0',
            method='system'
        )
        
        return {
            'status': 'processed',
            'patient_id': patient_id,
            'anonymized_data_retained': True,
            'medical_records_preserved': True,
            'contact_info_removed': True,
            'consents_revoked': True,
            'actions': erasure_actions,
            'timestamp': datetime.utcnow().isoformat(),
            'note': 'Data anonymized per GDPR requirements. Medical records retained for legal compliance.'
        }
    
    def handle_data_portability_request(self, patient_id: str) -> Dict[str, Any]:
        """
        Handle GDPR Data Portability requests (Article 20)
        Provides patient data in structured, machine-readable format
        
        Args:
            patient_id: Patient ID requesting data
            
        Returns:
            Patient data in structured format (FHIR JSON)
        """
        # Compile all patient data
        patient_data = self._compile_patient_data(patient_id)
        
        # Format data in standardized format (FHIR JSON)
        portable_data = self._convert_to_fhir_format(patient_data)
        
        # Log the portability request
        self.audit_logger.log_audit_event(
            'system',
            'data_portability_request',
            'patient',
            patient_id,
            {
                'format': 'FHIR',
                'data_categories': list(portable_data.keys()),
                'record_count': len(patient_data.get('records', []))
            },
            severity='info'
        )
        
        return portable_data
    
    def handle_access_request(self, patient_id: str) -> Dict[str, Any]:
        """
        Handle GDPR Right of Access requests (Article 15)
        Provides comprehensive access to all personal data
        
        Args:
            patient_id: Patient ID requesting access
            
        Returns:
            Dictionary containing all patient data
        """
        # Get all data access logs for transparency
        access_logs = self.audit_logger.generate_data_access_report(patient_id)
        
        # Get consent records
        consent_history = self._get_consent_history(patient_id)
        
        # Get patient data
        patient_data = self._compile_patient_data(patient_id)
        
        # Log the access request
        self.audit_logger.log_audit_event(
            'system',
            'data_access_request',
            'patient',
            patient_id,
            {'request_type': 'gdpr_article_15'},
            severity='info'
        )
        
        return {
            'patient_id': patient_id,
            'data': patient_data,
            'access_history': access_logs,
            'consent_history': consent_history,
            'retention_policies': self.retention_periods,
            'timestamp': datetime.utcnow().isoformat()
        }
    
    def validate_data_processing(self, patient_id: str, data_type: str, purpose: str) -> Dict[str, Any]:
        """
        Validate data processing complies with GDPR and HIPAA
        
        Args:
            patient_id: Patient ID
            data_type: Type of data being processed
            purpose: Purpose of processing
            
        Returns:
            Validation result dictionary
        """
        # Check consent for GDPR
        consent = self.audit_logger.get_consent_status(patient_id, 'data_processing')
        has_consent = self.audit_logger.has_valid_consent(patient_id, 'data_processing')
        
        # Validate purpose limitation (GDPR Article 5)
        valid_purposes = ['treatment', 'payment', 'healthcare_operations', 'research', 'legal']
        purpose_valid = purpose in valid_purposes
        
        # Check data minimization
        data_minimization = self._check_data_minimization(data_type, purpose)
        
        validation_result = {
            'gdpr_compliant': has_consent and purpose_valid,
            'hipaa_compliant': purpose in ['treatment', 'payment', 'healthcare_operations'],
            'purpose_limitation': purpose_valid,
            'data_minimization': data_minimization,
            'consent_status': {
                'has_consent': has_consent,
                'consent_record': consent
            },
            'timestamp': datetime.utcnow().isoformat()
        }
        
        # Log validation
        self.audit_logger.log_audit_event(
            'system',
            'data_processing_validation',
            'compliance',
            patient_id,
            validation_result,
            severity='info' if validation_result['gdpr_compliant'] else 'warning'
        )
        
        return validation_result
    
    def apply_data_retention_policy(self, data_type: str, cutoff_date: Optional[datetime] = None) -> Dict[str, Any]:
        """
        Apply data retention policies based on configured periods
        
        Args:
            data_type: Type of data to process
            cutoff_date: Optional cutoff date (default: based on retention period)
            
        Returns:
            Dictionary with retention results
        """
        retention_days = self.retention_periods.get(data_type)
        
        if retention_days is None:
            return {
                'status': 'skipped',
                'reason': f'No retention policy for {data_type}'
            }
        
        if cutoff_date is None:
            cutoff_date = datetime.utcnow() - timedelta(days=retention_days)
        
        # This would integrate with your data storage system
        # For now, return structure for implementation
        return {
            'status': 'applied',
            'data_type': data_type,
            'cutoff_date': cutoff_date.isoformat(),
            'retention_period_days': retention_days,
            'note': 'Retention policy applied. Data older than cutoff marked for deletion/anonymization.'
        }
    
    # Private helper methods
    
    def _anonymize_demographics(self, patient_id: str) -> str:
        """
        Anonymize patient demographics while retaining medical value
        
        Args:
            patient_id: Patient ID to anonymize
            
        Returns:
            Anonymization result identifier
        """
        # Implementation would integrate with database/storage
        # This is a placeholder for the actual anonymization logic
        anonymized_id = hashlib.sha256(patient_id.encode()).hexdigest()[:16]
        return f"anonymized_demographics_{anonymized_id}"
    
    def _remove_contact_information(self, patient_id: str) -> str:
        """
        Remove direct identifiers (contact information)
        
        Args:
            patient_id: Patient ID
            
        Returns:
            Removal result identifier
        """
        # Implementation for removing contact info
        return f"removed_contact_info_{patient_id}"
    
    def _retain_medical_records_anonymized(self, patient_id: str) -> str:
        """
        Retain medical records in anonymized form
        
        Args:
            patient_id: Patient ID
            
        Returns:
            Anonymization result identifier
        """
        # Implementation for medical record anonymization
        return f"anonymized_medical_records_{patient_id}"
    
    def _revoke_all_consents(self, patient_id: str) -> Dict[str, Any]:
        """
        Revoke all active consents for a patient
        
        Args:
            patient_id: Patient ID
            
        Returns:
            Dictionary with revocation results
        """
        # Get all consent types
        consent_types = ['data_processing', 'research', 'marketing', 'third_party_sharing']
        revoked = []
        
        for consent_type in consent_types:
            self.audit_logger.record_consent(
                patient_id,
                consent_type,
                granted=False,
                purpose='erasure_request',
                version='1.0',
                method='system'
            )
            revoked.append(consent_type)
        
        return {'revoked_consents': revoked}
    
    def _compile_patient_data(self, patient_id: str) -> Dict[str, Any]:
        """
        Compile comprehensive patient data for portability
        
        Args:
            patient_id: Patient ID
            
        Returns:
            Dictionary containing all patient data
        """
        # This would integrate with your database/storage system
        # Returns structure for implementation
        return {
            'demographics': {},
            'medical_history': {},
            'diagnostic_results': {},
            'treatment_records': {},
            'ai_predictions': {},
            'consent_records': self._get_consent_history(patient_id)
        }
    
    def _convert_to_fhir_format(self, patient_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Convert patient data to FHIR standard format
        
        Args:
            patient_data: Patient data dictionary
            
        Returns:
            FHIR-formatted Bundle
        """
        # Basic FHIR Bundle structure
        return {
            "resourceType": "Bundle",
            "type": "collection",
            "timestamp": datetime.utcnow().isoformat(),
            "entry": [
                {
                    "resource": {
                        "resourceType": "Patient",
                        "id": patient_data.get('demographics', {}).get('id', 'unknown')
                    }
                }
            ]
        }
    
    def _get_consent_history(self, patient_id: str) -> List[Dict[str, Any]]:
        """
        Get full consent history for a patient
        
        Args:
            patient_id: Patient ID
            
        Returns:
            List of consent records
        """
        # This would query the audit logger's consent records
        # For now, return empty list - implementation would query database
        return []
    
    def _check_data_minimization(self, data_type: str, purpose: str) -> bool:
        """
        Ensure only necessary data is processed (GDPR Article 5)
        
        Args:
            data_type: Type of data
            purpose: Purpose of processing
            
        Returns:
            True if data minimization is satisfied
        """
        # Data minimization matrix
        minimization_matrix = {
            'demographics': ['treatment', 'payment', 'healthcare_operations', 'legal'],
            'medical_history': ['treatment', 'payment', 'clinical_decision_support'],
            'diagnostic_images': ['treatment', 'clinical_decision_support'],
            'genetic_data': ['treatment'],  # More restrictive
            'ai_predictions': ['treatment', 'clinical_decision_support', 'research']
        }
        
        allowed_purposes = minimization_matrix.get(data_type, [])
        return purpose in allowed_purposes
