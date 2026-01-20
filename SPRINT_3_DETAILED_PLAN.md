# Sprint 3 详细实施计划

**里程碑**: M1 - 核心功能闭环
**目标**: 完成核心功能的完整闭环，使系统能够实际处理学生提交、生成AI反馈、持久化存储数据
**预计工作量**: 4个主要任务模块

---

## 执行摘要

Sprint 3 聚焦于解决当前系统的核心问题，实现从"可演示"到"可使用"的跨越：

| 任务模块 | 优先级 | 复杂度 | 依赖关系 |
|---------|--------|--------|---------|
| 3.1 数据库连接修复 | P0 | 中 | 无 |
| 3.2 OpenAI API集成 | P0 | 高 | 3.1 |
| 3.3 数据持久化完善 | P0 | 中 | 3.1, 3.2 |
| 3.4 课程数据导入 | P1 | 低 | 3.1 |

---

## 任务 3.1: 数据库连接修复

### 3.1.1 问题分析

**当前状态**:
- 数据库层代码完整 (`app/database/database.py`)
- 17个数据模型定义完成 (`app/database/models.py`)
- 连接池配置存在但未经生产验证

**已发现问题**:
```python
# app/database/database.py:111-113
# 健康检查使用的text()函数需要正确导入
result = await session.execute(text("SELECT 1"))  # 需验证
```

**风险项**:
1. 连接池参数未针对并发场景优化
2. 缺少连接重试机制
3. 事务超时配置缺失

### 3.1.2 实施步骤

#### Step 1: 验证数据库连接配置
```python
# 文件: app/database/database.py
# 任务: 优化连接池配置

# 修改前
engine = create_async_engine(
    settings.DATABASE_URL,
    pool_size=settings.DATABASE_POOL_SIZE,
    max_overflow=settings.DATABASE_MAX_OVERFLOW,
)

# 修改后 - 添加健壮性配置
engine = create_async_engine(
    settings.DATABASE_URL,
    pool_size=settings.DATABASE_POOL_SIZE,          # 默认10
    max_overflow=settings.DATABASE_MAX_OVERFLOW,     # 默认20
    pool_pre_ping=True,                              # 连接前验证
    pool_recycle=3600,                               # 1小时回收
    pool_timeout=30,                                 # 连接超时30秒
    connect_args={
        "server_settings": {
            "application_name": "ai_teaching_assistant",
            "statement_timeout": "60000",            # SQL超时60秒
        },
        "command_timeout": 60,                       # 命令超时
    }
)
```

#### Step 2: 添加连接重试机制
```python
# 文件: app/database/database.py (新增函数)

import asyncio
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10)
)
async def get_db_with_retry() -> AsyncGenerator[AsyncSession, None]:
    """带重试机制的数据库会话获取"""
    async with SessionLocal() as session:
        try:
            # 验证连接有效
            await session.execute(text("SELECT 1"))
            yield session
        except Exception as e:
            logger.error(f"Database session error: {str(e)}")
            await session.rollback()
            raise
        finally:
            await session.close()
```

#### Step 3: 增强健康检查
```python
# 文件: app/database/database.py

async def comprehensive_health_check() -> dict:
    """全面的数据库健康检查"""
    checks = {
        "connection": False,
        "read_write": False,
        "pool_status": {},
        "response_time_ms": 0,
        "errors": []
    }

    start_time = time.time()

    try:
        async with SessionLocal() as session:
            # 1. 基础连接检查
            result = await session.execute(text("SELECT 1"))
            checks["connection"] = result.scalar() == 1

            # 2. 读写能力检查 (使用临时表)
            await session.execute(text("""
                CREATE TEMP TABLE IF NOT EXISTS health_check_temp (
                    id SERIAL PRIMARY KEY,
                    timestamp TIMESTAMP DEFAULT NOW()
                )
            """))
            await session.execute(text(
                "INSERT INTO health_check_temp DEFAULT VALUES"
            ))
            checks["read_write"] = True

            # 3. 连接池状态
            pool = engine.pool
            checks["pool_status"] = {
                "size": pool.size(),
                "checked_in": pool.checkedin(),
                "checked_out": pool.checkedout(),
                "overflow": pool.overflow(),
                "utilization": f"{(pool.checkedout() / max(pool.size(), 1)) * 100:.1f}%"
            }

    except Exception as e:
        checks["errors"].append(str(e))

    checks["response_time_ms"] = round((time.time() - start_time) * 1000, 2)

    return checks
```

#### Step 4: 添加数据库初始化脚本
```python
# 文件: scripts/init_database.py (新建)

#!/usr/bin/env python3
"""数据库初始化脚本"""

import asyncio
import sys
sys.path.append('.')

from app.database.database import engine, Base, init_db, comprehensive_health_check
from app.database.models import *  # 导入所有模型
from app.core.config import settings

async def main():
    print("=" * 50)
    print("AI Teaching Assistant - Database Initialization")
    print("=" * 50)

    # 1. 健康检查
    print("\n[1/4] Checking database connection...")
    health = await comprehensive_health_check()

    if not health["connection"]:
        print(f"❌ Database connection failed: {health['errors']}")
        print(f"   Connection URL: {settings.DATABASE_URL.replace(settings.DATABASE_URL.split(':')[2].split('@')[0], '****')}")
        return False

    print(f"✅ Database connected (response: {health['response_time_ms']}ms)")

    # 2. 创建表
    print("\n[2/4] Creating database tables...")
    try:
        await init_db()
        print("✅ All tables created successfully")
    except Exception as e:
        print(f"❌ Table creation failed: {e}")
        return False

    # 3. 验证表结构
    print("\n[3/4] Verifying table structure...")
    from app.database.database import db_manager
    table_info = await db_manager.get_table_info()

    expected_tables = [
        'users', 'classes', 'class_memberships', 'assignments',
        'submissions', 'ai_feedback', 'student_profiles',
        'teaching_sessions', 'courses', 'lessons',
        'course_exercises', 'learning_paths'
    ]

    missing_tables = [t for t in expected_tables if t not in table_info]
    if missing_tables:
        print(f"⚠️  Missing tables: {missing_tables}")
    else:
        print(f"✅ All {len(expected_tables)} expected tables exist")

    # 4. 显示表统计
    print("\n[4/4] Table Statistics:")
    print("-" * 40)
    for table, info in sorted(table_info.items()):
        print(f"  {table:<25} | {info['rows']:>6} rows")
    print("-" * 40)

    print("\n✅ Database initialization completed!")
    return True

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
```

