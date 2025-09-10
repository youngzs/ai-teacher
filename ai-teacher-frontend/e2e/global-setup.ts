/**
 * Playwright 全局设置
 * 在所有测试开始前执行的设置
 */

import { chromium, FullConfig } from '@playwright/test';

async function globalSetup(config: FullConfig) {
  console.log('🚀 Starting E2E test global setup...');
  
  try {
    // 启动浏览器进行预热和验证
    const browser = await chromium.launch();
    const context = await browser.newContext();
    const page = await context.newPage();
    
    // 验证前端应用是否可访问
    const baseURL = config.projects[0].use.baseURL || 'http://localhost:3000';
    console.log(`📡 Checking if app is running at ${baseURL}`);
    
    try {
      await page.goto(baseURL, { timeout: 30000 });
      console.log('✅ Frontend application is accessible');
    } catch (error) {
      console.error('❌ Frontend application is not accessible:', error);
      throw new Error(`Cannot access frontend at ${baseURL}`);
    }
    
    // 验证后端API是否可访问
    const apiURL = process.env.E2E_API_URL || 'http://localhost:8000';
    console.log(`🔍 Checking if API is running at ${apiURL}`);
    
    try {
      const response = await page.request.get(`${apiURL}/health`);
      if (response.ok()) {
        console.log('✅ Backend API is accessible');
      } else {
        console.log(`⚠️  Backend API returned status: ${response.status()}`);
      }
    } catch (error) {
      console.log('⚠️  Backend API health check failed:', error.message);
      // API不可访问时只记录警告，不中断测试（可能使用mock）
    }
    
    // 设置测试用户账号（如果需要）
    if (process.env.E2E_SETUP_TEST_USERS === 'true') {
      console.log('👥 Setting up test user accounts...');
      await setupTestUsers(page);
    }
    
    // 清理浏览器资源
    await context.close();
    await browser.close();
    
    console.log('✅ Global setup completed successfully');
    
  } catch (error) {
    console.error('❌ Global setup failed:', error);
    throw error;
  }
}

async function setupTestUsers(page: any) {
  try {
    const apiURL = process.env.E2E_API_URL || 'http://localhost:8000';
    
    // 测试教师账号
    const teacherData = {
      email: 'e2e.teacher@university.edu',
      password: 'E2ETestPassword123!',
      full_name: 'E2E Test Teacher',
      role: 'teacher',
      university: 'E2E Test University',
      department: 'Computer Science'
    };
    
    // 测试学生账号
    const studentData = {
      email: 'e2e.student@university.edu', 
      password: 'E2ETestPassword123!',
      full_name: 'E2E Test Student',
      role: 'student',
      university: 'E2E Test University',
      department: 'Computer Science',
      student_id: 'E2E001'
    };
    
    // 尝试创建测试账号
    for (const userData of [teacherData, studentData]) {
      try {
        const response = await page.request.post(`${apiURL}/api/v1/auth/register`, {
          data: userData
        });
        
        if (response.ok()) {
          console.log(`✅ Created test ${userData.role}: ${userData.email}`);
        } else {
          const errorData = await response.json().catch(() => ({}));
          if (response.status() === 400 && errorData.detail?.includes('already registered')) {
            console.log(`ℹ️  Test ${userData.role} already exists: ${userData.email}`);
          } else {
            console.log(`⚠️  Failed to create test ${userData.role}: ${response.status()}`);
          }
        }
      } catch (error) {
        console.log(`⚠️  Error creating test ${userData.role}:`, error.message);
      }
    }
  } catch (error) {
    console.log('⚠️  Test user setup failed:', error.message);
    // 不抛出错误，因为测试仍然可以继续
  }
}

export default globalSetup;