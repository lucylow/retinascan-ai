"""
EHR Integration Configuration
Configuration for FHIR, HL7, and clinical workflow settings
"""
import os
from dataclasses import dataclass
from typing import Dict, Any, List


@dataclass
class EHRConfig:
    """EHR integration configuration"""
    
    # FHIR Configuration
    fhir_base_url: str
    fhir_client_id: str
    fhir_client_secret: str
    fhir_auth_url: str
    fhir_token_url: str
    fhir_redirect_uri: str
    
    # HL7 v2 Configuration
    hl7_host: str
    hl7_port: int
    hl7_use_tls: bool
    
    # Workflow Configuration
    auto_approve_confidence: float = 0.9
    auto_approve_max_severity: int = 1
    require_human_review: bool = True
    enable_referral_automation: bool = True
    enable_follow_up_scheduling: bool = True
    
    @classmethod
    def from_env(cls):
        """Create configuration from environment variables"""
        
        return cls(
            fhir_base_url=os.getenv('FHIR_BASE_URL', 'https://fhir.epic.com/api/FHIR/R4'),
            fhir_client_id=os.getenv('FHIR_CLIENT_ID', ''),
            fhir_client_secret=os.getenv('FHIR_CLIENT_SECRET', ''),
            fhir_auth_url=os.getenv('FHIR_AUTH_URL', ''),
            fhir_token_url=os.getenv('FHIR_TOKEN_URL', ''),
            fhir_redirect_uri=os.getenv('FHIR_REDIRECT_URI', ''),
            hl7_host=os.getenv('HL7_HOST', 'localhost'),
            hl7_port=int(os.getenv('HL7_PORT', '2575')),
            hl7_use_tls=os.getenv('HL7_USE_TLS', 'false').lower() == 'true',
            auto_approve_confidence=float(os.getenv('AUTO_APPROVE_CONFIDENCE', '0.9')),
            auto_approve_max_severity=int(os.getenv('AUTO_APPROVE_MAX_SEVERITY', '1')),
            require_human_review=os.getenv('REQUIRE_HUMAN_REVIEW', 'true').lower() == 'true',
            enable_referral_automation=os.getenv('ENABLE_REFERRAL_AUTOMATION', 'true').lower() == 'true',
            enable_follow_up_scheduling=os.getenv('ENABLE_FOLLOW_UP_SCHEDULING', 'true').lower() == 'true'
        )
    
    def to_workflow_config(self) -> Dict[str, Any]:
        """Convert to workflow configuration dictionary"""
        
        return {
            'auto_approve_confidence': self.auto_approve_confidence,
            'auto_approve_max_severity': self.auto_approve_max_severity,
            'require_human_review': self.require_human_review,
            'enable_referral_automation': self.enable_referral_automation,
            'enable_follow_up_scheduling': self.enable_follow_up_scheduling
        }


@dataclass
class ClinicalWorkflowConfig:
    """Clinical workflow configuration"""
    
    # Integration settings
    enable_fhir: bool = True
    enable_hl7: bool = True
    fallback_to_hl7: bool = True
    
    # Review settings
    confidence_threshold_auto_approve: float = 0.9
    confidence_threshold_human_review: float = 0.7
    emergency_severity_level: int = 3
    
    # Notification settings
    notify_on_emergency: bool = True
    notify_on_low_confidence: bool = True
    notification_channels: List[str] = None
    
    def __post_init__(self):
        if self.notification_channels is None:
            self.notification_channels = ['ehr_inbox', 'email']


# Example deployment configuration
DEPLOYMENT_CONFIG = {
    'development': {
        'fhir_base_url': 'https://fhir.epicsandbox.com/api/FHIR/R4',
        'enable_hl7': False,
        'auto_approve_confidence': 0.95
    },
    'staging': {
        'fhir_base_url': 'https://fhir-staging.hospital.org/api/FHIR/R4',
        'enable_hl7': True,
        'auto_approve_confidence': 0.9
    },
    'production': {
        'fhir_base_url': 'https://fhir.hospital.org/api/FHIR/R4',
        'enable_hl7': True,
        'auto_approve_confidence': 0.9,
        'require_human_review': True
    }
}

