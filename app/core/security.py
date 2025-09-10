"""
AI教学助手系统 - 安全认证模块
包含JWT令牌处理、密码加密、权限验证等安全功能

Author: AI Backend Architecture Expert
Date: 2025-09-10
"""

from datetime import datetime, timedelta
from typing import Any, Optional, Dict, Union
from jose import JWTError, jwt
from passlib.context import CryptContext
from passlib.hash import bcrypt
from fastapi import HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import secrets
import hashlib
from enum import Enum

from .config import settings


class UserRole(Enum):
    """用户角色枚举"""
    STUDENT = "student"
    TEACHER = "teacher" 
    ADMIN = "admin"


class PermissionLevel(Enum):
    """权限级别枚举"""
    READ = "read"
    WRITE = "write"
    DELETE = "delete"
    ADMIN = "admin"


# 密码加密上下文
pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
    bcrypt__rounds=12  # 增加安全性
)

# HTTP Bearer认证
security = HTTPBearer()


def create_password_hash(password: str) -> str:
    """创建密码哈希"""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """验证密码"""
    try:
        return pwd_context.verify(plain_password, hashed_password)
    except Exception:
        return False


def generate_password_reset_token() -> str:
    """生成密码重置令牌"""
    return secrets.token_urlsafe(32)


def create_access_token(
    subject: Union[str, Any],
    expires_delta: Optional[timedelta] = None,
    additional_claims: Optional[Dict[str, Any]] = None
) -> str:
    """
    创建访问令牌
    
    Args:
        subject: 令牌主体（通常是用户ID）
        expires_delta: 过期时间增量
        additional_claims: 额外的声明信息
        
    Returns:
        JWT访问令牌字符串
    """
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
    
    to_encode = {
        "exp": expire,
        "sub": str(subject),
        "iat": datetime.utcnow(),
        "type": "access"
    }
    
    if additional_claims:
        to_encode.update(additional_claims)
    
    encoded_jwt = jwt.encode(
        to_encode, 
        settings.SECRET_KEY, 
        algorithm=settings.ALGORITHM
    )
    return encoded_jwt


def create_refresh_token(
    subject: Union[str, Any],
    expires_delta: Optional[timedelta] = None
) -> str:
    """
    创建刷新令牌
    
    Args:
        subject: 令牌主体（通常是用户ID）
        expires_delta: 过期时间增量
        
    Returns:
        JWT刷新令牌字符串
    """
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            days=settings.REFRESH_TOKEN_EXPIRE_DAYS
        )
    
    to_encode = {
        "exp": expire,
        "sub": str(subject),
        "iat": datetime.utcnow(),
        "type": "refresh"
    }
    
    encoded_jwt = jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )
    return encoded_jwt


def decode_token(token: str) -> Dict[str, Any]:
    """
    解码JWT令牌
    
    Args:
        token: JWT令牌字符串
        
    Returns:
        令牌payload字典
        
    Raises:
        HTTPException: 令牌无效或过期
    """
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )


def verify_token(token: str, token_type: str = "access") -> Dict[str, Any]:
    """
    验证令牌并返回payload
    
    Args:
        token: JWT令牌
        token_type: 令牌类型（access或refresh）
        
    Returns:
        令牌payload
        
    Raises:
        HTTPException: 令牌无效、过期或类型不匹配
    """
    payload = decode_token(token)
    
    # 检查令牌类型
    if payload.get("type") != token_type:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token type. Expected {token_type}",
        )
    
    # 检查过期时间
    exp = payload.get("exp")
    if exp is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has no expiration",
        )
    
    if datetime.utcnow() > datetime.fromtimestamp(exp):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
        )
    
    return payload


async def get_current_user_id(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> str:
    """
    从令牌中获取当前用户ID
    
    Args:
        credentials: HTTP认证凭据
        
    Returns:
        用户ID字符串
    """
    payload = verify_token(credentials.credentials)
    user_id = payload.get("sub")
    
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
        )
    
    return user_id


def create_api_key() -> str:
    """创建API密钥"""
    return f"ai_teacher_{secrets.token_urlsafe(32)}"


def hash_api_key(api_key: str) -> str:
    """对API密钥进行哈希"""
    return hashlib.sha256(api_key.encode()).hexdigest()


