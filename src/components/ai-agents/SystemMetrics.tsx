import React from 'react';
import { SystemMetrics as SystemMetricsType } from '../../services/aiAgentService';

interface SystemMetricsProps {
  metrics: SystemMetricsType | null;
}

export const SystemMetricsDisplay: React.FC<SystemMetricsProps> = ({ metrics }) => {
  const defaultMetrics = {
    total_workflows: 0,
    successful_workflows: 0,
    failed_workflows: 0,
    agent_performance: {}
  };

  const data = metrics || defaultMetrics;
  const successRate = data.total_workflows > 0
    ? (data.successful_workflows / data.total_workflows) * 100
    : 0;

  return (
    <div className="system-metrics">
      <h3>System Performance</h3>

      <div className="metrics-grid">
        <div className="metric-card primary">
          <div className="metric-icon">📈</div>
          <div className="metric-info">
            <span className="metric-value">{data.total_workflows}</span>
            <span className="metric-label">Total Workflows</span>
          </div>
        </div>

        <div className="metric-card success">
          <div className="metric-icon">✅</div>
          <div className="metric-info">
            <span className="metric-value">{successRate.toFixed(1)}%</span>
            <span className="metric-label">Success Rate</span>
          </div>
        </div>

        <div className="metric-card warning">
          <div className="metric-icon">⏱️</div>
          <div className="metric-info">
            <span className="metric-value">{data.failed_workflows}</span>
            <span className="metric-label">Failed</span>
          </div>
        </div>

        <div className="metric-card info">
          <div className="metric-icon">🤖</div>
          <div className="metric-info">
            <span className="metric-value">{Object.keys(data.agent_performance || {}).length}</span>
            <span className="metric-label">Active Agents</span>
          </div>
        </div>
      </div>

      <div className="agent-performance">
        <h4>Agent Performance</h4>
        {Object.keys(data.agent_performance || {}).length > 0 ? (
          Object.entries(data.agent_performance).map(([agent, perf]: [string, any]) => (
            <div key={agent} className="agent-performance-item">
              <div className="agent-name">
                <span className="agent-emoji">
                  {agent === 'data_processor' ? '📊' :
                    agent === 'model_specialist' ? '🤖' :
                      agent === 'diagnosis_analyst' ? '🔍' :
                        agent === 'quality_controller' ? '✅' : '📄'}
                </span>
                {agent.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
              </div>
              <div className="performance-stats">
                <span className="stat">{perf.tasks_processed || 0} tasks</span>
                <span className="stat">{((perf.success_rate || 0) * 100).toFixed(1)}% success</span>
                <span className="stat">{(perf.average_processing_time || 0).toFixed(2)}s avg</span>
              </div>
            </div>
          ))
        ) : (
          <div className="empty-state">
            <p>No agent performance data available</p>
          </div>
        )}
      </div>
    </div>
  );
};

