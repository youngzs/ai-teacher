import React, { useState } from 'react';
import {
  ChartBarIcon,
  BookOpenIcon,
  CheckCircleIcon,
  ExclamationCircleIcon,
  ClockIcon,
  StarIcon,
  FaceSmileIcon,
  FaceFrownIcon
} from '@heroicons/react/24/outline';

const FeedbackHistory: React.FC = () => {
  const [selectedFilter, setSelectedFilter] = useState<string>('all');
  
  // Mock feedback data
  const feedbackHistory = [
    {
      id: '1',
      assignmentTitle: 'Binary Search Implementation',
      course: 'CS101 - Intro to Programming',
      submissionDate: '2024-09-10',
      score: 95,
      maxScore: 100,
      status: 'excellent',
      feedback: {
        overall: 'Excellent implementation! Your binary search algorithm is well-structured and handles edge cases properly.',
        strengths: [
          'Clean and readable code structure',
          'Proper handling of edge cases',
          'Efficient time complexity implementation'
        ],
        improvements: [
          'Consider adding more detailed comments for complex logic'
        ],
        suggestions: [
          'Try implementing iterative version as well',
          'Explore binary search variations like finding first/last occurrence'
        ]
      },
      aiInsights: 'Strong understanding of divide-and-conquer algorithms. Ready for more advanced topics.'
    },
    {
      id: '2',
      assignmentTitle: 'Linked List Operations',
      course: 'CS201 - Data Structures',
      submissionDate: '2024-09-08',
      score: 78,
      maxScore: 100,
      status: 'good',
      feedback: {
        overall: 'Good work on implementing basic linked list operations. Some areas need improvement.',
        strengths: [
          'Correct insertion and deletion logic',
          'Good understanding of pointers'
        ],
        improvements: [
          'Memory leak in deletion function',
          'Missing null pointer checks',
          'Inconsistent variable naming'
        ],
        suggestions: [
          'Practice more with memory management',
          'Review defensive programming techniques',
          'Use consistent naming conventions'
        ]
      },
      aiInsights: 'Shows good grasp of basic concepts but needs to focus on edge cases and memory management.'
    },
    {
      id: '3',
      assignmentTitle: 'Array Manipulation',
      course: 'CS101 - Intro to Programming',
      submissionDate: '2024-09-06',
      score: 88,
      maxScore: 100,
      status: 'good',
      feedback: {
        overall: 'Solid array manipulation implementation with room for optimization.',
        strengths: [
          'Correct algorithm implementation',
          'Good test case coverage',
          'Clear variable naming'
        ],
        improvements: [
          'Algorithm can be optimized for better time complexity',
          'Some redundant operations in the main loop'
        ],
        suggestions: [
          'Study more efficient sorting algorithms',
          'Practice algorithmic optimization techniques'
        ]
      },
      aiInsights: 'Demonstrates solid programming fundamentals. Focus on algorithm optimization next.'
    },
    {
      id: '4',
      assignmentTitle: 'Simple Calculator',
      course: 'CS101 - Intro to Programming',
      submissionDate: '2024-09-04',
      score: 62,
      maxScore: 100,
      status: 'needs_improvement',
      feedback: {
        overall: 'Basic functionality implemented but several issues need attention.',
        strengths: [
          'Basic arithmetic operations work correctly',
          'User input handling is functional'
        ],
        improvements: [
          'Division by zero not handled',
          'Input validation is missing',
          'Code lacks proper structure and organization',
          'No error handling for invalid inputs'
        ],
        suggestions: [
          'Learn about exception handling',
          'Practice input validation techniques',
          'Study code organization best practices',
          'Review error handling patterns'
        ]
      },
      aiInsights: 'Needs to focus on defensive programming and error handling. Consider reviewing basic programming concepts.'
    }
  ];

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'excellent': return 'bg-green-100 text-green-800';
      case 'good': return 'bg-blue-100 text-blue-800';
      case 'needs_improvement': return 'bg-yellow-100 text-yellow-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'excellent':
        return <CheckCircleIcon className="h-5 w-5 text-green-500" />;
      case 'good':
        return <FaceSmileIcon className="h-5 w-5 text-blue-500" />;
      case 'needs_improvement':
        return <ExclamationCircleIcon className="h-5 w-5 text-yellow-500" />;
      default:
        return <ClockIcon className="h-5 w-5 text-gray-500" />;
    }
  };

  const getScoreColor = (score: number, maxScore: number) => {
    const percentage = (score / maxScore) * 100;
    if (percentage >= 90) return 'text-green-600';
    if (percentage >= 80) return 'text-blue-600';
    if (percentage >= 70) return 'text-yellow-600';
    return 'text-red-600';
  };

  const filteredFeedback = selectedFilter === 'all' 
    ? feedbackHistory 
    : feedbackHistory.filter(item => item.status === selectedFilter);

  const averageScore = feedbackHistory.reduce((sum, item) => sum + (item.score / item.maxScore * 100), 0) / feedbackHistory.length;

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="mb-8">
          <h2 className="text-2xl font-bold leading-7 text-gray-900 sm:text-3xl">
            Feedback History
          </h2>
          <p className="mt-1 text-sm text-gray-500">
            Review detailed feedback and insights from your assignment submissions
          </p>
        </div>

        {/* Summary Stats */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <div className="bg-white overflow-hidden shadow rounded-lg">
            <div className="p-5">
              <div className="flex items-center">
                <div className="flex-shrink-0">
                  <ChartBarIcon className="h-6 w-6 text-indigo-400" />
                </div>
                <div className="ml-5 w-0 flex-1">
                  <dl>
                    <dt className="text-sm font-medium text-gray-500 truncate">Average Score</dt>
                    <dd className="text-2xl font-semibold text-gray-900">{averageScore.toFixed(1)}%</dd>
                  </dl>
                </div>
              </div>
            </div>
          </div>

          <div className="bg-white overflow-hidden shadow rounded-lg">
            <div className="p-5">
              <div className="flex items-center">
                <div className="flex-shrink-0">
                  <BookOpenIcon className="h-6 w-6 text-green-400" />
                </div>
                <div className="ml-5 w-0 flex-1">
                  <dl>
                    <dt className="text-sm font-medium text-gray-500 truncate">Total Submissions</dt>
                    <dd className="text-2xl font-semibold text-gray-900">{feedbackHistory.length}</dd>
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
                    <dd className="text-2xl font-semibold text-gray-900">
                      {feedbackHistory.filter(f => f.status === 'excellent').length}
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
                    <dt className="text-sm font-medium text-gray-500 truncate">Improvement Trend</dt>
                    <dd className="text-2xl font-semibold text-gray-900">+12%</dd>
                  </dl>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Filter */}
        <div className="bg-white shadow rounded-lg mb-6">
          <div className="px-6 py-4">
            <label htmlFor="status-filter" className="block text-sm font-medium text-gray-700 mb-2">
              Filter by Status
            </label>
            <select
              id="status-filter"
              value={selectedFilter}
              onChange={(e) => setSelectedFilter(e.target.value)}
              className="block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm rounded-md"
            >
              <option value="all">All Feedback</option>
              <option value="excellent">Excellent</option>
              <option value="good">Good</option>
              <option value="needs_improvement">Needs Improvement</option>
            </select>
          </div>
        </div>

        {/* Feedback List */}
        <div className="space-y-6">
          {filteredFeedback.map((feedback) => (
            <div key={feedback.id} className="bg-white shadow rounded-lg overflow-hidden">
              {/* Header */}
              <div className="px-6 py-4 border-b border-gray-200">
                <div className="flex justify-between items-start">
                  <div>
                    <h3 className="text-lg font-medium text-gray-900">{feedback.assignmentTitle}</h3>
                    <p className="text-sm text-gray-500">{feedback.course}</p>
                  </div>
                  <div className="flex items-center space-x-4">
                    <div className="text-right">
                      <div className={`text-2xl font-bold ${getScoreColor(feedback.score, feedback.maxScore)}`}>
                        {feedback.score}/{feedback.maxScore}
                      </div>
                      <div className="text-sm text-gray-500">{new Date(feedback.submissionDate).toLocaleDateString()}</div>
                    </div>
                    <div className="flex items-center">
                      {getStatusIcon(feedback.status)}
                      <span className={`ml-2 inline-flex px-2 py-1 text-xs font-semibold rounded-full ${getStatusColor(feedback.status)}`}>
                        {feedback.status.replace('_', ' ')}
                      </span>
                    </div>
                  </div>
                </div>
              </div>

              {/* Content */}
              <div className="px-6 py-6">
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                  {/* Feedback Details */}
                  <div className="space-y-6">
                    <div>
                      <h4 className="text-sm font-medium text-gray-900 mb-2">Overall Feedback</h4>
                      <p className="text-sm text-gray-600">{feedback.feedback.overall}</p>
                    </div>

                    {feedback.feedback.strengths.length > 0 && (
                      <div>
                        <h4 className="text-sm font-medium text-gray-900 mb-2 flex items-center">
                          <CheckCircleIcon className="h-4 w-4 text-green-500 mr-1" />
                          Strengths
                        </h4>
                        <ul className="text-sm text-gray-600 space-y-1">
                          {feedback.feedback.strengths.map((strength, index) => (
                            <li key={index} className="flex items-start">
                              <span className="text-green-500 mr-2">•</span>
                              {strength}
                            </li>
                          ))}
                        </ul>
                      </div>
                    )}

                    {feedback.feedback.improvements.length > 0 && (
                      <div>
                        <h4 className="text-sm font-medium text-gray-900 mb-2 flex items-center">
                          <ExclamationCircleIcon className="h-4 w-4 text-yellow-500 mr-1" />
                          Areas for Improvement
                        </h4>
                        <ul className="text-sm text-gray-600 space-y-1">
                          {feedback.feedback.improvements.map((improvement, index) => (
                            <li key={index} className="flex items-start">
                              <span className="text-yellow-500 mr-2">•</span>
                              {improvement}
                            </li>
                          ))}
                        </ul>
                      </div>
                    )}
                  </div>

                  {/* AI Insights & Suggestions */}
                  <div className="space-y-6">
                    <div>
                      <h4 className="text-sm font-medium text-gray-900 mb-2 flex items-center">
                        <StarIcon className="h-4 w-4 text-blue-500 mr-1" />
                        AI Learning Insights
                      </h4>
                      <div className="bg-blue-50 border border-blue-200 rounded-md p-3">
                        <p className="text-sm text-blue-700">{feedback.aiInsights}</p>
                      </div>
                    </div>

                    {feedback.feedback.suggestions.length > 0 && (
                      <div>
                        <h4 className="text-sm font-medium text-gray-900 mb-2 flex items-center">
                          <BookOpenIcon className="h-4 w-4 text-purple-500 mr-1" />
                          Study Suggestions
                        </h4>
                        <ul className="text-sm text-gray-600 space-y-1">
                          {feedback.feedback.suggestions.map((suggestion, index) => (
                            <li key={index} className="flex items-start">
                              <span className="text-purple-500 mr-2">•</span>
                              {suggestion}
                            </li>
                          ))}
                        </ul>
                      </div>
                    )}
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>

        {filteredFeedback.length === 0 && (
          <div className="text-center py-12">
            <FaceFrownIcon className="mx-auto h-12 w-12 text-gray-400" />
            <h3 className="mt-2 text-sm font-medium text-gray-900">No feedback found</h3>
            <p className="mt-1 text-sm text-gray-500">No feedback matches the selected filter.</p>
          </div>
        )}
      </div>
    </div>
  );
};

export default FeedbackHistory;