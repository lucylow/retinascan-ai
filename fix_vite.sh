#!/usr/bin/env bash
set -euo pipefail
echo "=== RetinaScan AI: Cursor diagnostic + quick-fix script ==="

# 1) choose frontend folder if present
if [ -d "retinascan-frontend" ]; then
  FRONTEND_DIR="retinascan-frontend"
else
  FRONTEND_DIR="."
fi
echo "Using frontend dir: $FRONTEND_DIR"
cd "$FRONTEND_DIR"

# 2) ensure Node (try nvm if available)
REQUIRED_NODE_MAJOR=18
NODE_OK=false
if command -v node >/dev/null 2>&1; then
  NV=$(node -v | sed 's/v//')
  echo "Found node v$NV"
  MAJ=$(echo "$NV" | cut -d. -f1)
  if [ "$MAJ" -ge "$REQUIRED_NODE_MAJOR" ]; then
    NODE_OK=true
  else
    echo "Node version < $REQUIRED_NODE_MAJOR; attempting nvm if present..."
  fi
fi
if [ "$NODE_OK" = false ] && command -v nvm >/dev/null 2>&1; then
  echo "nvm found — installing/using node $REQUIRED_NODE_MAJOR..."
  nvm install $REQUIRED_NODE_MAJOR || true
  nvm use $REQUIRED_NODE_MAJOR || true
  echo "Now node: $(node -v || echo 'node missing')"
fi
echo

# 3) clean and reinstall dependencies
echo "Removing node_modules and lockfiles..."
rm -rf node_modules package-lock.json yarn.lock pnpm-lock.yaml
echo "Installing dependencies (npm ci if package-lock exists fallback to npm install)..."
if [ -f package-lock.json ]; then
  npm ci --prefer-offline --no-audit --progress=false || npm install
else
  npm install --no-audit --progress=false
fi
echo "Install finished."
echo

# 4) check vite present and list chunk dir (diagnose missing chunk error)
echo "Vite info:"
npm ls vite --depth=0 || true
echo "Vite binary/version:"
npx vite --version || true
echo

# 5) attempt a production build (recommended fix for /dev-server chunk problems)
echo "Attempting production build (this avoids dev server HMR overlay issues)..."
set +e
npm run build
BUILD_RC=$?
set -e
if [ $BUILD_RC -eq 0 ]; then
  echo "✅ Production build succeeded. Use the 'dist' output for deployment (avoid running 'vite dev' on no-code hosts)."
  exit 0
fi

# 6) If build failed, run diagnostics targeted to the reported error
echo
echo "❌ Production build FAILED (exit code $BUILD_RC). Running focused diagnostics to find why the Vite chunks are missing..."
echo "Listing vite dist chunks (if installed):"
if [ -d node_modules/vite/dist/node/chunks ]; then
  echo "node_modules/vite/dist/node/chunks (sample):"
  ls -la node_modules/vite/dist/node/chunks | head -n 40 || true
else
  echo "node_modules/vite/dist/node/chunks does not exist."
fi
echo

echo "=== show top of vite.config.* (if present) ==="
for f in vite.config.ts vite.config.js vite.config.mjs; do
  if [ -f "$f" ]; then
    echo "----- $f -----"
    sed -n '1,200p' "$f"
    echo "----------------"
  fi
done
echo

echo "=== show package.json scripts ==="
if [ -f package.json ]; then
  jq '{name: .name, scripts: .scripts, dependencies: .dependencies, devDependencies: .devDependencies}' package.json 2>/dev/null || cat package.json
fi
echo

echo "=== show last 200 lines of npm install logs (if any) ==="
if [ -f npm-debug.log ]; then tail -n 200 npm-debug.log; fi
echo

# 7) Try quick patch: disable HMR overlay for dev-run only and prebundle optimizeDeps
# (we will create a small temporary vite debug config and run build with it)
TMP_CFG="./.vite.debug.config.js"
echo "Creating temporary Vite override config at $TMP_CFG (disables HMR overlay & forces prebundle include)..."
cat > "$TMP_CFG" <<'EOF'
import { defineConfig } from 'vite'
export default defineConfig({
  server: {
    hmr: {
      overlay: false
    }
  },
  optimizeDeps: {
    include: ['react', 'react-dom', 'vue', '@vitejs/plugin-react', 'lodash'].filter(Boolean)
  }
})
EOF

echo "Attempting build with override config: npx vite build --config $TMP_CFG"
set +e
npx vite build --config "$TMP_CFG"
OVERRIDE_RC=$?
set -e
if [ $OVERRIDE_RC -eq 0 ]; then
  echo "✅ Build with override config succeeded. Deploy using the produced /dist. Consider adding server.hmr.overlay=false and required optimizeDeps to your main vite.config.ts."
  rm -f "$TMP_CFG"
  exit 0
fi

# 8) If override also failed, print helpful next steps / one-line fixes
echo
echo "=== Diagnostics summary ==="
echo "- Build exit code: $BUILD_RC"
echo "- Build with override exit code: $OVERRIDE_RC"
echo
echo "Common causes for the '/dev-server/... dep-*.js missing' error:"
echo "  1) Running vite dev on a host that mounts code under /dev-server (the dev wrapper path mismatches prebundle chunks)"
echo "  2) Corrupt/incomplete node_modules (lockfile mismatch or interrupted install)"
echo "  3) Vite version mismatch or missing prebundled chunks"
echo
echo "Suggested next actions (pick one):"
echo "A) Deploy the static production build output (recommended for no-code hosts):"
echo "   -> Ensure build succeeds locally, then upload the 'dist' directory (or configure host to run 'npm run build' and publish 'dist')."
echo
echo "B) Force clean, re-install and prebundle (if you must run dev on the host):"
echo "   -> Run these commands (copy-paste):"
echo "      rm -rf node_modules package-lock.json && npm i --prefer-offline --no-audit"
echo "      npx vite --force   # forces dependency pre-bundle"
echo
echo "C) If the host injects a wrapper path like /dev-server, avoid 'vite dev' there. Instead run a production build or use a host that runs your 'build' script."
echo
echo "D) Paste the output of these files (so I can give exact patch):"
echo "   - retinascan-frontend/package.json (scripts) "
echo "   - retinascan-frontend/vite.config.* (contents) "
echo "   - output of: ls -la node_modules/vite/dist/node/chunks"
echo
echo "If you want, run this command now to collect a single paste-friendly diagnostics bundle:"
echo "  (cd $FRONTEND_DIR && { echo '--- package.json ---'; cat package.json; echo; echo '--- vite.config.ts head ---'; head -n 200 vite.config.ts 2>/dev/null || true; echo; echo '--- vite chunks listing ---'; ls -la node_modules/vite/dist/node/chunks 2>/dev/null || true; } ) > /tmp/retinascan-diagnostics.txt && echo '/tmp/retinascan-diagnostics.txt created'"

exit 1
