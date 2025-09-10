import React, { useEffect } from 'react';
import { AppRouter } from './routes';
import { useAppStore } from './store/appStore';
import { ErrorBoundary } from './components/common/ErrorBoundary';

function App() {
  const { theme, setTheme } = useAppStore();

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

  return (
    <ErrorBoundary>
      <div className="min-h-screen bg-gray-50 dark:bg-gray-900 transition-colors">
        <AppRouter />
      </div>
    </ErrorBoundary>
  );
}

export default App;
