import type { 
  User, 
  Course, 
  Assignment, 
  Submission, 
  LoginForm, 
  RegisterForm,
  CreateCourseForm,
  CreateAssignmentForm,
  ApiResponse,
  PaginatedResponse 
} from '../types';
import { getErrorMessage } from '../utils';

// API Configuration
const API_CONFIG = {
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
};

// HTTP Client
class ApiClient {
  private baseURL: string;
  private defaultHeaders: Record<string, string>;

  constructor(config: typeof API_CONFIG) {
    this.baseURL = config.baseURL;
    this.defaultHeaders = config.headers;
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<ApiResponse<T>> {
    const url = `${this.baseURL}/api/v1${endpoint}`;
    const token = localStorage.getItem('auth-token');

    const config: RequestInit = {
      ...options,
      headers: {
        ...this.defaultHeaders,
        ...options.headers,
        ...(token && { Authorization: `Bearer ${token}` }),
      },
    };

    try {
      const response = await fetch(url, config);
      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.message || `HTTP Error: ${response.status}`);
      }

      return {
        success: true,
        data: data.data || data,
        message: data.message,
      };
    } catch (error) {
      return {
        success: false,
        message: getErrorMessage(error),
        errors: [getErrorMessage(error)],
      };
    }
  }

  async get<T>(endpoint: string): Promise<ApiResponse<T>> {
    return this.request<T>(endpoint, { method: 'GET' });
  }

  async post<T>(endpoint: string, data?: any): Promise<ApiResponse<T>> {
    return this.request<T>(endpoint, {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async put<T>(endpoint: string, data?: any): Promise<ApiResponse<T>> {
    return this.request<T>(endpoint, {
      method: 'PUT',
      body: JSON.stringify(data),
    });
  }

  async patch<T>(endpoint: string, data?: any): Promise<ApiResponse<T>> {
    return this.request<T>(endpoint, {
      method: 'PATCH',
      body: JSON.stringify(data),
    });
  }

  async delete<T>(endpoint: string): Promise<ApiResponse<T>> {
    return this.request<T>(endpoint, { method: 'DELETE' });
  }

  async upload<T>(endpoint: string, formData: FormData): Promise<ApiResponse<T>> {
    return this.request<T>(endpoint, {
      method: 'POST',
      body: formData,
      headers: {}, // Let browser set Content-Type for FormData
    });
  }
}

// Create API client instance
const apiClient = new ApiClient(API_CONFIG);

// Authentication API
export const authAPI = {
  login: (credentials: LoginForm) => 
    apiClient.post<{ user: User; token: string }>('/auth/login', credentials),
    
  register: (userData: RegisterForm) => 
    apiClient.post<{ user: User; token: string }>('/auth/register', userData),
    
  logout: () => 
    apiClient.post('/auth/logout'),
    
  refreshToken: () => 
    apiClient.post<{ token: string }>('/auth/refresh'),
    
  forgotPassword: (email: string) => 
    apiClient.post('/auth/forgot-password', { email }),
    
  resetPassword: (token: string, password: string) => 
    apiClient.post('/auth/reset-password', { token, password }),
    
  verifyEmail: (token: string) => 
    apiClient.post('/auth/verify-email', { token }),
    
  getCurrentUser: () => 
    apiClient.get<User>('/auth/me'),
};

// User API
export const userAPI = {
  getProfile: () => 
    apiClient.get<User>('/users/profile'),
    
  updateProfile: (userData: Partial<User>) => 
    apiClient.put<User>('/users/profile', userData),
    
  uploadAvatar: (file: File) => {
    const formData = new FormData();
    formData.append('avatar', file);
    return apiClient.upload<{ avatarUrl: string }>('/users/avatar', formData);
  },
  
  changePassword: (oldPassword: string, newPassword: string) => 
    apiClient.post('/users/change-password', { oldPassword, newPassword }),
};

// Course API
export const courseAPI = {
  getCourses: (params?: { page?: number; limit?: number; search?: string }) => 
    apiClient.get<PaginatedResponse<Course>>('/courses' + (params ? `?${new URLSearchParams(params as any)}` : '')),
    
  getCourse: (id: string) => 
    apiClient.get<Course>(`/courses/${id}`),
    
  createCourse: (courseData: CreateCourseForm) => 
    apiClient.post<Course>('/courses', courseData),
    
  updateCourse: (id: string, courseData: Partial<Course>) => 
    apiClient.put<Course>(`/courses/${id}`, courseData),
    
  deleteCourse: (id: string) => 
    apiClient.delete(`/courses/${id}`),
    
  getStudents: (courseId: string) => 
    apiClient.get<User[]>(`/courses/${courseId}/students`),
    
  addStudent: (courseId: string, studentEmail: string) => 
    apiClient.post(`/courses/${courseId}/students`, { email: studentEmail }),
    
  removeStudent: (courseId: string, studentId: string) => 
    apiClient.delete(`/courses/${courseId}/students/${studentId}`),
    
  getCourseStats: (courseId: string) => 
    apiClient.get<{
      totalStudents: number;
      totalAssignments: number;
      averageScore: number;
      completionRate: number;
    }>(`/courses/${courseId}/stats`),
};

// Assignment API
export const assignmentAPI = {
  getAssignments: (courseId: string) => 
    apiClient.get<Assignment[]>(`/courses/${courseId}/assignments`),
    
  getAssignment: (id: string) => 
    apiClient.get<Assignment>(`/assignments/${id}`),
    
  createAssignment: (courseId: string, assignmentData: CreateAssignmentForm) => 
    apiClient.post<Assignment>(`/courses/${courseId}/assignments`, assignmentData),
    
  updateAssignment: (id: string, assignmentData: Partial<Assignment>) => 
    apiClient.put<Assignment>(`/assignments/${id}`, assignmentData),
    
  deleteAssignment: (id: string) => 
    apiClient.delete(`/assignments/${id}`),
    
  publishAssignment: (id: string) => 
    apiClient.post(`/assignments/${id}/publish`),
    
  unpublishAssignment: (id: string) => 
    apiClient.post(`/assignments/${id}/unpublish`),
    
  getSubmissions: (assignmentId: string) => 
    apiClient.get<Submission[]>(`/assignments/${assignmentId}/submissions`),
};

// Submission API
export const submissionAPI = {
  getSubmission: (id: string) => 
    apiClient.get<Submission>(`/submissions/${id}`),
    
  createSubmission: (assignmentId: string, code: string) => 
    apiClient.post<Submission>(`/assignments/${assignmentId}/submit`, { code }),
    
  updateSubmission: (id: string, code: string) => 
    apiClient.put<Submission>(`/submissions/${id}`, { code }),
    
  getMySubmissions: (assignmentId?: string) => 
    apiClient.get<Submission[]>(`/submissions/my${assignmentId ? `?assignmentId=${assignmentId}` : ''}`),
    
  runCode: (code: string, language: string, testCases?: any[]) => 
    apiClient.post<{
      output: string;
      errors: string[];
      executionTime: number;
      memoryUsage: number;
      testResults?: any[];
    }>('/submissions/run', { code, language, testCases }),
    
  uploadFile: (assignmentId: string, file: File) => {
    const formData = new FormData();
    formData.append('file', file);
    return apiClient.upload<Submission>(`/assignments/${assignmentId}/upload`, formData);
  },
};

// Feedback API
export const feedbackAPI = {
  getFeedback: (submissionId: string) => 
    apiClient.get<any>(`/submissions/${submissionId}/feedback`),
    
  updateFeedback: (submissionId: string, adjustments: any) => 
    apiClient.put(`/submissions/${submissionId}/feedback`, adjustments),
    
  approveFeedback: (submissionId: string) => 
    apiClient.post(`/submissions/${submissionId}/feedback/approve`),
    
  regenerateFeedback: (submissionId: string) => 
    apiClient.post(`/submissions/${submissionId}/feedback/regenerate`),
};

// Analytics API
export const analyticsAPI = {
  getDashboardStats: () => 
    apiClient.get<{
      totalCourses: number;
      totalStudents: number;
      totalAssignments: number;
      averageScore: number;
      recentActivity: any[];
    }>('/analytics/dashboard'),
    
  getCourseAnalytics: (courseId: string) => 
    apiClient.get<any>(`/analytics/courses/${courseId}`),
    
  getStudentProgress: (studentId: string, courseId?: string) => 
    apiClient.get<any>(`/analytics/students/${studentId}${courseId ? `?courseId=${courseId}` : ''}`),
    
  getAssignmentAnalytics: (assignmentId: string) => 
    apiClient.get<any>(`/analytics/assignments/${assignmentId}`),
};

// Export default API object
export const api = {
  auth: authAPI,
  user: userAPI,
  course: courseAPI,
  assignment: assignmentAPI,
  submission: submissionAPI,
  feedback: feedbackAPI,
  analytics: analyticsAPI,
};