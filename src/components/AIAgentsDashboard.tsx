import React, { useState, useEffect } from 'react';
import { aiAgentService, AgentStatus, WorkflowStatus, SystemMetrics } from '../services/aiAgentService';
import { AgentCard } from './ai-agents/AgentCard';
import { ImageUploadArea } from './ai-agents/ImageUploadArea';
import { WorkflowList } from './ai-agents/WorkflowList';
import { WorkflowResults } from './ai-agents/WorkflowResults';
import { SystemMetricsDisplay } from './ai-agents/SystemMetrics';
import './AIAgentsDashboard.css';

export const AIAgentsDashboard: React.FC = () => {
  const [agents, setAgents] = useState<AgentStatus[]>([]);
  const [workflows, setWorkflows] = useState<WorkflowStatus[]>([]);
  const [selectedWorkflow, setSelectedWorkflow] = useState<string | null>(null);
  const [systemMetrics, setSystemMetrics] = useState<SystemMetrics | null>(null);
  const [isProcessing, setIsProcessing] = useState(false);
  const [isOnline, setIsOnline] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    initializeSystem();
    const interval = setInterval(() => {
      updateMetrics();
    }, 2000);
    return () => clearInterval(interval);
  }, []);

  const initializeSystem = async () => {
    try {
      await aiAgentService.healthCheck();
      setIsOnline(true);
      await updateMetrics();
    } catch (error: any) {
      console.error('Failed to initialize AI system:', error);
      setIsOnline(false);
      setError(error.message || 'Failed to connect to AI agent system');
    }
  };

  const updateMetrics = async () => {
    try {
      const [metrics, agentStatuses, recentWorkflows] = await Promise.all([
        aiAgentService.getSystemMetrics(),
        aiAgentService.getAgentStatuses(),
        aiAgentService.getRecentWorkflows(10)
      ]);

      setSystemMetrics(metrics);
      setAgents(agentStatuses);
      setWorkflows(recentWorkflows.map(wf => ({
        ...wf,
        startTime: new Date(wf.startTime),
        endTime: wf.endTime ? new Date(wf.endTime) : undefined,
      })));
      setError(null);
    } catch (error: any) {
      console.error('Failed to update metrics:', error);
      setError(error.message);
    }
  };

  const handleImageUpload = async (files: FileList) => {
    if (isProcessing || files.length === 0) return;

    setIsProcessing(true);
    const file = files[0];
    const workflowId = `web_${Date.now()}`;

    try {
      // Add to workflows queue
      setWorkflows(prev => [...prev, {
        id: workflowId,
        status: 'queued',
        progress: 0,
        currentStep: 'Waiting in queue',
        startTime: new Date()
      }]);

      // Process image
      const result = await aiAgentService.processImage(file, workflowId);

      // Update workflow status
      setWorkflows(prev => prev.map(wf =>
        wf.id === workflowId
          ? {
              ...wf,
              status: 'completed',
              progress: 100,
              result: result,
              endTime: new Date()
            }
          : wf
      ));

      setSelectedWorkflow(workflowId);
    } catch (error: any) {
      console.error('Processing failed:', error);
      setWorkflows(prev => prev.map(wf =>
        wf.id === workflowId
          ? {
              ...wf,
              status: 'failed',
              error: error.message || 'Unknown error occurred',
              endTime: new Date()
            }
          : wf
      ));
    } finally {
      setIsProcessing(false);
      await updateMetrics();
    }
  };

  return (
    <div className="ai-agents-dashboard">
      {/* Header */}
      <div className="dashboard-header">
        <h1>🩺 RetinaScan AI - Multi-Agent System</h1>
        <div className="system-status">
          <span className={`status-indicator ${isOnline ? 'online' : 'offline'}`}>
            {isOnline ? 'System Online' : 'System Offline'}
          </span>
        </div>
      </div>

      {error && (
        <div className="error-banner">
          ⚠️ {error}
        </div>
      )}

      <div className="dashboard-grid">
        {/* Left Column - Agent Status */}
        <div className="agents-panel">
          <h2>AI Agents Status</h2>
          <div className="agents-grid">
            {agents.length > 0 ? (
              agents.map(agent => (
                <AgentCard key={agent.agentId} agent={agent} />
              ))
            ) : (
              <div className="empty-state">
                <div className="empty-icon">🤖</div>
                <p>No agents available</p>
              </div>
            )}
          </div>
        </div>

        {/* Center Column - Workflow & Processing */}
        <div className="workflow-panel">
          <h2>Image Processing</h2>

          {/* Upload Area */}
          <ImageUploadArea
            onUpload={handleImageUpload}
            isProcessing={isProcessing}
          />

          {/* Active Workflows */}
          <WorkflowList
            workflows={workflows}
            selectedWorkflow={selectedWorkflow}
            onSelectWorkflow={setSelectedWorkflow}
          />
        </div>

        {/* Right Column - Results & Metrics */}
        <div className="results-panel">
          <h2>Results & Analytics</h2>

          {selectedWorkflow ? (
            <WorkflowResults
              workflow={workflows.find(w => w.id === selectedWorkflow)}
            />
          ) : (
            <SystemMetricsDisplay metrics={systemMetrics} />
          )}
        </div>
      </div>
    </div>
  );
};

