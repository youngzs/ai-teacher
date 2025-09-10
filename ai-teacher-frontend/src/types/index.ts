// User Types
export interface User {
  id: string;
  email: string;
  firstName: string;
  lastName: string;
  role: UserRole;
  avatar?: string;
  createdAt: string;
  updatedAt: string;
}

export const UserRole = {
  STUDENT: 'student',
  TEACHER: 'teacher',
  ADMIN: 'admin'
} as const;

export type UserRole = typeof UserRole[keyof typeof UserRole];

// Course Types
export interface Course {
  id: string;
  title: string;
  description: string;
  teacherId: string;
  teacher: User;
  language: ProgrammingLanguage;
  semester: string;
  year: number;
  isActive: boolean;
  studentCount: number;
  assignmentCount: number;
  createdAt: string;
  updatedAt: string;
}

export const ProgrammingLanguage = {
  C: 'c',
  PYTHON: 'python'
} as const;

export type ProgrammingLanguage = typeof ProgrammingLanguage[keyof typeof ProgrammingLanguage];

// Assignment Types
export interface Assignment {
  id: string;
  courseId: string;
  course: Course;
  title: string;
  description: string;
  requirements: string;
  language: ProgrammingLanguage;
  dueDate: string;
  totalPoints: number;
  testCases?: TestCase[];
  isPublished: boolean;
  submissionCount: number;
  createdAt: string;
  updatedAt: string;
}

export interface TestCase {
  id: string;
  input: string;
  expectedOutput: string;
  isPublic: boolean;
  points: number;
}

// Submission Types
export interface Submission {
  id: string;
  assignmentId: string;
  assignment: Assignment;
  studentId: string;
  student: User;
  code: string;
  language: ProgrammingLanguage;
  status: SubmissionStatus;
  score?: number;
  maxScore: number;
  feedback?: AIFeedback;
  submittedAt: string;
  gradedAt?: string;
}

export const SubmissionStatus = {
  PENDING: 'pending',
  GRADING: 'grading',
  COMPLETED: 'completed',
  ERROR: 'error'
} as const;

export type SubmissionStatus = typeof SubmissionStatus[keyof typeof SubmissionStatus];

// AI Feedback Types
export interface AIFeedback {
  id: string;
  submissionId: string;
  overallScore: number;
  codeQuality: CodeQualityAnalysis;
  functionality: FunctionalityAnalysis;
  suggestions: Suggestion[];
  errors: CodeError[];
  isReviewed: boolean;
  teacherAdjustments?: TeacherAdjustment[];
  generatedAt: string;
}

export interface CodeQualityAnalysis {
  readability: number;
  structure: number;
  naming: number;
  comments: number;
  efficiency: number;
  bestPractices: number;
}

export interface FunctionalityAnalysis {
  correctness: number;
  completeness: number;
  testCasesPassed: number;
  totalTestCases: number;
  executionTime?: number;
  memoryUsage?: number;
}

export interface Suggestion {
  type: SuggestionType;
  severity: SeverityLevel;
  line?: number;
  column?: number;
  message: string;
  example?: string;
  explanation: string;
}

export const SuggestionType = {
  SYNTAX: 'syntax',
  LOGIC: 'logic',
  PERFORMANCE: 'performance',
  STYLE: 'style',
  BEST_PRACTICE: 'best_practice'
} as const;

export type SuggestionType = typeof SuggestionType[keyof typeof SuggestionType];

export const SeverityLevel = {
  INFO: 'info',
  WARNING: 'warning',
  ERROR: 'error',
  CRITICAL: 'critical'
} as const;

export type SeverityLevel = typeof SeverityLevel[keyof typeof SeverityLevel];

export interface CodeError {
  type: string;
  line: number;
  column: number;
  message: string;
  suggestion?: string;
}

export interface TeacherAdjustment {
  field: string;
  originalValue: any;
  adjustedValue: any;
  reason: string;
  adjustedAt: string;
}

// Student Progress Types
export interface StudentProgress {
  studentId: string;
  courseId: string;
  overallScore: number;
  assignmentsCompleted: number;
  totalAssignments: number;
  learningPath: LearningPathNode[];
  strengths: string[];
  weaknesses: string[];
  recommendations: string[];
  lastActivity: string;
}

export interface LearningPathNode {
  concept: string;
  mastery: number;
  practiceCount: number;
  lastPracticed?: string;
}

// API Response Types
export interface ApiResponse<T> {
  success: boolean;
  data?: T;
  message?: string;
  errors?: string[];
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  pageSize: number;
  totalPages: number;
}

// Form Types
export interface LoginForm {
  email: string;
  password: string;
}

export interface RegisterForm {
  email: string;
  password: string;
  confirmPassword: string;
  firstName: string;
  lastName: string;
  role: UserRole;
}

export interface CreateCourseForm {
  title: string;
  description: string;
  language: ProgrammingLanguage;
  semester: string;
  year: number;
}

export interface CreateAssignmentForm {
  title: string;
  description: string;
  requirements: string;
  language: ProgrammingLanguage;
  dueDate: string;
  totalPoints: number;
  testCases: Omit<TestCase, 'id'>[];
}

// UI State Types
export interface LoadingState {
  isLoading: boolean;
  message?: string;
}

