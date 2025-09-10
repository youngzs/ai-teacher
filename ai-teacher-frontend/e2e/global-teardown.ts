/**
 * Playwright 全局清理
 * 在所有测试完成后执行的清理工作
 */

import { chromium, FullConfig } from '@playwright/test';

async function globalTeardown(config: FullConfig) {
  console.log('🧹 Starting E2E test global teardown...');
  
  try {
    // 清理测试数据
    if (process.env.E2E_CLEANUP_TEST_DATA === 'true') {
      console.log('🗑️  Cleaning up test data...');
      await cleanupTestData();
    }
    
    // 清理测试用户账号
    if (process.env.E2E_CLEANUP_TEST_USERS === 'true') {
      console.log('👥 Cleaning up test user accounts...');
      await cleanupTestUsers();
    }
    
    // 清理临时文件
    await cleanupTempFiles();
    
    console.log('✅ Global teardown completed successfully');
    
  } catch (error) {
    console.error('❌ Global teardown failed:', error);
    // 清理失败不应阻止测试完成
  }
}

async function cleanupTestData() {
  try {
    const browser = await chromium.launch();
    const context = await browser.newContext();
    const page = await context.newPage();
    
    const apiURL = process.env.E2E_API_URL || 'http://localhost:8000';
    
    // 删除E2E测试创建的提交记录
    try {
      const response = await page.request.delete(`${apiURL}/api/v1/test/cleanup/submissions`, {
        data: { test_marker: 'e2e-test' }
      });
      
      if (response.ok()) {
        console.log('✅ Test submissions cleaned up');
      } else {
        console.log(`⚠️  Submission cleanup returned: ${response.status()}`);
      }
    } catch (error) {
      console.log('⚠️  Failed to cleanup submissions:', error.message);
    }
    
    await context.close();
    await browser.close();
    
  } catch (error) {
    console.log('⚠️  Test data cleanup failed:', error.message);
  }
}

async function cleanupTestUsers() {
  try {
    const browser = await chromium.launch();
    const context = await browser.newContext();
    const page = await context.newPage();
    
    const apiURL = process.env.E2E_API_URL || 'http://localhost:8000';
    
    const testEmails = [
      'e2e.teacher@university.edu',
      'e2e.student@university.edu'
    ];
    
    for (const email of testEmails) {
      try {
        const response = await page.request.delete(`${apiURL}/api/v1/test/cleanup/user`, {
          data: { email }
        });
        
        if (response.ok()) {
          console.log(`✅ Cleaned up test user: ${email}`);
        } else {
          console.log(`⚠️  User cleanup returned: ${response.status()} for ${email}`);
        }
      } catch (error) {
        console.log(`⚠️  Failed to cleanup user ${email}:`, error.message);
      }
    }
    
    await context.close();
    await browser.close();
    
  } catch (error) {
    console.log('⚠️  Test user cleanup failed:', error.message);
  }
}

async function cleanupTempFiles() {
  try {
    const fs = require('fs').promises;
    const path = require('path');
    
    // 清理测试结果目录中的临时文件
    const testResultsDir = path.join(process.cwd(), 'test-results');
    
    try {
      const files = await fs.readdir(testResultsDir);
      const tempFiles = files.filter(file => 
        file.startsWith('temp-') || 
        file.endsWith('.tmp') ||
        file.includes('screenshot-')
      );
      
      for (const file of tempFiles) {
        await fs.unlink(path.join(testResultsDir, file));
        console.log(`✅ Cleaned up temp file: ${file}`);
      }
    } catch (error) {
      // 目录可能不存在，这是正常的
      console.log('ℹ️  No temp files to clean up');
    }
    
  } catch (error) {
    console.log('⚠️  Temp file cleanup failed:', error.message);
  }
}

export default globalTeardown;