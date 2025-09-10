import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
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
  Brain,
  CheckCircle,
  XCircle,
  AlertTriangle,
  Lightbulb,
  Code,
  TrendingUp,
  TrendingDown,
  Eye,
  ThumbsUp,
  ThumbsDown,
  MessageSquare,
  BookOpen,
  Target,
  Zap,
  Award,
  ArrowRight,
  ChevronDown,
  ChevronRight,
  Copy,
  ExternalLink,
  RefreshCw
} from 'lucide-react';
import { useAppStore } from '../../store/app';

interface FeedbackItem {
  id: string;
  type: 'success' | 'warning' | 'error' | 'improvement' | 'suggestion';
  category: 'syntax' | 'logic' | 'performance' | 'style' | 'best_practices' | 'debugging';
  title: string;
  message: string;
  lineNumber?: number;
  codeSnippet?: string;
  suggestion?: string;
  severity: 'low' | 'medium' | 'high';
  isExpanded?: boolean;
  relatedConcepts?: string[];
  learningResources?: string[];
}

interface AIFeedback {
  id: string;
  submissionId: string;
  assignmentTitle: string;
  course: string;
  submittedAt: string;
  score: number;
  overallGrade: 'A' | 'B' | 'C' | 'D' | 'F';
  overallComment: string;
  strengths: string[];
  improvements: string[];
  feedbackItems: FeedbackItem[];
  skillsAssessed: {
    category: string;
    score: number;
    feedback: string;
  }[];
  nextSteps: string[];
  isHelpful?: boolean;
  studentNotes?: string;
}

