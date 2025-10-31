# RetinaScan AI - Security & Privacy Implementation

## Overview

This document describes the comprehensive security and privacy framework implemented for RetinaScan AI. The system provides multi-layered protection for patient data, ensuring compliance with HIPAA, GDPR, and other regulatory requirements.

## Security Architecture

### Core Services

1. **Data Anonymization Service** (`services/data_anonymizer.py`)
   - Multiple anonymization profiles (research, public, limited, clinical)
   - DICOM metadata anonymization
   - Pixel-level PHI removal from images
   - Deterministic date shifting
   - Configurable generalization rules

2. **Encryption Service** (`services/encryption_service.py`)
   - AES-256 encryption for data at rest
   - Encrypted communication channels
   - Automatic key rotation
   - Secure file encryption/decryption
   - Context-based key management

3. **Access Control Service** (`services/access_control.py`)
   - Role-Based Access Control (RBAC)
   - JWT token-based authentication
   - Permission-based authorization
   - Emergency access protocols
   - Session management

4. **Audit Logging Service** (`services/audit_logger.py`)
   - Comprehensive event logging
   - Security incident tracking
   - Data access auditing
   - Compliance reporting
   - Real-time monitoring

5. **Breach Response Service** (`services/breach_response.py`)
   - Automated incident detection
   - Severity-based response
   - System isolation procedures
   - Regulatory notification workflows
   - Post-breach analysis

6. **Federated Learning Service** (`services/federated_learning.py`)
   - Privacy-preserving model training
   - Distributed aggregation
   - Differential privacy
   - Secure model distribution
   - No data movement

7. **Security Middleware** (`services/security_middleware.py`)
   - Request sanitization
   - Input validation
   - Security headers
   - Authentication/authorization checks

8. **Security Manager** (`services/security_manager.py`)
   - Unified security interface
   - Service orchestration
   - Statistics and monitoring
   - Centralized configuration

## Installation

### Dependencies

The security framework requires additional dependencies:

```bash
pip install PyJWT bcrypt python-jose cryptography
```

All dependencies are included in the updated `requirements.txt`.

### Configuration

Update your `.env` file with security configuration:

```bash
# Security Configuration
ANONYMIZATION_SECRET=your-anonymization-secret-key
KEY_STORAGE_PATH=./.keys
AUDIT_LOG_PATH=./logs/audit
ENABLE_ANONYMIZATION=True
ENABLE_ENCRYPTION=True
ENABLE_FEDERATED_LEARNING=False
JWT_SECRET_KEY=your-jwt-secret-key

# Database (if using)
DATABASE_URL=postgresql://user:pass@localhost:5432/retinascan
```

## Usage

### Basic Integration

```python
from services.security_manager import SecurityManager

# Initialize security manager
security_manager = SecurityManager()

# Anonymize patient data
patient_data = {
    'name': 'John Doe',
    'age': 45,
    'patientId': 'P12345',
    'diagnosis': 'Diabetic Retinopathy'
}

anonymized = security_manager.anonymize_patient_data(
    patient_data, 
    profile='research'
)

# Encrypt patient record
encrypted = security_manager.encrypt_patient_record(patient_data)

# Decrypt when needed
decrypted = security_manager.decrypt_patient_record(encrypted)
```

### Authentication & Authorization

```python
# Authenticate user
result = security_manager.authenticate_and_authorize(
    username='clinician@hospital.com',
    password='secure-password',
    resource='patient-data',
    action='read'
)

if result['authenticated'] and result['authorized']:
    token = result['token']['token']
    # Use token for subsequent requests
```

### Federated Learning

```python
# Initialize federated learning with your model
security_manager.initialize_federated_learning(base_model)

# Start federated round
round_config = security_manager.federated_learning.start_federated_round()

# Receive client updates
security_manager.federated_learning.receive_client_update(
    client_id='hospital1',
    update={
        'weight_updates': [...],
        'sample_count': 1000,
        'signature': '...'
    }
)
```

### Audit & Compliance

```python
# Generate compliance report
from datetime import datetime, timedelta

report = security_manager.generate_compliance_report(
    start_date=datetime.now() - timedelta(days=30),
    end_date=datetime.now()
)

# Get security statistics
stats = security_manager.get_security_statistics()
```

## Security Features

### 1. Data Anonymization

**Profiles:**
- **Research**: Removes direct identifiers, hashes patient IDs, applies date shifting
- **Public**: Maximum anonymization, generalizes age/location, year-only dates
- **Limited**: Keeps some identifiers but removes sensitive data
- **Clinical**: Minimal anonymization for operational use

**Methods:**
- Direct identifier removal
- HMAC-based hashing for IDs
- Deterministic date shifting
- Age/location generalization
- DICOM metadata stripping
- Image text overlay removal

### 2. Encryption

**Features:**
- AES-256 encryption for data at rest
- Context-based key management
- Automatic key rotation
- Encrypted file storage
- Secure communication channels
- Session-based encryption

