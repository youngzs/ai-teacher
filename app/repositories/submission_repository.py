"""
提交数据仓库 - Sprint 3

处理代码提交和AI反馈的数据访问
"""

from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, update, func, and_, desc
from sqlalchemy.orm import selectinload
from datetime import datetime
import uuid
import logging

from app.database.models import Submission, AIFeedback, User

logger = logging.getLogger(__name__)


class SubmissionRepository:
    """代码提交数据仓库"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(
        self,
        student_id: str,
        code: str,
        language: str,
        assignment_description: str,
        assignment_id: Optional[str] = None,
        student_message: Optional[str] = None
    ) -> Submission:
        """
        创建新的代码提交

        Args:
            student_id: 学生ID
            code: 代码内容
            language: 编程语言
            assignment_description: 作业描述
            assignment_id: 作业ID（可选）
            student_message: 学生留言（可选）

        Returns:
            创建的提交对象
        """
        submission = Submission(
            id=uuid.uuid4(),
            student_id=student_id,
            assignment_id=assignment_id,
            assignment_description=assignment_description,
            code=code,
            language=language,
            student_message=student_message,
            status="submitted",
            submitted_at=datetime.utcnow()
        )

        self.db.add(submission)
        await self.db.commit()
        await self.db.refresh(submission)

        logger.info(f"Created submission: {submission.id} for student: {student_id}")
        return submission

    async def get_by_id(
        self,
        submission_id: str,
        include_feedback: bool = False
    ) -> Optional[Submission]:
        """
        根据ID获取提交

        Args:
            submission_id: 提交ID
            include_feedback: 是否包含AI反馈

        Returns:
            提交对象或None
        """
        query = select(Submission).where(Submission.id == submission_id)

        if include_feedback:
            query = query.options(selectinload(Submission.ai_feedback))

        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def get_by_student(
        self,
        student_id: str,
        limit: int = 20,
        offset: int = 0,
        status: Optional[str] = None
    ) -> List[Submission]:
        """
        获取学生的所有提交

        Args:
            student_id: 学生ID
            limit: 返回数量限制
            offset: 偏移量
            status: 状态过滤

        Returns:
            提交列表
        """
        query = select(Submission).where(Submission.student_id == student_id)

        if status:
            query = query.where(Submission.status == status)

        query = query.order_by(desc(Submission.submitted_at)).limit(limit).offset(offset)

        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_by_assignment(
        self,
        assignment_id: str,
        limit: int = 50,
        offset: int = 0
    ) -> List[Submission]:
        """获取作业的所有提交"""
        query = (
            select(Submission)
            .where(Submission.assignment_id == assignment_id)
            .order_by(desc(Submission.submitted_at))
            .limit(limit)
            .offset(offset)
        )

        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def update_status(
        self,
        submission_id: str,
        status: str,
        processed_at: Optional[datetime] = None
    ) -> bool:
        """
        更新提交状态

        Args:
            submission_id: 提交ID
            status: 新状态
            processed_at: 处理时间

        Returns:
            是否更新成功
        """
        values = {"status": status, "updated_at": datetime.utcnow()}
        if processed_at:
            values["processed_at"] = processed_at

        result = await self.db.execute(
            update(Submission)
            .where(Submission.id == submission_id)
            .values(**values)
        )
        await self.db.commit()

        return result.rowcount > 0

    async def delete(self, submission_id: str) -> bool:
        """
        删除提交（级联删除AI反馈）

        Args:
            submission_id: 提交ID

        Returns:
            是否删除成功
        """
        # 先删除关联的AI反馈
        await self.db.execute(
            delete(AIFeedback).where(AIFeedback.submission_id == submission_id)
        )

        # 删除提交
        result = await self.db.execute(
            delete(Submission).where(Submission.id == submission_id)
        )
        await self.db.commit()

        logger.info(f"Deleted submission: {submission_id}")
        return result.rowcount > 0

    async def count_by_student(self, student_id: str) -> int:
        """统计学生提交数量"""
        result = await self.db.execute(
            select(func.count(Submission.id))
            .where(Submission.student_id == student_id)
        )
        return result.scalar() or 0

    async def count_by_assignment(self, assignment_id: str) -> int:
        """统计作业提交数量"""
        result = await self.db.execute(
            select(func.count(Submission.id))
            .where(Submission.assignment_id == assignment_id)
        )
        return result.scalar() or 0

    async def get_pending_submissions(self, limit: int = 10) -> List[Submission]:
        """获取待处理的提交"""
        query = (
            select(Submission)
            .where(Submission.status == "submitted")
            .order_by(Submission.submitted_at)
            .limit(limit)
        )

        result = await self.db.execute(query)
        return list(result.scalars().all())


class AIFeedbackRepository:
    """AI反馈数据仓库"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(
        self,
        submission_id: str,
        overall_score: float,
        analysis_result: Dict[str, Any],
        status: str = "completed",
        processing_time: Optional[float] = None,
        ai_model_version: Optional[str] = None
    ) -> AIFeedback:
        """
        创建AI反馈记录

        Args:
            submission_id: 提交ID
            overall_score: 总体评分
            analysis_result: 分析结果
            status: 状态
            processing_time: 处理时间
            ai_model_version: AI模型版本

        Returns:
            创建的反馈对象
        """
        feedback = AIFeedback(
            id=uuid.uuid4(),
            submission_id=submission_id,
            overall_score=overall_score,
            analysis_result=analysis_result,
            status=status,
            processing_time=processing_time,
            ai_model_version=ai_model_version,
            created_at=datetime.utcnow()
        )

        self.db.add(feedback)
        await self.db.commit()
        await self.db.refresh(feedback)

        logger.info(f"Created AI feedback: {feedback.id} for submission: {submission_id}")
        return feedback

    async def get_by_id(self, feedback_id: str) -> Optional[AIFeedback]:
        """根据ID获取反馈"""
        result = await self.db.execute(
            select(AIFeedback).where(AIFeedback.id == feedback_id)
        )
        return result.scalar_one_or_none()

    async def get_by_submission(
        self,
        submission_id: str,
        latest_only: bool = True
    ) -> Optional[AIFeedback]:
        """
        获取提交的AI反馈

        Args:
            submission_id: 提交ID
            latest_only: 是否只返回最新的

        Returns:
            反馈对象或None
        """
        query = (
            select(AIFeedback)
            .where(AIFeedback.submission_id == submission_id)
            .order_by(desc(AIFeedback.created_at))
        )

        if latest_only:
            query = query.limit(1)

        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def get_student_history(
        self,
        student_id: str,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """
        获取学生的反馈历史

        Args:
            student_id: 学生ID
            limit: 返回数量限制

        Returns:
            反馈历史列表
        """
        query = (
            select(
                AIFeedback.id,
                AIFeedback.overall_score,
                AIFeedback.analysis_result,
                AIFeedback.created_at,
                AIFeedback.processing_time,
                Submission.language,
                Submission.assignment_id,
                Submission.assignment_description
            )
            .join(Submission, AIFeedback.submission_id == Submission.id)
            .where(
                and_(
                    Submission.student_id == student_id,
                    AIFeedback.status == "completed"
                )
            )
            .order_by(desc(AIFeedback.created_at))
            .limit(limit)
        )

        result = await self.db.execute(query)
        records = result.fetchall()

        return [
            {
                "feedback_id": str(r.id),
                "score": r.overall_score,
                "analysis_summary": r.analysis_result,
                "created_at": r.created_at.isoformat() if r.created_at else None,
                "processing_time": r.processing_time,
                "language": r.language,
                "assignment_id": str(r.assignment_id) if r.assignment_id else None,
                "assignment_description": r.assignment_description[:100] if r.assignment_description else None
            }
            for r in records
        ]

    async def get_average_score_by_student(self, student_id: str) -> float:
        """获取学生的平均分"""
        query = (
            select(func.avg(AIFeedback.overall_score))
            .join(Submission, AIFeedback.submission_id == Submission.id)
            .where(
                and_(
                    Submission.student_id == student_id,
                    AIFeedback.status == "completed"
                )
            )
        )

        result = await self.db.execute(query)
        avg = result.scalar()
        return float(avg) if avg else 0.0

    async def mark_as_failed(
        self,
        submission_id: str,
        error_message: str
    ) -> AIFeedback:
        """标记分析失败"""
        return await self.create(
            submission_id=submission_id,
            overall_score=0.0,
            analysis_result={"error": error_message, "status": "failed"},
            status="failed"
        )

    async def get_statistics(self, days: int = 30) -> Dict[str, Any]:
        """
        获取反馈统计

        Args:
            days: 统计天数

        Returns:
            统计数据
        """
        from datetime import timedelta
        since = datetime.utcnow() - timedelta(days=days)

        # 总数
        total_query = select(func.count(AIFeedback.id)).where(
            AIFeedback.created_at >= since
        )
        total = (await self.db.execute(total_query)).scalar() or 0

        # 平均分
        avg_query = select(func.avg(AIFeedback.overall_score)).where(
            and_(
                AIFeedback.created_at >= since,
                AIFeedback.status == "completed"
            )
        )
        avg_score = (await self.db.execute(avg_query)).scalar() or 0

        # 平均处理时间
        time_query = select(func.avg(AIFeedback.processing_time)).where(
            and_(
                AIFeedback.created_at >= since,
                AIFeedback.processing_time.isnot(None)
            )
        )
        avg_time = (await self.db.execute(time_query)).scalar() or 0

        return {
            "total_feedbacks": total,
            "average_score": round(float(avg_score), 2),
            "average_processing_time": round(float(avg_time), 2),
            "period_days": days
        }
