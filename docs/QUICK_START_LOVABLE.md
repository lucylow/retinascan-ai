# Quick Start Guide - RetinaScan AI on Lovable

## 🚀 Quick Setup (5 minutes)

### Step 1: Environment Variables in Lovable
Go to Lovable Dashboard → Settings → Environment Variables and add:

```bash
VITE_SUPABASE_URL=https://your-project-id.supabase.co
VITE_SUPABASE_PUBLISHABLE_KEY=your-anon-key
```

### Step 2: Deploy Supabase Edge Function
Run in your terminal:

```bash
# Install Supabase CLI if needed
# npm install -g supabase

# Login to Supabase
supabase login

# Link to your project
supabase link --project-ref your-project-id

# Deploy the function
supabase functions deploy analyze-retina

# Set the secret
supabase secrets set LOVABLE_API_KEY=your-lovable-api-key --project-ref your-project-id
```

### Step 3: Deploy to Lovable
Push your code to Lovable - the app will automatically build and deploy!

### Step 4: Test
1. Open your app in Lovable
2. Upload a retinal fundus image
3. Click "Analyze Image"
4. View the results!

## 📋 What You Need

1. **Supabase Account** - Free tier works fine
2. **Lovable API Key** - From your Lovable dashboard
3. **Images** - Retinal fundus images (PNG, JPG, JPEG, max 16MB)

## ✅ Verification

After deployment, you should:
- ✅ See no "Configuration Required" warning
- ✅ Be able to upload images
- ✅ See analysis results with severity level
- ✅ See structured recommendations
- ✅ See class probabilities

## 🐛 Troubleshooting

### Warning Banner Shows
**Fix**: Set environment variables in Lovable settings

### "LOVABLE_API_KEY not configured"
**Fix**: Set secret in Supabase Edge Functions:
```bash
supabase secrets set LOVABLE_API_KEY=your-key
```

### Analysis fails
**Check**:
1. Browser console for errors
2. Supabase Edge Function logs
3. Lovable API key has credits

## 📚 More Details

- **Detailed Setup**: See `LOVABLE_SETUP.md`
- **Deployment Steps**: See `DEPLOYMENT_CHECKLIST.md`
- **Changes Made**: See `CONNECTIVITY_FIXES_SUMMARY.md`

## 🔗 Important Links

- Lovable Dashboard: https://lovable.dev
- Supabase Dashboard: https://app.supabase.com
- RetinaScan AI on Lovable: (your app URL)

---

**Ready to deploy?** Follow the 4 steps above and you're done! 🎉

