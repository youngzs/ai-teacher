"""
AI教学助手系统 - 认证相关模式定义
定义用户认证、注册、登录等相关的Pydantic模式

Author: AI Backend Architecture Expert
Date: 2025-09-10
"""

from pydantic import BaseModel, Field, validator, EmailStr
from typing import Optional, Dict, Any
from datetime import datetime
from enum import Enum

from .common import validate_non_empty_string, validate_username


class UserRole(str, Enum):
    """用户角色枚举"""
    STUDENT = "student"
    TEACHER = "teacher"
    ADMIN = "admin"


class UserRegister(BaseModel):
    """用户注册模式"""
    username: str = Field(..., min_length=3, max_length=20, description="用户名")
    email: EmailStr = Field(..., description="邮箱地址")
    password: str = Field(..., min_length=8, max_length=128, description="密码")
    full_name: str = Field(..., min_length=2, max_length=100, description="真实姓名")
    role: Optional[UserRole] = Field(UserRole.STUDENT, description="用户角色")
    
    # 额外信息
    phone: Optional[str] = Field(None, description="手机号码")
    organization: Optional[str] = Field(None, description="所属机构")
    
    @validator('username')
    def validate_username_format(cls, v):
        """验证用户名格式"""
        return validate_username(v)
    
    @validator('password')
    def validate_password_strength(cls, v):
        """验证密码强度"""
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        
        has_letter = any(c.isalpha() for c in v)
        has_digit = any(c.isdigit() for c in v)
        
        if not has_letter:
            raise ValueError('Password must contain at least one letter')
        if not has_digit:
            raise ValueError('Password must contain at least one digit')
        
        return v
    
    @validator('full_name')
    def validate_full_name(cls, v):
        """验证真实姓名"""
        return validate_non_empty_string(v)
    
    class Config:
        schema_extra = {
            "example": {
                "username": "student123",
                "email": "student@example.com",
                "password": "SecurePass123",
                "full_name": "张三",
                "role": "student",
                "phone": "13800138000",
                "organization": "计算机科学学院"
            }
        }


class UserLogin(BaseModel):
    """用户登录模式"""
    identifier: str = Field(..., description="用户名或邮箱")
    password: str = Field(..., description="密码")
    remember_me: bool = Field(False, description="记住我")
    
    class Config:
        schema_extra = {
            "example": {
                "identifier": "student@example.com",
                "password": "SecurePass123",
                "remember_me": false
            }
        }


class UserResponse(BaseModel):
    """用户信息响应模式"""
    id: str = Field(..., description="用户ID")
    username: str = Field(..., description="用户名")
    email: str = Field(..., description="邮箱地址")
    full_name: str = Field(..., description="真实姓名")
    role: UserRole = Field(..., description="用户角色")
    is_active: bool = Field(..., description="账户是否激活")
    
    # 可选字段
    phone: Optional[str] = Field(None, description="手机号码")
    organization: Optional[str] = Field(None, description="所属机构")
    avatar_url: Optional[str] = Field(None, description="头像URL")
    
    # 时间信息
    created_at: datetime = Field(..., description="创建时间")
    last_login_at: Optional[datetime] = Field(None, description="最后登录时间")
    
    # 统计信息
    profile_completeness: Optional[float] = Field(None, description="资料完整度")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
        schema_extra = {
            "example": {
                "id": "uuid-string",
                "username": "student123",
                "email": "student@example.com",
                "full_name": "张三",
                "role": "student",
                "is_active": true,
                "phone": "13800138000",
                "organization": "计算机科学学院",
                "avatar_url": "https://example.com/avatars/student123.jpg",
                "created_at": "2023-09-01T10:00:00",
                "last_login_at": "2023-09-10T15:30:00",
                "profile_completeness": 85.0
            }
        }


