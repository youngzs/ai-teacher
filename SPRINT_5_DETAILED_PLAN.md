# Sprint 5 详细实施计划 - 生产就绪

**Sprint目标**: M3 - 系统生产就绪，可部署上线
**计划周期**: Sprint 5
**优先级**: 完善优化

---

## 一、Sprint 5 任务总览

### 任务分解

| 编号 | 任务 | 优先级 | 预计工时 | 状态 |
|------|------|--------|----------|------|
| 5.1.1 | Prometheus监控指标完善 | P0 | 4h | 待开始 |
| 5.1.2 | Grafana仪表板配置 | P0 | 3h | 待开始 |
| 5.1.3 | 日志聚合系统实现 | P1 | 4h | 待开始 |
| 5.1.4 | 告警规则配置 | P1 | 2h | 待开始 |
| 5.2.1 | 数据库查询优化 | P0 | 4h | 待开始 |
| 5.2.2 | API响应缓存优化 | P1 | 3h | 待开始 |
| 5.2.3 | 前端性能优化 | P1 | 3h | 待开始 |
| 5.3.1 | 安全审计与加固 | P0 | 4h | 待开始 |
| 5.4.1 | 智能出题系统基础版 | P2 | 6h | 待开始 |

---

## 二、监控系统完善 (5.1)

### 5.1.1 Prometheus监控指标

#### 需要收集的指标

```yaml
# 应用指标
application_metrics:
  - http_requests_total: HTTP请求总数
  - http_request_duration_seconds: 请求延迟分布
  - http_request_size_bytes: 请求大小
  - http_response_size_bytes: 响应大小
  - active_connections: 活跃连接数

# AI服务指标
ai_service_metrics:
  - ai_analysis_requests_total: AI分析请求数
  - ai_analysis_duration_seconds: AI分析耗时
  - ai_api_calls_total: OpenAI API调用次数
  - ai_api_cost_usd: API调用成本(USD)
  - ai_cache_hit_ratio: 缓存命中率

# 代码执行指标
code_execution_metrics:
  - code_execution_total: 代码执行总数
  - code_execution_duration_seconds: 执行耗时
  - code_execution_success_rate: 执行成功率
  - code_compilation_errors: 编译错误数

# 数据库指标
database_metrics:
  - db_connections_active: 活跃连接数
  - db_connections_idle: 空闲连接数
  - db_query_duration_seconds: 查询耗时
  - db_pool_size: 连接池大小

# 系统指标
system_metrics:
  - process_cpu_seconds_total: CPU使用时间
  - process_resident_memory_bytes: 内存使用
  - process_open_fds: 打开文件描述符数
```

#### 实现代码结构

```python
# app/core/metrics.py
from prometheus_client import Counter, Histogram, Gauge, CollectorRegistry

# HTTP指标
http_requests_total = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status']
)

http_request_duration = Histogram(
    'http_request_duration_seconds',
    'HTTP request duration',
    ['method', 'endpoint'],
    buckets=[0.01, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0]
)

# AI服务指标
ai_analysis_duration = Histogram(
    'ai_analysis_duration_seconds',
    'AI analysis duration',
    ['analysis_type'],
    buckets=[0.1, 0.5, 1.0, 2.0, 5.0, 10.0, 30.0]
)

ai_api_cost = Counter(
    'ai_api_cost_usd_total',
    'Total AI API cost in USD',
    ['model']
)
```

### 5.1.2 Grafana仪表板配置

#### 仪表板结构

