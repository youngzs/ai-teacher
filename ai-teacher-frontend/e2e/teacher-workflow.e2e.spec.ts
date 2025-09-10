/**
 * 教师工作流程端到端测试
 * 测试教师的完整工作流程：班级管理→作业发布→AI反馈审核→结果发送
 */

import { test, expect, Page } from '@playwright/test';

// 测试数据
const TEACHER_USER = {
  email: 'e2e.teacher@university.edu',
  password: 'E2ETestPassword123!'
};

const SAMPLE_ASSIGNMENT = {
  title: 'E2E Test Assignment - Basic C Programming',
  description: 'Write a simple C program that calculates the factorial of a number using recursion.',
  language: 'c',
  difficulty: 'intermediate',
  dueDate: '2024-12-31',
  maxAttempts: 3,
  points: 100
};

const SAMPLE_CODE_SUBMISSIONS = [
  {
    studentName: 'Test Student 1',
    code: `#include <stdio.h>
int factorial(int n) {
    if (n <= 1) return 1;
    return n * factorial(n - 1);
}
int main() {
    printf("Factorial of 5 is %d\\n", factorial(5));
    return 0;
}`,
    expectedScore: 85
  },
  {
    studentName: 'Test Student 2',
    code: `#include <stdio.h>
int fact(int n) {
    if (n == 0) return 1;
    return n * fact(n - 1);
}
int main() {
    printf("%d", fact(5));
    return 0;
}`,
    expectedScore: 70
  }
];

// 帮助函数
async function loginAsTeacher(page: Page) {
  await page.goto('/login');
  await page.fill('input[type="email"]', TEACHER_USER.email);
  await page.fill('input[type="password"]', TEACHER_USER.password);
  await page.click('button[type="submit"]');
  await expect(page).toHaveURL(/\/dashboard/);
}

async function navigateToSection(page: Page, sectionName: string) {
  const navigation = page.locator('nav, [data-testid="sidebar"], .sidebar');
  await navigation.locator(`text=${sectionName}, a:has-text("${sectionName}")`).first().click();
}

