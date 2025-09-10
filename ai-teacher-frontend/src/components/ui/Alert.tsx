import React from 'react';
import {
  CheckCircleIcon,
  ExclamationTriangleIcon,
  InformationCircleIcon,
  XCircleIcon,
  XMarkIcon,
} from '@heroicons/react/24/outline';
import { cn } from '../../utils';
import type { AlertProps } from '../../types';

const iconMap = {
  success: CheckCircleIcon,
  warning: ExclamationTriangleIcon,
  info: InformationCircleIcon,
  error: XCircleIcon,
};

const alertStyles = {
  success: {
    container: 'bg-green-50 border-green-200 text-green-800',
    icon: 'text-green-600',
    title: 'text-green-800',
    message: 'text-green-700',
  },
  warning: {
    container: 'bg-yellow-50 border-yellow-200 text-yellow-800',
    icon: 'text-yellow-600',
    title: 'text-yellow-800',
    message: 'text-yellow-700',
  },
  info: {
    container: 'bg-blue-50 border-blue-200 text-blue-800',
    icon: 'text-blue-600',
    title: 'text-blue-800',
    message: 'text-blue-700',
  },
  error: {
    container: 'bg-red-50 border-red-200 text-red-800',
    icon: 'text-red-600',
    title: 'text-red-800',
    message: 'text-red-700',
  },
};

export const Alert: React.FC<AlertProps> = ({
  type,
  message,
  title,
  dismissible = false,
  onDismiss,
  className,
  icon = true,
  actions,
}) => {
  const IconComponent = iconMap[type];
  const styles = alertStyles[type];

  return (
    <div
      className={cn(
        'rounded-md border p-4',
        styles.container,
        className
      )}
    >
      <div className="flex">
        {icon && (
          <div className="flex-shrink-0">
            <IconComponent className={cn('h-5 w-5', styles.icon)} />
          </div>
        )}
        
        <div className={cn('ml-3 flex-1', !icon && 'ml-0')}>
          {title && (
            <h3 className={cn('text-sm font-medium', styles.title)}>
              {title}
            </h3>
          )}
          <div className={cn('text-sm', title ? 'mt-1' : '', styles.message)}>
            {message}
          </div>
          {actions && (
            <div className="mt-3">
              {actions}
            </div>
          )}
        </div>

        {dismissible && onDismiss && (
          <div className="ml-auto pl-3">
            <div className="-mx-1.5 -my-1.5">
              <button
                type="button"
                className={cn(
                  'inline-flex rounded-md p-1.5 focus:outline-none focus:ring-2 focus:ring-offset-2 transition-colors',
                  styles.icon,
                  'hover:bg-black hover:bg-opacity-10 focus:ring-current'
                )}
                onClick={onDismiss}
              >
                <XMarkIcon className="h-5 w-5" />
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default Alert;