```
┌──────────────────────────────────────────────────────────────────┐
│                    AI Teaching Assistant Dashboard                │
├──────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐    │
│  │   QPS总览      │ │   响应延迟 P99  │ │   错误率        │    │
│  │     1.2K       │ │     45ms        │ │     0.1%       │    │
│  └─────────────────┘ └─────────────────┘ └─────────────────┘    │
│                                                                  │
│  ┌────────────────────────────────────────────────────────────┐  │
│  │              请求量趋势 (24h)                              │  │
│  │  ▂▃▅▆▇█▇▆▅▄▃▂▁▂▃▄▅▆▇█▇▆▅▄▃▂▁▂▃▄▅                         │  │
│  └────────────────────────────────────────────────────────────┘  │
│                                                                  │
│  ┌──────────────────────┐ ┌──────────────────────┐              │
│  │  AI分析延迟分布       │ │  API端点响应时间      │              │
│  │  ┌────────────────┐  │ │  /api/v1/analysis    │              │
│  │  │   ▁▂▃▅▇█▅▃▂▁  │  │ │  /api/v1/submissions │              │
│  │  └────────────────┘  │ │  /api/v1/execution   │              │
│  └──────────────────────┘ └──────────────────────┘              │
│                                                                  │
│  ┌──────────────────────┐ ┌──────────────────────┐              │
│  │  数据库连接池状态     │ │  AI API成本追踪       │              │
│  │  Active: 5/20       │ │  Today: $12.50       │              │
│  │  Idle: 15/20        │ │  Month: $380.00      │              │
│  └──────────────────────┘ └──────────────────────┘              │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
```

### 5.1.3 日志聚合系统

#### 日志配置

```python
# 结构化日志格式
log_format = {
    "timestamp": "ISO8601",
    "level": "INFO/WARN/ERROR",
    "service": "ai-teacher-api",
    "trace_id": "uuid",
    "span_id": "uuid",
    "user_id": "optional",
    "message": "string",
    "extra": {}
}
```

### 5.1.4 告警规则

```yaml
# alerting_rules.yml
groups:
  - name: ai_teacher_alerts
    rules:
      - alert: HighErrorRate
        expr: sum(rate(http_requests_total{status=~"5.."}[5m])) / sum(rate(http_requests_total[5m])) > 0.05
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "High error rate detected"

      - alert: AIServiceSlow
        expr: histogram_quantile(0.99, rate(ai_analysis_duration_seconds_bucket[5m])) > 10
        for: 10m
        labels:
          severity: warning
        annotations:
          summary: "AI analysis is slow"

      - alert: DatabaseConnectionPoolExhausted
        expr: db_connections_active / db_pool_size > 0.9
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "Database connection pool near exhaustion"
```

---

## 三、性能优化 (5.2)

### 5.2.1 数据库查询优化

#### 索引优化

```sql
-- 提交表索引优化
CREATE INDEX idx_submissions_user_created ON submissions(user_id, created_at DESC);
CREATE INDEX idx_submissions_assignment ON submissions(assignment_id, status);

-- AI反馈表索引
CREATE INDEX idx_ai_feedback_submission ON ai_feedback(submission_id);
CREATE INDEX idx_ai_feedback_created ON ai_feedback(created_at DESC);

-- 用户活动索引
CREATE INDEX idx_user_activity_user_time ON user_activity(user_id, timestamp DESC);

-- 学习进度索引
CREATE INDEX idx_learning_progress_student_course ON learning_progress(student_id, course_id);
```

#### 查询优化策略

```python
# 使用预加载避免N+1问题
from sqlalchemy.orm import selectinload, joinedload

async def get_submissions_with_feedback(user_id: str):
    return await db.execute(
        select(Submission)
        .options(selectinload(Submission.ai_feedback))
        .where(Submission.user_id == user_id)
        .order_by(Submission.created_at.desc())
        .limit(50)
    )
```

### 5.2.2 API响应缓存优化

#### 缓存策略

```python
# 多层缓存策略
cache_strategies = {
    # 静态数据 - 长期缓存
    "course_list": {"ttl": 3600, "strategy": "cache_aside"},
    "supported_languages": {"ttl": 86400, "strategy": "cache_aside"},

    # 用户数据 - 短期缓存
    "user_profile": {"ttl": 300, "strategy": "cache_aside"},
    "user_submissions": {"ttl": 60, "strategy": "cache_aside"},

    # AI分析 - 内容寻址缓存
    "ai_analysis": {"ttl": 1800, "strategy": "content_hash"},
}
```

