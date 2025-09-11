import React from 'react';
import { NavLink, useLocation } from 'react-router-dom';
import { useAuthStore } from '../../store/authStore';
import {
  Home,
  BookOpen,
  FileText,
  Users,
  BarChart3,
  Settings,
  User,
  GraduationCap,
  ClipboardList,
  TrendingUp,
  MessageSquare
} from 'lucide-react';

const Sidebar: React.FC = () => {
  const { user } = useAuthStore();
  const location = useLocation();

  const isTeacher = user?.role === 'teacher';
  const isStudent = user?.role === 'student';

  const teacherNavItems = [
    { name: 'Dashboard', href: '/teacher/dashboard', icon: Home },
    { name: 'Courses', href: '/teacher/courses', icon: BookOpen },
    { name: 'Assignments', href: '/teacher/assignments', icon: FileText },
    { name: 'Students', href: '/teacher/students', icon: Users },
    { name: 'Analytics', href: '/teacher/analytics', icon: BarChart3 },
  ];

  const studentNavItems = [
    { name: 'Dashboard', href: '/student/dashboard', icon: Home },
    { name: 'Assignments', href: '/student/assignments', icon: ClipboardList },
    { name: 'Progress', href: '/student/progress', icon: TrendingUp },
    { name: 'Feedback', href: '/student/feedback', icon: MessageSquare },
  ];

  const commonNavItems = [
    { name: 'Profile', href: '/profile', icon: User },
    { name: 'Settings', href: '/settings', icon: Settings },
  ];

  const navItems = isTeacher ? teacherNavItems : isStudent ? studentNavItems : [];

  return (
    <div className="hidden lg:flex lg:flex-shrink-0">
      <div className="flex flex-col w-64">
        <div className="flex flex-col flex-grow pt-5 pb-4 overflow-y-auto bg-white border-r border-secondary-200">
          <nav className="mt-5 flex-1 px-2 space-y-1">
            {navItems.map((item) => {
              const isActive = location.pathname.startsWith(item.href);
              return (
                <NavLink
                  key={item.name}
                  to={item.href}
                  className={`group flex items-center px-2 py-2 text-sm font-medium rounded-md transition-colors ${
                    isActive
                      ? 'bg-primary-100 text-primary-900'
                      : 'text-secondary-600 hover:bg-secondary-50 hover:text-secondary-900'
                  }`}
                >
                  <item.icon
                    className={`mr-3 flex-shrink-0 h-5 w-5 ${
                      isActive ? 'text-primary-500' : 'text-secondary-400 group-hover:text-secondary-500'
                    }`}
                  />
                  {item.name}
                </NavLink>
              );
            })}

            {/* Divider */}
            <div className="border-t border-secondary-200 my-4"></div>

            {commonNavItems.map((item) => {
              const isActive = location.pathname === item.href;
              return (
                <NavLink
                  key={item.name}
                  to={item.href}
                  className={`group flex items-center px-2 py-2 text-sm font-medium rounded-md transition-colors ${
                    isActive
                      ? 'bg-primary-100 text-primary-900'
                      : 'text-secondary-600 hover:bg-secondary-50 hover:text-secondary-900'
                  }`}
                >
                  <item.icon
                    className={`mr-3 flex-shrink-0 h-5 w-5 ${
                      isActive ? 'text-primary-500' : 'text-secondary-400 group-hover:text-secondary-500'
                    }`}
                  />
                  {item.name}
                </NavLink>
              );
            })}
          </nav>
        </div>
      </div>
    </div>
  );
};

export default Sidebar;
