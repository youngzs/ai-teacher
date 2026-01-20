"""
AI教学助手系统 - 代码提交API端点
处理学生代码提交、获取提交历史、批量处理等功能

Author: AI Backend Architecture Expert
Date: 2025-09-10
Updated: Sprint 3 - 使用Repository模式重构
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query, BackgroundTasks, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc, func, and_
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import asyncio
import uuid

from ..database.database import get_db
from ..database.models import User, Submission, AIFeedback, Assignment
from ..core.dependencies import (
    get_current_active_user, require_teacher_or_admin,
    get_pagination_params, check_ownership_or_teacher, rate_limit_check,
    get_current_user_id
)
from ..schemas.submissions import (
    SubmissionCreate, SubmissionResponse, SubmissionListResponse,
    SubmissionUpdate, BatchSubmissionRequest
)
from ..schemas.common import ResponseModel, PaginatedResponse
from ..utils.logger import get_logger
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


@router.post("/", response_model=ResponseModel[SubmissionResponse])
async def create_submission(
    submission_data: SubmissionCreate,
    background_tasks: BackgroundTasks,
    request: Request,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
    submission_repo: SubmissionRepository = Depends(get_submission_repository),
    _: bool = Depends(rate_limit_check)
):
    """
    创建新的代码提交
    Sprint 3: 使用Repository模式
    """
    # 验证代码内容
    if not submission_data.code.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Code cannot be empty"
        )

    # 代码长度限制
    if len(submission_data.code) > 50000:  # 50KB限制
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="Code is too long. Maximum 50KB allowed."
        )

    # 如果指定了作业ID，验证作业存在且学生有权限访问
    if submission_data.assignment_id:
        assignment_result = await db.execute(
            select(Assignment).where(Assignment.id == submission_data.assignment_id)
        )
        assignment = assignment_result.scalar_one_or_none()

        if not assignment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Assignment not found"
            )

        # 检查学生是否在班级中
        from ..database.models import ClassMembership
        membership_result = await db.execute(
            select(ClassMembership).where(
                and_(
                    ClassMembership.class_id == assignment.class_id,
                    ClassMembership.student_id == current_user.id,
                    ClassMembership.is_active == True
                )
            )
        )
        if not membership_result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to this assignment"
            )

    try:
        # Sprint 3: 使用Repository创建提交记录
        submission = await submission_repo.create(
            student_id=str(current_user.id),
            code=submission_data.code,
            language=submission_data.language.value,
            assignment_description=submission_data.assignment_description,
            assignment_id=submission_data.assignment_id,
            student_message=submission_data.student_message
        )

        # 异步处理AI分析
        background_tasks.add_task(
            process_ai_analysis,
            str(submission.id),
            str(current_user.id),
            submission_data.dict()
        )

        logger.info(f"New submission created: {submission.id} by user {current_user.username}")

        return ResponseModel(
            success=True,
            data=SubmissionResponse(
                id=str(submission.id),
                student_id=str(submission.student_id),
                assignment_id=submission_data.assignment_id,
                assignment_description=submission.assignment_description,
                code=submission.code,
                language=submission.language,
                student_message=submission.student_message,
                status=submission.status,
                submitted_at=submission.submitted_at,
                ai_analysis_status="pending"
            ),
            message="Code submitted successfully. AI analysis in progress."
        )

    except Exception as e:
        logger.error(f"Submission creation failed for user {current_user.username}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create submission"
        )


@router.get("/{submission_id}", response_model=ResponseModel[SubmissionResponse])
async def get_submission(
    submission_id: str,
    current_user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
    submission_repo: SubmissionRepository = Depends(get_submission_repository),
    feedback_repo: AIFeedbackRepository = Depends(get_feedback_repository)
):
    """
    获取指定提交的详细信息
    Sprint 3: 使用Repository模式
    """
    # Sprint 3: 使用Repository获取提交
    submission = await submission_repo.get_by_id(submission_id, include_feedback=False)

    if not submission:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Submission not found"
        )

    # 权限检查：学生只能查看自己的提交，教师可以查看所有提交
    if str(submission.student_id) != current_user_id:
        # 检查用户是否是教师
        user_query = select(User).where(User.id == current_user_id)
        user_result = await db.execute(user_query)
        user = user_result.scalar_one_or_none()

        if not user or user.role not in ["teacher", "admin"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to view this submission"
            )

    # Sprint 3: 使用Repository获取AI反馈状态
    feedback = await feedback_repo.get_by_submission(submission_id)

    ai_analysis_status = "pending"
    if feedback:
        if feedback.status == "completed":
            ai_analysis_status = "completed"
        elif feedback.status == "failed":
            ai_analysis_status = "failed"
        else:
            ai_analysis_status = "processing"

    return ResponseModel(
        success=True,
        data=SubmissionResponse(
            id=str(submission.id),
            student_id=str(submission.student_id),
            assignment_id=str(submission.assignment_id) if submission.assignment_id else None,
            assignment_description=submission.assignment_description,
            code=submission.code,
            language=submission.language,
            student_message=submission.student_message,
            status=submission.status,
            submitted_at=submission.submitted_at,
            processed_at=submission.processed_at,
            ai_analysis_status=ai_analysis_status
        ),
        message="Submission retrieved successfully"
    )


@router.get("/", response_model=ResponseModel[PaginatedResponse[SubmissionListResponse]])
async def list_submissions(
    current_user: User = Depends(get_current_active_user),
    pagination: Dict[str, Any] = Depends(get_pagination_params),
    assignment_id: Optional[str] = Query(None, description="作业ID筛选"),
    language: Optional[str] = Query(None, description="编程语言筛选"),
    submission_status: Optional[str] = Query(None, alias="status", description="状态筛选"),
    db: AsyncSession = Depends(get_db),
    submission_repo: SubmissionRepository = Depends(get_submission_repository),
    feedback_repo: AIFeedbackRepository = Depends(get_feedback_repository)
):
    """
    获取提交列表（分页）
    Sprint 3: 使用Repository模式
    """
    try:
        # 构建查询条件
        conditions = []

        # 学生只能看自己的提交，教师和管理员可以看所有提交
        if current_user.role == "student":
            conditions.append(Submission.student_id == current_user.id)

        # 添加筛选条件
        if assignment_id:
            conditions.append(Submission.assignment_id == assignment_id)
        if language:
            conditions.append(Submission.language == language)
        if submission_status:
            conditions.append(Submission.status == submission_status)

        # 计算总数
        count_query = select(func.count(Submission.id)).where(and_(*conditions)) if conditions else select(func.count(Submission.id))
        total_result = await db.execute(count_query)
        total_count = total_result.scalar()

        # 获取分页数据
        query = (
            select(Submission)
            .where(and_(*conditions)) if conditions else select(Submission)
        )
        query = (
            query
            .order_by(desc(Submission.submitted_at))
            .offset(pagination["offset"])
            .limit(pagination["limit"])
        )

        result = await db.execute(query)
        submissions = result.scalars().all()

        # 构建响应数据
        submission_list = []
        for submission in submissions:
            # Sprint 3: 使用Repository获取AI反馈状态
            feedback = await feedback_repo.get_by_submission(str(submission.id))

            ai_status = "pending"
            if feedback:
                if feedback.status == "completed":
                    ai_status = "completed"
                elif feedback.status == "failed":
                    ai_status = "failed"
                else:
                    ai_status = "processing"

            submission_list.append(
                SubmissionListResponse(
                    id=str(submission.id),
                    assignment_id=str(submission.assignment_id) if submission.assignment_id else None,
                    assignment_description=submission.assignment_description,
                    language=submission.language,
                    status=submission.status,
                    submitted_at=submission.submitted_at,
                    ai_analysis_status=ai_status,
                    code_preview=submission.code[:200] + "..." if len(submission.code) > 200 else submission.code
                )
            )

        return ResponseModel(
            success=True,
            data=PaginatedResponse(
                items=submission_list,
                total=total_count,
                page=pagination["page"],
                size=pagination["size"],
                pages=(total_count + pagination["size"] - 1) // pagination["size"]
            ),
            message="Submissions retrieved successfully"
        )

    except Exception as e:
        logger.error(f"Error retrieving submissions: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve submissions"
        )


@router.put("/{submission_id}", response_model=ResponseModel[SubmissionResponse])
async def update_submission(
    submission_id: str,
    update_data: SubmissionUpdate,
    current_user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """
    更新提交信息（仅学生本人或教师可操作）
    """
    query = select(Submission).where(Submission.id == submission_id)
    result = await db.execute(query)
    submission = result.scalar_one_or_none()
    
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
                detail="Not authorized to update this submission"
            )
    
    try:
        # 更新字段
        if update_data.code is not None:
            submission.code = update_data.code
        if update_data.student_message is not None:
            submission.student_message = update_data.student_message
        if update_data.status is not None:
            submission.status = update_data.status
        
        submission.updated_at = datetime.utcnow()
        
        await db.commit()
        await db.refresh(submission)
        
        logger.info(f"Submission updated: {submission_id} by user {current_user_id}")
        
        return ResponseModel(
            success=True,
            data=SubmissionResponse(
                id=submission.id,
                student_id=submission.student_id,
                assignment_id=submission.assignment_id,
                assignment_description=submission.assignment_description,
                code=submission.code,
                language=submission.language,
                student_message=submission.student_message,
                status=submission.status,
                submitted_at=submission.submitted_at,
                processed_at=submission.processed_at
            ),
            message="Submission updated successfully"
        )
        
    except Exception as e:
        logger.error(f"Submission update failed: {str(e)}")
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update submission"
        )


@router.delete("/{submission_id}", response_model=ResponseModel[Dict[str, str]])
async def delete_submission(
    submission_id: str,
    current_user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
    submission_repo: SubmissionRepository = Depends(get_submission_repository)
):
    """
    删除提交（仅学生本人或管理员可操作）
    Sprint 3: 使用Repository模式
    """
    # Sprint 3: 使用Repository获取提交
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

        if not user or user.role != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to delete this submission"
            )

    try:
        # Sprint 3: 使用Repository删除提交（级联删除AI反馈）
        deleted = await submission_repo.delete(submission_id)

        if deleted:
            logger.info(f"Submission deleted: {submission_id} by user {current_user_id}")
            return ResponseModel(
                success=True,
                data={"message": "Submission deleted successfully"},
                message="Submission deleted successfully"
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to delete submission"
            )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Submission deletion failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete submission"
        )


@router.post("/batch", response_model=ResponseModel[List[SubmissionResponse]])
async def create_batch_submissions(
    batch_request: BatchSubmissionRequest,
    background_tasks: BackgroundTasks,
    current_user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """
    批量创建提交（教师功能）
    """
    # 检查用户权限
    user_query = select(User).where(User.id == current_user_id)
    user_result = await db.execute(user_query)
    user = user_result.scalar_one_or_none()
    
    if not user or user.role not in [UserRole.TEACHER, UserRole.ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only teachers and admins can create batch submissions"
        )
    
    if len(batch_request.submissions) > 50:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Maximum 50 submissions allowed per batch"
        )
    
    try:
        created_submissions = []
        
        for submission_data in batch_request.submissions:
            submission = Submission(
                id=str(uuid.uuid4()),
                student_id=submission_data.student_id,
                assignment_id=submission_data.assignment_id,
                assignment_description=submission_data.assignment_description,
                code=submission_data.code,
                language=submission_data.language,
                student_message=submission_data.student_message,
                status="submitted",
                submitted_at=datetime.utcnow()
            )
            
            db.add(submission)
            created_submissions.append(submission)
        
        await db.commit()
        
        # 批量处理AI分析
        for submission in created_submissions:
            background_tasks.add_task(
                process_ai_analysis,
                submission.id,
                submission.student_id,
                {
                    "assignment_id": submission.assignment_id,
                    "assignment_description": submission.assignment_description,
                    "code": submission.code,
                    "language": submission.language,
                    "student_message": submission.student_message
                }
            )
        
        logger.info(f"Batch submissions created: {len(created_submissions)} by user {current_user_id}")
        
        response_data = [
            SubmissionResponse(
                id=sub.id,
                student_id=sub.student_id,
                assignment_id=sub.assignment_id,
                assignment_description=sub.assignment_description,
                code=sub.code,
                language=sub.language,
                student_message=sub.student_message,
                status=sub.status,
                submitted_at=sub.submitted_at,
                ai_analysis_status="pending"
            )
            for sub in created_submissions
        ]
        
        return ResponseModel(
            success=True,
            data=response_data,
            message=f"Successfully created {len(created_submissions)} submissions"
        )
        
    except Exception as e:
        logger.error(f"Batch submission creation failed: {str(e)}")
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create batch submissions"
        )


async def process_ai_analysis(submission_id: str, student_id: str, submission_data: Dict[str, Any]):
    """
    处理AI分析的后台任务
    Sprint 3: 使用Repository模式，并更新学生画像
    """
    try:
        from ..main import get_ai_service
        from ..services.learning_progress_service import LearningProgressService

        # 获取AI服务
        ai_service = get_ai_service()

        async with SessionLocal() as db:
            # Sprint 3: 创建Repository实例
            submission_repo = SubmissionRepository(db)
            feedback_repo = AIFeedbackRepository(db)
            profile_repo = StudentProfileRepository(db)

            # 将提交数据转换为AI服务需要的格式
            from src.models.teaching_models import SubmissionData as SubmissionDataModel, ProgrammingLanguage

            submission_obj = SubmissionDataModel(
                student_id=student_id,
                assignment_id=submission_data.get("assignment_id"),
                assignment_description=submission_data["assignment_description"],
                code=submission_data["code"],
                language=ProgrammingLanguage(submission_data["language"]),
                submitted_at=datetime.utcnow(),
                student_message=submission_data.get("student_message")
            )

            # 执行AI分析
            result = await ai_service.process_submission(submission_obj)

            # Sprint 3: 使用Repository保存AI反馈结果
            feedback = await feedback_repo.create(
                submission_id=submission_id,
                overall_score=result.overall_score,
                analysis_result=result.to_dict(),
                status="completed",
                processing_time=getattr(result, 'processing_time', None),
                ai_model_version=getattr(result, 'model_version', 'v1.0')
            )

            # Sprint 3: 使用Repository更新提交状态
            await submission_repo.update_status(
                submission_id=submission_id,
                status="processed",
                processed_at=datetime.utcnow()
            )

            # Sprint 3: 更新学生画像
            await profile_repo.update_from_feedback(
                student_id=student_id,
                feedback_data=result.to_dict()
            )

            logger.info(f"AI analysis completed for submission: {submission_id}")

    except Exception as e:
        logger.error(f"AI analysis failed for submission {submission_id}: {str(e)}")

        # 标记为失败
        async with SessionLocal() as db:
            feedback_repo = AIFeedbackRepository(db)
            await feedback_repo.mark_as_failed(
                submission_id=submission_id,
                error_message=str(e)
            )


# 获取数据库会话的本地实例
from ..database.database import SessionLocal