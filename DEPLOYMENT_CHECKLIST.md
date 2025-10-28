# RetinaScan AI - Lovable Deployment Checklist

## Pre-Deployment

### 1. Environment Variables Setup

#### For Lovable Platform:
Add these in your Lovable project settings (Settings → Environment Variables):

- `VITE_SUPABASE_URL` - Your Supabase project URL
- `VITE_SUPABASE_PUBLISHABLE_KEY` - Your Supabase anon/public key

#### For Supabase Edge Functions:
Set these secrets in Supabase Dashboard (Edge Functions → analyze-retina → Settings → Secrets):

- `LOVABLE_API_KEY` - Your Lovable API key

### 2. Supabase Configuration

1. Deploy the Edge Function:
   ```bash
   supabase functions deploy analyze-retina
   ```

2. Verify function is deployed:
   - Go to Supabase Dashboard → Edge Functions
   - Check that `analyze-retina` function is active

3. Set the secret:
   ```bash
   supabase secrets set LOVABLE_API_KEY=your-key-here --project-ref your-project-id
   ```

### 3. Frontend Build

The app will automatically build when you push to Lovable. The build process:
- Compiles TypeScript
- Bundles assets
- Creates optimized production build
- Serves on Lovable's CDN

## Verification Steps

### 1. Check Configuration
- Open the app in Lovable
- Look for the configuration warning banner at the top
- If missing env vars, you'll see a yellow warning card

### 2. Test Image Upload
1. Click "Upload Retinal Image" or drop an image
2. Supported formats: PNG, JPG, JPEG (max 16MB)
3. Click "Analyze Image"
4. Wait for analysis (typically 5-15 seconds)

### 3. Verify Results
- Check that prediction results display correctly
- Verify severity level is shown
- Check confidence score is displayed
- Ensure class probabilities are shown
- Verify structured recommendations appear

### 4. Check Browser Console
- Open DevTools (F12)
- Look for any errors
- Verify Supabase connection messages
- Check network requests to Supabase Edge Function

## Common Issues

### Issue: "Configuration Required" warning
**Solution**: Set `VITE_SUPABASE_URL` and `VITE_SUPABASE_PUBLISHABLE_KEY` in Lovable environment variables

### Issue: "LOVABLE_API_KEY not configured"
**Solution**: Set the secret in Supabase Edge Functions:
1. Go to Supabase Dashboard
2. Edge Functions → analyze-retina → Settings
3. Add secret: `LOVABLE_API_KEY`

### Issue: "Analysis failed"
**Possible causes**:
- Supabase Edge Function not deployed
- LOVABLE_API_KEY not set or invalid
- Rate limit exceeded
- Invalid image format

**Solutions**:
- Check Supabase Edge Function logs
- Verify API key is correct
- Try with a different image
- Check rate limit status in Lovable dashboard

### Issue: No response from analysis
**Solutions**:
- Check Supabase Edge Function is invoked (network tab)
- Verify edge function logs in Supabase dashboard
- Check if LOVABLE_API_KEY has sufficient credits

## Post-Deployment

### 1. Monitor Usage
- Check Lovable API usage dashboard
- Monitor Supabase Edge Function logs
- Track error rates

### 2. Optimize Performance
- Consider caching frequent predictions
- Implement rate limiting
- Add retry logic for failed requests

### 3. Scale Configuration
- Adjust API key limits if needed
- Configure Supabase Edge Function concurrency
- Set up monitoring alerts

## Architecture Flow

```
User uploads image
    ↓
Frontend (React/Vite)
    ↓
Image converted to base64 data URL
    ↓
Supabase Edge Function invoked
    ↓
Edge Function receives image
    ↓
Calls Lovable AI Gateway (google/gemini-2.5-flash)
    ↓
AI analyzes retinal image
    ↓
Returns structured diagnosis
    ↓
Edge Function adds structured_recommendation
    ↓
Frontend receives and displays results
```

## Testing Checklist

- [ ] Environment variables set in Lovable
- [ ] LOVABLE_API_KEY set in Supabase Edge Functions
- [ ] Can upload image successfully
- [ ] Analysis completes without errors
- [ ] Results display correctly with all fields
- [ ] Structured recommendations appear
- [ ] Class probabilities are shown
- [ ] No console errors
- [ ] Warning banner disappears after config

## Support

For issues:
1. Check LOVABLE_SETUP.md for detailed setup
2. Review Supabase Edge Function logs
3. Check Lovable API dashboard for usage/errors
4. Verify environment variables are set correctly