### 3.1.3 验收标准

| 验收项 | 标准 | 验证方法 |
|--------|------|---------|
| 连接稳定性 | 1000次连接无失败 | 压力测试脚本 |
| 连接池性能 | 30并发下响应<100ms | Locust测试 |
| 健康检查 | 返回完整状态信息 | API调用 `/health/db` |
| 错误恢复 | 断连后自动重连 | 模拟网络中断 |

### 3.1.4 配置文件更新

```python
# 文件: app/core/config.py (更新)

class Settings(BaseSettings):
    # ... 现有配置 ...

    # 新增数据库高级配置
    DATABASE_POOL_TIMEOUT: int = Field(default=30, env="DATABASE_POOL_TIMEOUT")
    DATABASE_COMMAND_TIMEOUT: int = Field(default=60, env="DATABASE_COMMAND_TIMEOUT")
    DATABASE_STATEMENT_TIMEOUT: int = Field(default=60000, env="DATABASE_STATEMENT_TIMEOUT")
    DATABASE_RETRY_ATTEMPTS: int = Field(default=3, env="DATABASE_RETRY_ATTEMPTS")
```

---

## 任务 3.2: OpenAI API 集成

### 3.2.1 问题分析

**当前状态**:
- `src/agents/teaching_agents.py` 使用Mock AutoGen类
- Agent配置完整 (`src/config/agents_config.py`)
- AI服务层已封装 (`app/services/ai_service.py`)

**关键代码位置**:
```python
# src/agents/teaching_agents.py:15-43
# Mock实现 - 需要替换为真实API调用

try:
    from autogen import AssistantAgent, UserProxyAgent, GroupChat, GroupChatManager
except ImportError:
    # Mock classes - 这是当前使用的
    class AssistantAgent:
        ...
```

### 3.2.2 实施步骤

