import React from 'react';
import {
  ChartBarIcon,
  ArrowTrendingUpIcon,
  ArrowTrendingDownIcon,
  CheckCircleIcon,
  ExclamationCircleIcon,
  BookOpenIcon,
  ClockIcon,
  StarIcon
} from '@heroicons/react/24/outline';

const ProgressTracker: React.FC = () => {
  // Mock data
  const studentProgress = {
    overallProgress: 78,
    overallGrade: 'B+',
    totalPoints: 1240,
    maxPoints: 1600,
    coursesInProgress: 3,
    completedAssignments: 12,
    totalAssignments: 16
  };

  const courseProgress = [
    {
      id: '1',
      name: 'CS101 - Intro to Programming',
      progress: 85,
      grade: 'A-',
      points: 850,
      maxPoints: 1000,
      status: 'excellent',
      assignments: { completed: 8, total: 10 }
    },
    {
      id: '2',
      name: 'CS201 - Data Structures',
      progress: 72,
      grade: 'B',
      points: 360,
      maxPoints: 500,
      status: 'good',
      assignments: { completed: 3, total: 4 }
    },
    {
      id: '3',
      name: 'CS301 - Algorithms',
      progress: 45,
      grade: 'C+',
      points: 90,
      maxPoints: 200,
      status: 'needs_attention',
      assignments: { completed: 1, total: 2 }
    }
  ];

  const recentActivity = [
    {
      type: 'assignment_completed',
      title: 'Binary Search Implementation',
      course: 'CS101',
      score: 95,
      date: '2024-09-10',
      status: 'excellent'
    },
    {
      type: 'assignment_submitted',
      title: 'Linked List Operations',
      course: 'CS201',
      score: 78,
      date: '2024-09-08',
      status: 'good'
    },
    {
      type: 'feedback_received',
      title: 'Array Manipulation',
      course: 'CS101',
      score: 88,
      date: '2024-09-06',
      status: 'good'
    }
  ];

  const learningInsights = [
    {
      category: 'Strengths',
      items: ['Algorithm Design', 'Code Structure', 'Problem Solving'],
      icon: <CheckCircleIcon className="h-5 w-5 text-green-500" />
    },
    {
      category: 'Areas for Improvement',
      items: ['Time Complexity Analysis', 'Memory Management', 'Debugging Skills'],
      icon: <ExclamationCircleIcon className="h-5 w-5 text-yellow-500" />
    },
    {
      category: 'Recommended Focus',
      items: ['Practice more complex algorithms', 'Review data structure fundamentals', 'Work on edge case handling'],
      icon: <StarIcon className="h-5 w-5 text-blue-500" />
    }
  ];

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'excellent': return 'bg-green-100 text-green-800';
      case 'good': return 'bg-blue-100 text-blue-800';
      case 'needs_attention': return 'bg-yellow-100 text-yellow-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const getActivityIcon = (type: string) => {
    switch (type) {
      case 'assignment_completed':
        return <CheckCircleIcon className="h-6 w-6 text-green-500" />;
      case 'assignment_submitted':
        return <ClockIcon className="h-6 w-6 text-blue-500" />;
      case 'feedback_received':
        return <BookOpenIcon className="h-6 w-6 text-purple-500" />;
      default:
        return <ChartBarIcon className="h-6 w-6 text-gray-500" />;
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="mb-8">
          <h2 className="text-2xl font-bold leading-7 text-gray-900 sm:text-3xl">
            Progress Tracker
          </h2>
          <p className="mt-1 text-sm text-gray-500">
            Monitor your academic progress and performance across all courses
          </p>
        </div>

        {/* Overall Stats */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <div className="bg-white overflow-hidden shadow rounded-lg">
            <div className="p-5">
              <div className="flex items-center">
                <div className="flex-shrink-0">
                  <ChartBarIcon className="h-6 w-6 text-indigo-400" />
                </div>
                <div className="ml-5 w-0 flex-1">
                  <dl>
                    <dt className="text-sm font-medium text-gray-500 truncate">Overall Progress</dt>
                    <dd className="flex items-baseline">
                      <div className="text-2xl font-semibold text-gray-900">{studentProgress.overallProgress}%</div>
                      <div className="ml-2 flex items-baseline text-sm font-semibold text-green-600">
                        <ArrowTrendingUpIcon className="h-4 w-4 text-green-500 mr-1" />
                        +5%
                      </div>
                    </dd>
                  </dl>
                </div>
              </div>
            </div>
          </div>

          <div className="bg-white overflow-hidden shadow rounded-lg">
            <div className="p-5">
              <div className="flex items-center">
                <div className="flex-shrink-0">
                  <StarIcon className="h-6 w-6 text-yellow-400" />
                </div>
                <div className="ml-5 w-0 flex-1">
                  <dl>
                    <dt className="text-sm font-medium text-gray-500 truncate">Overall Grade</dt>
                    <dd className="text-2xl font-semibold text-gray-900">{studentProgress.overallGrade}</dd>
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
                    <dt className="text-sm font-medium text-gray-500 truncate">Assignments</dt>
                    <dd className="text-2xl font-semibold text-gray-900">
                      {studentProgress.completedAssignments}/{studentProgress.totalAssignments}
                    </dd>
                  </dl>
                </div>
              </div>
            </div>
          </div>

          <div className="bg-white overflow-hidden shadow rounded-lg">
            <div className="p-5">
              <div className="flex items-center">
                <div className="flex-shrink-0">
                  <BookOpenIcon className="h-6 w-6 text-purple-400" />
                </div>
                <div className="ml-5 w-0 flex-1">
                  <dl>
                    <dt className="text-sm font-medium text-gray-500 truncate">Total Points</dt>
                    <dd className="text-2xl font-semibold text-gray-900">
                      {studentProgress.totalPoints}/{studentProgress.maxPoints}
                    </dd>
                  </dl>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Course Progress */}
          <div className="bg-white shadow rounded-lg p-6">
            <h3 className="text-lg font-medium text-gray-900 mb-6">Course Progress</h3>
            <div className="space-y-6">
              {courseProgress.map((course) => (
                <div key={course.id} className="border border-gray-200 rounded-lg p-4">
                  <div className="flex justify-between items-start mb-3">
                    <div>
                      <h4 className="text-sm font-medium text-gray-900">{course.name}</h4>
                      <p className="text-sm text-gray-500">
                        {course.assignments.completed}/{course.assignments.total} assignments completed
                      </p>
                    </div>
                    <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${getStatusColor(course.status)}`}>
                      {course.grade}
                    </span>
                  </div>
                  
                  <div className="flex items-center mb-2">
                    <div className="flex-1">
                      <div className="w-full bg-gray-200 rounded-full h-2">
                        <div
                          className="bg-indigo-600 h-2 rounded-full"
                          style={{ width: `${course.progress}%` }}
                        ></div>
                      </div>
                    </div>
                    <span className="ml-3 text-sm font-medium text-gray-600">{course.progress}%</span>
                  </div>
                  
                  <div className="text-xs text-gray-500">
                    {course.points}/{course.maxPoints} points earned
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Recent Activity */}
          <div className="bg-white shadow rounded-lg p-6">
            <h3 className="text-lg font-medium text-gray-900 mb-6">Recent Activity</h3>
            <div className="flow-root">
              <ul className="-mb-8">
                {recentActivity.map((activity, index) => (
                  <li key={index}>
                    <div className="relative pb-8">
                      {index !== recentActivity.length - 1 && (
                        <span className="absolute top-4 left-4 -ml-px h-full w-0.5 bg-gray-200" />
                      )}
                      <div className="relative flex space-x-3">
                        <div className="flex-shrink-0">
                          {getActivityIcon(activity.type)}
                        </div>
                        <div className="min-w-0 flex-1 pt-1.5 flex justify-between space-x-4">
                          <div>
                            <p className="text-sm text-gray-900">
                              <span className="font-medium">{activity.title}</span> in {activity.course}
                            </p>
                            <p className="text-sm text-gray-500">Score: {activity.score}%</p>
                          </div>
                          <div className="text-right text-sm whitespace-nowrap text-gray-500">
                            {new Date(activity.date).toLocaleDateString()}
                          </div>
                        </div>
                      </div>
                    </div>
                  </li>
                ))}
              </ul>
            </div>
          </div>

          {/* Learning Insights */}
          <div className="lg:col-span-2 bg-white shadow rounded-lg p-6">
            <h3 className="text-lg font-medium text-gray-900 mb-6">AI Learning Insights</h3>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              {learningInsights.map((insight, index) => (
                <div key={index} className="border border-gray-200 rounded-lg p-4">
                  <div className="flex items-center mb-3">
                    {insight.icon}
                    <h4 className="ml-2 text-sm font-medium text-gray-900">{insight.category}</h4>
                  </div>
                  <ul className="space-y-1">
                    {insight.items.map((item, itemIndex) => (
                      <li key={itemIndex} className="text-sm text-gray-600">• {item}</li>
                    ))}
                  </ul>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ProgressTracker;