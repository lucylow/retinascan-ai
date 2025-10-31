# Security Integration Guide for RetinaScan AI

## Quick Start

The RetinaScan AI security framework has been successfully implemented. This guide shows you how to integrate and use it.

## Files Created

### Core Security Services

1. **`services/data_anonymizer.py`** - Data anonymization and de-identification
2. **`services/encryption_service.py`** - Encryption for data at rest and in transit
3. **`services/access_control.py`** - RBAC, authentication, and authorization
4. **`services/audit_logger.py`** - Comprehensive audit logging
5. **`services/breach_response.py`** - Automated incident response
6. **`services/federated_learning.py`** - Privacy-preserving model training
7. **`services/security_middleware.py`** - Request security middleware
8. **`services/security_manager.py`** - Unified security interface

### Documentation

- **`SECURITY_IMPLEMENTATION.md`** - Complete security documentation
- **`SECURITY_INTEGRATION_GUIDE.md`** - This file

## Installation

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

New dependencies added:
- `PyJWT==2.8.0` - JWT authentication
- `bcrypt==4.1.1` - Password hashing
- `python-jose[cryptography]==3.3.0` - Additional crypto support

### 2. Configure Environment

Update your `.env` file:

```bash
# Security Configuration
ANONYMIZATION_SECRET=your-secure-random-secret-key-here
KEY_STORAGE_PATH=./.keys
AUDIT_LOG_PATH=./logs/audit
ENABLE_ANONYMIZATION=True
ENABLE_ENCRYPTION=True
ENABLE_FEDERATED_LEARNING=False
JWT_SECRET_KEY=your-jwt-secret-key-here

# Existing Configuration
DATABASE_URL=...
HOST=0.0.0.0
PORT=8000
```

### 3. Create Directories

```bash
mkdir -p .keys logs/audit
chmod 700 .keys
chmod 755 logs
```

## Basic Usage

### Example 1: Anonymize Patient Data

```python
from services.security_manager import SecurityManager

# Initialize
security = SecurityManager()

# Anonymize data
patient_data = {
    'name': 'John Doe',
    'age': 45,
    'patientId': 'P12345',
    'diagnosis': 'Diabetic Retinopathy'
}

anonymized = security.anonymize_patient_data(
    patient_data,
    profile='research'  # Options: 'research', 'public', 'limited', 'clinical'
)

print(anonymized)
# {'age': '40-44', 'diagnosis': 'Diabetic Retinopathy', 'patientId': 'hashed_id...'}
```

### Example 2: Encrypt/Decrypt Data

```python
# Encrypt
encrypted = security.encrypt_patient_record(patient_data)
print(encrypted)
# {'encrypted_data': 'base64...', 'key_version': 'v1', ...}

# Decrypt
decrypted = security.decrypt_patient_record(encrypted)
print(decrypted)
# {'name': 'John Doe', ...}
```

### Example 3: Authentication & Authorization

```python
# Authenticate user
result = security.authenticate_and_authorize(
    username='clinician@hospital.com',
    password='password123',
    resource='patient-data',
    action='read'
)

if result['authenticated'] and result['authorized']:
    token = result['token']['token']
    print(f"Access granted! Token: {token[:20]}...")
```

### Example 4: Audit Logging

```python
# Log security event
security.audit_logger.log_security_event({
    'category': 'DATA_ACCESS',
    'severity': 'INFO',
    'userId': 'user123',
    'description': 'Patient data accessed'
})

# Generate compliance report
from datetime import datetime, timedelta

report = security.generate_compliance_report(
    start_date=datetime.now() - timedelta(days=30),
    end_date=datetime.now()
)

print(report['total_events'])  # Number of events
print(report['security_incidents'])  # Security incidents
```

## Integration with Flask Backend

### Option 1: Use Security Manager Directly

```python
from flask import Flask, request
from services.security_manager import SecurityManager

app = Flask(__name__)
security = SecurityManager()

@app.route('/api/secure/predict', methods=['POST'])
def secure_predict():
    # Check authentication
    token = request.headers.get('Authorization', '').replace('Bearer ', '')
    access_control = security.access_control
    
    user_payload = access_control.verify_access_token(token)
    if not user_payload:
        return {'error': 'Unauthorized'}, 401
    
    # Check authorization
    user = {
        'id': user_payload['sub'],
        'role': user_payload['role']
    }
    
    decision = access_control.check_access(user, 'analysis', 'request')
    if not decision['granted']:
        return {'error': 'Forbidden'}, 403
    
    # Process prediction...
    return {'success': True}
```

### Option 2: Use Security Middleware

