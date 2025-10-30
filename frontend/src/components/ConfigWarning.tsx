import { AlertTriangle } from "lucide-react";
import { Card } from "@/components/ui/card";
import { config } from "@/lib/config";

export function ConfigWarning() {
  if (config.isConfigured()) {
    return null;
  }

  const missing = config.getMissingConfig();

  return (
    <Card className="p-4 mb-4 border-yellow-500 bg-yellow-50 dark:bg-yellow-950">
      <div className="flex items-start gap-3">
        <AlertTriangle className="w-5 h-5 text-yellow-600 mt-0.5" />
        <div className="flex-1">
          <h3 className="font-semibold text-yellow-800 dark:text-yellow-200 mb-2">
            Configuration Required
          </h3>
          <p className="text-sm text-yellow-700 dark:text-yellow-300 mb-2">
            Please configure the following environment variables:
          </p>
          <ul className="list-disc list-inside text-sm text-yellow-700 dark:text-yellow-300 space-y-1">
            {missing.map((envVar) => (
              <li key={envVar} className="font-mono">{envVar}</li>
            ))}
          </ul>
          <p className="text-xs text-yellow-600 dark:text-yellow-400 mt-3">
            See <code className="bg-yellow-100 dark:bg-yellow-900 px-1 py-0.5 rounded">LOVABLE_SETUP.md</code> for setup instructions.
          </p>
        </div>
      </div>
    </Card>
  );
}

