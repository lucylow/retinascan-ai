# Frontend-Backend Integration Summary

## Overview

RetinaScan AI now has complete frontend-backend integration with EHR capabilities. This document outlines how all components work together.

## Integration Architecture

```
Frontend (React + TypeScript)
    ↓
EHR Integration Panel
    ↓
EHR Hooks (useEHRIntegration)
    ↓
Backend API (Flask)
    ↓
EHR Services (FHIR/HL7)
    ↓
EHR System
```

## Frontend Components

### 1. EHR Integration Panel (`src/components/EHRIntegrationPanel.tsx`)

**Purpose**: UI for EHR integration workflow

**Features**:
- Patient ID input and validation
- Patient demographics retrieval
- Analysis summary display
- EHR submission
- Submission status feedback
- Error handling

**Props**:
- `analysisResult`: AnalysisResult
- `imageData`: string | File
- `patientId`: string

### 2. EHR Integration Hook (`src/hooks/useEHRIntegration.ts`)

**Purpose**: API wrapper for EHR operations

**Methods**:
- `submitToEHR()`: Submit results to EHR
- `getPatientDemographics()`: Fetch patient info
- `getPatientConditions()`: Fetch patient conditions
- `processWorkflow()`: Complete clinical workflow

**State**:
- `isSubmitting`: Submission in progress
- `isLoadingPatient`: Patient data loading

### 3. Results Display (`src/components/Results/AnalysisResults.tsx`)

**Integration**: Embeds EHR Integration Panel
- Displays analysis results
- Shows EHR submission panel
- Handles patient context

## Backend Integration

### API Endpoints Used

#### 1. Patient Information
```http
GET /api/ehr/patient/<patient_id>
```
**Response**:
```json
{
  "success": true,
  "patient": {
    "patient_id": "...",
    "name": "...",
    "birth_date": "...",
    "gender": "...",
    "contact_info": {...}
  }
}
```

#### 2. Patient Conditions
```http
GET /api/ehr/patient/<patient_id>/conditions
```
**Response**:
```json
{
  "success": true,
  "conditions": [...]
}
```

#### 3. Submit Results
```http
POST /api/ehr/submit-results
```
**Request**:
```json
{
  "patient_id": "...",
  "ai_result": {
    "diagnosis": "...",
    "severity_level": 2,
    "confidence": 0.87,
    "recommendation": "..."
  },
  "image_data": "base64..."
}
```

**Response**:
```json
{
  "success": true,
  "observation_id": "...",
  "report_id": "...",
  "timestamp": "..."
}
```

#### 4. Clinical Workflow
```http
POST /api/ehr/workflow
```
**Request**:
```json
{
  "patient_id": "...",
  "image_data": "...",
  "workflow_config": {...}
}
```

## Data Flow

### Complete Workflow

1. **Patient Selection**
   - User enters patient ID
   - Frontend calls `GET /api/ehr/patient/<id>`
   - Displays patient demographics

2. **Image Upload**
   - User uploads retina image
   - Backend processes via `POST /api/predict`
   - Returns analysis results

3. **Results Display**
   - Frontend displays results
   - Shows EHR integration panel
   - Converts image to base64

4. **EHR Submission**
   - User clicks "Submit to EHR"
   - Frontend calls `POST /api/ehr/submit-results`
   - Backend creates FHIR resources
   - Returns submission confirmation

5. **Workflow (Optional)**
   - Complete automated workflow
   - Includes referrals and follow-ups
   - Generated via `POST /api/ehr/workflow`

## Configuration

### Frontend Configuration

File: `src/lib/config.ts`

```typescript
export const config = {
  api: {
    baseUrl: import.meta.env.VITE_API_BASE_URL || 'http://localhost:5000',
  },
  // ...
};
```

### Environment Variables

File: `.env` (frontend)

```bash
VITE_API_BASE_URL=http://localhost:5000
```

File: `.env` (backend)

```bash
# EHR Integration - FHIR Configuration
FHIR_BASE_URL=https://fhir.epic.com/api/FHIR/R4
FHIR_CLIENT_ID=your_client_id
FHIR_CLIENT_SECRET=your_client_secret
FHIR_AUTH_URL=https://fhir.epic.com/Interconnect-FHIR-Proxy-UserOAuth/oauth2/authorize
FHIR_TOKEN_URL=https://fhir.epic.com/Interconnect-FHIR-Proxy-UserOAuth/oauth2/token
FHIR_REDIRECT_URI=http://localhost:5000/api/auth/callback

# HL7 v2 Configuration
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

## Error Handling

### Frontend Error Handling

```typescript
try {
  const result = await submitToEHR(analysisResult, base64Image, patientId);
  if (result.success) {
    // Show success message
  } else {
    // Show error: result.error
  }
} catch (error) {
  // Handle network/API errors
}
```

### Backend Error Handling

```python
try:
    result = fhir_service.submit_ai_results_to_ehr(...)
    return jsonify(result)
