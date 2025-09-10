# 后端架构设计与实施指导

**目标读者**: Backend Architect Developer  
**项目**: AI教学助手系统后端服务  
**版本**: v1.0  
**更新日期**: 2024-01-22

---

## 🎯 后端架构总体设计

### 架构概述
```
AI教学助手后端架构
├── API网关层 (API Gateway Layer)
├── 业务服务层 (Business Service Layer)
├── AI集成层 (AI Integration Layer)
├── 数据访问层 (Data Access Layer)
├── 缓存层 (Cache Layer)
└── 存储层 (Storage Layer)
```

### 技术栈选择
- **Web框架**: FastAPI 0.100+
- **Python版本**: 3.11+
- **数据库**: PostgreSQL 15+
- **缓存**: Redis 7+
- **ORM**: SQLAlchemy 2.0+ with Async support
- **消息队列**: Celery + Redis (异步任务)
- **认证**: JWT + OAuth2
- **文档**: OpenAPI/Swagger (FastAPI自动生成)

---

## 🏗️ 系统架构设计

### 微服务架构模式
```
服务拆分策略
├── 用户管理服务 (User Management Service)
├── 课程管理服务 (Course Management Service)
├── 作业管理服务 (Assignment Service)
├── AI反馈服务 (AI Feedback Service)
├── 文件管理服务 (File Management Service)
└── 通知服务 (Notification Service)
```

### API接口设计规范
```yaml
RESTful API设计原则:
  基础路径: /api/v1
  认证方式: Bearer Token (JWT)
  响应格式: JSON
  状态码标准: HTTP标准状态码
  
接口命名规范:
  - GET /api/v1/users - 获取用户列表
  - POST /api/v1/users - 创建用户  
  - GET /api/v1/users/{user_id} - 获取特定用户
  - PUT /api/v1/users/{user_id} - 更新用户
  - DELETE /api/v1/users/{user_id} - 删除用户
```

---

## 🗄️ 数据库设计

### 核心数据模型
```sql
-- 用户表
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    full_name VARCHAR(100),
    role VARCHAR(20) NOT NULL DEFAULT 'student', -- 'teacher', 'student', 'admin'
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 课程表
CREATE TABLE courses (
    id SERIAL PRIMARY KEY,
    course_code VARCHAR(20) UNIQUE NOT NULL,
    course_name VARCHAR(200) NOT NULL,
    description TEXT,
    language VARCHAR(20) NOT NULL, -- 'C', 'Python'
    difficulty_level VARCHAR(20) NOT NULL, -- 'beginner', 'intermediate', 'advanced'
    teacher_id INTEGER REFERENCES users(id),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 作业表
CREATE TABLE assignments (
    id SERIAL PRIMARY KEY,
    course_id INTEGER REFERENCES courses(id),
    title VARCHAR(200) NOT NULL,
    description TEXT,
    requirements TEXT,
    due_date TIMESTAMP,
    max_score INTEGER DEFAULT 100,
    assignment_type VARCHAR(50), -- 'basic_io', 'loops', 'functions', 'recursion'
    test_cases JSONB, -- 存储测试用例
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 学生作业提交表
CREATE TABLE submissions (
    id SERIAL PRIMARY KEY,
    assignment_id INTEGER REFERENCES assignments(id),
    student_id INTEGER REFERENCES users(id),
    code_content TEXT NOT NULL,
    file_name VARCHAR(255),
    programming_language VARCHAR(20),
    submission_status VARCHAR(20) DEFAULT 'submitted', -- 'draft', 'submitted', 'reviewed'
    submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(assignment_id, student_id) -- 每个作业每个学生只能有一个最新提交
);

-- AI反馈表
CREATE TABLE ai_feedbacks (
    id SERIAL PRIMARY KEY,
    submission_id INTEGER REFERENCES submissions(id),
    feedback_content JSONB NOT NULL, -- 存储结构化反馈
    feedback_type VARCHAR(50), -- 'assignment_review', 'debugging_help', 'personalized_learning'
    agents_used TEXT[], -- 参与的AI Agent列表
    processing_time_ms INTEGER, -- 处理时间（毫秒）
    quality_score DECIMAL(3,2), -- 质量评分 0.00-5.00
    accuracy_rate DECIMAL(5,2), -- 准确率百分比
    is_reviewed BOOLEAN DEFAULT FALSE, -- 教师是否已审核
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 学生学习档案表  
CREATE TABLE student_profiles (
    id SERIAL PRIMARY KEY,
    student_id INTEGER REFERENCES users(id),
    course_id INTEGER REFERENCES courses(id),
    learning_style VARCHAR(50), -- 'visual', 'auditory', 'kinesthetic'
    current_level VARCHAR(20), -- 'beginner', 'intermediate', 'advanced'
    strengths TEXT[], -- 学习强项
    weaknesses TEXT[], -- 薄弱环节
    learning_pace VARCHAR(20), -- 'slow', 'normal', 'fast'
    engagement_score DECIMAL(3,2), -- 参与度评分
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(student_id, course_id)
);

-- 系统日志表
CREATE TABLE system_logs (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    action VARCHAR(100) NOT NULL,
    resource_type VARCHAR(50),
    resource_id INTEGER,
    details JSONB,
    ip_address INET,
    user_agent TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 索引优化策略
```sql
-- 性能优化索引
CREATE INDEX idx_submissions_assignment_student ON submissions(assignment_id, student_id);
CREATE INDEX idx_ai_feedbacks_submission ON ai_feedbacks(submission_id);
CREATE INDEX idx_student_profiles_student_course ON student_profiles(student_id, course_id);
CREATE INDEX idx_system_logs_user_created ON system_logs(user_id, created_at);
CREATE INDEX idx_assignments_course_active ON assignments(course_id) WHERE is_active = TRUE;

