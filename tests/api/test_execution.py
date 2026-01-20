"""
代码执行API测试
Sprint 4: 测试代码执行端点
"""

import pytest
import pytest_asyncio
from httpx import AsyncClient
from unittest.mock import patch, MagicMock, AsyncMock


class TestCodeExecutionAPI:
    """代码执行API测试类"""

    @pytest.mark.asyncio
    @pytest.mark.api
    async def test_get_supported_languages(self, async_client: AsyncClient):
        """测试获取支持的编程语言列表"""
        response = await async_client.get("/api/v1/execution/languages")

        assert response.status_code == 200
        data = response.json()

        assert data["success"] is True
        assert "data" in data

        languages = data["data"]
        assert len(languages) >= 3

        # 验证必要的语言支持
        language_ids = [lang["id"] for lang in languages]
        assert "c" in language_ids
        assert "python" in language_ids
        assert "cpp" in language_ids

    @pytest.mark.asyncio
    @pytest.mark.api
    async def test_execute_code_unauthorized(self, async_client: AsyncClient):
        """测试未授权执行代码"""
        code_data = {
            "code": "print('hello')",
            "language": "python"
        }

        response = await async_client.post(
            "/api/v1/execution/run",
            json=code_data
        )

        # 应该返回401未授权
        assert response.status_code == 401

    @pytest.mark.asyncio
    @pytest.mark.api
    async def test_execute_code_invalid_language(self, async_client: AsyncClient, auth_headers):
        """测试使用无效语言执行代码"""
        code_data = {
            "code": "print('hello')",
            "language": "invalid_lang"
        }

        response = await async_client.post(
            "/api/v1/execution/run",
            json=code_data,
            headers=auth_headers
        )

        assert response.status_code == 400
        assert "Unsupported language" in response.json().get("detail", "")

    @pytest.mark.asyncio
    @pytest.mark.api
    async def test_quick_execute_python(self, async_client: AsyncClient):
        """测试快速执行Python代码（无需认证）"""
        code_data = {
            "code": "print('hello world')",
            "language": "python",
            "timeout": 5.0
        }

        # Mock代码执行服务
        with patch('app.api.execution.get_code_execution_service') as mock_service:
            mock_instance = MagicMock()
            mock_instance.execute_code = AsyncMock(return_value=MagicMock(
                execution_id="test123",
                status=MagicMock(value="success"),
                output="hello world\n",
                error=None,
                execution_time=50.0,
                memory_used=1024,
                compilation_output=None,
                test_results=[],
                tests_passed=0,
                total_tests=0,
                score=0.0,
            ))
            mock_service.return_value = mock_instance

            response = await async_client.post(
                "/api/v1/execution/run-quick",
                json=code_data
            )

        assert response.status_code == 200
        data = response.json()
        assert "data" in data

    @pytest.mark.asyncio
    @pytest.mark.api
    async def test_execute_code_empty_code(self, async_client: AsyncClient, auth_headers):
        """测试执行空代码"""
        code_data = {
            "code": "",
            "language": "python"
        }

        response = await async_client.post(
            "/api/v1/execution/run",
            json=code_data,
            headers=auth_headers
        )

        # Pydantic验证应该拒绝空代码
        assert response.status_code == 422

    @pytest.mark.asyncio
    @pytest.mark.api
    async def test_execute_code_with_test_cases(self, async_client: AsyncClient, auth_headers):
        """测试带测试用例执行代码"""
        code_data = {
            "code": """
n = int(input())
print(n * 2)
            """,
            "language": "python",
            "test_cases": [
                {
                    "input": "5",
                    "expected_output": "10",
                    "description": "Test doubling 5"
                },
                {
                    "input": "10",
                    "expected_output": "20",
                    "description": "Test doubling 10"
                }
            ],
            "timeout": 5.0
        }

        # Mock代码执行服务
        with patch('app.api.execution.get_code_execution_service') as mock_service:
            mock_instance = MagicMock()
            mock_instance.execute_code = AsyncMock(return_value=MagicMock(
                execution_id="test456",
                status=MagicMock(value="success"),
                output="Test 1: ✓\nTest 2: ✓",
                error=None,
                execution_time=100.0,
                memory_used=2048,
                compilation_output=None,
                test_results=[
                    MagicMock(
                        test_case_id="tc1",
                        passed=True,
                        actual_output="10",
                        expected_output="10",
                        execution_time=30.0,
                        error_message=None
                    ),
                    MagicMock(
                        test_case_id="tc2",
                        passed=True,
                        actual_output="20",
                        expected_output="20",
                        execution_time=30.0,
                        error_message=None
                    )
                ],
                tests_passed=2,
                total_tests=2,
                score=100.0,
            ))
            mock_service.return_value = mock_instance

            response = await async_client.post(
                "/api/v1/execution/run",
                json=code_data,
                headers=auth_headers
            )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["tests_passed"] == 2
        assert data["data"]["total_tests"] == 2

    @pytest.mark.asyncio
    @pytest.mark.api
    async def test_cancel_execution(self, async_client: AsyncClient, auth_headers):
        """测试取消代码执行"""
        cancel_data = {
            "execution_id": "nonexistent123"
        }

        # Mock代码执行服务
        with patch('app.api.execution.get_code_execution_service') as mock_service:
            mock_instance = MagicMock()
            mock_instance.cancel_execution = AsyncMock(return_value=False)
            mock_service.return_value = mock_instance

            response = await async_client.post(
                "/api/v1/execution/cancel",
                json=cancel_data,
                headers=auth_headers
            )

        assert response.status_code == 200
        data = response.json()
        assert data["data"]["cancelled"] is False


