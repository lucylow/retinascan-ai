"""
FHIR Integration Service for RetinaScan AI
Provides HL7/FHIR interoperability with EHR systems
"""
import requests
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import uuid
import base64
from cryptography.fernet import Fernet
import os
import logging

logger = logging.getLogger(__name__)


@dataclass
class FHIRConfig:
    """FHIR server configuration"""
    fhir_base_url: str
    client_id: str
    client_secret: str
    auth_url: str
    token_url: str
    redirect_uri: str
    scope: str = "launch/patient patient/*.read patient/*.write openid profile"


class FHIRIntegrationService:
    """HL7/FHIR integration service for EHR interoperability"""
    
    def __init__(self, config: FHIRConfig):
        self.config = config
        self.access_token = None
        self.token_expiry = None
        self.patient_context = None
        self.encryption_key = Fernet.generate_key()
        self.cipher_suite = Fernet(self.encryption_key)
        
        # Standard code systems
        self.code_systems = {
            'loinc': 'http://loinc.org',
            'snomed': 'http://snomed.info/sct',
            'icd10': 'http://hl7.org/fhir/sid/icd-10',
            'rxnorm': 'http://www.nlm.nih.gov/research/umls/rxnorm'
        }
        
        # Diabetic retinopathy specific codes
        self.dr_codes = {
            'screening_observation': '81204-9',  # LOINC: Retinal imaging diabetic retinopathy screening
            'severity_scale': '81205-6',         # LOINC: Diabetic retinopathy severity scale
            'no_dr': '408637004',                # SNOMED: No diabetic retinopathy
            'mild_dr': '408638009',              # SNOMED: Mild non-proliferative diabetic retinopathy
            'moderate_dr': '408639001',          # SNOMED: Moderate non-proliferative diabetic retinopathy
            'severe_dr': '408640004',            # SNOMED: Severe non-proliferative diabetic retinopathy
            'pdr': '408641000',                  # SNOMED: Proliferative diabetic retinopathy
            'retinal_image': '42132-1'           # LOINC: Retinal image
        }
    
    def authenticate_smart_on_fhir(self, launch_token: str = None) -> bool:
        """Authenticate with SMART on FHIR using OAuth2"""
        
        try:
            if launch_token:
                # SMART App Launch scenario
                token_url = self.config.token_url
                auth_data = {
                    'grant_type': 'authorization_code',
                    'code': launch_token,
                    'client_id': self.config.client_id,
                    'client_secret': self.config.client_secret,
                    'redirect_uri': self.config.redirect_uri
                }
            else:
                # Client credentials flow (for backend services)
                token_url = self.config.token_url
                auth_data = {
                    'grant_type': 'client_credentials',
                    'client_id': self.config.client_id,
                    'client_secret': self.config.client_secret,
                    'scope': self.config.scope
                }
            
            response = requests.post(token_url, data=auth_data)
            
            if response.status_code == 200:
                token_data = response.json()
                self.access_token = token_data['access_token']
                self.token_expiry = datetime.now() + timedelta(seconds=token_data.get('expires_in', 3600))
                
                # Extract patient context if available
                if 'patient' in token_data:
                    self.patient_context = token_data['patient']
                
                logger.info("SMART on FHIR authentication successful")
                return True
            else:
                logger.error(f"Authentication failed: {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Authentication error: {str(e)}")
            return False
    
    def refresh_token_if_needed(self) -> bool:
        """Refresh token if expired"""
        if not self.access_token or datetime.now() >= self.token_expiry:
            return self.authenticate_smart_on_fhir()
        return True
    
    def get_patient_demographics(self, patient_id: str = None) -> Optional[Dict]:
        """Retrieve patient demographics from EHR"""
        
        if not self.refresh_token_if_needed():
            return None
        
        try:
            patient_id = patient_id or self.patient_context
            if not patient_id:
                logger.warning("No patient context available")
                return None
            
            url = f"{self.config.fhir_base_url}/Patient/{patient_id}"
            headers = {
                'Authorization': f'Bearer {self.access_token}',
                'Accept': 'application/fhir+json'
            }
            
            response = requests.get(url, headers=headers)
            
            if response.status_code == 200:
                patient_data = response.json()
                return self._parse_patient_demographics(patient_data)
            else:
                logger.error(f"Failed to fetch patient data: {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"Error fetching patient demographics: {str(e)}")
            return None
    
    def _parse_patient_demographics(self, patient_resource: Dict) -> Dict:
        """Parse FHIR Patient resource into simplified demographics"""
        
        demographics = {
            'patient_id': patient_resource.get('id'),
            'name': '',
            'birth_date': '',
            'gender': '',
            'contact_info': {},
            'conditions': []
        }
        
        # Extract name
        if 'name' in patient_resource and len(patient_resource['name']) > 0:
            name = patient_resource['name'][0]
            demographics['name'] = f"{name.get('given', [''])[0]} {name.get('family', '')}".strip()
        
        # Extract birth date and gender
        demographics['birth_date'] = patient_resource.get('birthDate', '')
        demographics['gender'] = patient_resource.get('gender', '')
        
        # Extract contact information
        if 'telecom' in patient_resource:
            for telecom in patient_resource['telecom']:
                system = telecom.get('system', '')
                value = telecom.get('value', '')
                if system == 'phone':
                    demographics['contact_info']['phone'] = value
                elif system == 'email':
                    demographics['contact_info']['email'] = value
        
        # Extract address
        if 'address' in patient_resource and len(patient_resource['address']) > 0:
            address = patient_resource['address'][0]
            demographics['contact_info']['address'] = {
                'line': address.get('line', ['']),
                'city': address.get('city', ''),
                'state': address.get('state', ''),
                'postal_code': address.get('postalCode', '')
            }
        
        return demographics
    
    def get_patient_conditions(self, patient_id: str = None) -> List[Dict]:
        """Retrieve patient conditions from EHR"""
        
        if not self.refresh_token_if_needed():
            return []
        
        try:
            patient_id = patient_id or self.patient_context
            url = f"{self.config.fhir_base_url}/Condition"
            params = {
                'patient': patient_id,
                '_count': 100
            }
            headers = {
                'Authorization': f'Bearer {self.access_token}',
                'Accept': 'application/fhir+json'
            }
            
            response = requests.get(url, params=params, headers=headers)
            
            if response.status_code == 200:
                bundle = response.json()
                conditions = []
                
                for entry in bundle.get('entry', []):
                    condition = entry.get('resource', {})
                    conditions.append(self._parse_condition(condition))
                
                return conditions
            else:
                logger.error(f"Failed to fetch conditions: {response.text}")
                return []
                
        except Exception as e:
            logger.error(f"Error fetching conditions: {str(e)}")
            return []
    
    def _parse_condition(self, condition_resource: Dict) -> Dict:
        """Parse FHIR Condition resource"""
        
        condition = {
            'id': condition_resource.get('id'),
            'code': '',
            'display': '',
            'system': '',
            'onset_date': '',
            'clinical_status': '',
            'verification_status': ''
        }
        
        # Extract code information
        if 'code' in condition_resource and 'coding' in condition_resource['code']:
            coding = condition_resource['code']['coding'][0]  # Take first coding
            condition['code'] = coding.get('code', '')
            condition['display'] = coding.get('display', '')
            condition['system'] = coding.get('system', '')
        
        # Extract dates and status
        condition['onset_date'] = condition_resource.get('onsetDateTime', '')
        condition['clinical_status'] = condition_resource.get('clinicalStatus', {}).get('coding', [{}])[0].get('code', '')
        condition['verification_status'] = condition_resource.get('verificationStatus', {}).get('coding', [{}])[0].get('code', '')
        
        return condition
    
    def create_dr_observation(self, ai_result: Dict, patient_id: str = None) -> Dict:
        """Create FHIR Observation for diabetic retinopathy screening result"""
        
        patient_id = patient_id or self.patient_context
        severity_level = ai_result.get('severity_level', 0)
        diagnosis = ai_result.get('diagnosis', 'Unknown')
        confidence = ai_result.get('confidence', 0.0)
        
        # Map diagnosis to SNOMED code
        diagnosis_codes = {
            'No Diabetic Retinopathy': self.dr_codes['no_dr'],
            'Mild Diabetic Retinopathy': self.dr_codes['mild_dr'],
            'Moderate Diabetic Retinopathy': self.dr_codes['moderate_dr'],
            'Severe Diabetic Retinopathy': self.dr_codes['severe_dr'],
            'Proliferative Diabetic Retinopathy': self.dr_codes['pdr']
        }
        
        observation = {
            "resourceType": "Observation",
            "id": f"retinascan-{uuid.uuid4().hex[:8]}",
            "status": "final",
            "category": [
                {
                    "coding": [
                        {
                            "system": self.code_systems['loinc'],
                            "code": "LP7839-6",
                            "display": "Radiology"
                        }
                    ]
                }
            ],
            "code": {
                "coding": [
                    {
                        "system": self.code_systems['loinc'],
                        "code": self.dr_codes['screening_observation'],
                        "display": "Diabetic retinopathy screening"
                    }
                ],
                "text": "AI-assisted diabetic retinopathy screening"
            },
            "subject": {
                "reference": f"Patient/{patient_id}"
            },
            "effectiveDateTime": datetime.now().isoformat(),
            "issued": datetime.now().isoformat(),
            "performer": [
                {
                    "reference": "Organization/retinascan-ai",
                    "display": "RetinaScan AI System"
                }
            ],
            "valueCodeableConcept": {
                "coding": [
                    {
                        "system": self.code_systems['snomed'],
                        "code": diagnosis_codes.get(diagnosis, ''),
                        "display": diagnosis
                    }
                ],
                "text": diagnosis
            },
            "interpretation": [
                {
                    "coding": [
                        {
                            "system": "http://terminology.hl7.org/CodeSystem/v3-ObservationInterpretation",
                            "code": "POS" if severity_level > 0 else "NEG",
                            "display": "Positive" if severity_level > 0 else "Negative"
                        }
                    ]
                }
            ],
            "method": {
                "text": "Deep learning analysis of retinal fundus image"
            },
            "component": [
                {
                    "code": {
                        "coding": [
                            {
                                "system": self.code_systems['loinc'],
                                "code": self.dr_codes['severity_scale'],
                                "display": "Diabetic retinopathy severity scale"
                            }
                        ]
                    },
                    "valueInteger": severity_level
                },
                {
                    "code": {
                        "text": "AI Confidence Score"
                    },
                    "valueDecimal": float(confidence)
                },
                {
                    "code": {
                        "text": "Quality Assessment Score"
                    },
                    "valueDecimal": float(ai_result.get('quality_score', 0.0))
                }
            ],
            "note": [
                {
                    "text": f"AI-generated screening result. Confidence: {confidence:.1%}. {ai_result.get('recommendation', '')}"
                }
            ]
        }
        
        return observation
    
    def create_diagnostic_report(self, ai_result: Dict, image_data: str, 
                               patient_id: str = None) -> Dict:
        """Create FHIR DiagnosticReport for comprehensive results"""
        
        patient_id = patient_id or self.patient_context
        
        # Create observation first
        observation = self.create_dr_observation(ai_result, patient_id)
        
        diagnostic_report = {
            "resourceType": "DiagnosticReport",
            "id": f"dr-report-{uuid.uuid4().hex[:8]}",
            "status": "final",
            "category": [
                {
                    "coding": [
                        {
                            "system": self.code_systems['loinc'],
                            "code": "LP29684-5",
                            "display": "Radiology"
                        }
                    ]
                }
            ],
            "code": {
                "coding": [
                    {
                        "system": self.code_systems['loinc'],
                        "code": "19005-8",
                        "display": "Radiology Report"
                    }
                ]
            },
            "subject": {
                "reference": f"Patient/{patient_id}"
            },
            "effectiveDateTime": datetime.now().isoformat(),
            "issued": datetime.now().isoformat(),
            "performer": [
                {
                    "reference": "Organization/retinascan-ai",
                    "display": "RetinaScan AI System"
                }
            ],
            "result": [
                {
                    "reference": f"Observation/{observation['id']}"
                }
            ],
            "imagingStudy": [
                {
                    "reference": f"ImagingStudy/{uuid.uuid4().hex[:8]}",
                    "display": "Retinal Fundus Photography"
                }
            ],
            "conclusion": ai_result.get('recommendation', ''),
            "presentedForm": [
                {
                    "contentType": "application/pdf",
                    "data": self._generate_pdf_report(ai_result, image_data),
                    "title": "RetinaScan AI Screening Report"
                }
            ]
        }
        
        return diagnostic_report
    
    def submit_ai_results_to_ehr(self, ai_result: Dict, image_data: str, 
                               patient_id: str = None) -> Dict:
        """Submit comprehensive AI results to EHR"""
        
        if not self.refresh_token_if_needed():
            return {'success': False, 'error': 'Authentication failed'}
        
        try:
            patient_id = patient_id or self.patient_context
            
            # Create and submit Observation
            observation = self.create_dr_observation(ai_result, patient_id)
            obs_response = self._submit_fhir_resource(observation, 'Observation')
            
            # Create and submit DiagnosticReport
            diagnostic_report = self.create_diagnostic_report(ai_result, image_data, patient_id)
            report_response = self._submit_fhir_resource(diagnostic_report, 'DiagnosticReport')
            
            # Create AuditEvent for compliance
            audit_event = self._create_audit_event(ai_result, patient_id)
            audit_response = self._submit_fhir_resource(audit_event, 'AuditEvent')
            
            return {
                'success': obs_response['success'] and report_response['success'],
                'observation_id': obs_response.get('id'),
                'report_id': report_response.get('id'),
                'audit_id': audit_response.get('id'),
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error submitting results to EHR: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def _submit_fhir_resource(self, resource: Dict, resource_type: str) -> Dict:
        """Submit FHIR resource to server"""
        
        url = f"{self.config.fhir_base_url}/{resource_type}"
        headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/fhir+json',
            'Accept': 'application/fhir+json'
        }
        
        response = requests.post(url, json=resource, headers=headers)
        
        if response.status_code in [200, 201]:
            response_data = response.json()
            return {
                'success': True,
                'id': response_data.get('id'),
                'location': response.headers.get('Location', '')
            }
        else:
            logger.error(f"Failed to submit {resource_type}: {response.text}")
            return {
                'success': False,
                'error': response.text,
                'status_code': response.status_code
            }
    
    def _create_audit_event(self, ai_result: Dict, patient_id: str) -> Dict:
        """Create FHIR AuditEvent for compliance and tracking"""
        
        return {
            "resourceType": "AuditEvent",
            "id": f"audit-{uuid.uuid4().hex[:8]}",
            "type": {
                "system": "http://terminology.hl7.org/CodeSystem/audit-event-type",
                "code": "rest",
                "display": "Restful Operation"
            },
            "subtype": [
                {
                    "system": "http://hl7.org/fhir/restful-interaction",
                    "code": "create",
                    "display": "create"
                }
            ],
            "action": "C",
            "recorded": datetime.now().isoformat(),
            "outcome": "0",
            "outcomeDesc": "AI screening results successfully processed",
            "purposeOfEvent": [
                {
                    "coding": [
                        {
                            "system": "http://terminology.hl7.org/CodeSystem/v3-ActReason",
                            "code": "TREAT",
                            "display": "Treatment"
                        }
                    ]
                }
            ],
            "agent": [
                {
                    "type": {
                        "coding": [
                            {
                                "system": "http://terminology.hl7.org/CodeSystem/extra-security-role-type",
                                "code": "authserver",
                                "display": "Authorization Server"
                            }
                        ]
                    },
                    "who": {
                        "reference": "Device/retinascan-ai",
                        "display": "RetinaScan AI System"
                    },
                    "requestor": True
                }
            ],
            "source": {
                "site": "RetinaScan AI Cloud",
                "observer": {
                    "reference": "Device/retinascan-ai"
                },
                "type": [
                    {
                        "system": "http://terminology.hl7.org/CodeSystem/security-source-type",
                        "code": "4",
                        "display": "Application Server"
                    }
                ]
            },
            "entity": [
                {
                    "what": {
                        "reference": f"Patient/{patient_id}"
                    },
                    "role": {
                        "coding": [
                            {
                                "system": "http://terminology.hl7.org/CodeSystem/object-role",
                                "code": "1",
                                "display": "Patient"
                            }
                        ]
                    }
                }
            ]
        }
    
    def _generate_pdf_report(self, ai_result: Dict, image_data: str) -> str:
        """Generate base64 encoded PDF report"""
        
        report_content = f"""
        RETINASCAN AI SCREENING REPORT
        ==============================
        
        Patient ID: {self.patient_context}
        Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}
        
        DIAGNOSIS: {ai_result.get('diagnosis', 'Unknown')}
        Severity Level: {ai_result.get('severity_level', 0)}
        Confidence: {ai_result.get('confidence', 0):.1%}
        Quality Score: {ai_result.get('quality_score', 0):.1%}
        
        RECOMMENDATIONS:
        {ai_result.get('recommendation', 'No specific recommendations')}
        
        CLINICAL NOTES:
        - AI-assisted screening completed
        - Results should be reviewed by qualified healthcare professional
        - Urgency: {self._get_urgency_level(ai_result.get('severity_level', 0))}
        
        --- END OF REPORT ---
        """
        
        report_bytes = report_content.encode('utf-8')
        return base64.b64encode(report_bytes).decode('utf-8')
    
    def _get_urgency_level(self, severity: int) -> str:
        """Get urgency level based on severity"""
        urgency_map = {
            0: "Routine",
            1: "Non-urgent",
            2: "Semi-urgent", 
            3: "Urgent",
            4: "Emergency"
        }
        return urgency_map.get(severity, "Unknown")

