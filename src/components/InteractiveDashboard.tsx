import React, { useEffect, useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { ResponsiveContainer, BarChart, Bar, CartesianGrid, XAxis, YAxis, Tooltip, LineChart, Line } from 'recharts';
import { config } from '@/lib/config';

interface DashboardMetrics {
  total_screenings: number;
  dr_detected: number;
  avg_confidence: number;
  severity_distribution: { [key: string]: number };
  temporal_data: Array<{ date: string; count: number }>;
}

export const InteractiveDashboard: React.FC = () => {
  const [metrics, setMetrics] = useState<DashboardMetrics | null>(null);

  useEffect(() => {
    fetch(`${config.api.baseUrl}/analytics/dashboard`)
      .then((res) => res.json())
      .then((data) => setMetrics(data))
      .catch(() => setMetrics(null));
  }, []);

  if (!metrics) return <div>Loading dashboard...</div>;

  const severityData = Object.entries(metrics.severity_distribution).map(([key, value]) => ({
    name: ['No DR', 'Mild', 'Moderate', 'Severe', 'PDR'][parseInt(key)] || key,
    count: value,
  }));

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card>
          <CardHeader>
            <CardTitle>Total Screenings</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-4xl font-bold">{metrics.total_screenings}</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>DR Detection Rate</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-4xl font-bold">
              {metrics.total_screenings > 0
                ? ((metrics.dr_detected / metrics.total_screenings) * 100).toFixed(1)
                : '0.0'}
              %
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Avg Confidence</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-4xl font-bold">{(metrics.avg_confidence * 100).toFixed(1)}%</p>
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Severity Distribution</CardTitle>
        </CardHeader>
        <CardContent>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={severityData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="name" />
              <YAxis />
              <Tooltip />
              <Bar dataKey="count" fill="#3b82f6" />
            </BarChart>
          </ResponsiveContainer>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Screening Trends</CardTitle>
        </CardHeader>
        <CardContent>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={metrics.temporal_data}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="date" />
              <YAxis />
              <Tooltip />
              <Line type="monotone" dataKey="count" stroke="#10b981" strokeWidth={2} />
            </LineChart>
          </ResponsiveContainer>
        </CardContent>
      </Card>
    </div>
  );
};

export default InteractiveDashboard;


