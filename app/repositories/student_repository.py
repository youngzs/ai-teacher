"""
学生数据仓库 - Sprint 3

处理学生和学生画像的数据访问
"""

from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, func, and_, desc
from datetime import datetime
import uuid
import logging

from app.database.models import User, StudentProfile, Submission, AIFeedback

logger = logging.getLogger(__name__)


class StudentRepository:
    """学生数据仓库"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, student_id: str) -> Optional[User]:
        """根据ID获取学生"""
        result = await self.db.execute(
            select(User).where(
                and_(
                    User.id == student_id,
                    User.role == "student"
                )
            )
        )
        return result.scalar_one_or_none()

    async def get_by_username(self, username: str) -> Optional[User]:
        """根据用户名获取学生"""
        result = await self.db.execute(
            select(User).where(
                and_(
                    User.username == username,
                    User.role == "student"
                )
            )
        )
        return result.scalar_one_or_none()

    async def get_all_active(
        self,
        limit: int = 100,
        offset: int = 0
    ) -> List[User]:
        """获取所有活跃学生"""
        query = (
            select(User)
            .where(
                and_(
                    User.role == "student",
                    User.is_active == True
                )
            )
            .order_by(User.created_at.desc())
            .limit(limit)
            .offset(offset)
        )

        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_students_by_class(
        self,
        class_id: str,
        limit: int = 50
    ) -> List[User]:
        """获取班级的所有学生"""
        from app.database.models import ClassMembership

        query = (
            select(User)
            .join(ClassMembership, User.id == ClassMembership.student_id)
            .where(
                and_(
                    ClassMembership.class_id == class_id,
                    ClassMembership.is_active == True,
                    User.is_active == True
                )
            )
            .limit(limit)
        )

        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def count_active_students(self) -> int:
        """统计活跃学生数量"""
        result = await self.db.execute(
            select(func.count(User.id))
            .where(
                and_(
                    User.role == "student",
                    User.is_active == True
                )
            )
        )
        return result.scalar() or 0

    async def get_student_statistics(self, student_id: str) -> Dict[str, Any]:
        """
        获取学生统计信息

        Args:
            student_id: 学生ID

        Returns:
            统计数据
        """
        # 提交数量
        submissions_count = await self.db.execute(
            select(func.count(Submission.id))
            .where(Submission.student_id == student_id)
        )
        total_submissions = submissions_count.scalar() or 0

        # 平均分
        avg_score = await self.db.execute(
            select(func.avg(AIFeedback.overall_score))
            .join(Submission, AIFeedback.submission_id == Submission.id)
            .where(
                and_(
                    Submission.student_id == student_id,
                    AIFeedback.status == "completed"
                )
            )
        )
        average_score = avg_score.scalar() or 0

        # 最近提交
        recent = await self.db.execute(
            select(Submission.submitted_at)
            .where(Submission.student_id == student_id)
            .order_by(desc(Submission.submitted_at))
            .limit(1)
        )
        last_submission = recent.scalar()

        # 高分提交数
        high_score = await self.db.execute(
            select(func.count(AIFeedback.id))
            .join(Submission, AIFeedback.submission_id == Submission.id)
            .where(
                and_(
                    Submission.student_id == student_id,
                    AIFeedback.overall_score >= 80
                )
            )
        )
        high_score_count = high_score.scalar() or 0

        return {
            "total_submissions": total_submissions,
            "average_score": round(float(average_score), 2),
            "last_submission": last_submission.isoformat() if last_submission else None,
            "high_score_submissions": high_score_count,
            "improvement_rate": self._calculate_improvement_rate(student_id)
        }

    def _calculate_improvement_rate(self, student_id: str) -> float:
        """计算进步率（简化版）"""
        # 这个方法可以根据需要进一步完善
        return 0.0


class StudentProfileRepository:
    """学生画像数据仓库"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_student_id(self, student_id: str) -> Optional[StudentProfile]:
        """根据学生ID获取画像"""
        result = await self.db.execute(
            select(StudentProfile).where(StudentProfile.student_id == student_id)
        )
        return result.scalar_one_or_none()

    async def create(
        self,
        student_id: str,
        competency_level: str = "novice",
        skill_scores: Optional[Dict] = None,
        learning_style: Optional[Dict] = None
    ) -> StudentProfile:
        """
        创建学生画像

        Args:
            student_id: 学生ID
            competency_level: 能力水平
            skill_scores: 技能得分
            learning_style: 学习风格

        Returns:
            创建的画像对象
        """
        profile = StudentProfile(
            id=uuid.uuid4(),
            student_id=student_id,
            competency_level=competency_level,
            skill_scores=skill_scores or {},
            learning_style=learning_style or {},
            error_patterns={},
            learning_history=[],
            progress_trends={},
            total_submissions=0,
            average_score=0.0,
            improvement_rate=0.0,
            created_at=datetime.utcnow()
        )

        self.db.add(profile)
        await self.db.commit()
        await self.db.refresh(profile)

        logger.info(f"Created student profile for: {student_id}")
        return profile

    async def get_or_create(self, student_id: str) -> StudentProfile:
        """获取或创建学生画像"""
        profile = await self.get_by_student_id(student_id)
        if not profile:
            profile = await self.create(student_id)
        return profile

    async def update(
        self,
        student_id: str,
        **kwargs
    ) -> Optional[StudentProfile]:
        """
        更新学生画像

        Args:
            student_id: 学生ID
            **kwargs: 要更新的字段

        Returns:
            更新后的画像对象
        """
        kwargs["updated_at"] = datetime.utcnow()

        result = await self.db.execute(
            update(StudentProfile)
            .where(StudentProfile.student_id == student_id)
            .values(**kwargs)
            .returning(StudentProfile)
        )
        await self.db.commit()

        return result.scalar_one_or_none()

    async def update_from_feedback(
        self,
        student_id: str,
        feedback_data: Dict[str, Any]
    ) -> StudentProfile:
        """
        根据反馈更新学生画像

        Args:
            student_id: 学生ID
            feedback_data: 反馈数据

        Returns:
            更新后的画像
        """
        profile = await self.get_or_create(student_id)

        # 更新统计数据
        profile.total_submissions += 1

        # 更新平均分
        new_score = feedback_data.get("overall_score", 0)
        if profile.total_submissions == 1:
            profile.average_score = new_score
        else:
            # 滑动平均
            profile.average_score = (
                profile.average_score * (profile.total_submissions - 1) + new_score
            ) / profile.total_submissions

        # 更新技能得分
        code_analysis = feedback_data.get("code_analysis", {})
        if code_analysis:
            current_skills = profile.skill_scores or {}
            for skill in ["syntax_score", "logic_score", "style_score", "performance_score"]:
                if skill in code_analysis:
                    skill_key = skill.replace("_score", "")
                    old_value = current_skills.get(skill_key, code_analysis[skill])
                    # 使用指数移动平均
                    current_skills[skill_key] = 0.7 * old_value + 0.3 * code_analysis[skill]
            profile.skill_scores = current_skills

        # 更新能力水平
        profile.competency_level = self._determine_level(profile.average_score)

        # 更新错误模式
        errors = code_analysis.get("critical_errors", [])
        if errors:
            error_patterns = profile.error_patterns or {}
            for error in errors:
                error_type = error.get("type", "unknown") if isinstance(error, dict) else str(error)
                error_patterns[error_type] = error_patterns.get(error_type, 0) + 1
            profile.error_patterns = error_patterns

        # 更新分析时间
        profile.last_analyzed = datetime.utcnow()
        profile.updated_at = datetime.utcnow()

        await self.db.commit()
        await self.db.refresh(profile)

        return profile

    def _determine_level(self, avg_score: float) -> str:
        """根据平均分确定能力水平"""
        if avg_score >= 90:
            return "expert"
        elif avg_score >= 80:
            return "proficient"
        elif avg_score >= 70:
            return "competent"
        elif avg_score >= 60:
            return "developing"
        else:
            return "novice"

    async def get_top_students(self, limit: int = 10) -> List[StudentProfile]:
        """获取得分最高的学生"""
        query = (
            select(StudentProfile)
            .where(StudentProfile.total_submissions >= 3)  # 至少3次提交
            .order_by(desc(StudentProfile.average_score))
            .limit(limit)
        )

        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_students_needing_help(self, limit: int = 10) -> List[StudentProfile]:
        """获取需要帮助的学生"""
        query = (
            select(StudentProfile)
            .where(
                and_(
                    StudentProfile.total_submissions >= 2,
                    StudentProfile.average_score < 60
                )
            )
            .order_by(StudentProfile.average_score)
            .limit(limit)
        )

        result = await self.db.execute(query)
        return list(result.scalars().all())
