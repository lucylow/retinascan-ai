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
    // Use metrics endpoint and generate dashboard data
    fetch(`${config.api.baseUrl}/api/metrics`)
      .then((res) => res.json())
      .then((data) => {
        // Transform metrics to dashboard format or use mock data
        // For now, use mock data structure until analytics endpoint is implemented
        if (data.success && data.system_metrics) {
          // Use available metrics endpoint data
          setMetrics({
            total_screenings: 0, // Would need to track this
            dr_detected: 0,
            avg_confidence: 0.85,
            severity_distribution: { '0': 5, '1': 3, '2': 2, '3': 1, '4': 0 },
            temporal_data: [
              { date: '2024-01', count: 10 },
              { date: '2024-02', count: 12 },
              { date: '2024-03', count: 15 },
            ],
          });
        } else {
          setMetrics(null);
        }
      })
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


