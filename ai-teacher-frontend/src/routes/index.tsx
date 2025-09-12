import React from 'react';
import { createBrowserRouter, RouterProvider, Navigate } from 'react-router-dom';
import { useAuthStore } from '../store/authStore';

// Layout Components
import RootLayout from '../components/layout/RootLayout';
import AuthLayout from '../components/layout/AuthLayout';
import ProtectedRoute from '../components/layout/ProtectedRoute';

// Pages
import LoginPage from '../pages/auth/LoginPage';
import RegisterPage from '../pages/auth/RegisterPage';
import DashboardPage from '../pages/dashboard/DashboardPage';
import ProfilePage from '../pages/profile/ProfilePage';

// Teacher Pages
import TeacherDashboard from '../pages/teacher/TeacherDashboard';
import CourseManagement from '../pages/teacher/CourseManagement';
import AssignmentManagement from '../pages/teacher/AssignmentManagement';
import StudentProgress from '../pages/teacher/StudentProgress';
import AnalyticsPage from '../pages/teacher/AnalyticsPage';

// Student Pages
import StudentDashboard from '../pages/student/StudentDashboard';
import AssignmentList from '../pages/student/AssignmentList';
import AssignmentSubmission from '../pages/student/AssignmentSubmission';
import ProgressTracker from '../pages/student/ProgressTracker';
import FeedbackHistory from '../pages/student/FeedbackHistory';

// Error Pages
import NotFoundPage from '../pages/error/NotFoundPage';
import UnauthorizedPage from '../pages/error/UnauthorizedPage';

// Development Pages  
import { ApiTestPage } from '../pages/ApiTestPage';

const router = createBrowserRouter([
  {
    path: '/',
    element: <RootLayout />,
    errorElement: <NotFoundPage />,
    children: [
      // Public routes
      {
        index: true,
        element: <Navigate to="/dashboard" replace />,
      },
      
      // Auth routes
      {
        path: 'auth',
        element: <AuthLayout />,
        children: [
          {
            path: 'login',
            element: <LoginPage />,
          },
          {
            path: 'register',
            element: <RegisterPage />,
          },
        ],
      },

      // Protected routes
      {
        path: 'dashboard',
        element: <ProtectedRoute />,
        children: [
          {
            index: true,
            element: <DashboardPage />,
          },
        ],
      },

      {
        path: 'profile',
        element: <ProtectedRoute />,
        children: [
          {
            index: true,
            element: <ProfilePage />,
          },
        ],
      },

      // Teacher routes
      {
        path: 'teacher',
        element: <ProtectedRoute requiredRole="teacher" />,
        children: [
          {
            index: true,
            element: <Navigate to="/teacher/dashboard" replace />,
          },
          {
            path: 'dashboard',
            element: <TeacherDashboard />,
          },
          {
            path: 'courses',
            children: [
              {
                index: true,
                element: <CourseManagement />,
              },
              {
                path: ':courseId',
                element: <CourseManagement />,
              },
            ],
          },
          {
            path: 'assignments',
            children: [
              {
                index: true,
                element: <AssignmentManagement />,
              },
              {
                path: ':assignmentId',
                element: <AssignmentManagement />,
              },
            ],
          },
          {
            path: 'students',
            element: <StudentProgress />,
          },
          {
            path: 'analytics',
            element: <AnalyticsPage />,
          },
        ],
      },

      // Student routes
      {
        path: 'student',
        element: <ProtectedRoute requiredRole="student" />,
        children: [
          {
            index: true,
            element: <Navigate to="/student/dashboard" replace />,
          },
          {
            path: 'dashboard',
            element: <StudentDashboard />,
          },
          {
            path: 'assignments',
            children: [
              {
                index: true,
                element: <AssignmentList />,
              },
              {
                path: ':assignmentId',
                children: [
                  {
                    index: true,
                    element: <AssignmentSubmission />,
                  },
                  {
                    path: 'submit',
                    element: <AssignmentSubmission />,
                  },
                ],
              },
            ],
          },
          {
            path: 'progress',
            element: <ProgressTracker />,
          },
          {
            path: 'feedback',
            element: <FeedbackHistory />,
          },
        ],
      },

      // Development routes (only in dev mode)
      ...(import.meta.env.DEV ? [{
        path: 'api-test',
        element: <ApiTestPage />,
      }] : []),

      // Error routes
      {
        path: 'unauthorized',
        element: <UnauthorizedPage />,
      },
      {
        path: '*',
        element: <NotFoundPage />,
      },
    ],
  },
]);

export const AppRouter: React.FC = () => {
  return <RouterProvider router={router} />;
};

export default AppRouter;