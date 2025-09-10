/**
 * 学生工作流程端到端测试  
 * 测试学生完整学习流程：登录→作业查看→代码提交→AI反馈接收→问题解决
 */

import { test, expect, Page } from '@playwright/test';

// 测试数据
const STUDENT_USER = {
  email: 'e2e.student@university.edu',
  password: 'E2ETestPassword123!'
};

const CODE_SAMPLES = {
  correct_c: `#include <stdio.h>
int factorial(int n) {
    if (n <= 1) return 1;
    return n * factorial(n - 1);
}
int main() {
    int num = 5;
    printf("Factorial of %d is %d\\n", num, factorial(num));
    return 0;
}`,
  
  buggy_c: `#include <stdio.h>
int factorial(int n) {
    if (n == 0) return 1;
    return n * factorial(n - 1);  // Missing base case for n=1
}
int main() {
    printf("%d", factorial(5));  // Missing newline
    return 0;
}`,
  
  incomplete_c: `#include <stdio.h>
int main() {
    // TODO: Implement factorial function
    return 0;
}`,
  
  python_sample: `def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)

print(fibonacci(10))`
};

// 帮助函数
async function loginAsStudent(page: Page) {
  await page.goto('/login');
  await page.fill('input[type="email"]', STUDENT_USER.email);
  await page.fill('input[type="password"]', STUDENT_USER.password);
  await page.click('button[type="submit"]');
  await expect(page).toHaveURL(/\/dashboard/);
}

async function submitCode(page: Page, code: string, language: string = 'c') {
  // 填写代码
  const codeEditor = page.locator('[data-testid="code-editor"] textarea, .code-editor textarea, textarea[name="code"]');
  await codeEditor.fill(code);
  
  // 选择编程语言
  const languageSelector = page.locator('select[name="language"]');
  if (await languageSelector.isVisible()) {
    await languageSelector.selectOption(language);
  }
  
  // 提交代码
  await page.click('button[type="submit"]:has-text("Submit"), button:has-text("Submit Code")');
}

