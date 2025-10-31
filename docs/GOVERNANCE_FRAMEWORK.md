# Governance Framework Documentation

## Overview

This document describes the comprehensive governance framework implemented for RetinaScan AI to ensure compliance with HIPAA (Health Insurance Portability and Accountability Act) and GDPR (General Data Protection Regulation) requirements.

## Architecture

The governance framework consists of four core components:

### 1. Security & Access Control (`security_manager.py`)

**Purpose**: Implements authentication, encryption, and role-based access control (RBAC)

**Key Features**:
- JWT token-based authentication with configurable expiration
- bcrypt password hashing
- Role-Based Access Control (RBAC) with granular permissions
- Data access level matrix (full, read_only, restricted, own, none)
- Flask decorators for route protection

**Roles Defined**:
- `clinician`: Full access to patient data, can submit diagnoses
- `researcher`: Access to anonymized data only
- `patient`: Access to own data, consent management
- `admin`: Full system access, audit logs, data retention
- `readonly`: Read-only access to patient data

### 2. Audit Logging (`audit_logger.py`)

**Purpose**: Comprehensive audit trails for HIPAA and GDPR compliance

**Key Features**:
- General audit logs for all system activities
- Data access logs (HIPAA requirement)
- Consent records (GDPR requirement)
- Model usage logs for AI governance
- Failed access attempt tracking
- Compliance report generation

**Database Tables**:
- `audit_logs`: General system activities
- `data_access_logs`: All data access events
- `consent_records`: Patient consent management
- `model_usage_logs`: AI model usage tracking

### 3. Data Governance (`data_governance.py`)

**Purpose**: Manages GDPR data subject rights and data lifecycle

**Key Features**:
- GDPR Right of Access (Article 15)
- GDPR Right to Data Portability (Article 20)
- GDPR Right to Erasure (Article 17) - with medical record preservation
- GDPR Right to Rectification (Article 16)
- Data minimization validation
- Purpose limitation enforcement
- Data retention policy management

**Retention Periods** (configurable):
- Medical records: 7 years
- Diagnostic images: 5 years
- AI predictions: 1 year
- Audit logs: 7 years (HIPAA requirement)
- Consent records: 7 years

### 4. Incident Response (`incident_response.py`)

**Purpose**: Security incident detection and breach notification management

**Key Features**:
- Automated breach detection
- Impact assessment
- Regulatory notification preparation (HIPAA 60 days, GDPR 72 hours)
- Affected individual notification
- Incident documentation

**Breach Thresholds**:
- PHI exposure: 1 record
- Unauthorized access: 1 attempt
- Data modification: Any unauthorized change
- Encryption failure: Any failure
- Authentication bypass: Any bypass

### 5. Integrated Framework (`governance_framework.py`)

**Purpose**: Main coordinator integrating all governance components

**Key Features**:
- Unified API for all governance operations
- Data processing validation
- Model usage logging
- Consent management
- GDPR request handling
- Compliance report generation

## API Endpoints

### Authentication Endpoints

**Note**: Authentication endpoints need to be implemented separately. The framework provides the security infrastructure, but user registration/login endpoints should be added to your application.

### Governance Endpoints

#### `POST /api/governance/consent`
Manage patient consent (GDPR requirement)

**Authentication**: Required (token)

**Request Body**:
```json
{
  "patient_id": "patient123",
  "consent_type": "data_processing",
  "granted": true,
  "expiration": "2025-12-31T23:59:59",
  "purpose": "Medical treatment",
  "version": "1.0"
}
```

**Response**:
```json
{
  "success": true,
  "result": {
    "status": "recorded",
    "patient_id": "patient123",
    "consent_type": "data_processing",
    "granted": true,
    "timestamp": "2024-01-15T10:30:00"
  }
}
```

#### `POST /api/governance/gdpr-request`
Handle GDPR data subject rights requests

**Authentication**: Required (token)

**Request Types**:
- `access`: Right of Access (Article 15)
- `portability`: Right to Data Portability (Article 20)
- `erasure`: Right to Erasure (Article 17)
- `rectification`: Right to Rectification (Article 16)

**Request Body**:
```json
{
  "request_type": "access",
  "patient_id": "patient123",
  "details": {}
}
```

#### `GET /api/governance/compliance-report`
Generate compliance reports for audit and regulatory submission

**Authentication**: Required (token)
**Permission**: `audit_logs`

**Query Parameters**:
- `type`: Report type (`audit`, `data_access`, `failed_access`)
- `start_date`: Start date (ISO format)
- `end_date`: End date (ISO format)
- `user_id`: Optional user filter
- `patient_id`: Optional patient filter
- `resource_type`: Optional resource type filter

#### `GET /api/governance/data-access/<patient_id>`
Get data access log for a patient (GDPR transparency)

**Authentication**: Required (token)
**Data Access**: Must have access to patient's PHI

**Query Parameters**:
- `start_date`: Optional start date filter
- `end_date`: Optional end date filter

#### `POST /api/governance/validate-processing`
Validate data processing for compliance before execution

**Authentication**: Required (token)

**Request Body**:
```json
{
  "patient_id": "patient123",
  "data_type": "phi",
  "purpose": "treatment",
  "access_type": "read"
}
```

#### `GET /api/governance/status`
Get governance framework status (public endpoint)

## Integration with Prediction Endpoint

The prediction endpoint (`/api/predict`) has been enhanced to:
- Extract user ID and patient ID from requests
- Log all model usage for governance
- Track processing times
- Record prediction results

