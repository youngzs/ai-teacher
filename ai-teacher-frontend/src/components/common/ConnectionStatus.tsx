import React from 'react';
import { useApiStore, useApiSelectors } from '../../store/apiStore';

interface ConnectionStatusProps {
  className?: string;
  showDetails?: boolean;
}

export const ConnectionStatus: React.FC<ConnectionStatusProps> = ({ 
  className = '', 
  showDetails = false 
}) => {
  const { apiConnected, aiApiConnected, lastHealthCheck } = useApiStore();
  const { isFullyConnected } = useApiSelectors();

  const getStatusColor = () => {
    if (isFullyConnected) return 'text-green-500';
    if (apiConnected || aiApiConnected) return 'text-yellow-500';
    return 'text-red-500';
  };

  const getStatusText = () => {
    if (isFullyConnected) return 'All systems connected';
    if (apiConnected && !aiApiConnected) return 'Main API connected, AI API disconnected';
    if (!apiConnected && aiApiConnected) return 'AI API connected, Main API disconnected';
    return 'Disconnected from all services';
  };

  const getStatusIcon = () => {
    if (isFullyConnected) return '●';
    if (apiConnected || aiApiConnected) return '◐';
    return '●';
  };

  if (!showDetails) {
    return (
      <div className={`flex items-center space-x-2 ${className}`}>
        <span className={`text-sm ${getStatusColor()}`}>
          {getStatusIcon()}
        </span>
        <span className="text-xs text-gray-500">
          {isFullyConnected ? 'Connected' : 'Issues detected'}
        </span>
      </div>
    );
  }

  return (
    <div className={`bg-white dark:bg-gray-800 border rounded-lg p-4 ${className}`}>
      <div className="flex items-center justify-between mb-2">
        <h3 className="text-sm font-medium text-gray-900 dark:text-white">
          System Status
        </h3>
        <span className={`text-sm ${getStatusColor()}`}>
          {getStatusIcon()} {isFullyConnected ? 'Healthy' : 'Issues'}
        </span>
      </div>
      
      <div className="space-y-2 text-sm">
        <div className="flex items-center justify-between">
          <span className="text-gray-600 dark:text-gray-300">Main API</span>
          <span className={apiConnected ? 'text-green-500' : 'text-red-500'}>
            {apiConnected ? '● Connected' : '● Disconnected'}
          </span>
        </div>
        
        <div className="flex items-center justify-between">
          <span className="text-gray-600 dark:text-gray-300">AI API</span>
          <span className={aiApiConnected ? 'text-green-500' : 'text-red-500'}>
            {aiApiConnected ? '● Connected' : '● Disconnected'}
          </span>
        </div>
        
        {lastHealthCheck && (
          <div className="flex items-center justify-between pt-2 border-t">
            <span className="text-gray-600 dark:text-gray-300">Last Check</span>
            <span className="text-xs text-gray-500">
              {lastHealthCheck.toLocaleTimeString()}
            </span>
          </div>
        )}
      </div>
      
      <p className="text-xs text-gray-500 mt-2">
        {getStatusText()}
      </p>
    </div>
  );
};