test.describe('Teacher Complete Workflow', () => {
  
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
    await page.evaluate(() => {
      localStorage.clear();
      sessionStorage.clear();
    });
  });
  
  test('should complete full teacher workflow: class management to assignment publishing', async ({ page }) => {
    // Step 1: 教师登录
    await loginAsTeacher(page);
    
    // 验证教师仪表板加载
    await expect(page.locator('[data-testid="teacher-dashboard"]')).toBeVisible();
    
    // Step 2: 班级管理
    await test.step('Manage class and students', async () => {
      await navigateToSection(page, 'Classes');
      
      // 验证班级列表页面
      await expect(page.locator('h1, h2')).toContainText(/classes|classroom/i);
      
      // 如果没有班级，创建一个测试班级
      const hasClasses = await page.locator('[data-testid="class-list"] .class-item').count();
      if (hasClasses === 0) {
        await page.click('button:has-text("Create Class"), button:has-text("New Class")');
        
        await page.fill('input[name="className"]', 'E2E Test Class - CS101');
        await page.fill('input[name="description"]', 'End-to-end testing class');
        await page.selectOption('select[name="semester"]', 'Fall 2024');
        
        await page.click('button[type="submit"]:has-text("Create")');
        
        await expect(page.locator('text="Class created successfully"')).toBeVisible();
      }
      
      // 选择一个班级进入
      await page.locator('[data-testid="class-list"] .class-item').first().click();
      
      // 验证学生列表
      await expect(page.locator('[data-testid="student-list"]')).toBeVisible();
    });
    
    // Step 3: 作业创建和发布
    await test.step('Create and publish assignment', async () => {
      await navigateToSection(page, 'Assignments');
      
      // 点击创建新作业
      await page.click('button:has-text("Create Assignment"), button:has-text("New Assignment")');
      
      // 填写作业详情
      await page.fill('input[name="title"]', SAMPLE_ASSIGNMENT.title);
      await page.fill('textarea[name="description"]', SAMPLE_ASSIGNMENT.description);
      await page.selectOption('select[name="language"]', SAMPLE_ASSIGNMENT.language);
      await page.selectOption('select[name="difficulty"]', SAMPLE_ASSIGNMENT.difficulty);
      await page.fill('input[name="dueDate"]', SAMPLE_ASSIGNMENT.dueDate);
      await page.fill('input[name="maxAttempts"]', SAMPLE_ASSIGNMENT.maxAttempts.toString());
      await page.fill('input[name="points"]', SAMPLE_ASSIGNMENT.points.toString());
      
      // 添加测试用例（如果有的话）
      const addTestCaseButton = page.locator('button:has-text("Add Test Case")');
      if (await addTestCaseButton.isVisible()) {
        await addTestCaseButton.click();
        await page.fill('textarea[name="input"]', '5');
        await page.fill('textarea[name="expectedOutput"]', '120');
      }
      
      // 保存作业
      await page.click('button[type="submit"]:has-text("Create"), button:has-text("Save")');
      
      // 验证作业创建成功
      await expect(page.locator('text="Assignment created successfully"')).toBeVisible();
      
      // 发布作业
      await page.click('button:has-text("Publish")');
      await expect(page.locator('text="Assignment published"')).toBeVisible();
    });
  });
  
  test('should handle student submissions and AI feedback review workflow', async ({ page }) => {
    await loginAsTeacher(page);
    
    // 导航到提交审核页面
    await test.step('Navigate to submissions review', async () => {
      await navigateToSection(page, 'Submissions');
      
      // 验证提交列表页面
      await expect(page.locator('h1, h2')).toContainText(/submissions|reviews/i);
      
      // 如果没有提交，可以创建一些测试提交
      const submissionCount = await page.locator('[data-testid="submission-list"] .submission-item').count();
      if (submissionCount === 0) {
        // 模拟有学生提交（通过API或直接创建）
        console.log('No submissions found - this would typically be handled by test data setup');
      }
    });
    
    // 审核AI反馈
    await test.step('Review AI feedback for submissions', async () => {
      // 选择第一个待审核的提交
      const firstSubmission = page.locator('[data-testid="submission-list"] .submission-item').first();
      await firstSubmission.click();
      
      // 验证代码和AI分析显示
      await expect(page.locator('[data-testid="code-display"]')).toBeVisible();
      await expect(page.locator('[data-testid="ai-analysis"]')).toBeVisible();
      
      // 查看AI反馈质量
      const aiFeedback = page.locator('[data-testid="ai-feedback"]');
      await expect(aiFeedback).toBeVisible();
      
      // 验证AI反馈包含必要元素
      await expect(aiFeedback.locator('text=/score|rating/i')).toBeVisible();
      await expect(aiFeedback.locator('text=/strengths|good/i')).toBeVisible();
      await expect(aiFeedback.locator('text=/improvements|suggestions/i')).toBeVisible();
      
      // 教师可以修改或补充AI反馈
      const editFeedbackButton = page.locator('button:has-text("Edit Feedback")');
      if (await editFeedbackButton.isVisible()) {
        await editFeedbackButton.click();
        
        // 添加教师评论
        await page.fill('textarea[name="teacherComment"]', 'Great work! The recursive approach is well implemented.');
        await page.fill('input[name="teacherScore"]', '88');
        
        // 保存修改
        await page.click('button:has-text("Save Changes")');
        await expect(page.locator('text="Feedback updated"')).toBeVisible();
      }
    });
    
    // 批量处理多个提交
    await test.step('Batch process multiple submissions', async () => {
      await page.goBack(); // 返回提交列表
      
      // 选择多个提交进行批量操作
      const submissions = page.locator('[data-testid="submission-list"] .submission-item input[type="checkbox"]');
      const submissionCount = Math.min(await submissions.count(), 3);
      
      for (let i = 0; i < submissionCount; i++) {
        await submissions.nth(i).check();
      }
      
      // 批量审核通过
      const batchApproveButton = page.locator('button:has-text("Approve Selected"), button:has-text("Batch Approve")');
      if (await batchApproveButton.isVisible()) {
        await batchApproveButton.click();
        
        // 确认批量操作
        await page.click('button:has-text("Confirm")');
        await expect(page.locator('text="Submissions approved"')).toBeVisible();
      }
    });
  });
  
  test('should send feedback to students and track results', async ({ page }) => {
    await loginAsTeacher(page);
    
    // 进入反馈发送流程
    await test.step('Send feedback to students', async () => {
      await navigateToSection(page, 'Feedback');
      
      // 查看待发送的反馈
      const pendingFeedback = page.locator('[data-testid="pending-feedback"]');
      await expect(pendingFeedback).toBeVisible();
      
      // 选择要发送的反馈
      await page.locator('input[type="checkbox"]').first().check();
      
      // 发送反馈
      await page.click('button:has-text("Send Feedback")');
      
      // 可以添加发送消息
      const messageModal = page.locator('[data-testid="send-message-modal"]');
      if (await messageModal.isVisible()) {
        await page.fill('textarea[name="message"]', 'Please review the feedback and try to improve your code accordingly.');
        await page.click('button:has-text("Send")');
      }
      
      await expect(page.locator('text="Feedback sent successfully"')).toBeVisible();
    });
    
    // 追踪学习结果
    await test.step('Track student learning outcomes', async () => {
      await navigateToSection(page, 'Analytics');
      
      // 验证分析仪表板
      await expect(page.locator('[data-testid="analytics-dashboard"]')).toBeVisible();
      
      // 查看班级整体表现
      const classPerformance = page.locator('[data-testid="class-performance"]');
      await expect(classPerformance).toBeVisible();
      
      // 验证关键指标存在
      await expect(page.locator('text=/average.*score|class.*average/i')).toBeVisible();
      await expect(page.locator('text=/improvement.*rate|progress/i')).toBeVisible();
      await expect(page.locator('text=/completion.*rate/i')).toBeVisible();
      
      // 查看个别学生进度
      const studentProgress = page.locator('[data-testid="student-progress-chart"]');
      if (await studentProgress.isVisible()) {
        await expect(studentProgress).toBeVisible();
      }
      
      // 导出报告（如果功能存在）
      const exportButton = page.locator('button:has-text("Export"), button:has-text("Download Report")');
      if (await exportButton.isVisible()) {
        // 设置下载处理
        const downloadPromise = page.waitForEvent('download');
        await exportButton.click();
        const download = await downloadPromise;
        expect(download.suggestedFilename()).toMatch(/report|analytics|progress/i);
      }
    });
  });
  
  test('should handle AI system errors gracefully in teacher workflow', async ({ page }) => {
    await loginAsTeacher(page);
    
    // 模拟AI服务不可用
    await test.step('Handle AI service unavailable', async () => {
      // 拦截AI分析请求并返回错误
      await page.route('**/api/v1/analysis/analyze', route => {
        route.fulfill({
          status: 503,
          contentType: 'application/json',
          body: JSON.stringify({
            detail: 'AI service temporarily unavailable'
          })
        });
      });
      
      await navigateToSection(page, 'Submissions');
      
      // 尝试触发AI分析
      const firstSubmission = page.locator('[data-testid="submission-list"] .submission-item').first();
      await firstSubmission.click();
      
      // 应该显示AI服务不可用的提示
      await expect(page.locator('text=/AI.*unavailable|service.*error/i')).toBeVisible();
      
      // 验证教师仍然可以手动评分
      const manualGradeButton = page.locator('button:has-text("Manual Grade")');
      if (await manualGradeButton.isVisible()) {
        await manualGradeButton.click();
        
        await page.fill('input[name="score"]', '85');
        await page.fill('textarea[name="comments"]', 'Good work on the recursive implementation.');
        
        await page.click('button[type="submit"]');
        await expect(page.locator('text="Manual grade saved"')).toBeVisible();
      }
    });
  });
  
  test('should support collaborative feedback review with other teachers', async ({ page }) => {
    await loginAsTeacher(page);
    
    await test.step('Collaborate on feedback review', async () => {
      await navigateToSection(page, 'Collaboration');
      
      // 查看协作功能（如果存在）
      const collaborationPanel = page.locator('[data-testid="collaboration-panel"]');
      if (await collaborationPanel.isVisible()) {
        await expect(collaborationPanel).toBeVisible();
        
        // 邀请其他教师协作
        const inviteButton = page.locator('button:has-text("Invite Collaborator")');
        if (await inviteButton.isVisible()) {
          await inviteButton.click();
          await page.fill('input[name="email"]', 'colleague@university.edu');
          await page.click('button:has-text("Send Invitation")');
          
          await expect(page.locator('text="Invitation sent"')).toBeVisible();
        }
        
        // 查看共享的反馈草稿
        const sharedFeedback = page.locator('[data-testid="shared-feedback"]');
        if (await sharedFeedback.isVisible()) {
          await expect(sharedFeedback).toBeVisible();
        }
      }
    });
  });
  
  test('should validate assignment creation with comprehensive requirements', async ({ page }) => {
    await loginAsTeacher(page);
    
    await test.step('Create comprehensive assignment with all features', async () => {
      await navigateToSection(page, 'Assignments');
      await page.click('button:has-text("Create Assignment")');
      
      // 填写基本信息
      await page.fill('input[name="title"]', 'Comprehensive E2E Test Assignment');
      await page.fill('textarea[name="description"]', 'A comprehensive programming assignment with multiple requirements.');
      
      // 设置编程语言特定选项
      await page.selectOption('select[name="language"]', 'c');
      
      // 添加代码模板
      const codeTemplate = `#include <stdio.h>

// TODO: Implement the required function here

int main() {
    // TODO: Add your main function code here
    return 0;
}`;
      
      const templateTextarea = page.locator('textarea[name="codeTemplate"]');
      if (await templateTextarea.isVisible()) {
        await templateTextarea.fill(codeTemplate);
      }
      
      // 添加多个测试用例
      const addTestCaseButton = page.locator('button:has-text("Add Test Case")');
      if (await addTestCaseButton.isVisible()) {
        // 测试用例 1
        await addTestCaseButton.click();
        await page.fill('input[name="testCases[0].input"]', '5');
        await page.fill('input[name="testCases[0].expectedOutput"]', '120');
        await page.fill('input[name="testCases[0].description"]', 'Factorial of 5');
        
        // 测试用例 2
        await addTestCaseButton.click();
        await page.fill('input[name="testCases[1].input"]', '0');
        await page.fill('input[name="testCases[1].expectedOutput"]', '1');
        await page.fill('input[name="testCases[1].description"]', 'Factorial of 0 (edge case)');
      }
      
      // 设置评分标准
      const rubricSection = page.locator('[data-testid="rubric-section"]');
      if (await rubricSection.isVisible()) {
        await page.fill('input[name="rubric.correctness"]', '40');
        await page.fill('input[name="rubric.codeQuality"]', '30');
        await page.fill('input[name="rubric.efficiency"]', '20');
        await page.fill('input[name="rubric.documentation"]', '10');
      }
      
      // 设置截止日期和限制
      await page.fill('input[name="dueDate"]', '2024-12-31');
      await page.fill('input[name="maxAttempts"]', '3');
      await page.check('input[name="allowLateSubmission"]');
      
      // 保存并发布
      await page.click('button[type="submit"]:has-text("Create")');
      await expect(page.locator('text="Assignment created successfully"')).toBeVisible();
      
      // 验证作业详情页面
      await expect(page.locator('h1')).toContainText('Comprehensive E2E Test Assignment');
      await expect(page.locator('text="C Programming"')).toBeVisible();
      await expect(page.locator('text="3 attempts allowed"')).toBeVisible();
    });
  });
});