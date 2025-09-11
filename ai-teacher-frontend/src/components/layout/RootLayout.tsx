import React from 'react';
import { Outlet } from 'react-router-dom';
import { useAuthStore } from '../../store/authStore';
import Header from './Header';
import Sidebar from './Sidebar';
import { Breadcrumb } from '../ui';
import { useBreadcrumbs } from '../../hooks/useBreadcrumbs';

const RootLayout: React.FC = () => {
  const { isAuthenticated } = useAuthStore();
  const breadcrumbs = useBreadcrumbs();

  if (!isAuthenticated) {
    // For unauthenticated routes, render without layout chrome
    return (
      <div className="min-h-screen bg-gray-50">
        <Outlet />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <Header />

      <div className="flex">
        <Sidebar />

        <main className="flex-1 lg:ml-64">
          <div className="py-6">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
              {breadcrumbs.length > 0 && (
                <div className="mb-4">
                  <Breadcrumb items={breadcrumbs} />
                </div>
              )}

              <Outlet />
            </div>
          </div>
        </main>
      </div>
    </div>
  );
};

export default RootLayout;
