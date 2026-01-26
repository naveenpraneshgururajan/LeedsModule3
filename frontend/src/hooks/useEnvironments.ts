/**
 * Custom Hook for Environments API
 */

import { useQuery, UseQueryResult } from '@tanstack/react-query';
import { apiService } from '../services/api';
import type { APIResponse, Environment } from '../types';

export const useEnvironments = (): UseQueryResult<APIResponse<Environment[]>> => {
  return useQuery({
    queryKey: ['environments'],
    queryFn: () => apiService.getAllEnvironments(),
    staleTime: 30000, // 30 seconds
    refetchInterval: 60000, // Refetch every minute
  });
};

export const useEnvironment = (envName: string): UseQueryResult<APIResponse<Environment>> => {
  return useQuery({
    queryKey: ['environment', envName],
    queryFn: () => apiService.getEnvironment(envName),
    enabled: !!envName,
    staleTime: 30000,
  });
};

export const useEnvironmentKeys = (envName: string) => {
  return useQuery({
    queryKey: ['environment-keys', envName],
    queryFn: () => apiService.getEnvironmentKeys(envName),
    enabled: !!envName,
    staleTime: 60000,
  });
};

export const useCompareEnvironments = (source: string, target: string) => {
  return useQuery({
    queryKey: ['compare', source, target],
    queryFn: () => apiService.compareEnvironments(source, target),
    enabled: !!source && !!target,
    staleTime: 60000,
  });
};

export const useEnvironmentTypesSummary = () => {
  return useQuery({
    queryKey: ['environment-types-summary'],
    queryFn: () => apiService.getEnvironmentTypesSummary(),
    staleTime: 60000,
  });
};
