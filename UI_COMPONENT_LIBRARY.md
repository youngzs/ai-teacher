# AI教学助手系统 - UI设计规范和组件库标准

## 1. 设计系统概述

### 1.1 设计理念
- **教育友好**: 界面清晰易懂，减少学习认知负担
- **效率优先**: 支持快速操作，提高教学和学习效率
- **包容性设计**: 支持无障碍访问，适应不同用户需求
- **一致性**: 统一的视觉语言和交互模式

### 1.2 品牌色彩系统
```css
:root {
  /* 主色彩 - 教育蓝 */
  --primary-50: #eff6ff;
  --primary-100: #dbeafe;
  --primary-500: #3b82f6;   /* 主要按钮、链接 */
  --primary-600: #2563eb;   /* 悬停状态 */
  --primary-700: #1d4ed8;   /* 激活状态 */
  
  /* 成功绿色 - 用于正确、通过状态 */
  --success-50: #f0fdf4;
  --success-100: #dcfce7;
  --success-500: #22c55e;
  --success-600: #16a34a;
  
  /* 警告橙色 - 用于警告、需要注意 */
  --warning-50: #fffbeb;
  --warning-100: #fef3c7;
  --warning-500: #f59e0b;
  --warning-600: #d97706;
  
  /* 错误红色 - 用于错误、失败状态 */
  --error-50: #fef2f2;
  --error-100: #fee2e2;
  --error-500: #ef4444;
  --error-600: #dc2626;
  
  /* 中性色 - 用于文本、背景、边框 */
  --gray-50: #f9fafb;
  --gray-100: #f3f4f6;
  --gray-200: #e5e7eb;
  --gray-300: #d1d5db;
  --gray-400: #9ca3af;
  --gray-500: #6b7280;
  --gray-600: #4b5563;
  --gray-700: #374151;
  --gray-800: #1f2937;
  --gray-900: #111827;
  
  /* 代码编辑器专用色彩 */
  --code-bg: #1e1e1e;
  --code-text: #d4d4d4;
  --code-comment: #6a9955;
  --code-keyword: #569cd6;
  --code-string: #ce9178;
  --code-number: #b5cea8;
  --code-error: #f14c4c;
}
```

### 1.3 字体系统
```css
:root {
  /* 界面字体 */
  --font-sans: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  
  /* 代码字体 */  
  --font-mono: 'JetBrains Mono', 'Fira Code', 'SF Mono', Consolas, monospace;
  
  /* 字体大小 */
  --text-xs: 0.75rem;     /* 12px */
  --text-sm: 0.875rem;    /* 14px */
  --text-base: 1rem;      /* 16px */
  --text-lg: 1.125rem;    /* 18px */
  --text-xl: 1.25rem;     /* 20px */
  --text-2xl: 1.5rem;     /* 24px */
  --text-3xl: 1.875rem;   /* 30px */
  --text-4xl: 2.25rem;    /* 36px */
  
  /* 行高 */
  --leading-tight: 1.25;
  --leading-normal: 1.5;
  --leading-relaxed: 1.625;
}
```

### 1.4 间距系统
```css
:root {
  /* 间距标准 - 基于4px网格 */
  --space-1: 0.25rem;   /* 4px */
  --space-2: 0.5rem;    /* 8px */
  --space-3: 0.75rem;   /* 12px */
  --space-4: 1rem;      /* 16px */
  --space-5: 1.25rem;   /* 20px */
  --space-6: 1.5rem;    /* 24px */
  --space-8: 2rem;      /* 32px */
  --space-10: 2.5rem;   /* 40px */
  --space-12: 3rem;     /* 48px */
  --space-16: 4rem;     /* 64px */
  --space-20: 5rem;     /* 80px */
}
```

---

## 2. 核心组件设计规范

### 2.1 Button 按钮组件

#### A. 按钮变体和状态
```typescript
interface ButtonProps {
  variant: 'primary' | 'secondary' | 'success' | 'warning' | 'danger' | 'ghost';
  size: 'sm' | 'md' | 'lg';
  state: 'default' | 'hover' | 'active' | 'disabled' | 'loading';
  icon?: ReactNode;
  iconPosition?: 'left' | 'right';
  fullWidth?: boolean;
}
```

