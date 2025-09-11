import React from 'react';
import { useAuthStore } from '../../store/authStore';
import { Card } from '../../components/ui';
import { BookOpen, Users, FileText, TrendingUp } from 'lucide-react';

const DashboardPage: React.FC = () => {
  const { user } = useAuthStore();

  const stats = [
    {
      title: 'Total Courses',
      value: '12',
      change: '+2 this month',
      icon: BookOpen,
      color: 'text-blue-600',
      bgColor: 'bg-blue-100'
    },
    {
      title: 'Active Students',
      value: '156',
      change: '+12 this week',
      icon: Users,
      color: 'text-green-600',
      bgColor: 'bg-green-100'
    },
    {
      title: 'Assignments',
      value: '8',
      change: '3 pending',
      icon: FileText,
      color: 'text-purple-600',
      bgColor: 'bg-purple-100'
    },
    {
      title: 'Progress',
      value: '87%',
      change: '+5% this week',
      icon: TrendingUp,
      color: 'text-orange-600',
      bgColor: 'bg-orange-100'
    }
  ];

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-secondary-900">
          Welcome back, {user?.firstName || 'User'}!
        </h1>
        <p className="text-secondary-600">
          Here's what's happening with your learning today.
        </p>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {stats.map((stat, index) => (
          <Card key={index} className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-secondary-600">{stat.title}</p>
                <p className="text-2xl font-bold text-secondary-900">{stat.value}</p>
                <p className="text-sm text-secondary-500">{stat.change}</p>
              </div>
              <div className={`p-3 rounded-lg ${stat.bgColor}`}>
                <stat.icon className={`w-6 h-6 ${stat.color}`} />
              </div>
            </div>
          </Card>
        ))}
      </div>

      {/* Recent Activity */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card className="p-6">
          <h3 className="text-lg font-semibold text-secondary-900 mb-4">Recent Activity</h3>
          <div className="space-y-4">
            <div className="flex items-center space-x-3">
              <div className="w-2 h-2 bg-green-500 rounded-full"></div>
              <div className="flex-1">
                <p className="text-sm text-secondary-900">Completed assignment: React Basics</p>
                <p className="text-xs text-secondary-500">2 hours ago</p>
              </div>
            </div>
            <div className="flex items-center space-x-3">
              <div className="w-2 h-2 bg-blue-500 rounded-full"></div>
              <div className="flex-1">
                <p className="text-sm text-secondary-900">Started new course: Advanced JavaScript</p>
                <p className="text-xs text-secondary-500">1 day ago</p>
              </div>
            </div>
            <div className="flex items-center space-x-3">
              <div className="w-2 h-2 bg-yellow-500 rounded-full"></div>
              <div className="flex-1">
                <p className="text-sm text-secondary-900">Received feedback on: CSS Grid</p>
                <p className="text-xs text-secondary-500">3 days ago</p>
              </div>
            </div>
          </div>
        </Card>

        <Card className="p-6">
          <h3 className="text-lg font-semibold text-secondary-900 mb-4">Upcoming Deadlines</h3>
          <div className="space-y-4">
            <div className="flex items-center justify-between p-3 bg-red-50 rounded-lg">
              <div>
                <p className="text-sm font-medium text-red-900">JavaScript Project</p>
                <p className="text-xs text-red-600">Due in 2 days</p>
              </div>
              <span className="px-2 py-1 text-xs font-medium text-red-800 bg-red-200 rounded-full">
                Urgent
              </span>
            </div>
            <div className="flex items-center justify-between p-3 bg-yellow-50 rounded-lg">
              <div>
                <p className="text-sm font-medium text-yellow-900">React Quiz</p>
                <p className="text-xs text-yellow-600">Due in 5 days</p>
              </div>
              <span className="px-2 py-1 text-xs font-medium text-yellow-800 bg-yellow-200 rounded-full">
                Pending
              </span>
            </div>
            <div className="flex items-center justify-between p-3 bg-green-50 rounded-lg">
              <div>
                <p className="text-sm font-medium text-green-900">CSS Assignment</p>
                <p className="text-xs text-green-600">Due in 1 week</p>
              </div>
              <span className="px-2 py-1 text-xs font-medium text-green-800 bg-green-200 rounded-full">
                On Track
              </span>
            </div>
          </div>
        </Card>
      </div>
    </div>
  );
};

export default DashboardPage;