#### Step 1: 创建OpenAI客户端封装
```python
# 文件: src/core/openai_client.py (新建)

"""
OpenAI API 客户端封装
支持多种调用模式和错误处理
"""

from typing import Dict, Any, List, Optional
from openai import AsyncOpenAI
import asyncio
import json
from tenacity import retry, stop_after_attempt, wait_exponential
import tiktoken

from app.core.config import settings
from src.utils.logger import get_logger

logger = get_logger(__name__)


class OpenAIClient:
    """OpenAI API 客户端"""

    def __init__(self):
        self.client: Optional[AsyncOpenAI] = None
        self.model = settings.OPENAI_MODEL
        self.max_tokens = 4000
        self.temperature = 0.3
        self._initialized = False

        # Token计数器
        try:
            self.encoding = tiktoken.encoding_for_model(self.model)
        except KeyError:
            self.encoding = tiktoken.get_encoding("cl100k_base")

    async def initialize(self):
        """初始化OpenAI客户端"""
        if self._initialized:
            return

        api_key = settings.OPENAI_API_KEY

        if not api_key:
            logger.warning("OpenAI API key not configured, using mock mode")
            self._initialized = True
            return

        self.client = AsyncOpenAI(
            api_key=api_key,
            timeout=settings.AI_RESPONSE_TIMEOUT,
            max_retries=3
        )

        # 验证API密钥
        try:
            await self.client.models.list()
            logger.info("OpenAI API connection verified")
            self._initialized = True
        except Exception as e:
            logger.error(f"OpenAI API verification failed: {e}")
            self.client = None
            raise

    def count_tokens(self, text: str) -> int:
        """计算文本的token数量"""
        return len(self.encoding.encode(text))

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10)
    )
    async def chat_completion(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        response_format: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        执行聊天补全请求

        Args:
            messages: 消息列表
            model: 模型名称
            temperature: 温度参数
            max_tokens: 最大token数
            response_format: 响应格式（如JSON模式）

        Returns:
            API响应结果
        """
        if not self.client:
            return await self._mock_completion(messages)

        try:
            params = {
                "model": model or self.model,
                "messages": messages,
                "temperature": temperature or self.temperature,
                "max_tokens": max_tokens or self.max_tokens,
            }

            if response_format:
                params["response_format"] = response_format

            response = await self.client.chat.completions.create(**params)

            return {
                "success": True,
                "content": response.choices[0].message.content,
                "usage": {
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens
                },
                "model": response.model,
                "finish_reason": response.choices[0].finish_reason
            }

        except Exception as e:
            logger.error(f"OpenAI API call failed: {e}")
            raise

    async def _mock_completion(self, messages: List[Dict[str, str]]) -> Dict[str, Any]:
        """Mock模式的响应生成"""
        logger.info("Using mock completion mode")

        # 模拟延迟
        await asyncio.sleep(0.5)

        # 生成模拟响应
        last_message = messages[-1]["content"] if messages else ""

        mock_response = {
            "code_analysis": {
                "syntax_score": 85,
                "logic_score": 80,
                "style_score": 75,
                "performance_score": 70,
                "critical_errors": [],
                "suggestions": ["代码结构良好", "建议添加更多注释"]
            },
            "feedback": {
                "recognition": "你的代码展示了良好的编程基础。",
                "guidance": "继续练习可以进一步提高代码质量。",
                "next_steps": ["学习更多设计模式", "增加错误处理"]
            },
            "overall_score": 77.5
        }

        return {
            "success": True,
            "content": json.dumps(mock_response, ensure_ascii=False),
            "usage": {"prompt_tokens": 100, "completion_tokens": 200, "total_tokens": 300},
            "model": "mock-model",
            "finish_reason": "stop",
            "is_mock": True
        }

    async def analyze_code(
        self,
        code: str,
        language: str,
        assignment_description: str,
        student_context: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        专门的代码分析方法

        Args:
            code: 待分析的代码
            language: 编程语言
            assignment_description: 作业描述
            student_context: 学生上下文信息

        Returns:
            代码分析结果
        """
        system_prompt = self._build_code_analysis_system_prompt(language)
        user_prompt = self._build_code_analysis_user_prompt(
            code, assignment_description, student_context
        )

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]

        result = await self.chat_completion(
            messages=messages,
            response_format={"type": "json_object"}
        )

        if result["success"]:
            try:
                result["parsed_content"] = json.loads(result["content"])
            except json.JSONDecodeError:
                result["parsed_content"] = {"raw": result["content"]}

        return result

    def _build_code_analysis_system_prompt(self, language: str) -> str:
        """构建代码分析系统提示"""
        return f"""你是一位专业的{language}编程教学助手，专门帮助大学生学习编程。

你的任务是分析学生提交的代码，并提供教育性的反馈。

请以JSON格式返回分析结果，包含以下字段：
{{
    "code_analysis": {{
        "syntax_score": <0-100的语法评分>,
        "logic_score": <0-100的逻辑评分>,
        "style_score": <0-100的代码风格评分>,
        "performance_score": <0-100的性能评分>,
        "critical_errors": [<严重错误列表>],
        "warnings": [<警告列表>],
        "suggestions": [<改进建议列表>]
    }},
    "feedback": {{
        "recognition": "<肯定学生做得好的地方>",
        "reconstruction": {{
            "issues": [<需要改进的问题>],
            "steps": [<具体改进步骤>]
        }},
        "reinforcement": "<鼓励和下一步建议>"
    }},
    "learning_points": [<本次作业涉及的知识点>],
    "overall_score": <0-100的总体评分>,
    "difficulty_assessment": "<novice|beginner|intermediate|advanced>"
}}

反馈原则：
1. 使用鼓励性语言，避免打击学生积极性
2. 错误反馈要具体，给出改正方法
3. 根据学生水平调整反馈深度
4. 提供具体的代码示例（如果适用）"""

    def _build_code_analysis_user_prompt(
        self,
        code: str,
        assignment_description: str,
        student_context: Optional[Dict]
    ) -> str:
        """构建代码分析用户提示"""
        prompt = f"""请分析以下学生代码提交：

## 作业要求
{assignment_description}

## 学生代码
```
{code}
```
"""

        if student_context:
            prompt += f"""
## 学生背景信息
- 技能水平: {student_context.get('competency_level', '未知')}
- 历史平均分: {student_context.get('average_score', '未知')}
- 常见错误模式: {student_context.get('error_patterns', '未知')}
"""

        return prompt


# 全局客户端实例
_openai_client: Optional[OpenAIClient] = None


async def get_openai_client() -> OpenAIClient:
    """获取OpenAI客户端单例"""
    global _openai_client

    if _openai_client is None:
        _openai_client = OpenAIClient()
        await _openai_client.initialize()

    return _openai_client
```

