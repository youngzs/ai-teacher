import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { useAppStore } from '../../store/app';
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '../../components/ui';
import { 
  BookOpen, 
  Users, 
  ClipboardList, 
  TrendingUp, 
  Plus, 
  Eye, 
  Clock, 
  AlertTriangle,
  CheckCircle,
  XCircle,
  Brain,
  Target,
  Award,
  Calendar,
  Activity
} from 'lucide-react';

export const TeacherDashboard: React.FC = () => {
  const { addNotification } = useAppStore();

  useEffect(() => {
    // Welcome notification
    addNotification({
      type: 'success',
      title: 'Welcome back!',
      message: 'Ready to guide your students on their programming journey?',
      duration: 3000
    });
  }, [addNotification]);

  // Mock data for the dashboard
  const stats = {
    totalCourses: 3,
    totalStudents: 45,
    totalAssignments: 12,
    averageScore: 85.2,
    pendingSubmissions: 18,
    aiReviewsPending: 7,
    avgFeedbackQuality: 4.3,
    weeklyProgress: 12.5
  };

  const aiInsights = {
    commonErrors: [
      { error: 'Syntax Errors', count: 23, trend: 'down' },
      { error: 'Logic Issues', count: 15, trend: 'up' },
      { error: 'Memory Management', count: 8, trend: 'stable' }
    ],
    feedbackMetrics: {
      totalGenerated: 142,
      qualityScore: 4.3,
      reviewRate: 85.2,
      studentSatisfaction: 4.1
    }
  };

  const weeklyData = {
    submissions: [12, 18, 15, 22, 19, 25, 20],
    feedback: [8, 14, 12, 18, 15, 21, 17],
    days: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
  };

  const recentActivity = [
    { id: '1', type: 'submission', description: 'New submission from Alice Johnson', time: '2 minutes ago' },
    { id: '2', type: 'assignment', description: 'Assignment "Binary Search" published', time: '1 hour ago' },
    { id: '3', type: 'feedback', description: 'AI feedback ready for review', time: '3 hours ago' },
  ];

  const courses = [
    { id: '1', title: 'C Programming Fundamentals', students: 20, assignments: 5, progress: 75 },
    { id: '2', title: 'Python Basics', students: 15, assignments: 4, progress: 60 },
    { id: '3', title: 'Data Structures', students: 10, assignments: 3, progress: 45 },
  ];

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-secondary-900">Teacher Dashboard</h1>
          <p className="text-secondary-600 mt-1">Monitor your courses and student progress</p>
        </div>
        <Link
          to="/courses/new"
          className="inline-flex items-center px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors"
        >
          <Plus className="w-5 h-5 mr-2" />
          New Course
        </Link>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 xl:grid-cols-8 gap-4">
        <Card className="md:col-span-1 lg:col-span-1 xl:col-span-2">
          <CardContent className="p-4">
            <div className="flex items-center">
              <div className="p-2 bg-blue-100 rounded-lg">
                <BookOpen className="w-5 h-5 text-blue-600" />
              </div>
              <div className="ml-3 flex-1">
                <p className="text-sm font-medium text-secondary-600">Courses</p>
                <p className="text-xl font-bold text-secondary-900">{stats.totalCourses}</p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card className="md:col-span-1 lg:col-span-1 xl:col-span-2">
          <CardContent className="p-4">
            <div className="flex items-center">
              <div className="p-2 bg-green-100 rounded-lg">
                <Users className="w-5 h-5 text-green-600" />
              </div>
              <div className="ml-3 flex-1">
                <p className="text-sm font-medium text-secondary-600">Students</p>
                <p className="text-xl font-bold text-secondary-900">{stats.totalStudents}</p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card className="md:col-span-1 lg:col-span-1 xl:col-span-2">
          <CardContent className="p-4">
            <div className="flex items-center">
              <div className="p-2 bg-purple-100 rounded-lg">
                <ClipboardList className="w-5 h-5 text-purple-600" />
              </div>
              <div className="ml-3 flex-1">
                <p className="text-sm font-medium text-secondary-600">Assignments</p>
                <p className="text-xl font-bold text-secondary-900">{stats.totalAssignments}</p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card className="md:col-span-1 lg:col-span-1 xl:col-span-2">
          <CardContent className="p-4">
            <div className="flex items-center">
              <div className="p-2 bg-orange-100 rounded-lg">
                <TrendingUp className="w-5 h-5 text-orange-600" />
              </div>
              <div className="ml-3 flex-1">
                <p className="text-sm font-medium text-secondary-600">Avg Score</p>
                <p className="text-xl font-bold text-secondary-900">{stats.averageScore}%</p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Priority Actions Bar */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <Card className="bg-warning-50 border-warning-200">
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center">
                <Clock className="w-5 h-5 text-warning-600 mr-2" />
                <div>
                  <p className="text-sm font-medium text-warning-800">Pending Reviews</p>
                  <p className="text-lg font-bold text-warning-900">{stats.pendingSubmissions}</p>
                </div>
              </div>
              <Link to="/submissions/pending" className="text-warning-600 hover:text-warning-700">
                <Eye className="w-4 h-4" />
              </Link>
            </div>
          </CardContent>
        </Card>

        <Card className="bg-primary-50 border-primary-200">
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center">
                <Brain className="w-5 h-5 text-primary-600 mr-2" />
                <div>
                  <p className="text-sm font-medium text-primary-800">AI Reviews</p>
                  <p className="text-lg font-bold text-primary-900">{stats.aiReviewsPending}</p>
                </div>
              </div>
              <Link to="/feedback/review" className="text-primary-600 hover:text-primary-700">
                <Eye className="w-4 h-4" />
              </Link>
            </div>
          </CardContent>
        </Card>

        <Card className="bg-success-50 border-success-200">
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center">
                <Award className="w-5 h-5 text-success-600 mr-2" />
                <div>
                  <p className="text-sm font-medium text-success-800">AI Quality</p>
                  <p className="text-lg font-bold text-success-900">{stats.avgFeedbackQuality}/5.0</p>
                </div>
              </div>
              <div className="flex items-center text-success-600">
                <TrendingUp className="w-4 h-4" />
              </div>
            </div>
          </CardContent>
        </Card>

        <Card className="bg-secondary-50 border-secondary-200">
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center">
                <Activity className="w-5 h-5 text-secondary-600 mr-2" />
                <div>
                  <p className="text-sm font-medium text-secondary-800">Weekly Growth</p>
                  <p className="text-lg font-bold text-secondary-900">+{stats.weeklyProgress}%</p>
                </div>
              </div>
              <div className="flex items-center text-success-600">
                <TrendingUp className="w-4 h-4" />
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      <div className="grid grid-cols-1 xl:grid-cols-3 gap-6">
        {/* Course Performance Overview */}
        <Card className="xl:col-span-2">
          <CardHeader className="flex flex-row items-center justify-between">
            <div>
              <CardTitle>Course Performance</CardTitle>
              <CardDescription>Student progress and engagement metrics</CardDescription>
            </div>
            <Link
              to="/courses"
              className="text-sm text-primary-600 hover:text-primary-700 font-medium"
            >
              View All
            </Link>
          </CardHeader>
          <CardContent>
            <div className="space-y-6">
              {courses.map((course) => (
                <div key={course.id} className="p-4 bg-gray-50 rounded-lg">
                  <div className="flex items-center justify-between mb-3">
                    <div className="flex-1">
                      <h4 className="font-semibold text-secondary-900">{course.title}</h4>
                      <p className="text-sm text-secondary-600">
                        {course.students} students • {course.assignments} assignments
                      </p>
                    </div>
                    <div className="flex items-center space-x-2">
                      <span className="text-sm font-medium text-secondary-700">{course.progress}%</span>
                      <Link
                        to={`/courses/${course.id}`}
                        className="p-1 text-secondary-400 hover:text-secondary-600"
                      >
                        <Eye className="w-4 h-4" />
                      </Link>
                    </div>
                  </div>
                  
                  {/* Progress Bar */}
                  <div className="w-full bg-gray-200 rounded-full h-2 mb-3">
                    <div 
                      className="bg-primary-600 h-2 rounded-full transition-all duration-300" 
                      style={{ width: `${course.progress}%` }}
                    ></div>
                  </div>
                  
                  {/* Course Metrics */}
                  <div className="grid grid-cols-3 gap-4 pt-3 border-t border-gray-200">
                    <div className="text-center">
                      <div className="text-lg font-semibold text-green-600">92%</div>
                      <div className="text-xs text-secondary-600">Submission Rate</div>
                    </div>
                    <div className="text-center">
                      <div className="text-lg font-semibold text-blue-600">4.2</div>
                      <div className="text-xs text-secondary-600">Avg Score</div>
                    </div>
                    <div className="text-center">
                      <div className="text-lg font-semibold text-purple-600">87%</div>
                      <div className="text-xs text-secondary-600">Engagement</div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* AI Insights Panel */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center">
              <Brain className="w-5 h-5 mr-2 text-primary-600" />
              AI Insights
            </CardTitle>
            <CardDescription>Common issues and recommendations</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {/* Common Errors */}
              <div>
                <h4 className="font-medium text-secondary-900 mb-3">Common Errors</h4>
                <div className="space-y-2">
                  {aiInsights.commonErrors.map((error, index) => (
                    <div key={index} className="flex items-center justify-between p-2 bg-gray-50 rounded">
                      <div className="flex-1">
                        <p className="text-sm font-medium">{error.error}</p>
                        <p className="text-xs text-secondary-600">{error.count} occurrences</p>
                      </div>
                      <div className={`flex items-center ${
                        error.trend === 'down' ? 'text-green-600' :
                        error.trend === 'up' ? 'text-red-600' :
                        'text-gray-600'
                      }`}>
                        {error.trend === 'down' ? (
                          <TrendingUp className="w-4 h-4 rotate-180" />
                        ) : error.trend === 'up' ? (
                          <TrendingUp className="w-4 h-4" />
                        ) : (
                          <div className="w-2 h-2 bg-gray-400 rounded-full" />
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
              
              {/* AI Quality Metrics */}
              <div>
                <h4 className="font-medium text-secondary-900 mb-3">AI Feedback Quality</h4>
                <div className="space-y-3">
                  <div className="flex justify-between items-center">
                    <span className="text-sm text-secondary-600">Generated</span>
                    <span className="font-medium">{aiInsights.feedbackMetrics.totalGenerated}</span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-sm text-secondary-600">Quality Score</span>
                    <span className="font-medium text-green-600">{aiInsights.feedbackMetrics.qualityScore}/5.0</span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-sm text-secondary-600">Review Rate</span>
                    <span className="font-medium">{aiInsights.feedbackMetrics.reviewRate}%</span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-sm text-secondary-600">Student Rating</span>
                    <span className="font-medium text-blue-600">{aiInsights.feedbackMetrics.studentSatisfaction}/5.0</span>
                  </div>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Weekly Activity Chart */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center">
            <Activity className="w-5 h-5 mr-2 text-primary-600" />
            Weekly Activity
          </CardTitle>
          <CardDescription>Student submissions and AI feedback generation</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="h-64 flex items-end justify-between p-4">
            {weeklyData.submissions.map((submissions, index) => (
              <div key={index} className="flex flex-col items-center space-y-2">
                <div className="flex space-x-1 items-end">
                  {/* Submissions bar */}
                  <div 
                    className="bg-primary-500 rounded-t w-4" 
                    style={{ height: `${(submissions / Math.max(...weeklyData.submissions)) * 150}px` }}
                  ></div>
                  {/* Feedback bar */}
                  <div 
                    className="bg-green-500 rounded-t w-4" 
                    style={{ height: `${(weeklyData.feedback[index] / Math.max(...weeklyData.feedback)) * 150}px` }}
                  ></div>
                </div>
                <div className="text-xs text-secondary-600">{weeklyData.days[index]}</div>
                <div className="text-xs text-center">
                  <div className="text-primary-600">{submissions}</div>
                  <div className="text-green-600">{weeklyData.feedback[index]}</div>
                </div>
              </div>
            ))}
          </div>
          <div className="flex justify-center space-x-4 pt-4 border-t">
            <div className="flex items-center">
              <div className="w-3 h-3 bg-primary-500 rounded mr-2"></div>
              <span className="text-sm text-secondary-600">Submissions</span>
            </div>
            <div className="flex items-center">
              <div className="w-3 h-3 bg-green-500 rounded mr-2"></div>
              <span className="text-sm text-secondary-600">AI Feedback</span>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Recent Activity */}
      <Card>
        <CardHeader>
          <CardTitle>Recent Activity</CardTitle>
          <CardDescription>Latest updates from your courses</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {recentActivity.map((activity) => (
              <div key={activity.id} className="flex items-start space-x-3 p-3 hover:bg-gray-50 rounded-lg transition-colors">
                <div className={`p-2 rounded-full ${
                  activity.type === 'submission' ? 'bg-green-100' :
                  activity.type === 'assignment' ? 'bg-blue-100' :
                  'bg-orange-100'
                }`}>
                  {activity.type === 'submission' ? (
                    <ClipboardList className="w-4 h-4 text-green-600" />
                  ) : activity.type === 'assignment' ? (
                    <BookOpen className="w-4 h-4 text-blue-600" />
                  ) : (
                    <Brain className="w-4 h-4 text-orange-600" />
                  )}
                </div>
                <div className="flex-1">
                  <p className="text-sm font-medium text-secondary-900">{activity.description}</p>
                  <p className="text-xs text-secondary-600 mt-1">{activity.time}</p>
                </div>
                <button className="text-secondary-400 hover:text-secondary-600 p-1">
                  <Eye className="w-4 h-4" />
                </button>
              </div>
            ))}
          </div>
          <div className="pt-4 border-t">
            <Link 
              to="/activity"
              className="text-sm text-primary-600 hover:text-primary-700 font-medium"
            >
              View All Activity →
            </Link>
          </div>
        </CardContent>
      </Card>

      {/* Quick Actions */}
      <Card>
        <CardHeader>
          <CardTitle>Quick Actions</CardTitle>
          <CardDescription>Common tasks to get you started</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            <Link
              to="/courses/new"
              className="flex items-center p-4 bg-primary-50 rounded-lg hover:bg-primary-100 transition-colors"
            >
              <Plus className="w-8 h-8 text-primary-600 mr-3" />
              <span className="font-medium text-primary-700">Create Course</span>
            </Link>
            
            <Link
              to="/assignments/new"
              className="flex items-center p-4 bg-green-50 rounded-lg hover:bg-green-100 transition-colors"
            >
              <ClipboardList className="w-8 h-8 text-green-600 mr-3" />
              <span className="font-medium text-green-700">New Assignment</span>
            </Link>
            
            <Link
              to="/students"
              className="flex items-center p-4 bg-blue-50 rounded-lg hover:bg-blue-100 transition-colors"
            >
              <Users className="w-8 h-8 text-blue-600 mr-3" />
              <span className="font-medium text-blue-700">View Students</span>
            </Link>
            
            <Link
              to="/analytics"
              className="flex items-center p-4 bg-orange-50 rounded-lg hover:bg-orange-100 transition-colors"
            >
              <TrendingUp className="w-8 h-8 text-orange-600 mr-3" />
              <span className="font-medium text-orange-700">View Analytics</span>
            </Link>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};