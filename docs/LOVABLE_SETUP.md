# RetinaScan AI - Lovable Setup Guide

This guide will help you set up and deploy RetinaScan AI on Lovable.

## Overview

RetinaScan AI uses Supabase Edge Functions to call Lovable's AI Gateway for retinal image analysis. The architecture is:

```
Frontend (React/Vite) → Supabase Edge Function → Lovable AI Gateway
```

## Environment Variables

### Required for Lovable Deployment

Set these in your Lovable project settings:

1. **LOVABLE_API_KEY**
   - Your Lovable API key for accessing the AI Gateway
   - Get it from your Lovable dashboard

### Supabase Configuration

Set these in your Supabase project settings (under Project Settings → API):

1. **VITE_SUPABASE_URL**
   - Your Supabase project URL
   - Format: `https://your-project-id.supabase.co`

2. **VITE_SUPABASE_PUBLISHABLE_KEY**
   - Your Supabase anon/public key
   - Get it from Supabase Dashboard → API Settings

3. **LOVABLE_API_KEY** (in Supabase)
   - Set this as a secret in Supabase Edge Function secrets
   - Go to Supabase Dashboard → Edge Functions → Secrets
   - Add: `LOVABLE_API_KEY` with your Lovable API key

## Local Development Setup

1. Create a `.env` file in the project root:

```env
VITE_SUPABASE_URL=https://your-project-id.supabase.co
VITE_SUPABASE_PUBLISHABLE_KEY=your-anon-key-here
```

2. For Supabase Edge Functions, set secrets locally:

```bash
supabase secrets set LOVABLE_API_KEY=your-lovable-api-key
```

## Supabase Edge Function

The Edge Function (`supabase/functions/analyze-retina/index.ts`) uses:
- Lovable's AI Gateway with `google/gemini-2.5-flash` vision model
- Processes retinal fundus images for diabetic retinopathy detection
- Returns structured diagnosis with severity levels and recommendations

## Deployment to Lovable

1. Push your code to Lovable
2. Configure environment variables in Lovable settings:
   - Go to Settings → Environment Variables
   - Add all required variables listed above
3. The app will automatically connect to Supabase and use your configured Lovable API key

## Testing

After deployment:

1. Upload a retinal fundus image
2. Click "Analyze Image"
3. The image is sent to Supabase Edge Function
4. Edge Function calls Lovable AI Gateway for analysis
5. Results are displayed with severity classification and recommendations

## Troubleshooting

### Error: "LOVABLE_API_KEY not configured"
- Make sure you've set the secret in Supabase Edge Functions
- Go to Supabase Dashboard → Edge Functions → analyze-retina → Settings → Secrets

### Error: "Supabase client not initialized"
- Check that VITE_SUPABASE_URL and VITE_SUPABASE_PUBLISHABLE_KEY are set
- Verify the keys are correct in Lovable environment variables

### No results showing
- Open browser console to see error messages
- Check Supabase Edge Function logs in dashboard
- Verify image format is supported (PNG, JPG, JPEG)

## API Response Format

The Edge Function returns:

```json
{
  "severity_class": 0-4,
  "severity_level": "None|Mild|Moderate|Severe|Proliferative",
  "confidence": 0-1,
  "label": "Full diagnosis label",
  "recommendation": "Clinical recommendation text",
  "structured_recommendation": {
    "action": "Recommended action",
    "urgency": "Urgency level",
    "follow_up_time": "When to follow up",
    "note": "Additional notes"
  },
  "class_probabilities": {
    "class_0": 0-1,
    "class_1": 0-1,
    "class_2": 0-1,
    "class_3": 0-1,
    "class_4": 0-1
  }
}
```

## Severity Levels

- **0 - No DR**: No diabetic retinopathy detected
- **1 - Mild**: Mild non-proliferative diabetic retinopathy
- **2 - Moderate**: Moderate non-proliferative diabetic retinopathy
- **3 - Severe**: Severe non-proliferative diabetic retinopathy
- **4 - Proliferative**: Proliferative diabetic retinopathy

---

**Note**: This is a medical AI tool for research and educational purposes only. Always consult qualified healthcare professionals for medical diagnosis.