#### Step 2: 重构Teaching Agents
```python
# 文件: src/agents/real_teaching_agents.py (新建)

"""
真实的AI Teaching Agents实现
使用OpenAI API替代Mock
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
import json
import asyncio

from src.core.openai_client import get_openai_client, OpenAIClient
from src.models.teaching_models import SubmissionData, TeachingFeedback
from src.config.agents_config import AgentRole, AgentConfigurations
from src.utils.logger import get_logger

logger = get_logger(__name__)


class RealTeachingAgent:
    """真实的教学Agent基类"""

    def __init__(self, role: AgentRole, openai_client: OpenAIClient):
        self.role = role
        self.client = openai_client
        self.config = AgentConfigurations.get_agent_config(role)
        self.name = self.config["name"]
        self.system_message = self.config["system_message"]

    async def process(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """处理输入并返回结果"""
        raise NotImplementedError


class CodeAnalyzerAgent(RealTeachingAgent):
    """代码分析Agent"""

    def __init__(self, openai_client: OpenAIClient):
        super().__init__(AgentRole.CODE_ANALYZER, openai_client)

    async def process(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """分析代码质量"""
        code = context.get("code", "")
        language = context.get("language", "python")

        result = await self.client.analyze_code(
            code=code,
            language=language,
            assignment_description=context.get("assignment_description", ""),
            student_context=context.get("student_context")
        )

        if result["success"]:
            return {
                "agent": self.name,
                "analysis": result.get("parsed_content", {}),
                "tokens_used": result.get("usage", {})
            }
        else:
            return {"agent": self.name, "error": "Analysis failed"}


class FeedbackGeneratorAgent(RealTeachingAgent):
    """反馈生成Agent"""

    def __init__(self, openai_client: OpenAIClient):
        super().__init__(AgentRole.FEEDBACK_GENERATOR, openai_client)

    async def process(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """基于分析结果生成教学反馈"""
        code_analysis = context.get("code_analysis", {})
        student_profile = context.get("student_profile", {})

        messages = [
            {"role": "system", "content": self.system_message},
            {"role": "user", "content": self._build_prompt(code_analysis, student_profile)}
        ]

        result = await self.client.chat_completion(
            messages=messages,
            response_format={"type": "json_object"}
        )

        if result["success"]:
            return {
                "agent": self.name,
                "feedback": json.loads(result["content"]),
                "tokens_used": result.get("usage", {})
            }
        else:
            return {"agent": self.name, "error": "Feedback generation failed"}

    def _build_prompt(self, code_analysis: Dict, student_profile: Dict) -> str:
        return f"""基于以下代码分析结果，生成个性化的教学反馈：

## 代码分析结果
{json.dumps(code_analysis, ensure_ascii=False, indent=2)}

## 学生画像
{json.dumps(student_profile, ensure_ascii=False, indent=2)}

请生成JSON格式的反馈，包含：recognition(肯定), reconstruction(改进建议), reinforcement(鼓励)"""


class RealMultiAgentTeachingSystem:
    """真实的多Agent教学系统"""

    def __init__(self):
        self.openai_client: Optional[OpenAIClient] = None
        self.agents: Dict[str, RealTeachingAgent] = {}
        self._initialized = False

    async def initialize(self):
        """初始化系统"""
        if self._initialized:
            return

        self.openai_client = await get_openai_client()

        # 创建所有Agent
        self.agents = {
            "CodeAnalyzer": CodeAnalyzerAgent(self.openai_client),
            "FeedbackGenerator": FeedbackGeneratorAgent(self.openai_client),
            # ... 其他Agent
        }

        self._initialized = True
        logger.info(f"Real Multi-Agent system initialized with {len(self.agents)} agents")

    async def process_submission(self, submission_data: SubmissionData) -> TeachingFeedback:
        """处理学生提交"""
        if not self._initialized:
            await self.initialize()

        start_time = datetime.now()

        # 构建上下文
        context = {
            "code": submission_data.code,
            "language": submission_data.language.value,
            "assignment_description": submission_data.assignment_description,
            "student_id": submission_data.student_id,
            "student_context": submission_data.student_history
        }

        # Step 1: 代码分析
        code_analysis_result = await self.agents["CodeAnalyzer"].process(context)
        context["code_analysis"] = code_analysis_result.get("analysis", {})

        # Step 2: 生成反馈
        feedback_result = await self.agents["FeedbackGenerator"].process(context)

        # 构建最终反馈
        analysis = context["code_analysis"]
        feedback = feedback_result.get("feedback", {})

        processing_time = (datetime.now() - start_time).total_seconds()

        return TeachingFeedback(
            session_id=f"session_{submission_data.student_id}_{int(datetime.now().timestamp())}",
            student_id=submission_data.student_id,
            overall_score=analysis.get("overall_score", 0),
            code_analysis=analysis.get("code_analysis", {}),
            student_profile={},
            teaching_strategy="STANDARD",
            feedback_content=feedback,
            recommendations=feedback.get("learning_points", []),
            quality_score=85,
            next_steps=feedback.get("reinforcement", {}).get("next_steps", []),
            estimated_completion_time="15-20分钟",
            created_at=datetime.now(),
            processing_time=processing_time
        )
```

#### Step 3: 更新AI服务层
```python
# 文件: app/services/ai_service.py (更新关键部分)

# 在 AITeachingService.__init__ 中添加
from src.agents.real_teaching_agents import RealMultiAgentTeachingSystem

class AITeachingService:
    def __init__(self):
        # ... 现有代码 ...
        self.use_real_api = settings.OPENAI_API_KEY is not None
        self.real_teaching_system: Optional[RealMultiAgentTeachingSystem] = None

    async def initialize(self):
        """初始化AI服务"""
        try:
            logger.info("Initializing AI Teaching Service...")

            if self.use_real_api:
                # 使用真实API
                self.real_teaching_system = RealMultiAgentTeachingSystem()
                await self.real_teaching_system.initialize()
                logger.info("Using REAL OpenAI API for AI analysis")
            else:
                # 使用Mock系统
                self.teaching_system = MultiAgentTeachingSystem("ai_teacher_backend")
                self.workflow_manager = WorkflowManager(self.teaching_system)
                logger.info("Using MOCK system for AI analysis (no API key)")

            self.is_initialized = True

        except Exception as e:
            logger.error(f"Failed to initialize AI Teaching Service: {str(e)}")
            raise

    async def process_submission(self, submission_data: SubmissionData) -> TeachingFeedback:
        """处理代码提交"""
        if not self.is_initialized:
            raise RuntimeError("AI service is not initialized")

        if self.use_real_api and self.real_teaching_system:
            return await self.real_teaching_system.process_submission(submission_data)
        else:
            # 使用原有Mock流程
            return await self._execute_assignment_analysis(submission_data, "mock_session")
```

### 3.2.3 环境变量配置