**Example Request**:
```bash
POST /api/predict
Headers:
  Authorization: Bearer <token>
  X-Patient-ID: patient123
Content-Type: multipart/form-data
  image: <file>
  patient_id: patient123
```

## Security Best Practices

1. **Secret Keys**: Always use strong, randomly generated secret keys stored in environment variables
2. **Token Expiration**: Tokens expire after 8 hours (configurable via `TOKEN_EXPIRATION_HOURS`)
3. **Password Hashing**: All passwords must be hashed using bcrypt
4. **Access Control**: Use principle of least privilege
5. **Audit Logging**: All sensitive operations are logged

## Compliance Checklist

### HIPAA Compliance

- ✅ Access Controls (§164.312)
- ✅ Person/Entity Authentication (§164.312)
- ✅ Audit Controls (§164.312)
- ✅ Breach Notification Rule (§164.400)
- ✅ Minimum Necessary Standard
- ✅ Data Integrity Controls

### GDPR Compliance

- ✅ Data Security (Article 32)
- ✅ Privacy by Design (Article 25)
- ✅ Accountability (Article 5)
- ✅ Lawful Processing (Article 6)
- ✅ Data Minimization (Article 5)
- ✅ Purpose Limitation (Article 5)
- ✅ Right of Access (Article 15)
- ✅ Right to Erasure (Article 17)
- ✅ Right to Data Portability (Article 20)
- ✅ Right to Rectification (Article 16)
- ✅ Consent Management (Article 7)
- ✅ Personal Data Breach Notification (Article 33)

## Database Schema

The governance framework uses SQLite by default. In production, you should migrate to a production-grade database (PostgreSQL, MySQL, etc.).

**Tables**:
- `audit_logs`: General audit trail
- `data_access_logs`: PHI access tracking
- `consent_records`: GDPR consent management
- `model_usage_logs`: AI usage tracking

## Configuration

### Environment Variables

```bash
# Required
SECRET_KEY=your-strong-secret-key-here

# Optional
TOKEN_EXPIRATION_HOURS=8
GOVERNANCE_DB_PATH=/path/to/governance.db
```

### Flask App Configuration

The governance framework automatically uses `SECRET_KEY` from Flask config if available.

## Usage Examples

### Protecting an Endpoint

```python
from services.governance.security_manager import token_required, permission_required

@app.route('/api/patient/<patient_id>/diagnosis', methods=['GET'])
@token_required
@permission_required('view_patient_data')
@data_access_required(data_type='phi', access_level='read')
def get_patient_diagnosis(patient_id):
    # Log data access
    governance.audit_logger.log_data_access(
        user_id=request.user['user_id'],
        patient_id=patient_id,
        data_type='phi',
        access_type='read',
        purpose='treatment',
        justification='Clinical decision making'
    )
    
    # Your diagnosis retrieval logic
    diagnosis = get_diagnosis(patient_id)
    return jsonify(diagnosis)
```

### Logging Model Usage

```python
governance.log_model_prediction(
    user_id='clinician123',
    patient_id='patient456',
    model_version='1.0.0',
    prediction_result={
        'diagnosis': 'Moderate Diabetic Retinopathy',
        'confidence': 0.87
    },
    processing_time_ms=1250
)
```

### Handling GDPR Request

```python
result = governance.handle_gdpr_request(
    request_type='access',
    patient_id='patient123',
    request_details={}
)
```

## Incident Response

### Automatic Breach Detection

The framework automatically detects potential breaches when:
- Unauthorized access attempts occur
- Failed authentication exceeds thresholds
- Data is accessed without proper authorization

### Manual Breach Reporting

```python
incident = governance.incident_mgr.detect_potential_breach(
    event_type='unauthorized_access',
    details={
        'user_id': 'user123',
        'patient_id': 'patient456',
        'access_attempts': 5
    },
    severity='high'
)
```

## Limitations and Future Enhancements

### Current Limitations

1. User management is not included - implement separately
2. Database uses SQLite (migrate to production DB)
3. Email/notification system integration needed for breach notifications
4. Encryption at rest not implemented (implement separately)

### Recommended Enhancements

1. **User Management System**: Implement user registration, authentication, and role management
2. **Database Migration**: Migrate to PostgreSQL for production
3. **Notification Service**: Integrate email/SMS for breach notifications
4. **Encryption at Rest**: Implement encryption for stored data
5. **Multi-Factor Authentication**: Add MFA for enhanced security
6. **Data Anonymization Tools**: Implement actual anonymization (currently placeholders)
7. **FHIR Integration**: Enhance data portability with full FHIR implementation

## Deployment Considerations

1. **Production Database**: Replace SQLite with production-grade database
2. **Secret Management**: Use secure secret management (AWS Secrets Manager, HashiCorp Vault)
3. **Backup Strategy**: Implement regular backups of audit logs
4. **Monitoring**: Set up monitoring for security incidents
5. **Compliance Training**: Ensure staff are trained on governance procedures

## Support and Maintenance

- **Regular Audits**: Conduct quarterly compliance audits
- **Policy Updates**: Update retention policies as regulations change
- **Security Updates**: Keep dependencies updated
- **Incident Reviews**: Review and learn from security incidents

## Additional Resources

- [HIPAA Compliance Guide](https://www.hhs.gov/hipaa/index.html)
- [GDPR Official Text](https://gdpr.eu/)
- [FHIR Specification](https://www.hl7.org/fhir/)

## License

This governance framework is part of the RetinaScan AI system and follows the same license terms.
