# Frontend-Backend Connectivity Setup

This document outlines the configuration and fixes applied to ensure proper connectivity between the frontend (React/Vite) and backend (Flask) applications.

## Configuration Summary

### Backend Configuration (`backend/config.py`)
- **CORS Origins**: Updated to include common frontend development ports:
  - `http://localhost:3000` (Create React App default)
  - `http://localhost:5173` (Vite default)
  - `http://localhost:8080` (Current Vite config)

### Frontend Configuration (`vite.config.ts`)
- **Dev Server Port**: `8080`
- **Proxy Configuration**: Added proxy for `/api/*` requests to backend during development
  - Proxies to `http://localhost:5000` (or `VITE_API_BASE_URL` if set)
  - Allows relative paths in development (e.g., `/api/predict`)

### API Configuration (`src/lib/config.ts`)
- **Base URL**: Defaults to `http://localhost:5000`
- **Environment Variable**: `VITE_API_BASE_URL` can override the default
- Supports both direct backend API and Supabase Edge Functions

## Changes Made

### 1. CORS Configuration
**File**: `backend/config.py`
- Added `http://localhost:8080` to default CORS origins
- Updated `env.sample` to include port 8080

### 2. Vite Proxy Setup
**File**: `vite.config.ts`
- Added proxy configuration for `/api/*` requests
- Proxies to backend during development
- Eliminates CORS issues in development

### 3. API Endpoint Alignment
Fixed inconsistent API endpoints:
- `src/pages/AIAnalyzer.tsx`: Updated `/predict` → `/api/predict`
- `src/components/ClinicMap.tsx`: Updated to use `config.api.baseUrl`
- `src/components/InteractiveDashboard.tsx`: Updated to use `/api/metrics` endpoint

## Environment Variables

### Required for Backend
```bash
# Backend
SECRET_KEY=dev-secret-key-2023
CORS_ORIGINS=http://localhost:3000,http://localhost:5173,http://localhost:8080
PORT=5000
```

### Required for Frontend
```bash
# Frontend
VITE_API_BASE_URL=http://localhost:5000
```

## API Endpoints Available

### Health & Status
- `GET /api/health` - Health check endpoint
- `GET /api/model/info` - Model information
- `GET /api/metrics` - System metrics

### Predictions
- `POST /api/predict` - Single image prediction
- `POST /api/predict/batch` - Batch predictions
- `POST /api/process` - Process image (alias for predict)

### Patient & Clinical
- `POST /api/intake` - Patient intake form
- `GET /api/clinics` - Nearby clinics
- `GET /api/workflows` - Workflow history

### EHR Integration
- `GET /api/ehr/patient/<patient_id>` - Get patient info
- `GET /api/ehr/patient/<patient_id>/conditions` - Get patient conditions
- `POST /api/ehr/submit-results` - Submit AI results to EHR
- `POST /api/ehr/workflow` - Process clinical workflow

### Governance & Compliance
- `GET /api/governance/status` - Governance framework status
- `POST /api/governance/consent` - Manage patient consent
- `POST /api/governance/gdpr-request` - Handle GDPR requests
- `GET /api/governance/compliance-report` - Generate compliance reports

## Testing Connectivity

### 1. Start Backend
```bash
cd backend
python app.py
# Backend should be running on http://localhost:5000
```

### 2. Start Frontend
```bash
npm run dev
# Frontend should be running on http://localhost:8080
```

### 3. Test Connection
1. Open browser to `http://localhost:8080`
2. Check browser console for any CORS errors
3. Try uploading an image and making a prediction
4. Check network tab in dev tools to verify API calls

### 4. Verify Health Endpoint
```bash
curl http://localhost:5000/api/health
```

Expected response:
```json
{
  "status": "healthy",
  "timestamp": "...",
  "model_status": "loaded",
  "version": "1.0.0"
}
```

## Development vs Production

### Development
- Uses Vite proxy for `/api/*` requests
- Frontend at `http://localhost:8080`
- Backend at `http://localhost:5000`
- CORS enabled for all dev ports

### Production
- Frontend uses `VITE_API_BASE_URL` environment variable
- Set to production backend URL
- CORS origins should be restricted to production domains

## Troubleshooting

### CORS Errors
- Verify `CORS_ORIGINS` in backend includes frontend origin
- Check that backend is running
- Ensure frontend is using correct API base URL

### Proxy Not Working
- Verify Vite dev server is running
- Check `vite.config.ts` proxy configuration
- Ensure backend is accessible at proxy target URL

### API Calls Failing
- Check browser network tab for request details
- Verify backend endpoints match frontend expectations
- Check backend logs for errors
- Verify `VITE_API_BASE_URL` is set correctly

## Next Steps

1. **Analytics Endpoint**: Consider implementing `/api/analytics/dashboard` endpoint for better dashboard data
2. **Environment Variable Validation**: Add runtime checks for required environment variables
3. **Error Handling**: Enhance error messages to guide users when connectivity fails
4. **Health Checks**: Add frontend health check component that verifies backend connectivity