```bash
# .env 文件更新

# OpenAI API配置
OPENAI_API_KEY=sk-your-api-key-here
OPENAI_MODEL=gpt-4-turbo-preview
AI_RESPONSE_TIMEOUT=60
MAX_AI_SESSIONS=50

# 成本控制
OPENAI_MAX_TOKENS_PER_REQUEST=4000
OPENAI_DAILY_BUDGET_USD=50
OPENAI_RATE_LIMIT_RPM=60
```

### 3.2.4 验收标准

| 验收项 | 标准 | 验证方法 |
|--------|------|---------|
| API连接 | 成功验证API密钥 | 启动日志 |
| 代码分析 | 返回结构化JSON | 测试用例 |
| 响应时间 | <30秒 | 性能测试 |
| 错误处理 | 优雅降级到Mock | 故意失败测试 |
| 成本监控 | 记录token使用 | 日志检查 |

---

## 任务 3.3: 数据持久化完善

### 3.3.1 问题分析

**当前状态**:
- API端点已实现数据库操作 (`app/api/submissions.py`)
- 后台任务有数据保存逻辑
- 部分SQL语句使用字符串拼接（需修复）

**需要修复的代码**:
```python
# app/api/submissions.py:411
# 问题：使用字符串SQL
await db.execute("DELETE FROM ai_feedback WHERE submission_id = :id", {"id": submission_id})

# 修复为：
from sqlalchemy import delete
await db.execute(delete(AIFeedback).where(AIFeedback.submission_id == submission_id))
```

### 3.3.2 实施步骤

#### Step 1: 创建数据访问层(Repository)
```python
# 文件: app/repositories/__init__.py (新建目录和文件)

"""数据访问层 - Repository模式"""
```

```python
# 文件: app/repositories/submission_repository.py (新建)

"""提交数据仓库"""

from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, update, func, and_
from sqlalchemy.orm import selectinload
from datetime import datetime
import uuid

from app.database.models import Submission, AIFeedback, User
from app.utils.logger import get_logger

logger = get_logger(__name__)


class SubmissionRepository:
    """提交数据仓库"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(
        self,
        student_id: str,
        code: str,
        language: str,
        assignment_description: str,
        assignment_id: Optional[str] = None,
        student_message: Optional[str] = None
    ) -> Submission:
        """创建新提交"""
        submission = Submission(
            id=uuid.uuid4(),
            student_id=student_id,
            assignment_id=assignment_id,
            assignment_description=assignment_description,
            code=code,
            language=language,
            student_message=student_message,
            status="submitted",
            submitted_at=datetime.utcnow()
        )

        self.db.add(submission)
        await self.db.commit()
        await self.db.refresh(submission)

        logger.info(f"Created submission: {submission.id}")
        return submission

    async def get_by_id(self, submission_id: str) -> Optional[Submission]:
        """根据ID获取提交"""
        result = await self.db.execute(
            select(Submission)
            .options(selectinload(Submission.ai_feedback))
            .where(Submission.id == submission_id)
        )
        return result.scalar_one_or_none()

    async def get_by_student(
        self,
        student_id: str,
        limit: int = 20,
        offset: int = 0
    ) -> List[Submission]:
        """获取学生的所有提交"""
        result = await self.db.execute(
            select(Submission)
            .where(Submission.student_id == student_id)
            .order_by(Submission.submitted_at.desc())
            .limit(limit)
            .offset(offset)
        )
        return list(result.scalars().all())

    async def update_status(
        self,
        submission_id: str,
        status: str,
        processed_at: Optional[datetime] = None
    ) -> bool:
        """更新提交状态"""
        values = {"status": status, "updated_at": datetime.utcnow()}
        if processed_at:
            values["processed_at"] = processed_at

        result = await self.db.execute(
            update(Submission)
            .where(Submission.id == submission_id)
            .values(**values)
        )
        await self.db.commit()

        return result.rowcount > 0

    async def delete(self, submission_id: str) -> bool:
        """删除提交（级联删除AI反馈）"""
        # 先删除关联的AI反馈
        await self.db.execute(
            delete(AIFeedback).where(AIFeedback.submission_id == submission_id)
        )

        # 删除提交
        result = await self.db.execute(
            delete(Submission).where(Submission.id == submission_id)
        )
        await self.db.commit()

        return result.rowcount > 0

    async def count_by_student(self, student_id: str) -> int:
        """统计学生提交数量"""
        result = await self.db.execute(
            select(func.count(Submission.id))
            .where(Submission.student_id == student_id)
        )
        return result.scalar() or 0


class AIFeedbackRepository:
    """AI反馈数据仓库"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(
        self,
        submission_id: str,
        overall_score: float,
        analysis_result: Dict[str, Any],
        status: str = "completed",
        processing_time: Optional[float] = None,
        ai_model_version: Optional[str] = None
    ) -> AIFeedback:
        """创建AI反馈记录"""
        feedback = AIFeedback(
            id=uuid.uuid4(),
            submission_id=submission_id,
            overall_score=overall_score,
            analysis_result=analysis_result,
            status=status,
            processing_time=processing_time,
            ai_model_version=ai_model_version,
            created_at=datetime.utcnow()
        )

        self.db.add(feedback)
        await self.db.commit()
        await self.db.refresh(feedback)

        logger.info(f"Created AI feedback: {feedback.id} for submission: {submission_id}")
        return feedback

    async def get_by_submission(self, submission_id: str) -> Optional[AIFeedback]:
        """获取提交的最新AI反馈"""
        result = await self.db.execute(
            select(AIFeedback)
            .where(AIFeedback.submission_id == submission_id)
            .order_by(AIFeedback.created_at.desc())
            .limit(1)
        )
        return result.scalar_one_or_none()

    async def get_student_history(
        self,
        student_id: str,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """获取学生的反馈历史"""
        query = (
            select(
                AIFeedback.overall_score,
                AIFeedback.analysis_result,
                AIFeedback.created_at,
                Submission.language,
                Submission.assignment_id
            )
            .join(Submission, AIFeedback.submission_id == Submission.id)
            .where(
                and_(
                    Submission.student_id == student_id,
                    AIFeedback.status == "completed"
                )
            )
            .order_by(AIFeedback.created_at.desc())
            .limit(limit)
        )

        result = await self.db.execute(query)
        records = result.fetchall()

        return [
            {
                "score": r.overall_score,
                "analysis_summary": r.analysis_result,
                "created_at": r.created_at.isoformat(),
                "language": r.language,
                "assignment_id": r.assignment_id
            }
            for r in records
        ]

    async def mark_as_failed(
        self,
        submission_id: str,
        error_message: str
    ) -> AIFeedback:
        """标记分析失败"""
        return await self.create(
            submission_id=submission_id,
            overall_score=0.0,
            analysis_result={"error": error_message},
            status="failed"
        )
```

