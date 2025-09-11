import { create } from 'zustand';
import { devtools } from 'zustand/middleware';

interface ApiState {
  // Loading states
  isLoading: boolean;
  loadingOperations: Set<string>;
  
  // Error states
  globalError: string | null;
  errors: Record<string, string>;
  
  // Connection states
  apiConnected: boolean;
  aiApiConnected: boolean;
  lastHealthCheck: Date | null;
}

interface ApiActions {
  // Loading management
  setLoading: (operation: string, loading: boolean) => void;
  setGlobalLoading: (loading: boolean) => void;
  
  // Error management
  setError: (key: string, error: string | null) => void;
  setGlobalError: (error: string | null) => void;
  clearErrors: () => void;
  clearError: (key: string) => void;
  
  // Connection management
  setApiConnection: (connected: boolean) => void;
  setAiApiConnection: (connected: boolean) => void;
  updateHealthCheck: () => void;
}

const initialState: ApiState = {
  isLoading: false,
  loadingOperations: new Set(),
  globalError: null,
  errors: {},
  apiConnected: false,
  aiApiConnected: false,
  lastHealthCheck: null,
};

export const useApiStore = create<ApiState & ApiActions>()(
  devtools(
    (set, get) => ({
      ...initialState,
      
      setLoading: (operation: string, loading: boolean) => {
        set((state) => {
          const newOperations = new Set(state.loadingOperations);
          if (loading) {
            newOperations.add(operation);
          } else {
            newOperations.delete(operation);
          }
          
          return {
            loadingOperations: newOperations,
            isLoading: newOperations.size > 0,
          };
        });
      },
      
      setGlobalLoading: (loading: boolean) => {
        set({ isLoading: loading });
      },
      
      setError: (key: string, error: string | null) => {
        set((state) => ({
          errors: error ? { ...state.errors, [key]: error } : (() => {
            const newErrors = { ...state.errors };
            delete newErrors[key];
            return newErrors;
          })(),
        }));
      },
      
      setGlobalError: (error: string | null) => {
        set({ globalError: error });
      },
      
      clearErrors: () => {
        set({ globalError: null, errors: {} });
      },
      
      clearError: (key: string) => {
        set((state) => {
          const newErrors = { ...state.errors };
          delete newErrors[key];
          return { errors: newErrors };
        });
      },
      
      setApiConnection: (connected: boolean) => {
        set({ apiConnected: connected });
      },
      
      setAiApiConnection: (connected: boolean) => {
        set({ aiApiConnected: connected });
      },
      
      updateHealthCheck: () => {
        set({ lastHealthCheck: new Date() });
      },
    }),
    {
      name: 'api-store',
    }
  )
);

// Selectors for computed values
export const useApiSelectors = () => {
  const state = useApiStore();
  
  return {
    hasErrors: Object.keys(state.errors).length > 0 || !!state.globalError,
    isFullyConnected: state.apiConnected && state.aiApiConnected,
    errorCount: Object.keys(state.errors).length + (state.globalError ? 1 : 0),
  };
};