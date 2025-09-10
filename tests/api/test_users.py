"""
用户管理API测试模块
测试用户CRUD操作、权限管理等功能
"""

import pytest
from httpx import AsyncClient
from unittest.mock import patch


class TestUsersAPI:
    """用户管理API测试类"""
    
    @pytest.mark.asyncio
    @pytest.mark.api
    async def test_get_user_profile(
        self, async_client: AsyncClient, test_user_data
    ):
        """测试获取用户个人资料"""
        # 注册并登录
        await async_client.post("/api/v1/auth/register", json=test_user_data)
        login_response = await async_client.post(
            "/api/v1/auth/login",
            json={"email": test_user_data["email"], "password": test_user_data["password"]}
        )
        token = login_response.json()["access_token"]
        user_id = login_response.json()["user"]["id"]
        
        # 获取用户资料
        response = await async_client.get(
            f"/api/v1/users/{user_id}",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == test_user_data["email"]
        assert data["full_name"] == test_user_data["full_name"]
        assert data["role"] == test_user_data["role"]
        assert "password" not in data
    
    @pytest.mark.asyncio
    @pytest.mark.api
    async def test_update_user_profile(
        self, async_client: AsyncClient, test_user_data
    ):
        """测试更新用户个人资料"""
        # 注册并登录
        await async_client.post("/api/v1/auth/register", json=test_user_data)
        login_response = await async_client.post(
            "/api/v1/auth/login",
            json={"email": test_user_data["email"], "password": test_user_data["password"]}
        )
        token = login_response.json()["access_token"]
        user_id = login_response.json()["user"]["id"]
        
        # 更新资料
        update_data = {
            "full_name": "Updated Professor Name",
            "department": "Advanced Computer Science",
            "bio": "专门研究AI教育技术"
        }
        
        response = await async_client.put(
            f"/api/v1/users/{user_id}",
            json=update_data,
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["full_name"] == update_data["full_name"]
        assert data["department"] == update_data["department"]
        assert data["bio"] == update_data["bio"]
    
    @pytest.mark.asyncio
    @pytest.mark.api
    async def test_update_other_user_profile_forbidden(
        self, async_client: AsyncClient, test_factory
    ):
        """测试更新其他用户资料被禁止"""
        # 创建两个用户
        user1_data = test_factory.create_user(email="user1@test.com")
        user2_data = test_factory.create_user(email="user2@test.com")
        
        # 注册用户1
        await async_client.post("/api/v1/auth/register", json=user1_data)
        login1_response = await async_client.post(
            "/api/v1/auth/login",
            json={"email": user1_data["email"], "password": user1_data["password"]}
        )
        token1 = login1_response.json()["access_token"]
        
        # 注册用户2
        await async_client.post("/api/v1/auth/register", json=user2_data)
        login2_response = await async_client.post(
            "/api/v1/auth/login",
            json={"email": user2_data["email"], "password": user2_data["password"]}
        )
        user2_id = login2_response.json()["user"]["id"]
        
        # 用户1尝试更新用户2的资料
        update_data = {"full_name": "Hacked Name"}
        response = await async_client.put(
            f"/api/v1/users/{user2_id}",
            json=update_data,
            headers={"Authorization": f"Bearer {token1}"}
        )
        
        assert response.status_code == 403
    
    @pytest.mark.asyncio
    @pytest.mark.api
    async def test_get_user_not_found(
        self, async_client: AsyncClient, test_user_data
    ):
        """测试获取不存在的用户"""
        # 登录获取token
        await async_client.post("/api/v1/auth/register", json=test_user_data)
        login_response = await async_client.post(
            "/api/v1/auth/login",
            json={"email": test_user_data["email"], "password": test_user_data["password"]}
        )
        token = login_response.json()["access_token"]
        
        response = await async_client.get(
            "/api/v1/users/999999",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 404
    
    @pytest.mark.asyncio
    @pytest.mark.api
    async def test_get_users_list_teacher_only(
        self, async_client: AsyncClient, test_factory
    ):
        """测试只有教师能获取用户列表"""
        # 创建教师账号
        teacher_data = test_factory.create_user(role="teacher")
        await async_client.post("/api/v1/auth/register", json=teacher_data)
        teacher_login = await async_client.post(
            "/api/v1/auth/login",
            json={"email": teacher_data["email"], "password": teacher_data["password"]}
        )
        teacher_token = teacher_login.json()["access_token"]
        
        # 创建学生账号
        student_data = test_factory.create_user(role="student", email="student@test.com")
        await async_client.post("/api/v1/auth/register", json=student_data)
        student_login = await async_client.post(
            "/api/v1/auth/login",
            json={"email": student_data["email"], "password": student_data["password"]}
        )
        student_token = student_login.json()["access_token"]
        
        # 教师请求用户列表
        teacher_response = await async_client.get(
            "/api/v1/users/",
            headers={"Authorization": f"Bearer {teacher_token}"}
        )
        
        # 学生请求用户列表
        student_response = await async_client.get(
            "/api/v1/users/",
            headers={"Authorization": f"Bearer {student_token}"}
        )
        
        # 根据权限设计，教师应该能访问，学生不能
        assert teacher_response.status_code == 200
        assert student_response.status_code == 403


class TestUserPreferences:
    """用户偏好设置测试"""
    
    @pytest.mark.asyncio
    @pytest.mark.api
    async def test_update_user_preferences(
        self, async_client: AsyncClient, test_user_data
    ):
        """测试更新用户偏好设置"""
        # 注册并登录
        await async_client.post("/api/v1/auth/register", json=test_user_data)
        login_response = await async_client.post(
            "/api/v1/auth/login",
            json={"email": test_user_data["email"], "password": test_user_data["password"]}
        )
        token = login_response.json()["access_token"]
        user_id = login_response.json()["user"]["id"]
        
        # 更新偏好设置
        preferences = {
            "language": "zh-CN",
            "notification_email": True,
            "notification_push": False,
            "theme": "dark",
            "feedback_style": "detailed",
            "difficulty_preference": "adaptive"
        }
        
        response = await async_client.put(
            f"/api/v1/users/{user_id}/preferences",
            json=preferences,
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["language"] == "zh-CN"
        assert data["theme"] == "dark"
        assert data["feedback_style"] == "detailed"
    
    @pytest.mark.asyncio
    @pytest.mark.api
    async def test_get_user_preferences(
        self, async_client: AsyncClient, test_user_data
    ):
        """测试获取用户偏好设置"""
        # 注册并登录
        await async_client.post("/api/v1/auth/register", json=test_user_data)
        login_response = await async_client.post(
            "/api/v1/auth/login",
            json={"email": test_user_data["email"], "password": test_user_data["password"]}
        )
        token = login_response.json()["access_token"]
        user_id = login_response.json()["user"]["id"]
        
        # 获取偏好设置
        response = await async_client.get(
            f"/api/v1/users/{user_id}/preferences",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        # 应该有默认偏好设置
        assert "language" in data
        assert "theme" in data


class TestUserStatistics:
    """用户统计信息测试"""
    
    @pytest.mark.asyncio
    @pytest.mark.api
    async def test_get_user_statistics(
        self, async_client: AsyncClient, test_user_data
    ):
        """测试获取用户统计信息"""
        # 注册并登录
        await async_client.post("/api/v1/auth/register", json=test_user_data)
        login_response = await async_client.post(
            "/api/v1/auth/login",
            json={"email": test_user_data["email"], "password": test_user_data["password"]}
        )
        token = login_response.json()["access_token"]
        user_id = login_response.json()["user"]["id"]
        
        # 获取统计信息
        response = await async_client.get(
            f"/api/v1/users/{user_id}/statistics",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "total_submissions" in data
        assert "average_score" in data
        assert "learning_progress" in data
        assert "activity_summary" in data
    
    @pytest.mark.asyncio
    @pytest.mark.api
    async def test_get_teacher_dashboard_stats(
        self, async_client: AsyncClient, test_factory
    ):
        """测试教师仪表板统计"""
        # 创建教师账号
        teacher_data = test_factory.create_user(role="teacher")
        await async_client.post("/api/v1/auth/register", json=teacher_data)
        login_response = await async_client.post(
            "/api/v1/auth/login",
            json={"email": teacher_data["email"], "password": teacher_data["password"]}
        )
        token = login_response.json()["access_token"]
        user_id = login_response.json()["user"]["id"]
        
        # 获取教师统计
        response = await async_client.get(
            f"/api/v1/users/{user_id}/teacher-stats",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "total_students" in data
        assert "total_assignments" in data
        assert "pending_reviews" in data
        assert "class_performance" in data


class TestUserActivity:
    """用户活动测试"""
    
    @pytest.mark.asyncio
    @pytest.mark.api
    async def test_record_user_activity(
        self, async_client: AsyncClient, test_user_data
    ):
        """测试记录用户活动"""
        # 注册并登录
        await async_client.post("/api/v1/auth/register", json=test_user_data)
        login_response = await async_client.post(
            "/api/v1/auth/login",
            json={"email": test_user_data["email"], "password": test_user_data["password"]}
        )
        token = login_response.json()["access_token"]
        
        # 记录活动
        activity_data = {
            "action": "code_submission",
            "details": {
                "assignment_id": "basic-loops",
                "language": "c",
                "duration_seconds": 300
            }
        }
        
        response = await async_client.post(
            "/api/v1/users/activity",
            json=activity_data,
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 201
    
    @pytest.mark.asyncio
    @pytest.mark.api
    async def test_get_user_activity_log(
        self, async_client: AsyncClient, test_user_data
    ):
        """测试获取用户活动日志"""
        # 注册并登录
        await async_client.post("/api/v1/auth/register", json=test_user_data)
        login_response = await async_client.post(
            "/api/v1/auth/login",
            json={"email": test_user_data["email"], "password": test_user_data["password"]}
        )
        token = login_response.json()["access_token"]
        user_id = login_response.json()["user"]["id"]
        
        # 获取活动日志
        response = await async_client.get(
            f"/api/v1/users/{user_id}/activity",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "total" in data


class TestUserValidation:
    """用户数据验证测试"""
    
    @pytest.mark.asyncio
    @pytest.mark.api
    async def test_invalid_email_format(self, async_client: AsyncClient):
        """测试无效邮箱格式"""
        invalid_data = {
            "email": "invalid-email-format",
            "password": "validpassword123",
            "full_name": "Test User",
            "role": "student",
            "university": "Test University",
            "department": "Computer Science"
        }
        
        response = await async_client.post("/api/v1/auth/register", json=invalid_data)
        assert response.status_code == 422
    
    @pytest.mark.asyncio
    @pytest.mark.api
    async def test_missing_required_fields(self, async_client: AsyncClient):
        """测试缺少必填字段"""
        incomplete_data = {
            "email": "test@university.edu",
            "password": "validpassword123"
            # 缺少其他必填字段
        }
        
        response = await async_client.post("/api/v1/auth/register", json=incomplete_data)
        assert response.status_code == 422
        
        errors = response.json()["detail"]
        required_fields = ["full_name", "role", "university"]
        for field in required_fields:
            assert any(field in str(error) for error in errors)
    
    @pytest.mark.asyncio
    @pytest.mark.api
    async def test_invalid_role_value(self, async_client: AsyncClient):
        """测试无效角色值"""
        invalid_role_data = {
            "email": "test@university.edu",
            "password": "validpassword123",
            "full_name": "Test User",
            "role": "administrator",  # 假设这个角色无效
            "university": "Test University",
            "department": "Computer Science"
        }
        
        response = await async_client.post("/api/v1/auth/register", json=invalid_role_data)
        assert response.status_code == 422
    
    @pytest.mark.asyncio
    @pytest.mark.api
    async def test_password_strength_validation(self, async_client: AsyncClient):
        """测试密码强度验证"""
        weak_passwords = ["123", "abc", "password", "12345678"]
        
        for weak_password in weak_passwords:
            weak_password_data = {
                "email": f"test{weak_password}@university.edu",
                "password": weak_password,
                "full_name": "Test User",
                "role": "student",
                "university": "Test University",
                "department": "Computer Science"
            }
            
            response = await async_client.post("/api/v1/auth/register", json=weak_password_data)
            assert response.status_code == 422


class TestUserSearch:
    """用户搜索测试"""
    
    @pytest.mark.asyncio
    @pytest.mark.api
    async def test_search_users_by_name(
        self, async_client: AsyncClient, test_factory
    ):
        """测试按姓名搜索用户"""
        # 创建教师账号（用于搜索权限）
        teacher_data = test_factory.create_user(role="teacher")
        await async_client.post("/api/v1/auth/register", json=teacher_data)
        login_response = await async_client.post(
            "/api/v1/auth/login",
            json={"email": teacher_data["email"], "password": teacher_data["password"]}
        )
        token = login_response.json()["access_token"]
        
        # 创建几个学生
        students = [
            test_factory.create_user(role="student", email="alice@test.com", full_name="Alice Johnson"),
            test_factory.create_user(role="student", email="bob@test.com", full_name="Bob Smith"),
            test_factory.create_user(role="student", email="carol@test.com", full_name="Carol Johnson")
        ]
        
        for student in students:
            await async_client.post("/api/v1/auth/register", json=student)
        
        # 搜索含有"Johnson"的用户
        response = await async_client.get(
            "/api/v1/users/search?q=Johnson",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 2  # Alice和Carol
        names = [user["full_name"] for user in data["items"]]
        assert "Alice Johnson" in names
        assert "Carol Johnson" in names
    
    @pytest.mark.asyncio
    @pytest.mark.api
    async def test_search_users_by_email(
        self, async_client: AsyncClient, test_factory
    ):
        """测试按邮箱搜索用户"""
        # 创建教师账号
        teacher_data = test_factory.create_user(role="teacher")
        await async_client.post("/api/v1/auth/register", json=teacher_data)
        login_response = await async_client.post(
            "/api/v1/auth/login",
            json={"email": teacher_data["email"], "password": teacher_data["password"]}
        )
        token = login_response.json()["access_token"]
        
        # 创建学生
        student_data = test_factory.create_user(role="student", email="specific@university.edu")
        await async_client.post("/api/v1/auth/register", json=student_data)
        
        # 按邮箱搜索
        response = await async_client.get(
            "/api/v1/users/search?q=specific@university.edu",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 1
        assert data["items"][0]["email"] == "specific@university.edu"