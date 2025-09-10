import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { 
  Card, 
  CardHeader, 
  CardTitle, 
  CardDescription, 
  CardContent,
  Button,
  Modal
} from '../../components/ui';
import {
  Code,
  Play,
  Upload,
  Save,
  RotateCcw,
  CheckCircle,
  XCircle,
  AlertTriangle,
  Clock,
  FileText,
  Brain,
  Lightbulb,
  Terminal,
  Eye,
  Copy,
  Download,
  HelpCircle,
  Zap
} from 'lucide-react';
import { useAppStore } from '../../store/app';

interface Assignment {
  id: string;
  title: string;
  description: string;
  requirements: string[];
  language: 'c' | 'python' | 'java';
  difficulty: 'easy' | 'medium' | 'hard';
  points: number;
  dueDate: string;
  estimatedTime: string;
  testCases: TestCase[];
  starterCode: string;
  hints: string[];
}

interface TestCase {
  id: string;
  name: string;
  input: string;
  expectedOutput: string;
  isPublic: boolean;
  points: number;
}

interface TestResult {
  testCaseId: string;
  passed: boolean;
  actualOutput: string;
  executionTime: number;
  error?: string;
}

export const SubmissionInterface: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { addNotification } = useAppStore();
  
  const [code, setCode] = useState('');
  const [isRunning, setIsRunning] = useState(false);
  const [testResults, setTestResults] = useState<TestResult[]>([]);
  const [showResults, setShowResults] = useState(false);
  const [activeTab, setActiveTab] = useState<'description' | 'tests' | 'hints'>('description');
  const [showSubmitModal, setShowSubmitModal] = useState(false);
  const [showHelpModal, setShowHelpModal] = useState(false);
  const [fontSize, setFontSize] = useState(14);
  const [theme, setTheme] = useState<'light' | 'dark'>('light');
  const [autoSaveEnabled, setAutoSaveEnabled] = useState(true);
  const [lastSaved, setLastSaved] = useState<Date | null>(null);

  // Mock assignment data
  const assignment: Assignment = {
    id: id || '1',
    title: 'Binary Search Implementation',
    description: `Implement a binary search algorithm in C that searches for a target value in a sorted array.

**Function Signature:**
\`\`\`c
int binarySearch(int arr[], int size, int target);
\`\`\`

**Return Value:**
- Return the index of the target element if found
- Return -1 if the target element is not found

**Example:**
For array [1, 3, 5, 7, 9, 11] and target 7, the function should return 3 (the index of 7).`,
    requirements: [
      'Implement the binary search algorithm correctly',
      'Handle edge cases (empty array, single element)',
      'Use proper variable names and add comments',
      'Ensure O(log n) time complexity',
      'Handle both found and not found cases'
    ],
    language: 'c',
    difficulty: 'medium',
    points: 25,
    dueDate: '2024-09-20T23:59:59',
    estimatedTime: '2 hours',
    testCases: [
      {
        id: '1',
        name: 'Basic Search - Found',
        input: '[1,3,5,7,9,11] 6 7',
        expectedOutput: '3',
        isPublic: true,
        points: 5
      },
      {
        id: '2',
        name: 'Basic Search - Not Found',
        input: '[1,3,5,7,9,11] 6 4',
        expectedOutput: '-1',
        isPublic: true,
        points: 5
      },
      {
        id: '3',
        name: 'Single Element - Found',
        input: '[5] 1 5',
        expectedOutput: '0',
        isPublic: true,
        points: 3
      },
      {
        id: '4',
        name: 'Empty Array',
        input: '[] 0 5',
        expectedOutput: '-1',
        isPublic: false,
        points: 4
      },
      {
        id: '5',
        name: 'Large Array Performance',
        input: 'large_array 1000 500',
        expectedOutput: '499',
        isPublic: false,
        points: 8
      }
    ],
    starterCode: `#include <stdio.h>

int binarySearch(int arr[], int size, int target) {
    // TODO: Implement binary search algorithm
    // Remember to use proper left, right, and mid pointers
    
    return -1; // Placeholder return
}

int main() {
    // Test your function here
    int arr[] = {1, 3, 5, 7, 9, 11};
    int size = 6;
    int target = 7;
    
    int result = binarySearch(arr, size, target);
    printf("Result: %d\\n", result);
    
    return 0;
}`,
    hints: [
      'Start with left = 0 and right = size - 1',
      'Calculate mid as (left + right) / 2 in each iteration',
      'Compare arr[mid] with target to decide which half to search',
      'Update left or right pointer based on the comparison',
      'Continue until left <= right'
    ]
  };

  useEffect(() => {
    if (assignment.starterCode) {
      setCode(assignment.starterCode);
    }
  }, [assignment.starterCode]);

  // Auto-save functionality
  useEffect(() => {
    if (autoSaveEnabled && code && code !== assignment.starterCode) {
      const timer = setTimeout(() => {
        handleSave();
      }, 2000); // Auto-save after 2 seconds of inactivity
      
      return () => clearTimeout(timer);
    }
  }, [code, autoSaveEnabled, assignment.starterCode]);

  const handleSave = () => {
    // Save code to localStorage or API
    localStorage.setItem(`assignment_${assignment.id}_code`, code);
    setLastSaved(new Date());
    addNotification({
      type: 'success',
      title: 'Code Saved',
      message: 'Your code has been saved automatically',
      duration: 2000
    });
  };

  const handleRun = async () => {
    setIsRunning(true);
    setShowResults(true);
    
    // Simulate code execution and testing
    const simulateTests = async () => {
      const results: TestResult[] = [];
      
      for (const testCase of assignment.testCases.filter(tc => tc.isPublic)) {
        await new Promise(resolve => setTimeout(resolve, 500)); // Simulate execution time
        
        // Mock test results
        const passed = Math.random() > 0.3; // 70% pass rate for demo
        results.push({
          testCaseId: testCase.id,
          passed,
          actualOutput: passed ? testCase.expectedOutput : 'Wrong output',
          executionTime: Math.random() * 100 + 10,
          error: passed ? undefined : 'Logic error in binary search implementation'
        });
      }
      
      return results;
    };

    try {
      const results = await simulateTests();
      setTestResults(results);
      
      const passedTests = results.filter(r => r.passed).length;
      const totalTests = results.length;
      
      if (passedTests === totalTests) {
        addNotification({
          type: 'success',
          title: 'All Tests Passed!',
          message: `Great job! Your code passed all ${totalTests} public tests.`,
          duration: 5000
        });
      } else {
        addNotification({
          type: 'warning',
          title: 'Some Tests Failed',
          message: `${passedTests}/${totalTests} tests passed. Check the results below.`,
          duration: 5000
        });
      }
    } catch (error) {
      addNotification({
        type: 'error',
        title: 'Execution Error',
        message: 'There was an error running your code. Please check your syntax.',
        duration: 5000
      });
    } finally {
      setIsRunning(false);
    }
  };

  const handleSubmit = () => {
    const publicTests = assignment.testCases.filter(tc => tc.isPublic);
    const passedPublicTests = testResults.filter(r => r.passed).length;
    
    if (passedPublicTests < publicTests.length) {
      addNotification({
        type: 'warning',
        title: 'Not All Tests Passed',
        message: 'Some public tests are still failing. Are you sure you want to submit?',
        duration: 5000
      });
    }
    
    setShowSubmitModal(true);
  };

  const confirmSubmit = () => {
    // Simulate submission
    addNotification({
      type: 'success',
      title: 'Assignment Submitted!',
      message: 'Your code has been submitted and will be graded by AI.',
      duration: 5000
    });
    
    setShowSubmitModal(false);
    navigate('/my-submissions');
  };

  const getDifficultyColor = (difficulty: string) => {
    switch (difficulty) {
      case 'easy': return 'text-green-600 bg-green-100';
      case 'medium': return 'text-yellow-600 bg-yellow-100';
      case 'hard': return 'text-red-600 bg-red-100';
      default: return 'text-gray-600 bg-gray-100';
    }
  };

  const isOverdue = new Date(assignment.dueDate) < new Date();

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b border-secondary-200 px-6 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <div>
              <h1 className="text-xl font-bold text-secondary-900">{assignment.title}</h1>
              <div className="flex items-center space-x-4 mt-1">
                <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getDifficultyColor(assignment.difficulty)}`}>
                  {assignment.difficulty}
                </span>
                <span className="text-sm text-secondary-600">{assignment.points} points</span>
                <span className={`text-sm flex items-center ${isOverdue ? 'text-red-600' : 'text-secondary-600'}`}>
                  <Clock className="w-4 h-4 mr-1" />
                  Due: {new Date(assignment.dueDate).toLocaleDateString()}
                  {isOverdue && ' (Overdue)'}
                </span>
              </div>
            </div>
          </div>
          
          <div className="flex items-center space-x-3">
            {lastSaved && (
              <span className="text-sm text-secondary-600">
                Saved {lastSaved.toLocaleTimeString()}
              </span>
            )}
            <Button variant="outline" onClick={() => setShowHelpModal(true)}>
              <HelpCircle className="w-4 h-4 mr-2" />
              Help
            </Button>
            <Button variant="outline" onClick={handleSave}>
              <Save className="w-4 h-4 mr-2" />
              Save
            </Button>
            <Button 
              onClick={handleRun} 
              disabled={isRunning}
              className="bg-green-600 hover:bg-green-700"
            >
              {isRunning ? (
                <>
                  <div className="animate-spin w-4 h-4 mr-2 border-2 border-white border-t-transparent rounded-full" />
                  Running...
                </>
              ) : (
                <>
                  <Play className="w-4 h-4 mr-2" />
                  Run Tests
                </>
              )}
            </Button>
            <Button 
              onClick={handleSubmit}
              className="bg-primary-600 hover:bg-primary-700"
            >
              <Upload className="w-4 h-4 mr-2" />
              Submit
            </Button>
          </div>
        </div>
      </div>

      <div className="flex h-[calc(100vh-80px)]">
        {/* Left Panel - Assignment Details */}
        <div className="w-96 bg-white border-r border-secondary-200 flex flex-col">
          {/* Tab Navigation */}
          <div className="flex border-b border-secondary-200">
            <button
              onClick={() => setActiveTab('description')}
              className={`flex-1 px-4 py-3 text-sm font-medium ${
                activeTab === 'description'
                  ? 'text-primary-600 border-b-2 border-primary-600 bg-primary-50'
                  : 'text-secondary-600 hover:text-secondary-900'
              }`}
            >
              <FileText className="w-4 h-4 inline mr-2" />
              Description
            </button>
            <button
              onClick={() => setActiveTab('tests')}
              className={`flex-1 px-4 py-3 text-sm font-medium ${
                activeTab === 'tests'
                  ? 'text-primary-600 border-b-2 border-primary-600 bg-primary-50'
                  : 'text-secondary-600 hover:text-secondary-900'
              }`}
            >
              <CheckCircle className="w-4 h-4 inline mr-2" />
              Tests ({assignment.testCases.filter(tc => tc.isPublic).length})
            </button>
            <button
              onClick={() => setActiveTab('hints')}
              className={`flex-1 px-4 py-3 text-sm font-medium ${
                activeTab === 'hints'
                  ? 'text-primary-600 border-b-2 border-primary-600 bg-primary-50'
                  : 'text-secondary-600 hover:text-secondary-900'
              }`}
            >
              <Lightbulb className="w-4 h-4 inline mr-2" />
              Hints ({assignment.hints.length})
            </button>
          </div>

          {/* Tab Content */}
          <div className="flex-1 overflow-y-auto p-4">
            {activeTab === 'description' && (
              <div className="space-y-4">
                <div>
                  <h3 className="font-semibold text-secondary-900 mb-2">Problem Description</h3>
                  <div className="prose prose-sm text-secondary-700">
                    <pre className="whitespace-pre-wrap text-sm">{assignment.description}</pre>
                  </div>
                </div>

                <div>
                  <h3 className="font-semibold text-secondary-900 mb-2">Requirements</h3>
                  <ul className="space-y-1">
                    {assignment.requirements.map((req, index) => (
                      <li key={index} className="flex items-start text-sm text-secondary-700">
                        <CheckCircle className="w-4 h-4 text-green-500 mr-2 mt-0.5 flex-shrink-0" />
                        {req}
                      </li>
                    ))}
                  </ul>
                </div>

                <div className="bg-blue-50 p-3 rounded-lg">
                  <h4 className="font-medium text-blue-900 mb-1">Estimated Time</h4>
                  <p className="text-sm text-blue-700">{assignment.estimatedTime}</p>
                </div>
              </div>
            )}

            {activeTab === 'tests' && (
              <div className="space-y-3">
                <h3 className="font-semibold text-secondary-900">Public Test Cases</h3>
                {assignment.testCases.filter(tc => tc.isPublic).map((testCase) => (
                  <div key={testCase.id} className="border rounded-lg p-3">
                    <div className="flex justify-between items-center mb-2">
                      <h4 className="font-medium text-secondary-900">{testCase.name}</h4>
                      <span className="text-xs bg-secondary-100 text-secondary-600 px-2 py-1 rounded">
                        {testCase.points} pts
                      </span>
                    </div>
                    <div className="space-y-2 text-sm">
                      <div>
                        <span className="font-medium text-secondary-700">Input:</span>
                        <pre className="bg-gray-100 p-2 rounded text-xs mt-1">{testCase.input}</pre>
                      </div>
                      <div>
                        <span className="font-medium text-secondary-700">Expected Output:</span>
                        <pre className="bg-gray-100 p-2 rounded text-xs mt-1">{testCase.expectedOutput}</pre>
                      </div>
                    </div>
                  </div>
                ))}
                <div className="bg-yellow-50 p-3 rounded-lg">
                  <p className="text-sm text-yellow-800">
                    <AlertTriangle className="w-4 h-4 inline mr-1" />
                    Additional private test cases will be used for final grading.
                  </p>
                </div>
              </div>
            )}

            {activeTab === 'hints' && (
              <div className="space-y-3">
                <h3 className="font-semibold text-secondary-900">Helpful Hints</h3>
                {assignment.hints.map((hint, index) => (
                  <div key={index} className="flex items-start bg-blue-50 p-3 rounded-lg">
                    <Lightbulb className="w-4 h-4 text-blue-600 mr-2 mt-0.5 flex-shrink-0" />
                    <p className="text-sm text-blue-800">{hint}</p>
                  </div>
                ))}
                <div className="bg-purple-50 p-3 rounded-lg">
                  <div className="flex items-center mb-2">
                    <Brain className="w-4 h-4 text-purple-600 mr-2" />
                    <span className="font-medium text-purple-900">AI Tutor</span>
                  </div>
                  <p className="text-sm text-purple-800">
                    Need more help? Click the "Get AI Help" button in the code editor for personalized assistance!
                  </p>
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Right Panel - Code Editor and Results */}
        <div className="flex-1 flex flex-col">
          {/* Editor Controls */}
          <div className="bg-white border-b border-secondary-200 px-4 py-2">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-4">
                <span className="text-sm text-secondary-600">main.{assignment.language}</span>
                <div className="flex items-center space-x-2">
                  <label className="flex items-center text-sm text-secondary-600">
                    <input
                      type="checkbox"
                      checked={autoSaveEnabled}
                      onChange={(e) => setAutoSaveEnabled(e.target.checked)}
                      className="rounded border-secondary-300 mr-1"
                    />
                    Auto-save
                  </label>
                </div>
              </div>
              <div className="flex items-center space-x-3">
                <div className="flex items-center space-x-2">
                  <label className="text-sm text-secondary-600">Font Size:</label>
                  <select 
                    value={fontSize} 
                    onChange={(e) => setFontSize(Number(e.target.value))}
                    className="text-xs border rounded px-2 py-1"
                  >
                    <option value={12}>12px</option>
                    <option value={14}>14px</option>
                    <option value={16}>16px</option>
                    <option value={18}>18px</option>
                  </select>
                </div>
                <div className="flex items-center space-x-2">
                  <label className="text-sm text-secondary-600">Theme:</label>
                  <select 
                    value={theme} 
                    onChange={(e) => setTheme(e.target.value as 'light' | 'dark')}
                    className="text-xs border rounded px-2 py-1"
                  >
                    <option value="light">Light</option>
                    <option value="dark">Dark</option>
                  </select>
                </div>
                <Button size="sm" variant="outline">
                  <Brain className="w-4 h-4 mr-1" />
                  Get AI Help
                </Button>
                <Button size="sm" variant="outline" onClick={() => setCode(assignment.starterCode)}>
                  <RotateCcw className="w-4 h-4 mr-1" />
                  Reset
                </Button>
              </div>
            </div>
          </div>

          <div className="flex-1 flex flex-col lg:flex-row">
            {/* Code Editor */}
            <div className="flex-1 relative">
              <textarea
                value={code}
                onChange={(e) => setCode(e.target.value)}
                className={`w-full h-full p-4 font-mono resize-none border-none outline-none ${
                  theme === 'dark' 
                    ? 'bg-gray-900 text-green-400' 
                    : 'bg-white text-secondary-900'
                }`}
                style={{ fontSize: `${fontSize}px` }}
                placeholder="Write your code here..."
                spellCheck={false}
              />
              
              {/* Line numbers would go here in a real implementation */}
              <div className="absolute top-4 left-4 pointer-events-none text-xs text-secondary-400 font-mono">
                {code.split('\n').map((_, i) => (
                  <div key={i} style={{ height: `${fontSize * 1.4}px`, lineHeight: `${fontSize * 1.4}px` }}>
                    {i + 1}
                  </div>
                ))}
              </div>
            </div>

            {/* Results Panel */}
            {showResults && (
              <div className="lg:w-96 bg-white border-l border-secondary-200">
                <div className="p-4 border-b border-secondary-200">
                  <h3 className="font-semibold text-secondary-900 flex items-center">
                    <Terminal className="w-5 h-5 mr-2" />
                    Test Results
                  </h3>
                </div>
                
                <div className="p-4 space-y-3">
                  {isRunning ? (
                    <div className="flex items-center justify-center py-8">
                      <div className="text-center">
                        <div className="animate-spin w-8 h-8 border-4 border-primary-600 border-t-transparent rounded-full mx-auto mb-3"></div>
                        <p className="text-sm text-secondary-600">Running tests...</p>
                      </div>
                    </div>
                  ) : (
                    testResults.map((result) => {
                      const testCase = assignment.testCases.find(tc => tc.id === result.testCaseId);
                      return (
                        <div key={result.testCaseId} className={`p-3 rounded-lg border ${
                          result.passed ? 'bg-green-50 border-green-200' : 'bg-red-50 border-red-200'
                        }`}>
                          <div className="flex items-center justify-between mb-2">
                            <h4 className="font-medium text-secondary-900">{testCase?.name}</h4>
                            {result.passed ? (
                              <CheckCircle className="w-5 h-5 text-green-600" />
                            ) : (
                              <XCircle className="w-5 h-5 text-red-600" />
                            )}
                          </div>
                          
                          <div className="text-xs space-y-1">
                            <p className="text-secondary-600">
                              Execution time: {result.executionTime.toFixed(2)}ms
                            </p>
                            
                            {!result.passed && (
                              <>
                                <div>
                                  <span className="font-medium text-red-700">Expected:</span>
                                  <pre className="bg-red-100 p-1 rounded mt-1">{testCase?.expectedOutput}</pre>
                                </div>
                                <div>
                                  <span className="font-medium text-red-700">Got:</span>
                                  <pre className="bg-red-100 p-1 rounded mt-1">{result.actualOutput}</pre>
                                </div>
                                {result.error && (
                                  <div>
                                    <span className="font-medium text-red-700">Error:</span>
                                    <p className="text-red-600">{result.error}</p>
                                  </div>
                                )}
                              </>
                            )}
                          </div>
                        </div>
                      );
                    })
                  )}
                  
                  {!isRunning && testResults.length > 0 && (
                    <div className="pt-3 border-t border-secondary-200">
                      <div className="text-center">
                        <p className="text-sm text-secondary-600">
                          {testResults.filter(r => r.passed).length} of {testResults.length} public tests passed
                        </p>
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={() => setShowResults(false)}
                          className="mt-2"
                        >
                          Hide Results
                        </Button>
                      </div>
                    </div>
                  )}
                </div>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Submit Confirmation Modal */}
      {showSubmitModal && (
        <Modal open={showSubmitModal} onClose={() => setShowSubmitModal(false)}>
          <div className="bg-white rounded-lg p-6 w-full max-w-md mx-4">
            <h2 className="text-xl font-bold text-secondary-900 mb-4">Submit Assignment</h2>
            <div className="space-y-4">
              <p className="text-secondary-600">
                Are you ready to submit your solution? Once submitted, you cannot make changes.
              </p>
              
              {testResults.length > 0 && (
                <div className="bg-blue-50 p-3 rounded-lg">
                  <p className="text-sm text-blue-800">
                    Your solution passed {testResults.filter(r => r.passed).length} of {testResults.length} public tests.
                  </p>
                </div>
              )}
              
              <div className="bg-yellow-50 p-3 rounded-lg">
                <p className="text-sm text-yellow-800">
                  <AlertTriangle className="w-4 h-4 inline mr-1" />
                  Your code will be tested against additional private test cases for final grading.
                </p>
              </div>
            </div>
            
            <div className="flex justify-end space-x-3 mt-6">
              <Button variant="outline" onClick={() => setShowSubmitModal(false)}>
                Cancel
              </Button>
              <Button onClick={confirmSubmit} className="bg-primary-600 hover:bg-primary-700">
                <Upload className="w-4 h-4 mr-2" />
                Submit Assignment
              </Button>
            </div>
          </div>
        </Modal>
      )}

      {/* Help Modal */}
      {showHelpModal && (
        <Modal open={showHelpModal} onClose={() => setShowHelpModal(false)}>
          <div className="bg-white rounded-lg p-6 w-full max-w-2xl mx-4 max-h-[80vh] overflow-y-auto">
            <h2 className="text-xl font-bold text-secondary-900 mb-4">Help & Shortcuts</h2>
            
            <div className="space-y-6">
              <div>
                <h3 className="font-semibold text-secondary-900 mb-2">Editor Features</h3>
                <ul className="space-y-1 text-sm text-secondary-700">
                  <li>• Auto-save automatically saves your work every 2 seconds</li>
                  <li>• Use Ctrl+S (Cmd+S) to manually save your code</li>
                  <li>• Adjust font size and theme for better readability</li>
                  <li>• Click "Reset" to restore the original starter code</li>
                </ul>
              </div>
              
              <div>
                <h3 className="font-semibold text-secondary-900 mb-2">Testing & Submission</h3>
                <ul className="space-y-1 text-sm text-secondary-700">
                  <li>• Run public tests to check your solution before submitting</li>
                  <li>• Private tests will be used for final grading</li>
                  <li>• You can submit multiple times before the deadline</li>
                  <li>• Late submissions may incur point penalties</li>
                </ul>
              </div>
              
              <div>
                <h3 className="font-semibold text-secondary-900 mb-2">Getting Help</h3>
                <ul className="space-y-1 text-sm text-secondary-700">
                  <li>• Check the hints tab for algorithm guidance</li>
                  <li>• Use "Get AI Help" for personalized assistance</li>
                  <li>• Review test cases to understand expected behavior</li>
                  <li>• Contact your instructor if you're stuck</li>
                </ul>
              </div>
            </div>
            
            <div className="flex justify-end mt-6">
              <Button onClick={() => setShowHelpModal(false)}>
                Got it
              </Button>
            </div>
          </div>
        </Modal>
      )}
    </div>
  );
};

export default SubmissionInterface;