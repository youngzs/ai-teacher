import { useState, useCallback } from 'react';
import type { ApiResponse } from '../types';

interface UseApiState<T> {
  data: T | null;
  loading: boolean;
  error: string | null;
}

interface UseApiReturn<T> {
  data: T | null;
  loading: boolean;
  error: string | null;
  execute: (...args: any[]) => Promise<T | null>;
  reset: () => void;
}

export function useApi<T>(
  apiFunction: (...args: any[]) => Promise<ApiResponse<T>>
): UseApiReturn<T> {
  const [state, setState] = useState<UseApiState<T>>({
    data: null,
    loading: false,
    error: null,
  });

  const execute = useCallback(async (...args: any[]): Promise<T | null> => {
    setState(prev => ({ ...prev, loading: true, error: null }));

    try {
      const response = await apiFunction(...args);
      
      if (response.success && response.data) {
        setState({
          data: response.data,
          loading: false,
          error: null,
        });
        return response.data;
      } else {
        setState({
          data: null,
          loading: false,
          error: response.message || 'An error occurred',
        });
        return null;
      }
    } catch (error: any) {
      setState({
        data: null,
        loading: false,
        error: error.message || 'An unexpected error occurred',
      });
      return null;
    }
  }, [apiFunction]);

  const reset = useCallback(() => {
    setState({
      data: null,
      loading: false,
      error: null,
    });
  }, []);

  return {
    ...state,
    execute,
    reset,
  };
}

// Hook for API calls that should execute immediately
export function useApiQuery<T>(
  apiFunction: (...args: any[]) => Promise<ApiResponse<T>>,
  args: any[] = [],
  dependencies: any[] = []
): UseApiReturn<T> {
  const api = useApi(apiFunction);

  React.useEffect(() => {
    api.execute(...args);
  }, dependencies);

  return api;
}

// Hook for mutations (create, update, delete operations)
export function useApiMutation<T, P = any>(
  apiFunction: (params: P) => Promise<ApiResponse<T>>,
  options?: {
    onSuccess?: (data: T) => void;
    onError?: (error: string) => void;
  }
): {
  mutate: (params: P) => Promise<T | null>;
  loading: boolean;
  error: string | null;
  reset: () => void;
} {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const mutate = useCallback(async (params: P): Promise<T | null> => {
    setLoading(true);
    setError(null);

    try {
      const response = await apiFunction(params);
      
      if (response.success && response.data) {
        setLoading(false);
        options?.onSuccess?.(response.data);
        return response.data;
      } else {
        const errorMessage = response.message || 'An error occurred';
        setError(errorMessage);
        setLoading(false);
        options?.onError?.(errorMessage);
        return null;
      }
    } catch (error: any) {
      const errorMessage = error.message || 'An unexpected error occurred';
      setError(errorMessage);
      setLoading(false);
      options?.onError?.(errorMessage);
      return null;
    }
  }, [apiFunction, options]);

  const reset = useCallback(() => {
    setLoading(false);
    setError(null);
  }, []);

  return {
    mutate,
    loading,
    error,
    reset,
  };
}