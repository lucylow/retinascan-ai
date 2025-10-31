"""
Security Manager for RetinaScan AI
Orchestrates all security services
"""
import logging
from typing import Dict, Any, Optional
try:
    from .data_anonymizer import DataAnonymizer
    from .encryption_service import EncryptionService
    from .access_control import AccessControlService, Permission
    from .audit_logger import AuditLogger
    from .breach_response import BreachResponseService
    from .security_middleware import SecurityMiddleware
    from .federated_learning import FederatedLearningService
except ImportError:
    from services.data_anonymizer import DataAnonymizer
    from services.encryption_service import EncryptionService
    from services.access_control import AccessControlService, Permission
    from services.audit_logger import AuditLogger
    from services.breach_response import BreachResponseService
    from services.security_middleware import SecurityMiddleware
    from services.federated_learning import FederatedLearningService

logger = logging.getLogger(__name__)


class SecurityManager:
    """
    Main security manager orchestrating all security services
    Provides unified interface for security operations
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize security manager with all services"""
        self.config = config or {}
        
        # Initialize services
        self.data_anonymizer = DataAnonymizer()
        self.encryption_service = EncryptionService()
        self.audit_logger = AuditLogger()
        self.access_control = AccessControlService()
        self.breach_response = BreachResponseService(audit_logger=self.audit_logger)
        self.federated_learning = FederatedLearningService()
        
        # Connect services
        self.access_control.audit_logger = self.audit_logger
        
        # Initialize middleware
        self.security_middleware = SecurityMiddleware(
            access_control=self.access_control,
            audit_logger=self.audit_logger
        )
        
        logger.info("Security Manager initialized successfully")
    
    def anonymize_patient_data(self, patient_data: Dict[str, Any], 
                               profile: str = 'research') -> Dict[str, Any]:
        """Anonymize patient data"""
        try:
            anonymized = self.data_anonymizer.anonymize_patient_data(patient_data, profile)
            
            # Log anonymization
            self.audit_logger.log_anonymization({
                'profile': profile,
                'record_type': 'patient_data',
                'fields_anonymized': len(patient_data) - len(anonymized),
                'success': True
            })
            
            return anonymized
            
        except Exception as e:
            logger.error(f"Data anonymization failed: {str(e)}")
            raise
    
    def encrypt_patient_record(self, record: Dict[str, Any]) -> Dict[str, Any]:
        """Encrypt patient record"""
        try:
            encrypted = self.encryption_service.encrypt_data(record, 'patient-record')
            
            # Log encryption
            self.audit_logger.log_security_event({
                'category': 'DATA_ENCRYPTION',
                'severity': 'INFO',
                'description': 'Patient record encrypted'
            })
            
            return encrypted
            
        except Exception as e:
            logger.error(f"Encryption failed: {str(e)}")
            raise
    
    def decrypt_patient_record(self, encrypted_payload: Dict[str, Any]) -> Dict[str, Any]:
        """Decrypt patient record"""
        try:
            decrypted = self.encryption_service.decrypt_data(encrypted_payload)
            return decrypted
            
        except Exception as e:
            logger.error(f"Decryption failed: {str(e)}")
            raise
    
    def authenticate_and_authorize(self, username: str, password: str, 
                                   resource: str, action: str) -> Dict[str, Any]:
        """Authenticate user and check authorization"""
        try:
            # Authenticate
            user = self.access_control.authenticate_user(username, password)
            if not user:
                return {'authenticated': False, 'error': 'Invalid credentials'}
            
            # Check authorization
            access_decision = self.access_control.check_access(user, resource, action)
            if not access_decision['granted']:
                return {'authenticated': True, 'authorized': False, 
                       'error': access_decision['reason']}
            
            # Create access token
            token = self.access_control.create_access_token(user)
            
            return {
                'authenticated': True,
                'authorized': True,
                'user': user,
                'token': token
            }
            
        except Exception as e:
            logger.error(f"Authentication/authorization failed: {str(e)}")
            return {'authenticated': False, 'error': str(e)}
    
    def handle_security_incident(self, incident: Dict[str, Any]) -> Dict[str, Any]:
        """Handle security incident"""
        try:
            response = self.breach_response.detect_and_respond(incident)
            return response
            
        except Exception as e:
            logger.error(f"Incident response failed: {str(e)}")
            raise
    
    def initialize_federated_learning(self, base_model: Any) -> None:
        """Initialize federated learning"""
        try:
            self.federated_learning.initialize_federated_model(base_model)
            logger.info("Federated learning initialized")
            
        except Exception as e:
            logger.error(f"Federated learning initialization failed: {str(e)}")
            raise
    
    def generate_compliance_report(self, start_date, end_date) -> Dict[str, Any]:
        """Generate compliance report"""
        try:
            report = self.audit_logger.generate_compliance_report(start_date, end_date)
            return report
            
        except Exception as e:
            logger.error(f"Compliance report generation failed: {str(e)}")
            raise
    
    def get_security_statistics(self) -> Dict[str, Any]:
        """Get current security statistics"""
        return {
            'audit_events': self.audit_logger.stats,
            'active_sessions': len(self.access_control.active_sessions),
            'active_federated_clients': len(self.federated_learning.clients),
            'key_version': self.encryption_service.current_key_version
        }

