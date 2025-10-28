import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { AlertCircle, CheckCircle, AlertTriangle } from "lucide-react";

interface DiagnosisResultProps {
  prediction: {
    severity_class: number;
    severity_level: string;
    confidence: number;
    label: string;
    recommendation: string;
    class_probabilities: Record<string, number>;
  };
}

export function DiagnosisResult({ prediction }: DiagnosisResultProps) {
  const getSeverityColor = (severity: number) => {
    if (severity === 0) return "text-green-500";
    if (severity === 1) return "text-yellow-500";
    if (severity === 2) return "text-orange-500";
    return "text-red-500";
  };

  const getSeverityIcon = (severity: number) => {
    if (severity === 0) return <CheckCircle className="w-6 h-6" />;
    if (severity <= 2) return <AlertTriangle className="w-6 h-6" />;
    return <AlertCircle className="w-6 h-6" />;
  };

  return (
    <Card className="p-6 animate-in fade-in slide-in-from-right duration-500">
      <h2 className="text-2xl font-semibold mb-4">Diagnosis Result</h2>
      
      <div className="space-y-6">
        <div className="flex items-center gap-3">
          <div className={getSeverityColor(prediction.severity_class)}>
            {getSeverityIcon(prediction.severity_class)}
          </div>
          <div className="flex-1">
            <h3 className="font-semibold text-lg">{prediction.label}</h3>
            <Badge variant={prediction.severity_class === 0 ? "default" : "destructive"}>
              {prediction.severity_level}
            </Badge>
          </div>
        </div>

        <div>
          <div className="flex justify-between mb-2">
            <span className="text-sm font-medium">Confidence</span>
            <span className="text-sm font-medium">{(prediction.confidence * 100).toFixed(1)}%</span>
          </div>
          <Progress value={prediction.confidence * 100} className="h-2" />
        </div>

        <div className="bg-muted/50 p-4 rounded-lg">
          <h4 className="font-semibold mb-2">Recommendation</h4>
          <p className="text-sm text-muted-foreground">{prediction.recommendation}</p>
        </div>

        <div>
          <h4 className="font-semibold mb-3">Class Probabilities</h4>
          <div className="space-y-2">
            {Object.entries(prediction.class_probabilities).map(([cls, prob]) => (
              <div key={cls}>
                <div className="flex justify-between text-sm mb-1">
                  <span>{cls.replace("class_", "Class ")}</span>
                  <span>{(prob * 100).toFixed(1)}%</span>
                </div>
                <Progress value={prob * 100} className="h-1" />
              </div>
            ))}
          </div>
        </div>
      </div>
    </Card>
  );
}
