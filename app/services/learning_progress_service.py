"""
学习进度追踪服务 - Sprint 3

提供学生学习进度追踪和分析功能
"""

from typing import Dict, Any, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, desc
from datetime import datetime, timedelta
import logging

from app.database.models import (
    Submission, AIFeedback, StudentProfile,
    LearningPath, StudentExerciseAttempt, Course, Lesson
)
from app.repositories.student_repository import StudentProfileRepository
from app.repositories.submission_repository import AIFeedbackRepository

logger = logging.getLogger(__name__)


class LearningProgressService:
    """
    学习进度服务

    提供以下功能:
    - 更新学生画像
    - 计算学习统计
    - 生成进度报告
    - 推荐学习内容
    """

    def __init__(self, db: AsyncSession):
        self.db = db
        self.profile_repo = StudentProfileRepository(db)
        self.feedback_repo = AIFeedbackRepository(db)

    async def update_student_profile_from_submission(
        self,
        student_id: str,
        feedback_result: Dict[str, Any]
    ) -> StudentProfile:
        """
        根据新提交更新学生画像

        Args:
            student_id: 学生ID
            feedback_result: AI反馈结果

        Returns:
            更新后的学生画像
        """
        return await self.profile_repo.update_from_feedback(student_id, feedback_result)

    async def get_comprehensive_progress(
        self,
        student_id: str
    ) -> Dict[str, Any]:
        """
        获取学生的综合学习进度

        Args:
            student_id: 学生ID

        Returns:
            综合进度数据
        """
        # 获取学生画像
        profile = await self.profile_repo.get_or_create(student_id)

        # 获取反馈历史
        feedback_history = await self.feedback_repo.get_student_history(student_id, limit=50)

        # 获取学习路径进度
        learning_paths = await self._get_learning_paths(student_id)

        # 计算趋势
        trends = self._calculate_trends(feedback_history)

        # 获取最近活动
        recent_activity = await self._get_recent_activity(student_id)

        return {
            "profile": {
                "student_id": student_id,
                "competency_level": profile.competency_level,
                "average_score": round(profile.average_score, 2),
                "total_submissions": profile.total_submissions,
                "skill_scores": profile.skill_scores,
                "error_patterns": profile.error_patterns
            },
            "progress_trends": trends,
            "learning_paths": learning_paths,
            "recent_activity": recent_activity,
            "recommendations": await self._generate_recommendations(profile, trends),
            "achievements": await self._get_achievements(student_id, profile),
            "generated_at": datetime.utcnow().isoformat()
        }

    async def _get_learning_paths(self, student_id: str) -> List[Dict[str, Any]]:
        """获取学生的学习路径"""
        query = (
            select(LearningPath, Course.name, Course.language)
            .join(Course, LearningPath.course_id == Course.id)
            .where(LearningPath.student_id == student_id)
        )

        result = await self.db.execute(query)
        paths = result.fetchall()

        return [
            {
                "course_id": str(p.LearningPath.course_id),
                "course_name": p.name,
                "language": p.language,
                "current_lesson": p.LearningPath.current_lesson,
                "progress_percentage": round(p.LearningPath.progress_percentage, 1),
                "learning_hours": round(p.LearningPath.learning_hours, 1),
                "status": p.LearningPath.status,
                "last_study_time": p.LearningPath.last_study_time.isoformat() if p.LearningPath.last_study_time else None
            }
            for p in paths
        ]

    def _calculate_trends(self, history: List[Dict]) -> Dict[str, Any]:
        """计算学习趋势"""
        if not history:
            return {
                "score_trend": "insufficient_data",
                "activity_trend": "insufficient_data",
                "improvement_areas": []
            }

        scores = [h.get("score", 0) for h in history if h.get("score") is not None]

        if len(scores) < 3:
            return {
                "score_trend": "insufficient_data",
                "recent_average": round(sum(scores) / len(scores), 2) if scores else 0,
                "improvement_areas": []
            }

        # 分析分数趋势
        recent_5 = scores[:5]
        older_5 = scores[5:10] if len(scores) >= 10 else scores[5:]

        recent_avg = sum(recent_5) / len(recent_5)
        older_avg = sum(older_5) / len(older_5) if older_5 else recent_avg

        if recent_avg > older_avg + 5:
            score_trend = "improving"
        elif recent_avg < older_avg - 5:
            score_trend = "declining"
        else:
            score_trend = "stable"

        # 分析需要改进的领域
        improvement_areas = self._identify_improvement_areas(history)

        return {
            "score_trend": score_trend,
            "recent_average": round(recent_avg, 2),
            "older_average": round(older_avg, 2),
            "improvement_delta": round(recent_avg - older_avg, 2),
            "total_analyzed": len(scores),
            "improvement_areas": improvement_areas
        }

    def _identify_improvement_areas(self, history: List[Dict]) -> List[str]:
        """识别需要改进的领域"""
        areas = []

        # 分析最近的反馈中的低分领域
        for h in history[:10]:
            analysis = h.get("analysis_summary", {})
            code_analysis = analysis.get("code_analysis", {})

            if code_analysis.get("syntax_score", 100) < 70:
                if "语法基础" not in areas:
                    areas.append("语法基础")
            if code_analysis.get("logic_score", 100) < 70:
                if "程序逻辑" not in areas:
                    areas.append("程序逻辑")
            if code_analysis.get("style_score", 100) < 70:
                if "代码规范" not in areas:
                    areas.append("代码规范")

        return areas[:3]  # 最多返回3个

    async def _get_recent_activity(
        self,
        student_id: str,
        days: int = 7
    ) -> Dict[str, Any]:
        """获取最近活动统计"""
        since = datetime.utcnow() - timedelta(days=days)

        # 提交数量
        submissions_query = (
            select(func.count(Submission.id))
            .where(
                and_(
                    Submission.student_id == student_id,
                    Submission.submitted_at >= since
                )
            )
        )
        submissions_count = (await self.db.execute(submissions_query)).scalar() or 0

        # 平均分
        avg_query = (
            select(func.avg(AIFeedback.overall_score))
            .join(Submission, AIFeedback.submission_id == Submission.id)
            .where(
                and_(
                    Submission.student_id == student_id,
                    AIFeedback.created_at >= since,
                    AIFeedback.status == "completed"
                )
            )
        )
        avg_score = (await self.db.execute(avg_query)).scalar() or 0

        # 活跃天数
        active_days_query = (
            select(func.count(func.distinct(func.date(Submission.submitted_at))))
            .where(
                and_(
                    Submission.student_id == student_id,
                    Submission.submitted_at >= since
                )
            )
        )
        active_days = (await self.db.execute(active_days_query)).scalar() or 0

        return {
            "period_days": days,
            "submissions": submissions_count,
            "average_score": round(float(avg_score), 2) if avg_score else 0,
            "active_days": active_days,
            "activity_level": self._determine_activity_level(submissions_count, active_days, days)
        }

    def _determine_activity_level(
        self,
        submissions: int,
        active_days: int,
        total_days: int
    ) -> str:
        """确定活跃度级别"""
        if active_days == 0:
            return "inactive"
        activity_ratio = active_days / total_days
        if activity_ratio >= 0.7:
            return "very_active"
        elif activity_ratio >= 0.4:
            return "active"
        elif activity_ratio >= 0.2:
            return "moderate"
        else:
            return "low"

    async def _generate_recommendations(
        self,
        profile: StudentProfile,
        trends: Dict[str, Any]
    ) -> List[Dict[str, str]]:
        """生成学习建议"""
        recommendations = []

        # 基于能力水平的建议
        level = profile.competency_level
        if level in ["novice", "developing"]:
            recommendations.append({
                "type": "practice",
                "title": "多做基础练习",
                "description": "建议从简单题目开始，逐步建立编程基础"
            })
        elif level in ["competent", "proficient"]:
            recommendations.append({
                "type": "challenge",
                "title": "尝试更多挑战",
                "description": "可以尝试难度更高的问题，提升解决复杂问题的能力"
            })

        # 基于趋势的建议
        trend = trends.get("score_trend", "stable")
        if trend == "declining":
            recommendations.append({
                "type": "review",
                "title": "回顾基础知识",
                "description": "建议复习之前学过的内容，巩固基础"
            })
        elif trend == "improving":
            recommendations.append({
                "type": "encouragement",
                "title": "继续保持！",
                "description": "你的进步很明显，继续保持这个势头"
            })

        # 基于需要改进领域的建议
        improvement_areas = trends.get("improvement_areas", [])
        for area in improvement_areas[:2]:
            recommendations.append({
                "type": "focus",
                "title": f"关注{area}",
                "description": f"建议多练习与{area}相关的内容"
            })

        return recommendations[:5]  # 最多5条建议

    async def _get_achievements(
        self,
        student_id: str,
        profile: StudentProfile
    ) -> List[Dict[str, Any]]:
        """获取学生成就"""
        achievements = []

        # 提交数量成就
        if profile.total_submissions >= 100:
            achievements.append({
                "id": "submissions_100",
                "title": "百次提交",
                "description": "累计提交达到100次",
                "icon": "star"
            })
        elif profile.total_submissions >= 50:
            achievements.append({
                "id": "submissions_50",
                "title": "勤学者",
                "description": "累计提交达到50次",
                "icon": "fire"
            })
        elif profile.total_submissions >= 10:
            achievements.append({
                "id": "submissions_10",
                "title": "初学者",
                "description": "累计提交达到10次",
                "icon": "seedling"
            })

        # 分数成就
        if profile.average_score >= 90:
            achievements.append({
                "id": "score_90",
                "title": "优秀学员",
                "description": "平均分达到90分以上",
                "icon": "trophy"
            })
        elif profile.average_score >= 80:
            achievements.append({
                "id": "score_80",
                "title": "良好表现",
                "description": "平均分达到80分以上",
                "icon": "medal"
            })

        # 能力等级成就
        if profile.competency_level == "expert":
            achievements.append({
                "id": "level_expert",
                "title": "编程专家",
                "description": "达到专家级别",
                "icon": "crown"
            })
        elif profile.competency_level == "proficient":
            achievements.append({
                "id": "level_proficient",
                "title": "熟练程序员",
                "description": "达到熟练级别",
                "icon": "certificate"
            })

        return achievements

    async def get_class_overview(
        self,
        class_id: str
    ) -> Dict[str, Any]:
        """
        获取班级整体概览

        Args:
            class_id: 班级ID

        Returns:
            班级概览数据
        """
        from app.database.models import ClassMembership

        # 获取班级学生
        students_query = (
            select(ClassMembership.student_id)
            .where(
                and_(
                    ClassMembership.class_id == class_id,
                    ClassMembership.is_active == True
                )
            )
        )
        students_result = await self.db.execute(students_query)
        student_ids = [str(r[0]) for r in students_result.fetchall()]

        if not student_ids:
            return {"error": "No students in class"}

        # 获取班级提交统计
        submissions_query = (
            select(func.count(Submission.id))
            .where(Submission.student_id.in_(student_ids))
        )
        total_submissions = (await self.db.execute(submissions_query)).scalar() or 0

        # 获取班级平均分
        avg_query = (
            select(func.avg(AIFeedback.overall_score))
            .join(Submission, AIFeedback.submission_id == Submission.id)
            .where(
                and_(
                    Submission.student_id.in_(student_ids),
                    AIFeedback.status == "completed"
                )
            )
        )
        class_avg = (await self.db.execute(avg_query)).scalar() or 0

        # 获取分数分布
        distribution = await self._get_score_distribution(student_ids)

        return {
            "class_id": class_id,
            "total_students": len(student_ids),
            "total_submissions": total_submissions,
            "class_average_score": round(float(class_avg), 2),
            "score_distribution": distribution,
            "generated_at": datetime.utcnow().isoformat()
        }

    async def _get_score_distribution(
        self,
        student_ids: List[str]
    ) -> Dict[str, int]:
        """获取分数分布"""
        # 简化的分数分布
        distribution = {
            "90-100": 0,
            "80-89": 0,
            "70-79": 0,
            "60-69": 0,
            "0-59": 0
        }

        query = (
            select(AIFeedback.overall_score)
            .join(Submission, AIFeedback.submission_id == Submission.id)
            .where(
                and_(
                    Submission.student_id.in_(student_ids),
                    AIFeedback.status == "completed"
                )
            )
        )

        result = await self.db.execute(query)
        scores = [r[0] for r in result.fetchall()]

        for score in scores:
            if score >= 90:
                distribution["90-100"] += 1
            elif score >= 80:
                distribution["80-89"] += 1
            elif score >= 70:
                distribution["70-79"] += 1
            elif score >= 60:
                distribution["60-69"] += 1
            else:
                distribution["0-59"] += 1

        return distribution
