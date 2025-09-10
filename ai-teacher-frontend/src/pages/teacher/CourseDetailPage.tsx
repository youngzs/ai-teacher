import React from 'react';
import { useParams } from 'react-router-dom';

export const CourseDetailPage: React.FC = () => {
  const { courseId } = useParams<{ courseId: string }>();

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-secondary-900">Course Details</h1>
        <p className="text-secondary-600 mt-1">Course ID: {courseId}</p>
      </div>
      
      <div className="bg-white rounded-lg shadow p-8 text-center">
        <h2 className="text-xl font-semibold text-secondary-900 mb-4">Course Detail View</h2>
        <p className="text-secondary-600">Detailed course information and management will be implemented here.</p>
        <p className="text-sm text-secondary-500 mt-2">Features: Course overview, student list, assignments, analytics</p>
      </div>
    </div>
  );
};