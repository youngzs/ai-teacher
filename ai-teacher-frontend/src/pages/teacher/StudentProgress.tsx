import React, { useState } from 'react';
import {
  ChartBarIcon,
  UserIcon,
  BookOpenIcon,
  ArrowTrendingUpIcon,
  ArrowTrendingDownIcon,
  CheckCircleIcon,
  ExclamationCircleIcon
} from '@heroicons/react/24/outline';

interface StudentProgress {
  id: string;
  name: string;
  email: string;
  avatar?: string;
  course: string;
  assignments: {
    completed: number;
    total: number;
    averageScore: number;
  };
  progress: {
    overall: number;
    trend: 'up' | 'down' | 'stable';
    weeklyChange: number;
  };
  lastActivity: string;
  strengths: string[];
  weaknesses: string[];
  status: 'excellent' | 'good' | 'needs_attention' | 'at_risk';
}

const StudentProgress: React.FC = () => {
  const [students] = useState<StudentProgress[]>([
    {
      id: '1',
      name: 'Alice Johnson',
      email: 'alice.johnson@university.edu',
      course: 'CS101 - Intro to Programming',
      assignments: {
        completed: 7,
        total: 8,
        averageScore: 92
      },
      progress: {
        overall: 95,
        trend: 'up',
        weeklyChange: 5
      },
      lastActivity: '2024-09-10',
      strengths: ['Algorithm Design', 'Code Quality', 'Problem Solving'],
      weaknesses: ['Debugging', 'Time Complexity'],
      status: 'excellent'
    },
    {
      id: '2',
      name: 'Bob Smith',
      email: 'bob.smith@university.edu',
      course: 'CS101 - Intro to Programming',
      assignments: {
        completed: 6,
        total: 8,
        averageScore: 78
      },
      progress: {
        overall: 72,
        trend: 'stable',
        weeklyChange: 0
      },
      lastActivity: '2024-09-09',
      strengths: ['Persistence', 'Code Documentation'],
      weaknesses: ['Logic Errors', 'Syntax Issues', 'Array Handling'],
      status: 'good'
    },
    {
      id: '3',
      name: 'Carol Williams',
      email: 'carol.williams@university.edu',
      course: 'CS201 - Data Structures',
      assignments: {
        completed: 4,
        total: 6,
        averageScore: 65
      },
      progress: {
        overall: 58,
        trend: 'down',
        weeklyChange: -8
      },
      lastActivity: '2024-09-07',
      strengths: ['Basic Concepts'],
      weaknesses: ['Complex Data Structures', 'Memory Management', 'Algorithm Efficiency'],
      status: 'needs_attention'
    },
    {
      id: '4',
      name: 'David Brown',
      email: 'david.brown@university.edu',
      course: 'CS101 - Intro to Programming',
      assignments: {
        completed: 3,
        total: 8,
        averageScore: 45
      },
      progress: {
        overall: 35,
        trend: 'down',
        weeklyChange: -12
      },
      lastActivity: '2024-09-05',
      strengths: [],
      weaknesses: ['Basic Syntax', 'Logic Flow', 'Problem Understanding', 'Code Structure'],
      status: 'at_risk'
    }
  ]);

  const [selectedCourse, setSelectedCourse] = useState<string>('all');
  const [selectedStatus, setSelectedStatus] = useState<string>('all');

  const getStatusColor = (status: StudentProgress['status']) => {
    switch (status) {
      case 'excellent':
        return 'bg-green-100 text-green-800';
      case 'good':
        return 'bg-blue-100 text-blue-800';
      case 'needs_attention':
        return 'bg-yellow-100 text-yellow-800';
      case 'at_risk':
        return 'bg-red-100 text-red-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const getStatusIcon = (status: StudentProgress['status']) => {
    switch (status) {
      case 'excellent':
        return <CheckCircleIcon className="h-5 w-5 text-green-500" />;
      case 'good':
        return <CheckCircleIcon className="h-5 w-5 text-blue-500" />;
      case 'needs_attention':
        return <ExclamationCircleIcon className="h-5 w-5 text-yellow-500" />;
      case 'at_risk':
        return <ExclamationCircleIcon className="h-5 w-5 text-red-500" />;
      default:
        return null;
    }
  };

  const getTrendIcon = (trend: 'up' | 'down' | 'stable') => {
    switch (trend) {
      case 'up':
        return <ArrowTrendingUpIcon className="h-4 w-4 text-green-500" />;
      case 'down':
        return <ArrowTrendingDownIcon className="h-4 w-4 text-red-500" />;
      default:
        return <div className="h-4 w-4 bg-gray-400 rounded-full"></div>;
    }
  };

  const filteredStudents = students.filter(student => {
    const courseMatch = selectedCourse === 'all' || student.course.includes(selectedCourse);
    const statusMatch = selectedStatus === 'all' || student.status === selectedStatus;
    return courseMatch && statusMatch;
  });

  const overallStats = {
    totalStudents: students.length,
    excellent: students.filter(s => s.status === 'excellent').length,
    good: students.filter(s => s.status === 'good').length,
    needsAttention: students.filter(s => s.status === 'needs_attention').length,
    atRisk: students.filter(s => s.status === 'at_risk').length,
    averageScore: Math.round(students.reduce((sum, s) => sum + s.assignments.averageScore, 0) / students.length)
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="mb-8">
          <h2 className="text-2xl font-bold leading-7 text-gray-900 sm:text-3xl">
            Student Progress
          </h2>
          <p className="mt-1 text-sm text-gray-500">
            Monitor student performance and identify areas for improvement
          </p>
        </div>

        {/* Stats Overview */}
        <div className="grid grid-cols-1 md:grid-cols-5 gap-6 mb-8">
          <div className="bg-white overflow-hidden shadow rounded-lg">
            <div className="p-5">
              <div className="flex items-center">
                <div className="flex-shrink-0">
                  <UserIcon className="h-6 w-6 text-gray-400" />
                </div>
                <div className="ml-5 w-0 flex-1">
                  <dl>
                    <dt className="text-sm font-medium text-gray-500 truncate">Total Students</dt>
                    <dd className="text-lg font-medium text-gray-900">{overallStats.totalStudents}</dd>
                  </dl>
                </div>
              </div>
            </div>
          </div>

          <div className="bg-white overflow-hidden shadow rounded-lg">
            <div className="p-5">
              <div className="flex items-center">
                <div className="flex-shrink-0">
                  <CheckCircleIcon className="h-6 w-6 text-green-400" />
                </div>
                <div className="ml-5 w-0 flex-1">
                  <dl>
                    <dt className="text-sm font-medium text-gray-500 truncate">Excellent</dt>
                    <dd className="text-lg font-medium text-gray-900">{overallStats.excellent}</dd>
                  </dl>
                </div>
              </div>
            </div>
          </div>

          <div className="bg-white overflow-hidden shadow rounded-lg">
            <div className="p-5">
              <div className="flex items-center">
                <div className="flex-shrink-0">
                  <CheckCircleIcon className="h-6 w-6 text-blue-400" />
                </div>
                <div className="ml-5 w-0 flex-1">
                  <dl>
                    <dt className="text-sm font-medium text-gray-500 truncate">Good</dt>
                    <dd className="text-lg font-medium text-gray-900">{overallStats.good}</dd>
                  </dl>
                </div>
              </div>
            </div>
          </div>

          <div className="bg-white overflow-hidden shadow rounded-lg">
            <div className="p-5">
              <div className="flex items-center">
                <div className="flex-shrink-0">
                  <ExclamationCircleIcon className="h-6 w-6 text-yellow-400" />
                </div>
                <div className="ml-5 w-0 flex-1">
                  <dl>
                    <dt className="text-sm font-medium text-gray-500 truncate">Needs Attention</dt>
                    <dd className="text-lg font-medium text-gray-900">{overallStats.needsAttention}</dd>
                  </dl>
                </div>
              </div>
            </div>
          </div>

          <div className="bg-white overflow-hidden shadow rounded-lg">
            <div className="p-5">
              <div className="flex items-center">
                <div className="flex-shrink-0">
                  <ExclamationCircleIcon className="h-6 w-6 text-red-400" />
                </div>
                <div className="ml-5 w-0 flex-1">
                  <dl>
                    <dt className="text-sm font-medium text-gray-500 truncate">At Risk</dt>
                    <dd className="text-lg font-medium text-gray-900">{overallStats.atRisk}</dd>
                  </dl>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Filters */}
        <div className="bg-white shadow rounded-lg mb-6">
          <div className="px-6 py-4">
            <div className="flex flex-col sm:flex-row gap-4">
              <div className="flex-1">
                <label htmlFor="course-filter" className="block text-sm font-medium text-gray-700">
                  Filter by Course
                </label>
                <select
                  id="course-filter"
                  value={selectedCourse}
                  onChange={(e) => setSelectedCourse(e.target.value)}
                  className="mt-1 block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm rounded-md"
                >
                  <option value="all">All Courses</option>
                  <option value="CS101">CS101 - Intro to Programming</option>
                  <option value="CS201">CS201 - Data Structures</option>
                  <option value="CS301">CS301 - Web Development</option>
                </select>
              </div>

              <div className="flex-1">
                <label htmlFor="status-filter" className="block text-sm font-medium text-gray-700">
                  Filter by Status
                </label>
                <select
                  id="status-filter"
                  value={selectedStatus}
                  onChange={(e) => setSelectedStatus(e.target.value)}
                  className="mt-1 block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm rounded-md"
                >
                  <option value="all">All Statuses</option>
                  <option value="excellent">Excellent</option>
                  <option value="good">Good</option>
                  <option value="needs_attention">Needs Attention</option>
                  <option value="at_risk">At Risk</option>
                </select>
              </div>
            </div>
          </div>
        </div>

        {/* Student List */}
        <div className="bg-white shadow rounded-lg">
          <div className="px-6 py-4 border-b border-gray-200">
            <h3 className="text-lg font-medium text-gray-900">Student Progress Details</h3>
          </div>
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Student
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Course
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Assignments
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Progress
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Status
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Last Activity
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {filteredStudents.map((student) => (
                  <tr key={student.id} className="hover:bg-gray-50">
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="flex items-center">
                        <div className="h-10 w-10 bg-gray-300 rounded-full flex items-center justify-center">
                          <UserIcon className="h-6 w-6 text-gray-600" />
                        </div>
                        <div className="ml-4">
                          <div className="text-sm font-medium text-gray-900">{student.name}</div>
                          <div className="text-sm text-gray-500">{student.email}</div>
                        </div>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {student.course}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm text-gray-900">
                        {student.assignments.completed}/{student.assignments.total}
                      </div>
                      <div className="text-sm text-gray-500">
                        Avg: {student.assignments.averageScore}%
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="flex items-center">
                        <div className="flex-1">
                          <div className="w-full bg-gray-200 rounded-full h-2">
                            <div
                              className="bg-indigo-600 h-2 rounded-full"
                              style={{ width: `${student.progress.overall}%` }}
                            ></div>
                          </div>
                        </div>
                        <div className="ml-2 flex items-center">
                          {getTrendIcon(student.progress.trend)}
                          <span className="ml-1 text-sm text-gray-600">
                            {student.progress.overall}%
                          </span>
                        </div>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="flex items-center">
                        {getStatusIcon(student.status)}
                        <span className={`ml-2 inline-flex px-2 py-1 text-xs font-semibold rounded-full ${getStatusColor(student.status)}`}>
                          {student.status.replace('_', ' ')}
                        </span>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {new Date(student.lastActivity).toLocaleDateString()}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
};

export default StudentProgress;