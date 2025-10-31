# Deployment Guide for Manus

This guide will help you deploy RetinaScan AI to Manus platform.

## Prerequisites

- Node.js 18+ (specified in `.nvmrc`)
- All environment variables configured
- Git repository ready

## Build Configuration

### Build Command
```bash
npm ci && npm run build
```

Or if using the safe build script:
```bash
npm ci && node scripts/build-safe.js
```

### Output Directory
- **Output Directory**: `dist`
- **Public Directory**: `public` (if needed for static assets)

### Node Version
- **Required**: Node.js 18.x (see `.nvmrc`)

## Environment Variables

Set these in your Manus deployment settings:

### Required for Production
- `VITE_API_BASE_URL` - Backend API URL (if using Flask backend)
- `VITE_SUPABASE_URL` - Supabase project URL (if using Supabase)
- `VITE_SUPABASE_PUBLISHABLE_KEY` - Supabase anon/public key (if using Supabase)

### Optional
- `VITE_BASE_PATH` - Base path for the app (default: `/`)
- `NODE_ENV` - Set to `production` (usually set automatically)

## Build Process

The build process:
1. Installs dependencies with `npm ci`
2. Runs `npm run build` which executes `scripts/build-safe.js`
3. Generates optimized chunks in `dist/` directory
4. Creates vendor chunks for better caching:
   - `react` - React, React DOM, React Router
   - `ui` - Radix UI components
   - `query` - TanStack Query
   - `charts` - Recharts
   - `supabase` - Supabase client

## Build Output

After build, you'll have:
```
dist/
├── index.html
└── assets/
    ├── index-[hash].js      (main app bundle)
    ├── react-[hash].js      (React vendor chunk)
    ├── query-[hash].js      (TanStack Query chunk)
    ├── ui-[hash].js         (UI components chunk)
    ├── charts-[hash].js      (Charts chunk)
    └── index-[hash].css     (styles)
```

## Deployment Settings

### Manus Configuration

1. **Build Command**: `npm ci && npm run build`
2. **Output Directory**: `dist`
3. **Node Version**: 18.x
4. **Install Command**: `npm ci` (or `npm install`)

### Environment Variables in Manus

Add these in your Manus dashboard:
```
VITE_API_BASE_URL=https://your-backend-url.com
VITE_SUPABASE_URL=https://your-project.supabase.co
VITE_SUPABASE_PUBLISHABLE_KEY=your-anon-key
```

## Troubleshooting

### Build Fails with TS6310 Error
- The build script automatically bypasses TypeScript checking
- If issues persist, check that `scripts/build-safe.js` is executable

### Missing Environment Variables
- The app will show a configuration warning if required vars are missing
- Check browser console for configuration status

### Chunk Loading Errors
- Ensure `VITE_BASE_PATH` is set correctly if deploying to a subdirectory
- Check that all chunks are uploaded to the correct path

### Build Takes Too Long
- This is normal for first build (7-8 seconds)
- Subsequent builds with cache should be faster

## Verification

After deployment, verify:
1. ✅ App loads without errors
2. ✅ Environment variables are loaded correctly
3. ✅ API calls work (check Network tab)
4. ✅ All routes work correctly
5. ✅ Images upload and process correctly

## Performance Optimizations

The build includes:
- ✅ Code splitting with manual chunks
- ✅ Tree shaking for unused code
- ✅ Minification enabled in production
- ✅ CSS code splitting
- ✅ Optimized vendor chunks for better caching

## Support

If you encounter issues:
1. Check build logs in Manus dashboard
2. Verify environment variables are set
3. Check browser console for runtime errors
4. Verify Node.js version is 18.x

