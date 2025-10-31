import React from 'react';

interface SystemMetricsProps {
  metrics: any;
}

export const SystemMetrics: React.FC<SystemMetricsProps> = ({ metrics }) => {
  const defaultMetrics = {
    total_workflows: 0,
    successful_workflows: 0,
    failed_workflows: 0,
    agent_performance: {},
  };

  const data = metrics || defaultMetrics;
  const total = data.total_workflows || 0;
  const succ = data.successful_workflows || 0;
  const successRate = total > 0 ? (succ / total) * 100 : 0;

  return (
    <div className="system-metrics">
      <h3>System Performance</h3>

      <div className="metrics-grid">
        <div className="metric-card primary">
          <div className="metric-icon">📈</div>
          <div className="metric-info">
            <span className="metric-value">{total}</span>
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
            <span className="metric-value">{data.failed_workflows || 0}</span>
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
        {Object.entries(data.agent_performance || {}).map(([agent, perf]: [string, any]) => (
          <div key={agent} className="agent-performance-item">
            <div className="agent-name">
              <span className="agent-emoji">
                {agent === 'data_processor' ? '📊' :
                agent === 'model_specialist' ? '🤖' :
                agent === 'diagnosis_analyst' ? '🔍' :
                agent === 'quality_controller' ? '✅' : '📄'}
              </span>
              {agent.replace('_', ' ').toUpperCase()}
            </div>
            <div className="performance-stats">
              <span className="stat">{(perf as any).tasks_processed} tasks</span>
              <span className="stat">{(((perf as any).success_rate || 0) * 100).toFixed(1)}% success</span>
              <span className="stat">{(((perf as any).average_processing_time || 0)).toFixed(2)}s avg</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default SystemMetrics;


