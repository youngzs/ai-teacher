"""
课程数据仓库 - Sprint 3

处理课程和课时的数据访问
"""

from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, func, and_, desc
from sqlalchemy.orm import selectinload
from datetime import datetime
import uuid
import logging

from app.database.models import (
    Course, Lesson, CourseExercise, LearningPath,
    StudentExerciseAttempt
)

logger = logging.getLogger(__name__)


class CourseRepository:
    """课程数据仓库"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(
        self,
        course_id: str,
        include_lessons: bool = False
    ) -> Optional[Course]:
        """
        根据ID获取课程

        Args:
            course_id: 课程ID
            include_lessons: 是否包含课时

        Returns:
            课程对象或None
        """
        query = select(Course).where(Course.id == course_id)

        if include_lessons:
            query = query.options(selectinload(Course.lessons))

        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def get_by_code(self, code: str) -> Optional[Course]:
        """根据课程代码获取课程"""
        result = await self.db.execute(
            select(Course).where(Course.code == code)
        )
        return result.scalar_one_or_none()

    async def get_all_active(
        self,
        language: Optional[str] = None,
        limit: int = 50
    ) -> List[Course]:
        """
        获取所有活跃课程

        Args:
            language: 编程语言过滤
            limit: 返回数量限制

        Returns:
            课程列表
        """
        query = select(Course).where(Course.is_active == True)

        if language:
            query = query.where(Course.language == language)

        query = query.order_by(Course.created_at.desc()).limit(limit)

        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def create(
        self,
        name: str,
        language: str,
        code: Optional[str] = None,
        description: Optional[str] = None,
        total_hours: int = 0,
        difficulty_level: str = "beginner",
        curriculum_data: Optional[Dict] = None,
        learning_objectives: Optional[List] = None
    ) -> Course:
        """
        创建课程

        Args:
            name: 课程名称
            language: 编程语言
            code: 课程代码
            description: 课程描述
            total_hours: 总课时
            difficulty_level: 难度级别
            curriculum_data: 课程大纲
            learning_objectives: 学习目标

        Returns:
            创建的课程对象
        """
        course = Course(
            id=uuid.uuid4(),
            name=name,
            code=code,
            language=language,
            description=description,
            total_hours=total_hours,
            difficulty_level=difficulty_level,
            curriculum_data=curriculum_data or {},
            learning_objectives=learning_objectives or [],
            is_active=True,
            created_at=datetime.utcnow()
        )

        self.db.add(course)
        await self.db.commit()
        await self.db.refresh(course)

        logger.info(f"Created course: {course.id} - {name}")
        return course

    async def update(self, course_id: str, **kwargs) -> Optional[Course]:
        """更新课程"""
        kwargs["updated_at"] = datetime.utcnow()

        await self.db.execute(
            update(Course)
            .where(Course.id == course_id)
            .values(**kwargs)
        )
        await self.db.commit()

        return await self.get_by_id(course_id)

    async def get_course_statistics(self, course_id: str) -> Dict[str, Any]:
        """获取课程统计"""
        # 课时数量
        lessons_count = await self.db.execute(
            select(func.count(Lesson.id))
            .where(Lesson.course_id == course_id)
        )
        total_lessons = lessons_count.scalar() or 0

        # 练习数量
        exercises_count = await self.db.execute(
            select(func.count(CourseExercise.id))
            .where(CourseExercise.course_id == course_id)
        )
        total_exercises = exercises_count.scalar() or 0

        # 学习路径数量（正在学习的学生数）
        learners_count = await self.db.execute(
            select(func.count(LearningPath.id))
            .where(
                and_(
                    LearningPath.course_id == course_id,
                    LearningPath.status == "active"
                )
            )
        )
        active_learners = learners_count.scalar() or 0

        return {
            "total_lessons": total_lessons,
            "total_exercises": total_exercises,
            "active_learners": active_learners
        }


class LessonRepository:
    """课时数据仓库"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, lesson_id: str) -> Optional[Lesson]:
        """根据ID获取课时"""
        result = await self.db.execute(
            select(Lesson).where(Lesson.id == lesson_id)
        )
        return result.scalar_one_or_none()

    async def get_by_course(
        self,
        course_id: str,
        active_only: bool = True
    ) -> List[Lesson]:
        """
        获取课程的所有课时

        Args:
            course_id: 课程ID
            active_only: 是否只返回活跃课时

        Returns:
            课时列表
        """
        query = select(Lesson).where(Lesson.course_id == course_id)

        if active_only:
            query = query.where(Lesson.is_active == True)

        query = query.order_by(Lesson.lesson_number)

        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_by_number(
        self,
        course_id: str,
        lesson_number: int
    ) -> Optional[Lesson]:
        """根据课程ID和课时编号获取课时"""
        result = await self.db.execute(
            select(Lesson).where(
                and_(
                    Lesson.course_id == course_id,
                    Lesson.lesson_number == lesson_number
                )
            )
        )
        return result.scalar_one_or_none()

    async def create(
        self,
        course_id: str,
        lesson_number: int,
        title: str,
        content: Optional[str] = None,
        duration: int = 45,
        learning_objectives: Optional[List] = None,
        key_concepts: Optional[List] = None,
        teaching_structure: Optional[Dict] = None,
        ai_support_strategies: Optional[Dict] = None
    ) -> Lesson:
        """
        创建课时

        Args:
            course_id: 课程ID
            lesson_number: 课时编号
            title: 课时标题
            content: 课时内容
            duration: 时长（分钟）
            learning_objectives: 学习目标
            key_concepts: 关键概念
            teaching_structure: 教学结构
            ai_support_strategies: AI支持策略

        Returns:
            创建的课时对象
        """
        lesson = Lesson(
            id=uuid.uuid4(),
            course_id=course_id,
            lesson_number=lesson_number,
            title=title,
            content=content,
            duration=duration,
            learning_objectives=learning_objectives or [],
            key_concepts=key_concepts or [],
            teaching_structure=teaching_structure or {},
            ai_support_strategies=ai_support_strategies or {},
            is_active=True,
            created_at=datetime.utcnow()
        )

        self.db.add(lesson)
        await self.db.commit()
        await self.db.refresh(lesson)

        logger.info(f"Created lesson: {lesson.id} - {title}")
        return lesson

    async def create_batch(
        self,
        course_id: str,
        lessons_data: List[Dict[str, Any]]
    ) -> List[Lesson]:
        """
        批量创建课时

        Args:
            course_id: 课程ID
            lessons_data: 课时数据列表

        Returns:
            创建的课时列表
        """
        lessons = []
        for data in lessons_data:
            lesson = Lesson(
                id=uuid.uuid4(),
                course_id=course_id,
                lesson_number=data.get("lesson_number"),
                title=data.get("title"),
                subtitle=data.get("subtitle"),
                content=data.get("content"),
                duration=data.get("duration", 45),
                learning_objectives=data.get("learning_objectives", []),
                key_concepts=data.get("key_concepts", []),
                teaching_structure=data.get("teaching_structure", {}),
                ai_support_strategies=data.get("ai_support_strategies", {}),
                is_active=True,
                created_at=datetime.utcnow()
            )
            lessons.append(lesson)
            self.db.add(lesson)

        await self.db.commit()

        for lesson in lessons:
            await self.db.refresh(lesson)

        logger.info(f"Created {len(lessons)} lessons for course: {course_id}")
        return lessons

    async def count_by_course(self, course_id: str) -> int:
        """统计课程的课时数量"""
        result = await self.db.execute(
            select(func.count(Lesson.id))
            .where(
                and_(
                    Lesson.course_id == course_id,
                    Lesson.is_active == True
                )
            )
        )
        return result.scalar() or 0


