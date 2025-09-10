import React from 'react';
import { useParams } from 'react-router-dom';

export const AssignmentDetailPage: React.FC = () => {
  const { assignmentId } = useParams<{ assignmentId: string }>();

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-secondary-900">Assignment Details</h1>
        <p className="text-secondary-600 mt-1">Assignment ID: {assignmentId}</p>
      </div>
      
      <div className="bg-white rounded-lg shadow p-8 text-center">
        <h2 className="text-xl font-semibold text-secondary-900 mb-4">Assignment Management</h2>
        <p className="text-secondary-600">Assignment details and student submissions will be displayed here.</p>
        <p className="text-sm text-secondary-500 mt-2">Features: Assignment info, submission list, grading, statistics</p>
      </div>
    </div>
  );
};