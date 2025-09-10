import React from 'react';

export const ProfilePage: React.FC = () => {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-secondary-900">Profile</h1>
        <p className="text-secondary-600 mt-1">Manage your account information</p>
      </div>
      
      <div className="bg-white rounded-lg shadow p-8 text-center">
        <h2 className="text-xl font-semibold text-secondary-900 mb-4">User Profile</h2>
        <p className="text-secondary-600">User profile management will be implemented here.</p>
        <p className="text-sm text-secondary-500 mt-2">Features: Edit profile, change avatar, update contact information</p>
      </div>
    </div>
  );
};