import { useMemo } from 'react';
import { useLocation } from 'react-router-dom';
import type { BreadcrumbItem } from '../types';

// Route title mapping
const routeTitles: Record<string, string> = {
  '/dashboard': 'Dashboard',
  '/profile': 'Profile',
  
  // Teacher routes
  '/teacher': 'Teacher',
  '/teacher/dashboard': 'Dashboard',
  '/teacher/courses': 'Courses',
  '/teacher/assignments': 'Assignments',
  '/teacher/students': 'Student Progress',
  '/teacher/analytics': 'Analytics',
  
  // Student routes
  '/student': 'Student',
  '/student/dashboard': 'Dashboard',
  '/student/assignments': 'Assignments',
  '/student/progress': 'Progress',
  '/student/feedback': 'Feedback History',
  
  // Common paths
  '/auth/login': 'Login',
  '/auth/register': 'Register',
};

export const useBreadcrumbs = (): BreadcrumbItem[] => {
  const location = useLocation();

  return useMemo(() => {
    const pathSegments = location.pathname.split('/').filter(Boolean);
    
    // Don't show breadcrumbs for auth routes
    if (pathSegments[0] === 'auth') {
      return [];
    }

    const breadcrumbs: BreadcrumbItem[] = [
      {
        label: 'Home',
        href: '/dashboard',
        current: false,
      },
    ];

    let currentPath = '';
    
    pathSegments.forEach((segment, index) => {
      currentPath += `/${segment}`;
      const isLast = index === pathSegments.length - 1;
      
      // Skip if this is a dynamic route parameter (like IDs)
      if (/^[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}$/i.test(segment)) {
        return;
      }
      
      const title = routeTitles[currentPath] || segment.charAt(0).toUpperCase() + segment.slice(1);
      
      breadcrumbs.push({
        label: title,
        href: isLast ? undefined : currentPath,
        current: isLast,
      });
    });

    // Remove home if it's the current page
    if (breadcrumbs.length > 1 && breadcrumbs[breadcrumbs.length - 1].href === '/dashboard') {
      return breadcrumbs.slice(1);
    }

    return breadcrumbs.slice(1); // Remove home from breadcrumbs since it's in the navigation
  }, [location.pathname]);
};