"""
AI教学助手系统 - 用户管理API端点
处理用户信息查询、更新、权限管理等功能

Author: AI Backend Architecture Expert
Date: 2025-09-10
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import List, Optional, Dict, Any
from datetime import datetime

from ..database.database import get_db
from ..database.models import User, Submission, AIFeedback
from ..core.security import get_current_user_id, UserRole, check_rate_limit
from ..schemas.auth import UserResponse, UserUpdate
from ..schemas.common import ResponseModel, PaginatedResponse
from ..utils.logger import get_logger

logger = get_logger(__name__)
router = APIRouter()


@router.get("/profile", response_model=ResponseModel[UserResponse])
async def get_user_profile(
    current_user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """获取当前用户详细信息"""
    try:
        # 获取用户基本信息
        user_query = select(User).where(User.id == current_user_id)
        user_result = await db.execute(user_query)
        user = user_result.scalar_one_or_none()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # 计算资料完整度
        profile_completeness = calculate_profile_completeness(user)
        
        return ResponseModel(
            success=True,
            data=UserResponse(
                id=user.id,
                username=user.username,
                email=user.email,
                full_name=user.full_name,
                role=UserRole(user.role),
                is_active=user.is_active,
                phone=user.profile_data.get("phone") if user.profile_data else None,
                organization=user.profile_data.get("organization") if user.profile_data else None,
                avatar_url=user.profile_data.get("avatar_url") if user.profile_data else None,
                created_at=user.created_at,
                last_login_at=user.last_login_at,
                profile_completeness=profile_completeness
            ),
            message="User profile retrieved successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get user profile for {current_user_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve user profile"
        )


@router.put("/profile", response_model=ResponseModel[UserResponse])
async def update_user_profile(
    user_update: UserUpdate,
    current_user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """更新用户信息"""
    try:
        # 获取用户信息
        user_query = select(User).where(User.id == current_user_id)
        user_result = await db.execute(user_query)
        user = user_result.scalar_one_or_none()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # 更新用户信息
        if user_update.full_name is not None:
            user.full_name = user_update.full_name
        
        # 更新扩展信息
        profile_data = user.profile_data or {}
        
        if user_update.phone is not None:
            profile_data["phone"] = user_update.phone
        
        if user_update.organization is not None:
            profile_data["organization"] = user_update.organization
        
        if user_update.avatar_url is not None:
            profile_data["avatar_url"] = user_update.avatar_url
        
        if user_update.preferences is not None:
            user.preferences = user_update.preferences
        
        user.profile_data = profile_data
        user.updated_at = datetime.utcnow()
        
        await db.commit()
        await db.refresh(user)
        
        # 计算更新后的资料完整度
        profile_completeness = calculate_profile_completeness(user)
        
        logger.info(f"User profile updated: {current_user_id}")
        
        return ResponseModel(
            success=True,
            data=UserResponse(
                id=user.id,
                username=user.username,
                email=user.email,
                full_name=user.full_name,
                role=UserRole(user.role),
                is_active=user.is_active,
                phone=user.profile_data.get("phone") if user.profile_data else None,
                organization=user.profile_data.get("organization") if user.profile_data else None,
                avatar_url=user.profile_data.get("avatar_url") if user.profile_data else None,
                created_at=user.created_at,
                last_login_at=user.last_login_at,
                profile_completeness=profile_completeness
            ),
            message="User profile updated successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update user profile for {current_user_id}: {str(e)}")
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update user profile"
        )


@router.get("/stats", response_model=ResponseModel[Dict[str, Any]])
async def get_user_stats(
    current_user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """获取用户统计信息"""
    try:
        # 获取用户角色
        user_query = select(User).where(User.id == current_user_id)
        user_result = await db.execute(user_query)
        user = user_result.scalar_one_or_none()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        stats = {}
        
        if user.role == UserRole.STUDENT:
            # 学生统计信息
            # 提交统计
            total_submissions = await db.scalar(
                select(func.count(Submission.id)).where(Submission.student_id == current_user_id)
            )
            
            # 平均分数
            avg_score_result = await db.execute(
                select(func.avg(AIFeedback.overall_score))
                .join(Submission, AIFeedback.submission_id == Submission.id)
                .where(Submission.student_id == current_user_id)
                .where(AIFeedback.status == "completed")
            )
            avg_score = avg_score_result.scalar() or 0.0
            
            # 按语言统计
            language_stats = await db.execute(
                select(Submission.language, func.count(Submission.id))
                .where(Submission.student_id == current_user_id)
                .group_by(Submission.language)
            )
            
            stats = {
                "role": "student",
                "total_submissions": total_submissions,
                "average_score": round(float(avg_score), 2),
                "submissions_by_language": {lang: count for lang, count in language_stats.fetchall()},
                "account_age_days": (datetime.utcnow() - user.created_at).days,
                "last_activity": user.last_login_at.isoformat() if user.last_login_at else None
            }
        
        elif user.role == UserRole.TEACHER:
            # 教师统计信息
            # 这里可以添加教师相关的统计，如班级数量、学生数量等
            stats = {
                "role": "teacher",
                "account_age_days": (datetime.utcnow() - user.created_at).days,
                "last_activity": user.last_login_at.isoformat() if user.last_login_at else None,
                "classes_count": 0,  # 需要实现班级功能后更新
                "students_count": 0   # 需要实现班级功能后更新
            }
        
        return ResponseModel(
            success=True,
            data=stats,
            message="User statistics retrieved successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get user stats for {current_user_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve user statistics"
        )


@router.get("/activity", response_model=ResponseModel[List[Dict[str, Any]]])
async def get_user_activity(
    days: int = Query(7, ge=1, le=30, description="获取最近几天的活动"),
    current_user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """获取用户活动记录"""
    try:
        # 计算日期范围
        end_date = datetime.utcnow()
        start_date = end_date.replace(hour=0, minute=0, second=0, microsecond=0)
        start_date = start_date - timedelta(days=days)
        
        # 获取提交活动
        submissions_query = select(
            Submission.id,
            Submission.assignment_description,
            Submission.language,
            Submission.submitted_at,
            AIFeedback.overall_score
        ).outerjoin(
            AIFeedback, Submission.id == AIFeedback.submission_id
        ).where(
            Submission.student_id == current_user_id,
            Submission.submitted_at >= start_date
        ).order_by(Submission.submitted_at.desc())
        
        submissions_result = await db.execute(submissions_query)
        submissions = submissions_result.fetchall()
        
        activities = []
        for sub in submissions:
            activities.append({
                "type": "submission",
                "id": sub.id,
                "title": f"提交了 {sub.language.upper()} 作业",
                "description": sub.assignment_description,
                "timestamp": sub.submitted_at.isoformat(),
                "score": float(sub.overall_score) if sub.overall_score else None,
                "language": sub.language
            })
        
        # 按时间排序
        activities.sort(key=lambda x: x["timestamp"], reverse=True)
        
        return ResponseModel(
            success=True,
            data=activities,
            message="User activity retrieved successfully"
        )
        
    except Exception as e:
        logger.error(f"Failed to get user activity for {current_user_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve user activity"
        )


@router.get("/preferences", response_model=ResponseModel[Dict[str, Any]])
async def get_user_preferences(
    current_user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """获取用户偏好设置"""
    try:
        user_query = select(User).where(User.id == current_user_id)
        user_result = await db.execute(user_query)
        user = user_result.scalar_one_or_none()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # 返回用户偏好设置，如果没有则返回默认设置
        preferences = user.preferences or {
            "theme": "light",
            "language": "zh-CN",
            "notifications": {
                "email": True,
                "push": True,
                "feedback": True
            },
            "code_editor": {
                "theme": "vs-code",
                "font_size": 14,
                "tab_size": 4,
                "auto_save": True
            },
            "learning": {
                "difficulty_preference": "adaptive",
                "feedback_detail": "detailed",
                "show_hints": True
            }
        }
        
        return ResponseModel(
            success=True,
            data=preferences,
            message="User preferences retrieved successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get user preferences for {current_user_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve user preferences"
        )


@router.put("/preferences", response_model=ResponseModel[Dict[str, Any]])
async def update_user_preferences(
    preferences: Dict[str, Any],
    current_user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """更新用户偏好设置"""
    try:
        user_query = select(User).where(User.id == current_user_id)
        user_result = await db.execute(user_query)
        user = user_result.scalar_one_or_none()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # 更新用户偏好设置
        user.preferences = preferences
        user.updated_at = datetime.utcnow()
        
        await db.commit()
        await db.refresh(user)
        
        logger.info(f"User preferences updated: {current_user_id}")
        
        return ResponseModel(
            success=True,
            data=user.preferences,
            message="User preferences updated successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update user preferences for {current_user_id}: {str(e)}")
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update user preferences"
        )


@router.delete("/account", response_model=ResponseModel[Dict[str, str]])
async def delete_user_account(
    current_user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """删除用户账户（软删除）"""
    try:
        user_query = select(User).where(User.id == current_user_id)
        user_result = await db.execute(user_query)
        user = user_result.scalar_one_or_none()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # 软删除：将用户设为非活跃状态
        user.is_active = False
        user.updated_at = datetime.utcnow()
        
        # 添加删除标记到profile_data
        profile_data = user.profile_data or {}
        profile_data["deleted_at"] = datetime.utcnow().isoformat()
        profile_data["deletion_reason"] = "user_requested"
        user.profile_data = profile_data
        
        await db.commit()
        
        logger.info(f"User account deactivated: {current_user_id}")
        
        return ResponseModel(
            success=True,
            data={"message": "Account has been deactivated"},
            message="Account deactivated successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete user account for {current_user_id}: {str(e)}")
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete user account"
        )


def calculate_profile_completeness(user: User) -> float:
    """计算用户资料完整度"""
    completeness = 0.0
    total_fields = 7
    
    # 检查基础字段
    if user.full_name:
        completeness += 1
    if user.email:
        completeness += 1
    if user.username:
        completeness += 1
    
    # 检查扩展字段
    if user.profile_data:
        if user.profile_data.get("phone"):
            completeness += 1
        if user.profile_data.get("organization"):
            completeness += 1
        if user.profile_data.get("avatar_url"):
            completeness += 1
    
    # 检查偏好设置
    if user.preferences:
        completeness += 1
    
    return round((completeness / total_fields) * 100, 1)


from datetime import timedelta