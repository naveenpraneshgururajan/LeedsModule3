/**
 * Custom Hook for Uplift API
 * Using standard React hooks (useState, useCallback)
 */

import { useState, useEffect, useCallback } from 'react';
import { apiService } from '../services/api';

interface UseMutationResult<T> {
  data: T | undefined;
  isPending: boolean;
  error: Error | null;
  mutateAsync: (variables: any) => Promise<T>;
}

export const useAnalyzeUplift = (): UseMutationResult<any> => {
  const [data, setData] = useState<any>();
  const [isPending, setIsPending] = useState(false);
  const [error, setError] = useState<Error | null>(null);

  const mutateAsync = useCallback(
    async ({ source, target, sinceDate }: { source: string; target: string; sinceDate?: string }) => {
      try {
        setIsPending(true);
        setError(null);
        const result = await apiService.analyzeUplift(source, target, sinceDate);
        setData(result);
        return result;
      } catch (err) {
        setError(err as Error);
        throw err;
      } finally {
        setIsPending(false);
      }
    },
    []
  );

  return { data, isPending, error, mutateAsync };
};

export const useGenerateChecklist = (): UseMutationResult<any> => {
  const [data, setData] = useState<any>();
  const [isPending, setIsPending] = useState(false);
  const [error, setError] = useState<Error | null>(null);

  const mutateAsync = useCallback(
    async ({
      source,
      target,
      format,
      sinceDate,
    }: {
      source: string;
      target: string;
      format?: 'markdown' | 'text' | 'html';
      sinceDate?: string;
    }) => {
      try {
        setIsPending(true);
        setError(null);
        const result = await apiService.generateChecklist(source, target, format, sinceDate);
        setData(result);
        return result;
      } catch (err) {
        setError(err as Error);
        throw err;
      } finally {
        setIsPending(false);
      }
    },
    []
  );

  return { data, isPending, error, mutateAsync };
};

export const useUpliftSuggestions = (envName: string) => {
  const [data, setData] = useState<any>();
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  const fetchData = useCallback(async () => {
    if (!envName) return;

    try {
      setIsLoading(true);
      setError(null);
      const result = await apiService.getUpliftSuggestions(envName);
      setData(result);
    } catch (err) {
      setError(err as Error);
    } finally {
      setIsLoading(false);
    }
  }, [envName]);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  return { data, isLoading, error, refetch: fetchData };
};

export const useValidateUplift = (): UseMutationResult<any> => {
  const [data, setData] = useState<any>();
  const [isPending, setIsPending] = useState(false);
  const [error, setError] = useState<Error | null>(null);

  const mutateAsync = useCallback(async ({ source, target }: { source: string; target: string }) => {
    try {
      setIsPending(true);
      setError(null);
      const result = await apiService.validateUplift(source, target);
      setData(result);
      return result;
    } catch (err) {
      setError(err as Error);
      throw err;
    } finally {
      setIsPending(false);
    }
  }, []);

  return { data, isPending, error, mutateAsync };
};
