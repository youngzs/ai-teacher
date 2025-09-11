import React, { useEffect } from 'react';
import { AppRouter } from './routes';
import { useAppStore } from './store/appStore';
import { useApiStore, useApiSelectors } from './store/apiStore';
import { ErrorBoundary } from './components/common/ErrorBoundary';
import { healthService } from './services/healthService';

function App() {
  const { theme, setTheme } = useAppStore();
  const { isFullyConnected } = useApiSelectors();
  const { apiConnected, aiApiConnected } = useApiStore();

  // Apply theme on mount and system preference changes
  useEffect(() => {
    setTheme(theme);
  }, [theme, setTheme]);

  // Initialize theme from system preference if not set
  useEffect(() => {
    if (theme === 'system') {
      const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
      const handleChange = () => setTheme('system');
      mediaQuery.addEventListener('change', handleChange);
      return () => mediaQuery.removeEventListener('change', handleChange);
    }
  }, [theme, setTheme]);

  // Initialize health checks on app startup
  useEffect(() => {
    console.log('🚀 AI Teacher Frontend starting...');
    console.log('Environment:', import.meta.env.MODE);
    console.log('API URLs:', {
      main: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000',
      ai: import.meta.env.VITE_AI_API_BASE_URL || 'http://localhost:8001',
    });

    // Start health checks
    healthService.startHealthChecks();

    // Perform initial connection test
    healthService.testConnection();

    // Cleanup on unmount
    return () => {
      healthService.stopHealthChecks();
    };
  }, []);

  // Log connection status changes
  useEffect(() => {
    if (isFullyConnected) {
      console.log('🟢 All systems connected');
    } else {
      console.log('🟡 Connection status:', { apiConnected, aiApiConnected });
    }
  }, [isFullyConnected, apiConnected, aiApiConnected]);

  return (
    <ErrorBoundary>
      <div className="min-h-screen bg-gray-50 dark:bg-gray-900 transition-colors">
        <AppRouter />
      </div>
    </ErrorBoundary>
  );
}

export default App;
