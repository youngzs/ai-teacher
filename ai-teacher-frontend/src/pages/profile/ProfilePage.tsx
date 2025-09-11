import React, { useState } from 'react';
import { useAuthStore } from '../../store/authStore';
import { Card, Button, Input } from '../../components/ui';
import { User, Mail, Shield, Save } from 'lucide-react';

const ProfilePage: React.FC = () => {
  const { user, updateProfile } = useAuthStore();
  const [isEditing, setIsEditing] = useState(false);
  const [formData, setFormData] = useState({
    firstName: user?.firstName || '',
    lastName: user?.lastName || '',
    email: user?.email || '',
  });

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  const handleSave = async () => {
    try {
      await updateProfile(formData);
      setIsEditing(false);
    } catch (error) {
      console.error('Failed to update profile:', error);
    }
  };

  const handleCancel = () => {
    setFormData({
      firstName: user?.firstName || '',
      lastName: user?.lastName || '',
      email: user?.email || '',
    });
    setIsEditing(false);
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-secondary-900">Profile Settings</h1>
          <p className="text-secondary-600">Manage your account information and preferences</p>
        </div>
        <div className="flex space-x-3">
          {isEditing ? (
            <>
              <Button variant="outline" onClick={handleCancel}>
                Cancel
              </Button>
              <Button onClick={handleSave}>
                <Save className="w-4 h-4 mr-2" />
                Save Changes
              </Button>
            </>
          ) : (
            <Button onClick={() => setIsEditing(true)}>
              Edit Profile
            </Button>
          )}
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Profile Information */}
        <div className="lg:col-span-2">
          <Card className="p-6">
            <h3 className="text-lg font-semibold text-secondary-900 mb-6">Personal Information</h3>

            <div className="space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <Input
                  name="firstName"
                  label="First Name"
                  value={formData.firstName}
                  onChange={handleInputChange}
                  disabled={!isEditing}
                  leftIcon={<User className="w-4 h-4" />}
                />
                <Input
                  name="lastName"
                  label="Last Name"
                  value={formData.lastName}
                  onChange={handleInputChange}
                  disabled={!isEditing}
                  leftIcon={<User className="w-4 h-4" />}
                />
              </div>

              <Input
                name="email"
                type="email"
                label="Email Address"
                value={formData.email}
                onChange={handleInputChange}
                disabled={!isEditing}
                leftIcon={<Mail className="w-4 h-4" />}
              />
            </div>
          </Card>
        </div>

        {/* Profile Summary */}
        <div className="space-y-6">
          <Card className="p-6">
            <h3 className="text-lg font-semibold text-secondary-900 mb-4">Account Summary</h3>

            <div className="space-y-4">
              <div className="flex items-center space-x-3">
                <div className="w-10 h-10 bg-primary-100 rounded-full flex items-center justify-center">
                  <User className="w-5 h-5 text-primary-600" />
                </div>
                <div>
                  <p className="text-sm font-medium text-secondary-900">Role</p>
                  <p className="text-sm text-secondary-600 capitalize">{user?.role}</p>
                </div>
              </div>

              <div className="flex items-center space-x-3">
                <div className="w-10 h-10 bg-green-100 rounded-full flex items-center justify-center">
                  <Shield className="w-5 h-5 text-green-600" />
                </div>
                <div>
                  <p className="text-sm font-medium text-secondary-900">Account Status</p>
                  <p className="text-sm text-green-600">Active</p>
                </div>
              </div>

              <div className="flex items-center space-x-3">
                <div className="w-10 h-10 bg-blue-100 rounded-full flex items-center justify-center">
                  <Mail className="w-5 h-5 text-blue-600" />
                </div>
                <div>
                  <p className="text-sm font-medium text-secondary-900">Email Verified</p>
                  <p className="text-sm text-blue-600">Verified</p>
                </div>
              </div>
            </div>
          </Card>

          <Card className="p-6">
            <h3 className="text-lg font-semibold text-secondary-900 mb-4">Quick Stats</h3>

            <div className="space-y-3">
              <div className="flex justify-between">
                <span className="text-sm text-secondary-600">Courses Completed</span>
                <span className="text-sm font-medium text-secondary-900">8</span>
              </div>
              <div className="flex justify-between">
                <span className="text-sm text-secondary-600">Assignments Submitted</span>
                <span className="text-sm font-medium text-secondary-900">24</span>
              </div>
              <div className="flex justify-between">
                <span className="text-sm text-secondary-600">Average Score</span>
                <span className="text-sm font-medium text-secondary-900">87%</span>
              </div>
              <div className="flex justify-between">
                <span className="text-sm text-secondary-600">Member Since</span>
                <span className="text-sm font-medium text-secondary-900">Jan 2024</span>
              </div>
            </div>
          </Card>
        </div>
      </div>
    </div>
  );
};

export default ProfilePage;
