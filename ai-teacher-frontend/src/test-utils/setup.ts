/**
 * 测试环境设置文件
 * 配置全局测试环境和工具
 */

import '@testing-library/jest-dom';
import { expect, afterEach, beforeAll, afterAll } from 'vitest';
import { cleanup } from '@testing-library/react';
import { server } from './mocks/server';

// 扩展expect匹配器
expect.extend({});

// 每个测试后清理
afterEach(() => {
  cleanup();
});

// 启动mock服务器
beforeAll(() => {
  server.listen({ onUnhandledRequest: 'error' });
});

// 每个测试后重置handlers
afterEach(() => {
  server.resetHandlers();
});

// 关闭mock服务器
afterAll(() => {
  server.close();
});

// Mock window.matchMedia
Object.defineProperty(window, 'matchMedia', {
  writable: true,
  value: vi.fn().mockImplementation(query => ({
    matches: false,
    media: query,
    onchange: null,
    addListener: vi.fn(), // deprecated
    removeListener: vi.fn(), // deprecated
    addEventListener: vi.fn(),
    removeEventListener: vi.fn(),
    dispatchEvent: vi.fn(),
  })),
});

// Mock ResizeObserver
global.ResizeObserver = vi.fn().mockImplementation(() => ({
  observe: vi.fn(),
  unobserve: vi.fn(),
  disconnect: vi.fn(),
}));

// Mock IntersectionObserver
global.IntersectionObserver = vi.fn().mockImplementation(() => ({
  observe: vi.fn(),
  unobserve: vi.fn(),
  disconnect: vi.fn(),
}));

// Mock scrollTo
Object.defineProperty(window, 'scrollTo', {
  value: vi.fn(),
  writable: true
});

// Mock HTMLElement.scrollIntoView
Object.defineProperty(HTMLElement.prototype, 'scrollIntoView', {
  value: vi.fn(),
  writable: true
});

// Mock console methods for cleaner test output
const originalConsole = global.console;
global.console = {
  ...console,
  warn: vi.fn(),
  error: vi.fn(),
};

// 恢复console (如果需要)
export const restoreConsole = () => {
  global.console = originalConsole;
};

// 测试工具常量
export const TEST_IDS = {
  // 通用组件
  BUTTON: 'button',
  INPUT: 'input',
  FORM: 'form',
  MODAL: 'modal',
  ALERT: 'alert',
  LOADING: 'loading',
  
  // 导航组件
  NAVBAR: 'navbar',
  SIDEBAR: 'sidebar',
  MENU: 'menu',
  
  // 代码相关
  CODE_EDITOR: 'code-editor',
  CODE_SUBMISSION: 'code-submission',
  CODE_FEEDBACK: 'code-feedback',
  
  // 用户界面
  LOGIN_FORM: 'login-form',
  REGISTER_FORM: 'register-form',
  USER_PROFILE: 'user-profile',
  
  // 教师界面
  TEACHER_DASHBOARD: 'teacher-dashboard',
  ASSIGNMENT_LIST: 'assignment-list',
  STUDENT_LIST: 'student-list',
  
  // 学生界面
  STUDENT_DASHBOARD: 'student-dashboard',
  SUBMISSION_HISTORY: 'submission-history',
  AI_FEEDBACK: 'ai-feedback'
};

// 测试数据常量
export const TEST_DATA = {
  // 用户数据
  TEACHER: {
    id: '1',
    email: 'teacher@test.com',
    fullName: 'Test Teacher',
    role: 'teacher',
    university: 'Test University',
    department: 'Computer Science'
  },
  
  STUDENT: {
    id: '2', 
    email: 'student@test.com',
    fullName: 'Test Student',
    role: 'student',
    university: 'Test University',
    department: 'Computer Science',
    studentId: 'CS2024001'
  },
  
  // 代码数据
  C_CODE: `#include <stdio.h>
int main() {
    printf("Hello World\\n");
    return 0;
}`,
  
  PYTHON_CODE: `def hello():
    print("Hello World")

hello()`,
  
  // AI反馈数据
  AI_FEEDBACK: {
    analysis: {
      syntaxErrors: [],
      logicIssues: [],
      styleSuggestions: ['Add comments for clarity'],
      complexityScore: 2,
      correctnessScore: 95
    },
    feedback: {
      overallAssessment: 'Good basic implementation',
      strengths: ['Correct syntax', 'Proper structure'],
      improvements: ['Add error handling'],
      nextSteps: ['Learn about functions'],
      difficultyLevel: 'beginner'
    }
  }
};