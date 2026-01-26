/**
 * Custom Hooks for Reports and Changes API
 */

import { useQuery, useMutation } from '@tanstack/react-query';
import { apiService } from '../services/api';

// ==================== CHANGES ====================

export const useChanges = (env?: string, since?: string, limit?: number) => {
  return useQuery({
    queryKey: ['changes', env, since, limit],
    queryFn: () => apiService.getChanges(env, since, limit),
    staleTime: 60000,
  });
};

export const useRecentChanges = (days: number = 7) => {
  return useQuery({
    queryKey: ['recent-changes', days],
    queryFn: () => apiService.getRecentChanges(days),
    staleTime: 60000,
  });
};

export const useEnvironmentHistory = (envName: string, limit: number = 10) => {
  return useQuery({
    queryKey: ['environment-history', envName, limit],
    queryFn: () => apiService.getEnvironmentHistory(envName, limit),
    enabled: !!envName,
    staleTime: 60000,
  });
};

// ==================== REPORTS ====================

export const useCoverageReport = () => {
  return useQuery({
    queryKey: ['coverage-report'],
    queryFn: () => apiService.getCoverageReport(),
    staleTime: 300000, // 5 minutes
  });
};

export const useAnomaliesReport = () => {
  return useQuery({
    queryKey: ['anomalies-report'],
    queryFn: () => apiService.getAnomaliesReport(),
    staleTime: 300000,
  });
};

export const useMLStatus = () => {
  return useQuery({
    queryKey: ['ml-status'],
    queryFn: () => apiService.getMLStatus(),
    staleTime: 60000,
  });
};

export const useSummary = () => {
  return useQuery({
    queryKey: ['summary'],
    queryFn: () => apiService.getSummary(),
    staleTime: 30000,
    refetchInterval: 60000, // Refetch every minute
  });
};

export const useGenerateReport = () => {
  return useMutation({
    mutationFn: ({
      type,
      format,
      environments,
    }: {
      type: 'coverage' | 'anomalies' | 'full';
      format: 'json' | 'html';
      environments?: string[];
    }) => apiService.generateReport(type, format, environments),
  });
};