except Exception as e:
    logger.error(f"Error: {str(e)}")
    return jsonify({'success': False, 'error': str(e)}), 500
```

## State Management

### Analysis Result Mapping

Frontend severity → Backend severity:
```typescript
{
  none: 0,
  mild: 1,
  moderate: 2,
  severe: 3,
  proliferative: 4
}
```

### Data Transformation

**Frontend → Backend**:
```typescript
{
  diagnosis: "Moderate Diabetic Retinopathy",
  severity_level: 2,
  confidence: 0.87,  // from 0-1
  quality_score: 0.9,
  recommendation: "Refer to ophthalmologist within 3-6 months"
}
```

## Testing Integration

### 1. Test Patient Lookup

```bash
curl http://localhost:5000/api/ehr/patient/test-123
```

### 2. Test Submission

```bash
curl -X POST http://localhost:5000/api/ehr/submit-results \
  -H "Content-Type: application/json" \
  -d '{
    "patient_id": "test-123",
    "ai_result": {
      "diagnosis": "Moderate Diabetic Retinopathy",
      "severity_level": 2,
      "confidence": 0.87,
      "recommendation": "Follow-up in 3-6 months"
    },
    "image_data": "base64..."
  }'
```

### 3. Frontend Testing

1. Start frontend: `npm run dev`
2. Start backend: `python main.py`
3. Upload retina image
4. Enter patient ID
5. Click "Submit to EHR"

## UI/UX Flow

### User Journey

1. **Upload Image**
   - User uploads retina scan
   - Shows upload progress
   - Displays analysis results

2. **Patient Verification**
   - User enters patient ID
   - Clicks "Load Patient"
   - Shows patient demographics
   - Displays existing conditions

3. **Review Results**
   - Displays severity level
   - Shows confidence score
   - Lists key findings
   - Provides recommendations

4. **Submit to EHR**
   - User reviews summary
   - Clicks "Submit to EHR"
   - Shows submission progress
   - Displays confirmation
   - Shows observation/report IDs

## Security Considerations

### Data Encryption
- Images converted to base64
- Encrypted in transit (HTTPS)
- Secure EHR credentials

### Authentication
- OAuth2 with SMART on FHIR
- Token-based API calls
- Secure patient data access

### HIPAA Compliance
- Audit trail logging
- PHI protection
- Access controls
- Data retention policies

## Troubleshooting

### Common Issues

#### 1. Patient Not Found
**Solution**: Verify patient ID and EHR configuration

#### 2. Submission Fails
**Solution**: Check EHR credentials and network connectivity

#### 3. Image Not Converting
**Solution**: Ensure FileReader API support and valid image format

#### 4. API Connection Issues
**Solution**: Verify backend is running and VITE_API_BASE_URL is correct

### Debug Mode

Enable verbose logging:

```typescript
// Frontend
console.log('EHR Integration:', { patientId, imageData, analysisResult });

// Backend
logger.setLevel(logging.DEBUG)
```

## Performance Optimization

### Frontend
- Lazy load EHR panel
- Debounce patient lookup
- Cache patient data
- Optimize image conversion

### Backend
- Async workflow processing
- Connection pooling
- Token caching
- Batch operations

## Future Enhancements

1. **Real-time Updates**: WebSocket for live status
2. **Batch Processing**: Multiple patients at once
3. **Advanced Workflows**: Custom workflow rules
4. **Dashboard**: EHR metrics and analytics
5. **Notifications**: Push alerts for critical results

## Summary

The integration is complete and production-ready:

✅ Frontend EHR UI components  
✅ Backend EHR API endpoints  
✅ FHIR R4 compliance  
✅ HL7 v2 support  
✅ Clinical workflows  
✅ Error handling  
✅ Security measures  
✅ Documentation  

For detailed setup, see:
- `EHR_INTEGRATION_GUIDE.md`
- `EHR_INTEGRATION_SUMMARY.md`
- `README.md`

