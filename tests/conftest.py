"""
pytest配置文件 - 提供测试fixtures和配置
"""

import asyncio
import os
import pytest
import pytest_asyncio
from typing import Generator, AsyncGenerator
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from fastapi.testclient import TestClient

# 设置测试环境变量
os.environ["TESTING"] = "true"
os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///./test.db"
os.environ["SECRET_KEY"] = "test-secret-key-for-testing-only"
os.environ["OPENAI_API_KEY"] = "test-key"

# 导入应用
from app.main import app
from app.database.session import get_db, Base
from app.core.config import settings


@pytest.fixture(scope="session")
def event_loop():
    """创建事件循环用于整个测试会话"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="session")
async def test_engine():
    """创建测试数据库引擎"""
    engine = create_async_engine(
        "sqlite+aiosqlite:///./test.db",
        echo=True,
        future=True
    )
    
    # 创建所有表
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    yield engine
    
    # 清理
    await engine.dispose()
    if os.path.exists("test.db"):
        os.remove("test.db")


@pytest_asyncio.fixture
async def test_db(test_engine):
    """创建测试数据库会话"""
    async_session = async_sessionmaker(test_engine, expire_on_commit=False)
    
    async with async_session() as session:
        yield session
        await session.rollback()


@pytest.fixture
def client(test_db):
    """创建测试客户端"""
    def override_get_db():
        yield test_db
    
    app.dependency_overrides[get_db] = override_get_db
    
    with TestClient(app) as test_client:
        yield test_client
    
    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def async_client(test_db):
    """创建异步测试客户端"""
    def override_get_db():
        yield test_db
    
    app.dependency_overrides[get_db] = override_get_db
    
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://testserver"
    ) as async_test_client:
        yield async_test_client
    
    app.dependency_overrides.clear()


@pytest.fixture
def test_user_data():
    """测试用户数据"""
    return {
        "email": "test@university.edu",
        "password": "securepassword123",
        "full_name": "Test Professor",
        "role": "teacher",
        "university": "Test University",
        "department": "Computer Science"
    }


@pytest.fixture
def test_student_data():
    """测试学生数据"""
    return {
        "email": "student@university.edu", 
        "password": "studentpass123",
        "full_name": "Test Student",
        "role": "student",
        "university": "Test University",
        "department": "Computer Science",
        "student_id": "CS2024001"
    }


@pytest.fixture
def sample_code_submission():
    """示例代码提交"""
    return {
        "code": '''
#include <stdio.h>
int main() {
    int n = 5;
    for(int i = 0; i < n; i++) {
        printf("Hello World\\n");
    }
    return 0;
}
        ''',
        "language": "c",
        "assignment_id": "basic-loops",
        "student_id": "CS2024001"
    }


@pytest.fixture
def mock_ai_response():
    """模拟AI响应数据"""
    return {
        "analysis": {
            "syntax_errors": [],
            "logic_issues": [],
            "style_suggestions": [
                "Consider adding comments to explain the loop logic"
            ],
            "complexity_score": 2,
            "correctness_score": 95
        },
        "feedback": {
            "overall_assessment": "Good basic implementation",
            "strengths": ["Correct syntax", "Proper loop structure"],
            "improvements": ["Add comments for clarity"],
            "next_steps": ["Try implementing nested loops"],
            "difficulty_level": "beginner"
        },
        "pedagogical_advice": {
            "teaching_strategy": "positive_reinforcement",
            "focus_areas": ["code_documentation"],
            "estimated_mastery": 0.8
        }
    }


@pytest.fixture
def auth_headers(client, test_user_data):
    """获取认证头部"""
    # 首先注册用户
    response = client.post("/api/v1/auth/register", json=test_user_data)
    assert response.status_code in [200, 201]
    
    # 然后登录获取token
    login_data = {
        "email": test_user_data["email"],
        "password": test_user_data["password"]
    }
    response = client.post("/api/v1/auth/login", json=login_data)
    assert response.status_code == 200
    
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture(autouse=True)
def clean_db(test_db):
    """每个测试后清理数据库"""
    yield
    # 清理逻辑将在test_db fixture的rollback中处理


# 测试标记
pytest_plugins = []

def pytest_configure(config):
    """配置pytest标记"""
    config.addinivalue_line("markers", "unit: 单元测试")
    config.addinivalue_line("markers", "integration: 集成测试")
    config.addinivalue_line("markers", "api: API测试")
    config.addinivalue_line("markers", "ai: AI功能测试")
    config.addinivalue_line("markers", "slow: 慢速测试")
    config.addinivalue_line("markers", "auth: 认证相关测试")
    config.addinivalue_line("markers", "database: 数据库相关测试")


# 测试数据工厂
class TestDataFactory:
    """测试数据工厂类"""
    
    @staticmethod
    def create_user(role="teacher", **kwargs):
        """创建用户数据"""
        base_data = {
            "email": f"test_{role}@university.edu",
            "password": "testpassword123",
            "full_name": f"Test {role.title()}",
            "role": role,
            "university": "Test University",
            "department": "Computer Science"
        }
        base_data.update(kwargs)
        return base_data
    
    @staticmethod
    def create_assignment(**kwargs):
        """创建作业数据"""
        base_data = {
            "title": "Basic C Programming",
            "description": "Write a simple C program",
            "language": "c",
            "difficulty": "beginner",
            "due_date": "2024-12-31T23:59:59",
            "max_attempts": 3
        }
        base_data.update(kwargs)
        return base_data
    
    @staticmethod
    def create_submission(**kwargs):
        """创建提交数据"""
        base_data = {
            "code": "#include <stdio.h>\nint main(){return 0;}",
            "language": "c",
            "assignment_id": "test-assignment"
        }
        base_data.update(kwargs)
        return base_data


@pytest.fixture
def test_factory():
    """测试数据工厂fixture"""
    return TestDataFactory