#### Step 2: 创建学习进度服务
```python
# 文件: app/services/learning_progress_service.py (新建)

"""学习进度追踪服务"""

from typing import Dict, Any, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from datetime import datetime, timedelta

from app.database.models import (
    Submission, AIFeedback, StudentProfile,
    LearningPath, StudentExerciseAttempt
)
from app.utils.logger import get_logger

logger = get_logger(__name__)


class LearningProgressService:
    """学习进度服务"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def update_student_profile(self, student_id: str) -> StudentProfile:
        """更新学生画像"""
        # 获取或创建学生画像
        result = await self.db.execute(
            select(StudentProfile).where(StudentProfile.student_id == student_id)
        )
        profile = result.scalar_one_or_none()

        if not profile:
            profile = StudentProfile(
                student_id=student_id,
                competency_level="novice",
                total_submissions=0,
                average_score=0.0
            )
            self.db.add(profile)

        # 计算统计数据
        stats = await self._calculate_student_stats(student_id)

        # 更新画像
        profile.total_submissions = stats["total_submissions"]
        profile.average_score = stats["average_score"]
        profile.competency_level = self._determine_competency_level(stats)
        profile.skill_scores = stats["skill_scores"]
        profile.error_patterns = stats["error_patterns"]
        profile.progress_trends = stats["progress_trends"]
        profile.last_analyzed = datetime.utcnow()
        profile.updated_at = datetime.utcnow()

        await self.db.commit()
        await self.db.refresh(profile)

        return profile

    async def _calculate_student_stats(self, student_id: str) -> Dict[str, Any]:
        """计算学生统计数据"""
        # 获取所有完成的反馈
        query = (
            select(AIFeedback.overall_score, AIFeedback.analysis_result)
            .join(Submission, AIFeedback.submission_id == Submission.id)
            .where(
                and_(
                    Submission.student_id == student_id,
                    AIFeedback.status == "completed"
                )
            )
            .order_by(AIFeedback.created_at.desc())
            .limit(50)
        )

        result = await self.db.execute(query)
        records = list(result.fetchall())

        if not records:
            return {
                "total_submissions": 0,
                "average_score": 0.0,
                "skill_scores": {},
                "error_patterns": {},
                "progress_trends": {}
            }

        scores = [r.overall_score for r in records]

        # 计算技能得分
        skill_scores = self._aggregate_skill_scores(records)

        # 分析错误模式
        error_patterns = self._analyze_error_patterns(records)

        # 计算进步趋势
        progress_trends = self._calculate_progress_trends(scores)

        return {
            "total_submissions": len(records),
            "average_score": sum(scores) / len(scores),
            "skill_scores": skill_scores,
            "error_patterns": error_patterns,
            "progress_trends": progress_trends
        }

    def _determine_competency_level(self, stats: Dict) -> str:
        """确定能力水平"""
        avg_score = stats.get("average_score", 0)
        submissions = stats.get("total_submissions", 0)

        if submissions < 3:
            return "novice"

        if avg_score >= 90:
            return "expert"
        elif avg_score >= 80:
            return "proficient"
        elif avg_score >= 70:
            return "competent"
        elif avg_score >= 60:
            return "advanced_beginner"
        else:
            return "novice"

    def _aggregate_skill_scores(self, records) -> Dict[str, float]:
        """聚合技能得分"""
        skills = {"syntax": [], "logic": [], "style": [], "performance": []}

        for record in records:
            analysis = record.analysis_result or {}
            code_analysis = analysis.get("code_analysis", {})

            if "syntax_score" in code_analysis:
                skills["syntax"].append(code_analysis["syntax_score"])
            if "logic_score" in code_analysis:
                skills["logic"].append(code_analysis["logic_score"])
            if "style_score" in code_analysis:
                skills["style"].append(code_analysis["style_score"])
            if "performance_score" in code_analysis:
                skills["performance"].append(code_analysis["performance_score"])

        return {
            skill: sum(scores) / len(scores) if scores else 0.0
            for skill, scores in skills.items()
        }

    def _analyze_error_patterns(self, records) -> Dict[str, int]:
        """分析错误模式"""
        patterns = {}

        for record in records:
            analysis = record.analysis_result or {}
            errors = analysis.get("code_analysis", {}).get("critical_errors", [])

            for error in errors:
                error_type = error.get("type", "unknown") if isinstance(error, dict) else str(error)
                patterns[error_type] = patterns.get(error_type, 0) + 1

        return patterns

    def _calculate_progress_trends(self, scores: List[float]) -> Dict[str, Any]:
        """计算进步趋势"""
        if len(scores) < 2:
            return {"trend": "insufficient_data"}

        recent_scores = scores[:10]  # 最近10次
        older_scores = scores[10:20] if len(scores) > 10 else []

        recent_avg = sum(recent_scores) / len(recent_scores)
        older_avg = sum(older_scores) / len(older_scores) if older_scores else recent_avg

        if recent_avg > older_avg + 5:
            trend = "improving"
        elif recent_avg < older_avg - 5:
            trend = "declining"
        else:
            trend = "stable"

        return {
            "trend": trend,
            "recent_average": round(recent_avg, 2),
            "older_average": round(older_avg, 2),
            "improvement": round(recent_avg - older_avg, 2)
        }

    async def get_learning_path_progress(
        self,
        student_id: str,
        course_id: str
    ) -> Dict[str, Any]:
        """获取学习路径进度"""
        result = await self.db.execute(
            select(LearningPath).where(
                and_(
                    LearningPath.student_id == student_id,
                    LearningPath.course_id == course_id
                )
            )
        )
        path = result.scalar_one_or_none()

        if not path:
            return {
                "enrolled": False,
                "progress_percentage": 0,
                "current_lesson": 0,
                "completed_lessons": []
            }

        return {
            "enrolled": True,
            "progress_percentage": path.progress_percentage,
            "current_lesson": path.current_lesson,
            "completed_lessons": path.completed_lessons,
            "learning_hours": path.learning_hours,
            "last_study_time": path.last_study_time.isoformat() if path.last_study_time else None,
            "status": path.status
        }
```

