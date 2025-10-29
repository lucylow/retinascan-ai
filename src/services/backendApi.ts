/**
 * Backend API service for direct communication with RetinaScan AI backend
 */

export interface PredictionResponse {
  success: boolean;
  severity_class: number;
  severity_level: string;
  confidence: number;
  label: string;
  recommendation: string;
  structured_recommendation?: {
    action: string;
    urgency: string;
    follow_up_time: string;
    note: string;
  };
  class_probabilities: Record<string, number>;
  timestamp: string;
  diagnosis?: string;
}

export interface HealthResponse {
  status: string;
  timestamp: string;
  model_loaded: boolean;
  model_info?: {
    num_classes?: number;
    input_shape?: string;
  };
}

const API_BASE_URL = import.meta.env.VITE_BACKEND_API_URL || 'http://localhost:8000';

class BackendApiService {
  private baseUrl: string;

  constructor() {
    this.baseUrl = API_BASE_URL.replace(/\/$/, ''); // Remove trailing slash
  }

  /**
   * Check backend health
   */
  async healthCheck(): Promise<HealthResponse> {
    try {
      const response = await fetch(`${this.baseUrl}/health`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        throw new Error(`Health check failed: ${response.status} ${response.statusText}`);
      }

      return response.json();
    } catch (error) {
      console.error('Health check error:', error);
      throw error;
    }
  }

  /**
   * Predict diabetic retinopathy from image file
   */
  async predictImage(file: File): Promise<PredictionResponse> {
    try {
      const formData = new FormData();
      formData.append('file', file);

      const response = await fetch(`${this.baseUrl}/predict`, {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ 
          detail: `HTTP ${response.status}: ${response.statusText}` 
        }));
        throw new Error(errorData.detail || errorData.error || 'Prediction failed');
      }

      const data: PredictionResponse = await response.json();

      // Validate response structure
      if (!data.success || typeof data.severity_class === 'undefined') {
        throw new Error('Invalid response format from backend');
      }

      return data;
    } catch (error: any) {
      console.error('Prediction error:', error);
      throw error;
    }
  }

  /**
   * Get model information
   */
  async getModelInfo(): Promise<any> {
    try {
      const response = await fetch(`${this.baseUrl}/model/info`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        throw new Error(`Failed to get model info: ${response.status}`);
      }

      return response.json();
    } catch (error) {
      console.error('Model info error:', error);
      throw error;
    }
  }

  /**
   * Check if backend is available
   */
  async isBackendAvailable(): Promise<boolean> {
    try {
      await this.healthCheck();
      return true;
    } catch {
      return false;
    }
  }
}

export const backendApi = new BackendApiService();