-- 全文搜索索引
CREATE INDEX idx_assignments_description_gin ON assignments USING gin(to_tsvector('english', description));
CREATE INDEX idx_courses_name_gin ON courses USING gin(to_tsvector('english', course_name));
```

---

## 🚀 FastAPI应用架构

### 项目结构设计
```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py                  # FastAPI应用入口
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py           # 配置管理
│   │   ├── security.py         # 认证和安全
│   │   ├── database.py         # 数据库连接
│   │   └── dependencies.py     # 依赖注入
│   ├── api/
│   │   ├── __init__.py
│   │   ├── v1/
│   │   │   ├── __init__.py
│   │   │   ├── endpoints/
│   │   │   │   ├── users.py
│   │   │   │   ├── courses.py
│   │   │   │   ├── assignments.py
│   │   │   │   ├── submissions.py
│   │   │   │   ├── ai_feedback.py
│   │   │   │   └── analytics.py
│   │   │   └── api.py          # 路由汇总
│   ├── models/
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── course.py
│   │   ├── assignment.py
│   │   ├── submission.py
│   │   └── ai_feedback.py
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── user.py             # Pydantic模型
│   │   ├── course.py
│   │   ├── assignment.py
│   │   ├── submission.py
│   │   └── ai_feedback.py
│   ├── services/
│   │   ├── __init__.py
│   │   ├── user_service.py
│   │   ├── course_service.py
│   │   ├── assignment_service.py
│   │   ├── ai_integration_service.py
│   │   └── notification_service.py
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── validators.py
│   │   ├── helpers.py
│   │   └── exceptions.py
│   └── tests/
│       ├── __init__.py
│       ├── test_users.py
│       ├── test_courses.py
│       ├── test_assignments.py
│       └── test_ai_integration.py
├── migrations/
├── requirements.txt
├── docker-compose.yml
├── Dockerfile
└── README.md
```

### 核心配置管理
```python
# app/core/config.py
from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # 基础配置
    PROJECT_NAME: str = "AI Teaching Assistant API"
    VERSION: str = "1.0.0"
    DEBUG: bool = False
    
    # 数据库配置
    DATABASE_URL: str
    DATABASE_POOL_SIZE: int = 10
    DATABASE_MAX_OVERFLOW: int = 20
    
    # Redis配置
    REDIS_URL: str = "redis://localhost:6379"
    
    # 安全配置
    SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    ALGORITHM: str = "HS256"
    
    # AI服务配置
    AI_SERVICE_URL: str = "http://localhost:8001"
    AI_SERVICE_TIMEOUT: int = 30
    
    # 文件存储配置
    UPLOAD_DIRECTORY: str = "./uploads"
    MAX_UPLOAD_SIZE: int = 10 * 1024 * 1024  # 10MB
    
    # 日志配置
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "app.log"
    
    class Config:
        env_file = ".env"

