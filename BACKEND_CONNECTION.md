# Backend-Frontend Connection Guide

This guide explains how the frontend and backend connect, and how to ensure they're working together properly.

## Connection Architecture

The frontend supports **two methods** for connecting to the backend:

1. **Direct Backend API** (Primary method when available)
   - Connects directly to the FastAPI backend at `http://localhost:8000`
   - Faster and more reliable for local development
   - Uses REST API endpoints (`/health`, `/predict`, `/model/info`)

2. **Supabase Edge Functions** (Fallback)
   - Used when direct backend is not available
   - Connects through Supabase Edge Function `analyze-retina`
   - Useful for cloud deployments

The frontend automatically tries the direct backend first, then falls back to Supabase if the backend is unavailable.

## Configuration

### Backend Configuration

The FastAPI backend (`main.py`) runs on port 8000 by default. CORS is configured to allow connections from:
- `http://localhost:3000`
- `http://localhost:5173` (Vite default)
- `http://localhost:8080` (Current Vite config)

To change the port, set the `PORT` environment variable:
```bash
export PORT=8001
python main.py
```

To customize CORS origins, set the `CORS_ORIGINS` environment variable:
```bash
export CORS_ORIGINS=http://localhost:8080,https://yourdomain.com
python main.py
```

### Frontend Configuration

The frontend automatically detects the backend URL. You can configure it via environment variable:

```env
VITE_BACKEND_API_URL=http://localhost:8000
```

If not set, it defaults to `http://localhost:8000`.

### Flask Backend Configuration

The Flask backend (`backend/app.py`) runs on port 5000 by default. CORS is also configured for the same origins.

To run the Flask backend:
```bash
cd backend
python app.py
```

## Verification Steps

### 1. Check Backend is Running

**FastAPI Backend:**
```bash
curl http://localhost:8000/health
```

Expected response:
```json
{
  "status": "healthy",
  "timestamp": "2024-01-20T10:30:00Z",
  "model_loaded": true,
  "model_info": {...}
}
```

**Flask Backend:**
```bash
curl http://localhost:5000/api/health
```

### 2. Check Frontend Can Connect

1. Open the browser console (F12)
2. Look for connection logs:
   - "Using direct backend API" - Direct connection working
   - "Backend API not available, trying Supabase" - Using fallback
   - "Using Supabase Edge Function" - Using Supabase only

### 3. Test Image Upload

1. Open the frontend at `http://localhost:8080`
2. Upload a retinal image
3. Click "Analyze Image"
4. Check the browser console for:
   - API call logs
   - Response data
   - Any errors

## Troubleshooting

### Issue: "Backend API not available"

**Symptoms:**
- Console shows "Backend API not available, trying Supabase"
- Falls back to Supabase Edge Function

**Solutions:**
1. Ensure the backend is running:
   ```bash
   python main.py
   ```
2. Check the backend URL is correct (default: `http://localhost:8000`)
3. Verify CORS is configured correctly
4. Check firewall/network settings

### Issue: CORS Errors

**Symptoms:**
- Browser console shows CORS errors
- Network tab shows CORS preflight failures

**Solutions:**
1. Check `config.py` includes your frontend URL in `CORS_ORIGINS`
2. Ensure frontend URL matches exactly (including protocol and port)
3. Restart the backend after changing CORS settings

### Issue: Connection Timeout

**Symptoms:**
- Requests hang or timeout
- No response from backend

**Solutions:**
1. Verify backend is running on the expected port
2. Check if another service is using the port:
   ```bash
   lsof -i :8000  # Mac/Linux
   netstat -ano | findstr :8000  # Windows
   ```
3. Check firewall settings
4. Try accessing the health endpoint directly in browser

### Issue: Wrong Backend Port

**Symptoms:**
- Frontend connects but gets 404 errors
- Health check fails

**Solutions:**
1. Update `VITE_BACKEND_API_URL` to match your backend port
2. Or update backend to use default port 8000

## Development Workflow

### Local Development (Recommended)

1. **Start the backend:**
   ```bash
   python main.py
   ```
   Backend runs on `http://localhost:8000`

2. **Start the frontend:**
   ```bash
   npm run dev
   ```
   Frontend runs on `http://localhost:8080`

3. **Upload an image** - The frontend will automatically connect to the backend

### With Supabase Only

1. Set Supabase environment variables
2. Deploy Supabase Edge Function
3. Frontend will automatically use Supabase when backend is unavailable

## API Endpoints

### Direct Backend API

- `GET /health` - Health check
- `POST /predict` - Image prediction (multipart/form-data with `file`)
- `GET /model/info` - Model information

### Flask Backend API

- `GET /api/health` - Health check
- `POST /api/predict` - Image prediction (multipart/form-data with `image`)
- `GET /api/model/info` - Model information

## Environment Variables Summary

### Backend
```env
PORT=8000
HOST=0.0.0.0
CORS_ORIGINS=http://localhost:8080,http://localhost:3000
DEBUG=False
MODEL_PATH=models/retina_model.h5
```

### Frontend
```env
VITE_BACKEND_API_URL=http://localhost:8000
VITE_SUPABASE_URL=https://your-project.supabase.co
VITE_SUPABASE_PUBLISHABLE_KEY=your-key
```

## Code Structure

### Backend API Service
Located at: `src/services/backendApi.ts`
- Handles all direct backend API calls
- Provides health check, prediction, and model info methods
- Automatic error handling and response validation

### Image Upload Component
Located at: `src/components/ImageUpload.tsx`
- Tries direct backend API first
- Falls back to Supabase Edge Functions
- Provides clear error messages

### Configuration
Located at: `src/lib/config.ts`
- Centralized configuration management
- Environment variable handling
- Development logging

