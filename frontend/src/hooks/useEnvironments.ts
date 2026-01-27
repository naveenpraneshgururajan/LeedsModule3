/**
 * Custom Hook for Environments API
 * Using standard React hooks (useState, useEffect)
 */

import { useState, useEffect, useCallback } from 'react';
import { apiService } from '../services/api';
import type { APIResponse, Environment } from '../types';

interface UseQueryResult<T> {
  data: T | undefined;
  isLoading: boolean;
  error: Error | null;
  refetch: () => Promise<void>;
}

export const useEnvironments = (): UseQueryResult<APIResponse<Environment[]>> => {
  const [data, setData] = useState<APIResponse<Environment[]>>();
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  const fetchData = useCallback(async () => {
    try {
      setIsLoading(true);
      setError(null);
      const result = await apiService.getAllEnvironments();
      setData(result);
    } catch (err) {
      setError(err as Error);
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchData();
    // Refetch every minute
    const interval = setInterval(fetchData, 60000);
    return () => clearInterval(interval);
  }, [fetchData]);

  return { data, isLoading, error, refetch: fetchData };
};

export const useEnvironment = (envName: string): UseQueryResult<APIResponse<Environment>> => {
  const [data, setData] = useState<APIResponse<Environment>>();
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  const fetchData = useCallback(async () => {
    if (!envName) return;

    try {
      setIsLoading(true);
      setError(null);
      const result = await apiService.getEnvironment(envName);
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

export const useEnvironmentKeys = (envName: string) => {
  const [data, setData] = useState<APIResponse<{ environment: string; keys: string[]; count: number }>>();
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  const fetchData = useCallback(async () => {
    if (!envName) return;

    try {
      setIsLoading(true);
      setError(null);
      const result = await apiService.getEnvironmentKeys(envName);
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

export const useCompareEnvironments = (source: string, target: string) => {
  const [data, setData] = useState<APIResponse<any>>();
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  const fetchData = useCallback(async () => {
    if (!source || !target) return;

    try {
      setIsLoading(true);
      setError(null);
      const result = await apiService.compareEnvironments(source, target);
      setData(result);
    } catch (err) {
      setError(err as Error);
    } finally {
      setIsLoading(false);
    }
  }, [source, target]);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  return { data, isLoading, error, refetch: fetchData };
};

export const useEnvironmentTypesSummary = () => {
  const [data, setData] = useState<APIResponse<any[]>>();
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  const fetchData = useCallback(async () => {
    try {
      setIsLoading(true);
      setError(null);
      const result = await apiService.getEnvironmentTypesSummary();
      setData(result);
    } catch (err) {
      setError(err as Error);
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  return { data, isLoading, error, refetch: fetchData };
};