**Key Management:**
- Separate keys per context (patient records, analysis results, model weights)
- Secure key storage with restricted permissions
- Key versioning for rotation
- Audit trail for key operations

### 3. Access Control

**Roles:**
- **Clinician**: Access to patient data, analysis results, export reports
- **Researcher**: Access to anonymized data, aggregate stats, research exports
- **Administrator**: System management, audit logs, user management
- **Patient**: Access to own data only
- **Model Engineer**: Model training, federated learning management

**Features:**
- JWT token authentication
- Role-based permissions
- Emergency access protocols
- Session management
- Multi-factor authentication ready

### 4. Audit Logging

**Event Types:**
- Security events (authentication, authorization, breaches)
- Data access (patient records, anonymized data, exports)
- Model training (standard, federated learning)
- Anonymization operations
- Emergency access grants
- Breach incidents

**Compliance:**
- HIPAA audit trail requirements
- GDPR logging obligations
- Automated compliance reports
- Real-time monitoring
- Long-term archival

### 5. Breach Response

**Severity Levels:**
- **Critical**: PHI compromise, system intrusion, immediate containment
- **High**: Unauthorized access, suspicious activity
- **Medium**: Failed authentication patterns, misconfigurations
- **Low**: Minor security events

**Response Actions:**
- Automated system isolation
- Credential revocation
- Forensic data preservation
- Stakeholder notifications
- Regulatory reporting
- Patient notifications

### 6. Federated Learning

**Privacy Features:**
- No data movement from sites
- Local model training only
- Aggregated parameter updates
- Differential privacy noise
- Secure aggregation protocols
- Encrypted communications

**Workflow:**
1. Distribute model to clients
2. Local training on site data
3. Aggregate weight updates
4. Apply privacy-preserving techniques
5. Update global model
6. Repeat for continuous learning

## Compliance

### HIPAA Compliance

- **Access Controls**: Role-based access, audit trails, encryption
- **Breach Notification**: Automated 60-day reporting
- **Minimum Necessary**: Least privilege principle
- **Audit Logs**: Comprehensive tracking
- **Data Security**: Encryption at rest and in transit

### GDPR Compliance

- **Right to Access**: Patients can view their data
- **Right to Erasure**: Secure data deletion
- **Data Minimization**: Only necessary data processed
- **Privacy by Design**: Built-in protections
- **Breach Notification**: 72-hour reporting

### Other Standards

- **SOC 2**: Audit logging, access controls
- **ISO 27001**: Security management system
- **HITECH**: Enhanced HIPAA requirements
- **MHLW (Japan)**: Japanese healthcare regulations

## Monitoring & Alerts

### Security Events

- Failed authentication attempts
- Unauthorized access attempts
- Suspicious data access patterns
- Security configuration changes
- Breach detection

### Anomaly Detection

- Unusual access times/locations
- Rapid data downloads
- Privilege escalation attempts
- Multiple failed logins
- Emergency access abuse

### Real-time Alerts

- Email notifications
- Slack/Teams integration
- SIEM system integration
- Dashboard alerts
- Incident response triggers

## Best Practices

### Development

1. **Always use security middleware** for API endpoints
2. **Encrypt sensitive data** before storage
3. **Anonymize data** for research/analytics
4. **Log all security events** comprehensively
5. **Validate and sanitize** all inputs
6. **Use HTTPS only** for production

### Operations

1. **Rotate keys** regularly (quarterly recommended)
2. **Review audit logs** weekly
3. **Update dependencies** monthly
4. **Test breach procedures** quarterly
5. **Backup audit logs** securely
6. **Monitor security metrics** continuously

### Compliance

1. **Conduct assessments** annually
2. **Update policies** as needed
3. **Train staff** on security procedures
4. **Document incidents** thoroughly
5. **Review access logs** regularly
6. **Maintain certifications** current

## Testing

### Unit Tests

```bash
python -m pytest tests/test_security.py
```

### Integration Tests

```bash
python -m pytest tests/test_security_integration.py
```

### Security Tests

```bash
python -m pytest tests/test_security_audit.py
python -m pytest tests/test_federated_learning.py
```

## Troubleshooting

### Common Issues

**Issue**: Import errors for security modules
**Solution**: Install dependencies: `pip install -r requirements.txt`

**Issue**: Encryption key errors
**Solution**: Ensure `.keys` directory has proper permissions: `chmod 600 .keys`

**Issue**: Audit logging not working
**Solution**: Check log directory permissions: `mkdir -p logs/audit && chmod 755 logs`

**Issue**: JWT token verification failing
**Solution**: Verify `JWT_SECRET_KEY` is set and consistent across instances

## Support

For security concerns or questions:
- Email: security@retinascan.ai
- Issues: GitHub security advisory
- Emergency: Internal security hotline

## References

- [HIPAA Compliance Guide](https://www.hhs.gov/hipaa/)
- [GDPR Documentation](https://gdpr.eu/)
- [NIST Cybersecurity Framework](https://www.nist.gov/cyberframework)
- [Federated Learning Papers](https://arxiv.org/list/cs.LG/recent)