### 5.2.3 前端性能优化

#### 优化清单

```typescript
// 代码分割
const MonacoEditor = lazy(() => import('./components/editor/MonacoCodeEditor'));
const Charts = lazy(() => import('./components/charts'));

// 虚拟滚动
import { FixedSizeList } from 'react-window';

// 图片优化
// - WebP格式支持
// - 懒加载
// - 响应式图片

// Bundle优化
// - Tree shaking
// - 压缩混淆
// - 依赖分析
```

---

## 四、安全加固 (5.3)

### 5.3.1 安全审计清单

```yaml
security_audit:
  authentication:
    - JWT token过期时间检查
    - 刷新token机制
    - 密码强度策略
    - 登录尝试限制

  authorization:
    - RBAC权限验证
    - 资源所有权检查
    - API端点权限

  input_validation:
    - SQL注入防护(ORM)
    - XSS防护(内容转义)
    - CSRF保护(token)
    - 文件上传验证

  data_protection:
    - 敏感数据加密
    - 日志脱敏
    - 传输加密(HTTPS)

  code_security:
    - 依赖漏洞扫描
    - 代码静态分析
    - 密钥管理
```

### 安全中间件增强

```python
# app/core/security_middleware.py
class SecurityMiddleware:
    """安全中间件"""

    # Content Security Policy
    CSP_POLICY = {
        "default-src": "'self'",
        "script-src": "'self' 'unsafe-inline'",
        "style-src": "'self' 'unsafe-inline'",
        "img-src": "'self' data: https:",
        "connect-src": "'self'",
    }

    # 速率限制
    RATE_LIMITS = {
        "auth": "5/minute",
        "api": "100/minute",
        "code_execution": "10/minute",
    }
```

---

## 五、智能出题系统 (5.4)

### 5.4.1 基础版功能

#### 出题引擎设计

```python
class QuestionGenerator:
    """智能出题生成器"""

    async def generate_question(
        self,
        topic: str,
        difficulty: str,
        question_type: str,
        context: dict
    ) -> Question:
        """
        根据主题和难度生成编程题目

        Args:
            topic: 知识点主题
            difficulty: beginner/intermediate/advanced
            question_type: coding/multiple_choice/fill_blank
            context: 学生画像等上下文
        """
        pass

    async def generate_test_cases(
        self,
        question: Question,
        count: int = 5
    ) -> List[TestCase]:
        """为题目生成测试用例"""
        pass
```

#### 题目模板系统

```python
question_templates = {
    "coding": {
        "basic_loop": {
            "template": "编写一个程序，{action}。输入{input_desc}，输出{output_desc}。",
            "variables": ["action", "input_desc", "output_desc"],
            "difficulty_range": ["beginner", "intermediate"],
        },
        "function_impl": {
            "template": "实现函数 {function_name}({params})，功能为{description}。",
            "variables": ["function_name", "params", "description"],
            "difficulty_range": ["intermediate", "advanced"],
        },
    },
    "multiple_choice": {
        "concept": {
            "template": "关于{concept}，以下说法正确的是？",
            "variables": ["concept"],
        },
    },
}
```

---

## 六、验收标准

### 功能验收

| 功能 | 验收标准 |
|------|----------|
| 监控系统 | Prometheus指标可访问，Grafana仪表板可用 |
| 日志系统 | 结构化日志输出，可按trace_id追踪 |
| 告警系统 | 错误率>5%时触发告警 |
| 数据库优化 | 复杂查询<100ms |
| API缓存 | 缓存命中率>60% |
| 安全加固 | 通过OWASP Top 10检查 |
| 智能出题 | 能生成基础编程题 |

### 性能指标

| 指标 | 目标值 |
|------|--------|
| API响应时间P99 | <200ms |
| AI分析时间P99 | <5s |
| 页面加载时间 | <2s |
| 错误率 | <0.1% |
| 系统可用性 | >99.9% |

---

**文档版本**: v1.0
**创建日期**: 2026-01-20
**最后更新**: 2026-01-20