settings = Settings()
```

### 数据库连接管理
```python
# app/core/database.py
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from .config import settings

# 异步数据库引擎
engine = create_async_engine(
    settings.DATABASE_URL,
    pool_size=settings.DATABASE_POOL_SIZE,
    max_overflow=settings.DATABASE_MAX_OVERFLOW,
    echo=settings.DEBUG
)

# 异步Session工厂
AsyncSessionLocal = sessionmaker(
    engine, 
    class_=AsyncSession, 
    expire_on_commit=False
)

# 基础模型类
Base = declarative_base()

# 数据库依赖注入
async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
```

### 认证和安全
```python
# app/core/security.py
from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from .config import settings

# 密码加密
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT Token配置
security = HTTPBearer()

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """验证密码"""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """生成密码哈希"""
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """创建访问令牌"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """获取当前用户"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(credentials.credentials, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    # 这里应该从数据库获取用户信息
    # user = await get_user_by_username(username)
    # if user is None:
    #     raise credentials_exception
    # return user
    return {"username": username}
```

---

## 🔌 AI集成服务设计

### AI服务集成层
```python
# app/services/ai_integration_service.py
import asyncio
import aiohttp
import json
from typing import Dict, Any, Optional
from datetime import datetime
from ..core.config import settings
from ..utils.exceptions import AIServiceException