class TokenResponse(BaseModel):
    """令牌响应模式"""
    access_token: str = Field(..., description="访问令牌")
    refresh_token: str = Field(..., description="刷新令牌")
    token_type: str = Field("bearer", description="令牌类型")
    expires_in: int = Field(..., description="过期时间（秒）")
    
    # 用户信息
    user: UserResponse = Field(..., description="用户信息")
    
    # 权限信息
    permissions: Optional[list] = Field(None, description="用户权限列表")
    
    class Config:
        schema_extra = {
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer",
                "expires_in": 86400,
                "user": {
                    "id": "uuid-string",
                    "username": "student123",
                    "email": "student@example.com",
                    "full_name": "张三",
                    "role": "student",
                    "is_active": true
                },
                "permissions": ["read:own_submissions", "write:own_submissions"]
            }
        }


class PasswordReset(BaseModel):
    """密码重置请求模式"""
    email: EmailStr = Field(..., description="邮箱地址")
    
    class Config:
        schema_extra = {
            "example": {
                "email": "student@example.com"
            }
        }


class PasswordResetConfirm(BaseModel):
    """密码重置确认模式"""
    token: str = Field(..., description="重置令牌")
    new_password: str = Field(..., min_length=8, max_length=128, description="新密码")
    
    @validator('new_password')
    def validate_password_strength(cls, v):
        """验证密码强度"""
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        
        has_letter = any(c.isalpha() for c in v)
        has_digit = any(c.isdigit() for c in v)
        
        if not has_letter:
            raise ValueError('Password must contain at least one letter')
        if not has_digit:
            raise ValueError('Password must contain at least one digit')
        
        return v
    
    class Config:
        schema_extra = {
            "example": {
                "token": "reset-token-string",
                "new_password": "NewSecurePass123"
            }
        }


class PasswordChange(BaseModel):
    """密码修改模式"""
    current_password: str = Field(..., description="当前密码")
    new_password: str = Field(..., min_length=8, max_length=128, description="新密码")
    
    @validator('new_password')
    def validate_password_strength(cls, v):
        """验证密码强度"""
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        
        has_letter = any(c.isalpha() for c in v)
        has_digit = any(c.isdigit() for c in v)
        
        if not has_letter:
            raise ValueError('Password must contain at least one letter')
        if not has_digit:
            raise ValueError('Password must contain at least one digit')
        
        return v
    
    class Config:
        schema_extra = {
            "example": {
                "current_password": "OldPassword123",
                "new_password": "NewSecurePass123"
            }
        }


class UserUpdate(BaseModel):
    """用户信息更新模式"""
    full_name: Optional[str] = Field(None, min_length=2, max_length=100, description="真实姓名")
    phone: Optional[str] = Field(None, description="手机号码")
    organization: Optional[str] = Field(None, description="所属机构")
    avatar_url: Optional[str] = Field(None, description="头像URL")
    preferences: Optional[Dict[str, Any]] = Field(None, description="用户偏好设置")
    
    @validator('full_name')
    def validate_full_name(cls, v):
        """验证真实姓名"""
        if v is not None:
            return validate_non_empty_string(v)
        return v
    
    class Config:
        schema_extra = {
            "example": {
                "full_name": "李四",
                "phone": "13900139000",
                "organization": "软件工程学院",
                "avatar_url": "https://example.com/avatars/new-avatar.jpg",
                "preferences": {
                    "theme": "dark",
                    "language": "zh-CN",
                    "notifications": {
                        "email": true,
                        "push": false
                    }
                }
            }
        }


class ApiKeyCreate(BaseModel):
    """API密钥创建模式"""
    name: str = Field(..., min_length=1, max_length=100, description="密钥名称")
    permissions: list = Field([], description="权限列表")
    expires_in_days: Optional[int] = Field(None, ge=1, le=365, description="过期天数")
    
    @validator('name')
    def validate_name(cls, v):
        """验证密钥名称"""
        return validate_non_empty_string(v)
    
    class Config:
        schema_extra = {
            "example": {
                "name": "Frontend API Key",
                "permissions": ["read:submissions", "write:submissions"],
                "expires_in_days": 90
            }
        }


