"""
数据访问层 - Repository模式 (Sprint 3)

提供统一的数据访问接口，封装数据库操作细节
"""

from .submission_repository import SubmissionRepository, AIFeedbackRepository
from .student_repository import StudentRepository, StudentProfileRepository
from .course_repository import CourseRepository, LessonRepository

__all__ = [
    "SubmissionRepository",
    "AIFeedbackRepository",
    "StudentRepository",
    "StudentProfileRepository",
    "CourseRepository",
    "LessonRepository",
]