export interface ErrorState {
  hasError: boolean;
  message?: string;
  details?: any;
}

// Navigation Types
export interface NavItem {
  name: string;
  href: string;
  icon?: React.ComponentType<any>;
  current?: boolean;
  children?: NavItem[];
}

// Dashboard Types
export interface DashboardStats {
  totalStudents: number;
  totalCourses: number;
  totalAssignments: number;
  averageScore: number;
  recentActivity: ActivityItem[];
}

export interface ActivityItem {
  id: string;
  type: 'submission' | 'assignment' | 'course' | 'feedback';
  description: string;
  user: User;
  timestamp: string;
  metadata?: Record<string, any>;
}

// Code Editor Types
export interface EditorConfig {
  language: string;
  theme: 'light' | 'dark';
  fontSize: number;
  tabSize: number;
  wordWrap: boolean;
  lineNumbers: boolean;
  minimap: boolean;
}

export interface CodeFile {
  name: string;
  content: string;
  language: string;
}

// UI Component Props Types
export interface ButtonProps {
  variant?: 'primary' | 'secondary' | 'success' | 'warning' | 'danger' | 'ghost' | 'outline';
  size?: 'sm' | 'md' | 'lg';
  disabled?: boolean;
  loading?: boolean;
  children: React.ReactNode;
  onClick?: (e: React.MouseEvent<HTMLButtonElement>) => void;
  type?: 'button' | 'submit' | 'reset';
  className?: string;
  fullWidth?: boolean;
}

export interface InputProps {
  label?: string;
  placeholder?: string;
  type?: 'text' | 'email' | 'password' | 'number' | 'textarea' | 'search';
  value?: string;
  onChange?: (value: string) => void;
  onBlur?: () => void;
  onFocus?: () => void;
  error?: string;
  disabled?: boolean;
  required?: boolean;
  className?: string;
  rows?: number; // for textarea
  maxLength?: number;
}

export interface CardProps {
  title?: string;
  children: React.ReactNode;
  className?: string;
  actions?: React.ReactNode;
  padding?: 'none' | 'sm' | 'md' | 'lg';
  shadow?: 'none' | 'sm' | 'md' | 'lg';
  hover?: boolean;
}

export interface ModalProps {
  isOpen: boolean;
  onClose: () => void;
  title?: string;
  children: React.ReactNode;
  size?: 'sm' | 'md' | 'lg' | 'xl' | 'full';
  closeOnOverlayClick?: boolean;
  closeOnEsc?: boolean;
  showCloseButton?: boolean;
  footer?: React.ReactNode;
  className?: string;
}

export interface AlertProps {
  type: 'success' | 'error' | 'warning' | 'info';
  message: string;
  title?: string;
  dismissible?: boolean;
  onDismiss?: () => void;
  className?: string;
  icon?: boolean;
  actions?: React.ReactNode;
}

export interface LoadingProps {
  size?: 'sm' | 'md' | 'lg';
  color?: string;
  text?: string;
  overlay?: boolean;
  className?: string;
  fullscreen?: boolean;
}

export interface TableColumn<T = any> {
  key: string;
  title: string;
  dataIndex: keyof T;
  render?: (value: any, record: T, index: number) => React.ReactNode;
  sortable?: boolean;
  width?: string | number;
  align?: 'left' | 'center' | 'right';
  fixed?: 'left' | 'right';
}

export interface TableProps<T = any> {
  columns: TableColumn<T>[];
  data: T[];
  loading?: boolean;
  pagination?: {
    current: number;
    pageSize: number;
    total: number;
    onChange: (page: number, pageSize: number) => void;
    showSizeChanger?: boolean;
    pageSizeOptions?: number[];
  };
  onSort?: (key: string, direction: 'asc' | 'desc') => void;
  className?: string;
  rowSelection?: {
    selectedRowKeys: string[];
    onChange: (selectedRowKeys: string[], selectedRows: T[]) => void;
  };
  emptyText?: string;
}

export interface FormProps {
  onSubmit: (values: Record<string, any>) => void;
  initialValues?: Record<string, any>;
  children: React.ReactNode;
  className?: string;
  loading?: boolean;
}

export interface BreadcrumbItem {
  label: string;
  href?: string;
  current?: boolean;
}

export interface BreadcrumbProps {
  items: BreadcrumbItem[];
  className?: string;
}

// Theme and App State Types
export interface AppTheme {
  mode: 'light' | 'dark';
  primaryColor: string;
  fontFamily: string;
  fontSize: 'sm' | 'md' | 'lg';
}

export interface GlobalState {
  theme: AppTheme;
  loading: boolean;
  error: string | null;
  notifications: NotificationItem[];
  sidebarOpen: boolean;
  user: User | null;
  isAuthenticated: boolean;
}

export interface NotificationItem {
  id: string;
  type: 'success' | 'error' | 'warning' | 'info';
  title?: string;
  message: string;
  duration?: number;
  timestamp: string;
  read?: boolean;
}

// Route Configuration Types
export interface RouteConfig {
  path: string;
  component: React.ComponentType;
  exact?: boolean;
  protected?: boolean;
  roles?: UserRole[];
  title: string;
  breadcrumb?: string;
  icon?: React.ComponentType;
}