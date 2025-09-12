"""
AI教学助手系统 - 依赖注入模块
包含FastAPI依赖注入功能，如用户认证、权限检查等

Author: AI Backend Architecture Expert
Date: 2025-09-11
"""

from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional, Dict, Any
import json

from ..database.database import get_db
from ..database.models import User
from ..core.security import verify_token, check_rate_limit
from ..core.config import settings
from ..utils.logger import get_logger

logger = get_logger(__name__)

# HTTP Bearer认证实例
security = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> User:
    """
    获取当前认证用户
    
    Args:
        credentials: HTTP认证凭据
        db: 数据库会话
        
    Returns:
        当前用户对象
        
    Raises:
        HTTPException: 认证失败
    """
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication credentials required",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    try:
        # 验证token
        payload = verify_token(credentials.credentials)
        user_id = payload.get("sub")
        
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials"
            )
        
        # 查询用户
        result = await db.execute(
            select(User).where(User.id == user_id, User.is_active == True)
        )
        user = result.scalar_one_or_none()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found or inactive"
            )
        
        return user
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Authentication error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials"
        )


async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    获取当前活跃用户
    
    Args:
        current_user: 当前用户
        
    Returns:
        活跃的当前用户
        
    Raises:
        HTTPException: 用户未激活
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user account"
        )
    return current_user


def require_role(*allowed_roles: str):
    """
    角色权限装饰器工厂
    
    Args:
        allowed_roles: 允许的用户角色列表
        
    Returns:
        依赖函数
    """
    async def check_role(
        current_user: User = Depends(get_current_active_user)
    ) -> User:
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Operation requires one of these roles: {', '.join(allowed_roles)}"
            )
        return current_user
    
    return check_role


def require_student():
    """学生权限依赖"""
    return require_role("student")


def require_teacher():
    """教师权限依赖"""  
    return require_role("teacher")


def require_teacher_or_admin():
    """教师或管理员权限依赖"""
    return require_role("teacher", "admin")


def require_admin():
    """管理员权限依赖"""
    return require_role("admin")


async def check_ownership_or_teacher(
    resource_user_id: str,
    current_user: User = Depends(get_current_active_user)
) -> User:
    """
    检查资源所有权或教师权限
    
    Args:
        resource_user_id: 资源所属用户ID
        current_user: 当前用户
        
    Returns:
        当前用户
        
    Raises:
        HTTPException: 权限不足
    """
    # 管理员或教师可以访问所有资源
    if current_user.role in ["admin", "teacher"]:
        return current_user
    
    # 用户只能访问自己的资源
    if str(current_user.id) != str(resource_user_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied: insufficient permissions"
        )
    
    return current_user


async def rate_limit_check(
    request: Request,
    limit: int = None
) -> bool:
    """
    速率限制检查依赖
    
    Args:
        request: HTTP请求对象
        limit: 限制次数
        
    Returns:
        是否通过限制
        
    Raises:
        HTTPException: 超过速率限制
    """
    if limit is None:
        limit = settings.RATE_LIMIT_PER_MINUTE
    
    # 获取客户端IP
    client_ip = request.client.host
    
    # 检查速率限制
    if not check_rate_limit(f"api_{client_ip}", limit):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many requests. Please try again later."
        )
    
    return True


class OptionalAuth:
    """
    可选认证依赖
    如果提供了token则验证，否则返回None
    """
    
    def __init__(self):
        self.security = HTTPBearer(auto_error=False)
    
    async def __call__(
        self,
        credentials: Optional[HTTPAuthorizationCredentials] = Depends(HTTPBearer(auto_error=False)),
        db: AsyncSession = Depends(get_db)
    ) -> Optional[User]:
        """
        可选的用户认证
        
        Args:
            credentials: 可选的认证凭据
            db: 数据库会话
            
        Returns:
            用户对象或None
        """
        if not credentials:
            return None
        
        try:
            payload = verify_token(credentials.credentials)
            user_id = payload.get("sub")
            
            if user_id:
                result = await db.execute(
                    select(User).where(User.id == user_id, User.is_active == True)
                )
                return result.scalar_one_or_none()
        except Exception as e:
            logger.warning(f"Optional auth failed: {str(e)}")
            
        return None


# 创建可选认证实例
optional_auth = OptionalAuth()


def get_pagination_params(
    page: int = 1,
    size: int = 20
) -> Dict[str, Any]:
    """
    分页参数依赖
    
    Args:
        page: 页码（从1开始）
        size: 每页大小
        
    Returns:
        分页参数字典
    """
    if page < 1:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Page number must be greater than 0"
        )
    
    if size < 1 or size > 100:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Page size must be between 1 and 100"
        )
    
    offset = (page - 1) * size
    
    return {
        "page": page,
        "size": size,
        "offset": offset,
        "limit": size
    }


async def validate_json_body(
    request: Request,
    max_size: int = 1024 * 1024  # 1MB
) -> Dict[str, Any]:
    """
    验证JSON请求体
    
    Args:
        request: HTTP请求对象
        max_size: 最大请求体大小
        
    Returns:
        解析后的JSON数据
        
    Raises:
        HTTPException: JSON格式错误或过大
    """
    try:
        # 检查Content-Type
        content_type = request.headers.get("content-type", "")
        if not content_type.startswith("application/json"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Content-Type must be application/json"
            )
        
        # 读取请求体
        body = await request.body()
        
        # 检查大小
        if len(body) > max_size:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"Request body too large. Maximum size: {max_size} bytes"
            )
        
        # 解析JSON
        return json.loads(body)
        
    except json.JSONDecodeError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid JSON format"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"JSON validation error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid request format"
        )


class RequestLogging:
    """
    请求日志记录依赖
    """
    
    async def __call__(self, request: Request):
        """记录请求信息"""
        logger.info(f"API Request: {request.method} {request.url.path}")
        return True


# 创建请求日志实例
request_logging = RequestLogging()


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
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token",
            headers={"WWW-Authenticate": "Bearer"}
        )
    return user_id