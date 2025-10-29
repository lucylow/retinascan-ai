import React from 'react';
import { AgentStatus } from '../../services/aiAgentService';

interface AgentCardProps {
  agent: AgentStatus;
}

export const AgentCard: React.FC<AgentCardProps> = ({ agent }) => {
  const getAgentIcon = (role: string) => {
    const icons: { [key: string]: string } = {
      'data_processor': '📊',
      'model_specialist': '🤖',
      'diagnosis_analyst': '🔍',
      'quality_controller': '✅',
      'report_generator': '📄'
    };
    return icons[role] || '⚙️';
  };

  const getRoleName = (role: string) => {
    const names: { [key: string]: string } = {
      'data_processor': 'Data Processor',
      'model_specialist': 'AI Specialist',
      'diagnosis_analyst': 'Diagnosis Analyst',
      'quality_controller': 'Quality Control',
      'report_generator': 'Report Generator'
    };
    return names[role] || role.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
  };

  return (
    <div className={`agent-card ${agent.status}`}>
      <div className="agent-header">
        <span className="agent-icon">{getAgentIcon(agent.role)}</span>
        <div className="agent-info">
          <h3>{getRoleName(agent.role)}</h3>
          <span className="agent-id">{agent.agentId}</span>
        </div>
        <div className={`status-badge ${agent.status}`}>
          {agent.status === 'processing' ? '🔄' : agent.status === 'online' ? '🟢' : '🔴'}
        </div>
      </div>

      <div className="agent-metrics">
        <div className="metric">
          <span className="metric-label">Tasks</span>
          <span className="metric-value">{agent.performance.tasksProcessed}</span>
        </div>
        <div className="metric">
          <span className="metric-label">Success</span>
          <span className="metric-value">{(agent.performance.successRate * 100).toFixed(1)}%</span>
        </div>
        <div className="metric">
          <span className="metric-label">Avg Time</span>
          <span className="metric-value">{agent.performance.avgProcessingTime.toFixed(2)}s</span>
        </div>
      </div>

      {agent.currentTask && (
        <div className="current-task">
          <span className="task-label">Current Task:</span>
          <span className="task-name">{agent.currentTask}</span>
        </div>
      )}
    </div>
  );
};

