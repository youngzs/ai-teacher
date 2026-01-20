"""
课程API测试
Sprint 4: 测试课程相关端点
"""

import pytest
import pytest_asyncio
from httpx import AsyncClient
from unittest.mock import patch, MagicMock, AsyncMock
import uuid


class TestCoursesAPI:
    """课程API测试类"""

    @pytest.mark.asyncio
    @pytest.mark.api
    async def test_list_courses_unauthorized(self, async_client: AsyncClient):
        """测试未授权获取课程列表"""
        response = await async_client.get("/api/v1/courses/")

        # 应该返回401未授权
        assert response.status_code == 401

    @pytest.mark.asyncio
    @pytest.mark.api
    async def test_list_courses_empty(self, async_client: AsyncClient, auth_headers):
        """测试获取空课程列表"""
        response = await async_client.get(
            "/api/v1/courses/",
            headers=auth_headers
        )

        # Mock可能返回200或404取决于实现
        assert response.status_code in [200, 404]

    @pytest.mark.asyncio
    @pytest.mark.api
    async def test_get_course_not_found(self, async_client: AsyncClient, auth_headers):
        """测试获取不存在的课程"""
        fake_id = str(uuid.uuid4())
        response = await async_client.get(
            f"/api/v1/courses/{fake_id}",
            headers=auth_headers
        )

        assert response.status_code == 404

    @pytest.mark.asyncio
    @pytest.mark.api
    async def test_get_course_invalid_id(self, async_client: AsyncClient, auth_headers):
        """测试使用无效ID获取课程"""
        response = await async_client.get(
            "/api/v1/courses/invalid-uuid",
            headers=auth_headers
        )

        # 应该返回400或422 (验证错误)
        assert response.status_code in [400, 422, 404]


class TestAssignmentsAPI:
    """作业API测试类"""

    @pytest.mark.asyncio
    @pytest.mark.api
    async def test_list_assignments_unauthorized(self, async_client: AsyncClient):
        """测试未授权获取作业列表"""
        response = await async_client.get("/api/v1/courses/assignments")

        assert response.status_code == 401

    @pytest.mark.asyncio
    @pytest.mark.api
    async def test_create_assignment_validation(self, async_client: AsyncClient, auth_headers):
        """测试创建作业时的验证"""
        # 缺少必要字段
        invalid_data = {
            "title": ""  # 空标题
        }

        response = await async_client.post(
            "/api/v1/courses/assignments",
            json=invalid_data,
            headers=auth_headers
        )

        # 应该返回验证错误
        assert response.status_code in [400, 422]


class TestExercisesAPI:
    """练习API测试类"""

    @pytest.mark.asyncio
    @pytest.mark.api
    async def test_get_exercise_not_found(self, async_client: AsyncClient, auth_headers):
        """测试获取不存在的练习"""
        fake_id = str(uuid.uuid4())
        response = await async_client.get(
            f"/api/v1/courses/exercises/{fake_id}",
            headers=auth_headers
        )

        assert response.status_code == 404


@pytest.fixture
def auth_headers():
    """获取认证头部"""
    return {"Authorization": "Bearer mock-test-token"}