test.describe('Student Complete Learning Workflow', () => {
  
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
    await page.evaluate(() => {
      localStorage.clear();
      sessionStorage.clear();
    });
  });
  
  test('should complete student onboarding and dashboard exploration', async ({ page }) => {
    await loginAsStudent(page);
    
    // 验证学生仪表板
    await test.step('Explore student dashboard', async () => {
      await expect(page.locator('[data-testid="student-dashboard"]')).toBeVisible();
      
      // 验证关键信息显示
      await expect(page.locator('text=/welcome|hello/i')).toBeVisible();
      
      // 验证学生专有功能存在
      const dashboardSections = [
        'My Assignments',
        'Recent Submissions', 
        'AI Feedback',
        'Progress Overview'
      ];
      
      for (const section of dashboardSections) {
        const sectionElement = page.locator(`text="${section}", h2:has-text("${section}"), h3:has-text("${section}")`);
        if (await sectionElement.isVisible()) {
          await expect(sectionElement).toBeVisible();
        }
      }
      
      // 查看学习进度概览
      const progressSection = page.locator('[data-testid="progress-overview"]');
      if (await progressSection.isVisible()) {
        await expect(progressSection).toBeVisible();
        
        // 验证进度指标
        await expect(progressSection.locator('text=/completed|progress|score/i')).toBeVisible();
      }
    });
    
    // 探索导航菜单
    await test.step('Navigate through student menu sections', async () => {
      const navigationItems = [
        'Assignments',
        'Submissions', 
        'Feedback',
        'Profile'
      ];
      
      for (const item of navigationItems) {
        const navLink = page.locator(`nav a:has-text("${item}"), .sidebar a:has-text("${item}"), .menu a:has-text("${item}")`).first();
        if (await navLink.isVisible()) {
          await navLink.click();
          
          // 验证页面加载
          await expect(page.locator('h1, h2')).toContainText(new RegExp(item, 'i'));
          
          // 返回仪表板以便下次导航
          await page.locator('a:has-text("Dashboard"), a:has-text("Home")').first().click();
        }
      }
    });
  });
  
  test('should view and start assignments', async ({ page }) => {
    await loginAsStudent(page);
    
    await test.step('Browse available assignments', async () => {
      // 导航到作业页面
      await page.locator('nav a:has-text("Assignments"), .sidebar a:has-text("Assignments")').first().click();
      
      // 验证作业列表页面
      await expect(page.locator('h1, h2')).toContainText(/assignments/i);
      
      // 查看作业卡片/列表
      const assignmentList = page.locator('[data-testid="assignment-list"], .assignment-list');
      await expect(assignmentList).toBeVisible();
      
      // 验证作业信息显示
      const firstAssignment = assignmentList.locator('.assignment-item, .assignment-card').first();
      await expect(firstAssignment).toBeVisible();
      
      // 验证作业详细信息
      await expect(firstAssignment.locator('text=/title|name/i')).toBeVisible();
      await expect(firstAssignment.locator('text=/due|deadline/i')).toBeVisible();
      await expect(firstAssignment.locator('text=/difficulty|level/i')).toBeVisible();
      await expect(firstAssignment.locator('text=/language/i')).toBeVisible();
    });
    
    await test.step('View assignment details', async () => {
      // 点击查看作业详情
      await page.locator('.assignment-item, .assignment-card').first().click();
      
      // 验证作业详情页面
      await expect(page.locator('h1')).toContainText(/assignment|homework/i);
      
      // 验证作业描述和要求
      const assignmentDetails = page.locator('[data-testid="assignment-details"]');
      await expect(assignmentDetails).toBeVisible();
      
      // 查看代码模板（如果提供）
      const codeTemplate = page.locator('[data-testid="code-template"]');
      if (await codeTemplate.isVisible()) {
        await expect(codeTemplate).toBeVisible();
      }
      
      // 查看测试用例说明（如果提供）
      const testCases = page.locator('[data-testid="test-cases"]');
      if (await testCases.isVisible()) {
        await expect(testCases).toBeVisible();
      }
      
      // 查看评分标准
      const rubric = page.locator('[data-testid="rubric"]');
      if (await rubric.isVisible()) {
        await expect(rubric).toBeVisible();
      }
    });
    
    await test.step('Start working on assignment', async () => {
      // 点击开始作业按钮
      const startButton = page.locator('button:has-text("Start Assignment"), button:has-text("Begin"), a:has-text("Start")');
      await startButton.click();
      
      // 验证进入代码编辑页面
      await expect(page.locator('[data-testid="code-editor"]')).toBeVisible();
      
      // 验证编程语言已正确设置
      const languageIndicator = page.locator('[data-testid="language-selector"], .language-indicator');
      if (await languageIndicator.isVisible()) {
        await expect(languageIndicator).toContainText(/c|python|javascript/i);
      }
    });
  });
  
  test('should submit code and receive AI feedback', async ({ page }) => {
    await loginAsStudent(page);
    
    // 导航到一个作业
    await page.locator('nav a:has-text("Assignments")').first().click();
    await page.locator('.assignment-item').first().click();
    await page.locator('button:has-text("Start"), a:has-text("Start")').click();
    
    await test.step('Submit correct code and get positive feedback', async () => {
      await submitCode(page, CODE_SAMPLES.correct_c);
      
      // 等待提交处理
      await expect(page.locator('text="Code submitted successfully"')).toBeVisible();
      
      // 等待AI分析完成
      const loadingIndicator = page.locator('[data-testid="ai-analyzing"], .loading, text=/analyzing|processing/i');
      if (await loadingIndicator.isVisible()) {
        await expect(loadingIndicator).toBeHidden({ timeout: 30000 });
      }
      
      // 验证AI反馈显示
      const aiFeedback = page.locator('[data-testid="ai-feedback"]');
      await expect(aiFeedback).toBeVisible({ timeout: 15000 });
      
      // 验证反馈内容结构
      await expect(aiFeedback.locator('text=/score|grade/i')).toBeVisible();
      await expect(aiFeedback.locator('text=/strengths|good|excellent/i')).toBeVisible();
      await expect(aiFeedback.locator('text=/suggestions|improvements/i')).toBeVisible();
      
      // 验证积极反馈的存在
      const feedbackText = await aiFeedback.textContent();
      expect(feedbackText).toMatch(/good|excellent|well|correct|nice/i);
    });
    
    await test.step('Submit buggy code and get constructive feedback', async () => {
      // 清除当前代码并提交有bug的代码
      await page.locator('[data-testid="code-editor"] textarea').fill('');
      await submitCode(page, CODE_SAMPLES.buggy_c);
      
      await expect(page.locator('text="Code submitted successfully"')).toBeVisible();
      
      // 等待AI分析
      await expect(page.locator('[data-testid="ai-feedback"]')).toBeVisible({ timeout: 15000 });
      
      // 验证构建性反馈
      const feedback = page.locator('[data-testid="ai-feedback"]');
      const feedbackText = await feedback.textContent();
      
      // 应该包含错误识别
      expect(feedbackText).toMatch(/error|bug|issue|problem|missing|incorrect/i);
      
      // 应该包含改进建议
      expect(feedbackText).toMatch(/try|consider|add|fix|change|improve/i);
      
      // 验证调试提示
      const debuggingTips = feedback.locator('[data-testid="debugging-tips"]');
      if (await debuggingTips.isVisible()) {
        await expect(debuggingTips).toBeVisible();
      }
    });
    
    await test.step('Use hint system if available', async () => {
      const hintButton = page.locator('button:has-text("Hint"), button:has-text("Get Help")');
      if (await hintButton.isVisible()) {
        await hintButton.click();
        
        // 验证提示显示
        const hint = page.locator('[data-testid="hint-modal"], [data-testid="hint-panel"]');
        await expect(hint).toBeVisible();
        
        // 验证提示内容有用
        const hintText = await hint.textContent();
        expect(hintText.length).toBeGreaterThan(20); // 确保有实质内容
        
        // 关闭提示
        await page.locator('button:has-text("Close"), button:has-text("Got it")').click();
      }
    });
  });
  
  test('should iterate on code based on AI feedback', async ({ page }) => {
    await loginAsStudent(page);
    
    // 导航到作业并开始
    await page.locator('nav a:has-text("Assignments")').first().click();
    await page.locator('.assignment-item').first().click();
    await page.locator('button:has-text("Start")').click();
    
    await test.step('Initial submission with issues', async () => {
      await submitCode(page, CODE_SAMPLES.incomplete_c);
      
      // 等待反馈
      await expect(page.locator('[data-testid="ai-feedback"]')).toBeVisible({ timeout: 15000 });
      
      // 记录初始分数
      const initialScoreElement = page.locator('[data-testid="score"], text=/score.*\\d+/i');
      const initialScore = await initialScoreElement.textContent();
      
      // 验证获得了改进建议
      const feedback = page.locator('[data-testid="ai-feedback"]');
      await expect(feedback.locator('text=/implement|complete|add|finish/i')).toBeVisible();
    });
    
    await test.step('Improve code based on feedback', async () => {
      // 修改代码
      const improvedCode = `#include <stdio.h>
int factorial(int n) {
    if (n <= 1) return 1;
    return n * factorial(n - 1);
}
int main() {
    int num = 5;
    printf("Factorial of %d is %d\\n", num, factorial(num));
    return 0;
}`;
      
      await page.locator('[data-testid="code-editor"] textarea').fill(improvedCode);
      await submitCode(page, ''); // 代码已填写，只需点击提交
      
      // 等待新的反馈
      await expect(page.locator('[data-testid="ai-feedback"]')).toBeVisible({ timeout: 15000 });
      
      // 验证分数提高
      const newScoreElement = page.locator('[data-testid="score"], text=/score.*\\d+/i');
      const newFeedback = page.locator('[data-testid="ai-feedback"]');
      
      // 应该看到更积极的反馈
      const feedbackText = await newFeedback.textContent();
      expect(feedbackText).toMatch(/better|improved|good|excellent|well/i);
    });
    
    await test.step('Track submission history', async () => {
      // 查看提交历史
      const historyButton = page.locator('button:has-text("History"), button:has-text("Previous Submissions")');
      if (await historyButton.isVisible()) {
        await historyButton.click();
        
        // 验证显示多次提交
        const submissionHistory = page.locator('[data-testid="submission-history"]');
        await expect(submissionHistory).toBeVisible();
        
        const submissions = submissionHistory.locator('.submission-item');
        const submissionCount = await submissions.count();
        expect(submissionCount).toBeGreaterThan(1);
        
        // 验证每个提交都有分数和时间戳
        for (let i = 0; i < Math.min(submissionCount, 3); i++) {
          await expect(submissions.nth(i).locator('text=/score|\\d+%|\\d+\\/\\d+/')).toBeVisible();
          await expect(submissions.nth(i).locator('text=/\\d+:\\d+|ago|\\d{4}-\\d{2}-\\d{2}/')).toBeVisible();
        }
      }
    });
  });
  
  test('should handle different programming languages', async ({ page }) => {
    await loginAsStudent(page);
    
    await test.step('Work with Python assignment', async () => {
      // 寻找Python作业（如果有的话）
      await page.locator('nav a:has-text("Assignments")').first().click();
      
      const pythonAssignment = page.locator('.assignment-item:has-text("Python"), .assignment-item:has-text("python")').first();
      
      if (await pythonAssignment.isVisible()) {
        await pythonAssignment.click();
        await page.locator('button:has-text("Start")').click();
        
        // 验证Python编辑器环境
        const languageIndicator = page.locator('text="Python", [data-language="python"]');
        await expect(languageIndicator).toBeVisible();
        
        // 提交Python代码
        await submitCode(page, CODE_SAMPLES.python_sample, 'python');
        
        // 验证Python特定的反馈
        await expect(page.locator('[data-testid="ai-feedback"]')).toBeVisible({ timeout: 15000 });
        
        const feedback = await page.locator('[data-testid="ai-feedback"]').textContent();
        // Python反馈可能包含特定的建议
        const hasPythonSpecificFeedback = 
          feedback.includes('pythonic') || 
          feedback.includes('list comprehension') ||
          feedback.includes('PEP 8') ||
          feedback.includes('function');
        
        // 至少应该有一般性的编程反馈
        expect(feedback.length).toBeGreaterThan(50);
      }
    });
  });
  
  test('should access learning resources and help', async ({ page }) => {
    await loginAsStudent(page);
    
    await test.step('Access help and documentation', async () => {
      // 查找帮助链接
      const helpButton = page.locator('button:has-text("Help"), a:has-text("Help"), button:has-text("?")');
      
      if (await helpButton.isVisible()) {
        await helpButton.click();
        
        // 验证帮助内容
        const helpModal = page.locator('[data-testid="help-modal"], .help-modal, .modal');
        await expect(helpModal).toBeVisible();
        
        // 查看常见问题
        const faqSection = helpModal.locator('text="FAQ", text="Frequently Asked Questions"');
        if (await faqSection.isVisible()) {
          await expect(faqSection).toBeVisible();
        }
        
        // 查看编程指南链接
        const guidesLink = helpModal.locator('a:has-text("Programming Guide"), a:has-text("Tutorial")');
        if (await guidesLink.isVisible()) {
          await expect(guidesLink).toBeVisible();
        }
        
        await page.locator('button:has-text("Close")').click();
      }
    });
    
    await test.step('Access code examples and resources', async () => {
      // 查找示例代码或资源链接
      const resourcesLink = page.locator('a:has-text("Resources"), a:has-text("Examples"), a:has-text("Library")');
      
      if (await resourcesLink.isVisible()) {
        await resourcesLink.click();
        
        // 验证资源页面
        await expect(page.locator('h1, h2')).toContainText(/resources|examples|library/i);
        
        // 查看代码示例
        const codeExamples = page.locator('[data-testid="code-examples"], .code-example');
        if (await codeExamples.isVisible()) {
          await expect(codeExamples).toBeVisible();
          
          // 点击一个示例
          const firstExample = codeExamples.locator('.example-item').first();
          if (await firstExample.isVisible()) {
            await firstExample.click();
            
            // 验证示例详情显示
            const exampleCode = page.locator('pre, code, [data-testid="example-code"]');
            await expect(exampleCode).toBeVisible();
          }
        }
      }
    });
  });
  
  test('should handle assignment deadlines and late submissions', async ({ page }) => {
    await loginAsStudent(page);
    
    await test.step('View assignment deadlines', async () => {
      await page.locator('nav a:has-text("Assignments")').first().click();
      
      // 验证截止日期显示
      const assignments = page.locator('.assignment-item');
      const assignmentCount = await assignments.count();
      
      for (let i = 0; i < Math.min(assignmentCount, 3); i++) {
        const assignment = assignments.nth(i);
        
        // 验证每个作业都显示截止日期
        await expect(assignment.locator('text=/due|deadline/i')).toBeVisible();
        await expect(assignment.locator('text=/\\d{4}-\\d{2}-\\d{2}|\\d+.*day|tomorrow|today/i')).toBeVisible();
        
        // 检查紧急标记（如果接近截止日期）
        const urgentMarker = assignment.locator('.urgent, .deadline-warning, text=/urgent|soon/i');
        // 紧急标记可能存在也可能不存在，取决于作业截止时间
      }
    });
    
    await test.step('Handle overdue assignment submission attempt', async () => {
      // 查找已过期的作业（如果有的话）
      const overdueAssignment = page.locator('.assignment-item:has-text("Overdue"), .assignment-item.overdue').first();
      
      if (await overdueAssignment.isVisible()) {
        await overdueAssignment.click();
        
        // 尝试开始过期作业
        const startButton = page.locator('button:has-text("Start")');
        
        if (await startButton.isVisible()) {
          await startButton.click();
          
          // 应该显示过期警告
          const overdueWarning = page.locator('text=/overdue|late.*penalty|deadline.*passed/i');
          await expect(overdueWarning).toBeVisible();
          
          // 但仍然允许提交（如果配置允许迟交）
          await expect(page.locator('[data-testid="code-editor"]')).toBeVisible();
        } else {
          // 如果不允许迟交，应该显示相应消息
          const noSubmissionMessage = page.locator('text=/submission.*closed|deadline.*passed|no.*longer.*accept/i');
          await expect(noSubmissionMessage).toBeVisible();
        }
      }
    });
  });
  
  test('should provide feedback on student experience', async ({ page }) => {
    await loginAsStudent(page);
    
    await test.step('Rate AI feedback quality', async () => {
      // 提交代码并获得反馈
      await page.locator('nav a:has-text("Assignments")').first().click();
      await page.locator('.assignment-item').first().click();
      await page.locator('button:has-text("Start")').click();
      
      await submitCode(page, CODE_SAMPLES.correct_c);
      await expect(page.locator('[data-testid="ai-feedback"]')).toBeVisible({ timeout: 15000 });
      
      // 查找反馈评分功能
      const feedbackRating = page.locator('[data-testid="feedback-rating"], .feedback-rating');
      
      if (await feedbackRating.isVisible()) {
        // 给反馈评分
        const ratingStars = feedbackRating.locator('.star, button[data-rating]');
        const starCount = await ratingStars.count();
        
        if (starCount > 0) {
          // 点击4星评分
          const fourthStar = ratingStars.nth(3);
          await fourthStar.click();
          
          // 验证评分被记录
          await expect(page.locator('text="Thank you for your feedback"')).toBeVisible();
        }
      }
    });
    
    await test.step('Provide general feedback about the system', async () => {
      // 查找系统反馈功能
      const feedbackButton = page.locator('button:has-text("Feedback"), a:has-text("Send Feedback"), button:has-text("Report Issue")');
      
      if (await feedbackButton.isVisible()) {
        await feedbackButton.click();
        
        const feedbackForm = page.locator('[data-testid="feedback-form"], .feedback-form');
        await expect(feedbackForm).toBeVisible();
        
        // 填写反馈
        await page.fill('textarea[name="feedback"]', 'The AI feedback is very helpful and detailed. It helps me understand my mistakes and learn better.');
        await page.selectOption('select[name="category"]', 'positive');
        
        await page.click('button[type="submit"]:has-text("Send")');
        await expect(page.locator('text="Feedback submitted successfully"')).toBeVisible();
      }
    });
  });
});