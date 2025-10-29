import React from 'react';
import { WorkflowStatus } from '../../services/aiAgentService';

interface WorkflowListProps {
  workflows: WorkflowStatus[];
  selectedWorkflow: string | null;
  onSelectWorkflow: (id: string) => void;
}

export const WorkflowList: React.FC<WorkflowListProps> = ({
  workflows,
  selectedWorkflow,
  onSelectWorkflow
}) => {
  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed': return '✅';
      case 'running': return '🔄';
      case 'failed': return '❌';
      case 'queued': return '⏳';
      default: return '⚙️';
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed': return '#48bb78';
      case 'running': return '#ed8936';
      case 'failed': return '#e53e3e';
      case 'queued': return '#4299e1';
      default: return '#718096';
    }
  };

  const formatTime = (date: Date) => {
    return new Date(date).toLocaleTimeString();
  };

  return (
    <div className="workflow-list">
      <div className="workflow-header">
        <h3>Recent Workflows</h3>
        <span className="workflow-count">{workflows.length} total</span>
      </div>

      <div className="workflow-items">
        {workflows.map(workflow => (
          <div
            key={workflow.id}
            className={`workflow-item ${selectedWorkflow === workflow.id ? 'selected' : ''}`}
            onClick={() => onSelectWorkflow(workflow.id)}
          >
            <div className="workflow-main">
              <div className="workflow-status">
                <span
                  className="status-icon"
                  style={{ color: getStatusColor(workflow.status) }}
                >
                  {getStatusIcon(workflow.status)}
                </span>
                <span className="workflow-id">{workflow.id}</span>
              </div>

              <div className="workflow-time">
                {formatTime(workflow.startTime)}
              </div>
            </div>

            <div className="workflow-progress">
              <div className="progress-bar">
                <div
                  className="progress-fill"
                  style={{ width: `${workflow.progress}%` }}
                ></div>
              </div>
              <span className="progress-text">{workflow.progress}%</span>
            </div>

            <div className="workflow-step">
              {workflow.currentStep}
            </div>

            {workflow.status === 'running' && (
              <div className="workflow-indicator">
                <div className="pulse-animation"></div>
                Live
              </div>
            )}
          </div>
        ))}

        {workflows.length === 0 && (
          <div className="empty-state">
            <div className="empty-icon">📋</div>
            <p>No workflows yet</p>
            <span>Upload an image to start analysis</span>
          </div>
        )}
      </div>
    </div>
  );
};

