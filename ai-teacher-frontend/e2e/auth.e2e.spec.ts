/**
 * 认证流程端到端测试
 * 测试用户登录、注册、权限控制等认证相关功能
 */

import { test, expect } from '@playwright/test';

// 测试数据
const TEST_USERS = {
  teacher: {
    email: 'e2e.teacher@university.edu',
    password: 'E2ETestPassword123!',
    fullName: 'E2E Test Teacher',
    role: 'teacher'
  },
  student: {
    email: 'e2e.student@university.edu',
    password: 'E2ETestPassword123!',
    fullName: 'E2E Test Student',
    role: 'student'
  },
  newUser: {
    email: `e2e.new.${Date.now()}@university.edu`,
    password: 'NewUserPassword123!',
    fullName: 'E2E New User',
    role: 'student',
    university: 'E2E Test University',
    department: 'Computer Science'
  }
};

test.describe('Authentication Flow', () => {
  
  test.beforeEach(async ({ page }) => {
    // 每个测试前清除本地存储
    await page.goto('/');
    await page.evaluate(() => {
      localStorage.clear();
      sessionStorage.clear();
    });
  });
  
  test('should display login page correctly', async ({ page }) => {
    await page.goto('/login');
    
    // 验证页面标题和元素
    await expect(page).toHaveTitle(/AI Teaching Assistant/);
    await expect(page.locator('h1')).toContainText('AI Teaching Assistant');
    
    // 验证表单元素存在
    await expect(page.locator('input[type="email"]')).toBeVisible();
    await expect(page.locator('input[type="password"]')).toBeVisible();
    await expect(page.locator('button[type="submit"]')).toBeVisible();
    
    // 验证导航链接
    await expect(page.locator('a[href="/register"]')).toContainText('Sign up');
    await expect(page.locator('a[href="/forgot-password"]')).toContainText('Forgot');
  });
  
  test('should show validation errors for invalid inputs', async ({ page }) => {
    await page.goto('/login');
    
    // 尝试提交空表单
    await page.click('button[type="submit"]');
    
    // 验证HTML5表单验证或自定义验证
    const emailInput = page.locator('input[type="email"]');
    const passwordInput = page.locator('input[type="password"]');
    
    await expect(emailInput).toHaveAttribute('required');
    await expect(passwordInput).toHaveAttribute('required');
    
    // 测试无效邮箱格式
    await emailInput.fill('invalid-email');
    await passwordInput.fill('password');
    await page.click('button[type="submit"]');
    
    // 应该显示邮箱格式错误或无法提交
    const isInvalid = await emailInput.evaluate((el: HTMLInputElement) => !el.validity.valid);
    expect(isInvalid).toBe(true);
  });
  
  test('should login successfully with valid teacher credentials', async ({ page }) => {
    await page.goto('/login');
    
    // 填写教师登录信息
    await page.fill('input[type="email"]', TEST_USERS.teacher.email);
    await page.fill('input[type="password"]', TEST_USERS.teacher.password);
    
    // 点击登录按钮
    await page.click('button[type="submit"]');
    
    // 验证登录成功 - 应该重定向到仪表板
    await expect(page).toHaveURL(/\/dashboard/);
    
    // 验证教师界面元素存在
    await expect(page.locator('[data-testid="teacher-dashboard"]')).toBeVisible({ timeout: 10000 });
    
    // 验证用户信息显示
    await expect(page.locator('text=' + TEST_USERS.teacher.fullName)).toBeVisible();
    
    // 验证教师专有功能存在
    await expect(page.locator('text=Student Management')).toBeVisible();
    await expect(page.locator('text=Assignment Creation')).toBeVisible();
  });
  
  test('should login successfully with valid student credentials', async ({ page }) => {
    await page.goto('/login');
    
    // 填写学生登录信息
    await page.fill('input[type="email"]', TEST_USERS.student.email);
    await page.fill('input[type="password"]', TEST_USERS.student.password);
    
    // 点击登录按钮
    await page.click('button[type="submit"]');
    
    // 验证登录成功
    await expect(page).toHaveURL(/\/dashboard/);
    
    // 验证学生界面元素存在
    await expect(page.locator('[data-testid="student-dashboard"]')).toBeVisible({ timeout: 10000 });
    
    // 验证用户信息显示
    await expect(page.locator('text=' + TEST_USERS.student.fullName)).toBeVisible();
    
    // 验证学生专有功能存在
    await expect(page.locator('text=My Assignments')).toBeVisible();
    await expect(page.locator('text=Code Submission')).toBeVisible();
  });
  
  test('should show error for invalid credentials', async ({ page }) => {
    await page.goto('/login');
    
    // 使用错误的凭据
    await page.fill('input[type="email"]', 'wrong@university.edu');
    await page.fill('input[type="password"]', 'wrongpassword');
    
    await page.click('button[type="submit"]');
    
    // 验证错误信息显示
    await expect(page.locator('[role="alert"]')).toBeVisible();
    await expect(page.locator('text=/invalid.*credentials|incorrect.*password/i')).toBeVisible();
    
    // 确保仍在登录页面
    await expect(page).toHaveURL(/\/login/);
  });
  
  test('should toggle password visibility', async ({ page }) => {
    await page.goto('/login');
    
    const passwordInput = page.locator('input[type="password"]');
    const toggleButton = page.locator('[data-testid="toggle-password"]');
    
    // 初始状态应该是password类型
    await expect(passwordInput).toHaveAttribute('type', 'password');
    
    // 填写密码
    await passwordInput.fill('testpassword');
    
    // 点击显示密码
    await toggleButton.click();
    
    // 验证变为text类型
    await expect(passwordInput).toHaveAttribute('type', 'text');
    
    // 再次点击隐藏密码
    await toggleButton.click();
    
    // 验证变回password类型
    await expect(passwordInput).toHaveAttribute('type', 'password');
  });
  
  test('should register new user successfully', async ({ page }) => {
    await page.goto('/register');
    
    // 验证注册页面存在
    await expect(page.locator('h1')).toContainText(/sign up|register/i);
    
    // 填写注册信息
    const newUser = TEST_USERS.newUser;
    await page.fill('input[name="email"]', newUser.email);
    await page.fill('input[name="password"]', newUser.password);
    await page.fill('input[name="fullName"]', newUser.fullName);
    await page.selectOption('select[name="role"]', newUser.role);
    await page.fill('input[name="university"]', newUser.university);
    await page.fill('input[name="department"]', newUser.department);
    
    // 提交注册
    await page.click('button[type="submit"]');
    
    // 验证注册成功 - 可能重定向到登录页或直接登录
    await expect(page).toHaveURL(/\/(login|dashboard)/);
    
    if (page.url().includes('/login')) {
      // 如果重定向到登录页，显示成功消息
      await expect(page.locator('text=/registration successful|account created/i')).toBeVisible();
      
      // 尝试用新账号登录
      await page.fill('input[type="email"]', newUser.email);
      await page.fill('input[type="password"]', newUser.password);
      await page.click('button[type="submit"]');
      
      await expect(page).toHaveURL(/\/dashboard/);
    }
  });
  
  test('should prevent registration with existing email', async ({ page }) => {
    await page.goto('/register');
    
    // 使用已存在的邮箱
    await page.fill('input[name="email"]', TEST_USERS.teacher.email);
    await page.fill('input[name="password"]', 'SomePassword123!');
    await page.fill('input[name="fullName"]', 'Duplicate User');
    await page.selectOption('select[name="role"]', 'teacher');
    await page.fill('input[name="university"]', 'Test University');
    await page.fill('input[name="department"]', 'Computer Science');
    
    await page.click('button[type="submit"]');
    
    // 验证错误消息
    await expect(page.locator('[role="alert"]')).toBeVisible();
    await expect(page.locator('text=/already.*registered|email.*exists/i')).toBeVisible();
  });
  
  test('should logout successfully', async ({ page }) => {
    // 先登录
    await page.goto('/login');
    await page.fill('input[type="email"]', TEST_USERS.teacher.email);
    await page.fill('input[type="password"]', TEST_USERS.teacher.password);
    await page.click('button[type="submit"]');
    
    await expect(page).toHaveURL(/\/dashboard/);
    
    // 找到并点击登出按钮
    const logoutButton = page.locator('button:has-text("Logout"), button:has-text("Sign Out"), a:has-text("Logout"), a:has-text("Sign Out")');
    await logoutButton.first().click();
    
    // 验证登出成功 - 重定向到登录页
    await expect(page).toHaveURL(/\/login/);
    
    // 验证本地存储被清除
    const token = await page.evaluate(() => localStorage.getItem('access_token'));
    expect(token).toBeNull();
  });
  
  test('should redirect unauthenticated users to login', async ({ page }) => {
    // 直接访问需要认证的页面
    await page.goto('/dashboard');
    
    // 应该重定向到登录页面
    await expect(page).toHaveURL(/\/login/);
    
    // 尝试访问其他受保护页面
    await page.goto('/assignments');
    await expect(page).toHaveURL(/\/login/);
    
    await page.goto('/profile');
    await expect(page).toHaveURL(/\/login/);
  });
  
  test('should remember redirect URL after login', async ({ page }) => {
    // 尝试访问受保护页面
    await page.goto('/assignments');
    
    // 应该重定向到登录页面
    await expect(page).toHaveURL(/\/login/);
    
    // 登录
    await page.fill('input[type="email"]', TEST_USERS.teacher.email);
    await page.fill('input[type="password"]', TEST_USERS.teacher.password);
    await page.click('button[type="submit"]');
    
    // 登录后应该重定向到最初访问的页面
    await expect(page).toHaveURL(/\/assignments/);
  });
  
  test('should handle session expiration gracefully', async ({ page }) => {
    // 登录
    await page.goto('/login');
    await page.fill('input[type="email"]', TEST_USERS.teacher.email);
    await page.fill('input[type="password"]', TEST_USERS.teacher.password);
    await page.click('button[type="submit"]');
    
    await expect(page).toHaveURL(/\/dashboard/);
    
    // 模拟token过期 - 清除localStorage中的token
    await page.evaluate(() => {
      localStorage.removeItem('access_token');
    });
    
    // 尝试访问需要认证的API
    await page.click('a[href="/profile"]');
    
    // 应该重定向到登录页面
    await expect(page).toHaveURL(/\/login/);
    
    // 可能显示会话过期消息
    const sessionMessage = page.locator('text=/session.*expired|please.*login.*again/i');
    if (await sessionMessage.isVisible()) {
      await expect(sessionMessage).toBeVisible();
    }
  });
  
  test('should validate password strength on registration', async ({ page }) => {
    await page.goto('/register');
    
    const passwordInput = page.locator('input[name="password"]');
    const strengthIndicator = page.locator('[data-testid="password-strength"], .password-strength');
    
    // 测试弱密码
    await passwordInput.fill('123');
    if (await strengthIndicator.isVisible()) {
      await expect(strengthIndicator).toContainText(/weak/i);
    }
    
    // 测试中等强度密码
    await passwordInput.fill('password123');
    if (await strengthIndicator.isVisible()) {
      await expect(strengthIndicator).toContainText(/medium|fair/i);
    }
    
    // 测试强密码
    await passwordInput.fill('StrongPassword123!');
    if (await strengthIndicator.isVisible()) {
      await expect(strengthIndicator).toContainText(/strong/i);
    }
  });
  
  test('should handle network errors gracefully', async ({ page }) => {
    // 拦截网络请求并返回错误
    await page.route('**/api/v1/auth/login', route => {
      route.abort('failed');
    });
    
    await page.goto('/login');
    await page.fill('input[type="email"]', TEST_USERS.teacher.email);
    await page.fill('input[type="password"]', TEST_USERS.teacher.password);
    
    await page.click('button[type="submit"]');
    
    // 应该显示网络错误消息
    await expect(page.locator('text=/network.*error|connection.*failed|try.*again/i')).toBeVisible();
  });
});