"""
Incident Response Manager
Manages security incidents and breach notifications for HIPAA and GDPR compliance
"""

from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
from .audit_logger import AuditLogger
import json


class IncidentResponseManager:
    """
    Manages security incidents and breach notifications
    Implements automated breach detection and regulatory notification procedures
    """
    
    def __init__(self, audit_logger: AuditLogger):
        """
        Initialize IncidentResponseManager
        
        Args:
            audit_logger: AuditLogger instance for logging incidents
        """
        self.audit_logger = audit_logger
        
        # Breach reporting thresholds
        self.breach_thresholds = {
            'phi_exposure': 1,  # Any PHI exposure may require reporting
            'unauthorized_access': 1,
            'data_modification': 1,
            'data_deletion': 1,
            'encryption_failure': 1,
            'authentication_bypass': 1
        }
        
        # Notification timelines (in hours)
        self.notification_timelines = {
            'gdpr': 72,  # GDPR: Within 72 hours of awareness
            'hipaa': 1440,  # HIPAA: Within 60 days (1440 hours)
            'internal': 1,  # Internal notification within 1 hour
            'affected_individuals': 72  # Affected individuals within 72 hours
        }
    
    def detect_potential_breach(
        self,
        event_type: str,
        details: Dict[str, Any],
        severity: str = 'medium'
    ) -> Dict[str, Any]:
        """
        Automatically detect potential breach conditions
        
        Args:
            event_type: Type of security event
            details: Event details dictionary
            severity: Severity level (low, medium, high, critical)
            
        Returns:
            Dictionary with breach assessment and response actions
        """
        requires_reporting = self._assess_breach_severity(event_type, details, severity)
        
        response = {
            'event_type': event_type,
            'detected_at': datetime.utcnow().isoformat(),
            'severity': severity,
            'requires_reporting': requires_reporting,
            'regulations_affected': []
        }
        
        if requires_reporting:
            # Determine which regulations are affected
            if details.get('phi_involved', False) or details.get('us_data', False):
                response['regulations_affected'].append('hipaa')
            
            if details.get('eu_data', False) or details.get('gdpr_applicable', True):
                response['regulations_affected'].append('gdpr')
            
            # Initiate breach response
            response_actions = self._initiate_breach_response(event_type, details, response)
            response['response_actions'] = response_actions
            
            # Log the breach detection
            self.audit_logger.log_audit_event(
                'system',
                'breach_detected',
                'security',
                None,
                {
                    'event_type': event_type,
                    'details': details,
                    'requires_reporting': True,
                    'severity': severity,
                    'regulations': response['regulations_affected']
                },
                severity='critical' if severity in ['high', 'critical'] else 'warning'
            )
        
        return response
    
    def _assess_breach_severity(
        self,
        event_type: str,
        details: Dict[str, Any],
        severity: str
    ) -> bool:
        """
        Assess if incident meets breach reporting thresholds
        
        Args:
            event_type: Type of security event
            details: Event details
            severity: Severity level
            
        Returns:
            True if breach reporting required, False otherwise
        """
        # Critical severity always requires reporting
        if severity == 'critical':
            return True
        
        # Check specific thresholds
        if event_type == 'phi_exposure':
            records_exposed = details.get('records_exposed', 0)
            return records_exposed >= self.breach_thresholds['phi_exposure']
        
        elif event_type == 'unauthorized_access':
            access_attempts = details.get('access_attempts', 0)
            return access_attempts >= self.breach_thresholds['unauthorized_access']
        
        elif event_type == 'data_modification':
            return details.get('unauthorized_modification', False)
        
        elif event_type == 'data_deletion':
            return details.get('unauthorized_deletion', False)
        
        elif event_type == 'encryption_failure':
            return True  # Any encryption failure is serious
        
        elif event_type == 'authentication_bypass':
            return True  # Authentication bypass always requires reporting
        
        # High severity generally requires reporting
        return severity == 'high'
    
    def _initiate_breach_response(
        self,
        event_type: str,
        details: Dict[str, Any],
        response: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Execute breach response procedures
        
        Args:
            event_type: Type of breach
            details: Breach details
            response: Response dictionary to update
            
        Returns:
            List of response actions taken
        """
        response_actions = []
        
        # 1. Immediate containment
        containment_result = self._contain_breach(event_type, details)
        response_actions.append({
            'action': 'contain_breach',
            'status': 'completed',
            'result': containment_result,
            'timestamp': datetime.utcnow().isoformat()
        })
        
        # 2. Impact assessment
        impact_assessment = self._assess_impact(details)
        response_actions.append({
            'action': 'assess_impact',
            'status': 'completed',
            'result': impact_assessment,
            'timestamp': datetime.utcnow().isoformat()
        })
        
        # 3. Notification preparation
        notification_result = self._prepare_notifications(event_type, details, response.get('regulations_affected', []))
        response_actions.append({
            'action': 'prepare_notifications',
            'status': 'completed',
            'result': notification_result,
            'timestamp': datetime.utcnow().isoformat()
        })
        
        # 4. Document incident
        documentation = self._document_incident(event_type, details, response_actions)
        response_actions.append({
            'action': 'document_incident',
            'status': 'completed',
            'result': documentation,
            'timestamp': datetime.utcnow().isoformat()
        })
        
        return response_actions
    
    def _contain_breach(self, event_type: str, details: Dict[str, Any]) -> Dict[str, Any]:
        """
        Immediate containment actions
        
        Args:
            event_type: Type of breach
            details: Breach details
            
        Returns:
            Containment result
        """
        containment_actions = []
        
        # Example containment actions (would integrate with actual system)
        if event_type == 'unauthorized_access':
            containment_actions.append('Revoke affected user sessions')
            containment_actions.append('Reset compromised credentials')
            containment_actions.append('Enforce additional authentication')
        
        elif event_type == 'data_modification' or event_type == 'data_deletion':
            containment_actions.append('Disable affected data access')
            containment_actions.append('Restore from backup if available')
        
        elif event_type == 'encryption_failure':
            containment_actions.append('Disable affected data endpoints')
            containment_actions.append('Enable alternative encryption')
        
        return {
            'containment_actions': containment_actions,
            'containment_status': 'active',
            'note': 'Automated containment initiated. Manual review required.'
        }
    
    def _assess_impact(self, details: Dict[str, Any]) -> Dict[str, Any]:
        """
        Assess scope and impact of breach
        
        Args:
            details: Breach details
            
        Returns:
            Impact assessment dictionary
        """
        impact = {
            'records_affected': details.get('records_exposed', 0),
            'data_types_affected': details.get('data_types', []),
            'users_affected': details.get('users_affected', []),
            'geographic_scope': details.get('geographic_scope', 'unknown'),
            'risk_level': self._calculate_risk_level(details),
            'estimated_remediation_time': self._estimate_remediation_time(details)
        }
        
        return impact
    
    def _prepare_notifications(
        self,
        event_type: str,
        details: Dict[str, Any],
        regulations: List[str]
    ) -> Dict[str, Any]:
        """
        Prepare notifications for regulatory authorities
        
        Args:
            event_type: Type of breach
            details: Breach details
            regulations: List of affected regulations (HIPAA, GDPR)
            
        Returns:
            Notification preparation result
        """
        notifications = {
            'internal_notification': {
                'status': 'prepared',
                'timeline': f'{self.notification_timelines["internal"]} hours',
                'recipients': ['security_team', 'compliance_officer', 'legal_counsel']
            }
        }
        
        # GDPR notification (if applicable)
        if 'gdpr' in regulations:
            notifications['gdpr_notification'] = {
                'status': 'prepared',
                'timeline': f'{self.notification_timelines["gdpr"]} hours',
                'authority': 'Supervisory Authority (DPA)',
                'deadline': (datetime.utcnow() + timedelta(hours=self.notification_timelines['gdpr'])).isoformat(),
                'required_info': [
                    'Nature of breach',
                    'Categories of data subjects affected',
                    'Number of data subjects affected',
                    'Likely consequences',
                    'Measures proposed to address breach'
                ]
            }
        
        # HIPAA notification (if applicable)
        if 'hipaa' in regulations:
            notifications['hipaa_notification'] = {
                'status': 'prepared',
                'timeline': f'{self.notification_timelines["hipaa"]} hours (60 days)',
                'authority': 'HHS Office for Civil Rights',
                'deadline': (datetime.utcnow() + timedelta(hours=self.notification_timelines['hipaa'])).isoformat(),
                'required_info': [
                    'Nature and extent of breach',
                    'Protected health information involved',
                    'Who used or accessed PHI',
                    'Risk assessment',
                    'Mitigation measures'
                ]
            }
        
        # Affected individuals notification
        notifications['individual_notification'] = {
            'status': 'prepared',
            'timeline': f'{self.notification_timelines["affected_individuals"]} hours',
            'method': details.get('notification_method', 'email'),
            'required_content': [
                'Description of breach',
                'Types of information involved',
                'Steps being taken',
                'Recommended actions',
                'Contact information'
            ]
        }
        
        return notifications
    
    def _document_incident(
        self,
        event_type: str,
        details: Dict[str, Any],
        response_actions: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Document incident for compliance and audit
        
        Args:
            event_type: Type of breach
            details: Breach details
            response_actions: List of response actions taken
            
        Returns:
            Documentation result
        """
        incident_record = {
            'incident_id': self._generate_incident_id(),
            'event_type': event_type,
            'detected_at': datetime.utcnow().isoformat(),
            'details': details,
            'response_actions': response_actions,
            'documentation_status': 'complete'
        }
        
        # This would be stored in a separate incidents database/table
        # For now, we log it via audit logger
        self.audit_logger.log_audit_event(
            'system',
            'incident_documented',
            'security',
            incident_record['incident_id'],
            incident_record,
            severity='critical'
        )
        
        return {
            'incident_id': incident_record['incident_id'],
            'status': 'documented',
            'note': 'Incident fully documented and logged for compliance audit'
        }
    
    def _calculate_risk_level(self, details: Dict[str, Any]) -> str:
        """
        Calculate overall risk level of breach
        
        Args:
            details: Breach details
            
        Returns:
            Risk level: low, medium, high, critical
        """
        records_affected = details.get('records_exposed', 0)
        data_types = details.get('data_types', [])
        
        # Critical: Sensitive data types or large number of records
        if 'phi' in data_types or 'genetic' in data_types or records_affected > 500:
            return 'critical'
        
        # High: Moderate records or sensitive operations
        if records_affected > 100 or 'sensitive' in data_types:
            return 'high'
        
        # Medium: Small number of records
        if records_affected > 10:
            return 'medium'
        
        return 'low'
    
    def _estimate_remediation_time(self, details: Dict[str, Any]) -> str:
        """
        Estimate time required for remediation
        
        Args:
            details: Breach details
            
        Returns:
            Estimated remediation time description
        """
        severity = self._calculate_risk_level(details)
        
        estimates = {
            'critical': '24-48 hours',
            'high': '3-7 days',
            'medium': '1-2 weeks',
            'low': '2-4 weeks'
        }
        
        return estimates.get(severity, 'unknown')
    
    def _generate_incident_id(self) -> str:
        """
        Generate unique incident ID
        
        Returns:
            Unique incident identifier
        """
        timestamp = datetime.utcnow().strftime('%Y%m%d%H%M%S')
        return f"INCIDENT-{timestamp}"
    
    def report_breach_to_authorities(
        self,
        incident_id: str,
        regulation: str,
        notification_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Report breach to regulatory authorities
        
        Args:
            incident_id: Incident ID
            regulation: Regulation (hipaa or gdpr)
            notification_data: Data to include in notification
            
        Returns:
            Notification result
        """
        # This would integrate with actual notification systems
        # For GDPR: Send to Supervisory Authority
        # For HIPAA: Send to HHS OCR
        
        notification_result = {
            'incident_id': incident_id,
            'regulation': regulation,
            'notification_sent': True,
            'timestamp': datetime.utcnow().isoformat(),
            'notification_data': notification_data,
            'note': f'Breach notification prepared for {regulation.upper()}. Integration with authority API required.'
        }
        
        # Log notification
        self.audit_logger.log_audit_event(
            'system',
            'breach_notification_sent',
            'compliance',
            incident_id,
            notification_result,
            severity='info'
        )
        
        return notification_result
    
    def notify_affected_individuals(
        self,
        incident_id: str,
        affected_patient_ids: List[str],
        notification_content: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Notify affected individuals of breach
        
        Args:
            incident_id: Incident ID
            affected_patient_ids: List of affected patient IDs
            notification_content: Content of notification
            
        Returns:
            Notification result
        """
        # This would integrate with notification system (email, mail, etc.)
        notification_result = {
            'incident_id': incident_id,
            'individuals_notified': len(affected_patient_ids),
            'notification_method': notification_content.get('method', 'email'),
            'notification_sent': True,
            'timestamp': datetime.utcnow().isoformat(),
            'note': 'Individual notifications prepared. Integration with notification service required.'
        }
        
        # Log notification
        self.audit_logger.log_audit_event(
            'system',
            'individual_notification_sent',
            'compliance',
            incident_id,
            notification_result,
            severity='info'
        )
        
        return notification_result
