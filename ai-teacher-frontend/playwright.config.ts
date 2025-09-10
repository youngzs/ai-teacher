/**
 * Playwright E2E测试配置
 */

import { defineConfig, devices } from '@playwright/test';

/**
 * 从环境变量读取配置，如果没有设置则使用默认值
 */
export default defineConfig({
  // 测试目录
  testDir: './e2e',
  
  // 每个测试文件最大并行数
  fullyParallel: true,
  
  // CI环境中失败时不重试，本地环境重试1次
  retries: process.env.CI ? 2 : 1,
  
  // 并行worker数量
  workers: process.env.CI ? 1 : undefined,
  
  // 报告配置
  reporter: [
    ['html'],
    ['json', { outputFile: 'test-results/results.json' }],
    ['junit', { outputFile: 'test-results/results.xml' }]
  ],
  
  // 全局设置
  use: {
    // 基础URL - 根据环境调整
    baseURL: process.env.E2E_BASE_URL || 'http://localhost:3000',
    
    // 浏览器上下文配置
    trace: 'on-first-retry',
    screenshot: 'only-on-failure',
    video: 'retain-on-failure',
    
    // 超时设置
    actionTimeout: 10000,
    navigationTimeout: 30000,
    
    // 用户代理
    userAgent: 'AI-Teacher-E2E-Tests/1.0',
  },
  
  // 测试项目配置 - 不同浏览器和设备
  projects: [
    // 桌面浏览器
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
    {
      name: 'firefox',
      use: { ...devices['Desktop Firefox'] },
    },
    {
      name: 'webkit',
      use: { ...devices['Desktop Safari'] },
    },
    
    // 移动设备
    {
      name: 'mobile-chrome',
      use: { ...devices['Pixel 5'] },
    },
    {
      name: 'mobile-safari',
      use: { ...devices['iPhone 12'] },
    },
    
    // Microsoft Edge
    {
      name: 'msedge',
      use: { ...devices['Desktop Edge'], channel: 'msedge' },
    },
    
    // Google Chrome
    {
      name: 'chrome',
      use: { ...devices['Desktop Chrome'], channel: 'chrome' },
    },
  ],
  
  // 开发服务器配置
  webServer: {
    command: 'npm run dev',
    url: 'http://localhost:3000',
    reuseExistingServer: !process.env.CI,
    timeout: 120000,
    env: {
      NODE_ENV: 'test',
    },
  },
  
  // 期望配置
  expect: {
    // 断言超时
    timeout: 5000,
    // 截图比较阈值
    threshold: 0.3,
  },
  
  // 全局测试超时
  timeout: 30000,
  
  // 输出目录
  outputDir: 'test-results/',
  
  // 测试匹配模式
  testMatch: [
    '**/*.e2e.ts',
    '**/*.e2e.spec.ts',
    '**/e2e/**/*.test.ts',
    '**/e2e/**/*.spec.ts'
  ],
  
  // 忽略文件
  testIgnore: [
    '**/.git/**',
    '**/node_modules/**',
    '**/dist/**'
  ],
  
  // 测试环境变量
  globalSetup: require.resolve('./e2e/global-setup.ts'),
  globalTeardown: require.resolve('./e2e/global-teardown.ts'),
});