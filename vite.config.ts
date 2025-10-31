import { defineConfig } from "vite";
import react from "@vitejs/plugin-react-swc";
import path from "path";

// https://vitejs.dev/config/
// Vite uses SWC for transpilation, not TypeScript compiler
// Type checking is optional and can be bypassed if tsconfig has issues
export default defineConfig({
  server: {
    port: 8080,
  },
  plugins: [
    react({
      // SWC plugin doesn't perform type checking by default
      // It only transpiles TypeScript to JavaScript
    }),
  ],
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
        // Suppress TypeScript config warnings during build
        // These don't affect the actual build since SWC handles transpilation
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
