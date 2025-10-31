# EHR Integration Guide for RetinaScan AI

This guide explains how RetinaScan AI integrates with Electronic Health Records (EHR) systems using HL7/FHIR standards for seamless clinical workflow integration.

## Overview

RetinaScan AI is designed to augment existing clinical workflows without disrupting them. The integration supports:

- **FHIR R4** for modern RESTful API integration
- **HL7 v2** for legacy system support via MLLP
- **SMART on FHIR** for OAuth2-based app launch
- **Standard Terminologies** (LOINC, SNOMED CT, ICD-10)

## Architecture

### Key Components

1. **FHIR Integration Service** (`services/fhir_integration.py`)
   - Handles OAuth2 authentication with SMART on FHIR
   - Creates FHIR-compliant observations and diagnostic reports
   - Submits results to EHR systems
   - Manages patient context and demographics

2. **HL7 v2 Integration** (`services/hl7_integration.py`)
   - Provides MLLP-based messaging for legacy systems
   - Creates ADT^A08 messages for patient updates
   - Handles OBX segments for observation data
   - Supports secure TLS connections

3. **Clinical Workflow Manager** (`services/clinical_workflow.py`)
   - Orchestrates end-to-end screening workflow
   - Manages patient validation, AI analysis, and EHR submission
   - Handles automated referrals and follow-up scheduling
   - Maintains comprehensive audit trails

4. **Configuration** (`services/ehr_config.py`)
   - Centralized EHR configuration management
   - Environment-based deployment settings
   - Workflow automation rules

## Setup Instructions

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

Additional dependencies for EHR integration:
- `fhir.resources` (already included)
- `cryptography` (for encryption)
- `flask-cors` (for CORS support)
- `requests` (for HTTP calls)

### 2. Configure Environment Variables

Copy `env.sample` to `.env` and configure the following:

```bash
# FHIR Configuration
FHIR_BASE_URL=https://fhir.epic.com/api/FHIR/R4
FHIR_CLIENT_ID=your_client_id
FHIR_CLIENT_SECRET=your_client_secret
FHIR_AUTH_URL=https://fhir.epic.com/Interconnect-FHIR-Proxy-UserOAuth/oauth2/authorize
FHIR_TOKEN_URL=https://fhir.epic.com/Interconnect-FHIR-Proxy-UserOAuth/oauth2/token
FHIR_REDIRECT_URI=http://localhost:5000/api/auth/callback

# HL7 v2 Configuration (if needed)
HL7_HOST=localhost
HL7_PORT=2575
HL7_USE_TLS=false

# Workflow Configuration
AUTO_APPROVE_CONFIDENCE=0.9
AUTO_APPROVE_MAX_SEVERITY=1
REQUIRE_HUMAN_REVIEW=true
ENABLE_REFERRAL_AUTOMATION=true
ENABLE_FOLLOW_UP_SCHEDULING=true
```

### 3. Register SMART on FHIR Application

1. Contact your EHR vendor (Epic, Cerner, Allscripts, etc.)
2. Register your application as a SMART on FHIR app
3. Obtain OAuth2 client credentials
4. Configure redirect URIs and scopes
5. Test with sandbox environment first

### 4. Configure Workflow Rules

Adjust the workflow configuration based on your clinical needs:

- **Auto-approve confidence**: Results above this threshold are automatically approved
- **Auto-approve max severity**: Maximum severity level for auto-approval
- **Require human review**: Always require clinician review before EHR submission
- **Referral automation**: Automatically create referrals for moderate/severe cases
- **Follow-up scheduling**: Automatically schedule follow-up appointments

## API Endpoints

### EHR Integration Endpoints

#### Get Patient Information
```http
GET /api/ehr/patient/<patient_id>
```

Retrieves patient demographics from EHR.

#### Get Patient Conditions
```http
GET /api/ehr/patient/<patient_id>/conditions
```

Retrieves patient conditions from EHR.

#### Submit Results to EHR
```http
POST /api/ehr/submit-results
Content-Type: application/json

{
  "patient_id": "12345",
  "ai_result": {
    "diagnosis": "Moderate Diabetic Retinopathy",
    "severity_level": 2,
    "confidence": 0.87,
    "recommendation": "Refer to ophthalmologist within 3-6 months"
  },
  "image_data": "base64_encoded_image"
}
```

#### Process Complete Workflow
```http
POST /api/ehr/workflow
Content-Type: application/json

{
  "patient_id": "12345",
  "image_data": "base64_encoded_image",
  "workflow_config": {
    "auto_approve_confidence": 0.9,
    "auto_approve_max_severity": 1
  }
}
```

#### Get Workflow Audit Trail
```http
GET /api/ehr/workflow/<workflow_id>/audit
```

#### Get Workflow Metrics
```http
GET /api/ehr/metrics?period=day
```

## Clinical Workflow

The system follows a complete clinical workflow:

