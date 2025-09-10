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
  Users,
  UserPlus,
  Search,
  Filter,
  MoreHorizontal,
  Eye,
  Edit,
  Trash2,
  Download,
  Mail,
  CheckCircle,
  XCircle,
  Clock,
  TrendingUp,
  TrendingDown,
  Award,
  AlertTriangle
} from 'lucide-react';
import { useAppStore } from '../../store/app';

interface Student {
  id: string;
  studentId: string;
  name: string;
  email: string;
  avatar?: string;
  joinDate: string;
  lastActivity: string;
  progress: number;
  submissionsCount: number;
  averageScore: number;
  status: 'active' | 'inactive' | 'struggling';
  courseCompletion: number;
  aiInteractionCount: number;
  skillLevel: 'beginner' | 'intermediate' | 'advanced';
}

interface CourseInfo {
  id: string;
  name: string;
  totalStudents: number;
  activeStudents: number;
  averageProgress: number;
}

export const ClassManagement: React.FC = () => {
  const { addNotification } = useAppStore();
  const [selectedStudents, setSelectedStudents] = useState<string[]>([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [filterStatus, setFilterStatus] = useState<'all' | 'active' | 'inactive' | 'struggling'>('all');
  const [filterSkillLevel, setFilterSkillLevel] = useState<'all' | 'beginner' | 'intermediate' | 'advanced'>('all');
  const [showStudentModal, setShowStudentModal] = useState(false);
  const [selectedStudent, setSelectedStudent] = useState<Student | null>(null);
  const [showAddStudentModal, setShowAddStudentModal] = useState(false);
  const [viewMode, setViewMode] = useState<'grid' | 'table'>('table');

  // Mock course data
  const courseInfo: CourseInfo = {
    id: '1',
    name: 'C Programming Fundamentals',
    totalStudents: 45,
    activeStudents: 42,
    averageProgress: 72.5
  };

  // Mock student data
  const [students] = useState<Student[]>([
    {
      id: '1',
      studentId: 'CS2024001',
      name: 'Alice Johnson',
      email: 'alice.johnson@university.edu',
      joinDate: '2024-09-01',
      lastActivity: '2 hours ago',
      progress: 85,
      submissionsCount: 12,
      averageScore: 88.5,
      status: 'active',
      courseCompletion: 75,
      aiInteractionCount: 45,
      skillLevel: 'intermediate'
    },
    {
      id: '2',
      studentId: 'CS2024002',
      name: 'Bob Smith',
      email: 'bob.smith@university.edu',
      joinDate: '2024-09-01',
      lastActivity: '1 day ago',
      progress: 42,
      submissionsCount: 6,
      averageScore: 65.2,
      status: 'struggling',
      courseCompletion: 35,
      aiInteractionCount: 23,
      skillLevel: 'beginner'
    },
    {
      id: '3',
      studentId: 'CS2024003',
      name: 'Carol Davis',
      email: 'carol.davis@university.edu',
      joinDate: '2024-09-01',
      lastActivity: '30 minutes ago',
      progress: 95,
      submissionsCount: 15,
      averageScore: 94.7,
      status: 'active',
      courseCompletion: 90,
      aiInteractionCount: 67,
      skillLevel: 'advanced'
    },
    {
      id: '4',
      studentId: 'CS2024004',
      name: 'David Wilson',
      email: 'david.wilson@university.edu',
      joinDate: '2024-09-01',
      lastActivity: '5 days ago',
      progress: 28,
      submissionsCount: 3,
      averageScore: 45.8,
      status: 'inactive',
      courseCompletion: 15,
      aiInteractionCount: 12,
      skillLevel: 'beginner'
    },
    // Add more students...
  ]);

  // Filter students based on search and filters
  const filteredStudents = students.filter(student => {
    const matchesSearch = student.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         student.email.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         student.studentId.toLowerCase().includes(searchTerm.toLowerCase());
    
    const matchesStatus = filterStatus === 'all' || student.status === filterStatus;
    const matchesSkillLevel = filterSkillLevel === 'all' || student.skillLevel === filterSkillLevel;
    
    return matchesSearch && matchesStatus && matchesSkillLevel;
  });

  const handleSelectStudent = (studentId: string) => {
    setSelectedStudents(prev => 
      prev.includes(studentId) 
        ? prev.filter(id => id !== studentId)
        : [...prev, studentId]
    );
  };

  const handleSelectAll = () => {
    setSelectedStudents(
      selectedStudents.length === filteredStudents.length 
        ? [] 
        : filteredStudents.map(s => s.id)
    );
  };

  const handleBulkAction = (action: string) => {
    addNotification({
      type: 'success',
      title: 'Bulk Action',
      message: `${action} applied to ${selectedStudents.length} students`,
      duration: 3000
    });
    setSelectedStudents([]);
  };

  const getStatusColor = (status: Student['status']) => {
    switch (status) {
      case 'active': return 'text-green-600 bg-green-100';
      case 'inactive': return 'text-red-600 bg-red-100';
      case 'struggling': return 'text-yellow-600 bg-yellow-100';
      default: return 'text-gray-600 bg-gray-100';
    }
  };

  const getSkillLevelColor = (level: Student['skillLevel']) => {
    switch (level) {
      case 'beginner': return 'text-blue-600 bg-blue-100';
      case 'intermediate': return 'text-purple-600 bg-purple-100';
      case 'advanced': return 'text-green-600 bg-green-100';
      default: return 'text-gray-600 bg-gray-100';
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-start">
        <div>
          <h1 className="text-3xl font-bold text-secondary-900">Class Management</h1>
          <p className="text-secondary-600 mt-1">
            {courseInfo.name} • {courseInfo.totalStudents} students
          </p>
        </div>
        <Button 
          onClick={() => setShowAddStudentModal(true)}
          className="bg-primary-600 hover:bg-primary-700"
        >
          <UserPlus className="w-4 h-4 mr-2" />
          Add Student
        </Button>
      </div>

      {/* Course Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center">
              <Users className="w-8 h-8 text-blue-600 mr-3" />
              <div>
                <p className="text-2xl font-bold text-secondary-900">{courseInfo.totalStudents}</p>
                <p className="text-sm text-secondary-600">Total Students</p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <div className="flex items-center">
              <CheckCircle className="w-8 h-8 text-green-600 mr-3" />
              <div>
                <p className="text-2xl font-bold text-secondary-900">{courseInfo.activeStudents}</p>
                <p className="text-sm text-secondary-600">Active Students</p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <div className="flex items-center">
              <TrendingUp className="w-8 h-8 text-purple-600 mr-3" />
              <div>
                <p className="text-2xl font-bold text-secondary-900">{courseInfo.averageProgress}%</p>
                <p className="text-sm text-secondary-600">Avg Progress</p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <div className="flex items-center">
              <AlertTriangle className="w-8 h-8 text-yellow-600 mr-3" />
              <div>
                <p className="text-2xl font-bold text-secondary-900">
                  {students.filter(s => s.status === 'struggling').length}
                </p>
                <p className="text-sm text-secondary-600">Need Help</p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Controls and Filters */}
      <Card>
        <CardContent className="p-6">
          <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between space-y-4 lg:space-y-0">
            {/* Search */}
            <div className="flex items-center space-x-4 flex-1 max-w-md">
              <div className="relative flex-1">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-secondary-400 w-4 h-4" />
                <Input
                  placeholder="Search students..."
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
                  <option value="active">Active</option>
                  <option value="inactive">Inactive</option>
                  <option value="struggling">Struggling</option>
                </select>
              </div>

              <select
                value={filterSkillLevel}
                onChange={(e) => setFilterSkillLevel(e.target.value as any)}
                className="input text-sm"
              >
                <option value="all">All Levels</option>
                <option value="beginner">Beginner</option>
                <option value="intermediate">Intermediate</option>
                <option value="advanced">Advanced</option>
              </select>

              <div className="flex border rounded-lg">
                <button
                  onClick={() => setViewMode('table')}
                  className={`px-3 py-2 text-sm ${viewMode === 'table' 
                    ? 'bg-primary-100 text-primary-600' 
                    : 'text-secondary-600 hover:bg-gray-100'}`}
                >
                  Table
                </button>
                <button
                  onClick={() => setViewMode('grid')}
                  className={`px-3 py-2 text-sm ${viewMode === 'grid' 
                    ? 'bg-primary-100 text-primary-600' 
                    : 'text-secondary-600 hover:bg-gray-100'}`}
                >
                  Grid
                </button>
              </div>
            </div>
          </div>

          {/* Bulk Actions */}
          {selectedStudents.length > 0 && (
            <div className="mt-4 p-3 bg-primary-50 rounded-lg flex items-center justify-between">
              <span className="text-sm font-medium text-primary-700">
                {selectedStudents.length} student{selectedStudents.length > 1 ? 's' : ''} selected
              </span>
              <div className="flex space-x-2">
                <Button
                  size="sm"
                  variant="outline"
                  onClick={() => handleBulkAction('Send Email')}
                >
                  <Mail className="w-4 h-4 mr-1" />
                  Email
                </Button>
                <Button
                  size="sm"
                  variant="outline"
                  onClick={() => handleBulkAction('Export Data')}
                >
                  <Download className="w-4 h-4 mr-1" />
                  Export
                </Button>
                <Button
                  size="sm"
                  variant="outline"
                  onClick={() => setSelectedStudents([])}
                >
                  Clear
                </Button>
              </div>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Student List */}
      <Card>
        <CardHeader>
          <CardTitle>Students ({filteredStudents.length})</CardTitle>
          <CardDescription>Manage your class roster and track student progress</CardDescription>
        </CardHeader>
        <CardContent>
          {viewMode === 'table' ? (
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b border-secondary-200">
                    <th className="text-left py-3 px-2">
                      <input
                        type="checkbox"
                        checked={selectedStudents.length === filteredStudents.length && filteredStudents.length > 0}
                        onChange={handleSelectAll}
                        className="rounded border-secondary-300"
                      />
                    </th>
                    <th className="text-left py-3 px-4 font-medium text-secondary-700">Student</th>
                    <th className="text-left py-3 px-4 font-medium text-secondary-700">Status</th>
                    <th className="text-left py-3 px-4 font-medium text-secondary-700">Progress</th>
                    <th className="text-left py-3 px-4 font-medium text-secondary-700">Score</th>
                    <th className="text-left py-3 px-4 font-medium text-secondary-700">Submissions</th>
                    <th className="text-left py-3 px-4 font-medium text-secondary-700">Last Activity</th>
                    <th className="text-left py-3 px-4 font-medium text-secondary-700">Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {filteredStudents.map((student) => (
                    <tr key={student.id} className="border-b border-secondary-100 hover:bg-gray-50">
                      <td className="py-4 px-2">
                        <input
                          type="checkbox"
                          checked={selectedStudents.includes(student.id)}
                          onChange={() => handleSelectStudent(student.id)}
                          className="rounded border-secondary-300"
                        />
                      </td>
                      <td className="py-4 px-4">
                        <div className="flex items-center">
                          <div className="w-10 h-10 bg-primary-100 rounded-full flex items-center justify-center mr-3">
                            <span className="text-sm font-medium text-primary-600">
                              {student.name.split(' ').map(n => n[0]).join('')}
                            </span>
                          </div>
                          <div>
                            <p className="font-medium text-secondary-900">{student.name}</p>
                            <p className="text-sm text-secondary-600">{student.studentId}</p>
                          </div>
                        </div>
                      </td>
                      <td className="py-4 px-4">
                        <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getStatusColor(student.status)}`}>
                          {student.status}
                        </span>
                      </td>
                      <td className="py-4 px-4">
                        <div className="flex items-center">
                          <div className="w-16 bg-gray-200 rounded-full h-2 mr-2">
                            <div
                              className="bg-primary-600 h-2 rounded-full"
                              style={{ width: `${student.progress}%` }}
                            ></div>
                          </div>
                          <span className="text-sm font-medium">{student.progress}%</span>
                        </div>
                      </td>
                      <td className="py-4 px-4">
                        <span className="font-medium">{student.averageScore.toFixed(1)}%</span>
                      </td>
                      <td className="py-4 px-4">
                        <span className="text-secondary-700">{student.submissionsCount}</span>
                      </td>
                      <td className="py-4 px-4">
                        <span className="text-sm text-secondary-600">{student.lastActivity}</span>
                      </td>
                      <td className="py-4 px-4">
                        <div className="flex items-center space-x-2">
                          <button
                            onClick={() => {
                              setSelectedStudent(student);
                              setShowStudentModal(true);
                            }}
                            className="p-1 text-secondary-400 hover:text-secondary-600"
                          >
                            <Eye className="w-4 h-4" />
                          </button>
                          <button className="p-1 text-secondary-400 hover:text-secondary-600">
                            <Edit className="w-4 h-4" />
                          </button>
                          <button className="p-1 text-secondary-400 hover:text-red-600">
                            <Trash2 className="w-4 h-4" />
                          </button>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {filteredStudents.map((student) => (
                <Card key={student.id} className="hover:shadow-lg transition-shadow">
                  <CardContent className="p-6">
                    <div className="flex items-center justify-between mb-4">
                      <div className="flex items-center">
                        <input
                          type="checkbox"
                          checked={selectedStudents.includes(student.id)}
                          onChange={() => handleSelectStudent(student.id)}
                          className="rounded border-secondary-300 mr-3"
                        />
                        <div className="w-12 h-12 bg-primary-100 rounded-full flex items-center justify-center">
                          <span className="text-lg font-medium text-primary-600">
                            {student.name.split(' ').map(n => n[0]).join('')}
                          </span>
                        </div>
                      </div>
                      <div className="flex space-x-1">
                        <button
                          onClick={() => {
                            setSelectedStudent(student);
                            setShowStudentModal(true);
                          }}
                          className="p-1 text-secondary-400 hover:text-secondary-600"
                        >
                          <Eye className="w-4 h-4" />
                        </button>
                        <button className="p-1 text-secondary-400 hover:text-secondary-600">
                          <MoreHorizontal className="w-4 h-4" />
                        </button>
                      </div>
                    </div>

                    <div className="space-y-3">
                      <div>
                        <h3 className="font-semibold text-secondary-900">{student.name}</h3>
                        <p className="text-sm text-secondary-600">{student.studentId}</p>
                      </div>

                      <div className="flex justify-between items-center">
                        <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getStatusColor(student.status)}`}>
                          {student.status}
                        </span>
                        <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getSkillLevelColor(student.skillLevel)}`}>
                          {student.skillLevel}
                        </span>
                      </div>

                      <div className="space-y-2">
                        <div className="flex justify-between text-sm">
                          <span className="text-secondary-600">Progress</span>
                          <span className="font-medium">{student.progress}%</span>
                        </div>
                        <div className="w-full bg-gray-200 rounded-full h-2">
                          <div
                            className="bg-primary-600 h-2 rounded-full"
                            style={{ width: `${student.progress}%` }}
                          ></div>
                        </div>
                      </div>

                      <div className="grid grid-cols-2 gap-4 text-sm">
                        <div>
                          <p className="text-secondary-600">Score</p>
                          <p className="font-medium">{student.averageScore.toFixed(1)}%</p>
                        </div>
                        <div>
                          <p className="text-secondary-600">Submissions</p>
                          <p className="font-medium">{student.submissionsCount}</p>
                        </div>
                      </div>

                      <div className="text-xs text-secondary-600 border-t pt-2">
                        Last active: {student.lastActivity}
                      </div>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          )}

          {filteredStudents.length === 0 && (
            <div className="text-center py-12">
              <Users className="w-12 h-12 text-secondary-300 mx-auto mb-4" />
              <h3 className="text-lg font-medium text-secondary-900 mb-2">No students found</h3>
              <p className="text-secondary-600">Try adjusting your search or filters</p>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Student Detail Modal */}
      {showStudentModal && selectedStudent && (
        <Modal open={showStudentModal} onClose={() => setShowStudentModal(false)}>
          <div className="bg-white rounded-lg p-6 w-full max-w-2xl mx-4">
            <div className="flex items-center justify-between mb-6">
              <div className="flex items-center">
                <div className="w-16 h-16 bg-primary-100 rounded-full flex items-center justify-center mr-4">
                  <span className="text-xl font-medium text-primary-600">
                    {selectedStudent.name.split(' ').map(n => n[0]).join('')}
                  </span>
                </div>
                <div>
                  <h2 className="text-xl font-bold text-secondary-900">{selectedStudent.name}</h2>
                  <p className="text-secondary-600">{selectedStudent.studentId}</p>
                  <p className="text-sm text-secondary-500">{selectedStudent.email}</p>
                </div>
              </div>
              <button
                onClick={() => setShowStudentModal(false)}
                className="text-secondary-400 hover:text-secondary-600"
              >
                ✕
              </button>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="space-y-4">
                <div>
                  <h3 className="font-medium text-secondary-900 mb-2">Academic Progress</h3>
                  <div className="space-y-3">
                    <div className="flex justify-between">
                      <span className="text-sm text-secondary-600">Overall Progress</span>
                      <span className="font-medium">{selectedStudent.progress}%</span>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-2">
                      <div
                        className="bg-primary-600 h-2 rounded-full"
                        style={{ width: `${selectedStudent.progress}%` }}
                      ></div>
                    </div>
                    
                    <div className="flex justify-between">
                      <span className="text-sm text-secondary-600">Course Completion</span>
                      <span className="font-medium">{selectedStudent.courseCompletion}%</span>
                    </div>
                    
                    <div className="flex justify-between">
                      <span className="text-sm text-secondary-600">Average Score</span>
                      <span className="font-medium">{selectedStudent.averageScore.toFixed(1)}%</span>
                    </div>
                  </div>
                </div>

                <div>
                  <h3 className="font-medium text-secondary-900 mb-2">Activity Stats</h3>
                  <div className="space-y-2">
                    <div className="flex justify-between">
                      <span className="text-sm text-secondary-600">Submissions</span>
                      <span className="font-medium">{selectedStudent.submissionsCount}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-sm text-secondary-600">AI Interactions</span>
                      <span className="font-medium">{selectedStudent.aiInteractionCount}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-sm text-secondary-600">Last Activity</span>
                      <span className="font-medium">{selectedStudent.lastActivity}</span>
                    </div>
                  </div>
                </div>
              </div>

              <div className="space-y-4">
                <div>
                  <h3 className="font-medium text-secondary-900 mb-2">Status & Level</h3>
                  <div className="space-y-3">
                    <div className="flex justify-between items-center">
                      <span className="text-sm text-secondary-600">Status</span>
                      <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getStatusColor(selectedStudent.status)}`}>
                        {selectedStudent.status}
                      </span>
                    </div>
                    <div className="flex justify-between items-center">
                      <span className="text-sm text-secondary-600">Skill Level</span>
                      <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getSkillLevelColor(selectedStudent.skillLevel)}`}>
                        {selectedStudent.skillLevel}
                      </span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-sm text-secondary-600">Join Date</span>
                      <span className="font-medium">{selectedStudent.joinDate}</span>
                    </div>
                  </div>
                </div>

                <div>
                  <h3 className="font-medium text-secondary-900 mb-2">Quick Actions</h3>
                  <div className="space-y-2">
                    <Button variant="outline" className="w-full justify-start">
                      <Mail className="w-4 h-4 mr-2" />
                      Send Email
                    </Button>
                    <Button variant="outline" className="w-full justify-start">
                      <Eye className="w-4 h-4 mr-2" />
                      View Submissions
                    </Button>
                    <Button variant="outline" className="w-full justify-start">
                      <Award className="w-4 h-4 mr-2" />
                      View Progress
                    </Button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </Modal>
      )}

      {/* Add Student Modal */}
      {showAddStudentModal && (
        <Modal open={showAddStudentModal} onClose={() => setShowAddStudentModal(false)}>
          <div className="bg-white rounded-lg p-6 w-full max-w-md mx-4">
            <h2 className="text-xl font-bold text-secondary-900 mb-4">Add New Student</h2>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-secondary-700 mb-1">
                  Student Name
                </label>
                <Input placeholder="Enter student name" />
              </div>
              <div>
                <label className="block text-sm font-medium text-secondary-700 mb-1">
                  Student ID
                </label>
                <Input placeholder="Enter student ID" />
              </div>
              <div>
                <label className="block text-sm font-medium text-secondary-700 mb-1">
                  Email Address
                </label>
                <Input type="email" placeholder="Enter email address" />
              </div>
              <div>
                <label className="block text-sm font-medium text-secondary-700 mb-1">
                  Skill Level
                </label>
                <select className="input w-full">
                  <option value="beginner">Beginner</option>
                  <option value="intermediate">Intermediate</option>
                  <option value="advanced">Advanced</option>
                </select>
              </div>
            </div>
            <div className="flex justify-end space-x-3 mt-6">
              <Button variant="outline" onClick={() => setShowAddStudentModal(false)}>
                Cancel
              </Button>
              <Button onClick={() => {
                addNotification({
                  type: 'success',
                  title: 'Student Added',
                  message: 'New student has been added to the class',
                  duration: 3000
                });
                setShowAddStudentModal(false);
              }}>
                Add Student
              </Button>
            </div>
          </div>
        </Modal>
      )}
    </div>
  );
};

export default ClassManagement;