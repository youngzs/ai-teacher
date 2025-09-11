import { useState, useCallback, useEffect } from 'react';
import type { ApiResponse } from '../types';
import { useApiStore } from '../store/apiStore';

interface UseApiWithStoreOptions {
  key?: string; // Unique key for this operation
  showGlobalLoading?: boolean; // Show in global loading state
  showGlobalError?: boolean; // Show errors globally
  autoExecute?: boolean; // Execute immediately on mount
}

interface UseApiWithStoreReturn<T> {
  data: T | null;
  loading: boolean;
  error: string | null;
  execute: (...args: any[]) => Promise<T | null>;
  reset: () => void;
  retry: () => void;
}

export function useApiWithStore<T>(
  apiFunction: (...args: any[]) => Promise<ApiResponse<T>>,
  options: UseApiWithStoreOptions = {}
): UseApiWithStoreReturn<T> {
  const {
    key = Math.random().toString(36).substr(2, 9), // Generate random key if not provided
    showGlobalLoading = false,
    showGlobalError = false,
  } = options;

  const [data, setData] = useState<T | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [lastArgs, setLastArgs] = useState<any[]>([]);

  const {
    setLoading: setGlobalLoadingState,
    setError: setGlobalErrorState,
    clearError: clearGlobalError,
  } = useApiStore();

  const execute = useCallback(async (...args: any[]): Promise<T | null> => {
    setLastArgs(args);
    setLoading(true);
    setError(null);

    if (showGlobalLoading) {
      setGlobalLoadingState(key, true);
    }
    if (showGlobalError) {
      clearGlobalError(key);
    }

    try {
      const response = await apiFunction(...args);
      
      if (response.success && response.data !== undefined) {
        setData(response.data);
        setLoading(false);
        
        if (showGlobalLoading) {
          setGlobalLoadingState(key, false);
        }
        
        return response.data;
      } else {
        const errorMessage = response.message || 'An error occurred';
        setError(errorMessage);
        setLoading(false);
        
        if (showGlobalLoading) {
          setGlobalLoadingState(key, false);
        }
        if (showGlobalError) {
          setGlobalErrorState(key, errorMessage);
        }
        
        return null;
      }
    } catch (error: any) {
      const errorMessage = error.message || 'An unexpected error occurred';
      setError(errorMessage);
      setLoading(false);
      
      if (showGlobalLoading) {
        setGlobalLoadingState(key, false);
      }
      if (showGlobalError) {
        setGlobalErrorState(key, errorMessage);
      }
      
      return null;
    }
  }, [apiFunction, key, showGlobalLoading, showGlobalError, setGlobalLoadingState, setGlobalErrorState, clearGlobalError]);

  const reset = useCallback(() => {
    setData(null);
    setLoading(false);
    setError(null);
    setLastArgs([]);
    
    if (showGlobalLoading) {
      setGlobalLoadingState(key, false);
    }
    if (showGlobalError) {
      clearGlobalError(key);
    }
  }, [key, showGlobalLoading, showGlobalError, setGlobalLoadingState, clearGlobalError]);

  const retry = useCallback(() => {
    if (lastArgs.length > 0) {
      execute(...lastArgs);
    }
  }, [execute, lastArgs]);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (showGlobalLoading) {
        setGlobalLoadingState(key, false);
      }
      if (showGlobalError) {
        clearGlobalError(key);
      }
    };
  }, [key, showGlobalLoading, showGlobalError, setGlobalLoadingState, clearGlobalError]);

  return {
    data,
    loading,
    error,
    execute,
    reset,
    retry,
  };
}

// Hook for immediate execution (queries)
export function useApiQuery<T>(
  apiFunction: (...args: any[]) => Promise<ApiResponse<T>>,
  args: any[] = [],
  dependencies: any[] = [],
  options: UseApiWithStoreOptions = {}
): UseApiWithStoreReturn<T> {
  const api = useApiWithStore(apiFunction, options);

  useEffect(() => {
    api.execute(...args);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, dependencies);

  return api;
}

// Hook for mutations with success/error callbacks
export function useApiMutationWithStore<T, P = any>(
  apiFunction: (params: P) => Promise<ApiResponse<T>>,
  options?: UseApiWithStoreOptions & {
    onSuccess?: (data: T) => void;
    onError?: (error: string) => void;
  }
): {
  mutate: (params: P) => Promise<T | null>;
  loading: boolean;
  error: string | null;
  reset: () => void;
  retry: () => void;
} {
  const { onSuccess, onError, ...apiOptions } = options || {};
  
  const api = useApiWithStore<T>(
    apiFunction as (...args: any[]) => Promise<ApiResponse<T>>,
    apiOptions
  );

  const mutate = useCallback(async (params: P): Promise<T | null> => {
    const result = await api.execute(params);
    if (result) {
      onSuccess?.(result);
    } else if (api.error) {
      onError?.(api.error);
    }
    return result;
  }, [api, onSuccess, onError]);

  return {
    mutate,
    loading: api.loading,
    error: api.error,
    reset: api.reset,
    retry: api.retry,
  };
}