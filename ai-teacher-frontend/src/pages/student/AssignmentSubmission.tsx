import React, { useState } from 'react';
import {
  DocumentTextIcon,
  CloudArrowUpIcon,
  CheckCircleIcon,
  ExclamationTriangleIcon,
  PlayIcon
} from '@heroicons/react/24/outline';

const AssignmentSubmission: React.FC = () => {
  const [code, setCode] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isRunning, setIsRunning] = useState(false);
  
  // Mock assignment data
  const assignment = {
    id: '1',
    title: 'Binary Search Implementation',
    description: 'Implement a binary search algorithm in C that finds the position of a target value in a sorted array.',
    dueDate: '2024-09-15',
    maxPoints: 100,
    language: 'C',
    testCases: [
      { input: 'arr=[1,3,5,7,9], target=5', expected: '2' },
      { input: 'arr=[1,3,5,7,9], target=1', expected: '0' },
      { input: 'arr=[1,3,5,7,9], target=10', expected: '-1' }
    ]
  };

  const handleSubmit = async () => {
    setIsSubmitting(true);
    // Simulate submission
    setTimeout(() => {
      setIsSubmitting(false);
      alert('Assignment submitted successfully!');
    }, 2000);
  };

  const handleRunCode = async () => {
    setIsRunning(true);
    // Simulate code execution
    setTimeout(() => {
      setIsRunning(false);
      alert('Code executed successfully!');
    }, 1500);
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="mb-8">
          <h2 className="text-2xl font-bold leading-7 text-gray-900 sm:text-3xl">
            {assignment.title}
          </h2>
          <p className="mt-1 text-sm text-gray-500">
            Due: {new Date(assignment.dueDate).toLocaleDateString()} • Max Points: {assignment.maxPoints} • Language: {assignment.language}
          </p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Assignment Details */}
          <div className="lg:col-span-1">
            <div className="bg-white shadow rounded-lg p-6 mb-6">
              <h3 className="text-lg font-medium text-gray-900 mb-4">Assignment Details</h3>
              <p className="text-sm text-gray-600 mb-4">{assignment.description}</p>
              
              <div className="space-y-3">
                <div className="flex items-center">
                  <DocumentTextIcon className="h-5 w-5 text-gray-400 mr-2" />
                  <span className="text-sm text-gray-600">Due: {new Date(assignment.dueDate).toLocaleDateString()}</span>
                </div>
                <div className="flex items-center">
                  <CheckCircleIcon className="h-5 w-5 text-gray-400 mr-2" />
                  <span className="text-sm text-gray-600">Max Points: {assignment.maxPoints}</span>
                </div>
              </div>
            </div>

            {/* Test Cases */}
            <div className="bg-white shadow rounded-lg p-6">
              <h3 className="text-lg font-medium text-gray-900 mb-4">Test Cases</h3>
              <div className="space-y-3">
                {assignment.testCases.map((testCase, index) => (
                  <div key={index} className="border border-gray-200 rounded-md p-3">
                    <div className="text-xs font-medium text-gray-500 uppercase">Test Case {index + 1}</div>
                    <div className="mt-1 text-sm text-gray-900">
                      <strong>Input:</strong> {testCase.input}
                    </div>
                    <div className="text-sm text-gray-900">
                      <strong>Expected:</strong> {testCase.expected}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Code Editor */}
          <div className="lg:col-span-2">
            <div className="bg-white shadow rounded-lg">
              <div className="px-6 py-4 border-b border-gray-200">
                <div className="flex justify-between items-center">
                  <h3 className="text-lg font-medium text-gray-900">Code Editor</h3>
                  <div className="flex space-x-2">
                    <button
                      onClick={handleRunCode}
                      disabled={isRunning || !code.trim()}
                      className="inline-flex items-center px-3 py-2 border border-gray-300 shadow-sm text-sm leading-4 font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                      <PlayIcon className="h-4 w-4 mr-2" />
                      {isRunning ? 'Running...' : 'Run Code'}
                    </button>
                    <button
                      onClick={handleSubmit}
                      disabled={isSubmitting || !code.trim()}
                      className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                      <CloudArrowUpIcon className="h-4 w-4 mr-2" />
                      {isSubmitting ? 'Submitting...' : 'Submit'}
                    </button>
                  </div>
                </div>
              </div>
              
              <div className="p-6">
                <textarea
                  value={code}
                  onChange={(e) => setCode(e.target.value)}
                  className="w-full h-96 p-4 text-sm font-mono border border-gray-300 rounded-md focus:ring-indigo-500 focus:border-indigo-500"
                  placeholder={`// Write your ${assignment.language} code here...\n#include <stdio.h>\n\nint binarySearch(int arr[], int size, int target) {\n    // Your implementation here\n    return -1;\n}\n\nint main() {\n    // Test your implementation\n    return 0;\n}`}
                  style={{ fontFamily: 'Fira Code, Monaco, Consolas, monospace' }}
                />
              </div>
            </div>

            {/* Output Panel */}
            <div className="mt-6 bg-white shadow rounded-lg">
              <div className="px-6 py-4 border-b border-gray-200">
                <h3 className="text-lg font-medium text-gray-900">Output</h3>
              </div>
              <div className="p-6">
                <div className="bg-black text-green-400 p-4 rounded-md font-mono text-sm min-h-32">
                  <div className="text-gray-400">// Output will appear here when you run your code</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AssignmentSubmission;