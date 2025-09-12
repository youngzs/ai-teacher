import React from 'react';
import { ConnectionStatus } from '../components/common/ConnectionStatus';
import { useApiWithStore } from '../hooks/useApiWithStore';
import { useApiStore, useApiSelectors } from '../store/apiStore';
import { api } from '../services/api';
import { healthService } from '../services/healthService';

export const ApiTestPage: React.FC = () => {
  const { isFullyConnected, hasErrors } = useApiSelectors();
  const { globalError, errors, isLoading } = useApiStore();

  // Test API hooks
  const healthCheck = useApiWithStore(api.system.healthCheck, {
    key: 'main-health-check',
    showGlobalLoading: true,
    showGlobalError: true,
  });

  const aiHealthCheck = useApiWithStore(api.system.aiHealthCheck, {
    key: 'ai-health-check', 
    showGlobalLoading: true,
    showGlobalError: true,
  });

  const handleTestMainAPI = async () => {
    await healthCheck.execute();
  };

  const handleTestAIAPI = async () => {
    await aiHealthCheck.execute();
  };

  const handleTestBoth = async () => {
    await healthService.testConnection();
  };

  const handleQuickTest = async () => {
    const result = await healthService.quickTest();
    alert(`Quick test result: ${result ? 'Success' : 'Failed'}`);
  };

  return (
    <div className="max-w-4xl mx-auto p-6 space-y-6">
      <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
        API Integration Test Page
      </h1>
      
      <p className="text-gray-600 dark:text-gray-400">
        This page demonstrates the API integration, connection health checks, 
        and error handling system.
      </p>

      {/* Connection Status Overview */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <ConnectionStatus showDetails className="col-span-full md:col-span-1" />
        
        <div className="bg-white dark:bg-gray-800 border rounded-lg p-4">
          <h3 className="text-lg font-medium mb-4">Global State</h3>
          <div className="space-y-2 text-sm">
            <div className="flex justify-between">
              <span>Connected:</span>
              <span className={isFullyConnected ? 'text-green-600' : 'text-red-600'}>
                {isFullyConnected ? 'Yes' : 'No'}
              </span>
            </div>
            <div className="flex justify-between">
              <span>Loading:</span>
              <span className={isLoading ? 'text-yellow-600' : 'text-gray-500'}>
                {isLoading ? 'Yes' : 'No'}
              </span>
            </div>
            <div className="flex justify-between">
              <span>Errors:</span>
              <span className={hasErrors ? 'text-red-600' : 'text-green-600'}>
                {hasErrors ? 'Yes' : 'None'}
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* API Test Buttons */}
      <div className="bg-white dark:bg-gray-800 border rounded-lg p-6">
        <h3 className="text-lg font-medium mb-4">API Connection Tests</h3>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <button
            onClick={handleTestMainAPI}
            disabled={healthCheck.loading}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
          >
            {healthCheck.loading ? 'Testing...' : 'Test Main API'}
          </button>
          
          <button
            onClick={handleTestAIAPI}
            disabled={aiHealthCheck.loading}
            className="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 disabled:opacity-50"
          >
            {aiHealthCheck.loading ? 'Testing...' : 'Test AI API'}
          </button>
          
          <button
            onClick={handleTestBoth}
            className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700"
          >
            Test Both APIs
          </button>
          
          <button
            onClick={handleQuickTest}
            className="px-4 py-2 bg-orange-600 text-white rounded-lg hover:bg-orange-700"
          >
            Quick Test
          </button>
        </div>
      </div>

      {/* Test Results */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Main API Results */}
        <div className="bg-white dark:bg-gray-800 border rounded-lg p-4">
          <h4 className="font-medium mb-2">Main API (Port 8000)</h4>
          {healthCheck.data && (
            <div className="text-sm text-green-600">
              <pre className="bg-gray-100 dark:bg-gray-700 p-2 rounded text-xs overflow-auto">
                {JSON.stringify(healthCheck.data, null, 2)}
              </pre>
            </div>
          )}
          {healthCheck.error && (
            <div className="text-sm text-red-600">
              Error: {healthCheck.error}
            </div>
          )}
        </div>

        {/* AI API Results */}
        <div className="bg-white dark:bg-gray-800 border rounded-lg p-4">
          <h4 className="font-medium mb-2">AI API (Port 8001)</h4>
          {aiHealthCheck.data && (
            <div className="text-sm text-green-600">
              <pre className="bg-gray-100 dark:bg-gray-700 p-2 rounded text-xs overflow-auto">
                {JSON.stringify(aiHealthCheck.data, null, 2)}
              </pre>
            </div>
          )}
          {aiHealthCheck.error && (
            <div className="text-sm text-red-600">
              Error: {aiHealthCheck.error}
            </div>
          )}
        </div>
      </div>

      {/* Global Errors */}
      {globalError && (
        <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-4">
          <h4 className="font-medium text-red-800 dark:text-red-200 mb-2">Global Error</h4>
          <p className="text-red-700 dark:text-red-300">{globalError}</p>
        </div>
      )}

      {/* Individual Errors */}
      {Object.keys(errors).length > 0 && (
        <div className="bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-800 rounded-lg p-4">
          <h4 className="font-medium text-yellow-800 dark:text-yellow-200 mb-2">Operation Errors</h4>
          <div className="space-y-1">
            {Object.entries(errors).map(([key, error]) => (
              <div key={key} className="text-yellow-700 dark:text-yellow-300 text-sm">
                <strong>{key}:</strong> {error}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Development Tools */}
      <div className="bg-gray-50 dark:bg-gray-900 border rounded-lg p-4">
        <h4 className="font-medium mb-2">Developer Tools</h4>
        <p className="text-sm text-gray-600 dark:text-gray-400 mb-2">
          Open browser console and try these commands:
        </p>
        <div className="bg-gray-100 dark:bg-gray-800 p-3 rounded text-xs font-mono">
          <div>• <code>window.testConnection()</code> - Test both APIs</div>
          <div>• <code>window.quickTest()</code> - Quick connection test</div>
          <div>• <code>window.healthService</code> - Access health service</div>
        </div>
      </div>
    </div>
  );
};