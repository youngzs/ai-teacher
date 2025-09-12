"""
AI教学助手系统 - 认证API端点
处理用户登录、注册、令牌刷新等认证相关功能

Author: AI Backend Architecture Expert
Date: 2025-09-10
"""

from fastapi import APIRouter, Depends, HTTPException, status, Form, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Dict, Any
import re
from datetime import datetime, timedelta

from ..database.database import get_db
from ..database.models import User
from ..core.security import (
    create_access_token, create_refresh_token, verify_password, 
    create_password_hash, verify_token,
    UserRole, check_rate_limit
)
from ..core.dependencies import get_current_active_user, rate_limit_check
from ..core.config import settings
from ..schemas.auth import (
    UserRegister, UserLogin, TokenResponse, UserResponse,
    PasswordReset, PasswordResetConfirm
)
from ..schemas.common import ResponseModel
from ..utils.email import send_password_reset_email
from ..utils.logger import get_logger

logger = get_logger(__name__)
router = APIRouter()


def validate_email(email: str) -> bool:
    """验证邮箱格式"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def validate_password(password: str) -> tuple[bool, str]:
    """
    验证密码强度
    
    Returns:
        (is_valid, error_message)
    """
    if len(password) < 8:
        return False, "密码长度至少8位"
    
    if not re.search(r'[A-Za-z]', password):
        return False, "密码必须包含字母"
    
    if not re.search(r'[0-9]', password):
        return False, "密码必须包含数字"
    
    return True, ""


@router.post("/register", response_model=ResponseModel[UserResponse])
async def register(
    user_data: UserRegister,
    request: Request,
    db: AsyncSession = Depends(get_db),
    _: bool = Depends(rate_limit_check)
):
    """
    用户注册
    """
    # 检查是否允许注册
    if not settings.ENABLE_SIGNUP:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Registration is currently disabled"
        )
    
    # 验证邮箱格式
    if not validate_email(user_data.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid email format"
        )
    
    # 验证密码强度
    is_valid, error_message = validate_password(user_data.password)
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_message
        )
    
    # 检查邮箱是否已存在
    existing_user_result = await db.execute(
        select(User).where(User.email == user_data.email)
    )
    if existing_user_result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # 检查用户名是否已存在
    existing_username_result = await db.execute(
        select(User).where(User.username == user_data.username)
    )
    if existing_username_result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already taken"
        )
    
    try:
        # 创建新用户
        hashed_password = create_password_hash(user_data.password)
        
        new_user = User(
            username=user_data.username,
            email=user_data.email,
            hashed_password=hashed_password,
            full_name=user_data.full_name,
            role=user_data.role.value if user_data.role else "student",
            is_active=True
        )
        
        db.add(new_user)
        await db.commit()
        await db.refresh(new_user)
        
        logger.info(f"New user registered: {user_data.email}")
        
        return ResponseModel(
            success=True,
            data=UserResponse(
                id=str(new_user.id),
                username=new_user.username,
                email=new_user.email,
                full_name=new_user.full_name,
                role=new_user.role,
                is_active=new_user.is_active,
                created_at=new_user.created_at
            ),
            message="User registered successfully"
        )
        
    except Exception as e:
        logger.error(f"Registration failed for {user_data.email}: {str(e)}")
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration failed. Please try again."
        )


@router.post("/login", response_model=ResponseModel[TokenResponse])
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db),
    _: bool = Depends(rate_limit_check)
):
    """
    用户登录
    """
    # 查找用户（支持邮箱或用户名登录）
    user_result = await db.execute(
        select(User).where(
            (User.email == form_data.username) | (User.username == form_data.username),
            User.is_active == True
        )
    )
    
    user = user_result.scalar_one_or_none()
    
    if not user or not verify_password(form_data.password, user.hashed_password):
        logger.warning(f"Failed login attempt for: {form_data.username}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email/username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    try:
        # 更新最后登录时间
        user.last_login_at = datetime.utcnow()
        await db.commit()
        
        # 创建访问令牌和刷新令牌
        access_token = create_access_token(
            subject=str(user.id),
            additional_claims={
                "role": user.role,
                "username": user.username
            }
        )
        refresh_token = create_refresh_token(subject=str(user.id))
        
        logger.info(f"User logged in: {user.email}")
        
        return ResponseModel(
            success=True,
            data=TokenResponse(
                access_token=access_token,
                refresh_token=refresh_token,
                token_type="bearer",
                expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
                user=UserResponse(
                    id=str(user.id),
                    username=user.username,
                    email=user.email,
                    full_name=user.full_name,
                    role=user.role,
                    is_active=user.is_active,
                    created_at=user.created_at,
                    last_login_at=user.last_login_at
                )
            ),
            message="Login successful"
        )
        
    except Exception as e:
        logger.error(f"Login process failed for {user.email}: {str(e)}")
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Login failed. Please try again."
        )


@router.post("/refresh", response_model=ResponseModel[TokenResponse])
async def refresh_token(
    refresh_token: str = Form(...),
    db: AsyncSession = Depends(get_db)
):
    """
    刷新访问令牌
    """
    try:
        # 验证刷新令牌
        payload = verify_token(refresh_token, token_type="refresh")
        user_id = payload.get("sub")
        
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )
        
        # 查找用户
        user_query = await db.execute(
            """
            SELECT id, username, email, full_name, role, is_active 
            FROM users 
            WHERE id = :user_id AND is_active = true
            """,
            {"user_id": user_id}
        )
        
        user = user_query.first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found or inactive"
            )
        
        # 创建新的访问令牌
        new_access_token = create_access_token(
            subject=user.id,
            additional_claims={
                "role": user.role,
                "username": user.username
            }
        )
        
        return ResponseModel(
            success=True,
            data=TokenResponse(
                access_token=new_access_token,
                refresh_token=refresh_token,  # 刷新令牌保持不变
                token_type="bearer",
                expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
                user=UserResponse(
                    id=user.id,
                    username=user.username,
                    email=user.email,
                    full_name=user.full_name,
                    role=user.role,
                    is_active=user.is_active
                )
            ),
            message="Token refreshed successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Token refresh failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Token refresh failed"
        )


@router.post("/logout", response_model=ResponseModel[Dict[str, str]])
async def logout(
    current_user: User = Depends(get_current_active_user)
):
    """
    用户登出
    """
    # 在实际应用中，这里可以将令牌加入黑名单
    # 目前只是简单的成功响应
    
    logger.info(f"User logged out: {current_user.id}")
    
    return ResponseModel(
        success=True,
        data={"message": "Successfully logged out"},
        message="Logout successful"
    )


@router.post("/password-reset", response_model=ResponseModel[Dict[str, str]])
async def request_password_reset(
    reset_data: PasswordReset,
    db: AsyncSession = Depends(get_db)
):
    """
    请求密码重置
    """
    # 速率限制
    if not check_rate_limit(f"reset_{reset_data.email}", 3):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many reset requests. Please try again later."
        )
    
    # 查找用户
    user_query = await db.execute(
        "SELECT id, email, full_name FROM users WHERE email = :email AND is_active = true",
        {"email": reset_data.email}
    )
    
    user = user_query.first()
    
    # 无论用户是否存在都返回成功（安全考虑）
    if user:
        try:
            # 生成重置令牌
            reset_token = create_access_token(
                subject=user.id,
                expires_delta=timedelta(hours=1),  # 1小时过期
                additional_claims={"type": "password_reset"}
            )
            
            # 发送重置邮件
            await send_password_reset_email(
                email=user.email,
                name=user.full_name,
                reset_token=reset_token
            )
            
            logger.info(f"Password reset requested for: {user.email}")
            
        except Exception as e:
            logger.error(f"Password reset email failed for {user.email}: {str(e)}")
    
    return ResponseModel(
        success=True,
        data={"message": "Password reset instructions sent"},
        message="If the email exists, reset instructions have been sent"
    )


@router.post("/password-reset/confirm", response_model=ResponseModel[Dict[str, str]])
async def confirm_password_reset(
    reset_data: PasswordResetConfirm,
    db: AsyncSession = Depends(get_db)
):
    """
    确认密码重置
    """
    try:
        # 验证重置令牌
        payload = verify_token(reset_data.token)
        
        # 检查令牌类型
        if payload.get("type") != "password_reset":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid reset token"
            )
        
        user_id = payload.get("sub")
        
        # 验证新密码
        is_valid, error_message = validate_password(reset_data.new_password)
        if not is_valid:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=error_message
            )
        
        # 更新密码
        hashed_password = create_password_hash(reset_data.new_password)
        
        result = await db.execute(
            "UPDATE users SET hashed_password = :password WHERE id = :user_id",
            {"password": hashed_password, "user_id": user_id}
        )
        
        if result.rowcount == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User not found"
            )
        
        await db.commit()
        
        logger.info(f"Password reset completed for user: {user_id}")
        
        return ResponseModel(
            success=True,
            data={"message": "Password reset successful"},
            message="Password has been reset successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Password reset confirmation failed: {str(e)}")
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Password reset failed"
        )


@router.get("/me", response_model=ResponseModel[UserResponse])
async def get_current_user_info(
    current_user: User = Depends(get_current_active_user)
):
    """
    获取当前用户信息
    """
    return ResponseModel(
        success=True,
        data=UserResponse(
            id=str(current_user.id),
            username=current_user.username,
            email=current_user.email,
            full_name=current_user.full_name,
            role=current_user.role,
            is_active=current_user.is_active,
            created_at=current_user.created_at,
            last_login_at=current_user.last_login_at
        ),
        message="User information retrieved successfully"
    )