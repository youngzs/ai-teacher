"""
AI教学助手系统 - AI分析API端点
处理AI代码分析、反馈生成、调试指导等功能

Author: AI Backend Architecture Expert
Date: 2025-09-10
Updated: Sprint 3 - 使用Repository模式重构
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from typing import List, Optional, Dict, Any
from datetime import datetime
import asyncio
import uuid

from ..database.database import get_db
from ..database.models import User, Submission, AIFeedback
from ..core.security import get_current_user_id, UserRole, check_rate_limit
from ..schemas.analysis import (
    AnalysisRequest, AnalysisResponse, FeedbackResponse,
    DebuggingRequest, DebuggingResponse, BatchAnalysisRequest
)
from ..schemas.common import ResponseModel, PaginatedResponse
from ..utils.logger import get_logger
from ..main import get_ai_service
from ..services.ai_service import AITeachingService
# Sprint 3: 导入Repository
from ..repositories import SubmissionRepository, AIFeedbackRepository, StudentProfileRepository

logger = get_logger(__name__)
router = APIRouter()


# Sprint 3: Repository依赖注入
def get_submission_repository(db: AsyncSession = Depends(get_db)) -> SubmissionRepository:
    """获取提交仓库实例"""
    return SubmissionRepository(db)


def get_feedback_repository(db: AsyncSession = Depends(get_db)) -> AIFeedbackRepository:
    """获取AI反馈仓库实例"""
    return AIFeedbackRepository(db)


def get_profile_repository(db: AsyncSession = Depends(get_db)) -> StudentProfileRepository:
    """获取学生画像仓库实例"""
    return StudentProfileRepository(db)


@router.post("/", response_model=ResponseModel[AnalysisResponse])
async def analyze_code(
    analysis_request: AnalysisRequest,
    background_tasks: BackgroundTasks,
    current_user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
    ai_service: AITeachingService = Depends(get_ai_service)
):
    """
    分析代码并生成AI反馈
    """
    # 速率限制检查
    if not check_rate_limit(f"analysis_{current_user_id}", 15):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many analysis requests. Please wait before trying again."
        )
    
    # 验证代码内容
    if not analysis_request.code.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Code cannot be empty"
        )
    
    try:
        # 创建提交记录（如果没有提供submission_id）
        submission_id = analysis_request.submission_id
        
        if not submission_id:
            submission = Submission(
                id=str(uuid.uuid4()),
                student_id=current_user_id,
                assignment_id=analysis_request.assignment_id or "analysis_request",
                assignment_description=analysis_request.assignment_description or "Direct analysis request",
                code=analysis_request.code,
                language=analysis_request.language,
                student_message=analysis_request.student_message,
                status="analyzing",
                submitted_at=datetime.utcnow()
            )
            
            db.add(submission)
            await db.commit()
            submission_id = submission.id
        else:
            # 验证提交是否存在且用户有权限
            submission_query = select(Submission).where(Submission.id == submission_id)
            submission_result = await db.execute(submission_query)
            submission = submission_result.scalar_one_or_none()
            
            if not submission:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Submission not found"
                )
            
            # 权限检查
            if submission.student_id != current_user_id:
                user_query = select(User).where(User.id == current_user_id)
                user_result = await db.execute(user_query)
                user = user_result.scalar_one_or_none()
                
                if not user or user.role not in [UserRole.TEACHER, UserRole.ADMIN]:
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail="Not authorized to analyze this submission"
                    )
        
        # 检查是否已有分析结果
        existing_feedback_query = select(AIFeedback).where(
            AIFeedback.submission_id == submission_id,
            AIFeedback.status == "completed"
        )
        existing_result = await db.execute(existing_feedback_query)
        existing_feedback = existing_result.scalar_one_or_none()
        
        if existing_feedback and not analysis_request.force_reanalyze:
            return ResponseModel(
                success=True,
                data=AnalysisResponse(
                    submission_id=submission_id,
                    analysis_id=existing_feedback.id,
                    status="completed",
                    overall_score=existing_feedback.overall_score,
                    analysis_result=existing_feedback.analysis_result,
                    created_at=existing_feedback.created_at,
                    processing_time=0.0
                ),
                message="Analysis result retrieved from cache"
            )
        
        # 执行AI分析
        start_time = datetime.utcnow()
        
        # 准备分析数据
        from src.models.teaching_models import SubmissionData, ProgrammingLanguage
        
        submission_data = SubmissionData(
            student_id=current_user_id,
            assignment_id=submission.assignment_id,
            assignment_description=submission.assignment_description,
            code=analysis_request.code,
            language=ProgrammingLanguage(analysis_request.language),
            submitted_at=submission.submitted_at,
            student_message=analysis_request.student_message
        )
        
        # 获取学生历史数据（用于个性化）
        student_history = await get_student_history(current_user_id, db)
        
        # 执行AI分析
        if analysis_request.analysis_type == "debugging":
            result = await ai_service.process_debugging_session(submission_data)
        elif analysis_request.analysis_type == "personalized":
            result = await ai_service.process_personalized_learning(submission_data, student_history)
        else:  # 默认为assignment分析
            result = await ai_service.process_submission(submission_data)
        
        end_time = datetime.utcnow()
        processing_time = (end_time - start_time).total_seconds()
        
        # 保存AI分析结果
        ai_feedback = AIFeedback(
            id=str(uuid.uuid4()),
            submission_id=submission_id,
            overall_score=result.overall_score,
            analysis_result=result.to_dict(),
            status="completed",
            created_at=end_time,
            processing_time=processing_time
        )
        
        db.add(ai_feedback)
        
        # 更新提交状态
        await db.execute(
            "UPDATE submissions SET status = 'analyzed', processed_at = :now WHERE id = :id",
            {"now": end_time, "id": submission_id}
        )
        
        await db.commit()
        
        logger.info(f"AI analysis completed for submission {submission_id} in {processing_time:.2f}s")
        
        return ResponseModel(
            success=True,
            data=AnalysisResponse(
                submission_id=submission_id,
                analysis_id=ai_feedback.id,
                status="completed",
                overall_score=result.overall_score,
                analysis_result=result.to_dict(),
                created_at=ai_feedback.created_at,
                processing_time=processing_time
            ),
            message="Code analysis completed successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"AI analysis failed for user {current_user_id}: {str(e)}")
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="AI analysis failed. Please try again."
        )


@router.get("/feedback/{submission_id}", response_model=ResponseModel[FeedbackResponse])
async def get_feedback(
    submission_id: str,
    current_user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
    submission_repo: SubmissionRepository = Depends(get_submission_repository),
    feedback_repo: AIFeedbackRepository = Depends(get_feedback_repository)
):
    """
    获取指定提交的AI反馈
    Sprint 3: 使用Repository模式
    """
    # Sprint 3: 使用Repository验证提交存在性
    submission = await submission_repo.get_by_id(submission_id)

    if not submission:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Submission not found"
        )

    # 权限检查
    if str(submission.student_id) != current_user_id:
        user_query = select(User).where(User.id == current_user_id)
        user_result = await db.execute(user_query)
        user = user_result.scalar_one_or_none()

        if not user or user.role not in [UserRole.TEACHER, UserRole.ADMIN]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to view this feedback"
            )

    # Sprint 3: 使用Repository获取AI反馈
    feedback = await feedback_repo.get_by_submission(submission_id)

    if not feedback:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No feedback available for this submission"
        )

    return ResponseModel(
        success=True,
        data=FeedbackResponse(
            feedback_id=str(feedback.id),
            submission_id=submission_id,
            overall_score=feedback.overall_score,
            analysis_result=feedback.analysis_result,
            status=feedback.status,
            created_at=feedback.created_at,
            processing_time=feedback.processing_time
        ),
        message="Feedback retrieved successfully"
    )


@router.post("/debug", response_model=ResponseModel[DebuggingResponse])
async def debug_code(
    debug_request: DebuggingRequest,
    current_user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
    ai_service: AITeachingService = Depends(get_ai_service)
):
    """
    调试代码并提供调试指导
    """
    # 速率限制检查
    if not check_rate_limit(f"debug_{current_user_id}", 10):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many debugging requests. Please wait before trying again."
        )
    
    try:
        start_time = datetime.utcnow()
        
        # 准备调试数据
        from src.models.teaching_models import SubmissionData, ProgrammingLanguage
        
        submission_data = SubmissionData(
            student_id=current_user_id,
            assignment_id="debug_session",
            assignment_description=debug_request.problem_description,
            code=debug_request.code,
            language=ProgrammingLanguage(debug_request.language),
            submitted_at=start_time,
            student_message=debug_request.specific_issue
        )
        
        # 执行调试分析
        result = await ai_service.process_debugging_session(submission_data)
        
        end_time = datetime.utcnow()
        processing_time = (end_time - start_time).total_seconds()
        
        logger.info(f"Debugging session completed for user {current_user_id} in {processing_time:.2f}s")
        
        return ResponseModel(
            success=True,
            data=DebuggingResponse(
                session_id=result.session_id,
                debugging_guidance=result.to_dict(),
                errors_found=len(result.code_analysis.get("critical_errors", [])),
                suggestions_count=len(result.feedback_content.get("reconstruction", {}).get("steps", [])),
                processing_time=processing_time,
                next_steps=result.next_steps
            ),
            message="Debugging guidance generated successfully"
        )
        
    except Exception as e:
        logger.error(f"Debugging failed for user {current_user_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Debugging analysis failed. Please try again."
        )


@router.post("/batch", response_model=ResponseModel[List[AnalysisResponse]])
async def batch_analyze(
    batch_request: BatchAnalysisRequest,
    background_tasks: BackgroundTasks,
    current_user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """
    批量分析代码（教师功能）
    """
    # 权限检查
    user_query = select(User).where(User.id == current_user_id)
    user_result = await db.execute(user_query)
    user = user_result.scalar_one_or_none()
    
    if not user or user.role not in [UserRole.TEACHER, UserRole.ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only teachers and admins can perform batch analysis"
        )
    
    if len(batch_request.submission_ids) > 20:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Maximum 20 submissions allowed per batch"
        )
    
    try:
        # 验证所有提交存在
        submission_query = select(Submission).where(
            Submission.id.in_(batch_request.submission_ids)
        )
        submission_result = await db.execute(submission_query)
        submissions = submission_result.scalars().all()
        
        if len(submissions) != len(batch_request.submission_ids):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Some submissions not found"
            )
        
        # 启动批量分析任务
        batch_id = str(uuid.uuid4())
        
        for submission in submissions:
            background_tasks.add_task(
                process_batch_analysis,
                submission.id,
                batch_id,
                batch_request.analysis_type
            )
        
        logger.info(f"Batch analysis started: {batch_id} with {len(submissions)} submissions")
        
        # 返回初始响应（分析正在进行中）
        response_data = [
            AnalysisResponse(
                submission_id=sub.id,
                analysis_id=f"batch_{batch_id}_{sub.id}",
                status="processing",
                overall_score=0.0,
                analysis_result={},
                created_at=datetime.utcnow(),
                processing_time=0.0
            )
            for sub in submissions
        ]
        
        return ResponseModel(
            success=True,
            data=response_data,
            message=f"Batch analysis started for {len(submissions)} submissions"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Batch analysis initiation failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to start batch analysis"
        )


@router.get("/history/{student_id}", response_model=ResponseModel[List[AnalysisResponse]])
async def get_student_analysis_history(
    student_id: str,
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=50),
    current_user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
    feedback_repo: AIFeedbackRepository = Depends(get_feedback_repository)
):
    """
    获取学生的分析历史记录
    Sprint 3: 使用Repository模式
    """
    # 权限检查：学生只能查看自己的历史，教师可以查看所有学生的历史
    if student_id != current_user_id:
        user_query = select(User).where(User.id == current_user_id)
        user_result = await db.execute(user_query)
        user = user_result.scalar_one_or_none()

        if not user or user.role not in [UserRole.TEACHER, UserRole.ADMIN]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to view this student's history"
            )

    try:
        # Sprint 3: 使用Repository获取学生的分析历史
        history = await feedback_repo.get_student_history(student_id, limit=page_size)

        response_data = [
            AnalysisResponse(
                submission_id=record.get("assignment_id", ""),
                analysis_id=record.get("feedback_id", ""),
                status="completed",
                overall_score=record.get("score", 0.0),
                analysis_result=record.get("analysis_summary", {}),
                created_at=datetime.fromisoformat(record["created_at"]) if record.get("created_at") else None,
                processing_time=record.get("processing_time", 0.0)
            )
            for record in history
        ]

        return ResponseModel(
            success=True,
            data=response_data,
            message="Analysis history retrieved successfully"
        )

    except Exception as e:
        logger.error(f"Failed to retrieve analysis history for student {student_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve analysis history"
        )


async def get_student_history(student_id: str, db: AsyncSession) -> List[Dict[str, Any]]:
    """
    获取学生的学习历史数据
    """
    try:
        query = """
        SELECT s.assignment_id, f.overall_score, s.language, s.submitted_at,
               f.analysis_result
        FROM submissions s
        LEFT JOIN ai_feedback f ON s.id = f.submission_id
        WHERE s.student_id = :student_id AND f.status = 'completed'
        ORDER BY s.submitted_at DESC
        LIMIT 20
        """
        
        result = await db.execute(query, {"student_id": student_id})
        records = result.fetchall()
        
        history = []
        for record in records:
            history.append({
                "assignment_id": record.assignment_id,
                "score": record.overall_score,
                "language": record.language,
                "submitted_at": record.submitted_at.isoformat() if record.submitted_at else None,
                "analysis_summary": {
                    "strengths": record.analysis_result.get("strengths", []) if record.analysis_result else [],
                    "weaknesses": record.analysis_result.get("critical_errors", []) if record.analysis_result else []
                }
            })
        
        return history
        
    except Exception as e:
        logger.error(f"Failed to get student history for {student_id}: {str(e)}")
        return []


async def process_batch_analysis(submission_id: str, batch_id: str, analysis_type: str):
    """
    处理批量分析的后台任务
    """
    try:
        from ..main import get_ai_service
        from ..database.database import SessionLocal
        
        ai_service = get_ai_service()
        
        async with SessionLocal() as db:
            # 获取提交信息
            submission_query = select(Submission).where(Submission.id == submission_id)
            submission_result = await db.execute(submission_query)
            submission = submission_result.scalar_one_or_none()
            
            if not submission:
                logger.error(f"Submission {submission_id} not found for batch analysis")
                return
            
            # 执行分析
            from src.models.teaching_models import SubmissionData, ProgrammingLanguage
            
            submission_data = SubmissionData(
                student_id=submission.student_id,
                assignment_id=submission.assignment_id,
                assignment_description=submission.assignment_description,
                code=submission.code,
                language=ProgrammingLanguage(submission.language),
                submitted_at=submission.submitted_at,
                student_message=submission.student_message
            )
            
            # 根据分析类型选择处理方法
            if analysis_type == "debugging":
                result = await ai_service.process_debugging_session(submission_data)
            else:
                result = await ai_service.process_submission(submission_data)
            
            # 保存结果
            ai_feedback = AIFeedback(
                id=str(uuid.uuid4()),
                submission_id=submission_id,
                overall_score=result.overall_score,
                analysis_result=result.to_dict(),
                status="completed",
                created_at=datetime.utcnow()
            )
            
            db.add(ai_feedback)
            await db.commit()
            
            logger.info(f"Batch analysis completed for submission {submission_id}")
            
    except Exception as e:
        logger.error(f"Batch analysis failed for submission {submission_id}: {str(e)}")


# 导入数据库会话
from ..database.database import SessionLocal