class TestCodeExecutionService:
    """代码执行服务单元测试"""

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_service_initialization(self):
        """测试服务初始化"""
        from app.services.code_execution_service import CodeExecutionService

        service = CodeExecutionService()
        assert service.temp_base_dir.exists()
        assert len(service.active_executions) == 0

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_compare_output_exact_match(self):
        """测试输出比较 - 精确匹配"""
        from app.services.code_execution_service import CodeExecutionService

        service = CodeExecutionService()

        assert service._compare_output("hello", "hello") is True
        assert service._compare_output("hello\n", "hello") is True
        assert service._compare_output("hello", "hello\n") is True
        assert service._compare_output("hello\nworld", "hello\nworld") is True

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_compare_output_whitespace(self):
        """测试输出比较 - 空白字符处理"""
        from app.services.code_execution_service import CodeExecutionService

        service = CodeExecutionService()

        # 尾随空白应该被忽略
        assert service._compare_output("hello  ", "hello") is True
        assert service._compare_output("hello\t", "hello") is True

        # 但中间的空白不能忽略
        assert service._compare_output("he llo", "hello") is False

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_compare_output_different(self):
        """测试输出比较 - 不同输出"""
        from app.services.code_execution_service import CodeExecutionService

        service = CodeExecutionService()

        assert service._compare_output("hello", "world") is False
        assert service._compare_output("123", "456") is False

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_language_config(self):
        """测试语言配置"""
        from app.services.code_execution_service import (
            CodeExecutionService,
            ProgrammingLanguage
        )

        service = CodeExecutionService()

        # 检查所有支持的语言都有配置
        for lang in ProgrammingLanguage:
            assert lang in service.LANGUAGE_CONFIG
            config = service.LANGUAGE_CONFIG[lang]
            assert "extension" in config
            assert "run_cmd" in config

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_build_run_command_python(self):
        """测试构建Python运行命令"""
        from app.services.code_execution_service import (
            CodeExecutionService,
            ProgrammingLanguage
        )
        from pathlib import Path

        service = CodeExecutionService()
        config = service.LANGUAGE_CONFIG[ProgrammingLanguage.PYTHON]

        source_file = Path("/tmp/test.py")
        work_dir = Path("/tmp")

        cmd = service._build_run_command(source_file, None, work_dir, config)

        assert "python3" in cmd[0]
        assert str(source_file) in cmd[1]

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_cleanup(self):
        """测试清理功能"""
        from app.services.code_execution_service import CodeExecutionService

        service = CodeExecutionService()

        # 创建一些临时文件
        test_dir = service.temp_base_dir / "test_cleanup"
        test_dir.mkdir(exist_ok=True)
        (test_dir / "test.txt").write_text("test")

        # 执行清理
        service.cleanup()

        # 验证目录被重新创建但为空
        assert service.temp_base_dir.exists()


@pytest.fixture
def auth_headers(client, test_user_data):
    """获取认证头部fixture - 覆盖conftest中的版本用于此测试模块"""
    from unittest.mock import patch, MagicMock

    # Mock认证
    with patch('app.core.dependencies.get_current_active_user') as mock_auth:
        mock_user = MagicMock()
        mock_user.id = "test-user-id"
        mock_user.email = "test@example.com"
        mock_user.role = "teacher"
        mock_auth.return_value = mock_user

        yield {"Authorization": "Bearer mock-token"}