class AIIntegrationService:
    """AI服务集成层"""
    
    def __init__(self):
        self.ai_service_url = settings.AI_SERVICE_URL
        self.timeout = settings.AI_SERVICE_TIMEOUT
        
    async def request_assignment_review(
        self, 
        code: str, 
        language: str, 
        assignment_type: str,
        course_level: str,
        student_profile: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """请求作业批改服务"""
        
        payload = {
            "workflow_type": "assignment_review",
            "data": {
                "code": code,
                "language": language,
                "assignment_type": assignment_type,
                "course_level": course_level,
                "student_profile": student_profile
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        
        return await self._make_ai_request("/api/v1/review-assignment", payload)
    
    async def request_debugging_help(
        self,
        code: str,
        error_message: str,
        language: str,
        student_level: str
    ) -> Dict[str, Any]:
        """请求调试辅导服务"""
        
        payload = {
            "workflow_type": "debugging_help",
            "data": {
                "code": code,
                "error_message": error_message,
                "language": language,
                "student_level": student_level
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        
        return await self._make_ai_request("/api/v1/debug-help", payload)
    
    async def request_personalized_learning(
        self,
        student_profile: Dict,
        learning_history: Dict,
        current_course: Dict
    ) -> Dict[str, Any]:
        """请求个性化学习建议"""
        
        payload = {
            "workflow_type": "personalized_learning",
            "data": {
                "student_profile": student_profile,
                "learning_history": learning_history,
                "current_course": current_course
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        
        return await self._make_ai_request("/api/v1/personalized-learning", payload)
    
    async def _make_ai_request(self, endpoint: str, payload: Dict) -> Dict[str, Any]:
        """发送AI服务请求"""
        url = f"{self.ai_service_url}{endpoint}"
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    url,
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=self.timeout)
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        return result
                    else:
                        error_detail = await response.text()
                        raise AIServiceException(
                            f"AI service error: {response.status} - {error_detail}"
                        )
        except asyncio.TimeoutError:
            raise AIServiceException("AI service timeout")
        except Exception as e:
            raise AIServiceException(f"AI service connection error: {str(e)}")
```

### 异步任务处理
```python
# app/services/task_service.py
from celery import Celery
from typing import Dict, Any
from .ai_integration_service import AIIntegrationService

# Celery配置
celery_app = Celery(
    "ai_teaching_tasks",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL
)

@celery_app.task(bind=True, max_retries=3)
async def process_assignment_async(self, submission_data: Dict[str, Any]):
    """异步处理作业批改任务"""
    try:
        ai_service = AIIntegrationService()
        result = await ai_service.request_assignment_review(
            code=submission_data["code"],
            language=submission_data["language"],
            assignment_type=submission_data["assignment_type"],
            course_level=submission_data["course_level"]
        )
        
        # 保存结果到数据库
        await save_ai_feedback(submission_data["submission_id"], result)
        
        # 发送通知给学生和教师
        await send_feedback_notification(submission_data["student_id"], result)
        
        return {"status": "success", "result": result}
        
    except Exception as exc:
        # 重试机制
        if self.request.retries < self.max_retries:
            # 指数退避重试
            countdown = 2 ** self.request.retries
            raise self.retry(countdown=countdown)
        else:
            # 记录失败日志
            await log_task_failure(submission_data, str(exc))
            return {"status": "failed", "error": str(exc)}
```

---

## 📊 缓存策略设计

### Redis缓存配置
```python
# app/core/redis.py
import redis.asyncio as redis
from typing import Optional, Any
import json
from .config import settings

class RedisCache:
    """Redis缓存管理"""
    
    def __init__(self):
        self.redis_client = redis.from_url(
            settings.REDIS_URL,
            encoding="utf-8",
            decode_responses=True
        )
    
    async def get(self, key: str) -> Optional[Any]:
        """获取缓存值"""
        try:
            value = await self.redis_client.get(key)
            if value:
                return json.loads(value)
            return None
        except Exception:
            return None
    
    async def set(
        self, 
        key: str, 
        value: Any, 
        expire_seconds: int = 3600
    ) -> bool:
        """设置缓存值"""
        try:
            serialized_value = json.dumps(value, default=str)
            await self.redis_client.setex(key, expire_seconds, serialized_value)
            return True
        except Exception:
            return False
    
    async def delete(self, key: str) -> bool:
        """删除缓存"""
        try:
            await self.redis_client.delete(key)
            return True
        except Exception:
            return False
    
    async def exists(self, key: str) -> bool:
        """检查键是否存在"""
        try:
            return await self.redis_client.exists(key) > 0
        except Exception:
            return False

# 全局缓存实例
cache = RedisCache()

# 缓存装饰器
def cache_result(expire_seconds: int = 3600):
    """缓存结果装饰器"""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            # 生成缓存键
            cache_key = f"{func.__name__}:{hash(str(args) + str(kwargs))}"
            
            # 尝试从缓存获取
            cached_result = await cache.get(cache_key)
            if cached_result is not None:
                return cached_result
            
            # 执行函数并缓存结果
            result = await func(*args, **kwargs)
            await cache.set(cache_key, result, expire_seconds)
            return result
        return wrapper
    return decorator
```

### 缓存策略应用
```python
# 缓存用户信息
@cache_result(expire_seconds=1800)  # 30分钟
async def get_user_profile(user_id: int):
    """获取用户档案（带缓存）"""
    pass

# 缓存课程信息
@cache_result(expire_seconds=3600)  # 1小时
async def get_course_details(course_id: int):
    """获取课程详情（带缓存）"""
    pass

# 缓存AI分析结果
@cache_result(expire_seconds=7200)  # 2小时
async def get_similar_code_analysis(code_hash: str):
    """获取相似代码分析结果（带缓存）"""
    pass
```

---

## 🔧 API端点实现

### 用户管理API
```python
# app/api/v1/endpoints/users.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from ...core.database import get_db
from ...core.security import get_current_user, get_password_hash
from ...schemas.user import UserCreate, UserResponse, UserUpdate
from ...services.user_service import UserService

router = APIRouter()

@router.post("/", response_model=UserResponse)
async def create_user(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db)
):
    """创建新用户"""
    user_service = UserService(db)
    
    # 检查用户名和邮箱是否已存在
    if await user_service.get_by_username(user_data.username):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )
    
    if await user_service.get_by_email(user_data.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # 创建用户
    hashed_password = get_password_hash(user_data.password)
    user_data.password = hashed_password
    
    user = await user_service.create(user_data)
    return user

@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """获取当前用户信息"""
    user_service = UserService(db)
    user = await user_service.get_by_username(current_user["username"])
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return user

@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """获取指定用户信息"""
    user_service = UserService(db)
    user = await user_service.get_by_id(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return user
```

### 作业提交和AI反馈API
```python
# app/api/v1/endpoints/submissions.py
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
import asyncio

from ...core.database import get_db
from ...core.security import get_current_user
from ...schemas.submission import SubmissionCreate, SubmissionResponse
from ...services.submission_service import SubmissionService
from ...services.ai_integration_service import AIIntegrationService
from ...services.task_service import process_assignment_async

router = APIRouter()

@router.post("/", response_model=SubmissionResponse)
async def submit_assignment(
    assignment_id: int,
    code_content: str,
    programming_language: str,
    file: UploadFile = File(None),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """提交作业代码"""
    submission_service = SubmissionService(db)
    
    # 创建提交记录
    submission_data = SubmissionCreate(
        assignment_id=assignment_id,
        student_id=current_user["user_id"],
        code_content=code_content,
        programming_language=programming_language,
        file_name=file.filename if file else None
    )
    
    submission = await submission_service.create(submission_data)
    
    # 异步启动AI分析任务
    task_data = {
        "submission_id": submission.id,
        "code": code_content,
        "language": programming_language,
        "assignment_type": submission.assignment.assignment_type,
        "course_level": submission.assignment.course.difficulty_level,
        "student_id": current_user["user_id"]
    }
    
    # 启动异步任务
    process_assignment_async.delay(task_data)
    
    return submission

@router.get("/{submission_id}/feedback")
async def get_submission_feedback(
    submission_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """获取提交的AI反馈"""
    submission_service = SubmissionService(db)
    feedback = await submission_service.get_feedback(submission_id)
    
    if not feedback:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Feedback not found or still processing"
        )
    
    return feedback

@router.post("/{submission_id}/request-help")
async def request_debugging_help(
    submission_id: int,
    error_message: str,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """请求调试帮助"""
    submission_service = SubmissionService(db)
    ai_service = AIIntegrationService()
    
    submission = await submission_service.get_by_id(submission_id)
    if not submission:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Submission not found"
        )
    
    # 请求AI调试帮助
    help_result = await ai_service.request_debugging_help(
        code=submission.code_content,
        error_message=error_message,
        language=submission.programming_language,
        student_level=current_user.get("level", "beginner")
    )
    
    # 保存调试帮助结果
    await submission_service.save_debugging_help(submission_id, help_result)
    
    return help_result
```

---

## 🧪 测试策略

### 单元测试
```python
# app/tests/test_ai_integration.py
import pytest
from unittest.mock import Mock, patch
from app.services.ai_integration_service import AIIntegrationService
from app.utils.exceptions import AIServiceException

class TestAIIntegrationService:
    
    @pytest.fixture
    def ai_service(self):
        return AIIntegrationService()
    
    @pytest.mark.asyncio
    async def test_request_assignment_review_success(self, ai_service):
        """测试作业批改请求成功场景"""
        # Mock AI服务响应
        mock_response = {
            "feedback": {
                "overall_assessment": "Good work!",
                "code_quality": 4.2,
                "suggestions": ["Add more comments"]
            },
            "processing_time": 2.5,
            "quality_score": 4.0
        }
        
        with patch('aiohttp.ClientSession.post') as mock_post:
            mock_post.return_value.__aenter__.return_value.status = 200
            mock_post.return_value.__aenter__.return_value.json.return_value = mock_response
            
            result = await ai_service.request_assignment_review(
                code="print('Hello World')",
                language="Python",
                assignment_type="basic_io",
                course_level="beginner"
            )
            
            assert result == mock_response
            assert result["feedback"]["code_quality"] == 4.2
    
    @pytest.mark.asyncio
    async def test_request_assignment_review_timeout(self, ai_service):
        """测试AI服务超时场景"""
        with patch('aiohttp.ClientSession.post') as mock_post:
            mock_post.side_effect = asyncio.TimeoutError()
            
            with pytest.raises(AIServiceException, match="AI service timeout"):
                await ai_service.request_assignment_review(
                    code="print('Hello World')",
                    language="Python", 
                    assignment_type="basic_io",
                    course_level="beginner"
                )
```

### 集成测试
```python
# app/tests/test_endpoints_integration.py
import pytest
from httpx import AsyncClient
from app.main import app

class TestSubmissionEndpoints:
    
    @pytest.mark.asyncio
    async def test_submit_assignment_integration(self):
        """测试作业提交端到端流程"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            # 1. 用户登录
            login_response = await client.post("/api/v1/auth/login", json={
                "username": "test_student",
                "password": "test_password"
            })
            assert login_response.status_code == 200
            token = login_response.json()["access_token"]
            
            # 2. 提交作业
            submission_response = await client.post(
                "/api/v1/submissions/",
                json={
                    "assignment_id": 1,
                    "code_content": "print('Hello World')",
                    "programming_language": "Python"
                },
                headers={"Authorization": f"Bearer {token}"}
            )
            assert submission_response.status_code == 200
            submission_id = submission_response.json()["id"]
            
            # 3. 等待AI处理完成（在实际测试中可能需要mock）
            import asyncio
            await asyncio.sleep(5)
            
            # 4. 获取反馈
            feedback_response = await client.get(
                f"/api/v1/submissions/{submission_id}/feedback",
                headers={"Authorization": f"Bearer {token}"}
            )
            assert feedback_response.status_code == 200
            feedback = feedback_response.json()
            assert "feedback_content" in feedback
```

---

## 📈 性能优化策略

### 数据库优化
```python
# 连接池优化
DATABASE_CONFIG = {
    "pool_size": 20,          # 连接池大小
    "max_overflow": 30,       # 最大溢出连接
    "pool_timeout": 30,       # 获取连接超时
    "pool_recycle": 3600,     # 连接回收时间
    "pool_pre_ping": True     # 连接预检查
}

# 查询优化
async def get_user_submissions_optimized(user_id: int, limit: int = 10):
    """优化的用户提交查询"""
    query = select(Submission).where(
        Submission.student_id == user_id
    ).options(
        selectinload(Submission.assignment),  # 预加载关联数据
        selectinload(Submission.ai_feedback)
    ).order_by(
        Submission.submitted_at.desc()
    ).limit(limit)
    
    result = await session.execute(query)
    return result.scalars().all()
```

### 缓存策略优化
```python
# 多层缓存策略
class MultiLevelCache:
    def __init__(self):
        self.memory_cache = {}  # 内存缓存
        self.redis_cache = RedisCache()  # Redis缓存
    
    async def get(self, key: str):
        # L1: 检查内存缓存
        if key in self.memory_cache:
            return self.memory_cache[key]
        
        # L2: 检查Redis缓存
        value = await self.redis_cache.get(key)
        if value:
            # 回写到内存缓存
            self.memory_cache[key] = value
            return value
        
        return None
    
    async def set(self, key: str, value: Any, memory_expire: int = 300, redis_expire: int = 3600):
        # 同时写入两级缓存
        self.memory_cache[key] = value
        await self.redis_cache.set(key, value, redis_expire)
        
        # 内存缓存过期处理
        asyncio.create_task(self._expire_memory_cache(key, memory_expire))
```

### 异步处理优化
```python
# 批量处理优化
async def process_batch_submissions(submission_ids: List[int]):
    """批量处理提交任务"""
    semaphore = asyncio.Semaphore(5)  # 限制并发数
    
    async def process_single(submission_id: int):
        async with semaphore:
            return await process_submission(submission_id)
    
    tasks = [process_single(sid) for sid in submission_ids]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    return results
```

---

## 🚀 部署配置

### Docker配置
```dockerfile
# Dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Docker Compose
```yaml
# docker-compose.yml
version: '3.8'

services:
  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql+asyncpg://user:password@db:5432/ai_teaching
      - REDIS_URL=redis://redis:6379
    depends_on:
      - db
      - redis
    volumes:
      - ./uploads:/app/uploads

  db:
    image: postgres:15
    environment:
      - POSTGRES_DB=ai_teaching
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=password
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  redis:
    image: redis:7
    ports:
      - "6379:6379"

  celery:
    build: .
    command: celery -A app.services.task_service worker --loglevel=info
    environment:
      - DATABASE_URL=postgresql+asyncpg://user:password@db:5432/ai_teaching
      - REDIS_URL=redis://redis:6379
    depends_on:
      - db
      - redis

volumes:
  postgres_data:
```

---

## 📊 监控和日志

### 日志配置
```python
# app/core/logging.py
import logging
import sys
from pathlib import Path

def setup_logging():
    """配置应用日志"""
    
    # 创建日志目录
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    # 配置格式
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # 文件处理器
    file_handler = logging.FileHandler(log_dir / "app.log")
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.INFO)
    
    # 控制台处理器
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    console_handler.setLevel(logging.INFO)
    
    # 根日志配置
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)
    
    return root_logger
```

### 性能监控
```python
# app/core/monitoring.py
import time
from functools import wraps
from prometheus_client import Counter, Histogram, generate_latest

# 监控指标
REQUEST_COUNT = Counter('http_requests_total', 'Total HTTP requests', ['method', 'endpoint'])
REQUEST_DURATION = Histogram('http_request_duration_seconds', 'HTTP request duration')

def monitor_performance(func):
    """性能监控装饰器"""
    @wraps(func)
    async def wrapper(*args, **kwargs):
        start_time = time.time()
        try:
            result = await func(*args, **kwargs)
            REQUEST_COUNT.labels(method='POST', endpoint=func.__name__).inc()
            return result
        finally:
            REQUEST_DURATION.observe(time.time() - start_time)
    return wrapper
```

---

## 🎯 交付标准

### 必须交付 (Must Have)
- ✅ 完整的FastAPI应用架构
- ✅ 数据库模型和迁移脚本
- ✅ 核心API端点实现
- ✅ AI服务集成接口
- ✅ 认证和安全机制
- ✅ 基础测试覆盖

### 期望交付 (Should Have)
- ✅ Redis缓存集成
- ✅ 异步任务处理
- ✅ 完整的错误处理
- ✅ API文档和测试
- ✅ Docker部署配置

### 可选交付 (Nice to Have)
- ✅ 性能监控和日志
- ✅ 数据库连接池优化
- ✅ 批量处理优化
- ✅ 多环境配置支持

**作为Backend Architect Developer，请基于这份详细指南，构建高性能、可扩展的后端服务架构。确保系统能够稳定支撑AI教学助手的核心业务功能。**