import React from 'react';
import { Card } from '../../components/ui';
import {
  BookOpen,
  Users,
  FileText,
  BarChart3,
  TrendingUp,
  Clock,
  CheckCircle,
  AlertCircle
} from 'lucide-react';

const TeacherDashboard: React.FC = () => {
  const stats = [
    {
      title: 'Total Courses',
      value: '8',
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
      value: '24',
      change: '3 pending review',
      icon: FileText,
      color: 'text-purple-600',
      bgColor: 'bg-purple-100'
    },
    {
      title: 'Avg. Score',
      value: '87%',
      change: '+5% this week',
      icon: TrendingUp,
      color: 'text-orange-600',
      bgColor: 'bg-orange-100'
    }
  ];

  const recentAssignments = [
    {
      id: '1',
      title: 'JavaScript Fundamentals Quiz',
      course: 'Web Development 101',
      submissions: 45,
      totalStudents: 50,
      dueDate: '2024-01-15',
      status: 'pending'
    },
    {
      id: '2',
      title: 'React Component Lab',
      course: 'Frontend Development',
      submissions: 38,
      totalStudents: 42,
      dueDate: '2024-01-18',
      status: 'in-progress'
    },
    {
      id: '3',
      title: 'CSS Grid Exercise',
      course: 'Web Development 101',
      submissions: 50,
      totalStudents: 50,
      dueDate: '2024-01-12',
      status: 'completed'
    }
  ];

  const upcomingDeadlines = [
    {
      title: 'Python Data Structures',
      course: 'Programming Fundamentals',
      dueDate: '2024-01-20',
      priority: 'high',
      submissions: 12,
      totalStudents: 30
    },
    {
      title: 'Database Design Project',
      course: 'Backend Development',
      dueDate: '2024-01-25',
      priority: 'medium',
      submissions: 8,
      totalStudents: 25
    },
    {
      title: 'API Integration Lab',
      course: 'Full Stack Development',
      dueDate: '2024-01-28',
      priority: 'low',
      submissions: 5,
      totalStudents: 20
    }
  ];

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed':
        return <CheckCircle className="w-4 h-4 text-green-500" />;
      case 'in-progress':
        return <Clock className="w-4 h-4 text-yellow-500" />;
      case 'pending':
        return <AlertCircle className="w-4 h-4 text-red-500" />;
      default:
        return <Clock className="w-4 h-4 text-gray-500" />;
    }
  };

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'high':
        return 'text-red-600 bg-red-100';
      case 'medium':
        return 'text-yellow-600 bg-yellow-100';
      case 'low':
        return 'text-green-600 bg-green-100';
      default:
        return 'text-gray-600 bg-gray-100';
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-secondary-900">Teacher Dashboard</h1>
        <p className="text-secondary-600">
          Overview of your courses, students, and assignments
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

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Recent Assignments */}
        <Card className="p-6">
          <h3 className="text-lg font-semibold text-secondary-900 mb-4">Recent Assignments</h3>
          <div className="space-y-4">
            {recentAssignments.map((assignment) => (
              <div key={assignment.id} className="flex items-center justify-between p-3 bg-secondary-50 rounded-lg">
                <div className="flex-1">
                  <div className="flex items-center space-x-2">
                    {getStatusIcon(assignment.status)}
                    <h4 className="text-sm font-medium text-secondary-900">{assignment.title}</h4>
                  </div>
                  <p className="text-xs text-secondary-600">{assignment.course}</p>
                  <p className="text-xs text-secondary-500">
                    {assignment.submissions}/{assignment.totalStudents} submissions
                  </p>
                </div>
                <div className="text-right">
                  <p className="text-xs text-secondary-500">Due: {assignment.dueDate}</p>
                  <div className="w-16 bg-secondary-200 rounded-full h-2 mt-1">
                    <div
                      className="bg-primary-600 h-2 rounded-full"
                      style={{
                        width: `${(assignment.submissions / assignment.totalStudents) * 100}%`
                      }}
                    ></div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </Card>

        {/* Upcoming Deadlines */}
        <Card className="p-6">
          <h3 className="text-lg font-semibold text-secondary-900 mb-4">Upcoming Deadlines</h3>
          <div className="space-y-4">
            {upcomingDeadlines.map((deadline, index) => (
              <div key={index} className="p-3 border border-secondary-200 rounded-lg">
                <div className="flex items-center justify-between mb-2">
                  <h4 className="text-sm font-medium text-secondary-900">{deadline.title}</h4>
                  <span className={`px-2 py-1 text-xs font-medium rounded-full ${getPriorityColor(deadline.priority)}`}>
                    {deadline.priority}
                  </span>
                </div>
                <p className="text-xs text-secondary-600 mb-2">{deadline.course}</p>
                <div className="flex items-center justify-between">
                  <p className="text-xs text-secondary-500">Due: {deadline.dueDate}</p>
                  <p className="text-xs text-secondary-500">
                    {deadline.submissions}/{deadline.totalStudents} submitted
                  </p>
                </div>
                <div className="w-full bg-secondary-200 rounded-full h-2 mt-2">
                  <div
                    className="bg-primary-600 h-2 rounded-full"
                    style={{
                      width: `${(deadline.submissions / deadline.totalStudents) * 100}%`
                    }}
                  ></div>
                </div>
              </div>
            ))}
          </div>
        </Card>
      </div>

      {/* Quick Actions */}
      <Card className="p-6">
        <h3 className="text-lg font-semibold text-secondary-900 mb-4">Quick Actions</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <button className="p-4 border border-secondary-200 rounded-lg hover:bg-secondary-50 transition-colors text-left">
            <BookOpen className="w-6 h-6 text-primary-600 mb-2" />
            <h4 className="font-medium text-secondary-900">Create New Course</h4>
            <p className="text-sm text-secondary-600">Set up a new course for your students</p>
          </button>
          <button className="p-4 border border-secondary-200 rounded-lg hover:bg-secondary-50 transition-colors text-left">
            <FileText className="w-6 h-6 text-primary-600 mb-2" />
            <h4 className="font-medium text-secondary-900">Create Assignment</h4>
            <p className="text-sm text-secondary-600">Add a new assignment to your course</p>
          </button>
          <button className="p-4 border border-secondary-200 rounded-lg hover:bg-secondary-50 transition-colors text-left">
            <BarChart3 className="w-6 h-6 text-primary-600 mb-2" />
            <h4 className="font-medium text-secondary-900">View Analytics</h4>
            <p className="text-sm text-secondary-600">Analyze student performance and progress</p>
          </button>
        </div>
      </Card>
    </div>
  );
};

export default TeacherDashboard;
