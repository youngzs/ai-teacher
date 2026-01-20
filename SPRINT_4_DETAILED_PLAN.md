# Sprint 4 详细实施计划

**目标**: 完善用户体验 (M2: 完整用户体验)
**时间**: Sprint 4
**里程碑**: M2 - 完整用户体验，教师工具完善

---

## 一、Sprint 4 总览

### 1.1 目标

基于Sprint 3完成的核心功能闭环，Sprint 4聚焦于提升用户体验：

1. **前端功能完善** - 专业代码编辑器体验
2. **教师工具开发** - 高效批量管理工具
3. **学习进度可视化** - 直观的数据展示
4. **测试覆盖提升** - 确保代码质量

### 1.2 关键交付物

| 交付物 | 优先级 | 说明 |
|--------|--------|------|
| Monaco Editor组件 | P0 | 专业级代码编辑体验 |
| 代码运行服务 | P0 | 实时代码执行和测试 |
| 批量批改界面 | P1 | 教师效率工具 |
| 反馈模板系统 | P1 | 可复用反馈模板 |
| 学习进度图表 | P1 | Chart.js可视化 |
| 知识点热力图 | P2 | 掌握程度可视化 |
| API单元测试 | P1 | 测试覆盖率提升 |

---

## 二、任务详细计划

### 2.1 前端功能完善 (4.1)

#### 4.1.1 集成Monaco Editor代码编辑器

**目标**: 替换当前textarea为专业级Monaco Editor

**技术方案**:
```typescript
// 安装依赖
npm install @monaco-editor/react monaco-editor

// 组件结构
ai-teacher-frontend/src/components/
├── editor/
│   ├── MonacoCodeEditor.tsx      // 主编辑器组件
│   ├── EditorToolbar.tsx         // 工具栏组件
│   ├── EditorThemeProvider.tsx   // 主题提供者
│   ├── languageConfigs.ts        // 语言配置
│   └── index.ts                  // 导出
```

**功能需求**:
- [x] 语法高亮 (C, Python, Java, JavaScript)
- [x] 代码自动补全
- [x] 代码折叠
- [x] 行号显示
- [x] 错误标记显示
- [x] 主题切换 (vs-dark, vs-light)
- [x] 字体大小调节
- [x] 快捷键支持
- [x] 迷你地图 (可选)
- [x] 自动缩进

**代码示例**:
```tsx
// MonacoCodeEditor.tsx
import Editor, { Monaco } from '@monaco-editor/react';
import { editor } from 'monaco-editor';

interface MonacoCodeEditorProps {
  value: string;
  onChange: (value: string) => void;
  language: 'c' | 'python' | 'java' | 'javascript';
  theme?: 'vs-dark' | 'vs-light';
  readOnly?: boolean;
  errors?: CodeError[];
  onSave?: () => void;
}

export const MonacoCodeEditor: React.FC<MonacoCodeEditorProps> = ({
  value,
  onChange,
  language,
  theme = 'vs-dark',
  readOnly = false,
  errors = [],
  onSave
}) => {
  const handleEditorMount = (editor: editor.IStandaloneCodeEditor, monaco: Monaco) => {
    // 配置快捷键
    editor.addCommand(monaco.KeyMod.CtrlCmd | monaco.KeyCode.KeyS, () => {
      onSave?.();
    });

    // 设置错误标记
    if (errors.length > 0) {
      const markers = errors.map(err => ({
        startLineNumber: err.line,
        startColumn: err.column,
        endLineNumber: err.line,
        endColumn: err.column + 10,
        message: err.message,
        severity: monaco.MarkerSeverity.Error
      }));
      monaco.editor.setModelMarkers(editor.getModel()!, 'owner', markers);
    }
  };

  return (
    <Editor
      height="500px"
      language={language}
      theme={theme}
      value={value}
      onChange={(val) => onChange(val || '')}
      onMount={handleEditorMount}
      options={{
        minimap: { enabled: true },
        fontSize: 14,
        lineNumbers: 'on',
        folding: true,
        automaticLayout: true,
        readOnly
      }}
    />
  );
};
```

#### 4.1.2 实现代码运行测试功能

