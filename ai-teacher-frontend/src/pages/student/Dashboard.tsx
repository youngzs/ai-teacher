import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { useAppStore } from '../../store/app';
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '../../components/ui';
import { 
  BookOpen, 
  ClipboardCheck, 
  TrendingUp, 
  Clock, 
  Upload, 
  Eye, 
  AlertTriangle,
  Brain,
  Target,
  Award,
  Zap,
  MessageSquare,
  CheckCircle,
  XCircle,
  Activity,
  Calendar,
  Star,
  Trophy,
  Lightbulb
} from 'lucide-react';

export const StudentDashboard: React.FC = () => {
  const { addNotification } = useAppStore();

  useEffect(() => {
    // Welcome notification
    addNotification({
      type: 'info',
      title: 'Welcome back!',
      message: 'Ready to continue your programming journey?',
      duration: 3000
    });
  }, [addNotification]);

  // Mock data for the dashboard
  const stats = {
    enrolledCourses: 2,
    completedAssignments: 8,
    averageScore: 88.5,
    hoursSpent: 24,
    aiInteractions: 156,
    skillPoints: 1240,
    currentStreak: 7,
    weeklyGoal: 12,
    weeklyCompleted: 9
  };

  const skillProgress = {
    syntax: { level: 85, recent: +5 },
    logic: { level: 72, recent: +8 },
    debugging: { level: 68, recent: -2 },
    algorithms: { level: 59, recent: +12 },
    bestPractices: { level: 77, recent: +3 }
  };

  const recentFeedback = [
    {
      id: '1',
      assignment: 'Binary Search Implementation',
      type: 'improvement',
      message: 'Great implementation! Consider adding input validation.',
      timestamp: '2 hours ago',
      category: 'Code Quality'
    },
    {
      id: '2',
      assignment: 'Array Operations',
      type: 'success',
      message: 'Excellent use of efficient algorithms!',
      timestamp: '1 day ago',
      category: 'Performance'
    },
    {
      id: '3',
      assignment: 'String Manipulation',
      type: 'warning',
      message: 'Memory management needs attention in line 15.',
      timestamp: '2 days ago',
      category: 'Memory Management'
    }
  ];

  const achievements = [
    { id: '1', title: 'Code Master', description: '100 successful submissions', icon: '🏆', unlocked: true },
    { id: '2', title: 'Debug Detective', description: 'Fixed 50 logic errors', icon: '🔍', unlocked: true },
    { id: '3', title: 'Speed Coder', description: 'Complete assignment in under 30 min', icon: '⚡', unlocked: false },
    { id: '4', title: 'AI Collaborator', description: '200 AI interactions', icon: '🤖', unlocked: false }
  ];

  const upcomingAssignments = [
    { 
      id: '1', 
      title: 'Binary Search Implementation', 
      course: 'Data Structures', 
      dueDate: '2024-01-15',
      difficulty: 'Medium',
      isOverdue: false
    },
    { 
      id: '2', 
      title: 'File I/O Operations', 
      course: 'C Programming', 
      dueDate: '2024-01-12',
      difficulty: 'Easy',
      isOverdue: true
    },
    { 
      id: '3', 
      title: 'Sorting Algorithms', 
      course: 'Python Basics', 
      dueDate: '2024-01-20',
      difficulty: 'Hard',
      isOverdue: false
    },
  ];

  const recentSubmissions = [
    { id: '1', title: 'Array Operations', course: 'C Programming', score: 95, status: 'graded', submittedAt: '2024-01-08' },
    { id: '2', title: 'String Manipulation', course: 'Python Basics', score: 82, status: 'graded', submittedAt: '2024-01-06' },
    { id: '3', title: 'Loops and Conditions', course: 'C Programming', score: null, status: 'pending', submittedAt: '2024-01-10' },
  ];

  const courses = [
    { 
      id: '1', 
      title: 'C Programming Fundamentals', 
      instructor: 'Dr. Smith',
      progress: 75,
      nextAssignment: 'Pointers and Memory'
    },
    { 
      id: '2', 
      title: 'Python Basics', 
      instructor: 'Prof. Johnson',
      progress: 60,
      nextAssignment: 'Object-Oriented Programming'
    },
  ];

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-secondary-900">Student Dashboard</h1>
          <p className="text-secondary-600 mt-1">Track your learning progress and assignments</p>
        </div>
        <div className="flex space-x-3">
          <Link
            to="/my-submissions"
            className="inline-flex items-center px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors"
          >
            <Upload className="w-5 h-5 mr-2" />
            My Submissions
          </Link>
        </div>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 xl:grid-cols-6 gap-4">
        <Card className="md:col-span-1 xl:col-span-1">
          <CardContent className="p-4">
            <div className="flex items-center">
              <div className="p-2 bg-blue-100 rounded-lg">
                <BookOpen className="w-5 h-5 text-blue-600" />
              </div>
              <div className="ml-3 flex-1">
                <p className="text-sm font-medium text-secondary-600">Courses</p>
                <p className="text-xl font-bold text-secondary-900">{stats.enrolledCourses}</p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card className="md:col-span-1 xl:col-span-1">
          <CardContent className="p-4">
            <div className="flex items-center">
              <div className="p-2 bg-green-100 rounded-lg">
                <ClipboardCheck className="w-5 h-5 text-green-600" />
              </div>
              <div className="ml-3 flex-1">
                <p className="text-sm font-medium text-secondary-600">Completed</p>
                <p className="text-xl font-bold text-secondary-900">{stats.completedAssignments}</p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card className="md:col-span-1 xl:col-span-1">
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

        <Card className="md:col-span-1 xl:col-span-1">
          <CardContent className="p-4">
            <div className="flex items-center">
              <div className="p-2 bg-purple-100 rounded-lg">
                <Brain className="w-5 h-5 text-purple-600" />
              </div>
              <div className="ml-3 flex-1">
                <p className="text-sm font-medium text-secondary-600">AI Helps</p>
                <p className="text-xl font-bold text-secondary-900">{stats.aiInteractions}</p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card className="md:col-span-1 xl:col-span-1">
          <CardContent className="p-4">
            <div className="flex items-center">
              <div className="p-2 bg-yellow-100 rounded-lg">
                <Zap className="w-5 h-5 text-yellow-600" />
              </div>
              <div className="ml-3 flex-1">
                <p className="text-sm font-medium text-secondary-600">Streak</p>
                <p className="text-xl font-bold text-secondary-900">{stats.currentStreak} days</p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card className="md:col-span-1 xl:col-span-1">
          <CardContent className="p-4">
            <div className="flex items-center">
              <div className="p-2 bg-indigo-100 rounded-lg">
                <Star className="w-5 h-5 text-indigo-600" />
              </div>
              <div className="ml-3 flex-1">
                <p className="text-sm font-medium text-secondary-600">XP Points</p>
                <p className="text-xl font-bold text-secondary-900">{stats.skillPoints.toLocaleString()}</p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Weekly Goal Progress */}
      <Card className="bg-gradient-to-r from-primary-50 to-primary-100">
        <CardContent className="p-6">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center">
              <Target className="w-6 h-6 text-primary-600 mr-3" />
              <div>
                <h3 className="font-semibold text-primary-900">Weekly Learning Goal</h3>
                <p className="text-sm text-primary-700">Complete {stats.weeklyGoal} assignments this week</p>
              </div>
            </div>
            <div className="text-right">
              <p className="text-2xl font-bold text-primary-900">{stats.weeklyCompleted}/{stats.weeklyGoal}</p>
              <p className="text-sm text-primary-700">{Math.round((stats.weeklyCompleted / stats.weeklyGoal) * 100)}% Complete</p>
            </div>
          </div>
          <div className="w-full bg-primary-200 rounded-full h-3">
            <div 
              className="bg-primary-600 h-3 rounded-full transition-all duration-300" 
              style={{ width: `${(stats.weeklyCompleted / stats.weeklyGoal) * 100}%` }}
            ></div>
          </div>
        </CardContent>
      </Card>

      <div className="grid grid-cols-1 xl:grid-cols-3 gap-6">
        {/* Upcoming Assignments */}
        <Card className="xl:col-span-2">
          <CardHeader>
            <CardTitle className="flex items-center">
              <Calendar className="w-5 h-5 mr-2 text-primary-600" />
              Upcoming Assignments
              {upcomingAssignments.some(a => a.isOverdue) && (
                <AlertTriangle className="w-5 h-5 text-red-500 ml-2" />
              )}
            </CardTitle>
            <CardDescription>Assignments due soon and priorities</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {upcomingAssignments.map((assignment) => (
                <div 
                  key={assignment.id} 
                  className={`p-4 rounded-lg border ${
                    assignment.isOverdue 
                      ? 'bg-red-50 border-red-200' 
                      : 'bg-white border-secondary-200 hover:border-primary-300 hover:shadow-sm'
                  } transition-all`}
                >
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center mb-2">
                        <h4 className={`font-semibold ${assignment.isOverdue ? 'text-red-900' : 'text-secondary-900'}`}>
                          {assignment.title}
                        </h4>
                        <span className={`ml-2 px-2 py-1 rounded-full text-xs font-medium ${
                          assignment.difficulty === 'Easy' ? 'bg-green-100 text-green-600' :
                          assignment.difficulty === 'Medium' ? 'bg-yellow-100 text-yellow-600' :
                          'bg-red-100 text-red-600'
                        }`}>
                          {assignment.difficulty}
                        </span>
                      </div>
                      <p className="text-sm text-secondary-600 mb-2">{assignment.course}</p>
                      <div className="flex items-center space-x-4 text-xs">
                        <span className={`flex items-center ${
                          assignment.isOverdue ? 'text-red-600 font-medium' : 'text-secondary-600'
                        }`}>
                          <Clock className="w-3 h-3 mr-1" />
                          Due: {new Date(assignment.dueDate).toLocaleDateString()}
                          {assignment.isOverdue && ' (Overdue)'}
                        </span>
                        <span className="text-secondary-600">Est. 2 hours</span>
                      </div>
                    </div>
                    <div className="flex flex-col items-end space-y-2">
                      <Link
                        to={`/assignments/${assignment.id}/submit`}
                        className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
                          assignment.isOverdue 
                            ? 'bg-red-600 text-white hover:bg-red-700' 
                            : 'bg-primary-600 text-white hover:bg-primary-700'
                        }`}
                      >
                        {assignment.isOverdue ? 'Submit Late' : 'Start'}
                      </Link>
                      <button className="text-xs text-secondary-500 hover:text-secondary-700">
                        View Details
                      </button>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* AI Feedback Panel */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center">
              <Brain className="w-5 h-5 mr-2 text-purple-600" />
              Recent AI Feedback
            </CardTitle>
            <CardDescription>Latest insights from your AI tutor</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {recentFeedback.map((feedback) => (
                <div key={feedback.id} className="p-3 rounded-lg bg-gray-50 hover:bg-gray-100 transition-colors">
                  <div className="flex items-start space-x-3">
                    <div className={`p-1 rounded-full flex-shrink-0 ${
                      feedback.type === 'success' ? 'bg-green-100' :
                      feedback.type === 'warning' ? 'bg-yellow-100' :
                      'bg-blue-100'
                    }`}>
                      {feedback.type === 'success' ? (
                        <CheckCircle className="w-4 h-4 text-green-600" />
                      ) : feedback.type === 'warning' ? (
                        <AlertTriangle className="w-4 h-4 text-yellow-600" />
                      ) : (
                        <Lightbulb className="w-4 h-4 text-blue-600" />
                      )}
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center justify-between mb-1">
                        <p className="text-xs font-medium text-secondary-600 truncate">
                          {feedback.assignment}
                        </p>
                        <span className="text-xs text-secondary-500 flex-shrink-0">
                          {feedback.timestamp}
                        </span>
                      </div>
                      <p className="text-sm text-secondary-900 mb-1">{feedback.message}</p>
                      <span className="inline-flex items-center px-2 py-0.5 rounded-full text-xs bg-secondary-100 text-secondary-600">
                        {feedback.category}
                      </span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
            <div className="pt-4 border-t">
              <Link 
                to="/feedback"
                className="text-sm text-purple-600 hover:text-purple-700 font-medium"
              >
                View All Feedback →
              </Link>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Skills Progress */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center">
            <Activity className="w-5 h-5 mr-2 text-primary-600" />
            Skill Development
          </CardTitle>
          <CardDescription>Track your programming skills improvement</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-6">
            {Object.entries(skillProgress).map(([skill, data]) => (
              <div key={skill} className="text-center">
                <div className="relative w-20 h-20 mx-auto mb-3">
                  <svg className="w-20 h-20 transform -rotate-90" viewBox="0 0 36 36">
                    <path
                      d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
                      fill="none"
                      stroke="#e5e7eb"
                      strokeWidth="2"
                    />
                    <path
                      d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
                      fill="none"
                      stroke="#3b82f6"
                      strokeWidth="2"
                      strokeDasharray={`${data.level}, 100`}
                    />
                  </svg>
                  <div className="absolute inset-0 flex items-center justify-center">
                    <span className="text-sm font-bold text-secondary-900">{data.level}%</span>
                  </div>
                </div>
                <h4 className="font-medium text-secondary-900 capitalize mb-1">{skill.replace(/([A-Z])/g, ' $1').trim()}</h4>
                <div className={`flex items-center justify-center text-xs ${
                  data.recent > 0 ? 'text-green-600' : 
                  data.recent < 0 ? 'text-red-600' : 'text-secondary-600'
                }`}>
                  <TrendingUp className={`w-3 h-3 mr-1 ${
                    data.recent < 0 ? 'rotate-180' : ''
                  }`} />
                  {data.recent > 0 ? '+' : ''}{data.recent} this week
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Achievements and Recent Submissions */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Achievements */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center">
              <Trophy className="w-5 h-5 mr-2 text-yellow-600" />
              Achievements
            </CardTitle>
            <CardDescription>Your programming milestones</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              {achievements.map((achievement) => (
                <div key={achievement.id} className={`p-4 rounded-lg border transition-all ${
                  achievement.unlocked 
                    ? 'bg-yellow-50 border-yellow-200' 
                    : 'bg-gray-50 border-gray-200 opacity-60'
                }`}>
                  <div className="flex items-center mb-2">
                    <span className="text-2xl mr-3">{achievement.icon}</span>
                    <div className="flex-1">
                      <h4 className={`font-medium ${
                        achievement.unlocked ? 'text-yellow-900' : 'text-gray-600'
                      }`}>
                        {achievement.title}
                      </h4>
                      {achievement.unlocked && (
                        <CheckCircle className="w-4 h-4 text-yellow-600 inline ml-1" />
                      )}
                    </div>
                  </div>
                  <p className={`text-sm ${
                    achievement.unlocked ? 'text-yellow-700' : 'text-gray-500'
                  }`}>
                    {achievement.description}
                  </p>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* Recent Submissions */}
        <Card>
          <CardHeader className="flex flex-row items-center justify-between">
            <div>
              <CardTitle>Recent Submissions</CardTitle>
              <CardDescription>Your latest assignment submissions</CardDescription>
            </div>
            <Link
              to="/my-submissions"
              className="text-sm text-primary-600 hover:text-primary-700 font-medium"
            >
              View All
            </Link>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {recentSubmissions.map((submission) => (
                <div key={submission.id} className="flex items-center justify-between p-4 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors">
                  <div className="flex-1">
                    <h4 className="font-medium text-secondary-900">{submission.title}</h4>
                    <p className="text-sm text-secondary-600">{submission.course}</p>
                    <div className="flex items-center mt-2 space-x-4">
                      <p className="text-xs text-secondary-600">
                        Submitted: {new Date(submission.submittedAt).toLocaleDateString()}
                      </p>
                      <div className={`px-2 py-1 rounded-full text-xs font-medium ${
                        submission.status === 'graded' 
                          ? submission.score >= 80
                            ? 'bg-green-100 text-green-800'
                            : 'bg-yellow-100 text-yellow-800'
                          : 'bg-blue-100 text-blue-800'
                      }`}>
                        {submission.status === 'graded' ? 
                          `${submission.score}%` : 
                          'AI Review Pending'
                        }
                      </div>
                    </div>
                  </div>
                  <Link
                    to={`/submissions/${submission.id}`}
                    className="ml-4 p-2 text-secondary-400 hover:text-secondary-600 transition-colors"
                  >
                    <Eye className="w-5 h-5" />
                  </Link>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Current Courses */}
      <Card>
        <CardHeader>
          <CardTitle>Your Courses</CardTitle>
          <CardDescription>Track your progress in enrolled courses</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {courses.map((course) => (
              <div key={course.id} className="p-6 bg-gradient-to-br from-primary-50 to-primary-100 rounded-lg">
                <h3 className="font-semibold text-primary-900 text-lg">{course.title}</h3>
                <p className="text-primary-700 text-sm">{course.instructor}</p>
                
                <div className="mt-4">
                  <div className="flex justify-between text-sm text-primary-700 mb-1">
                    <span>Progress</span>
                    <span>{course.progress}%</span>
                  </div>
                  <div className="w-full bg-primary-200 rounded-full h-2">
                    <div 
                      className="bg-primary-600 h-2 rounded-full" 
                      style={{ width: `${course.progress}%` }}
                    ></div>
                  </div>
                </div>

                <div className="mt-4 flex justify-between items-center">
                  <div>
                    <p className="text-sm text-primary-600">Next Assignment:</p>
                    <p className="text-sm font-medium text-primary-900">{course.nextAssignment}</p>
                  </div>
                  <Link
                    to={`/courses/${course.id}`}
                    className="bg-primary-600 text-white px-4 py-2 rounded-md text-sm hover:bg-primary-700 transition-colors"
                  >
                    View Course
                  </Link>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  );
};