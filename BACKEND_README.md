# AI教学助手系统 - FastAPI后端

这是AI教学助手系统的FastAPI后端实现，提供完整的RESTful API服务，集成了现有的AI Agent系统。

## 🚀 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 环境配置

复制环境变量模板并配置：

```bash
cp .env.example .env
```

编辑 `.env` 文件，配置以下关键参数：

```env
# 数据库配置
DATABASE_URL=postgresql+asyncpg://ai_teacher:password@localhost:5432/ai_teacher_db

# Redis配置
REDIS_URL=redis://localhost:6379/0

# AI服务配置
OPENAI_API_KEY=your-openai-api-key

# 安全配置
SECRET_KEY=your-super-secret-key
```

### 3. 数据库初始化

```bash
python init_db.py
```

这将创建数据库表并添加默认管理员用户：
- 用户名: `admin`
- 密码: `admin123456`
- 邮箱: `admin@aiteacher.local`

### 4. 启动服务

```bash
python start_server.py
```

服务将在 `http://localhost:8000` 启动。

## 📚 API文档

- **Swagger UI**: http://localhost:8000/api/docs
- **ReDoc**: http://localhost:8000/api/redoc
- **健康检查**: http://localhost:8000/health

## 🏗️ 项目结构

```
app/
├── main.py              # FastAPI主应用
├── core/                # 核心配置
│   ├── config.py       # 应用配置
│   └── security.py     # 安全认证
├── api/                 # API端点
│   ├── auth.py         # 认证相关
│   ├── submissions.py  # 代码提交
│   ├── analysis.py     # AI分析
│   ├── users.py        # 用户管理
│   └── dashboard.py    # 仪表板
├── database/           # 数据库相关
│   ├── database.py     # 数据库配置
│   └── models.py       # 数据模型
├── schemas/            # Pydantic模式
│   ├── common.py       # 通用模式
│   ├── auth.py         # 认证模式
│   ├── submissions.py  # 提交模式
│   └── analysis.py     # 分析模式
├── services/           # 业务服务
│   └── ai_service.py   # AI服务集成
└── utils/              # 工具函数
    ├── logger.py       # 日志配置
    ├── email.py        # 邮件服务
    └── cache.py        # 缓存管理
```

## 🔌 API端点概览

### 认证相关 (`/api/v1/auth`)
- `POST /register` - 用户注册
- `POST /login` - 用户登录
- `POST /refresh` - 刷新令牌
- `POST /logout` - 用户登出
- `POST /password-reset` - 请求密码重置
- `POST /password-reset/confirm` - 确认密码重置
- `GET /me` - 获取当前用户信息

### 代码提交 (`/api/v1/submissions`)
- `POST /` - 创建代码提交
- `GET /{submission_id}` - 获取提交详情
- `GET /` - 获取提交列表（分页）
- `PUT /{submission_id}` - 更新提交
- `DELETE /{submission_id}` - 删除提交
- `POST /batch` - 批量创建提交

### AI分析 (`/api/v1/analysis`)
- `POST /` - 执行代码分析
- `GET /feedback/{submission_id}` - 获取AI反馈
- `POST /debug` - 调试代码
- `POST /batch` - 批量分析
- `GET /history/{student_id}` - 获取分析历史

### 用户管理 (`/api/v1/users`)
- `GET /profile` - 获取用户资料
- `PUT /profile` - 更新用户资料
- `GET /stats` - 获取用户统计
- `GET /activity` - 获取用户活动
- `GET /preferences` - 获取用户偏好
- `PUT /preferences` - 更新用户偏好
- `DELETE /account` - 删除用户账户

### 仪表板 (`/api/v1/dashboard`)
- `GET /overview` - 获取概览信息
- `GET /recent-activity` - 获取最近活动
- `GET /analytics` - 获取分析数据
- `GET /system-health` - 获取系统健康状态（管理员）

## 🤖 AI系统集成

后端完整集成了现有的AI Agent系统：

### 多Agent架构
- **CodeAnalyzer**: 代码技术分析
- **PedagogyExpert**: 教学策略制定
- **StudentProfiler**: 学生画像分析
- **FeedbackGenerator**: 反馈内容生成
- **QualityController**: 质量控制检查
- **DebuggingMentor**: 调试指导

### 工作流支持
- **作业分析工作流**: 完整的代码评估和反馈生成
- **调试指导工作流**: 苏格拉底式调试引导
- **个性化学习工作流**: 基于学习历史的个性化建议

### 异步处理
- 所有AI分析都采用异步处理
- 支持批量分析和并发处理
- 配置连接池和超时控制
- 完整的错误处理和重试机制

## 🗄️ 数据库设计

### 核心表结构
- **users**: 用户信息
- **submissions**: 代码提交记录
- **ai_feedback**: AI分析反馈
- **student_profiles**: 学生学习画像
- **teaching_sessions**: 教学会话记录

### 性能优化
- 适当的数据库索引
- 连接池配置
- 查询优化
- 数据分页

## 🔒 安全特性

### 认证与授权
- JWT令牌认证
- 刷新令牌机制
- 基于角色的权限控制
- API密钥支持

### 安全防护
- 速率限制
- CORS配置
- 安全头部设置
- 输入验证和过滤
- SQL注入防护

### 数据保护
- 密码加密存储
- 敏感数据脱敏
- 审计日志记录

## 📊 监控与日志

### 日志系统
- 结构化日志记录
- 多级别日志输出
- 日志轮转和压缩
- 性能指标记录

### 健康检查
- 数据库连接状态
- AI服务状态
- 系统资源使用情况
- API响应时间监控

## 🚀 部署指南

### 开发环境
```bash
# 启动开发服务器
python start_server.py
```

### 生产环境
```bash
# 使用Gunicorn
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000

# 或使用Docker（需要创建Dockerfile）
docker build -t ai-teacher-backend .
docker run -p 8000:8000 ai-teacher-backend
```

### 环境变量配置
生产环境必需配置：
- `ENVIRONMENT=production`
- `DEBUG=false`
- `SECRET_KEY` - 强密钥
- `DATABASE_URL` - 生产数据库
- `REDIS_URL` - Redis缓存
- `OPENAI_API_KEY` - OpenAI API密钥
- `ALLOWED_HOSTS` - 允许的域名

## 🧪 测试

```bash
# 运行测试
pytest

# 运行测试并生成覆盖率报告
pytest --cov=app --cov-report=html
```

## 🔧 开发工具

### 代码质量
```bash
# 代码格式化
black app/
isort app/

# 代码检查
flake8 app/
mypy app/
```

### 数据库迁移
```bash
# 生成迁移文件（需要安装Alembic）
alembic revision --autogenerate -m "description"

# 执行迁移
alembic upgrade head
```

## 📈 性能优化

### API性能
- 异步处理
- 连接池优化
- 缓存策略
- 查询优化

### AI处理优化
- 任务队列
- 并发控制
- 结果缓存
- 超时处理

## 🤝 贡献指南

1. Fork项目
2. 创建特性分支
3. 提交代码更改
4. 创建Pull Request

请确保：
- 遵循代码规范
- 添加必要的测试
- 更新文档
- 通过CI检查

## 📞 技术支持

如有问题或建议，请通过以下方式联系：
- 创建GitHub Issue
- 发送邮件到开发团队

---

**注意**: 这是MVP版本的后端实现，专注于核心功能。后续版本将添加更多高级特性如实时通知、高级分析、多租户支持等。