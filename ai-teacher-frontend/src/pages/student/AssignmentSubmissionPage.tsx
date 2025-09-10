import React from 'react';
import { useParams } from 'react-router-dom';

export const AssignmentSubmissionPage: React.FC = () => {
  const { assignmentId } = useParams<{ assignmentId: string }>();

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-secondary-900">Submit Assignment</h1>
        <p className="text-secondary-600 mt-1">Assignment ID: {assignmentId}</p>
      </div>
      
      <div className="bg-white rounded-lg shadow p-8 text-center">
        <h2 className="text-xl font-semibold text-secondary-900 mb-4">Assignment Submission Interface</h2>
        <p className="text-secondary-600">Code editor and submission functionality will be implemented here.</p>
        <p className="text-sm text-secondary-500 mt-2">Features: Code editor, file upload, test cases, real-time feedback</p>
      </div>
    </div>
  );
};