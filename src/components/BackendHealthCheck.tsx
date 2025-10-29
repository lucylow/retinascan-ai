/**
 * Backend Health Check Component
 * Allows users to test backend API connectivity and CORS configuration
 */
import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { backendApi, type HealthResponse } from "@/services/backendApi";
import { config } from "@/lib/config";
import { CheckCircle2, XCircle, Loader2, ExternalLink, AlertCircle } from "lucide-react";

export function BackendHealthCheck() {
  const [healthStatus, setHealthStatus] = useState<{
    status: "not-checked" | "checking" | "success" | "error";
    message: string;
    healthData?: HealthResponse;
    error?: string;
  }>({
    status: "not-checked",
    message: "Not checked",
  });

  const checkHealth = async () => {
    setHealthStatus({
      status: "checking",
      message: "Checking backend health...",
    });

    try {
      const healthData = await backendApi.healthCheck();
      setHealthStatus({
        status: "success",
        message: `Backend is healthy! Model loaded: ${healthData.model_loaded ? "Yes" : "No"}`,
        healthData,
      });
    } catch (error: any) {
      console.error("Health check error:", error);
      
      // Provide helpful error messages
      let errorMessage = error.message || "Unknown error";
      if (errorMessage.includes("CORS") || errorMessage.includes("Failed to fetch")) {
        errorMessage = `CORS Error: The backend may not be configured to allow requests from this domain. Check your backend CORS_ORIGINS configuration.`;
      } else if (errorMessage.includes("NetworkError") || errorMessage.includes("network")) {
        errorMessage = `Network Error: The backend API may not be accessible. Check the VITE_BACKEND_API_URL environment variable.`;
      }

      setHealthStatus({
        status: "error",
        message: "Backend health check failed",
        error: errorMessage,
      });
    }
  };

  const apiUrl = config.backend.apiUrl;
  // Ensure docs URL is valid even if apiUrl ends with a slash
  const docsUrl = `${apiUrl.replace(/\/$/, '')}/docs`;

  return (
    <Card className="p-6 border-2">
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="text-lg font-semibold mb-1">Backend API Health Check</h3>
            <p className="text-sm text-muted-foreground">
              Test the connection to your RetinaScan AI backend
            </p>
          </div>
          {healthStatus.status === "checking" && (
            <Loader2 className="w-5 h-5 animate-spin text-primary" />
          )}
          {healthStatus.status === "success" && (
            <CheckCircle2 className="w-5 h-5 text-green-500" />
          )}
          {healthStatus.status === "error" && (
            <XCircle className="w-5 h-5 text-red-500" />
          )}
        </div>

        <div className="space-y-2">
          <div className="flex items-center gap-2 text-sm">
            <span className="text-muted-foreground">API URL:</span>
            <code className="bg-muted px-2 py-1 rounded text-xs font-mono">
              {apiUrl}
            </code>
          </div>

          {healthStatus.status === "not-checked" && (
            <p className="text-sm text-muted-foreground">
              Click the button below to verify backend connectivity and CORS configuration.
            </p>
          )}

          {healthStatus.status === "success" && healthStatus.healthData && (
            <div className="space-y-2 p-3 bg-green-50 dark:bg-green-950 rounded-md">
              <div className="flex items-center gap-2 text-sm text-green-800 dark:text-green-200">
                <CheckCircle2 className="w-4 h-4" />
                <span className="font-semibold">{healthStatus.message}</span>
              </div>
              {healthStatus.healthData.model_info && (
                <div className="text-xs text-green-700 dark:text-green-300 ml-6 space-y-1">
                  <div>Status: {healthStatus.healthData.status}</div>
                  <div>
                    Model Info: {healthStatus.healthData.model_info.input_shape || "N/A"}
                  </div>
                  <div>Timestamp: {new Date(healthStatus.healthData.timestamp).toLocaleString()}</div>
                </div>
              )}
            </div>
          )}

          {healthStatus.status === "error" && (
            <div className="space-y-2 p-3 bg-red-50 dark:bg-red-950 rounded-md">
              <div className="flex items-start gap-2 text-sm text-red-800 dark:text-red-200">
                <AlertCircle className="w-4 h-4 mt-0.5 flex-shrink-0" />
                <div className="flex-1">
                  <div className="font-semibold mb-1">{healthStatus.message}</div>
                  <div className="text-xs text-red-700 dark:text-red-300 whitespace-pre-wrap">
                    {healthStatus.error}
                  </div>
                </div>
              </div>
              <div className="text-xs text-red-600 dark:text-red-400 ml-6 space-y-1">
                <p className="font-semibold">Troubleshooting steps:</p>
                <ul className="list-disc list-inside space-y-1">
                  <li>Verify the backend is running and accessible</li>
                  <li>Check that <code className="bg-red-100 dark:bg-red-900 px-1 rounded">VITE_BACKEND_API_URL</code> matches your deployed backend URL</li>
                  <li>Ensure your backend&apos;s <code className="bg-red-100 dark:bg-red-900 px-1 rounded">CORS_ORIGINS</code> includes this domain</li>
                </ul>
              </div>
            </div>
          )}
        </div>

        <div className="flex gap-2">
          <Button
            onClick={checkHealth}
            disabled={healthStatus.status === "checking"}
            variant={healthStatus.status === "success" ? "outline" : "default"}
          >
            {healthStatus.status === "checking" ? (
              <>
                <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                Checking...
              </>
            ) : healthStatus.status === "success" ? (
              "Check Again"
            ) : (
              "Check API Health"
            )}
          </Button>
          <Button
            variant="outline"
            onClick={() => window.open(docsUrl, "_blank")}
            className="flex items-center gap-2"
          >
            <ExternalLink className="w-4 h-4" />
            View API Docs
          </Button>
        </div>
      </div>
    </Card>
  );
}

