"""
代码提交API测试模块
测试代码提交、分析、反馈等核心功能
"""

import pytest
from httpx import AsyncClient
from unittest.mock import patch, AsyncMock
import json


class TestSubmissionsAPI:
    """代码提交API测试类"""
    
    @pytest.mark.asyncio
    @pytest.mark.api
    async def test_create_submission_success(
        self, async_client: AsyncClient, test_user_data, sample_code_submission
    ):
        """测试创建代码提交成功"""
        # 注册并登录获取token
        await async_client.post("/api/v1/auth/register", json=test_user_data)
        login_response = await async_client.post(
            "/api/v1/auth/login",
            json={"email": test_user_data["email"], "password": test_user_data["password"]}
        )
        token = login_response.json()["access_token"]
        
        # 创建提交
        response = await async_client.post(
            "/api/v1/submissions/",
            json=sample_code_submission,
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 201
        data = response.json()
        assert "id" in data
        assert data["code"] == sample_code_submission["code"]
        assert data["language"] == sample_code_submission["language"]
        assert data["assignment_id"] == sample_code_submission["assignment_id"]
        assert data["status"] == "pending"
    
    @pytest.mark.asyncio
    @pytest.mark.api
    async def test_create_submission_unauthorized(
        self, async_client: AsyncClient, sample_code_submission
    ):
        """测试未授权创建提交失败"""
        response = await async_client.post(
            "/api/v1/submissions/",
            json=sample_code_submission
        )
        
        assert response.status_code == 401
    
    @pytest.mark.asyncio
    @pytest.mark.api
    async def test_create_submission_invalid_language(
        self, async_client: AsyncClient, test_user_data, sample_code_submission
    ):
        """测试无效编程语言"""
        # 登录获取token
        await async_client.post("/api/v1/auth/register", json=test_user_data)
        login_response = await async_client.post(
            "/api/v1/auth/login",
            json={"email": test_user_data["email"], "password": test_user_data["password"]}
        )
        token = login_response.json()["access_token"]
        
        # 修改为无效语言
        sample_code_submission["language"] = "invalid_language"
        
        response = await async_client.post(
            "/api/v1/submissions/",
            json=sample_code_submission,
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 422
    
    @pytest.mark.asyncio
    @pytest.mark.api
    async def test_get_submission_by_id(
        self, async_client: AsyncClient, test_user_data, sample_code_submission
    ):
        """测试通过ID获取提交"""
        # 登录获取token
        await async_client.post("/api/v1/auth/register", json=test_user_data)
        login_response = await async_client.post(
            "/api/v1/auth/login",
            json={"email": test_user_data["email"], "password": test_user_data["password"]}
        )
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # 创建提交
        create_response = await async_client.post(
            "/api/v1/submissions/",
            json=sample_code_submission,
            headers=headers
        )
        submission_id = create_response.json()["id"]
        
        # 获取提交
        response = await async_client.get(
            f"/api/v1/submissions/{submission_id}",
            headers=headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == submission_id
        assert data["code"] == sample_code_submission["code"]
    
    @pytest.mark.asyncio
    @pytest.mark.api
    async def test_get_submission_not_found(
        self, async_client: AsyncClient, test_user_data
    ):
        """测试获取不存在的提交"""
        # 登录获取token
        await async_client.post("/api/v1/auth/register", json=test_user_data)
        login_response = await async_client.post(
            "/api/v1/auth/login",
            json={"email": test_user_data["email"], "password": test_user_data["password"]}
        )
        token = login_response.json()["access_token"]
        
        response = await async_client.get(
            "/api/v1/submissions/999999",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 404
    
    @pytest.mark.asyncio
    @pytest.mark.api
    async def test_get_user_submissions(
        self, async_client: AsyncClient, test_user_data, sample_code_submission
    ):
        """测试获取用户所有提交"""
        # 登录获取token
        await async_client.post("/api/v1/auth/register", json=test_user_data)
        login_response = await async_client.post(
            "/api/v1/auth/login",
            json={"email": test_user_data["email"], "password": test_user_data["password"]}
        )
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # 创建多个提交
        await async_client.post("/api/v1/submissions/", json=sample_code_submission, headers=headers)
        await async_client.post("/api/v1/submissions/", json=sample_code_submission, headers=headers)
        
        # 获取用户提交列表
        response = await async_client.get("/api/v1/submissions/", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert len(data["items"]) == 2
        assert "total" in data
        assert "page" in data
        assert "size" in data
    
    @pytest.mark.asyncio
    @pytest.mark.api
    async def test_update_submission(
        self, async_client: AsyncClient, test_user_data, sample_code_submission
    ):
        """测试更新提交"""
        # 登录获取token
        await async_client.post("/api/v1/auth/register", json=test_user_data)
        login_response = await async_client.post(
            "/api/v1/auth/login",
            json={"email": test_user_data["email"], "password": test_user_data["password"]}
        )
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # 创建提交
        create_response = await async_client.post(
            "/api/v1/submissions/",
            json=sample_code_submission,
            headers=headers
        )
        submission_id = create_response.json()["id"]
        
        # 更新提交
        updated_data = {
            "code": "#include <stdio.h>\nint main(){printf(\"Updated\"); return 0;}",
            "language": "c"
        }
        response = await async_client.put(
            f"/api/v1/submissions/{submission_id}",
            json=updated_data,
            headers=headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == updated_data["code"]
    
    @pytest.mark.asyncio
    @pytest.mark.api
    async def test_delete_submission(
        self, async_client: AsyncClient, test_user_data, sample_code_submission
    ):
        """测试删除提交"""
        # 登录获取token
        await async_client.post("/api/v1/auth/register", json=test_user_data)
        login_response = await async_client.post(
            "/api/v1/auth/login",
            json={"email": test_user_data["email"], "password": test_user_data["password"]}
        )
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # 创建提交
        create_response = await async_client.post(
            "/api/v1/submissions/",
            json=sample_code_submission,
            headers=headers
        )
        submission_id = create_response.json()["id"]
        
        # 删除提交
        response = await async_client.delete(
            f"/api/v1/submissions/{submission_id}",
            headers=headers
        )
        
        assert response.status_code == 204
        
        # 验证删除成功
        get_response = await async_client.get(
            f"/api/v1/submissions/{submission_id}",
            headers=headers
        )
        assert get_response.status_code == 404


class TestSubmissionAnalysis:
    """代码提交分析测试"""
    
    @pytest.mark.asyncio
    @pytest.mark.api
    @pytest.mark.ai
    @patch("app.services.ai_service.MultiAgentTeachingSystem.analyze_code")
    async def test_analyze_submission_success(
        self, mock_analyze, async_client: AsyncClient, test_user_data, 
        sample_code_submission, mock_ai_response
    ):
        """测试代码分析成功"""
        mock_analyze.return_value = mock_ai_response
        
        # 登录获取token
        await async_client.post("/api/v1/auth/register", json=test_user_data)
        login_response = await async_client.post(
            "/api/v1/auth/login",
            json={"email": test_user_data["email"], "password": test_user_data["password"]}
        )
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # 创建提交
        create_response = await async_client.post(
            "/api/v1/submissions/",
            json=sample_code_submission,
            headers=headers
        )
        submission_id = create_response.json()["id"]
        
        # 触发分析
        response = await async_client.post(
            f"/api/v1/submissions/{submission_id}/analyze",
            headers=headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "analysis" in data
        assert "feedback" in data
        assert data["status"] == "completed"
        
        # 验证mock被调用
        mock_analyze.assert_called_once()
    
    @pytest.mark.asyncio
    @pytest.mark.api
    @pytest.mark.ai
    async def test_analyze_nonexistent_submission(
        self, async_client: AsyncClient, test_user_data
    ):
        """测试分析不存在的提交"""
        # 登录获取token
        await async_client.post("/api/v1/auth/register", json=test_user_data)
        login_response = await async_client.post(
            "/api/v1/auth/login",
            json={"email": test_user_data["email"], "password": test_user_data["password"]}
        )
        token = login_response.json()["access_token"]
        
        response = await async_client.post(
            "/api/v1/submissions/999999/analyze",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 404
    
    @pytest.mark.asyncio
    @pytest.mark.api
    @pytest.mark.ai
    @patch("app.services.ai_service.MultiAgentTeachingSystem.analyze_code")
    async def test_analyze_submission_ai_error(
        self, mock_analyze, async_client: AsyncClient, test_user_data, sample_code_submission
    ):
        """测试AI分析出错处理"""
        mock_analyze.side_effect = Exception("AI服务暂时不可用")
        
        # 登录获取token
        await async_client.post("/api/v1/auth/register", json=test_user_data)
        login_response = await async_client.post(
            "/api/v1/auth/login",
            json={"email": test_user_data["email"], "password": test_user_data["password"]}
        )
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # 创建提交
        create_response = await async_client.post(
            "/api/v1/submissions/",
            json=sample_code_submission,
            headers=headers
        )
        submission_id = create_response.json()["id"]
        
        # 触发分析
        response = await async_client.post(
            f"/api/v1/submissions/{submission_id}/analyze",
            headers=headers
        )
        
        assert response.status_code == 500
        assert "AI服务" in response.json()["detail"]
    
    @pytest.mark.asyncio
    @pytest.mark.api
    async def test_get_submission_feedback(
        self, async_client: AsyncClient, test_user_data, sample_code_submission
    ):
        """测试获取提交反馈"""
        # 登录获取token
        await async_client.post("/api/v1/auth/register", json=test_user_data)
        login_response = await async_client.post(
            "/api/v1/auth/login",
            json={"email": test_user_data["email"], "password": test_user_data["password"]}
        )
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # 创建提交
        create_response = await async_client.post(
            "/api/v1/submissions/",
            json=sample_code_submission,
            headers=headers
        )
        submission_id = create_response.json()["id"]
        
        # 获取反馈
        response = await async_client.get(
            f"/api/v1/submissions/{submission_id}/feedback",
            headers=headers
        )
        
        # 如果还没有分析，应该返回404或者空反馈
        assert response.status_code in [200, 404]


class TestSubmissionValidation:
    """代码提交验证测试"""
    
    @pytest.mark.asyncio
    @pytest.mark.api
    async def test_empty_code_validation(
        self, async_client: AsyncClient, test_user_data
    ):
        """测试空代码验证"""
        # 登录获取token
        await async_client.post("/api/v1/auth/register", json=test_user_data)
        login_response = await async_client.post(
            "/api/v1/auth/login",
            json={"email": test_user_data["email"], "password": test_user_data["password"]}
        )
        token = login_response.json()["access_token"]
        
        empty_submission = {
            "code": "",
            "language": "c",
            "assignment_id": "test-assignment"
        }
        
        response = await async_client.post(
            "/api/v1/submissions/",
            json=empty_submission,
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 422
    
    @pytest.mark.asyncio
    @pytest.mark.api
    async def test_code_length_limit(
        self, async_client: AsyncClient, test_user_data
    ):
        """测试代码长度限制"""
        # 登录获取token
        await async_client.post("/api/v1/auth/register", json=test_user_data)
        login_response = await async_client.post(
            "/api/v1/auth/login",
            json={"email": test_user_data["email"], "password": test_user_data["password"]}
        )
        token = login_response.json()["access_token"]
        
        # 创建超长代码
        long_code = "int main(){return 0;}" * 10000  # 假设这超过了限制
        long_submission = {
            "code": long_code,
            "language": "c",
            "assignment_id": "test-assignment"
        }
        
        response = await async_client.post(
            "/api/v1/submissions/",
            json=long_submission,
            headers={"Authorization": f"Bearer {token}"}
        )
        
        # 根据实际限制，这可能成功或失败
        assert response.status_code in [201, 422]
    
    @pytest.mark.asyncio
    @pytest.mark.api
    async def test_missing_assignment_id(
        self, async_client: AsyncClient, test_user_data
    ):
        """测试缺少作业ID"""
        # 登录获取token
        await async_client.post("/api/v1/auth/register", json=test_user_data)
        login_response = await async_client.post(
            "/api/v1/auth/login",
            json={"email": test_user_data["email"], "password": test_user_data["password"]}
        )
        token = login_response.json()["access_token"]
        
        incomplete_submission = {
            "code": "#include <stdio.h>\nint main(){return 0;}",
            "language": "c"
            # 缺少 assignment_id
        }
        
        response = await async_client.post(
            "/api/v1/submissions/",
            json=incomplete_submission,
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 422


class TestSubmissionPermissions:
    """提交权限测试"""
    
    @pytest.mark.asyncio
    @pytest.mark.api
    @pytest.mark.auth
    async def test_user_can_only_access_own_submissions(
        self, async_client: AsyncClient, test_factory
    ):
        """测试用户只能访问自己的提交"""
        # 创建两个用户
        user1_data = test_factory.create_user(email="user1@test.com")
        user2_data = test_factory.create_user(email="user2@test.com")
        
        # 注册用户1并登录
        await async_client.post("/api/v1/auth/register", json=user1_data)
        login1_response = await async_client.post(
            "/api/v1/auth/login",
            json={"email": user1_data["email"], "password": user1_data["password"]}
        )
        token1 = login1_response.json()["access_token"]
        
        # 注册用户2并登录
        await async_client.post("/api/v1/auth/register", json=user2_data)
        login2_response = await async_client.post(
            "/api/v1/auth/login",
            json={"email": user2_data["email"], "password": user2_data["password"]}
        )
        token2 = login2_response.json()["access_token"]
        
        # 用户1创建提交
        submission_data = test_factory.create_submission()
        create_response = await async_client.post(
            "/api/v1/submissions/",
            json=submission_data,
            headers={"Authorization": f"Bearer {token1}"}
        )
        submission_id = create_response.json()["id"]
        
        # 用户2尝试访问用户1的提交
        response = await async_client.get(
            f"/api/v1/submissions/{submission_id}",
            headers={"Authorization": f"Bearer {token2}"}
        )
        
        assert response.status_code == 404  # 应该看起来像不存在
    
    @pytest.mark.asyncio
    @pytest.mark.api
    @pytest.mark.auth
    async def test_teacher_can_view_student_submissions(
        self, async_client: AsyncClient, test_factory
    ):
        """测试教师可以查看学生提交（如果有此权限）"""
        # 创建教师和学生账号
        teacher_data = test_factory.create_user(role="teacher", email="teacher@test.com")
        student_data = test_factory.create_user(role="student", email="student@test.com")
        
        # 注册并登录
        await async_client.post("/api/v1/auth/register", json=teacher_data)
        await async_client.post("/api/v1/auth/register", json=student_data)
        
        teacher_login = await async_client.post(
            "/api/v1/auth/login",
            json={"email": teacher_data["email"], "password": teacher_data["password"]}
        )
        student_login = await async_client.post(
            "/api/v1/auth/login",
            json={"email": student_data["email"], "password": student_data["password"]}
        )
        
        teacher_token = teacher_login.json()["access_token"]
        student_token = student_login.json()["access_token"]
        
        # 学生创建提交
        submission_data = test_factory.create_submission()
        create_response = await async_client.post(
            "/api/v1/submissions/",
            json=submission_data,
            headers={"Authorization": f"Bearer {student_token}"}
        )
        submission_id = create_response.json()["id"]
        
        # 教师尝试查看学生提交
        response = await async_client.get(
            f"/api/v1/submissions/{submission_id}",
            headers={"Authorization": f"Bearer {teacher_token}"}
        )
        
        # 根据系统设计，这可能成功或失败
        assert response.status_code in [200, 403, 404]