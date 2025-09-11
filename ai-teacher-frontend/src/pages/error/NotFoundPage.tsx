import React from 'react';
import { Link } from 'react-router-dom';
import { Home, ArrowLeft } from 'lucide-react';

const NotFoundPage: React.FC = () => {
  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-primary-50 via-white to-secondary-50">
      <div className="max-w-md w-full text-center space-y-8">
        <div>
          <h1 className="text-9xl font-bold text-primary-600">404</h1>
          <h2 className="text-2xl font-bold text-secondary-900 mt-4">Page Not Found</h2>
          <p className="text-secondary-600 mt-2">
            Sorry, we couldn't find the page you're looking for.
          </p>
        </div>

        <div className="space-y-4">
          <Link 
            to="/" 
            className="w-full inline-flex items-center justify-center rounded-md font-medium transition-all duration-200 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500 focus-visible:ring-offset-2 bg-blue-600 text-white hover:bg-blue-700 active:bg-blue-800 shadow-sm hover:shadow h-10 px-4 text-sm gap-2"
          >
            <Home className="w-4 h-4 mr-2" />
            Go Home
          </Link>

          <Link 
            to="#" 
            onClick={() => history.back()}
            className="w-full inline-flex items-center justify-center rounded-md font-medium transition-all duration-200 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500 focus-visible:ring-offset-2 border border-gray-300 bg-transparent text-gray-700 hover:bg-gray-50 active:bg-gray-100 h-10 px-4 text-sm gap-2"
          >
            <ArrowLeft className="w-4 h-4 mr-2" />
            Go Back
          </Link>
        </div>
      </div>
    </div>
  );
};

export default NotFoundPage;