### 3.3.3 验收标准

| 验收项 | 标准 | 验证方法 |
|--------|------|---------|
| 提交保存 | 数据正确持久化 | 数据库查询验证 |
| AI反馈保存 | 完整JSON存储 | 数据完整性检查 |
| 学生画像更新 | 自动计算更新 | 提交后验证 |
| 查询性能 | <50ms | 性能测试 |
| 数据完整性 | 无孤立数据 | 外键约束验证 |

---

## 任务 3.4: 课程数据导入

### 3.4.1 问题分析

**当前状态**:
- 导入脚本完整 (`scripts/import_curriculum.py`)
- C语言课程文档完整 (`docs/education/c_language_detailed_curriculum.md`)
- 数据库表结构已定义

**阻塞问题**:
- 数据库连接配置可能不匹配
- 需要先完成3.1数据库修复

### 3.4.2 实施步骤

#### Step 1: 修复导入脚本
```python
# 文件: scripts/import_curriculum.py (修改DatabaseImporter类)

class DatabaseImporter:
    """数据库导入器 - 修复版"""

    def __init__(self):
        # 使用与app相同的配置
        from app.core.config import settings
        self.db_url = settings.DATABASE_URL.replace(
            "postgresql+asyncpg://",
            "postgresql://"
        )
        self.conn = None

    async def connect(self):
        """连接数据库（带重试）"""
        import asyncpg
        from tenacity import retry, stop_after_attempt, wait_fixed

        @retry(stop=stop_after_attempt(3), wait=wait_fixed(2))
        async def _connect():
            return await asyncpg.connect(self.db_url)

        try:
            self.conn = await _connect()

            # 验证连接
            result = await self.conn.fetchval("SELECT 1")
            if result == 1:
                print("✅ 数据库连接成功")
            return True
        except Exception as e:
            print(f"❌ 数据库连接失败: {e}")
            raise
```

#### Step 2: 创建导入验证脚本
```python
# 文件: scripts/verify_curriculum_import.py (新建)

#!/usr/bin/env python3
"""验证课程数据导入结果"""

import asyncio
import sys
sys.path.append('.')

from app.database.database import SessionLocal
from sqlalchemy import select, func
from app.database.models import Course, Lesson, CourseExercise


async def verify_import():
    """验证导入数据"""
    print("=" * 50)
    print("课程数据导入验证")
    print("=" * 50)

    async with SessionLocal() as db:
        # 1. 检查课程
        courses = await db.execute(select(Course))
        course_list = list(courses.scalars().all())
        print(f"\n📚 课程数量: {len(course_list)}")

        for course in course_list:
            print(f"   - {course.name} ({course.code})")
            print(f"     语言: {course.language}, 课时: {course.total_hours}")

        # 2. 检查课时
        lessons_count = await db.execute(
            select(func.count(Lesson.id))
        )
        total_lessons = lessons_count.scalar()
        print(f"\n📖 总课时数: {total_lessons}")

        # 3. 检查练习
        exercises_count = await db.execute(
            select(func.count(CourseExercise.id))
        )
        total_exercises = exercises_count.scalar()
        print(f"\n📝 总练习数: {total_exercises}")

        # 4. 数据完整性检查
        print("\n🔍 数据完整性检查:")

        # 检查孤立课时
        orphan_lessons = await db.execute(
            select(Lesson)
            .outerjoin(Course, Lesson.course_id == Course.id)
            .where(Course.id == None)
        )
        orphan_count = len(list(orphan_lessons.scalars().all()))
        print(f"   - 孤立课时: {orphan_count} {'✅' if orphan_count == 0 else '⚠️'}")

    print("\n" + "=" * 50)
    print("验证完成")
    print("=" * 50)


if __name__ == "__main__":
    asyncio.run(verify_import())
```

