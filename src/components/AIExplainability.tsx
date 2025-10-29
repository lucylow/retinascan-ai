import React from 'react';
import { Card } from './ui/card';
import { Progress } from './ui/progress';
import { Badge } from './ui/badge';
import { Tooltip } from './ui/Tooltip';
import { Info, TrendingUp, AlertTriangle } from 'lucide-react';
import { PredictionResponse } from '@/lib/validation';

interface AIExplainabilityProps {
  prediction: PredictionResponse;
  imageSrc?: string;
}

/**
 * AI Explainability component for transparency
 * Visualizes AI decision-making and confidence
 */
export const AIExplainability: React.FC<AIExplainabilityProps> = ({
  prediction,
  imageSrc,
}) => {
  const getConfidenceColor = (confidence: number): string => {
    if (confidence >= 0.8) return 'text-green-600';
    if (confidence >= 0.6) return 'text-yellow-600';
    return 'text-orange-600';
  };

  const getConfidenceBadge = (confidence: number): string => {
    if (confidence >= 0.9) return 'Very High';
    if (confidence >= 0.8) return 'High';
    if (confidence >= 0.6) return 'Moderate';
    if (confidence >= 0.4) return 'Low';
    return 'Very Low';
  };

  const confidence = prediction.confidence;
  const uncertainty = prediction.uncertainty?.epistemic || 0;
  const confidenceInterval = prediction.uncertainty?.confidence_interval;

  return (
    <div className="space-y-4">
      <Card className="p-6">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold">AI Confidence & Uncertainty</h3>
          <Tooltip
            content="AI confidence measures how certain the model is about its prediction. Lower confidence may indicate the need for additional review."
            icon="info"
            ariaLabel="Confidence explanation"
          >
            <span />
          </Tooltip>
        </div>

        {/* Confidence Score */}
        <div className="space-y-3 mb-4">
          <div className="flex items-center justify-between">
            <span className="text-sm font-medium">Prediction Confidence</span>
            <div className="flex items-center gap-2">
              <span className={`text-lg font-bold ${getConfidenceColor(confidence)}`}>
                {(confidence * 100).toFixed(1)}%
              </span>
              <Badge variant={confidence >= 0.8 ? 'default' : 'secondary'}>
                {getConfidenceBadge(confidence)}
              </Badge>
            </div>
          </div>
          <Progress value={confidence * 100} className="h-3" />
        </div>

        {/* Uncertainty Score */}
        {uncertainty > 0 && (
          <div className="space-y-3 mb-4 p-3 bg-muted/50 rounded-lg">
            <div className="flex items-center justify-between">
              <span className="text-sm font-medium flex items-center gap-2">
                Model Uncertainty
                <Tooltip
                  content="Uncertainty indicates areas where the AI model is less certain. Higher uncertainty may suggest the need for clinical review."
                  icon="info"
                  ariaLabel="Uncertainty explanation"
                >
                  <span />
                </Tooltip>
              </span>
              <span className={`text-sm font-medium ${uncertainty > 0.3 ? 'text-orange-600' : 'text-gray-600'}`}>
                {(uncertainty * 100).toFixed(1)}%
              </span>
            </div>
            <Progress value={uncertainty * 100} className="h-2" />
          </div>
        )}

        {/* Confidence Interval */}
        {confidenceInterval && (
          <div className="p-3 bg-muted/30 rounded-lg">
            <div className="flex items-center gap-2 mb-2">
              <Info className="w-4 h-4 text-muted-foreground" />
              <span className="text-sm font-medium">Confidence Range</span>
            </div>
            <div className="flex items-center justify-between text-xs text-muted-foreground">
              <span>Lower: {(confidenceInterval.lower * 100).toFixed(1)}%</span>
              <span>Upper: {(confidenceInterval.upper * 100).toFixed(1)}%</span>
            </div>
          </div>
        )}

        {/* Recommendation based on confidence */}
        {confidence < 0.7 && (
          <div className="mt-4 p-3 bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-800 rounded-lg">
            <div className="flex items-start gap-2">
              <AlertTriangle className="w-5 h-5 text-yellow-600 mt-0.5" />
              <div className="flex-1">
                <p className="text-sm font-medium text-yellow-900 dark:text-yellow-100">
                  Lower Confidence Detected
                </p>
                <p className="text-xs text-yellow-700 dark:text-yellow-200 mt-1">
                  The AI prediction has lower confidence. Specialist review is recommended for verification.
                </p>
              </div>
            </div>
          </div>
        )}
      </Card>

      {/* Risk Stratification */}
      {prediction.risk_stratification && (
        <Card className="p-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold">Risk Assessment</h3>
            <TrendingUp className="w-5 h-5 text-muted-foreground" />
          </div>

          <div className="space-y-3">
            <div>
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm font-medium">Risk Level</span>
                <Badge
                  variant={
                    prediction.risk_stratification.risk_level === 'Low'
                      ? 'default'
                      : prediction.risk_stratification.risk_level === 'High'
                      ? 'destructive'
                      : 'secondary'
                  }
                >
                  {prediction.risk_stratification.risk_level}
                </Badge>
              </div>
            </div>

            {prediction.risk_stratification.requires_specialist_review && (
              <div className="p-3 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg">
                <p className="text-sm font-medium text-red-900 dark:text-red-100">
                  ⚠️ Specialist Review Required
                </p>
              </div>
            )}

            <p className="text-sm text-muted-foreground">
              {prediction.risk_stratification.recommendation_note}
            </p>
          </div>
        </Card>
      )}

      {/* Visualization */}
      {prediction.visualization && (
        <Card className="p-6">
          <h3 className="text-lg font-semibold mb-4">AI Decision Visualization</h3>
          
          {prediction.visualization.grad_cam_overlay && imageSrc && (
            <div className="space-y-3">
              <img
                src={prediction.visualization.grad_cam_overlay}
                alt="AI attention visualization"
                className="w-full rounded-lg border"
              />
              {prediction.visualization.description && (
                <p className="text-sm text-muted-foreground">
                  {prediction.visualization.description}
                </p>
              )}
            </div>
          )}

          {prediction.visualization.description && !prediction.visualization.grad_cam_overlay && (
            <div className="p-4 bg-muted/50 rounded-lg">
              <p className="text-sm text-muted-foreground">
                {prediction.visualization.description}
              </p>
            </div>
          )}

          <div className="mt-4 p-3 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
            <p className="text-xs text-blue-900 dark:text-blue-100">
              <strong>How to read this:</strong> Highlighted regions indicate areas the AI model
              focused on when making its diagnosis. Brighter regions had more influence on the decision.
            </p>
          </div>
        </Card>
      )}

      {/* Class Probabilities Breakdown */}
      <Card className="p-6">
        <h3 className="text-lg font-semibold mb-4">Prediction Breakdown</h3>
        <div className="space-y-3">
          {Object.entries(prediction.class_probabilities)
            .sort(([, a], [, b]) => b - a)
            .map(([className, probability]) => (
              <div key={className} className="space-y-1">
                <div className="flex items-center justify-between text-sm">
                  <span className="capitalize">{className.replace(/_/g, ' ')}</span>
                  <span className="font-medium">{(probability * 100).toFixed(1)}%</span>
                </div>
                <Progress
                  value={probability * 100}
                  className="h-2"
                />
              </div>
            ))}
        </div>
      </Card>
    </div>
  );
};

