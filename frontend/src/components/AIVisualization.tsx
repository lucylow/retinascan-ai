import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Badge } from '@/components/ui/badge';
import { ZoomIn, Eye, Activity, TrendingUp } from 'lucide-react';

interface LesionRegion {
  bbox: { x: number; y: number; width: number; height: number };
  confidence: number;
  area: number;
  lesion_type: string;
}

interface Visualizations {
  confidence_chart: string;
  attention_map: string;
  lesion_count: number;
  detected_lesions: LesionRegion[];
}

interface AIVisualizationProps {
  visualizations: Visualizations;
  prediction: any;
}

export const AIVisualization: React.FC<AIVisualizationProps> = ({ visualizations, prediction }) => {
  const [selectedTab, setSelectedTab] = useState('heatmap');
  const [zoomLevel, setZoomLevel] = useState(1);

  const getLesionTypeColor = (type: string) => {
    const colors: Record<string, string> = {
      microaneurysm: 'bg-yellow-500',
      hemorrhage: 'bg-red-500',
      hard_exudate: 'bg-orange-500',
      cotton_wool_spot: 'bg-blue-500',
      abnormality: 'bg-purple-500',
    };
    return colors[type] || 'bg-gray-500';
  };

  const formatLesionType = (type: string) =>
    type
      .split('_')
      .map((w) => w.charAt(0).toUpperCase() + w.slice(1))
      .join(' ');

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center space-x-2">
              <Eye className="h-5 w-5 text-blue-500" />
              <div>
                <p className="text-sm text-gray-500">Detected Lesions</p>
                <p className="text-2xl font-bold">{visualizations.lesion_count}</p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center space-x-2">
              <Activity className="h-5 w-5 text-green-500" />
              <div>
                <p className="text-sm text-gray-500">Confidence</p>
                <p className="text-2xl font-bold">{((prediction.confidence || 0) * 100).toFixed(1)}%</p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center space-x-2">
              <TrendingUp className="h-5 w-5 text-purple-500" />
              <div>
                <p className="text-sm text-gray-500">Severity</p>
                <p className="text-2xl font-bold">{prediction.severity_level}</p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center justify-between">
            <span>AI-Powered Analysis</span>
            <button
              onClick={() => setZoomLevel((z) => Math.min(z + 0.5, 3))}
              className="flex items-center space-x-1 text-sm text-blue-600 hover:text-blue-800"
            >
              <ZoomIn className="h-4 w-4" />
              <span>Zoom</span>
            </button>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <Tabs value={selectedTab} onValueChange={setSelectedTab}>
            <TabsList className="grid w-full grid-cols-3">
              <TabsTrigger value="heatmap">Attention Heatmap</TabsTrigger>
              <TabsTrigger value="confidence">Confidence Analysis</TabsTrigger>
              <TabsTrigger value="lesions">Lesion Detection</TabsTrigger>
            </TabsList>

            <TabsContent value="heatmap" className="space-y-4">
              <div className="relative overflow-auto">
                <img
                  src={visualizations.attention_map}
                  alt="AI Attention Heatmap"
                  className="w-full rounded-lg"
                  style={{ transform: `scale(${zoomLevel})`, transformOrigin: 'top left' }}
                />
              </div>
              <div className="bg-blue-50 p-4 rounded-lg">
                <p className="text-sm text-blue-800">
                  <strong>Explainability:</strong> The heatmap highlights regions that influenced the AI's decision. Brighter
                  areas indicate higher attention, typically corresponding to lesions like microaneurysms, hemorrhages, or
                  exudates.
                </p>
              </div>
            </TabsContent>

            <TabsContent value="confidence" className="space-y-4">
              <img src={visualizations.confidence_chart} alt="Confidence Distribution" className="w-full rounded-lg" />
              {prediction.class_probabilities && (
                <div className="grid grid-cols-2 md:grid-cols-5 gap-2">
                  {Object.entries(prediction.class_probabilities).map(([cls, prob]) => (
                    <div key={cls} className="text-center">
                      <div className="text-xs text-gray-500 mb-1">
                        {['No DR', 'Mild', 'Moderate', 'Severe', 'PDR'][parseInt(cls.split('_')[1])]
                          || cls}
                      </div>
                      <div className="text-lg font-bold">{((prob as number) * 100).toFixed(1)}%</div>
                    </div>
                  ))}
                </div>
              )}
            </TabsContent>

            <TabsContent value="lesions" className="space-y-4">
              <div className="space-y-3">
                {visualizations.detected_lesions.slice(0, 8).map((lesion, idx) => (
                  <div
                    key={idx}
                    className="flex items-center justify-between p-3 bg-gray-50 rounded-lg hover:bg-gray-100 transition"
                  >
                    <div className="flex items-center space-x-3">
                      <Badge className={getLesionTypeColor(lesion.lesion_type)}>{idx + 1}</Badge>
                      <div>
                        <p className="font-medium">{formatLesionType(lesion.lesion_type)}</p>
                        <p className="text-sm text-gray-500">
                          Position: ({lesion.bbox.x}, {lesion.bbox.y}) • Size: {lesion.area}px²
                        </p>
                      </div>
                    </div>
                    <div className="text-right">
                      <p className="text-sm font-semibold">{(lesion.confidence * 100).toFixed(0)}%</p>
                      <p className="text-xs text-gray-500">confidence</p>
                    </div>
                  </div>
                ))}
              </div>

              {visualizations.lesion_count > 8 && (
                <p className="text-sm text-center text-gray-500">
                  Showing top 8 of {visualizations.lesion_count} detected regions
                </p>
              )}
            </TabsContent>
          </Tabs>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Clinical Insights</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="space-y-2">
              <h4 className="font-semibold">Key Findings:</h4>
              <ul className="list-disc list-inside space-y-1 text-sm text-gray-700">
                <li>{visualizations.lesion_count} potentially pathological regions detected</li>
                <li>
                  Primary lesions:{' '}
                  {Array.from(new Set(visualizations.detected_lesions.map((l) => formatLesionType(l.lesion_type)))).join(', ')}
                </li>
                <li>Confidence level: {((prediction.confidence || 0) * 100).toFixed(1)}%</li>
              </ul>
            </div>
            <div className="space-y-2">
              <h4 className="font-semibold">AI Methodology:</h4>
              <ul className="list-disc list-inside space-y-1 text-sm text-gray-700">
                <li>GradCAM explainability technique</li>
                <li>CNN-based feature detection</li>
                <li>Transfer learning backbone</li>
              </ul>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default AIVisualization;