**目标**: 提供实时代码执行和测试结果展示

**后端API扩展**:
```python
# app/api/code_execution.py
@router.post("/execute")
async def execute_code(
    code: str,
    language: str,
    test_cases: List[TestCase],
    timeout: int = 10
) -> ExecutionResult:
    """
    执行代码并返回结果
    支持: C, Python, Java
    """
    pass

@router.post("/run-tests")
async def run_tests(
    submission_id: str,
    test_cases: List[TestCase]
) -> TestResults:
    """
    运行测试用例
    """
    pass
```

**前端组件**:
```typescript
// 组件结构
ai-teacher-frontend/src/components/
├── execution/
│   ├── CodeRunner.tsx           // 代码运行器
│   ├── TestCaseRunner.tsx       // 测试用例运行
│   ├── ExecutionOutput.tsx      // 输出展示
│   ├── TestResultsPanel.tsx     // 测试结果面板
│   └── index.ts
```

**功能需求**:
- [x] 代码编译和运行
- [x] 标准输入输出
- [x] 测试用例执行
- [x] 运行时间和内存统计
- [x] 错误信息展示
- [x] 执行状态指示 (运行中/成功/失败)

---

### 2.2 教师工具开发 (4.2)

#### 4.2.1 批量批改界面

**目标**: 提供高效的批量批改工作流

**页面结构**:
```typescript
// 页面路径: /teacher/batch-grading
// 文件: ai-teacher-frontend/src/pages/teacher/BatchGradingPage.tsx

interface BatchGradingPageProps {
  assignmentId: string;
}

// 功能:
// 1. 待批改列表 (筛选、排序)
// 2. 批量选择
// 3. 批量操作 (批准AI反馈、拒绝、重新生成)
// 4. 快速预览代码和反馈
// 5. 进度统计
```

**组件设计**:
```typescript
// 组件结构
ai-teacher-frontend/src/components/teacher/
├── BatchGradingTable.tsx        // 批量批改表格
├── SubmissionPreview.tsx        // 提交预览
├── QuickActions.tsx             // 快捷操作
├── BatchProgressBar.tsx         // 批量进度条
├── GradingFilters.tsx           // 筛选器
└── index.ts
```

**功能需求**:
- [x] 分页显示待批改提交
- [x] 按状态/分数/时间筛选
- [x] 批量选择 (全选/取消)
- [x] 批量批准AI反馈
- [x] 批量要求修改
- [x] 快速预览 (代码 + AI反馈)
- [x] 单个详细查看
- [x] 进度统计 (已批改/待批改/总数)

#### 4.2.2 反馈模板系统

**目标**: 提供可复用的反馈模板管理

**数据模型扩展**:
```python
# app/database/models.py
class FeedbackTemplate(Base):
    """反馈模板表"""
    __tablename__ = "feedback_templates"

    id = Column(UUID, primary_key=True)
    teacher_id = Column(UUID, ForeignKey("users.id"))
    name = Column(String(100), nullable=False)
    category = Column(String(50))  # syntax, logic, style, performance
    content = Column(Text, nullable=False)
    variables = Column(JSONB, default=[])  # 模板变量
    is_public = Column(Boolean, default=False)
    usage_count = Column(Integer, default=0)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)
```

**API端点**:
```python
# app/api/templates.py
@router.get("/templates")           # 获取模板列表
@router.post("/templates")          # 创建模板
@router.get("/templates/{id}")      # 获取单个模板
@router.put("/templates/{id}")      # 更新模板
@router.delete("/templates/{id}")   # 删除模板
@router.post("/templates/{id}/use") # 使用模板生成反馈
```

**前端组件**:
```typescript
// 组件结构
ai-teacher-frontend/src/components/teacher/
├── templates/
│   ├── TemplateManager.tsx       // 模板管理器
│   ├── TemplateEditor.tsx        // 模板编辑器
│   ├── TemplateSelector.tsx      // 模板选择器
│   ├── TemplatePreview.tsx       // 模板预览
│   └── index.ts
```

---

### 2.3 学习进度可视化 (4.3)

#### 4.3.1 学习进度图表组件