class ApiKeyResponse(BaseModel):
    """API密钥响应模式"""
    id: str = Field(..., description="密钥ID")
    name: str = Field(..., description="密钥名称")
    key: Optional[str] = Field(None, description="密钥值（仅在创建时返回）")
    prefix: str = Field(..., description="密钥前缀")
    permissions: list = Field(..., description="权限列表")
    is_active: bool = Field(..., description="是否激活")
    created_at: datetime = Field(..., description="创建时间")
    expires_at: Optional[datetime] = Field(None, description="过期时间")
    last_used_at: Optional[datetime] = Field(None, description="最后使用时间")
    usage_count: int = Field(..., description="使用次数")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class SessionInfo(BaseModel):
    """会话信息模式"""
    session_id: str = Field(..., description="会话ID")
    user_id: str = Field(..., description="用户ID")
    ip_address: str = Field(..., description="IP地址")
    user_agent: str = Field(..., description="用户代理")
    created_at: datetime = Field(..., description="创建时间")
    last_activity: datetime = Field(..., description="最后活动时间")
    is_active: bool = Field(..., description="是否活跃")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class LoginHistory(BaseModel):
    """登录历史模式"""
    id: str = Field(..., description="记录ID")
    user_id: str = Field(..., description="用户ID")
    ip_address: str = Field(..., description="IP地址")
    user_agent: str = Field(..., description="用户代理")
    location: Optional[str] = Field(None, description="登录地点")
    success: bool = Field(..., description="是否成功")
    failure_reason: Optional[str] = Field(None, description="失败原因")
    timestamp: datetime = Field(..., description="时间戳")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class TwoFactorSetup(BaseModel):
    """双因素认证设置模式"""
    enable: bool = Field(..., description="是否启用")
    method: str = Field("totp", description="认证方法")
    backup_codes: Optional[list] = Field(None, description="备用代码")


class TwoFactorVerify(BaseModel):
    """双因素认证验证模式"""
    code: str = Field(..., min_length=6, max_length=6, description="验证码")
    
    @validator('code')
    def validate_code_format(cls, v):
        """验证验证码格式"""
        if not v.isdigit():
            raise ValueError('Verification code must be 6 digits')
        return v


class UserPermissions(BaseModel):
    """用户权限模式"""
    user_id: str = Field(..., description="用户ID")
    permissions: list = Field(..., description="权限列表")
    roles: list = Field(..., description="角色列表")
    effective_permissions: list = Field(..., description="有效权限列表")


class RoleCreate(BaseModel):
    """角色创建模式"""
    name: str = Field(..., min_length=1, max_length=50, description="角色名称")
    description: Optional[str] = Field(None, description="角色描述")
    permissions: list = Field([], description="权限列表")
    
    @validator('name')
    def validate_role_name(cls, v):
        """验证角色名称"""
        return validate_non_empty_string(v)


class RoleResponse(BaseModel):
    """角色响应模式"""
    id: str = Field(..., description="角色ID")
    name: str = Field(..., description="角色名称")
    description: Optional[str] = Field(None, description="角色描述")
    permissions: list = Field(..., description="权限列表")
    user_count: int = Field(0, description="用户数量")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: Optional[datetime] = Field(None, description="更新时间")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


# 导出所有模式
__all__ = [
    "UserRole",
    "UserRegister",
    "UserLogin", 
    "UserResponse",
    "TokenResponse",
    "PasswordReset",
    "PasswordResetConfirm",
    "PasswordChange",
    "UserUpdate",
    "ApiKeyCreate",
    "ApiKeyResponse",
    "SessionInfo",
    "LoginHistory",
    "TwoFactorSetup",
    "TwoFactorVerify",
    "UserPermissions",
    "RoleCreate",
    "RoleResponse"
]