```python
from services.security_middleware import SecurityMiddleware

security_middleware = SecurityMiddleware(
    access_control=security.access_control,
    audit_logger=security.audit_logger
)

@app.before_request
async def check_security():
    # Get endpoint info
    endpoint = request.endpoint
    resource = request.view_args.get('resource', 'general')
    action = request.method.lower()
    
    # Check security
    result = await security_middleware.handle_request(
        request, endpoint, resource, action
    )
    
    if not result['valid']:
        return {'error': result['error']}, 401
    
    # Add user to request context
    request.user = result['user']
```

## Federated Learning Setup

### Initialize Federated Learning

```python
import tensorflow as tf

# Load your model
model = tf.keras.models.load_model('models/retina_model.h5')

# Initialize federated learning
security.initialize_federated_learning(model)

# Start a federated round
round_config = security.federated_learning.start_federated_round()

# Clients will train locally and send updates
# Server aggregates and updates global model
```

## Advanced Features

### Custom Anonymization Profiles

```python
from services.data_anonymizer import DataAnonymizer

anonymizer = DataAnonymizer()

# Add custom profile
anonymizer.anonymization_profiles['custom'] = {
    'remove_fields': ['name', 'email'],
    'hash_fields': ['patientId'],
    'keep_fields': ['age', 'gender', 'diagnosis'],
    'date_shift': True,
    'generalization': {'age': '5-year-buckets'}
}

# Use custom profile
anonymized = anonymizer.anonymize_patient_data(
    patient_data,
    profile='custom'
)
```

### Key Rotation

```python
# Rotate encryption keys
new_version = security.encryption_service.rotate_keys()
print(f"New key version: {new_version}")
```

### Emergency Access

```python
# Request emergency access
emergency = security.access_control.request_emergency_access(
    user={'id': 'doctor123', 'role': 'clinician'},
    reason='Critical patient emergency',
    supervisor={'id': 'supervisor456', 'role': 'administrator'}
)

if emergency['granted']:
    print(f"Emergency access granted until {emergency['expires_at']}")
```

## Testing

### Unit Tests

```bash
# Test data anonymization
python -m pytest tests/test_data_anonymizer.py

# Test encryption
python -m pytest tests/test_encryption.py

# Test access control
python -m pytest tests/test_access_control.py
```

### Integration Tests

```bash
# Test full security workflow
python -m pytest tests/test_security_integration.py
```

## Monitoring & Compliance

### View Security Statistics

```python
stats = security.get_security_statistics()
print(stats)
# {
#   'audit_events': {...},
#   'active_sessions': 5,
#   'active_federated_clients': 3,
#   'key_version': 'v1'
# }
```

### Generate Compliance Report

```python
from datetime import datetime, timedelta

report = security.generate_compliance_report(
    start_date=datetime.now() - timedelta(days=90),
    end_date=datetime.now()
)

print(f"Total events: {report['total_events']}")
print(f"Security incidents: {report['security_incidents']}")
print(f"Compliance status: {report['compliance_status']}")
```

## Best Practices

1. **Always encrypt sensitive data** before storing in database
2. **Anonymize data** when sharing for research
3. **Use appropriate anonymization profiles** for different use cases
4. **Rotate keys regularly** (quarterly recommended)
5. **Review audit logs** weekly for suspicious activity
6. **Test breach procedures** quarterly
7. **Keep dependencies updated** for security patches
8. **Never commit secrets** to version control

## Troubleshooting

### Import Errors

```bash
# Ensure all dependencies installed
pip install -r requirements.txt

# Check Python path
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
```

### Permission Errors

```bash
# Fix key directory permissions
chmod 700 .keys
chmod 600 .keys/*.key 2>/dev/null || true
```

### Token Validation Errors

```bash
# Check JWT_SECRET_KEY is set consistently
echo $JWT_SECRET_KEY

# Regenerate if needed
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

## Next Steps

1. **Review** `SECURITY_IMPLEMENTATION.md` for complete documentation
2. **Configure** your environment variables
3. **Integrate** security services into your application
4. **Test** your integration thoroughly
5. **Monitor** security events regularly
6. **Update** security configurations as needed

## Support

For questions or issues:
- Check `SECURITY_IMPLEMENTATION.md` for detailed docs
- Review service docstrings for API documentation
- Contact security team for production setup

## Summary

The security framework provides:
- ✅ Data anonymization with multiple profiles
- ✅ AES-256 encryption for data protection
- ✅ RBAC-based access control
- ✅ Comprehensive audit logging
- ✅ Automated breach response
- ✅ Federated learning for privacy
- ✅ HIPAA/GDPR compliance ready

Your RetinaScan AI system is now production-ready with enterprise-grade security!

