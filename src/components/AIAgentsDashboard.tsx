import React, { useState, useEffect, useCallback } from 'react';
import { AgentCard } from './AgentCard';
import { ImageUploadArea } from './ImageUploadArea';
import { WorkflowList } from './WorkflowList';
import { WorkflowResults } from './WorkflowResults';
import { SystemMetrics } from './SystemMetrics';
import '../styles/AIAgentsDashboard.css';

type AgentStatus = {
  role: string;
  agentId: string;
  performance: {
    tasksProcessed: number;
    successRate: number;
    avgProcessingTime: number;
  };
  status: 'online' | 'offline' | 'processing';
  currentTask?: string;
};

type WorkflowStatus = {
  id: string;
  status: 'running' | 'completed' | 'failed' | 'queued';
  progress: number;
  currentStep: string;
  startTime: Date;
  endTime?: Date;
  result?: any;
  error?: string;
};

export const AIAgentsDashboard: React.FC = () => {
  const [agents, setAgents] = useState<AgentStatus[]>([]);
  const [workflows, setWorkflows] = useState<WorkflowStatus[]>([]);
  const [selectedWorkflow, setSelectedWorkflow] = useState<string | null>(null);
  const [systemMetrics, setSystemMetrics] = useState<any>({});
  const [isProcessing, setIsProcessing] = useState(false);

  useEffect(() => {
    const stop = startMetricsPolling();
    return stop;
  }, []);

  const mapAgents = useCallback((agentPerf: any): AgentStatus[] => {
    if (!agentPerf) return [];
    return Object.entries(agentPerf).map(([role, perf]: [string, any]) => ({
      role,
      agentId: `${role}-${Math.random().toString(36).slice(2, 6)}`,
      performance: {
        tasksProcessed: perf.tasks_processed || 0,
        successRate: perf.success_rate || 0,
        avgProcessingTime: perf.average_processing_time || 0,
      },
      status: 'online',
    }));
  }, []);

  const startMetricsPolling = useCallback(() => {
    const interval = setInterval(async () => {
      try {
        const res = await fetch('/api/metrics');
        const data = await res.json();
        setSystemMetrics(data.system_metrics || {});

        const agentsMapped = mapAgents(data.system_metrics?.agent_performance);
        setAgents(agentsMapped);

        const wfRes = await fetch('/api/workflows');
        const wfData = await wfRes.json();
        const wfStatuses: WorkflowStatus[] = (wfData.workflows || []).slice(-10).map((wf: any) => ({
          id: wf.workflow_id || 'unknown',
          status: (wf.status || 'running') as WorkflowStatus['status'],
          progress: calculateProgress(wf),
          currentStep: getCurrentStep(wf),
          startTime: wf.start_time ? new Date(wf.start_time) : new Date(),
          endTime: wf.end_time ? new Date(wf.end_time) : undefined,
          result: wf.result,
          error: wf.error,
        }));
        setWorkflows(wfStatuses);
      } catch (e) {
        // eslint-disable-next-line no-console
        console.error('Polling failed', e);
      }
    }, 2000);
    return () => clearInterval(interval);
  }, [mapAgents]);

  const calculateProgress = (workflow: any): number => {
    const steps = ['data_processing', 'model_prediction', 'diagnosis_analysis', 'quality_control', 'report_generation'];
    const currentStep = workflow.current_step || 'data_processing';
    const stepIndex = Math.max(steps.indexOf(currentStep), 0);
    return Math.round(((stepIndex + 1) / steps.length) * 100);
  };

  const getCurrentStep = (workflow: any): string => {
    const stepMap: { [key: string]: string } = {
      data_processing: 'Data Processing',
      model_prediction: 'AI Analysis',
      diagnosis_analysis: 'Clinical Review',
      quality_control: 'Quality Control',
      report_generation: 'Report Generation',
    };
    return stepMap[workflow.current_step] || 'Starting...';
  };

  const handleImageUpload = async (files: FileList) => {
    if (isProcessing) return;
    setIsProcessing(true);
    const file = files[0];
    const workflowId = `web_${Date.now()}`;

    setWorkflows((prev) => [
      ...prev,
      {
        id: workflowId,
        status: 'queued',
        progress: 0,
        currentStep: 'Waiting in queue',
        startTime: new Date(),
      },
    ]);

    try {
      const fd = new FormData();
      fd.append('image', file);
      const res = await fetch('/api/process', { method: 'POST', body: fd });
      const data = await res.json();
      if (!data.success) throw new Error(data.error || 'Processing failed');

      setWorkflows((prev) =>
        prev.map((wf) =>
          wf.id === workflowId
            ? { ...wf, status: 'completed', progress: 100, result: data.result }
            : wf
        )
      );
    } catch (error: any) {
      setWorkflows((prev) =>
        prev.map((wf) =>
          wf.id === workflowId
            ? { ...wf, status: 'failed', error: error?.message || 'Unknown error' }
            : wf
        )
      );
    } finally {
      setIsProcessing(false);
    }
  };

  return (
    <div className="ai-agents-dashboard">
      <div className="dashboard-header">
        <h1>🩺 RetinaScan AI - Multi-Agent System</h1>
        <div className="system-status">
          <span className={`status-indicator ${'online'}`}>
            System Online
          </span>
        </div>
      </div>

      <div className="dashboard-grid">
        <div className="agents-panel">
          <h2>AI Agents Status</h2>
          <div className="agents-grid">
            {agents.map((agent) => (
              <AgentCard key={agent.agentId} agent={agent} />
            ))}
          </div>
        </div>

        <div className="workflow-panel">
          <h2>Image Processing</h2>
          <ImageUploadArea onUpload={handleImageUpload} isProcessing={isProcessing} />
          <WorkflowList
            workflows={workflows}
            selectedWorkflow={selectedWorkflow}
            onSelectWorkflow={setSelectedWorkflow}
          />
        </div>

        <div className="results-panel">
          <h2>Results & Analytics</h2>
          {selectedWorkflow ? (
            <WorkflowResults workflow={workflows.find((w) => w.id === selectedWorkflow)} />
          ) : (
            <SystemMetrics metrics={systemMetrics} />
          )}
        </div>
      </div>
    </div>
  );
};

export default AIAgentsDashboard;