#### B. 视觉规范
```css
/* 主要按钮 - 用于核心操作 */
.btn-primary {
  background: var(--primary-500);
  color: white;
  border: 2px solid var(--primary-500);
  transition: all 200ms ease;
  box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1);
}

.btn-primary:hover {
  background: var(--primary-600);
  border-color: var(--primary-600);
  box-shadow: 0 4px 8px 0 rgba(59, 130, 246, 0.15);
  transform: translateY(-1px);
}

.btn-primary:active {
  background: var(--primary-700);
  transform: translateY(0);
  box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1);
}

/* 次要按钮 - 用于辅助操作 */
.btn-secondary {
  background: white;
  color: var(--gray-700);
  border: 2px solid var(--gray-300);
}

.btn-secondary:hover {
  background: var(--gray-50);
  border-color: var(--gray-400);
}

/* 成功按钮 - 用于确认、提交 */
.btn-success {
  background: var(--success-500);
  color: white;
  border: 2px solid var(--success-500);
}

/* 危险按钮 - 用于删除、重置 */
.btn-danger {
  background: var(--error-500);
  color: white;
  border: 2px solid var(--error-500);
}
```

#### C. 尺寸规范
```css
.btn-sm {
  padding: var(--space-2) var(--space-3);
  font-size: var(--text-sm);
  min-height: 2rem;
}

.btn-md {
  padding: var(--space-3) var(--space-4);
  font-size: var(--text-base);
  min-height: 2.5rem;
}

.btn-lg {
  padding: var(--space-4) var(--space-6);
  font-size: var(--text-lg);
  min-height: 3rem;
}
```

### 2.2 CodeEditor 代码编辑器组件

#### A. 编辑器配置
```typescript
interface CodeEditorProps {
  language: 'c' | 'python' | 'java';
  theme: 'light' | 'dark' | 'high-contrast';
  value: string;
  onChange: (value: string) => void;
  readOnly?: boolean;
  showLineNumbers?: boolean;
  showMinimap?: boolean;
  wordWrap?: 'on' | 'off' | 'wordWrapColumn';
  fontSize?: number;
  tabSize?: number;
  diagnostics?: Diagnostic[];
  onError?: (errors: Error[]) => void;
}
```

#### B. 主题样式
```css
/* 浅色主题 - 适合白天使用 */
.code-editor-light {
  background: #ffffff;
  color: var(--gray-800);
  border: 1px solid var(--gray-200);
  border-radius: 8px;
}

.code-editor-light .line-numbers {
  background: var(--gray-50);
  color: var(--gray-400);
  border-right: 1px solid var(--gray-200);
}

/* 深色主题 - 适合夜间或长时间使用 */
.code-editor-dark {
  background: #1e1e1e;
  color: #d4d4d4;
  border: 1px solid #3c3c3c;
}

/* 高对比度主题 - 无障碍支持 */
.code-editor-high-contrast {
  background: #000000;
  color: #ffffff;
  border: 2px solid #ffff00;
}
```

#### C. 语法高亮规则
```css
.token.comment { color: var(--code-comment); font-style: italic; }
.token.keyword { color: var(--code-keyword); font-weight: bold; }
.token.string { color: var(--code-string); }
.token.number { color: var(--code-number); }
.token.operator { color: var(--gray-600); }
.token.function { color: #dcdcaa; }
.token.variable { color: #9cdcfe; }
```

### 2.3 TestResult 测试结果组件

#### A. 组件结构
```typescript
interface TestResultProps {
  results: TestCase[];
  overallStatus: 'pending' | 'running' | 'passed' | 'failed';
  executionTime?: number;
  memoryUsage?: number;
  onRerun?: () => void;
  showDetails?: boolean;
}

interface TestCase {
  id: string;
  name: string;
  status: 'passed' | 'failed' | 'timeout';
  input: string;
  expected: string;
  actual?: string;
  error?: string;
  executionTime?: number;
}
```

#### B. 状态指示器设计
```css
/* 测试状态颜色编码 */
.test-status-passed {
  background: var(--success-50);
  color: var(--success-700);
  border-left: 4px solid var(--success-500);
}

.test-status-failed {
  background: var(--error-50);
  color: var(--error-700);
  border-left: 4px solid var(--error-500);
}

.test-status-running {
  background: var(--warning-50);
  color: var(--warning-700);
  border-left: 4px solid var(--warning-500);
}

/* 测试结果对比 */
.test-comparison {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: var(--space-4);
  margin-top: var(--space-3);
}

.test-expected, .test-actual {
  padding: var(--space-3);
  border-radius: 6px;
  font-family: var(--font-mono);
  font-size: var(--text-sm);
}

.test-expected {
  background: var(--success-50);
  border: 1px solid var(--success-200);
}

.test-actual.failed {
  background: var(--error-50);
  border: 1px solid var(--error-200);
}
```

