/**
 * Service for communicating with the multi-agent AI workflow backend
 */

export interface AgentStatus {
  role: string;
  agentId: string;
  performance: {
    tasksProcessed: number;
    successRate: number;
    avgProcessingTime: number;
  };
  status: 'online' | 'offline' | 'processing';
  currentTask?: string;
}

export interface WorkflowStatus {
  id: string;
  status: 'running' | 'completed' | 'failed' | 'queued';
  progress: number;
  currentStep: string;
  startTime: Date;
  endTime?: Date;
  result?: any;
  error?: string;
}

export interface SystemMetrics {
  total_workflows: number;
  successful_workflows: number;
  failed_workflows: number;
  agent_performance: Record<string, {
    tasks_processed: number;
    success_rate: number;
    average_processing_time: number;
  }>;
  timestamp: string;
}

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

class AIAgentService {
  private baseUrl: string;

  constructor() {
    this.baseUrl = API_BASE_URL;
  }

  /**
   * Process an image through the multi-agent workflow
   */
  async processImage(file: File, workflowId?: string): Promise<any> {
    const formData = new FormData();
    formData.append('file', file);
    if (workflowId) {
      formData.append('workflow_id', workflowId);
    }

    const response = await fetch(`${this.baseUrl}/ai-agent/process`, {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Unknown error' }));
      throw new Error(error.detail || `HTTP ${response.status}`);
    }

    return response.json();
  }

  /**
   * Get system metrics
   */
  async getSystemMetrics(): Promise<SystemMetrics> {
    const response = await fetch(`${this.baseUrl}/ai-agent/metrics`);
    
    if (!response.ok) {
      throw new Error('Failed to fetch system metrics');
    }

    return response.json();
  }

  /**
   * Get workflow status
   */
  async getWorkflowStatus(workflowId: string): Promise<WorkflowStatus> {
    const response = await fetch(`${this.baseUrl}/ai-agent/workflow/${workflowId}`);
    
    if (!response.ok) {
      throw new Error('Failed to fetch workflow status');
    }

    return response.json();
  }

  /**
   * Get recent workflows
   */
  async getRecentWorkflows(limit: number = 50): Promise<WorkflowStatus[]> {
    const response = await fetch(`${this.baseUrl}/ai-agent/workflows?limit=${limit}`);
    
    if (!response.ok) {
      throw new Error('Failed to fetch workflows');
    }

    return response.json();
  }

  /**
   * Get agent statuses
   */
  async getAgentStatuses(): Promise<AgentStatus[]> {
    const response = await fetch(`${this.baseUrl}/ai-agent/agents`);
    
    if (!response.ok) {
      throw new Error('Failed to fetch agent statuses');
    }

    return response.json();
  }

  /**
   * Health check for the AI agent system
   */
  async healthCheck(): Promise<{ status: string; timestamp: string }> {
    const response = await fetch(`${this.baseUrl}/ai-agent/health`);
    
    if (!response.ok) {
      throw new Error('Health check failed');
    }

    return response.json();
  }
}

export const aiAgentService = new AIAgentService();

