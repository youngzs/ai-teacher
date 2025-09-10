import { create } from 'zustand';
import type { Course, Assignment, Submission, LoadingState, ErrorState } from '../types';

interface AppState {
  // UI State
  sidebarOpen: boolean;
  theme: 'light' | 'dark' | 'system';
  notifications: Notification[];
  
  // Data State
  courses: Course[];
  assignments: Assignment[];
  submissions: Submission[];
  
  // Loading States
  coursesLoading: LoadingState;
  assignmentsLoading: LoadingState;
  submissionsLoading: LoadingState;
  
  // Error States
  coursesError: ErrorState;
  assignmentsError: ErrorState;
  submissionsError: ErrorState;
  
  // Actions
  toggleSidebar: () => void;
  setTheme: (theme: 'light' | 'dark' | 'system') => void;
  addNotification: (notification: Omit<Notification, 'id' | 'timestamp'>) => void;
  removeNotification: (id: string) => void;
  clearNotifications: () => void;
  
  // Data Actions
  setCourses: (courses: Course[]) => void;
  addCourse: (course: Course) => void;
  updateCourse: (id: string, updates: Partial<Course>) => void;
  removeCourse: (id: string) => void;
  
  setAssignments: (assignments: Assignment[]) => void;
  addAssignment: (assignment: Assignment) => void;
  updateAssignment: (id: string, updates: Partial<Assignment>) => void;
  removeAssignment: (id: string) => void;
  
  setSubmissions: (submissions: Submission[]) => void;
  addSubmission: (submission: Submission) => void;
  updateSubmission: (id: string, updates: Partial<Submission>) => void;
  
  // Loading Actions
  setCoursesLoading: (state: LoadingState) => void;
  setAssignmentsLoading: (state: LoadingState) => void;
  setSubmissionsLoading: (state: LoadingState) => void;
  
  // Error Actions
  setCoursesError: (error: ErrorState) => void;
  setAssignmentsError: (error: ErrorState) => void;
  setSubmissionsError: (error: ErrorState) => void;
  clearErrors: () => void;
}

interface Notification {
  id: string;
  type: 'info' | 'success' | 'warning' | 'error';
  title: string;
  message: string;
  duration?: number;
  timestamp: string;
}

export const useAppStore = create<AppState>((set, get) => ({
  // Initial UI State
  sidebarOpen: true,
  theme: 'system',
  notifications: [],
  
  // Initial Data State
  courses: [],
  assignments: [],
  submissions: [],
  
  // Initial Loading States
  coursesLoading: { isLoading: false },
  assignmentsLoading: { isLoading: false },
  submissionsLoading: { isLoading: false },
  
  // Initial Error States
  coursesError: { hasError: false },
  assignmentsError: { hasError: false },
  submissionsError: { hasError: false },

  // UI Actions
  toggleSidebar: () => set((state) => ({ sidebarOpen: !state.sidebarOpen })),
  
  setTheme: (theme) => {
    set({ theme });
    // Apply theme to document
    const root = document.documentElement;
    if (theme === 'dark' || (theme === 'system' && window.matchMedia('(prefers-color-scheme: dark)').matches)) {
      root.classList.add('dark');
    } else {
      root.classList.remove('dark');
    }
  },
  
  addNotification: (notification) => {
    const id = Math.random().toString(36).substr(2, 9);
    const newNotification: Notification = {
      ...notification,
      id,
      timestamp: new Date().toISOString()
    };
    
    set((state) => ({
      notifications: [...state.notifications, newNotification]
    }));
    
    // Auto-remove notification after duration
    if (notification.duration !== 0) {
      setTimeout(() => {
        get().removeNotification(id);
      }, notification.duration || 5000);
    }
  },
  
  removeNotification: (id) =>
    set((state) => ({
      notifications: state.notifications.filter((n) => n.id !== id)
    })),
    
  clearNotifications: () => set({ notifications: [] }),

  // Course Actions
  setCourses: (courses) => set({ courses }),
  
  addCourse: (course) =>
    set((state) => ({ courses: [...state.courses, course] })),
    
  updateCourse: (id, updates) =>
    set((state) => ({
      courses: state.courses.map((course) =>
        course.id === id ? { ...course, ...updates } : course
      )
    })),
    
  removeCourse: (id) =>
    set((state) => ({
      courses: state.courses.filter((course) => course.id !== id)
    })),

  // Assignment Actions
  setAssignments: (assignments) => set({ assignments }),
  
  addAssignment: (assignment) =>
    set((state) => ({ assignments: [...state.assignments, assignment] })),
    
  updateAssignment: (id, updates) =>
    set((state) => ({
      assignments: state.assignments.map((assignment) =>
        assignment.id === id ? { ...assignment, ...updates } : assignment
      )
    })),
    
  removeAssignment: (id) =>
    set((state) => ({
      assignments: state.assignments.filter((assignment) => assignment.id !== id)
    })),

  // Submission Actions
  setSubmissions: (submissions) => set({ submissions }),
  
  addSubmission: (submission) =>
    set((state) => ({ submissions: [...state.submissions, submission] })),
    
  updateSubmission: (id, updates) =>
    set((state) => ({
      submissions: state.submissions.map((submission) =>
        submission.id === id ? { ...submission, ...updates } : submission
      )
    })),

  // Loading Actions
  setCoursesLoading: (state) => set({ coursesLoading: state }),
  setAssignmentsLoading: (state) => set({ assignmentsLoading: state }),
  setSubmissionsLoading: (state) => set({ submissionsLoading: state }),

  // Error Actions
  setCoursesError: (error) => set({ coursesError: error }),
  setAssignmentsError: (error) => set({ assignmentsError: error }),
  setSubmissionsError: (error) => set({ submissionsError: error }),
  
  clearErrors: () =>
    set({
      coursesError: { hasError: false },
      assignmentsError: { hasError: false },
      submissionsError: { hasError: false }
    })
}));