### 2.4 FeedbackPanel 反馈面板组件

#### A. 反馈类型和结构
```typescript
interface FeedbackPanelProps {
  feedback: AIFeedback;
  editable?: boolean;
  onEdit?: (feedback: AIFeedback) => void;
  onApprove?: () => void;
  onReject?: () => void;
  showTeacherControls?: boolean;
}

interface AIFeedback {
  overallScore: number;
  categories: {
    syntax: FeedbackCategory;
    logic: FeedbackCategory;
    performance: FeedbackCategory;
    style: FeedbackCategory;
  };
  suggestions: string[];
  strengths: string[];
  improvements: string[];
  teacherNotes?: string;
}

interface FeedbackCategory {
  score: number;
  status: 'excellent' | 'good' | 'needs_improvement' | 'poor';
  comments: string[];
}
```

#### B. 评分可视化设计
```css
/* 整体评分圆环 */
.score-ring {
  position: relative;
  width: 80px;
  height: 80px;
  border-radius: 50%;
  background: conic-gradient(
    var(--success-500) 0deg,
    var(--success-500) calc(var(--score) * 3.6deg),
    var(--gray-200) calc(var(--score) * 3.6deg),
    var(--gray-200) 360deg
  );
}

.score-ring::before {
  content: '';
  position: absolute;
  top: 8px;
  left: 8px;
  width: 64px;
  height: 64px;
  border-radius: 50%;
  background: white;
}

.score-text {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  font-size: var(--text-xl);
  font-weight: 700;
  color: var(--gray-700);
}

/* 分类评分条 */
.category-score {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  padding: var(--space-3);
  border-radius: 8px;
  background: var(--gray-50);
  margin-bottom: var(--space-2);
}

.score-bar {
  flex: 1;
  height: 8px;
  border-radius: 4px;
  background: var(--gray-200);
  overflow: hidden;
}

.score-fill {
  height: 100%;
  border-radius: 4px;
  transition: width 500ms ease;
}

.score-fill.excellent { background: var(--success-500); }
.score-fill.good { background: var(--primary-500); }
.score-fill.needs_improvement { background: var(--warning-500); }
.score-fill.poor { background: var(--error-500); }
```

### 2.5 StatusIndicator 状态指示器组件

#### A. 状态类型定义
```typescript
interface StatusIndicatorProps {
  status: 'success' | 'warning' | 'error' | 'info' | 'loading';
  size?: 'sm' | 'md' | 'lg';
  animated?: boolean;
  showText?: boolean;
  text?: string;
}
```

#### B. 状态样式规范
```css
.status-indicator {
  display: inline-flex;
  align-items: center;
  gap: var(--space-2);
  font-size: var(--text-sm);
  font-weight: 500;
}

.status-dot {
  border-radius: 50%;
  flex-shrink: 0;
}

.status-dot.sm { width: 8px; height: 8px; }
.status-dot.md { width: 12px; height: 12px; }
.status-dot.lg { width: 16px; height: 16px; }

.status-success {
  background: var(--success-500);
  color: var(--success-700);
}

.status-warning {
  background: var(--warning-500);
  color: var(--warning-700);
}

.status-error {
  background: var(--error-500);
  color: var(--error-700);
}

.status-loading {
  background: var(--primary-500);
  animation: pulse 2s ease-in-out infinite alternate;
}

@keyframes pulse {
  from { opacity: 1; }
  to { opacity: 0.5; }
}
```

---

## 3. 布局组件规范