**目标**: 使用Chart.js实现丰富的数据可视化

**安装依赖**:
```bash
npm install chart.js react-chartjs-2
```

**组件结构**:
```typescript
// 组件结构
ai-teacher-frontend/src/components/charts/
├── ProgressChart.tsx             // 进度折线图
├── SkillRadarChart.tsx           // 技能雷达图
├── ScoreDistributionChart.tsx    // 分数分布图
├── SubmissionTrendChart.tsx      // 提交趋势图
├── ComparisonBarChart.tsx        // 对比柱状图
└── index.ts
```

**具体图表**:

1. **个人进度折线图**
```tsx
// ProgressChart.tsx
import { Line } from 'react-chartjs-2';

interface ProgressChartProps {
  data: {
    date: string;
    score: number;
  }[];
}

// 显示: 时间 vs 分数趋势
```

2. **技能雷达图**
```tsx
// SkillRadarChart.tsx
import { Radar } from 'react-chartjs-2';

interface SkillRadarChartProps {
  skills: {
    name: string;
    score: number;
    maxScore: number;
  }[];
}

// 显示: 语法、逻辑、调试、算法、最佳实践等维度
```

3. **班级对比柱状图**
```tsx
// ComparisonBarChart.tsx
import { Bar } from 'react-chartjs-2';

interface ComparisonBarChartProps {
  students: {
    name: string;
    averageScore: number;
  }[];
}

// 显示: 班级学生成绩对比
```

#### 4.3.2 知识点掌握热力图

**目标**: 可视化展示知识点掌握程度

**组件设计**:
```typescript
// 组件: KnowledgeHeatmap.tsx
import React from 'react';

interface KnowledgePoint {
  id: string;
  name: string;
  category: string;
  masteryLevel: number; // 0-100
  practiceCount: number;
  lastPracticed: string;
}

interface KnowledgeHeatmapProps {
  knowledgePoints: KnowledgePoint[];
  onPointClick?: (point: KnowledgePoint) => void;
}

// 颜色映射:
// 0-25: 红色 (未掌握)
// 25-50: 橙色 (初步了解)
// 50-75: 黄色 (基本掌握)
// 75-100: 绿色 (熟练掌握)
```

**页面集成**:
```typescript
// 学生进度页面增强
// 文件: ai-teacher-frontend/src/pages/student/ProgressTracker.tsx

// 新增:
// 1. 技能雷达图
// 2. 进度折线图
// 3. 知识点热力图
// 4. 学习时间统计
// 5. 成就徽章展示
```

---

### 2.4 测试覆盖提升 (4.4)

#### 4.4.1 API端点单元测试

**目标**: 将测试覆盖率从30%提升到70%

**测试文件结构**:
```python
# tests/
├── unit/
│   ├── test_auth.py              # 认证API测试
│   ├── test_submissions.py       # 提交API测试
│   ├── test_analysis.py          # 分析API测试
│   ├── test_courses.py           # 课程API测试
│   ├── test_users.py             # 用户API测试
│   └── test_dashboard.py         # 仪表板API测试
├── integration/
│   ├── test_ai_service.py        # AI服务集成测试
│   ├── test_database.py          # 数据库集成测试
│   └── test_workflow.py          # 工作流集成测试
└── conftest.py                   # 测试配置和fixtures
```

**测试示例**:
```python
# tests/unit/test_submissions.py
import pytest
from httpx import AsyncClient
from app.main import app

@pytest.fixture
async def authenticated_client():
    async with AsyncClient(app=app, base_url="http://test") as client:
        # 模拟登录
        response = await client.post("/api/v1/auth/login", json={
            "email": "test@example.com",
            "password": "testpassword"
        })
        token = response.json()["access_token"]
        client.headers["Authorization"] = f"Bearer {token}"
        yield client

class TestSubmissions:
    async def test_create_submission(self, authenticated_client):
        """测试创建提交"""
        response = await authenticated_client.post("/api/v1/submissions/", json={
            "code": "print('hello')",
            "language": "python",
            "assignment_description": "测试作业"
        })
        assert response.status_code == 200
        assert response.json()["success"] == True

    async def test_get_submission(self, authenticated_client):
        """测试获取提交"""
        # 先创建
        create_response = await authenticated_client.post("/api/v1/submissions/", json={
            "code": "print('hello')",
            "language": "python",
            "assignment_description": "测试作业"
        })
        submission_id = create_response.json()["data"]["id"]

        # 再获取
        response = await authenticated_client.get(f"/api/v1/submissions/{submission_id}")
        assert response.status_code == 200
```

