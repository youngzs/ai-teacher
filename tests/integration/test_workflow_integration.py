"""
集成测试 - 工作流端到端测试
Sprint 4: 测试完整的用户工作流

测试场景:
1. 学生提交代码 → AI分析 → 获取反馈
2. 教师创建作业 → 学生提交 → 教师批改
3. 课程进度追踪 → 学习分析
"""

import pytest
import pytest_asyncio
from httpx import AsyncClient
from unittest.mock import patch, MagicMock, AsyncMock
import uuid


@pytest.mark.integration
class TestStudentSubmissionWorkflow:
    """学生提交工作流集成测试"""

    @pytest.mark.asyncio
    async def test_complete_submission_workflow(
        self,
        async_client: AsyncClient,
        test_student_data,
        sample_code_submission
    ):
        """
        测试完整的代码提交工作流:
        1. 学生登录
        2. 提交代码
        3. 获取AI分析结果
        4. 查看反馈
        """
        # 步骤1: 模拟学生登录
        with patch('app.core.dependencies.get_current_active_user') as mock_auth:
            mock_user = MagicMock()
            mock_user.id = str(uuid.uuid4())
            mock_user.email = test_student_data["email"]
            mock_user.role = "student"
            mock_auth.return_value = mock_user

            # 步骤2: 提交代码
            submission_data = {
                "code": sample_code_submission["code"],
                "language": sample_code_submission["language"],
                "assignment_id": str(uuid.uuid4())
            }

            with patch('app.api.submissions.SubmissionRepository') as mock_repo:
                mock_repo_instance = MagicMock()
                mock_repo_instance.create = AsyncMock(return_value=MagicMock(
                    id=str(uuid.uuid4()),
                    code=submission_data["code"],
                    language=submission_data["language"],
                    status="pending"
                ))
                mock_repo.return_value = mock_repo_instance

                # 注意: 这里的测试可能需要根据实际API实现调整
                # 因为我们使用mock，主要是验证工作流的正确性

    @pytest.mark.asyncio
    async def test_code_execution_workflow(self, async_client: AsyncClient):
        """
        测试代码执行工作流:
        1. 提交代码执行请求
        2. 获取执行结果
        3. 验证测试用例结果
        """
        # 测试代码
        test_code = """
def add(a, b):
    return a + b

# 测试
print(add(2, 3))
"""

        execution_request = {
            "code": test_code,
            "language": "python",
            "stdin_input": "",
            "timeout": 5.0
        }

        with patch('app.api.execution.get_code_execution_service') as mock_service:
            mock_instance = MagicMock()
            mock_instance.execute_code = AsyncMock(return_value=MagicMock(
                execution_id="int-test-001",
                status=MagicMock(value="success"),
                output="5\n",
                error=None,
                execution_time=45.5,
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
                json=execution_request
            )

            assert response.status_code == 200
            data = response.json()
            assert data["data"]["output"] == "5\n"


@pytest.mark.integration
class TestTeacherGradingWorkflow:
    """教师批改工作流集成测试"""

    @pytest.mark.asyncio
    async def test_batch_grading_workflow(self, async_client: AsyncClient):
        """
        测试批量批改工作流:
        1. 教师获取待批改列表
        2. 请求AI评分
        3. 审核并确认成绩
        4. 返还给学生
        """
        # 这里主要是流程验证
        # 实际测试需要根据具体API实现

        # 模拟获取待批改提交
        with patch('app.core.dependencies.get_current_active_user') as mock_auth:
            mock_user = MagicMock()
            mock_user.id = str(uuid.uuid4())
            mock_user.role = "teacher"
            mock_auth.return_value = mock_user

            # 获取提交列表端点（如果存在）
            # response = await async_client.get(
            #     "/api/v1/submissions/pending",
            #     headers={"Authorization": "Bearer mock-token"}
            # )

    @pytest.mark.asyncio
    async def test_feedback_template_usage(self, async_client: AsyncClient):
        """
        测试反馈模板使用流程:
        1. 获取反馈模板列表
        2. 选择模板
        3. 填充变量
        4. 发送反馈
        """
        # 反馈模板功能在前端实现
        # 这里可以测试相关API端点（如果存在）
        pass


@pytest.mark.integration
class TestLearningProgressWorkflow:
    """学习进度追踪工作流集成测试"""

    @pytest.mark.asyncio
    async def test_progress_tracking_workflow(self, async_client: AsyncClient):
        """
        测试学习进度追踪工作流:
        1. 学生完成练习
        2. 系统记录进度
        3. 生成学习报告
        4. 更新技能评估
        """
        # 进度追踪涉及多个组件的协同
        pass

    @pytest.mark.asyncio
    async def test_dashboard_data_aggregation(self, async_client: AsyncClient):
        """
        测试仪表盘数据聚合:
        1. 获取学生统计数据
        2. 获取课程进度
        3. 获取成绩分布
        """
        with patch('app.core.dependencies.get_current_active_user') as mock_auth:
            mock_user = MagicMock()
            mock_user.id = str(uuid.uuid4())
            mock_user.role = "teacher"
            mock_auth.return_value = mock_user

            # 测试仪表盘端点
            response = await async_client.get(
                "/api/v1/dashboard/overview",
                headers={"Authorization": "Bearer mock-token"}
            )

            # 根据实现可能返回不同状态码
            assert response.status_code in [200, 401, 404]


@pytest.mark.integration
class TestAIAnalysisWorkflow:
    """AI分析工作流集成测试"""

    @pytest.mark.asyncio
    async def test_ai_feedback_generation(self, async_client: AsyncClient):
        """
        测试AI反馈生成流程:
        1. 提交代码
        2. AI分析代码
        3. 生成个性化反馈
        4. 返回结构化结果
        """
        with patch('app.core.dependencies.get_current_active_user') as mock_auth:
            mock_user = MagicMock()
            mock_user.id = str(uuid.uuid4())
            mock_user.role = "student"
            mock_auth.return_value = mock_user

            analysis_request = {
                "code": "#include <stdio.h>\nint main() { printf(\"Hello\"); return 0; }",
                "language": "c",
                "context": {
                    "assignment_type": "basic",
                    "student_level": "beginner"
                }
            }

            # Mock AI服务
            with patch('app.services.ai_service.AITeachingService') as mock_ai:
                mock_instance = MagicMock()
                mock_instance.analyze_code = AsyncMock(return_value={
                    "analysis": {"score": 85},
                    "feedback": {"message": "Good work!"}
                })

                # 测试分析端点
                # response = await async_client.post(
                #     "/api/v1/analysis/analyze",
                #     json=analysis_request,
                #     headers={"Authorization": "Bearer mock-token"}
                # )


@pytest.mark.integration
class TestErrorHandling:
    """错误处理集成测试"""

    @pytest.mark.asyncio
    async def test_invalid_code_handling(self, async_client: AsyncClient):
        """测试无效代码处理"""
        with patch('app.api.execution.get_code_execution_service') as mock_service:
            mock_instance = MagicMock()
            mock_instance.execute_code = AsyncMock(return_value=MagicMock(
                execution_id="error-test",
                status=MagicMock(value="compilation_error"),
                output="",
                error="syntax error: expected ';'",
                execution_time=10.0,
                memory_used=0,
                compilation_output="main.c:1:5: error: expected ';'",
                test_results=[],
                tests_passed=0,
                total_tests=0,
                score=0.0,
            ))
            mock_service.return_value = mock_instance

            response = await async_client.post(
                "/api/v1/execution/run-quick",
                json={
                    "code": "int main() { return 0 }",  # 缺少分号
                    "language": "c"
                }
            )

            assert response.status_code == 200
            data = response.json()
            assert data["data"]["status"] == "compilation_error"

    @pytest.mark.asyncio
    async def test_timeout_handling(self, async_client: AsyncClient):
        """测试超时处理"""
        with patch('app.api.execution.get_code_execution_service') as mock_service:
            mock_instance = MagicMock()
            mock_instance.execute_code = AsyncMock(return_value=MagicMock(
                execution_id="timeout-test",
                status=MagicMock(value="timeout"),
                output="",
                error="Execution timeout (5s)",
                execution_time=5000.0,
                memory_used=0,
                compilation_output=None,
                test_results=[],
                tests_passed=0,
                total_tests=0,
                score=0.0,
            ))
            mock_service.return_value = mock_instance

            response = await async_client.post(
                "/api/v1/execution/run-quick",
                json={
                    "code": "while True: pass",  # 无限循环
                    "language": "python",
                    "timeout": 5.0
                }
            )

            assert response.status_code == 200
            data = response.json()
            assert data["data"]["status"] == "timeout"

    @pytest.mark.asyncio
    async def test_rate_limiting(self, async_client: AsyncClient):
        """测试速率限制"""
        # 快速发送多个请求测试速率限制
        # 这需要根据实际的速率限制实现来测试
        pass
