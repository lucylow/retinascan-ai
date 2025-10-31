import { defineConfig } from "vite";
import react from "@vitejs/plugin-react-swc";
import path from "path";

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      // Correctly resolve the '@' alias using process.cwd()
      // This works in any environment (CommonJS, ES Modules, etc.)
      "@": path.resolve(process.cwd(), "frontend/src"),
    },
  },
  build: {
    target: 'es2020',
    sourcemap: false,
  },
});
