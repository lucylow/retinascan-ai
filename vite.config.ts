import { defineConfig } from "vite";
import react from "@vitejs/plugin-react-swc";
import path from "path";

// https://vitejs.dev/config/
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