#### 4.4.2 前端组件测试

**测试框架**: Vitest + Testing Library

**测试文件结构**:
```typescript
// ai-teacher-frontend/src/
├── components/
│   └── __tests__/
│       ├── Button.test.tsx
│       ├── CodeEditor.test.tsx
│       ├── Modal.test.tsx
│       └── Table.test.tsx
├── pages/
│   └── __tests__/
│       ├── LoginPage.test.tsx
│       ├── StudentDashboard.test.tsx
│       └── TeacherDashboard.test.tsx
└── hooks/
    └── __tests__/
        ├── useAuth.test.ts
        └── useApi.test.ts
```

**测试示例**:
```typescript
// src/components/__tests__/MonacoCodeEditor.test.tsx
import { render, screen, fireEvent } from '@testing-library/react';
import { MonacoCodeEditor } from '../editor/MonacoCodeEditor';

describe('MonacoCodeEditor', () => {
  it('renders with initial value', () => {
    render(
      <MonacoCodeEditor
        value="print('hello')"
        onChange={() => {}}
        language="python"
      />
    );
    expect(screen.getByRole('textbox')).toBeInTheDocument();
  });

  it('calls onChange when content changes', () => {
    const handleChange = vi.fn();
    render(
      <MonacoCodeEditor
        value=""
        onChange={handleChange}
        language="python"
      />
    );
    // 模拟编辑器内容变化
    // ...
  });
});
```

---

## 三、实施顺序

### Phase 1: 代码编辑器升级 (4.1)
1. 安装Monaco Editor依赖
2. 创建MonacoCodeEditor组件
3. 创建EditorToolbar组件
4. 替换现有textarea编辑器
5. 添加代码运行功能

### Phase 2: 教师工具 (4.2)
1. 创建批量批改页面
2. 实现批量操作API
3. 创建反馈模板数据模型
4. 实现模板管理API
5. 创建前端模板组件

### Phase 3: 可视化图表 (4.3)
1. 安装Chart.js依赖
2. 创建基础图表组件
3. 创建知识点热力图
4. 集成到学生进度页面
5. 集成到教师分析页面

### Phase 4: 测试覆盖 (4.4)
1. 配置测试环境
2. 编写API单元测试
3. 编写前端组件测试
4. 运行测试并修复问题
5. 生成覆盖率报告

---

## 四、风险与缓解措施

| 风险 | 影响 | 缓解措施 |
|------|------|----------|
| Monaco Editor包体积大 | 首屏加载慢 | 懒加载、代码分割 |
| 代码执行安全风险 | 系统安全 | 沙箱隔离、资源限制 |
| 图表性能问题 | 大数据卡顿 | 数据聚合、分页加载 |
| 测试覆盖时间不足 | 质量风险 | 优先核心路径测试 |

---

## 五、验收标准

### 功能验收
- [ ] Monaco Editor正常工作，支持C/Python/Java
- [ ] 代码运行功能可用，正确返回结果
- [ ] 批量批改界面可用，支持批量操作
- [ ] 反馈模板系统可用，支持CRUD
- [ ] 学习进度图表正确显示数据
- [ ] 知识点热力图颜色正确映射

### 性能验收
- [ ] 编辑器首次加载 < 3秒
- [ ] 代码运行响应 < 5秒
- [ ] 图表渲染 < 1秒
- [ ] 页面交互流畅，无卡顿

### 测试验收
- [ ] API测试覆盖率 > 60%
- [ ] 前端组件测试覆盖率 > 50%
- [ ] 所有测试通过

---

**文档版本**: v1.0
**创建日期**: 2026-01-20
**下次评审**: Sprint 4完成后
