"""
AI教学助手系统 - 仪表板API端点
提供系统概览、统计数据、监控信息等功能

Author: AI Backend Architecture Expert
Date: 2025-09-10
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc, text
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta

from ..database.database import get_db
from ..database.models import User, Submission, AIFeedback, SystemMetrics
from ..core.security import get_current_user_id, UserRole, require_role
from ..schemas.common import ResponseModel
from ..utils.logger import get_logger
from ..main import get_ai_service

logger = get_logger(__name__)
router = APIRouter()


@router.get("/overview", response_model=ResponseModel[Dict[str, Any]])
async def get_dashboard_overview(
    current_user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """获取仪表板概览信息"""
    try:
        # 获取当前用户信息
        user_query = select(User).where(User.id == current_user_id)
        user_result = await db.execute(user_query)
        user = user_result.scalar_one_or_none()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        overview = {}
        
        if user.role == UserRole.STUDENT:
            # 学生仪表板概览
            overview = await _get_student_overview(current_user_id, db)
        elif user.role in [UserRole.TEACHER, UserRole.ADMIN]:
            # 教师/管理员仪表板概览
            overview = await _get_teacher_overview(current_user_id, db)
        
        return ResponseModel(
            success=True,
            data=overview,
            message="Dashboard overview retrieved successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get dashboard overview for {current_user_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve dashboard overview"
        )


@router.get("/recent-activity", response_model=ResponseModel[List[Dict[str, Any]]])
async def get_recent_activity(
    limit: int = Query(10, ge=1, le=50, description="返回记录数量"),
    current_user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """获取最近活动"""
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
        
        activities = []
        
        if user.role == UserRole.STUDENT:
            # 学生的最近活动
            submissions_query = select(
                Submission.id,
                Submission.assignment_description,
                Submission.language,
                Submission.status,
                Submission.submitted_at,
                AIFeedback.overall_score
            ).outerjoin(
                AIFeedback, Submission.id == AIFeedback.submission_id
            ).where(
                Submission.student_id == current_user_id
            ).order_by(desc(Submission.submitted_at)).limit(limit)
            
            submissions_result = await db.execute(submissions_query)
            submissions = submissions_result.fetchall()
            
            for sub in submissions:
                activities.append({
                    "type": "submission",
                    "id": sub.id,
                    "title": f"提交了作业: {sub.assignment_description[:50]}...",
                    "status": sub.status,
                    "language": sub.language,
                    "score": float(sub.overall_score) if sub.overall_score else None,
                    "timestamp": sub.submitted_at.isoformat()
                })
        
        elif user.role in [UserRole.TEACHER, UserRole.ADMIN]:
            # 教师/管理员的最近活动（系统级别）
            recent_submissions = select(
                Submission.id,
                Submission.assignment_description,
                Submission.language,
                Submission.status,
                Submission.submitted_at,
                User.full_name.label('student_name')
            ).join(
                User, Submission.student_id == User.id
            ).order_by(desc(Submission.submitted_at)).limit(limit)
            
            result = await db.execute(recent_submissions)
            submissions = result.fetchall()
            
            for sub in submissions:
                activities.append({
                    "type": "student_submission",
                    "id": sub.id,
                    "title": f"{sub.student_name} 提交了作业",
                    "description": sub.assignment_description[:50] + "...",
                    "status": sub.status,
                    "language": sub.language,
                    "timestamp": sub.submitted_at.isoformat()
                })
        
        return ResponseModel(
            success=True,
            data=activities,
            message="Recent activity retrieved successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get recent activity for {current_user_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve recent activity"
        )


@router.get("/analytics", response_model=ResponseModel[Dict[str, Any]])
async def get_analytics(
    period: str = Query("7d", regex="^(24h|7d|30d|90d)$", description="分析周期"),
    current_user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """获取分析数据"""
    try:
        # 计算时间范围
        now = datetime.utcnow()
        if period == "24h":
            start_time = now - timedelta(hours=24)
        elif period == "7d":
            start_time = now - timedelta(days=7)
        elif period == "30d":
            start_time = now - timedelta(days=30)
        else:  # 90d
            start_time = now - timedelta(days=90)
        
        # 获取用户角色
        user_query = select(User).where(User.id == current_user_id)
        user_result = await db.execute(user_query)
        user = user_result.scalar_one_or_none()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        analytics = {}
        
        if user.role == UserRole.STUDENT:
            # 学生分析数据
            analytics = await _get_student_analytics(current_user_id, start_time, db)
        elif user.role in [UserRole.TEACHER, UserRole.ADMIN]:
            # 教师/管理员分析数据
            analytics = await _get_system_analytics(start_time, db)
        
        analytics["period"] = period
        analytics["start_time"] = start_time.isoformat()
        analytics["end_time"] = now.isoformat()
        
        return ResponseModel(
            success=True,
            data=analytics,
            message="Analytics data retrieved successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get analytics for {current_user_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve analytics data"
        )


@router.get("/system-health", response_model=ResponseModel[Dict[str, Any]])
@require_role(UserRole.ADMIN)
async def get_system_health(
    current_user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
    ai_service = Depends(get_ai_service)
):
    """获取系统健康状态（仅管理员）"""
    try:
        # 数据库健康检查
        db_health = await _check_database_health(db)
        
        # AI服务健康检查
        ai_health = await ai_service.health_check()
        
        # 系统指标
        system_metrics = await _get_system_metrics(db)
        
        health_data = {
            "overall_status": "healthy" if db_health["status"] == "healthy" and ai_health else "unhealthy",
            "database": db_health,
            "ai_service": {
                "status": "healthy" if ai_health else "unhealthy",
                "initialized": ai_service.is_initialized
            },
            "system_metrics": system_metrics,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        return ResponseModel(
            success=True,
            data=health_data,
            message="System health retrieved successfully"
        )
        
    except Exception as e:
        logger.error(f"Failed to get system health: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve system health"
        )


# 私有辅助函数

async def _get_student_overview(user_id: str, db: AsyncSession) -> Dict[str, Any]:
    """获取学生概览数据"""
    # 总提交数
    total_submissions = await db.scalar(
        select(func.count(Submission.id)).where(Submission.student_id == user_id)
    )
    
    # 平均分数
    avg_score_result = await db.execute(
        select(func.avg(AIFeedback.overall_score))
        .join(Submission, AIFeedback.submission_id == Submission.id)
        .where(Submission.student_id == user_id)
        .where(AIFeedback.status == "completed")
    )
    avg_score = avg_score_result.scalar() or 0.0
    
    # 最近7天的提交
    week_ago = datetime.utcnow() - timedelta(days=7)
    recent_submissions = await db.scalar(
        select(func.count(Submission.id))
        .where(Submission.student_id == user_id)
        .where(Submission.submitted_at >= week_ago)
    )
    
    # 最高分数
    best_score_result = await db.execute(
        select(func.max(AIFeedback.overall_score))
        .join(Submission, AIFeedback.submission_id == Submission.id)
        .where(Submission.student_id == user_id)
        .where(AIFeedback.status == "completed")
    )
    best_score = best_score_result.scalar() or 0.0
    
    # 编程语言统计
    language_stats = await db.execute(
        select(Submission.language, func.count(Submission.id))
        .where(Submission.student_id == user_id)
        .group_by(Submission.language)
    )
    
    return {
        "user_type": "student",
        "total_submissions": total_submissions or 0,
        "average_score": round(float(avg_score), 2),
        "best_score": round(float(best_score), 2),
        "recent_submissions": recent_submissions or 0,
        "languages": {lang: count for lang, count in language_stats.fetchall()},
        "improvement_trend": await _calculate_improvement_trend(user_id, db)
    }


async def _get_teacher_overview(user_id: str, db: AsyncSession) -> Dict[str, Any]:
    """获取教师概览数据"""
    # 系统总览统计
    total_students = await db.scalar(
        select(func.count(User.id)).where(User.role == UserRole.STUDENT.value)
    )
    
    total_submissions = await db.scalar(
        select(func.count(Submission.id))
    )
    
    # 今天的活动
    today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    today_submissions = await db.scalar(
        select(func.count(Submission.id))
        .where(Submission.submitted_at >= today)
    )
    
    # 等待处理的提交
    pending_analysis = await db.scalar(
        select(func.count(Submission.id))
        .where(Submission.status.in_(["submitted", "analyzing"]))
    )
    
    # 平均系统分数
    avg_system_score = await db.scalar(
        select(func.avg(AIFeedback.overall_score))
        .where(AIFeedback.status == "completed")
    ) or 0.0
    
    return {
        "user_type": "teacher",
        "total_students": total_students or 0,
        "total_submissions": total_submissions or 0,
        "today_submissions": today_submissions or 0,
        "pending_analysis": pending_analysis or 0,
        "average_system_score": round(float(avg_system_score), 2),
        "system_load": await _calculate_system_load(db)
    }


async def _get_student_analytics(user_id: str, start_time: datetime, db: AsyncSession) -> Dict[str, Any]:
    """获取学生分析数据"""
    # 时间趋势数据
    daily_stats = await db.execute(
        text("""
        SELECT 
            DATE(submitted_at) as date,
            COUNT(*) as submissions,
            AVG(af.overall_score) as avg_score
        FROM submissions s
        LEFT JOIN ai_feedback af ON s.id = af.submission_id
        WHERE s.student_id = :user_id 
        AND s.submitted_at >= :start_time
        GROUP BY DATE(submitted_at)
        ORDER BY date
        """),
        {"user_id": user_id, "start_time": start_time}
    )
    
    daily_data = []
    for row in daily_stats.fetchall():
        daily_data.append({
            "date": row.date.isoformat() if row.date else None,
            "submissions": row.submissions,
            "average_score": round(float(row.avg_score or 0), 2)
        })
    
    # 语言偏好趋势
    language_trend = await db.execute(
        select(Submission.language, func.count(Submission.id))
        .where(Submission.student_id == user_id)
        .where(Submission.submitted_at >= start_time)
        .group_by(Submission.language)
    )
    
    return {
        "daily_progress": daily_data,
        "language_usage": {lang: count for lang, count in language_trend.fetchall()},
        "total_period_submissions": len(daily_data),
        "improvement_rate": await _calculate_improvement_rate(user_id, start_time, db)
    }


async def _get_system_analytics(start_time: datetime, db: AsyncSession) -> Dict[str, Any]:
    """获取系统分析数据"""
    # 系统范围的统计
    total_users = await db.scalar(
        select(func.count(User.id)).where(User.created_at >= start_time)
    )
    
    total_submissions = await db.scalar(
        select(func.count(Submission.id)).where(Submission.submitted_at >= start_time)
    )
    
    successful_analyses = await db.scalar(
        select(func.count(AIFeedback.id))
        .where(AIFeedback.status == "completed")
        .where(AIFeedback.created_at >= start_time)
    )
    
    # 语言使用统计
    language_stats = await db.execute(
        select(Submission.language, func.count(Submission.id))
        .where(Submission.submitted_at >= start_time)
        .group_by(Submission.language)
    )
    
    # 平均处理时间
    avg_processing_time = await db.scalar(
        select(func.avg(AIFeedback.processing_time))
        .where(AIFeedback.status == "completed")
        .where(AIFeedback.created_at >= start_time)
    ) or 0.0
    
    return {
        "new_users": total_users or 0,
        "total_submissions": total_submissions or 0,
        "successful_analyses": successful_analyses or 0,
        "success_rate": round((successful_analyses / total_submissions * 100) if total_submissions else 0, 2),
        "language_distribution": {lang: count for lang, count in language_stats.fetchall()},
        "average_processing_time": round(float(avg_processing_time), 2)
    }


async def _calculate_improvement_trend(user_id: str, db: AsyncSession) -> str:
    """计算改进趋势"""
    # 获取最近10次提交的分数
    recent_scores = await db.execute(
        select(AIFeedback.overall_score)
        .join(Submission, AIFeedback.submission_id == Submission.id)
        .where(Submission.student_id == user_id)
        .where(AIFeedback.status == "completed")
        .order_by(desc(Submission.submitted_at))
        .limit(10)
    )
    
    scores = [float(score[0]) for score in recent_scores.fetchall()]
    
    if len(scores) < 3:
        return "insufficient_data"
    
    # 简单的趋势计算
    first_half = scores[:len(scores)//2]
    second_half = scores[len(scores)//2:]
    
    if sum(second_half) > sum(first_half):
        return "improving"
    elif sum(second_half) < sum(first_half):
        return "declining"
    else:
        return "stable"


async def _calculate_improvement_rate(user_id: str, start_time: datetime, db: AsyncSession) -> float:
    """计算改进率"""
    scores = await db.execute(
        select(AIFeedback.overall_score)
        .join(Submission, AIFeedback.submission_id == Submission.id)
        .where(Submission.student_id == user_id)
        .where(AIFeedback.status == "completed")
        .where(Submission.submitted_at >= start_time)
        .order_by(Submission.submitted_at)
    )
    
    score_list = [float(score[0]) for score in scores.fetchall()]
    
    if len(score_list) < 2:
        return 0.0
    
    return round(((score_list[-1] - score_list[0]) / score_list[0]) * 100, 2) if score_list[0] > 0 else 0.0


async def _calculate_system_load(db: AsyncSession) -> Dict[str, Any]:
    """计算系统负载"""
    pending_count = await db.scalar(
        select(func.count(Submission.id))
        .where(Submission.status.in_(["submitted", "analyzing"]))
    )
    
    return {
        "pending_analyses": pending_count or 0,
        "load_level": "high" if (pending_count or 0) > 50 else "medium" if (pending_count or 0) > 10 else "low"
    }


async def _check_database_health(db: AsyncSession) -> Dict[str, Any]:
    """检查数据库健康状态"""
    try:
        start_time = datetime.utcnow()
        
        # 执行简单查询测试
        result = await db.execute(text("SELECT 1"))
        result.scalar()
        
        response_time = (datetime.utcnow() - start_time).total_seconds() * 1000
        
        return {
            "status": "healthy",
            "response_time_ms": round(response_time, 2)
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e)
        }


async def _get_system_metrics(db: AsyncSession) -> Dict[str, Any]:
    """获取系统指标"""
    # 这里可以添加更详细的系统指标收集
    # 目前返回基础指标
    return {
        "cpu_usage": 0.0,  # 需要实现
        "memory_usage": 0.0,  # 需要实现
        "disk_usage": 0.0,  # 需要实现
        "active_connections": 0  # 需要实现
    }