### 3.1 Grid 栅格系统
```css
.grid-container {
  display: grid;
  gap: var(--space-6);
  width: 100%;
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 var(--space-4);
}

/* 12列栅格系统 */
.grid-12 { grid-template-columns: repeat(12, 1fr); }
.grid-8 { grid-template-columns: repeat(8, 1fr); }
.grid-6 { grid-template-columns: repeat(6, 1fr); }
.grid-4 { grid-template-columns: repeat(4, 1fr); }
.grid-3 { grid-template-columns: repeat(3, 1fr); }
.grid-2 { grid-template-columns: repeat(2, 1fr); }

/* 响应式断点 */
@media (max-width: 768px) {
  .grid-container { padding: 0 var(--space-3); }
  .grid-12, .grid-8, .grid-6, .grid-4, .grid-3, .grid-2 {
    grid-template-columns: 1fr;
  }
}

@media (min-width: 769px) and (max-width: 1024px) {
  .grid-12 { grid-template-columns: repeat(8, 1fr); }
  .grid-8, .grid-6 { grid-template-columns: repeat(4, 1fr); }
  .grid-4, .grid-3 { grid-template-columns: repeat(2, 1fr); }
}
```

### 3.2 Card 卡片组件
```css
.card {
  background: white;
  border-radius: 12px;
  border: 1px solid var(--gray-200);
  box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1);
  transition: all 200ms ease;
  overflow: hidden;
}

.card:hover {
  box-shadow: 0 4px 12px 0 rgba(0, 0, 0, 0.15);
  transform: translateY(-2px);
}

.card-header {
  padding: var(--space-4) var(--space-6);
  border-bottom: 1px solid var(--gray-200);
  background: var(--gray-50);
}

.card-body {
  padding: var(--space-6);
}

.card-footer {
  padding: var(--space-4) var(--space-6);
  border-top: 1px solid var(--gray-200);
  background: var(--gray-50);
}
```

### 3.3 Modal 模态框组件
```css
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.5);
  backdrop-filter: blur(4px);
  z-index: 1000;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: var(--space-4);
}

.modal-content {
  background: white;
  border-radius: 16px;
  box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25);
  max-width: 90vw;
  max-height: 90vh;
  overflow: auto;
  animation: modalSlideIn 300ms ease;
}

@keyframes modalSlideIn {
  from {
    opacity: 0;
    transform: scale(0.9) translateY(20px);
  }
  to {
    opacity: 1;
    transform: scale(1) translateY(0);
  }
}

.modal-header {
  padding: var(--space-6);
  border-bottom: 1px solid var(--gray-200);
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.modal-body {
  padding: var(--space-6);
}

.modal-footer {
  padding: var(--space-4) var(--space-6);
  border-top: 1px solid var(--gray-200);
  display: flex;
  gap: var(--space-3);
  justify-content: flex-end;
}
```

---

## 4. 交互动画规范

### 4.1 过渡动画
```css
/* 标准过渡时长 */
:root {
  --duration-fast: 150ms;
  --duration-normal: 300ms;
  --duration-slow: 500ms;
  
  --ease-out: cubic-bezier(0.25, 0.46, 0.45, 0.94);
  --ease-in: cubic-bezier(0.55, 0.055, 0.675, 0.19);
  --ease-in-out: cubic-bezier(0.645, 0.045, 0.355, 1);
}

/* 悬停效果 */
.interactive {
  transition: all var(--duration-fast) var(--ease-out);
}

.interactive:hover {
  transform: translateY(-2px);
}

/* 加载动画 */
.loading-spinner {
  animation: spin var(--duration-slow) linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

/* 淡入动画 */
.fade-in {
  animation: fadeIn var(--duration-normal) var(--ease-out);
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

/* 滑入动画 */
.slide-in-up {
  animation: slideInUp var(--duration-normal) var(--ease-out);
}

@keyframes slideInUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
```

### 4.2 微交互动画
```css
/* 按钮点击反馈 */
.btn-click-feedback {
  position: relative;
  overflow: hidden;
}

.btn-click-feedback::before {
  content: '';
  position: absolute;
  top: 50%;
  left: 50%;
  width: 0;
  height: 0;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.3);
  transition: all var(--duration-fast) var(--ease-out);
  transform: translate(-50%, -50%);
}

.btn-click-feedback:active::before {
  width: 200px;
  height: 200px;
}

/* 成功状态动画 */
.success-checkmark {
  stroke-dasharray: 16;
  stroke-dashoffset: 16;
  animation: checkmark var(--duration-normal) var(--ease-out) forwards;
}

@keyframes checkmark {
  to {
    stroke-dashoffset: 0;
  }
}

/* 错误摇摆动画 */
.error-shake {
  animation: shake var(--duration-fast) ease-in-out 2;
}

@keyframes shake {
  0%, 100% { transform: translateX(0); }
  25% { transform: translateX(-5px); }
  75% { transform: translateX(5px); }
}
```