class LearningPathRepository:
    """学习路径数据仓库"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_student_and_course(
        self,
        student_id: str,
        course_id: str
    ) -> Optional[LearningPath]:
        """获取学生的特定课程学习路径"""
        result = await self.db.execute(
            select(LearningPath).where(
                and_(
                    LearningPath.student_id == student_id,
                    LearningPath.course_id == course_id
                )
            )
        )
        return result.scalar_one_or_none()

    async def get_by_student(self, student_id: str) -> List[LearningPath]:
        """获取学生的所有学习路径"""
        result = await self.db.execute(
            select(LearningPath)
            .where(LearningPath.student_id == student_id)
            .order_by(desc(LearningPath.last_study_time))
        )
        return list(result.scalars().all())

    async def create(
        self,
        student_id: str,
        course_id: str
    ) -> LearningPath:
        """创建学习路径"""
        path = LearningPath(
            id=uuid.uuid4(),
            student_id=student_id,
            course_id=course_id,
            current_lesson=1,
            completed_lessons=[],
            progress_percentage=0.0,
            learning_hours=0.0,
            status="active",
            created_at=datetime.utcnow()
        )

        self.db.add(path)
        await self.db.commit()
        await self.db.refresh(path)

        logger.info(f"Created learning path for student {student_id} in course {course_id}")
        return path

    async def get_or_create(
        self,
        student_id: str,
        course_id: str
    ) -> LearningPath:
        """获取或创建学习路径"""
        path = await self.get_by_student_and_course(student_id, course_id)
        if not path:
            path = await self.create(student_id, course_id)
        return path

    async def update_progress(
        self,
        student_id: str,
        course_id: str,
        lesson_completed: int,
        time_spent: float = 0
    ) -> LearningPath:
        """
        更新学习进度

        Args:
            student_id: 学生ID
            course_id: 课程ID
            lesson_completed: 完成的课时编号
            time_spent: 花费时间（小时）

        Returns:
            更新后的学习路径
        """
        path = await self.get_or_create(student_id, course_id)

        # 更新已完成课时
        completed = path.completed_lessons or []
        if lesson_completed not in completed:
            completed.append(lesson_completed)
            completed.sort()

        # 获取课程总课时数
        total_lessons = await self.db.execute(
            select(func.count(Lesson.id))
            .where(
                and_(
                    Lesson.course_id == course_id,
                    Lesson.is_active == True
                )
            )
        )
        total = total_lessons.scalar() or 1

        # 更新进度
        path.completed_lessons = completed
        path.current_lesson = max(completed) + 1 if completed else 1
        path.progress_percentage = (len(completed) / total) * 100
        path.learning_hours += time_spent
        path.last_study_time = datetime.utcnow()
        path.updated_at = datetime.utcnow()

        # 检查是否完成
        if len(completed) >= total:
            path.status = "completed"

        await self.db.commit()
        await self.db.refresh(path)

        return path
