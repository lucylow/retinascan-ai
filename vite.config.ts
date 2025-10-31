import { defineConfig } from "vite";
import react from "@vitejs/plugin-react-swc";
import path from "path";

// https://vitejs.dev/config/
// Production-optimized Vite configuration
// Supports deployment with proper chunk splitting and error handling
export default defineConfig(({ mode }) => {
  const isProduction = mode === "production";
  
  return {
    server: {
      port: 8080,
      host: true, // Listen on all addresses for containerized deployments
      proxy: {
        // Proxy API requests to backend during development
        '/api': {
          target: 'http://localhost:5000',
          changeOrigin: true,
          secure: false,
          rewrite: (path) => path, // Keep /api prefix
        },
      },
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
    base: process.env.VITE_BASE_PATH || "/",
    build: {
      target: "es2020",
      outDir: "dist",
      assetsDir: "assets",
      sourcemap: false,
      minify: isProduction ? "esbuild" : false,
      cssCodeSplit: true,
      chunkSizeWarningLimit: 1000,
      rollupOptions: {
        output: {
          manualChunks: {
            // Vendor chunks for better caching
            react: ["react", "react-dom", "react-router-dom"],
            ui: ["@radix-ui/react-progress", "@radix-ui/react-slot", "@radix-ui/react-toast"],
            charts: ["recharts"],
            query: ["@tanstack/react-query"],
            supabase: ["@supabase/supabase-js"],
          },
          chunkFileNames: "assets/[name]-[hash].js",
          entryFileNames: "assets/[name]-[hash].js",
          assetFileNames: "assets/[name]-[hash].[ext]",
        },
        onwarn(warning, warn) {
          // Suppress known warnings that don't affect functionality
          if (warning.code === "PLUGIN_WARNING") return;
          if (warning.code === "UNRESOLVED_IMPORT") return;
          if (warning.code === "EMPTY_BUNDLE") return;
          warn(warning);
        },
      },
    },
    esbuild: {
      logOverride: {
        "this-is-undefined-in-esm": "silent",
      },
    },
    optimizeDeps: {
      include: [
        "react",
        "react-dom",
        "react-router-dom",
        "@tanstack/react-query",
        "@supabase/supabase-js",
      ],
      exclude: ["@typescript/vfs"],
    },
  };
});
