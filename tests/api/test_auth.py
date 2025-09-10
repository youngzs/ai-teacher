"""
认证API测试模块
测试用户注册、登录、权限验证等认证相关功能
"""

import pytest
from httpx import AsyncClient
from unittest.mock import patch


class TestAuthAPI:
    """认证API测试类"""
    
    @pytest.mark.asyncio
    @pytest.mark.api
    @pytest.mark.auth
    async def test_user_registration_success(self, async_client: AsyncClient, test_user_data):
        """测试用户注册成功"""
        response = await async_client.post("/api/v1/auth/register", json=test_user_data)
        
        assert response.status_code == 201
        data = response.json()
        assert "id" in data
        assert data["email"] == test_user_data["email"]
        assert data["full_name"] == test_user_data["full_name"]
        assert data["role"] == test_user_data["role"]
        assert "password" not in data  # 密码不应该返回
    
    @pytest.mark.asyncio
    @pytest.mark.api
    @pytest.mark.auth
    async def test_user_registration_duplicate_email(self, async_client: AsyncClient, test_user_data):
        """测试重复邮箱注册失败"""
        # 第一次注册
        response1 = await async_client.post("/api/v1/auth/register", json=test_user_data)
        assert response1.status_code == 201
        
        # 第二次注册相同邮箱
        response2 = await async_client.post("/api/v1/auth/register", json=test_user_data)
        assert response2.status_code == 400
        assert "already registered" in response2.json()["detail"].lower()
    
    @pytest.mark.asyncio
    @pytest.mark.api
    @pytest.mark.auth
    async def test_user_registration_invalid_email(self, async_client: AsyncClient, test_user_data):
        """测试无效邮箱格式"""
        test_user_data["email"] = "invalid-email"
        response = await async_client.post("/api/v1/auth/register", json=test_user_data)
        
        assert response.status_code == 422
        errors = response.json()["detail"]
        assert any(error["type"] == "value_error" for error in errors)
    
    @pytest.mark.asyncio
    @pytest.mark.api
    @pytest.mark.auth
    async def test_user_registration_weak_password(self, async_client: AsyncClient, test_user_data):
        """测试弱密码验证"""
        test_user_data["password"] = "123"
        response = await async_client.post("/api/v1/auth/register", json=test_user_data)
        
        assert response.status_code == 422
    
    @pytest.mark.asyncio
    @pytest.mark.api
    @pytest.mark.auth
    async def test_user_login_success(self, async_client: AsyncClient, test_user_data):
        """测试用户登录成功"""
        # 先注册
        await async_client.post("/api/v1/auth/register", json=test_user_data)
        
        # 然后登录
        login_data = {
            "email": test_user_data["email"],
            "password": test_user_data["password"]
        }
        response = await async_client.post("/api/v1/auth/login", json=login_data)
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "token_type" in data
        assert data["token_type"] == "bearer"
        assert "user" in data
        assert data["user"]["email"] == test_user_data["email"]
    
    @pytest.mark.asyncio
    @pytest.mark.api
    @pytest.mark.auth
    async def test_user_login_wrong_password(self, async_client: AsyncClient, test_user_data):
        """测试错误密码登录失败"""
        # 先注册
        await async_client.post("/api/v1/auth/register", json=test_user_data)
        
        # 用错误密码登录
        login_data = {
            "email": test_user_data["email"],
            "password": "wrongpassword"
        }
        response = await async_client.post("/api/v1/auth/login", json=login_data)
        
        assert response.status_code == 401
        assert "incorrect" in response.json()["detail"].lower()
    
    @pytest.mark.asyncio
    @pytest.mark.api
    @pytest.mark.auth
    async def test_user_login_nonexistent_email(self, async_client: AsyncClient):
        """测试不存在的邮箱登录失败"""
        login_data = {
            "email": "nonexistent@university.edu",
            "password": "somepassword"
        }
        response = await async_client.post("/api/v1/auth/login", json=login_data)
        
        assert response.status_code == 401
        assert "incorrect" in response.json()["detail"].lower()
    
    @pytest.mark.asyncio
    @pytest.mark.api
    @pytest.mark.auth
    async def test_get_current_user(self, async_client: AsyncClient, test_user_data):
        """测试获取当前用户信息"""
        # 注册并登录获取token
        await async_client.post("/api/v1/auth/register", json=test_user_data)
        login_response = await async_client.post(
            "/api/v1/auth/login",
            json={"email": test_user_data["email"], "password": test_user_data["password"]}
        )
        token = login_response.json()["access_token"]
        
        # 获取用户信息
        response = await async_client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == test_user_data["email"]
        assert data["full_name"] == test_user_data["full_name"]
    
    @pytest.mark.asyncio
    @pytest.mark.api
    @pytest.mark.auth
    async def test_get_current_user_invalid_token(self, async_client: AsyncClient):
        """测试无效token获取用户信息失败"""
        response = await async_client.get(
            "/api/v1/auth/me",
            headers={"Authorization": "Bearer invalid_token"}
        )
        
        assert response.status_code == 401
    
    @pytest.mark.asyncio
    @pytest.mark.api
    @pytest.mark.auth
    async def test_get_current_user_no_token(self, async_client: AsyncClient):
        """测试无token获取用户信息失败"""
        response = await async_client.get("/api/v1/auth/me")
        
        assert response.status_code == 401
    
    @pytest.mark.asyncio
    @pytest.mark.api
    @pytest.mark.auth
    async def test_token_refresh(self, async_client: AsyncClient, test_user_data):
        """测试token刷新功能"""
        # 注册并登录
        await async_client.post("/api/v1/auth/register", json=test_user_data)
        login_response = await async_client.post(
            "/api/v1/auth/login",
            json={"email": test_user_data["email"], "password": test_user_data["password"]}
        )
        token = login_response.json()["access_token"]
        
        # 刷新token
        response = await async_client.post(
            "/api/v1/auth/refresh",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["access_token"] != token  # 新token应该不同
    
    @pytest.mark.asyncio
    @pytest.mark.api
    @pytest.mark.auth
    async def test_user_logout(self, async_client: AsyncClient, test_user_data):
        """测试用户登出功能"""
        # 注册并登录
        await async_client.post("/api/v1/auth/register", json=test_user_data)
        login_response = await async_client.post(
            "/api/v1/auth/login",
            json={"email": test_user_data["email"], "password": test_user_data["password"]}
        )
        token = login_response.json()["access_token"]
        
        # 登出
        response = await async_client.post(
            "/api/v1/auth/logout",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        
        # 验证token失效
        me_response = await async_client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert me_response.status_code == 401


class TestRoleBasedAccess:
    """基于角色的访问控制测试"""
    
    @pytest.mark.asyncio
    @pytest.mark.api
    @pytest.mark.auth
    async def test_teacher_role_assignment(self, async_client: AsyncClient, test_factory):
        """测试教师角色分配"""
        teacher_data = test_factory.create_user(role="teacher")
        response = await async_client.post("/api/v1/auth/register", json=teacher_data)
        
        assert response.status_code == 201
        assert response.json()["role"] == "teacher"
    
    @pytest.mark.asyncio
    @pytest.mark.api
    @pytest.mark.auth
    async def test_student_role_assignment(self, async_client: AsyncClient, test_factory):
        """测试学生角色分配"""
        student_data = test_factory.create_user(role="student")
        response = await async_client.post("/api/v1/auth/register", json=student_data)
        
        assert response.status_code == 201
        assert response.json()["role"] == "student"
    
    @pytest.mark.asyncio
    @pytest.mark.api
    @pytest.mark.auth
    async def test_invalid_role_rejection(self, async_client: AsyncClient, test_factory):
        """测试无效角色拒绝"""
        invalid_data = test_factory.create_user(role="admin")  # 假设admin角色无效
        response = await async_client.post("/api/v1/auth/register", json=invalid_data)
        
        assert response.status_code == 422


class TestPasswordSecurity:
    """密码安全测试"""
    
    @pytest.mark.asyncio
    @pytest.mark.api
    @pytest.mark.auth
    async def test_password_hashing(self, async_client: AsyncClient, test_user_data):
        """测试密码正确加密存储"""
        # 这个测试需要访问数据库来验证密码是否被正确哈希
        response = await async_client.post("/api/v1/auth/register", json=test_user_data)
        assert response.status_code == 201
        
        # 验证返回的数据不包含明文密码
        assert "password" not in response.json()
    
    @pytest.mark.asyncio
    @pytest.mark.api
    @pytest.mark.auth
    async def test_password_change_success(self, async_client: AsyncClient, test_user_data):
        """测试密码修改成功"""
        # 注册并登录
        await async_client.post("/api/v1/auth/register", json=test_user_data)
        login_response = await async_client.post(
            "/api/v1/auth/login",
            json={"email": test_user_data["email"], "password": test_user_data["password"]}
        )
        token = login_response.json()["access_token"]
        
        # 修改密码
        change_data = {
            "current_password": test_user_data["password"],
            "new_password": "newSecurePassword123"
        }
        response = await async_client.put(
            "/api/v1/auth/change-password",
            json=change_data,
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        
        # 验证新密码可以登录
        new_login_response = await async_client.post(
            "/api/v1/auth/login",
            json={"email": test_user_data["email"], "password": "newSecurePassword123"}
        )
        assert new_login_response.status_code == 200
    
    @pytest.mark.asyncio
    @pytest.mark.api
    @pytest.mark.auth
    async def test_password_change_wrong_current(self, async_client: AsyncClient, test_user_data):
        """测试错误的当前密码修改失败"""
        # 注册并登录
        await async_client.post("/api/v1/auth/register", json=test_user_data)
        login_response = await async_client.post(
            "/api/v1/auth/login",
            json={"email": test_user_data["email"], "password": test_user_data["password"]}
        )
        token = login_response.json()["access_token"]
        
        # 用错误的当前密码修改
        change_data = {
            "current_password": "wrongpassword",
            "new_password": "newSecurePassword123"
        }
        response = await async_client.put(
            "/api/v1/auth/change-password",
            json=change_data,
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 400