---

## 5. 响应式设计规范

### 5.1 断点系统
```css
/* 移动端优先断点 */
:root {
  --mobile: 0;
  --tablet: 768px;
  --desktop: 1024px;
  --large: 1440px;
}

/* 响应式工具类 */
.hidden { display: none; }
.block { display: block; }
.flex { display: flex; }
.grid { display: grid; }

@media (min-width: 768px) {
  .md\:hidden { display: none; }
  .md\:block { display: block; }
  .md\:flex { display: flex; }
  .md\:grid { display: grid; }
}

@media (min-width: 1024px) {
  .lg\:hidden { display: none; }
  .lg\:block { display: block; }
  .lg\:flex { display: flex; }
  .lg\:grid { display: grid; }
}
```

### 5.2 容器适配
```css
.container {
  width: 100%;
  margin: 0 auto;
  padding: 0 var(--space-4);
}

@media (min-width: 768px) {
  .container {
    max-width: 728px;
  }
}

@media (min-width: 1024px) {
  .container {
    max-width: 984px;
  }
}

@media (min-width: 1440px) {
  .container {
    max-width: 1200px;
  }
}
```

---

## 6. 无障碍设计规范

### 6.1 颜色对比度
```css
/* 确保文字与背景对比度 ≥ 4.5:1 */
.text-contrast {
  color: var(--gray-700);
  background: white;
}

.text-high-contrast {
  color: var(--gray-900);
  background: white;
}

/* 链接可见性 */
.link {
  color: var(--primary-600);
  text-decoration: underline;
  text-underline-offset: 2px;
}

.link:hover,
.link:focus {
  color: var(--primary-700);
  text-decoration-thickness: 2px;
}
```

### 6.2 焦点指示器
```css
/* 键盘焦点样式 */
.focusable:focus-visible {
  outline: 2px solid var(--primary-500);
  outline-offset: 2px;
  border-radius: 4px;
}

/* 跳过链接 */
.skip-link {
  position: absolute;
  top: -40px;
  left: 6px;
  background: var(--primary-500);
  color: white;
  padding: var(--space-2) var(--space-4);
  border-radius: 4px;
  text-decoration: none;
  z-index: 1000;
}

.skip-link:focus {
  top: 6px;
}
```

### 6.3 屏幕阅读器支持
```css
/* 视觉隐藏但屏幕阅读器可读 */
.sr-only {
  position: absolute;
  width: 1px;
  height: 1px;
  padding: 0;
  margin: -1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  white-space: nowrap;
  border: 0;
}

/* ARIA状态指示 */
[aria-disabled="true"] {
  opacity: 0.5;
  pointer-events: none;
}

[aria-expanded="true"] .expand-icon {
  transform: rotate(180deg);
}
```

---

## 7. 组件使用指南

### 7.1 组件组合规则
- **一致性**: 同类功能使用相同组件
- **层级性**: 重要操作使用主要样式，次要操作使用次要样式
- **上下文性**: 根据使用场景选择合适的组件变体
- **可访问性**: 确保所有组件支持键盘导航和屏幕阅读器

### 7.2 自定义组件指南
```typescript
// 组件开发模板
interface CustomComponentProps {
  className?: string;
  children?: ReactNode;
  // ... 其他props
}

const CustomComponent: React.FC<CustomComponentProps> = ({
  className,
  children,
  ...props
}) => {
  return (
    <div
      className={cn('base-styles', className)}
      {...props}
    >
      {children}
    </div>
  );
};

// 使用cn函数合并class名称，确保样式优先级正确
```

### 7.3 组件测试标准
```typescript
// 组件测试要求
describe('Component', () => {
  test('应该正确渲染', () => {
    render(<Component />);
    expect(screen.getByRole('button')).toBeInTheDocument();
  });
  
  test('应该支持键盘导航', () => {
    render(<Component />);
    const element = screen.getByRole('button');
    element.focus();
    expect(element).toHaveFocus();
  });
  
  test('应该满足无障碍标准', async () => {
    const { container } = render(<Component />);
    const results = await axe(container);
    expect(results).toHaveNoViolations();
  });
});
```

这套UI组件库标准为AI教学助手系统提供了完整的设计语言和实现规范，确保界面的一致性、可用性和可访问性。