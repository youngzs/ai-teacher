import React from 'react';

export const StudentCoursesPage: React.FC = () => {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-secondary-900">My Courses</h1>
        <p className="text-secondary-600 mt-1">View your enrolled courses and assignments</p>
      </div>
      
      <div className="bg-white rounded-lg shadow p-8 text-center">
        <h2 className="text-xl font-semibold text-secondary-900 mb-4">Student Course View</h2>
        <p className="text-secondary-600">Student course overview and navigation will be implemented here.</p>
        <p className="text-sm text-secondary-500 mt-2">Features: Course list, assignments, progress tracking, resources</p>
      </div>
    </div>
  );
};