export const FeedbackViewer: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const { addNotification } = useAppStore();
  
  const [feedback, setFeedback] = useState<AIFeedback | null>(null);
  const [activeTab, setActiveTab] = useState<'overview' | 'details' | 'skills' | 'resources'>('overview');
  const [showNoteModal, setShowNoteModal] = useState(false);
  const [studentNotes, setStudentNotes] = useState('');
  const [feedbackRating, setFeedbackRating] = useState<'helpful' | 'not_helpful' | null>(null);

  // Mock feedback data
  useEffect(() => {
    const mockFeedback: AIFeedback = {
      id: id || '1',
      submissionId: 'sub_001',
      assignmentTitle: 'Binary Search Implementation',
      course: 'Data Structures and Algorithms',
      submittedAt: '2024-09-10T14:30:00Z',
      score: 78,
      overallGrade: 'B',
      overallComment: 'Good implementation of binary search with correct logic. Your solution demonstrates understanding of the algorithm\'s core concepts. There are opportunities for improvement in edge case handling and code organization.',
      strengths: [
        'Correct implementation of binary search algorithm',
        'Proper use of while loop and boundary conditions',
        'Good understanding of divide and conquer approach',
        'Clean variable naming conventions'
      ],
      improvements: [
        'Add input validation for null arrays',
        'Handle integer overflow in mid calculation',
        'Add more comprehensive comments',
        'Consider edge case when array is empty'
      ],
      feedbackItems: [
        {
          id: '1',
          type: 'success',
          category: 'logic',
          title: 'Correct Binary Search Logic',
          message: 'Excellent implementation of the binary search algorithm! You correctly update the left and right pointers based on the comparison with the middle element.',
          lineNumber: 8,
          codeSnippet: `if (arr[mid] == target) {
    return mid;
} else if (arr[mid] < target) {
    left = mid + 1;
} else {
    right = mid - 1;
}`,
          severity: 'low',
          isExpanded: true,
          relatedConcepts: ['Binary Search', 'Divide and Conquer'],
          learningResources: ['Binary Search Tutorial', 'Algorithm Complexity Guide']
        },
        {
          id: '2',
          type: 'warning',
          category: 'best_practices',
          title: 'Integer Overflow Risk',
          message: 'The mid calculation `(left + right) / 2` can cause integer overflow for large values. Consider using `left + (right - left) / 2` instead.',
          lineNumber: 5,
          codeSnippet: `int mid = (left + right) / 2; // Potential overflow`,
          suggestion: `int mid = left + (right - left) / 2; // Overflow-safe`,
          severity: 'medium',
          isExpanded: false,
          relatedConcepts: ['Integer Overflow', 'Safe Arithmetic'],
          learningResources: ['Integer Overflow Prevention', 'Safe Programming Practices']
        },
        {
          id: '3',
          type: 'improvement',
          category: 'style',
          title: 'Add Input Validation',
          message: 'Consider adding input validation to handle null arrays and negative sizes gracefully.',
          lineNumber: 1,
          suggestion: `if (arr == NULL || size <= 0) {
    return -1;
}`,
          severity: 'low',
          isExpanded: false,
          relatedConcepts: ['Input Validation', 'Error Handling'],
          learningResources: ['Defensive Programming', 'Input Validation Best Practices']
        },
        {
          id: '4',
          type: 'suggestion',
          category: 'performance',
          title: 'Algorithm Efficiency',
          message: 'Your implementation achieves O(log n) time complexity, which is optimal for binary search. Well done!',
          severity: 'low',
          isExpanded: false,
          relatedConcepts: ['Time Complexity', 'Big O Notation'],
          learningResources: ['Algorithm Analysis', 'Time Complexity Guide']
        }
      ],
      skillsAssessed: [
        {
          category: 'Algorithm Implementation',
          score: 85,
          feedback: 'Strong understanding of binary search algorithm with correct implementation.'
        },
        {
          category: 'Code Structure',
          score: 75,
          feedback: 'Good code organization. Could benefit from more detailed comments.'
        },
        {
          category: 'Edge Case Handling',
          score: 60,
          feedback: 'Basic edge cases handled. Consider additional input validation scenarios.'
        },
        {
          category: 'Best Practices',
          score: 70,
          feedback: 'Follows most coding conventions. Some improvements needed for robustness.'
        }
      ],
      nextSteps: [
        'Practice implementing input validation in your algorithms',
        'Study integer overflow prevention techniques',
        'Review edge case testing strategies',
        'Explore more advanced binary search variations'
      ],
      studentNotes: ''
    };
    
    setFeedback(mockFeedback);
    setStudentNotes(mockFeedback.studentNotes || '');
  }, [id]);

  const toggleFeedbackItem = (itemId: string) => {
    if (feedback) {
      setFeedback({
        ...feedback,
        feedbackItems: feedback.feedbackItems.map(item => 
          item.id === itemId ? { ...item, isExpanded: !item.isExpanded } : item
        )
      });
    }
  };

  const handleFeedbackRating = (rating: 'helpful' | 'not_helpful') => {
    setFeedbackRating(rating);
    addNotification({
      type: 'success',
      title: 'Feedback Recorded',
      message: `Thank you for rating this feedback as ${rating.replace('_', ' ')}!`,
      duration: 3000
    });
  };

  const saveFeedbackNotes = () => {
    if (feedback) {
      setFeedback({ ...feedback, studentNotes });
      addNotification({
        type: 'success',
        title: 'Notes Saved',
        message: 'Your personal notes have been saved.',
        duration: 3000
      });
    }
    setShowNoteModal(false);
  };

  const getFeedbackIcon = (type: FeedbackItem['type']) => {
    switch (type) {
      case 'success': return <CheckCircle className="w-5 h-5 text-green-600" />;
      case 'warning': return <AlertTriangle className="w-5 h-5 text-yellow-600" />;
      case 'error': return <XCircle className="w-5 h-5 text-red-600" />;
      case 'improvement': return <TrendingUp className="w-5 h-5 text-blue-600" />;
      case 'suggestion': return <Lightbulb className="w-5 h-5 text-purple-600" />;
      default: return <Brain className="w-5 h-5 text-secondary-600" />;
    }
  };

  const getFeedbackColor = (type: FeedbackItem['type']) => {
    switch (type) {
      case 'success': return 'border-green-200 bg-green-50';
      case 'warning': return 'border-yellow-200 bg-yellow-50';
      case 'error': return 'border-red-200 bg-red-50';
      case 'improvement': return 'border-blue-200 bg-blue-50';
      case 'suggestion': return 'border-purple-200 bg-purple-50';
      default: return 'border-secondary-200 bg-secondary-50';
    }
  };

  const getSeverityColor = (severity: FeedbackItem['severity']) => {
    switch (severity) {
      case 'high': return 'text-red-600 bg-red-100';
      case 'medium': return 'text-yellow-600 bg-yellow-100';
      case 'low': return 'text-blue-600 bg-blue-100';
      default: return 'text-gray-600 bg-gray-100';
    }
  };

  const getGradeColor = (grade: string) => {
    switch (grade) {
      case 'A': return 'text-green-600 bg-green-100';
      case 'B': return 'text-blue-600 bg-blue-100';
      case 'C': return 'text-yellow-600 bg-yellow-100';
      case 'D': return 'text-orange-600 bg-orange-100';
      case 'F': return 'text-red-600 bg-red-100';
      default: return 'text-gray-600 bg-gray-100';
    }
  };

  if (!feedback) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="animate-spin w-8 h-8 border-4 border-primary-600 border-t-transparent rounded-full mx-auto mb-4"></div>
          <p className="text-secondary-600">Loading AI feedback...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-7xl mx-auto space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <div className="flex items-center space-x-3">
              <Brain className="w-8 h-8 text-primary-600" />
              <div>
                <h1 className="text-2xl font-bold text-secondary-900">AI Feedback Analysis</h1>
                <p className="text-secondary-600">{feedback.assignmentTitle} • {feedback.course}</p>
              </div>
            </div>
          </div>
          <div className="flex items-center space-x-3">
            <Button variant="outline" onClick={() => setShowNoteModal(true)}>
              <MessageSquare className="w-4 h-4 mr-2" />
              Add Notes
            </Button>
            <Link 
              to={`/submissions/${feedback.submissionId}`}
              className="inline-flex items-center px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors"
            >
              <Eye className="w-4 h-4 mr-2" />
              View Submission
            </Link>
          </div>
        </div>

        {/* Overall Score Card */}
        <Card className="bg-gradient-to-r from-primary-50 to-primary-100">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-6">
                <div className="text-center">
                  <div className="text-4xl font-bold text-primary-900">{feedback.score}</div>
                  <div className="text-sm text-primary-700">Score</div>
                </div>
                <div className="text-center">
                  <div className={`text-2xl font-bold px-4 py-2 rounded-full ${getGradeColor(feedback.overallGrade)}`}>
                    {feedback.overallGrade}
                  </div>
                  <div className="text-sm text-primary-700">Grade</div>
                </div>
                <div className="flex-1">
                  <p className="text-primary-900 font-medium mb-2">Overall Assessment</p>
                  <p className="text-primary-800 text-sm leading-relaxed">{feedback.overallComment}</p>
                </div>
              </div>
              <div className="text-right">
                <p className="text-sm text-primary-700">Submitted</p>
                <p className="text-primary-900 font-medium">
                  {new Date(feedback.submittedAt).toLocaleDateString()}
                </p>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Tab Navigation */}
        <div className="flex space-x-1 bg-white rounded-lg p-1 border">
          <button
            onClick={() => setActiveTab('overview')}
            className={`flex-1 px-4 py-2 text-sm font-medium rounded-md transition-colors ${
              activeTab === 'overview'
                ? 'bg-primary-100 text-primary-700'
                : 'text-secondary-600 hover:text-secondary-900'
            }`}
          >
            Overview
          </button>
          <button
            onClick={() => setActiveTab('details')}
            className={`flex-1 px-4 py-2 text-sm font-medium rounded-md transition-colors ${
              activeTab === 'details'
                ? 'bg-primary-100 text-primary-700'
                : 'text-secondary-600 hover:text-secondary-900'
            }`}
          >
            Detailed Feedback ({feedback.feedbackItems.length})
          </button>
          <button
            onClick={() => setActiveTab('skills')}
            className={`flex-1 px-4 py-2 text-sm font-medium rounded-md transition-colors ${
              activeTab === 'skills'
                ? 'bg-primary-100 text-primary-700'
                : 'text-secondary-600 hover:text-secondary-900'
            }`}
          >
            Skills Assessment
          </button>
          <button
            onClick={() => setActiveTab('resources')}
            className={`flex-1 px-4 py-2 text-sm font-medium rounded-md transition-colors ${
              activeTab === 'resources'
                ? 'bg-primary-100 text-primary-700'
                : 'text-secondary-600 hover:text-secondary-900'
            }`}
          >
            Learning Path
          </button>
        </div>

        {/* Tab Content */}
        {activeTab === 'overview' && (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Strengths */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center text-green-700">
                  <CheckCircle className="w-5 h-5 mr-2" />
                  What You Did Well
                </CardTitle>
              </CardHeader>
              <CardContent>
                <ul className="space-y-3">
                  {feedback.strengths.map((strength, index) => (
                    <li key={index} className="flex items-start">
                      <div className="w-2 h-2 bg-green-500 rounded-full mt-2 mr-3 flex-shrink-0"></div>
                      <span className="text-secondary-700">{strength}</span>
                    </li>
                  ))}
                </ul>
              </CardContent>
            </Card>

            {/* Improvements */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center text-blue-700">
                  <TrendingUp className="w-5 h-5 mr-2" />
                  Areas for Improvement
                </CardTitle>
              </CardHeader>
              <CardContent>
                <ul className="space-y-3">
                  {feedback.improvements.map((improvement, index) => (
                    <li key={index} className="flex items-start">
                      <div className="w-2 h-2 bg-blue-500 rounded-full mt-2 mr-3 flex-shrink-0"></div>
                      <span className="text-secondary-700">{improvement}</span>
                    </li>
                  ))}
                </ul>
              </CardContent>
            </Card>

            {/* Feedback Summary */}
            <Card className="lg:col-span-2">
              <CardHeader>
                <CardTitle className="flex items-center">
                  <Brain className="w-5 h-5 mr-2 text-primary-600" />
                  Feedback Summary
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                  {['success', 'warning', 'improvement', 'suggestion'].map(type => {
                    const count = feedback.feedbackItems.filter(item => item.type === type).length;
                    const colors = {
                      success: 'text-green-600 bg-green-100',
                      warning: 'text-yellow-600 bg-yellow-100',
                      improvement: 'text-blue-600 bg-blue-100',
                      suggestion: 'text-purple-600 bg-purple-100'
                    };
                    
                    return (
                      <div key={type} className="text-center">
                        <div className={`inline-flex items-center justify-center w-12 h-12 rounded-full ${colors[type as keyof typeof colors]} mb-2`}>
                          <span className="text-lg font-bold">{count}</span>
                        </div>
                        <p className="text-sm font-medium text-secondary-900 capitalize">{type}s</p>
                      </div>
                    );
                  })}
                </div>
              </CardContent>
            </Card>
          </div>
        )}

        {activeTab === 'details' && (
          <div className="space-y-4">
            {feedback.feedbackItems.map((item) => (
              <Card key={item.id} className={`border-l-4 ${getFeedbackColor(item.type)}`}>
                <CardContent className="p-4">
                  <div className="flex items-start justify-between">
                    <div className="flex items-start space-x-3 flex-1">
                      {getFeedbackIcon(item.type)}
                      <div className="flex-1">
                        <div className="flex items-center space-x-3 mb-2">
                          <h3 className="font-semibold text-secondary-900">{item.title}</h3>
                          <span className={`px-2 py-1 rounded-full text-xs font-medium ${getSeverityColor(item.severity)}`}>
                            {item.severity}
                          </span>
                          <span className="px-2 py-1 bg-secondary-100 text-secondary-600 rounded-full text-xs">
                            {item.category.replace('_', ' ')}
                          </span>
                        </div>
                        
                        <p className="text-secondary-700 mb-3">{item.message}</p>

                        {item.isExpanded && (
                          <div className="space-y-4">
                            {item.codeSnippet && (
                              <div>
                                <h4 className="font-medium text-secondary-900 mb-2 flex items-center">
                                  <Code className="w-4 h-4 mr-1" />
                                  Code Reference {item.lineNumber && `(Line ${item.lineNumber})`}
                                </h4>
                                <div className="relative">
                                  <pre className="bg-gray-900 text-green-400 p-4 rounded-lg text-sm overflow-x-auto">
                                    <code>{item.codeSnippet}</code>
                                  </pre>
                                  <Button
                                    size="sm"
                                    variant="outline"
                                    className="absolute top-2 right-2 text-xs"
                                    onClick={() => navigator.clipboard.writeText(item.codeSnippet || '')}
                                  >
                                    <Copy className="w-3 h-3 mr-1" />
                                    Copy
                                  </Button>
                                </div>
                              </div>
                            )}

                            {item.suggestion && (
                              <div>
                                <h4 className="font-medium text-secondary-900 mb-2 flex items-center">
                                  <Lightbulb className="w-4 h-4 mr-1" />
                                  Suggested Improvement
                                </h4>
                                <pre className="bg-blue-50 border border-blue-200 text-blue-900 p-4 rounded-lg text-sm overflow-x-auto">
                                  <code>{item.suggestion}</code>
                                </pre>
                              </div>
                            )}

                            {item.relatedConcepts && item.relatedConcepts.length > 0 && (
                              <div>
                                <h4 className="font-medium text-secondary-900 mb-2">Related Concepts</h4>
                                <div className="flex flex-wrap gap-2">
                                  {item.relatedConcepts.map((concept, index) => (
                                    <span key={index} className="px-3 py-1 bg-primary-100 text-primary-700 rounded-full text-sm">
                                      {concept}
                                    </span>
                                  ))}
                                </div>
                              </div>
                            )}

                            {item.learningResources && item.learningResources.length > 0 && (
                              <div>
                                <h4 className="font-medium text-secondary-900 mb-2">Learning Resources</h4>
                                <ul className="space-y-1">
                                  {item.learningResources.map((resource, index) => (
                                    <li key={index}>
                                      <button className="text-primary-600 hover:text-primary-700 text-sm flex items-center">
                                        <BookOpen className="w-3 h-3 mr-1" />
                                        {resource}
                                        <ExternalLink className="w-3 h-3 ml-1" />
                                      </button>
                                    </li>
                                  ))}
                                </ul>
                              </div>
                            )}
                          </div>
                        )}
                      </div>
                    </div>
                    
                    <Button
                      size="sm"
                      variant="ghost"
                      onClick={() => toggleFeedbackItem(item.id)}
                      className="flex-shrink-0 ml-2"
                    >
                      {item.isExpanded ? (
                        <ChevronDown className="w-4 h-4" />
                      ) : (
                        <ChevronRight className="w-4 h-4" />
                      )}
                    </Button>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        )}

        {activeTab === 'skills' && (
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center">
                <Target className="w-5 h-5 mr-2 text-primary-600" />
                Skills Assessment
              </CardTitle>
              <CardDescription>
                Detailed breakdown of your programming skills demonstrated in this assignment
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-6">
                {feedback.skillsAssessed.map((skill, index) => (
                  <div key={index} className="border-b border-secondary-200 last:border-b-0 pb-6 last:pb-0">
                    <div className="flex items-center justify-between mb-3">
                      <h3 className="font-semibold text-secondary-900">{skill.category}</h3>
                      <div className="flex items-center space-x-2">
                        <div className="text-right">
                          <span className="text-2xl font-bold text-primary-600">{skill.score}</span>
                          <span className="text-secondary-600">/100</span>
                        </div>
                        <div className={`w-8 h-8 rounded-full flex items-center justify-center ${
                          skill.score >= 80 ? 'bg-green-100' :
                          skill.score >= 60 ? 'bg-yellow-100' : 'bg-red-100'
                        }`}>
                          {skill.score >= 80 ? (
                            <CheckCircle className="w-4 h-4 text-green-600" />
                          ) : skill.score >= 60 ? (
                            <AlertTriangle className="w-4 h-4 text-yellow-600" />
                          ) : (
                            <XCircle className="w-4 h-4 text-red-600" />
                          )}
                        </div>
                      </div>
                    </div>
                    
                    <div className="flex items-center mb-2">
                      <div className="flex-1 bg-gray-200 rounded-full h-3">
                        <div 
                          className={`h-3 rounded-full ${
                            skill.score >= 80 ? 'bg-green-500' :
                            skill.score >= 60 ? 'bg-yellow-500' : 'bg-red-500'
                          }`}
                          style={{ width: `${skill.score}%` }}
                        ></div>
                      </div>
                    </div>
                    
                    <p className="text-secondary-700 text-sm">{skill.feedback}</p>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        )}

        {activeTab === 'resources' && (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center">
                  <Zap className="w-5 h-5 mr-2 text-primary-600" />
                  Next Steps
                </CardTitle>
                <CardDescription>
                  Recommended actions to improve your programming skills
                </CardDescription>
              </CardHeader>
              <CardContent>
                <ul className="space-y-4">
                  {feedback.nextSteps.map((step, index) => (
                    <li key={index} className="flex items-start">
                      <div className="w-6 h-6 bg-primary-100 text-primary-600 rounded-full flex items-center justify-center text-sm font-medium mr-3 mt-0.5 flex-shrink-0">
                        {index + 1}
                      </div>
                      <div className="flex-1">
                        <p className="text-secondary-700">{step}</p>
                        <Button size="sm" variant="outline" className="mt-2">
                          <ArrowRight className="w-3 h-3 mr-1" />
                          Learn More
                        </Button>
                      </div>
                    </li>
                  ))}
                </ul>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="flex items-center">
                  <Award className="w-5 h-5 mr-2 text-primary-600" />
                  Learning Achievements
                </CardTitle>
                <CardDescription>
                  Skills and concepts you've mastered
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div className="flex items-center p-3 bg-green-50 border border-green-200 rounded-lg">
                    <CheckCircle className="w-6 h-6 text-green-600 mr-3" />
                    <div>
                      <p className="font-medium text-green-900">Algorithm Implementation</p>
                      <p className="text-sm text-green-700">Successfully implemented binary search</p>
                    </div>
                  </div>
                  
                  <div className="flex items-center p-3 bg-blue-50 border border-blue-200 rounded-lg">
                    <CheckCircle className="w-6 h-6 text-blue-600 mr-3" />
                    <div>
                      <p className="font-medium text-blue-900">Loop Control</p>
                      <p className="text-sm text-blue-700">Proper use of while loops and conditions</p>
                    </div>
                  </div>
                  
                  <div className="flex items-center p-3 bg-purple-50 border border-purple-200 rounded-lg">
                    <CheckCircle className="w-6 h-6 text-purple-600 mr-3" />
                    <div>
                      <p className="font-medium text-purple-900">Variable Management</p>
                      <p className="text-sm text-purple-700">Clean variable naming and scope handling</p>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        )}

        {/* Feedback Rating */}
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="font-medium text-secondary-900">Was this feedback helpful?</p>
                <p className="text-sm text-secondary-600">Your feedback helps us improve AI analysis</p>
              </div>
              <div className="flex items-center space-x-3">
                <Button
                  size="sm"
                  variant={feedbackRating === 'helpful' ? 'default' : 'outline'}
                  onClick={() => handleFeedbackRating('helpful')}
                  className={feedbackRating === 'helpful' ? 'bg-green-600 hover:bg-green-700' : ''}
                >
                  <ThumbsUp className="w-4 h-4 mr-2" />
                  Helpful
                </Button>
                <Button
                  size="sm"
                  variant={feedbackRating === 'not_helpful' ? 'default' : 'outline'}
                  onClick={() => handleFeedbackRating('not_helpful')}
                  className={feedbackRating === 'not_helpful' ? 'bg-red-600 hover:bg-red-700' : ''}
                >
                  <ThumbsDown className="w-4 h-4 mr-2" />
                  Not Helpful
                </Button>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Notes Modal */}
      {showNoteModal && (
        <Modal open={showNoteModal} onClose={() => setShowNoteModal(false)}>
          <div className="bg-white rounded-lg p-6 w-full max-w-md mx-4">
            <h2 className="text-xl font-bold text-secondary-900 mb-4">Add Personal Notes</h2>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-secondary-700 mb-2">
                  Your Notes
                </label>
                <textarea
                  value={studentNotes}
                  onChange={(e) => setStudentNotes(e.target.value)}
                  className="w-full h-32 p-3 border border-secondary-300 rounded-lg resize-none"
                  placeholder="Add your thoughts, questions, or reminders about this feedback..."
                />
              </div>
            </div>
            
            <div className="flex justify-end space-x-3 mt-6">
              <Button variant="outline" onClick={() => setShowNoteModal(false)}>
                Cancel
              </Button>
              <Button onClick={saveFeedbackNotes}>
                Save Notes
              </Button>
            </div>
          </div>
        </Modal>
      )}
    </div>
  );
};

export default FeedbackViewer;