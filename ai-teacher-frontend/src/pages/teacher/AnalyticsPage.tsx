import React from 'react';
import {
  ChartBarIcon,
  ArrowTrendingUpIcon,
  UserGroupIcon,
  BookOpenIcon,
  ClockIcon,
  CheckCircleIcon
} from '@heroicons/react/24/outline';

const AnalyticsPage: React.FC = () => {
  // Mock data for demonstration
  const classStats = {
    totalStudents: 45,
    activeAssignments: 8,
    avgCompletionRate: 87,
    avgScore: 82.5,
    totalSubmissions: 324,
    pendingReviews: 12
  };

  const weeklyData = [
    { week: 'Week 1', submissions: 32, avgScore: 78 },
    { week: 'Week 2', submissions: 28, avgScore: 81 },
    { week: 'Week 3', submissions: 35, avgScore: 85 },
    { week: 'Week 4', submissions: 40, avgScore: 83 },
    { week: 'Week 5', submissions: 38, avgScore: 87 },
    { week: 'Week 6', submissions: 42, avgScore: 89 },
  ];

  const topChallenges = [
    { topic: 'Loop Logic', errorCount: 24, improvement: '+15%' },
    { topic: 'Array Indexing', errorCount: 18, improvement: '+8%' },
    { topic: 'Function Parameters', errorCount: 12, improvement: '+20%' },
    { topic: 'Variable Scope', errorCount: 9, improvement: '+12%' },
    { topic: 'Conditional Logic', errorCount: 7, improvement: '+5%' },
  ];

  const performanceDistribution = {
    excellent: 12, // 90-100%
    good: 18,      // 80-89%
    average: 10,   // 70-79%
    belowAverage: 5 // <70%
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="mb-8">
          <h2 className="text-2xl font-bold leading-7 text-gray-900 sm:text-3xl">
            Analytics Dashboard
          </h2>
          <p className="mt-1 text-sm text-gray-500">
            Comprehensive insights into student performance and learning patterns
          </p>
        </div>

        {/* Key Metrics */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
          <div className="bg-white overflow-hidden shadow rounded-lg">
            <div className="p-5">
              <div className="flex items-center">
                <div className="flex-shrink-0">
                  <UserGroupIcon className="h-6 w-6 text-indigo-400" />
                </div>
                <div className="ml-5 w-0 flex-1">
                  <dl>
                    <dt className="text-sm font-medium text-gray-500 truncate">Total Students</dt>
                    <dd className="flex items-baseline">
                      <div className="text-2xl font-semibold text-gray-900">{classStats.totalStudents}</div>
                      <div className="ml-2 flex items-baseline text-sm font-semibold text-green-600">
                        <ArrowTrendingUpIcon className="h-4 w-4 text-green-500 mr-1" />
                        +5 this semester
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
                  <ChartBarIcon className="h-6 w-6 text-green-400" />
                </div>
                <div className="ml-5 w-0 flex-1">
                  <dl>
                    <dt className="text-sm font-medium text-gray-500 truncate">Average Score</dt>
                    <dd className="flex items-baseline">
                      <div className="text-2xl font-semibold text-gray-900">{classStats.avgScore}%</div>
                      <div className="ml-2 flex items-baseline text-sm font-semibold text-green-600">
                        <ArrowTrendingUpIcon className="h-4 w-4 text-green-500 mr-1" />
                        +3.2%
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
                  <CheckCircleIcon className="h-6 w-6 text-blue-400" />
                </div>
                <div className="ml-5 w-0 flex-1">
                  <dl>
                    <dt className="text-sm font-medium text-gray-500 truncate">Completion Rate</dt>
                    <dd className="flex items-baseline">
                      <div className="text-2xl font-semibold text-gray-900">{classStats.avgCompletionRate}%</div>
                      <div className="ml-2 flex items-baseline text-sm font-semibold text-green-600">
                        <ArrowTrendingUpIcon className="h-4 w-4 text-green-500 mr-1" />
                        +1.5%
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
                  <BookOpenIcon className="h-6 w-6 text-purple-400" />
                </div>
                <div className="ml-5 w-0 flex-1">
                  <dl>
                    <dt className="text-sm font-medium text-gray-500 truncate">Active Assignments</dt>
                    <dd className="text-2xl font-semibold text-gray-900">{classStats.activeAssignments}</dd>
                  </dl>
                </div>
              </div>
            </div>
          </div>

          <div className="bg-white overflow-hidden shadow rounded-lg">
            <div className="p-5">
              <div className="flex items-center">
                <div className="flex-shrink-0">
                  <ClockIcon className="h-6 w-6 text-yellow-400" />
                </div>
                <div className="ml-5 w-0 flex-1">
                  <dl>
                    <dt className="text-sm font-medium text-gray-500 truncate">Pending Reviews</dt>
                    <dd className="text-2xl font-semibold text-gray-900">{classStats.pendingReviews}</dd>
                  </dl>
                </div>
              </div>
            </div>
          </div>

          <div className="bg-white overflow-hidden shadow rounded-lg">
            <div className="p-5">
              <div className="flex items-center">
                <div className="flex-shrink-0">
                  <ChartBarIcon className="h-6 w-6 text-red-400" />
                </div>
                <div className="ml-5 w-0 flex-1">
                  <dl>
                    <dt className="text-sm font-medium text-gray-500 truncate">Total Submissions</dt>
                    <dd className="text-2xl font-semibold text-gray-900">{classStats.totalSubmissions}</dd>
                  </dl>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Weekly Submissions Chart */}
          <div className="bg-white shadow rounded-lg p-6">
            <h3 className="text-lg font-medium text-gray-900 mb-4">Weekly Submissions & Scores</h3>
            <div className="space-y-4">
              {weeklyData.map((week) => (
                <div key={week.week} className="flex items-center justify-between">
                  <div className="flex-1">
                    <div className="flex justify-between items-center mb-1">
                      <span className="text-sm font-medium text-gray-700">{week.week}</span>
                      <span className="text-sm text-gray-500">{week.submissions} submissions</span>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-2">
                      <div
                        className="bg-indigo-600 h-2 rounded-full"
                        style={{ width: `${week.avgScore}%` }}
                      ></div>
                    </div>
                    <div className="mt-1 text-xs text-gray-500">Avg Score: {week.avgScore}%</div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Performance Distribution */}
          <div className="bg-white shadow rounded-lg p-6">
            <h3 className="text-lg font-medium text-gray-900 mb-4">Performance Distribution</h3>
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center">
                  <div className="w-4 h-4 bg-green-500 rounded mr-3"></div>
                  <span className="text-sm text-gray-700">Excellent (90-100%)</span>
                </div>
                <span className="text-sm font-medium text-gray-900">{performanceDistribution.excellent} students</span>
              </div>
              <div className="flex items-center justify-between">
                <div className="flex items-center">
                  <div className="w-4 h-4 bg-blue-500 rounded mr-3"></div>
                  <span className="text-sm text-gray-700">Good (80-89%)</span>
                </div>
                <span className="text-sm font-medium text-gray-900">{performanceDistribution.good} students</span>
              </div>
              <div className="flex items-center justify-between">
                <div className="flex items-center">
                  <div className="w-4 h-4 bg-yellow-500 rounded mr-3"></div>
                  <span className="text-sm text-gray-700">Average (70-79%)</span>
                </div>
                <span className="text-sm font-medium text-gray-900">{performanceDistribution.average} students</span>
              </div>
              <div className="flex items-center justify-between">
                <div className="flex items-center">
                  <div className="w-4 h-4 bg-red-500 rounded mr-3"></div>
                  <span className="text-sm text-gray-700">Below Average (&lt;70%)</span>
                </div>
                <span className="text-sm font-medium text-gray-900">{performanceDistribution.belowAverage} students</span>
              </div>
            </div>

            {/* Visual Chart */}
            <div className="mt-6">
              <div className="w-full bg-gray-200 rounded-full h-6 flex overflow-hidden">
                <div 
                  className="bg-green-500 h-full"
                  style={{ width: `${(performanceDistribution.excellent / classStats.totalStudents) * 100}%` }}
                ></div>
                <div 
                  className="bg-blue-500 h-full"
                  style={{ width: `${(performanceDistribution.good / classStats.totalStudents) * 100}%` }}
                ></div>
                <div 
                  className="bg-yellow-500 h-full"
                  style={{ width: `${(performanceDistribution.average / classStats.totalStudents) * 100}%` }}
                ></div>
                <div 
                  className="bg-red-500 h-full"
                  style={{ width: `${(performanceDistribution.belowAverage / classStats.totalStudents) * 100}%` }}
                ></div>
              </div>
            </div>
          </div>

          {/* Top Challenges */}
          <div className="bg-white shadow rounded-lg p-6">
            <h3 className="text-lg font-medium text-gray-900 mb-4">Most Common Challenges</h3>
            <div className="space-y-4">
              {topChallenges.map((challenge, index) => (
                <div key={challenge.topic} className="flex items-center justify-between">
                  <div className="flex items-center">
                    <div className="flex items-center justify-center w-6 h-6 bg-indigo-100 rounded-full mr-3">
                      <span className="text-xs font-medium text-indigo-600">{index + 1}</span>
                    </div>
                    <div>
                      <div className="text-sm font-medium text-gray-900">{challenge.topic}</div>
                      <div className="text-xs text-gray-500">{challenge.errorCount} errors this week</div>
                    </div>
                  </div>
                  <div className="flex items-center">
                    <span className="text-xs text-green-600 mr-1">{challenge.improvement}</span>
                    <ArrowTrendingUpIcon className="h-4 w-4 text-green-500" />
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* AI Insights */}
          <div className="bg-white shadow rounded-lg p-6">
            <h3 className="text-lg font-medium text-gray-900 mb-4">AI Teaching Insights</h3>
            <div className="space-y-4">
              <div className="bg-blue-50 border border-blue-200 rounded-md p-4">
                <div className="flex">
                  <div className="flex-shrink-0">
                    <ChartBarIcon className="h-5 w-5 text-blue-400" />
                  </div>
                  <div className="ml-3">
                    <h4 className="text-sm font-medium text-blue-800">Pattern Recognition</h4>
                    <p className="text-sm text-blue-700 mt-1">
                      Students struggle most with loop boundaries on Fridays, suggesting fatigue effects.
                    </p>
                  </div>
                </div>
              </div>

              <div className="bg-green-50 border border-green-200 rounded-md p-4">
                <div className="flex">
                  <div className="flex-shrink-0">
                    <ArrowTrendingUpIcon className="h-5 w-5 text-green-400" />
                  </div>
                  <div className="ml-3">
                    <h4 className="text-sm font-medium text-green-800">Improvement Trend</h4>
                    <p className="text-sm text-green-700 mt-1">
                      Overall class performance improved 15% after implementing personalized feedback.
                    </p>
                  </div>
                </div>
              </div>

              <div className="bg-yellow-50 border border-yellow-200 rounded-md p-4">
                <div className="flex">
                  <div className="flex-shrink-0">
                    <ClockIcon className="h-5 w-5 text-yellow-400" />
                  </div>
                  <div className="ml-3">
                    <h4 className="text-sm font-medium text-yellow-800">Timing Insight</h4>
                    <p className="text-sm text-yellow-700 mt-1">
                      Students who submit assignments before 6 PM score 12% higher on average.
                    </p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AnalyticsPage;