import axios, { AxiosInstance, AxiosResponse, AxiosError } from 'axios';
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
  aiBaseURL: import.meta.env.VITE_AI_API_BASE_URL || 'http://localhost:8001',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
};

// HTTP Client using Axios
class ApiClient {
  private client: AxiosInstance;
  private aiClient: AxiosInstance;

  constructor(config: typeof API_CONFIG) {
    // Main API client
    this.client = axios.create({
      baseURL: `${config.baseURL}/api/v1`,
      timeout: config.timeout,
      headers: config.headers,
    });

    // AI API client
    this.aiClient = axios.create({
      baseURL: `${config.aiBaseURL}/api/v1`,
      timeout: 30000, // AI operations may take longer
      headers: config.headers,
    });

    this.setupInterceptors(this.client);
    this.setupInterceptors(this.aiClient);
  }

  private setupInterceptors(client: AxiosInstance) {
    // Request interceptor - add auth token
    client.interceptors.request.use(
      (config) => {
        const token = localStorage.getItem('auth-token');
        if (token) {
          config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
      },
      (error) => Promise.reject(error)
    );

    // Response interceptor - handle common errors
    client.interceptors.response.use(
      (response: AxiosResponse) => response,
      (error: AxiosError) => {
        if (error.response?.status === 401) {
          // Unauthorized - clear token and redirect to login
          localStorage.removeItem('auth-token');
          window.location.href = '/login';
        }
        return Promise.reject(error);
      }
    );
  }

  private handleResponse<T>(response: AxiosResponse): ApiResponse<T> {
    return {
      success: true,
      data: response.data.data || response.data,
      message: response.data.message,
    };
  }

  private handleError(error: any): ApiResponse<never> {
    if (axios.isAxiosError(error)) {
      const message = error.response?.data?.message || error.message;
      return {
        success: false,
        message,
        errors: [message],
      };
    }
    
    const message = getErrorMessage(error);
    return {
      success: false,
      message,
      errors: [message],
    };
  }

  async get<T>(endpoint: string, useAI = false): Promise<ApiResponse<T>> {
    try {
      const client = useAI ? this.aiClient : this.client;
      const response = await client.get(endpoint);
      return this.handleResponse<T>(response);
    } catch (error) {
      return this.handleError(error);
    }
  }

  async post<T>(endpoint: string, data?: any, useAI = false): Promise<ApiResponse<T>> {
    try {
      const client = useAI ? this.aiClient : this.client;
      const response = await client.post(endpoint, data);
      return this.handleResponse<T>(response);
    } catch (error) {
      return this.handleError(error);
    }
  }

  async put<T>(endpoint: string, data?: any, useAI = false): Promise<ApiResponse<T>> {
    try {
      const client = useAI ? this.aiClient : this.client;
      const response = await client.put(endpoint, data);
      return this.handleResponse<T>(response);
    } catch (error) {
      return this.handleError(error);
    }
  }

  async patch<T>(endpoint: string, data?: any, useAI = false): Promise<ApiResponse<T>> {
    try {
      const client = useAI ? this.aiClient : this.client;
      const response = await client.patch(endpoint, data);
      return this.handleResponse<T>(response);
    } catch (error) {
      return this.handleError(error);
    }
  }

  async delete<T>(endpoint: string, useAI = false): Promise<ApiResponse<T>> {
    try {
      const client = useAI ? this.aiClient : this.client;
      const response = await client.delete(endpoint);
      return this.handleResponse<T>(response);
    } catch (error) {
      return this.handleError(error);
    }
  }

  async upload<T>(endpoint: string, formData: FormData, useAI = false): Promise<ApiResponse<T>> {
    try {
      const client = useAI ? this.aiClient : this.client;
      const response = await client.post(endpoint, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      return this.handleResponse<T>(response);
    } catch (error) {
      return this.handleError(error);
    }
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
    
  // AI-powered code analysis and feedback
  analyzeCode: (code: string, language: string, assignmentId?: string) =>
    apiClient.post<{
      feedback: any;
      suggestions: string[];
      errors: any[];
      score: number;
    }>('/ai/analyze-code', { code, language, assignmentId }, true),
    
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

// System Health API
export const systemAPI = {
  healthCheck: () => 
    apiClient.get<{ status: string; timestamp: string; version: string }>('/health'),
    
  aiHealthCheck: () => 
    apiClient.get<{ status: string; timestamp: string; version: string }>('/health', true),
};

// AI Services API
export const aiAPI = {
  analyzeCode: (code: string, language: string, assignmentContext?: any) =>
    apiClient.post<{
      feedback: any;
      suggestions: string[];
      errors: any[];
      score: number;
      improvements: string[];
    }>('/ai/analyze', { code, language, assignmentContext }, true),
    
  generateFeedback: (submissionId: string, analysisData: any) =>
    apiClient.post<{
      feedback: string;
      strengths: string[];
      improvements: string[];
      nextSteps: string[];
    }>('/ai/feedback', { submissionId, analysisData }, true),
    
  gradeSubmission: (submissionId: string, rubric?: any) =>
    apiClient.post<{
      score: number;
      breakdown: Record<string, number>;
      feedback: string;
      suggestions: string[];
    }>('/ai/grade', { submissionId, rubric }, true),
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
  system: systemAPI,
  ai: aiAPI,
};