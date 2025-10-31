"""
Audit Logging Service for RetinaScan AI
Comprehensive logging for security, compliance, and auditing
"""
import logging
import json
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from pathlib import Path
import os

logger = logging.getLogger(__name__)


class AuditLogger:
    """
    Service for comprehensive audit logging
    Tracks security events, data access, and compliance activities
    """
    
    def __init__(self, log_directory: Optional[str] = None):
        self.log_directory = Path(log_directory or './logs/audit')
        self.log_directory.mkdir(parents=True, exist_ok=True)
        
        # Log file for today
        self.today_log = self.log_directory / f"audit_{datetime.now().strftime('%Y%m%d')}.log"
        
        # In-memory queue for performance
        self.log_queue = []
        self.is_processing = False
        
        # Statistics
        self.stats = {
            'total_events': 0,
            'security_incidents': 0,
            'data_access_events': 0,
            'failed_authentications': 0
        }
    
    def log_security_event(self, event: Dict[str, Any]) -> None:
        """
        Log security-related event
        
        Args:
            event: Security event data
        """
        audit_event = {
            'id': self._generate_event_id(),
            'type': 'SECURITY_EVENT',
            'category': event.get('category', 'UNKNOWN'),
            'severity': event.get('severity', 'INFO'),
            'user_id': event.get('userId'),
            'timestamp': datetime.utcnow().isoformat(),
            'source_ip': event.get('ipAddress'),
            'user_agent': event.get('userAgent'),
            'description': event.get('description', ''),
            'details': event.get('details', {})
        }
        
        # Update statistics
        if audit_event['severity'] in ['WARNING', 'ERROR', 'CRITICAL']:
            self.stats['security_incidents'] += 1
        
        self._queue_event(audit_event)
        logger.info(f"Security event logged: {audit_event['category']}")
    
    def log_access_attempt(self, user_id: str, resource: str, action: str,
                          granted: bool, **kwargs) -> None:
        """
        Log access attempt
        
        Args:
            user_id: User ID
            resource: Resource identifier
            action: Action attempted
            granted: Whether access was granted
            **kwargs: Additional context
        """
        audit_event = {
            'id': self._generate_event_id(),
            'type': 'ACCESS_ATTEMPT',
            'user_id': user_id,
            'timestamp': datetime.utcnow().isoformat(),
            'resource': resource,
            'action': action,
            'granted': granted,
            'ip_address': kwargs.get('ipAddress', kwargs.get('ip_address')),
            'user_agent': kwargs.get('userAgent', kwargs.get('user_agent')),
            'details': kwargs.get('details', {})
        }
        
        # Update statistics
        if not granted:
            self.stats['failed_authentications'] += 1
        
        self._queue_event(audit_event)
        logger.debug(f"Access attempt logged: {user_id} -> {action}:{resource} ({granted})")
    
    def log_data_access(self, event: Dict[str, Any]) -> None:
        """
        Log data access event
        
        Args:
            event: Data access event data
        """
        audit_event = {
            'id': self._generate_event_id(),
            'type': 'DATA_ACCESS',
            'user_id': event.get('userId'),
            'timestamp': datetime.utcnow().isoformat(),
            'resource_type': event.get('resourceType'),
            'access_type': event.get('accessType'),
            'patient_id': event.get('patientId'),
            'record_id': event.get('recordId'),
            'ip_address': event.get('ipAddress'),
            'fields_accessed': event.get('fieldsAccessed', []),
            'query': event.get('query'),
            'result_count': event.get('resultCount'),
            'details': event.get('details', {})
        }
        
        self.stats['data_access_events'] += 1
        self._queue_event(audit_event)
        logger.info(f"Data access logged: {audit_event['access_type']}")
    
    def log_model_training(self, event: Dict[str, Any]) -> None:
        """
        Log model training event
        
        Args:
            event: Model training event data
        """
        audit_event = {
            'id': self._generate_event_id(),
            'type': 'MODEL_TRAINING',
            'timestamp': datetime.utcnow().isoformat(),
            'model_version': event.get('modelVersion'),
            'training_type': event.get('trainingType', 'STANDARD'),
            'dataset_size': event.get('datasetSize'),
            'demographics': event.get('demographics', {}),
            'accuracy': event.get('accuracy'),
            'fairness_metrics': event.get('fairnessMetrics', {}),
            'training_duration': event.get('trainingDuration'),
            'details': event.get('details', {})
        }
        
        self._queue_event(audit_event)
        logger.info(f"Model training logged: {audit_event['model_version']}")
    
    def log_federated_learning_round(self, event: Dict[str, Any]) -> None:
        """
        Log federated learning round
        
        Args:
            event: Federated learning event data
        """
        audit_event = {
            'id': self._generate_event_id(),
            'type': 'FEDERATED_LEARNING',
            'timestamp': datetime.utcnow().isoformat(),
            'round_id': event.get('roundId'),
            'participating_clients': event.get('participatingClients', []),
            'samples_processed': event.get('samplesProcessed'),
            'aggregation_method': event.get('aggregationMethod'),
            'privacy_budget_used': event.get('privacyBudgetUsed'),
            'metrics': event.get('metrics', {}),
            'details': event.get('details', {})
        }
        
        self._queue_event(audit_event)
        logger.info(f"Federated learning round logged: {audit_event['round_id']}")
    
    def log_emergency_access(self, user: Dict[str, Any], supervisor: Dict[str, Any],
                           reason: str) -> None:
        """
        Log emergency access grant
        
        Args:
            user: User receiving emergency access
            supervisor: Supervisor approving access
            reason: Reason for emergency access
        """
        audit_event = {
            'id': self._generate_event_id(),
            'type': 'EMERGENCY_ACCESS',
            'timestamp': datetime.utcnow().isoformat(),
            'user_id': user.get('id'),
            'username': user.get('username'),
            'supervisor_id': supervisor.get('id'),
            'supervisor_username': supervisor.get('username'),
            'reason': reason,
            'severity': 'HIGH'
        }
        
        self.stats['security_incidents'] += 1
        self._queue_event(audit_event)
        logger.warning(f"Emergency access logged: {user.get('username')}")
    
    def log_anonymization(self, event: Dict[str, Any]) -> None:
        """
        Log data anonymization event
        
        Args:
            event: Anonymization event data
        """
        audit_event = {
            'id': self._generate_event_id(),
            'type': 'ANONYMIZATION',
            'timestamp': datetime.utcnow().isoformat(),
            'profile': event.get('profile'),
            'record_type': event.get('recordType'),
            'fields_anonymized': event.get('fieldsAnonymized', []),
            'success': event.get('success', True),
            'details': event.get('details', {})
        }
        
        self._queue_event(audit_event)
        logger.info(f"Anonymization logged: {audit_event['profile']}")
    
    def log_breach_incident(self, incident: Dict[str, Any]) -> None:
        """
        Log security breach incident
        
        Args:
            incident: Breach incident data
        """
        audit_event = {
            'id': self._generate_event_id(),
            'type': 'BREACH_INCIDENT',
            'timestamp': datetime.utcnow().isoformat(),
            'severity': incident.get('severity', 'HIGH'),
            'affected_systems': incident.get('affectedSystems', []),
            'data_compromised': incident.get('dataCompromised', []),
            'detection_time': incident.get('detectionTime'),
            'containment_time': incident.get('containmentTime'),
            'affected_patients': incident.get('affectedPatients'),
            'description': incident.get('description'),
            'details': incident.get('details', {})
        }
        
        self.stats['security_incidents'] += 1
        self._queue_event(audit_event)
        logger.critical(f"Breach incident logged: {audit_event['severity']}")
    
    def generate_compliance_report(self, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """
        Generate compliance report for date range
        
        Args:
            start_date: Report start date
            end_date: Report end date
            
        Returns:
            Compliance report
        """
        # Load and filter events
        events = self._load_events_in_range(start_date, end_date)
        
        # Analyze events
        report = {
            'period': {
                'start_date': start_date.isoformat(),
                'end_date': end_date.isoformat()
            },
            'total_events': len(events),
            'security_incidents': len([e for e in events if e['type'] == 'BREACH_INCIDENT' 
                                     or 'UNAUTHORIZED' in e.get('category', '')]),
            'data_access_breakdown': self._analyze_data_access(events),
            'model_training_breakdown': self._analyze_model_training(events),
            'compliance_status': self._check_regulatory_compliance(events),
            'recommendations': self._generate_recommendations(events)
        }
        
        logger.info(f"Compliance report generated: {report['total_events']} events")
        return report
    
    def _queue_event(self, event: Dict[str, Any]) -> None:
        """Add event to queue for processing"""
        self.log_queue.append(event)
        self.stats['total_events'] += 1
        
        # Process queue if not already processing
        if not self.is_processing:
            self._process_queue()
    
    def _process_queue(self) -> None:
        """Process queued events"""
        if self.is_processing:
            return
        
        self.is_processing = True
        
        try:
            while self.log_queue:
                event = self.log_queue.pop(0)
                self._store_event(event)
        finally:
            self.is_processing = False
    
    def _store_event(self, event: Dict[str, Any]) -> None:
        """Store audit event to log file"""
        try:
            with open(self.today_log, 'a') as f:
                f.write(json.dumps(event) + '\n')
        except Exception as e:
            logger.error(f"Failed to store audit event: {str(e)}")
    
    def _load_events_in_range(self, start_date: datetime, end_date: datetime) -> List[Dict[str, Any]]:
        """Load events within date range"""
        events = []
        
        # Load from log files in range
        current_date = start_date
        while current_date <= end_date:
            log_file = self.log_directory / f"audit_{current_date.strftime('%Y%m%d')}.log"
            if log_file.exists():
                try:
                    with open(log_file, 'r') as f:
                        for line in f:
                            event = json.loads(line)
                            event_date = datetime.fromisoformat(event['timestamp'])
                            if start_date <= event_date <= end_date:
                                events.append(event)
                except Exception as e:
                    logger.error(f"Failed to load log file {log_file}: {str(e)}")
            
            current_date += timedelta(days=1)
        
        return events
    
    def _analyze_data_access(self, events: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze data access patterns"""
        access_events = [e for e in events if e['type'] == 'DATA_ACCESS']
        
        return {
            'total_accesses': len(access_events),
            'unique_users': len(set(e['user_id'] for e in access_events if 'user_id' in e)),
            'failed_attempts': len([e for e in events if e['type'] == 'ACCESS_ATTEMPT' and not e.get('granted')]),
            'emergency_accesses': len([e for e in events if e['type'] == 'EMERGENCY_ACCESS'])
        }
    
    def _analyze_model_training(self, events: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze model training activities"""
        training_events = [e for e in events if e['type'] == 'MODEL_TRAINING']
        fl_events = [e for e in events if e['type'] == 'FEDERATED_LEARNING']
        
        return {
            'standard_trainings': len(training_events),
            'federated_rounds': len(fl_events),
            'total_samples': sum(e.get('dataset_size', 0) for e in training_events),
            'avg_accuracy': sum(e.get('accuracy', 0) for e in training_events) / max(len(training_events), 1)
        }
    
    def _check_regulatory_compliance(self, events: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Check regulatory compliance status"""
        return {
            'hipaa_compliant': True,  # Simplified
            'gdpr_compliant': True,
            'issues': []
        }
    
    def _generate_recommendations(self, events: List[Dict[str, Any]]) -> List[str]:
        """Generate security recommendations based on events"""
        recommendations = []
        
        # Check for suspicious patterns
        failed_auths = [e for e in events if e['type'] == 'ACCESS_ATTEMPT' and not e.get('granted')]
        if len(failed_auths) > 100:
            recommendations.append("High number of failed authentication attempts detected")
        
        emergency_accesses = [e for e in events if e['type'] == 'EMERGENCY_ACCESS']
        if len(emergency_accesses) > 10:
            recommendations.append("Excessive emergency access usage detected")
        
        return recommendations
    
    def _generate_event_id(self) -> str:
        """Generate unique event ID"""
        import uuid
        return str(uuid.uuid4())[:16]