### 3.4.3 验收标准

| 验收项 | 标准 | 验证方法 |
|--------|------|---------|
| 课程导入 | 1门C语言课程 | 验证脚本 |
| 课时导入 | ≥20个课时 | 数据库查询 |
| 练习导入 | ≥50道练习题 | 数据库查询 |
| 数据完整性 | 无孤立数据 | 完整性检查 |

---

## 测试计划

### 单元测试
```python
# tests/test_sprint3.py

import pytest
from unittest.mock import Mock, AsyncMock, patch

class TestDatabaseConnection:
    """数据库连接测试"""

    @pytest.mark.asyncio
    async def test_connection_health_check(self):
        """测试健康检查"""
        from app.database.database import comprehensive_health_check

        result = await comprehensive_health_check()

        assert result["connection"] == True
        assert "pool_status" in result
        assert result["response_time_ms"] < 100

class TestOpenAIClient:
    """OpenAI客户端测试"""

    @pytest.mark.asyncio
    async def test_mock_completion(self):
        """测试Mock模式"""
        from src.core.openai_client import OpenAIClient

        client = OpenAIClient()
        await client.initialize()

        result = await client._mock_completion([
            {"role": "user", "content": "test"}
        ])

        assert result["success"] == True
        assert "is_mock" in result

class TestSubmissionRepository:
    """提交仓库测试"""

    @pytest.mark.asyncio
    async def test_create_submission(self, db_session):
        """测试创建提交"""
        from app.repositories.submission_repository import SubmissionRepository

        repo = SubmissionRepository(db_session)

        submission = await repo.create(
            student_id="test-student-id",
            code="print('hello')",
            language="python",
            assignment_description="Test assignment"
        )

        assert submission.id is not None
        assert submission.status == "submitted"
```

### 集成测试
```python
# tests/integration/test_full_workflow.py

@pytest.mark.asyncio
async def test_full_submission_workflow():
    """测试完整的提交工作流"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        # 1. 登录
        login_response = await client.post("/api/v1/auth/login", json={
            "username": "test_student",
            "password": "test_password"
        })
        token = login_response.json()["data"]["access_token"]

        # 2. 提交代码
        headers = {"Authorization": f"Bearer {token}"}
        submission_response = await client.post(
            "/api/v1/submissions/",
            headers=headers,
            json={
                "code": "print('hello world')",
                "language": "python",
                "assignment_description": "Print hello world"
            }
        )

        assert submission_response.status_code == 200
        submission_id = submission_response.json()["data"]["id"]

        # 3. 等待AI分析完成
        await asyncio.sleep(5)

        # 4. 获取反馈
        feedback_response = await client.get(
            f"/api/v1/analysis/feedback/{submission_id}",
            headers=headers
        )

        assert feedback_response.status_code == 200
        assert feedback_response.json()["data"]["status"] == "completed"
```

---

## 执行顺序和依赖关系

```
                    ┌─────────────────┐
                    │  3.1 数据库修复  │
                    │    (优先级: P0)  │
                    └────────┬────────┘
                             │
              ┌──────────────┼──────────────┐
              │              │              │
              ▼              ▼              ▼
     ┌────────────┐  ┌─────────────┐  ┌───────────┐
     │ 3.2 OpenAI │  │ 3.3 数据持久 │  │ 3.4 课程  │
     │  API集成   │  │    化完善    │  │  数据导入  │
     │  (P0)      │  │   (P0)      │  │  (P1)     │
     └─────┬──────┘  └──────┬──────┘  └───────────┘
           │                │
           └────────┬───────┘
                    │
                    ▼
           ┌───────────────┐
           │  集成测试验证  │
           │   (所有完成后) │
           └───────────────┘
```

---

## 风险与缓解措施

| 风险 | 影响 | 概率 | 缓解措施 |
|------|------|------|---------|
| OpenAI API配额限制 | 高 | 中 | 实现缓存、设置日预算告警 |
| 数据库迁移问题 | 高 | 低 | 备份数据、增量迁移、回滚计划 |
| 性能不达标 | 中 | 中 | 连接池调优、查询优化、异步处理 |
| 数据导入失败 | 低 | 低 | 分批导入、事务回滚、验证脚本 |

---

## 交付物检查清单

### 代码交付
- [ ] `app/database/database.py` - 数据库连接优化
- [ ] `scripts/init_database.py` - 数据库初始化脚本
- [ ] `src/core/openai_client.py` - OpenAI客户端封装
- [ ] `src/agents/real_teaching_agents.py` - 真实Agent实现
- [ ] `app/repositories/submission_repository.py` - 数据访问层
- [ ] `app/services/learning_progress_service.py` - 学习进度服务
- [ ] `scripts/verify_curriculum_import.py` - 导入验证脚本

### 配置文件
- [ ] `.env.example` 更新
- [ ] `requirements.txt` 更新 (添加tenacity, openai等)

### 测试文件
- [ ] `tests/test_sprint3.py` - Sprint 3单元测试
- [ ] `tests/integration/test_full_workflow.py` - 集成测试

### 文档更新
- [ ] `README.md` 更新配置说明
- [ ] `DEVELOPMENT_SETUP.md` 更新开发指南

---

**文档版本**: v1.0
**创建日期**: 2026-01-19
**预计完成**: 根据团队资源安排
**负责人**: 待分配
