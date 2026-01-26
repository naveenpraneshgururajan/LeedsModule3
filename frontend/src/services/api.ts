/**
 * API Service - Axios-based API client for backend communication
 */

import axios, { AxiosInstance, AxiosResponse } from 'axios';
import type {
  APIResponse,
  Environment,
  UpliftAnalysis,
  ComparisonResult,
  Change,
  CoverageReport,
  Summary,
} from '../types';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

class APIService {
  private client: AxiosInstance;

  constructor() {
    this.client = axios.create({
      baseURL: API_BASE_URL,
      timeout: 30000,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Response interceptor for error handling
    this.client.interceptors.response.use(
      (response) => response,
      (error) => {
        console.error('API Error:', error);
        return Promise.reject(error);
      }
    );
  }

  // Health check
  async healthCheck() {
    const response = await this.client.get('/health');
    return response.data;
  }

  // ==================== ENVIRONMENTS ====================

  async getAllEnvironments(): Promise<APIResponse<Environment[]>> {
    const response = await this.client.get('/api/environments');
    return response.data;
  }

  async getEnvironment(envName: string): Promise<APIResponse<Environment>> {
    const response = await this.client.get(`/api/environments/${envName}`);
    return response.data;
  }

  async getEnvironmentKeys(envName: string): Promise<APIResponse<{ environment: string; keys: string[]; count: number }>> {
    const response = await this.client.get(`/api/environments/${envName}/keys`);
    return response.data;
  }

  async compareEnvironments(source: string, target: string): Promise<APIResponse<ComparisonResult>> {
    const response = await this.client.get(`/api/environments/${source}/compare/${target}`);
    return response.data;
  }

  async getEnvironmentTypesSummary(): Promise<APIResponse<any[]>> {
    const response = await this.client.get('/api/environments/types/summary');
    return response.data;
  }

  // ==================== UPLIFT ====================

  async analyzeUplift(source: string, target: string, sinceDate?: string): Promise<APIResponse<UpliftAnalysis>> {
    const response = await this.client.post('/api/uplift/analyze', {
      source,
      target,
      since_date: sinceDate,
    });
    return response.data;
  }

  async generateChecklist(
    source: string,
    target: string,
    format: 'markdown' | 'text' | 'html' = 'markdown',
    sinceDate?: string
  ): Promise<APIResponse<{ checklist: string; format: string; analysis: UpliftAnalysis }>> {
    const response = await this.client.post('/api/uplift/checklist', {
      source,
      target,
      format,
      since_date: sinceDate,
    });
    return response.data;
  }

  async getUpliftSuggestions(envName: string): Promise<APIResponse<any>> {
    const response = await this.client.get(`/api/uplift/suggestions/${envName}`);
    return response.data;
  }

  async validateUplift(source: string, target: string): Promise<APIResponse<any>> {
    const response = await this.client.post('/api/uplift/validate', {
      source,
      target,
    });
    return response.data;
  }

  // ==================== CHANGES ====================

  async getChanges(env?: string, since?: string, limit?: number): Promise<APIResponse<Change[]>> {
    const params = new URLSearchParams();
    if (env) params.append('env', env);
    if (since) params.append('since', since);
    if (limit) params.append('limit', limit.toString());

    const response = await this.client.get(`/api/changes?${params.toString()}`);
    return response.data;
  }

  async getRecentChanges(days: number = 7): Promise<APIResponse<Change[]>> {
    const response = await this.client.get(`/api/changes/recent?days=${days}`);
    return response.data;
  }

  async getEnvironmentHistory(envName: string, limit: number = 10): Promise<APIResponse<any>> {
    const response = await this.client.get(`/api/changes/history/${envName}?limit=${limit}`);
    return response.data;
  }

  async getEnvironmentDiff(envName: string, commit: string = 'HEAD'): Promise<APIResponse<any>> {
    const response = await this.client.get(`/api/changes/diff/${envName}?commit=${commit}`);
    return response.data;
  }

  async compareHistory(env1: string, env2: string): Promise<APIResponse<any>> {
    const response = await this.client.get(`/api/changes/compare-history?env1=${env1}&env2=${env2}`);
    return response.data;
  }

  async getGitStatus(): Promise<APIResponse<any>> {
    const response = await this.client.get('/api/changes/status');
    return response.data;
  }

  // ==================== REPORTS ====================

  async getCoverageReport(): Promise<APIResponse<CoverageReport>> {
    const response = await this.client.get('/api/reports/coverage');
    return response.data;
  }

  async getAnomaliesReport(): Promise<APIResponse<any>> {
    const response = await this.client.get('/api/reports/anomalies');
    return response.data;
  }

  async getMLStatus(): Promise<APIResponse<any>> {
    const response = await this.client.get('/api/reports/ml-status');
    return response.data;
  }

  async generateReport(
    type: 'coverage' | 'anomalies' | 'full',
    format: 'json' | 'html',
    environments?: string[]
  ): Promise<APIResponse<any>> {
    const response = await this.client.post('/api/reports/generate', {
      type,
      format,
      environments,
    });
    return response.data;
  }

  async getSummary(): Promise<APIResponse<Summary>> {
    const response = await this.client.get('/api/reports/summary');
    return response.data;
  }
}

// Export singleton instance
export const apiService = new APIService();
export default apiService;
