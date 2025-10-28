# RetinaScan AI - Vite Deployment Guide

## Problem Summary

The "Cannot find module 'dep-COdkJwUb.js'" error was caused by:
1. Corrupted `node_modules` installation
2. Missing Vite chunk files during development
3. Missing HMR and optimization configurations

## Fixes Applied

### 1. Updated `vite.config.ts`

Added comprehensive configuration:
- HMR settings with WebSocket protocol
- `optimizeDeps` to pre-bundle React and React Query
- Manual chunk splitting for better performance
- ESBuild target configuration

### 2. Fixed Dependencies

Ran a clean reinstall:
```bash
rm -rf node_modules package-lock.json
npm install
```

This restored the missing Vite chunk files in `node_modules/vite/dist/node/chunks/`.

## Running Locally

From the **repository root**:

```bash
# Install dependencies (if not already done)
npm install

# Start dev server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview
```

## Deployment to Lovable (or similar platforms)

### Configuration

1. **Set project root**: Point Lovable to the repository root (`/Users/llow/Desktop/retina-zero-code`)

2. **Build command**:
   ```bash
   npm ci && npm run build
   ```

3. **Publish directory**: `dist`

4. **Environment variables** (set in Lovable):
   - `VITE_SUPABASE_URL` - Your Supabase project URL
   - `VITE_SUPABASE_PUBLISHABLE_KEY` - Your Supabase anon/public key

### Why This Works

- The updated `vite.config.ts` handles chunk resolution issues
- Manual chunk splitting prevents missing dependency errors
- Production build (`npm run build`) creates a self-contained `dist/` folder
- Vite preview serves the built assets without relying on dev-only features

## Troubleshooting

### If the error persists on deploy:

1. **Clean install**:
   ```bash
   rm -rf node_modules package-lock.json
   npm ci
   ```

2. **Check Node version**:
   ```bash
   node -v  # Should be 16.14+ or 18+
   ```

3. **Verify Vite chunks exist**:
   ```bash
   ls -la node_modules/vite/dist/node/chunks/
   ```
   Should list several `.js` files (like `dep-BB45zftN.js`).

4. **Try production build locally first**:
   ```bash
   npm run build
   npm run preview
   ```

## Architecture Notes

This project has **two frontend setups**:
- **Root `src/`**: Vite + React + TypeScript (the active one)
- **`retinascan-frontend/`**: Create React App (not currently used)

Ensure Lovable is configured for the root Vite setup, not the `retinascan-frontend` folder.