def verify_api_key(api_key: str, hashed_key: str) -> bool:
    """验证API密钥"""
    return hash_api_key(api_key) == hashed_key


def require_permissions(*required_permissions: PermissionLevel):
    """
    权限装饰器工厂
    
    Args:
        required_permissions: 所需的权限级别
        
    Returns:
        权限检查装饰器
    """
    def permission_decorator(func):
        async def wrapper(*args, **kwargs):
            # 从kwargs中获取当前用户信息
            current_user = kwargs.get('current_user')
            if not current_user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Authentication required"
                )
            
            # 检查用户权限
            user_permissions = current_user.get('permissions', [])
            for permission in required_permissions:
                if permission.value not in user_permissions:
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail=f"Insufficient permissions. Required: {permission.value}"
                    )
            
            return await func(*args, **kwargs)
        return wrapper
    return permission_decorator


def require_role(*required_roles: UserRole):
    """
    角色装饰器工厂
    
    Args:
        required_roles: 所需的用户角色
        
    Returns:
        角色检查装饰器
    """
    def role_decorator(func):
        async def wrapper(*args, **kwargs):
            current_user = kwargs.get('current_user')
            if not current_user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Authentication required"
                )
            
            user_role = current_user.get('role')
            required_role_values = [role.value for role in required_roles]
            
            if user_role not in required_role_values:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Insufficient role. Required: {required_role_values}"
                )
            
            return await func(*args, **kwargs)
        return wrapper
    return role_decorator


class RateLimiter:
    """速率限制器"""
    
    def __init__(self):
        self.requests = {}
    
    def is_allowed(self, key: str, limit: int, window: int) -> bool:
        """
        检查是否允许请求
        
        Args:
            key: 限制键（通常是用户ID或IP）
            limit: 限制次数
            window: 时间窗口（秒）
            
        Returns:
            是否允许请求
        """
        now = datetime.utcnow()
        
        if key not in self.requests:
            self.requests[key] = []
        
        # 清理过期的请求记录
        self.requests[key] = [
            req_time for req_time in self.requests[key]
            if (now - req_time).total_seconds() < window
        ]
        
        # 检查是否超过限制
        if len(self.requests[key]) >= limit:
            return False
        
        # 记录当前请求
        self.requests[key].append(now)
        return True


# 全局速率限制器实例
rate_limiter = RateLimiter()


def check_rate_limit(key: str, limit: Optional[int] = None) -> bool:
    """
    检查速率限制
    
    Args:
        key: 限制键
        limit: 限制次数（默认使用配置值）
        
    Returns:
        是否允许请求
    """
    if limit is None:
        limit = settings.RATE_LIMIT_PER_MINUTE
    
    return rate_limiter.is_allowed(key, limit, 60)  # 60秒窗口


def generate_session_id() -> str:
    """生成会话ID"""
    return secrets.token_urlsafe(32)


def create_csrf_token() -> str:
    """创建CSRF令牌"""
    return secrets.token_urlsafe(32)


def verify_csrf_token(token: str, expected_token: str) -> bool:
    """验证CSRF令牌"""
    return token == expected_token


class SecurityHeaders:
    """安全头部配置"""
    
    @staticmethod
    def get_security_headers() -> Dict[str, str]:
        """获取安全头部"""
        return {
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "DENY",
            "X-XSS-Protection": "1; mode=block",
            "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
            "Referrer-Policy": "strict-origin-when-cross-origin",
            "Content-Security-Policy": "default-src 'self'",
        }


# 安全配置验证
def validate_security_config():
    """验证安全配置"""
    if len(settings.SECRET_KEY) < 32:
        raise ValueError("SECRET_KEY should be at least 32 characters long")
    
    if settings.ACCESS_TOKEN_EXPIRE_MINUTES < 1:
        raise ValueError("ACCESS_TOKEN_EXPIRE_MINUTES should be at least 1")
    
    if settings.REFRESH_TOKEN_EXPIRE_DAYS < 1:
        raise ValueError("REFRESH_TOKEN_EXPIRE_DAYS should be at least 1")


# 初始化时验证安全配置
validate_security_config()