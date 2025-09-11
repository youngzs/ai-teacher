import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import {
  Card,
  CardHeader,
  CardTitle,
  CardDescription,
  CardContent,
  Modal,
  Button,
  Input
} from '../../components/ui';
import {
  ClipboardList,
  Plus,
  Search,
  Filter,
  Eye,
  Edit,
  Copy,
  Trash2,
  Calendar,
  Clock,
  Users,
  CheckCircle,
  XCircle,
  AlertCircle,
  Brain,
  FileText,
  Code,
  Play,
  Download,
  Settings,
  MoreVertical
} from 'lucide-react';
import { useAppStore } from '../../store/appStore';

interface Assignment {
  id: string;
  title: string;
  description: string;
  courseId: string;
  courseName: string;
  language: 'c' | 'python' | 'java';
  difficulty: 'easy' | 'medium' | 'hard';
  points: number;
  dueDate: string;
  createdDate: string;
  status: 'draft' | 'published' | 'closed';
  submissionCount: number;
  totalStudents: number;
  avgScore: number;
  aiReviewsEnabled: boolean;
  testCases: number;
  estimatedTime: string;
  tags: string[];
}

interface SubmissionStats {
  submitted: number;
  pending: number;
  graded: number;
  needsReview: number;
}

export const AssignmentManagement: React.FC = () => {
  const { addNotification } = useAppStore();
  const [searchTerm, setSearchTerm] = useState('');
  const [filterStatus, setFilterStatus] = useState<'all' | 'draft' | 'published' | 'closed'>('all');
  const [filterCourse, setFilterCourse] = useState<'all' | string>('all');
  const [selectedAssignments, setSelectedAssignments] = useState<string[]>([]);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [showBulkReviewModal, setShowBulkReviewModal] = useState(false);
  const [viewMode, setViewMode] = useState<'grid' | 'list'>('grid');

  // Mock data
  const [assignments] = useState<Assignment[]>([
    {
      id: '1',
      title: 'Hello World Program',
      description: 'Write a simple program that prints "Hello, World!" to the console',
      courseId: '1',
      courseName: 'C Programming Fundamentals',
      language: 'c',
      difficulty: 'easy',
      points: 10,
      dueDate: '2024-09-15T23:59:59',
      createdDate: '2024-09-01T10:00:00',
      status: 'published',
      submissionCount: 42,
      totalStudents: 45,
      avgScore: 95.2,
      aiReviewsEnabled: true,
      testCases: 3,
      estimatedTime: '30 minutes',
      tags: ['basics', 'introduction']
    },
    {
      id: '2',
      title: 'Binary Search Implementation',
      description: 'Implement binary search algorithm with proper error handling',
      courseId: '1',
      courseName: 'C Programming Fundamentals',
      language: 'c',
      difficulty: 'medium',
      points: 25,
      dueDate: '2024-09-20T23:59:59',
      createdDate: '2024-09-05T14:00:00',
      status: 'published',
      submissionCount: 38,
      totalStudents: 45,
      avgScore: 78.5,
      aiReviewsEnabled: true,
      testCases: 8,
      estimatedTime: '2 hours',
      tags: ['algorithms', 'search', 'arrays']
    },
    {
      id: '3',
      title: 'Data Structure Quiz',
      description: 'Multiple choice quiz on arrays, linked lists, and basic data structures',
      courseId: '2',
      courseName: 'Data Structures',
      language: 'c',
      difficulty: 'medium',
      points: 20,
      dueDate: '2024-09-25T23:59:59',
      createdDate: '2024-09-10T09:00:00',
      status: 'draft',
      submissionCount: 0,
      totalStudents: 30,
      avgScore: 0,
      aiReviewsEnabled: false,
      testCases: 0,
      estimatedTime: '45 minutes',
      tags: ['data-structures', 'theory']
    },
    {
      id: '4',
      title: 'Python Lists and Loops',
      description: 'Practice working with Python lists, loops, and list comprehensions',
      courseId: '3',
      courseName: 'Python Basics',
      language: 'python',
      difficulty: 'easy',
      points: 15,
      dueDate: '2024-09-18T23:59:59',
      createdDate: '2024-09-03T11:00:00',
      status: 'published',
      submissionCount: 28,
      totalStudents: 32,
      avgScore: 88.7,
      aiReviewsEnabled: true,
      testCases: 6,
      estimatedTime: '1.5 hours',
      tags: ['python', 'loops', 'lists']
    }
  ]);

  // Mock courses for filter
  const courses = [
    { id: '1', name: 'C Programming Fundamentals' },
    { id: '2', name: 'Data Structures' },
    { id: '3', name: 'Python Basics' }
  ];

  // Filter assignments
  const filteredAssignments = assignments.filter(assignment => {
    const matchesSearch = assignment.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         assignment.description.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         assignment.tags.some(tag => tag.toLowerCase().includes(searchTerm.toLowerCase()));

    const matchesStatus = filterStatus === 'all' || assignment.status === filterStatus;
    const matchesCourse = filterCourse === 'all' || assignment.courseId === filterCourse;

    return matchesSearch && matchesStatus && matchesCourse;
  });

  const getStatusColor = (status: Assignment['status']) => {
    switch (status) {
      case 'published': return 'text-green-600 bg-green-100';
      case 'draft': return 'text-yellow-600 bg-yellow-100';
      case 'closed': return 'text-red-600 bg-red-100';
      default: return 'text-gray-600 bg-gray-100';
    }
  };

  const getDifficultyColor = (difficulty: Assignment['difficulty']) => {
    switch (difficulty) {
      case 'easy': return 'text-green-600 bg-green-100';
      case 'medium': return 'text-yellow-600 bg-yellow-100';
      case 'hard': return 'text-red-600 bg-red-100';
      default: return 'text-gray-600 bg-gray-100';
    }
  };

  const getLanguageIcon = (language: string) => {
    switch (language) {
      case 'c': return '🔧';
      case 'python': return '🐍';
      case 'java': return '☕';
      default: return '📝';
    }
  };

  const handleSelectAssignment = (assignmentId: string) => {
    setSelectedAssignments(prev =>
      prev.includes(assignmentId)
        ? prev.filter(id => id !== assignmentId)
        : [...prev, assignmentId]
    );
  };

  const handleSelectAll = () => {
    setSelectedAssignments(
      selectedAssignments.length === filteredAssignments.length
        ? []
        : filteredAssignments.map(a => a.id)
    );
  };

  const handleBulkAction = (action: string) => {
    addNotification({
      type: 'success',
      title: 'Bulk Action',
      message: `${action} applied to ${selectedAssignments.length} assignments`,
      duration: 3000
    });
    setSelectedAssignments([]);
  };

  const getSubmissionStats = (assignment: Assignment): SubmissionStats => {
    return {
      submitted: assignment.submissionCount,
      pending: Math.floor(assignment.submissionCount * 0.2),
      graded: Math.floor(assignment.submissionCount * 0.7),
      needsReview: Math.floor(assignment.submissionCount * 0.1)
    };
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-start">
        <div>
          <h1 className="text-3xl font-bold text-secondary-900">Assignment Management</h1>
          <p className="text-secondary-600 mt-1">Create, manage, and track programming assignments</p>
        </div>
        <Button
          onClick={() => setShowCreateModal(true)}
          className="bg-primary-600 hover:bg-primary-700"
        >
          <Plus className="w-4 h-4 mr-2" />
          New Assignment
        </Button>
      </div>

      {/* Overview Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center">
              <ClipboardList className="w-8 h-8 text-blue-600 mr-3" />
              <div>
                <p className="text-2xl font-bold text-secondary-900">{assignments.length}</p>
                <p className="text-sm text-secondary-600">Total Assignments</p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <div className="flex items-center">
              <CheckCircle className="w-8 h-8 text-green-600 mr-3" />
              <div>
                <p className="text-2xl font-bold text-secondary-900">
                  {assignments.filter(a => a.status === 'published').length}
                </p>
                <p className="text-sm text-secondary-600">Published</p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <div className="flex items-center">
              <Clock className="w-8 h-8 text-yellow-600 mr-3" />
              <div>
                <p className="text-2xl font-bold text-secondary-900">
                  {assignments.filter(a => a.status === 'draft').length}
                </p>
                <p className="text-sm text-secondary-600">Drafts</p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <div className="flex items-center">
              <Brain className="w-8 h-8 text-purple-600 mr-3" />
              <div>
                <p className="text-2xl font-bold text-secondary-900">
                  {assignments.reduce((sum, a) => sum + (a.aiReviewsEnabled && a.status === 'published' ? 1 : 0), 0)}
                </p>
                <p className="text-sm text-secondary-600">AI Enabled</p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Controls */}
      <Card>
        <CardContent className="p-6">
          <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between space-y-4 lg:space-y-0">
            {/* Search */}
            <div className="flex items-center space-x-4 flex-1 max-w-md">
              <div className="relative flex-1">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-secondary-400 w-4 h-4" />
                <Input
                  placeholder="Search assignments..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="pl-10"
                />
              </div>
            </div>

            {/* Filters */}
            <div className="flex items-center space-x-4">
              <div className="flex items-center space-x-2">
                <Filter className="w-4 h-4 text-secondary-600" />
                <select
                  value={filterStatus}
                  onChange={(e) => setFilterStatus(e.target.value as any)}
                  className="input text-sm"
                >
                  <option value="all">All Status</option>
                  <option value="draft">Draft</option>
                  <option value="published">Published</option>
                  <option value="closed">Closed</option>
                </select>
              </div>

              <select
                value={filterCourse}
                onChange={(e) => setFilterCourse(e.target.value)}
                className="input text-sm"
              >
                <option value="all">All Courses</option>
                {courses.map(course => (
                  <option key={course.id} value={course.id}>{course.name}</option>
                ))}
              </select>

              <div className="flex border rounded-lg">
                <button
                  onClick={() => setViewMode('grid')}
                  className={`px-3 py-2 text-sm ${viewMode === 'grid'
                    ? 'bg-primary-100 text-primary-600'
                    : 'text-secondary-600 hover:bg-gray-100'}`}
                >
                  Grid
                </button>
                <button
                  onClick={() => setViewMode('list')}
                  className={`px-3 py-2 text-sm ${viewMode === 'list'
                    ? 'bg-primary-100 text-primary-600'
                    : 'text-secondary-600 hover:bg-gray-100'}`}
                >
                  List
                </button>
              </div>
            </div>
          </div>

          {/* Bulk Actions */}
          {selectedAssignments.length > 0 && (
            <div className="mt-4 p-3 bg-primary-50 rounded-lg flex items-center justify-between">
              <span className="text-sm font-medium text-primary-700">
                {selectedAssignments.length} assignment{selectedAssignments.length > 1 ? 's' : ''} selected
              </span>
              <div className="flex space-x-2">
                <Button
                  size="sm"
                  variant="outline"
                  onClick={() => handleBulkAction('Publish')}
                >
                  Publish
                </Button>
                <Button
                  size="sm"
                  variant="outline"
                  onClick={() => setShowBulkReviewModal(true)}
                >
                  <Brain className="w-4 h-4 mr-1" />
                  AI Review
                </Button>
                <Button
                  size="sm"
                  variant="outline"
                  onClick={() => handleBulkAction('Export')}
                >
                  <Download className="w-4 h-4 mr-1" />
                  Export
                </Button>
                <Button
                  size="sm"
                  variant="outline"
                  onClick={() => setSelectedAssignments([])}
                >
                  Clear
                </Button>
              </div>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Assignment List */}
      <Card>
        <CardHeader>
          <CardTitle>Assignments ({filteredAssignments.length})</CardTitle>
          <CardDescription>Manage your programming assignments and track submissions</CardDescription>
        </CardHeader>
        <CardContent>
          {viewMode === 'grid' ? (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {filteredAssignments.map((assignment) => {
                const stats = getSubmissionStats(assignment);
                const isOverdue = new Date(assignment.dueDate) < new Date() && assignment.status === 'published';

                return (
                  <Card key={assignment.id} className="hover:shadow-lg transition-shadow">
                    <CardContent className="p-6">
                      <div className="flex items-start justify-between mb-4">
                        <input
                          type="checkbox"
                          checked={selectedAssignments.includes(assignment.id)}
                          onChange={() => handleSelectAssignment(assignment.id)}
                          className="rounded border-secondary-300 mt-1"
                        />
                        <button className="text-secondary-400 hover:text-secondary-600">
                          <MoreVertical className="w-4 h-4" />
                        </button>
                      </div>

                      <div className="space-y-4">
                        <div>
                          <div className="flex items-center mb-2">
                            <span className="text-lg mr-2">{getLanguageIcon(assignment.language)}</span>
                            <h3 className="font-semibold text-secondary-900 flex-1">{assignment.title}</h3>
                          </div>
                          <p className="text-sm text-secondary-600 line-clamp-2">{assignment.description}</p>
                        </div>

                        <div className="flex items-center justify-between">
                          <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getStatusColor(assignment.status)}`}>
                            {assignment.status}
                          </span>
                          <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getDifficultyColor(assignment.difficulty)}`}>
                            {assignment.difficulty}
                          </span>
                        </div>

                        <div className="grid grid-cols-2 gap-4 text-sm">
                          <div>
                            <p className="text-secondary-600">Due Date</p>
                            <p className={`font-medium ${isOverdue ? 'text-red-600' : ''}`}>
                              {new Date(assignment.dueDate).toLocaleDateString()}
                            </p>
                          </div>
                          <div>
                            <p className="text-secondary-600">Points</p>
                            <p className="font-medium">{assignment.points} pts</p>
                          </div>
                        </div>

                        {assignment.status === 'published' && (
                          <div className="space-y-2">
                            <div className="flex justify-between text-sm">
                              <span className="text-secondary-600">Submissions</span>
                              <span className="font-medium">{assignment.submissionCount}/{assignment.totalStudents}</span>
                            </div>
                            <div className="w-full bg-gray-200 rounded-full h-2">
                              <div
                                className="bg-primary-600 h-2 rounded-full"
                                style={{ width: `${(assignment.submissionCount / assignment.totalStudents) * 100}%` }}
                              ></div>
                            </div>
                            <div className="flex justify-between text-sm">
                              <span className="text-secondary-600">Avg Score</span>
                              <span className="font-medium">{assignment.avgScore.toFixed(1)}%</span>
                            </div>
                          </div>
                        )}

                        <div className="flex flex-wrap gap-1">
                          {assignment.tags.slice(0, 2).map(tag => (
                            <span key={tag} className="inline-flex items-center px-2 py-1 rounded-full text-xs bg-secondary-100 text-secondary-600">
                              {tag}
                            </span>
                          ))}
                          {assignment.tags.length > 2 && (
                            <span className="inline-flex items-center px-2 py-1 rounded-full text-xs bg-secondary-100 text-secondary-600">
                              +{assignment.tags.length - 2}
                            </span>
                          )}
                        </div>

                        <div className="flex items-center justify-between pt-4 border-t">
                          <div className="flex items-center space-x-3">
                            {assignment.aiReviewsEnabled && (
                              <div className="flex items-center text-purple-600">
                                <Brain className="w-4 h-4 mr-1" />
                                <span className="text-xs">AI</span>
                              </div>
                            )}
                            <div className="flex items-center text-secondary-600">
                              <FileText className="w-4 h-4 mr-1" />
                              <span className="text-xs">{assignment.testCases} tests</span>
                            </div>
                          </div>

                          <div className="flex space-x-1">
                            <Link
                              to={`/assignments/${assignment.id}`}
                              className="p-1 text-secondary-400 hover:text-secondary-600"
                            >
                              <Eye className="w-4 h-4" />
                            </Link>
                            <button className="p-1 text-secondary-400 hover:text-secondary-600">
                              <Edit className="w-4 h-4" />
                            </button>
                            <button className="p-1 text-secondary-400 hover:text-secondary-600">
                              <Copy className="w-4 h-4" />
                            </button>
                          </div>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                );
              })}
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b border-secondary-200">
                    <th className="text-left py-3 px-2">
                      <input
                        type="checkbox"
                        checked={selectedAssignments.length === filteredAssignments.length && filteredAssignments.length > 0}
                        onChange={handleSelectAll}
                        className="rounded border-secondary-300"
                      />
                    </th>
                    <th className="text-left py-3 px-4 font-medium text-secondary-700">Assignment</th>
                    <th className="text-left py-3 px-4 font-medium text-secondary-700">Course</th>
                    <th className="text-left py-3 px-4 font-medium text-secondary-700">Status</th>
                    <th className="text-left py-3 px-4 font-medium text-secondary-700">Due Date</th>
                    <th className="text-left py-3 px-4 font-medium text-secondary-700">Submissions</th>
                    <th className="text-left py-3 px-4 font-medium text-secondary-700">Avg Score</th>
                    <th className="text-left py-3 px-4 font-medium text-secondary-700">Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {filteredAssignments.map((assignment) => {
                    const isOverdue = new Date(assignment.dueDate) < new Date() && assignment.status === 'published';

                    return (
                      <tr key={assignment.id} className="border-b border-secondary-100 hover:bg-gray-50">
                        <td className="py-4 px-2">
                          <input
                            type="checkbox"
                            checked={selectedAssignments.includes(assignment.id)}
                            onChange={() => handleSelectAssignment(assignment.id)}
                            className="rounded border-secondary-300"
                          />
                        </td>
                        <td className="py-4 px-4">
                          <div className="flex items-center">
                            <span className="text-lg mr-3">{getLanguageIcon(assignment.language)}</span>
                            <div>
                              <p className="font-medium text-secondary-900">{assignment.title}</p>
                              <div className="flex items-center space-x-2">
                                <span className={`inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium ${getDifficultyColor(assignment.difficulty)}`}>
                                  {assignment.difficulty}
                                </span>
                                <span className="text-xs text-secondary-600">{assignment.points} pts</span>
                                {assignment.aiReviewsEnabled && (
                                  <Brain className="w-3 h-3 text-purple-600" />
                                )}
                              </div>
                            </div>
                          </div>
                        </td>
                        <td className="py-4 px-4">
                          <span className="text-sm text-secondary-700">{assignment.courseName}</span>
                        </td>
                        <td className="py-4 px-4">
                          <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getStatusColor(assignment.status)}`}>
                            {assignment.status}
                          </span>
                        </td>
                        <td className="py-4 px-4">
                          <span className={`text-sm ${isOverdue ? 'text-red-600 font-medium' : 'text-secondary-700'}`}>
                            {new Date(assignment.dueDate).toLocaleDateString()}
                          </span>
                          {isOverdue && (
                            <div className="flex items-center text-red-600 text-xs">
                              <AlertCircle className="w-3 h-3 mr-1" />
                              Overdue
                            </div>
                          )}
                        </td>
                        <td className="py-4 px-4">
                          <div className="flex items-center">
                            <span className="text-sm font-medium mr-2">
                              {assignment.submissionCount}/{assignment.totalStudents}
                            </span>
                            <div className="w-16 bg-gray-200 rounded-full h-1">
                              <div
                                className="bg-primary-600 h-1 rounded-full"
                                style={{ width: `${(assignment.submissionCount / assignment.totalStudents) * 100}%` }}
                              ></div>
                            </div>
                          </div>
                        </td>
                        <td className="py-4 px-4">
                          <span className="text-sm font-medium">
                            {assignment.status === 'published' ? `${assignment.avgScore.toFixed(1)}%` : '-'}
                          </span>
                        </td>
                        <td className="py-4 px-4">
                          <div className="flex items-center space-x-2">
                            <Link
                              to={`/assignments/${assignment.id}`}
                              className="p-1 text-secondary-400 hover:text-secondary-600"
                            >
                              <Eye className="w-4 h-4" />
                            </Link>
                            <button className="p-1 text-secondary-400 hover:text-secondary-600">
                              <Edit className="w-4 h-4" />
                            </button>
                            <button className="p-1 text-secondary-400 hover:text-secondary-600">
                              <Copy className="w-4 h-4" />
                            </button>
                            <button className="p-1 text-secondary-400 hover:text-red-600">
                              <Trash2 className="w-4 h-4" />
                            </button>
                          </div>
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          )}

          {filteredAssignments.length === 0 && (
            <div className="text-center py-12">
              <ClipboardList className="w-12 h-12 text-secondary-300 mx-auto mb-4" />
              <h3 className="text-lg font-medium text-secondary-900 mb-2">No assignments found</h3>
              <p className="text-secondary-600 mb-4">Try adjusting your search or filters</p>
              <Button onClick={() => setShowCreateModal(true)}>
                <Plus className="w-4 h-4 mr-2" />
                Create Assignment
              </Button>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Create Assignment Modal */}
      {showCreateModal && (
        <Modal open={showCreateModal} onClose={() => setShowCreateModal(false)}>
          <div className="bg-white rounded-lg p-6 w-full max-w-2xl mx-4 max-h-[90vh] overflow-y-auto">
            <h2 className="text-xl font-bold text-secondary-900 mb-6">Create New Assignment</h2>

            <div className="space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-secondary-700 mb-1">
                    Assignment Title
                  </label>
                  <Input placeholder="Enter assignment title" />
                </div>
                <div>
                  <label className="block text-sm font-medium text-secondary-700 mb-1">
                    Course
                  </label>
                  <select className="input w-full">
                    <option value="">Select course</option>
                    {courses.map(course => (
                      <option key={course.id} value={course.id}>{course.name}</option>
                    ))}
                  </select>
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-secondary-700 mb-1">
                  Description
                </label>
                <textarea
                  className="input w-full h-24 resize-none"
                  placeholder="Enter assignment description..."
                />
              </div>

              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div>
                  <label className="block text-sm font-medium text-secondary-700 mb-1">
                    Programming Language
                  </label>
                  <select className="input w-full">
                    <option value="c">C</option>
                    <option value="python">Python</option>
                    <option value="java">Java</option>
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-secondary-700 mb-1">
                    Difficulty
                  </label>
                  <select className="input w-full">
                    <option value="easy">Easy</option>
                    <option value="medium">Medium</option>
                    <option value="hard">Hard</option>
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-secondary-700 mb-1">
                    Points
                  </label>
                  <Input type="number" placeholder="0" min="0" />
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-secondary-700 mb-1">
                    Due Date
                  </label>
                  <Input type="datetime-local" />
                </div>
                <div>
                  <label className="block text-sm font-medium text-secondary-700 mb-1">
                    Estimated Time
                  </label>
                  <Input placeholder="e.g., 2 hours" />
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-secondary-700 mb-1">
                  Tags (comma separated)
                </label>
                <Input placeholder="e.g., loops, arrays, beginner" />
              </div>

              <div className="space-y-3">
                <label className="flex items-center">
                  <input type="checkbox" className="rounded border-secondary-300 mr-2" />
                  <span className="text-sm text-secondary-700">Enable AI-powered code review</span>
                </label>
                <label className="flex items-center">
                  <input type="checkbox" className="rounded border-secondary-300 mr-2" />
                  <span className="text-sm text-secondary-700">Allow multiple submissions</span>
                </label>
                <label className="flex items-center">
                  <input type="checkbox" className="rounded border-secondary-300 mr-2" />
                  <span className="text-sm text-secondary-700">Auto-grade with test cases</span>
                </label>
              </div>
            </div>

            <div className="flex justify-end space-x-3 mt-8">
              <Button variant="outline" onClick={() => setShowCreateModal(false)}>
                Cancel
              </Button>
              <Button variant="outline">
                Save Draft
              </Button>
              <Button onClick={() => {
                addNotification({
                  type: 'success',
                  title: 'Assignment Created',
                  message: 'New assignment has been created and published',
                  duration: 3000
                });
                setShowCreateModal(false);
              }}>
                Create & Publish
              </Button>
            </div>
          </div>
        </Modal>
      )}

      {/* Bulk AI Review Modal */}
      {showBulkReviewModal && (
        <Modal open={showBulkReviewModal} onClose={() => setShowBulkReviewModal(false)}>
          <div className="bg-white rounded-lg p-6 w-full max-w-md mx-4">
            <h2 className="text-xl font-bold text-secondary-900 mb-4">Enable AI Review</h2>
            <p className="text-secondary-600 mb-6">
              Enable AI-powered code review for {selectedAssignments.length} selected assignments?
            </p>
            <div className="flex justify-end space-x-3">
              <Button variant="outline" onClick={() => setShowBulkReviewModal(false)}>
                Cancel
              </Button>
              <Button onClick={() => {
                handleBulkAction('Enable AI Review');
                setShowBulkReviewModal(false);
              }}>
                Enable AI Review
              </Button>
            </div>
          </div>
        </Modal>
      )}
    </div>
  );
};

export default AssignmentManagement;
