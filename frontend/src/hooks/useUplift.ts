/**
 * Custom Hook for Uplift API
 */

import { useMutation, useQuery } from '@tanstack/react-query';
import { apiService } from '../services/api';

export const useAnalyzeUplift = () => {
  return useMutation({
    mutationFn: ({ source, target, sinceDate }: { source: string; target: string; sinceDate?: string }) =>
      apiService.analyzeUplift(source, target, sinceDate),
  });
};

export const useGenerateChecklist = () => {
  return useMutation({
    mutationFn: ({
      source,
      target,
      format,
      sinceDate,
    }: {
      source: string;
      target: string;
      format?: 'markdown' | 'text' | 'html';
      sinceDate?: string;
    }) => apiService.generateChecklist(source, target, format, sinceDate),
  });
};

export const useUpliftSuggestions = (envName: string) => {
  return useQuery({
    queryKey: ['uplift-suggestions', envName],
    queryFn: () => apiService.getUpliftSuggestions(envName),
    enabled: !!envName,
    staleTime: 300000, // 5 minutes
  });
};

export const useValidateUplift = () => {
  return useMutation({
    mutationFn: ({ source, target }: { source: string; target: string }) =>
      apiService.validateUplift(source, target),
  });
};