1. **Patient Check-in**: Validates patient context and retrieves demographics
2. **AI Analysis**: Performs diabetic retinopathy screening
3. **Results Review**: Applies auto-approval rules or flags for human review
4. **EHR Integration**: Submits results to EHR via FHIR or HL7 v2
5. **Referral Management**: Creates specialist referrals for moderate/severe cases
6. **Follow-up Scheduling**: Schedules appropriate follow-up based on severity

### Workflow Example

```python
from services.fhir_integration import FHIRIntegrationService, FHIRConfig
from services.ehr_config import EHRConfig

# Initialize services
ehr_config = EHRConfig.from_env()
fhir_config = FHIRConfig(...)
fhir_service = FHIRIntegrationService(fhir_config)

# Get patient information
patient = fhir_service.get_patient_demographics("12345")

# Submit AI results
result = fhir_service.submit_ai_results_to_ehr(
    ai_result={
        'diagnosis': 'Moderate Diabetic Retinopathy',
        'severity_level': 2,
        'confidence': 0.87
    },
    image_data='base64_image',
    patient_id='12345'
)
```

## FHIR Resources

### Observation
The system creates FHIR Observations with:
- **LOINC codes**: Standard terminology for diabetic retinopathy screening
- **SNOMED CT codes**: Detailed diagnosis codes
- **Interpretation**: Positive/Negative flags
- **Components**: Severity level, confidence score, quality score

### DiagnosticReport
Comprehensive diagnostic reports include:
- Patient context
- Observations
- Imaging studies
- PDF report in presentedForm

### AuditEvent
For compliance and tracking:
- Workflow steps
- Data access events
- Submission timestamps
- Outcome tracking

## HL7 v2 Messages

For legacy systems, the integration supports:

- **ADT^A08**: Patient update messages
- **OBX segments**: Observation results
- **MLLP framing**: Standard HL7 message framing
- **TLS support**: Secure message transport

### Message Example

```
MSH|^~\&|RETINASCAN_AI|AI_CLINIC|EHR_SYSTEM|HOSPITAL|20240101120000||ADT^A08|123456|P|2.5
EVN|A08|20240101120000|||RETINASCAN_AI^AI System^^^
PID|1|12345||Doe^John|19700101|M
OBX|1|ST|81204-9^Diabetic Retinopathy Screening^LN||Moderate DR|N|||F|||20240101120000||RETINASCAN_AI^AI System
```

## Security and Compliance

### Authentication
- OAuth2 with SMART on FHIR
- Token-based authentication
- Automatic token refresh
- Secure credential storage

### Data Protection
- PHI encryption
- Audit logging
- Access controls
- Secure communication (HTTPS/TLS)

### Compliance
- HIPAA compliant workflows
- FHIR AuditEvent for tracking
- Standardized terminologies
- Complete audit trails

## Testing

### Sandbox Testing

1. Use Epic MyChart Sandbox or similar test environment
2. Register test application
3. Configure test credentials
4. Verify authentication flow
5. Test resource creation and retrieval

### Integration Testing

```python
import pytest
from services.fhir_integration import FHIRIntegrationService

def test_authentication():
    service = FHIRIntegrationService(config)
    assert service.authenticate_smart_on_fhir() == True

def test_patient_demographics():
    service = FHIRIntegrationService(config)
    demographics = service.get_patient_demographics("test123")
    assert demographics is not None
    assert 'patient_id' in demographics
```

## Troubleshooting

### Common Issues

1. **Authentication failures**
   - Verify client credentials
   - Check token URL and redirect URIs
   - Ensure proper OAuth2 scopes

2. **Patient not found**
   - Verify patient ID format
   - Check FHIR server permissions
   - Ensure proper patient context

3. **EHR submission failures**
   - Review FHIR resource structure
   - Check required fields
   - Verify code systems and terminologies

4. **HL7 message rejections**
   - Validate message format
   - Check MLLP framing
   - Verify segment delimiters

## Deployment

### Production Checklist

- [ ] Configure production FHIR server URLs
- [ ] Set up secure credential storage
- [ ] Enable TLS for HL7 connections
- [ ] Configure auto-approval rules
- [ ] Set up audit logging
- [ ] Test with production EHR
- [ ] Train clinical staff
- [ ] Establish support procedures

### Monitoring

Monitor the following metrics:

- Workflow completion rates
- EHR integration success rates
- Average processing times
- Error rates by type
- Referral creation rates
- Follow-up scheduling rates

Access metrics via:
```http
GET /api/ehr/metrics?period=day
```

## Support

For issues or questions:

1. Check logs for detailed error messages
2. Review audit trails for workflow issues
3. Contact EHR vendor for integration support
4. Consult clinical informatics team

## References

- [HL7 FHIR Documentation](https://www.hl7.org/fhir/)
- [SMART on FHIR](https://docs.smarthealthit.org/)
- [LOINC Codes](https://loinc.org/)
- [SNOMED CT](https://www.snomed.org/)
- [Epic FHIR API](https://fhir.epic.com/)

## License

See LICENSE file for details.

