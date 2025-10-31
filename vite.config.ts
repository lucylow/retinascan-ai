import { defineConfig } from "vite";
import react from "@vitejs/plugin-react-swc";
import path from "path";

// https://vitejs.dev/config/
// Note: TS6310 error may appear during type checking due to read-only tsconfig files on Lovable platform.
// This does not affect Vite builds, which use SWC for transpilation (not TypeScript compilation).
// For type checking, use `npm run typecheck` which uses a workaround script to bypass project references.
export default defineConfig({
  server: {
    port: 8080,
  },
  plugins: [react()],
  resolve: {
    alias: {
      "@": path.resolve(process.cwd(), "src"),
    },
  },
  build: {
    target: 'es2020',
    sourcemap: false,
    minify: 'esbuild',
    rollupOptions: {
      onwarn(warning, warn) {
        // Suppress all warnings during build
        if (warning.code === 'PLUGIN_WARNING') return;
        if (warning.code === 'UNRESOLVED_IMPORT') return;
        warn(warning);
      },
    },
  },
  esbuild: {
    logOverride: { 
      'this-is-undefined-in-esm': 'silent',
    },
  },
  optimizeDeps: {
    exclude: ['@typescript/vfs'],
  },
});
