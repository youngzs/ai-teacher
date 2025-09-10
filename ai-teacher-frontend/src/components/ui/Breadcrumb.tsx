import React from 'react';
import { Link } from 'react-router-dom';
import { ChevronRightIcon, HomeIcon } from '@heroicons/react/24/outline';
import { cn } from '../../utils';
import type { BreadcrumbProps } from '../../types';

export const Breadcrumb: React.FC<BreadcrumbProps> = ({
  items,
  className,
}) => {
  if (!items || items.length === 0) return null;

  return (
    <nav className={cn('flex', className)} aria-label="Breadcrumb">
      <ol className="inline-flex items-center space-x-1 md:space-x-3">
        {items.map((item, index) => {
          const isFirst = index === 0;
          const isLast = index === items.length - 1;

          return (
            <li key={index} className="inline-flex items-center">
              {!isFirst && (
                <ChevronRightIcon className="flex-shrink-0 h-4 w-4 text-gray-400 mx-2" />
              )}
              
              <div className="flex items-center">
                {isFirst && (
                  <HomeIcon className="flex-shrink-0 h-4 w-4 text-gray-400 mr-2" />
                )}
                
                {item.href && !isLast ? (
                  <Link
                    to={item.href}
                    className="text-sm font-medium text-gray-500 hover:text-gray-700 transition-colors"
                  >
                    {item.label}
                  </Link>
                ) : (
                  <span
                    className={cn(
                      'text-sm font-medium',
                      isLast ? 'text-gray-900' : 'text-gray-500'
                    )}
                  >
                    {item.label}
                  </span>
                )}
              </div>
            </li>
          );
        })}
      </ol>
    </nav>
  );
};

export default Breadcrumb;