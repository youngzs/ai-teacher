"""
AI教学助手系统 - 课程相关模式定义
定义课程、班级、作业等相关的Pydantic模式

Author: AI Backend Architecture Expert
Date: 2025-09-11
"""

from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum

from .common import validate_non_empty_string


class DifficultyLevel(str, Enum):
    """难度级别枚举"""
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"


class AssignmentStatus(str, Enum):
    """作业状态枚举"""
    DRAFT = "draft"
    ACTIVE = "active"
    INACTIVE = "inactive"
    ARCHIVED = "archived"


# 班级相关模式
class ClassCreate(BaseModel):
    """创建班级模式"""
    name: str = Field(..., min_length=1, max_length=100, description="班级名称")
    description: Optional[str] = Field(None, max_length=500, description="班级描述")
    course_code: Optional[str] = Field(None, max_length=20, description="课程代码")
    semester: Optional[str] = Field(None, max_length=20, description="学期")
    academic_year: Optional[str] = Field(None, max_length=10, description="学年")
    settings: Optional[Dict[str, Any]] = Field(default={}, description="班级设置")
    
    @validator('name')
    def validate_name(cls, v):
        """验证班级名称"""
        return validate_non_empty_string(v)
    
    class Config:
        schema_extra = {
            "example": {
                "name": "Python程序设计基础",
                "description": "面向初学者的Python编程课程，涵盖基础语法、数据结构和简单算法",
                "course_code": "CS101",
                "semester": "2024春",
                "academic_year": "2023-2024",
                "settings": {
                    "allow_late_submission": True,
                    "auto_grading": True,
                    "discussion_enabled": True
                }
            }
        }


class ClassUpdate(BaseModel):
    """更新班级模式"""
    name: Optional[str] = Field(None, min_length=1, max_length=100, description="班级名称")
    description: Optional[str] = Field(None, max_length=500, description="班级描述")
    course_code: Optional[str] = Field(None, max_length=20, description="课程代码")
    semester: Optional[str] = Field(None, max_length=20, description="学期")
    academic_year: Optional[str] = Field(None, max_length=10, description="学年")
    settings: Optional[Dict[str, Any]] = Field(None, description="班级设置")
    is_active: Optional[bool] = Field(None, description="是否激活")
    
    @validator('name')
    def validate_name(cls, v):
        """验证班级名称"""
        if v is not None:
            return validate_non_empty_string(v)
        return v


class ClassResponse(BaseModel):
    """班级响应模式"""
    id: str = Field(..., description="班级ID")
    name: str = Field(..., description="班级名称")
    description: Optional[str] = Field(None, description="班级描述")
    teacher_id: str = Field(..., description="教师ID")
    teacher_name: Optional[str] = Field(None, description="教师姓名")
    course_code: Optional[str] = Field(None, description="课程代码")
    semester: Optional[str] = Field(None, description="学期")
    academic_year: Optional[str] = Field(None, description="学年")
    settings: Dict[str, Any] = Field(default={}, description="班级设置")
    is_active: bool = Field(..., description="是否激活")
    student_count: int = Field(0, description="学生数量")
    assignment_count: int = Field(0, description="作业数量")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: Optional[datetime] = Field(None, description="更新时间")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class ClassListResponse(BaseModel):
    """班级列表响应模式（简化版）"""
    id: str = Field(..., description="班级ID")
    name: str = Field(..., description="班级名称")
    course_code: Optional[str] = Field(None, description="课程代码")
    semester: Optional[str] = Field(None, description="学期")
    teacher_name: Optional[str] = Field(None, description="教师姓名")
    student_count: int = Field(0, description="学生数量")
    is_active: bool = Field(..., description="是否激活")
    created_at: datetime = Field(..., description="创建时间")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


# 作业相关模式
class AssignmentCreate(BaseModel):
    """创建作业模式"""
    title: str = Field(..., min_length=1, max_length=200, description="作业标题")
    description: str = Field(..., min_length=1, description="作业描述")
    language: str = Field(..., description="编程语言")
    difficulty_level: Optional[DifficultyLevel] = Field(None, description="难度级别")
    estimated_time: Optional[str] = Field(None, max_length=50, description="预计完成时间")
    due_date: Optional[datetime] = Field(None, description="截止时间")
    requirements: Optional[Dict[str, Any]] = Field(default={}, description="作业要求")
    test_cases: Optional[List[Dict[str, Any]]] = Field(default=[], description="测试用例")
    grading_rubric: Optional[Dict[str, Any]] = Field(default={}, description="评分标准")
    
    @validator('title')
    def validate_title(cls, v):
        """验证作业标题"""
        return validate_non_empty_string(v)
    
    @validator('description')
    def validate_description(cls, v):
        """验证作业描述"""
        return validate_non_empty_string(v)
    
    @validator('due_date')
    def validate_due_date(cls, v):
        """验证截止时间"""
        if v and v <= datetime.utcnow():
            raise ValueError('Due date must be in the future')
        return v
    
    class Config:
        schema_extra = {
            "example": {
                "title": "循环结构练习",
                "description": "使用for循环打印1到100之间的所有素数",
                "language": "python",
                "difficulty_level": "intermediate",
                "estimated_time": "30分钟",
                "due_date": "2024-12-31T23:59:59",
                "requirements": {
                    "min_lines": 5,
                    "max_lines": 50,
                    "required_concepts": ["for循环", "条件判断", "数学运算"]
                },
                "test_cases": [
                    {
                        "input": "",
                        "expected_output": "2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71, 73, 79, 83, 89, 97",
                        "description": "打印1到100的所有素数"
                    }
                ],
                "grading_rubric": {
                    "correctness": 40,
                    "efficiency": 30,
                    "code_style": 20,
                    "documentation": 10
                }
            }
        }


class AssignmentUpdate(BaseModel):
    """更新作业模式"""
    title: Optional[str] = Field(None, min_length=1, max_length=200, description="作业标题")
    description: Optional[str] = Field(None, min_length=1, description="作业描述")
    language: Optional[str] = Field(None, description="编程语言")
    difficulty_level: Optional[DifficultyLevel] = Field(None, description="难度级别")
    estimated_time: Optional[str] = Field(None, max_length=50, description="预计完成时间")
    due_date: Optional[datetime] = Field(None, description="截止时间")
    requirements: Optional[Dict[str, Any]] = Field(None, description="作业要求")
    test_cases: Optional[List[Dict[str, Any]]] = Field(None, description="测试用例")
    grading_rubric: Optional[Dict[str, Any]] = Field(None, description="评分标准")
    is_active: Optional[bool] = Field(None, description="是否激活")
    
    @validator('title')
    def validate_title(cls, v):
        """验证作业标题"""
        if v is not None:
            return validate_non_empty_string(v)
        return v
    
    @validator('description')
    def validate_description(cls, v):
        """验证作业描述"""
        if v is not None:
            return validate_non_empty_string(v)
        return v


class AssignmentResponse(BaseModel):
    """作业响应模式"""
    id: str = Field(..., description="作业ID")
    class_id: str = Field(..., description="班级ID")
    class_name: Optional[str] = Field(None, description="班级名称")
    title: str = Field(..., description="作业标题")
    description: str = Field(..., description="作业描述")
    language: str = Field(..., description="编程语言")
    difficulty_level: Optional[DifficultyLevel] = Field(None, description="难度级别")
    estimated_time: Optional[str] = Field(None, description="预计完成时间")
    due_date: Optional[datetime] = Field(None, description="截止时间")
    requirements: Dict[str, Any] = Field(default={}, description="作业要求")
    test_cases: List[Dict[str, Any]] = Field(default=[], description="测试用例")
    grading_rubric: Dict[str, Any] = Field(default={}, description="评分标准")
    is_active: bool = Field(..., description="是否激活")
    submission_count: int = Field(0, description="提交数量")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: Optional[datetime] = Field(None, description="更新时间")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class AssignmentListResponse(BaseModel):
    """作业列表响应模式（简化版）"""
    id: str = Field(..., description="作业ID")
    title: str = Field(..., description="作业标题")
    language: str = Field(..., description="编程语言")
    difficulty_level: Optional[DifficultyLevel] = Field(None, description="难度级别")
    due_date: Optional[datetime] = Field(None, description="截止时间")
    is_active: bool = Field(..., description="是否激活")
    submission_count: int = Field(0, description="提交数量")
    created_at: datetime = Field(..., description="创建时间")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


# 班级成员相关模式
class ClassMemberAdd(BaseModel):
    """添加班级成员模式"""
    student_emails: List[str] = Field(..., description="学生邮箱列表")
    role: str = Field("student", description="成员角色")
    
    @validator('student_emails')
    def validate_emails(cls, v):
        """验证邮箱列表"""
        if not v:
            raise ValueError('At least one email is required')
        if len(v) > 100:
            raise ValueError('Maximum 100 emails allowed')
        return v
    
    class Config:
        schema_extra = {
            "example": {
                "student_emails": [
                    "student1@example.com",
                    "student2@example.com",
                    "student3@example.com"
                ],
                "role": "student"
            }
        }


class ClassMemberResponse(BaseModel):
    """班级成员响应模式"""
    id: str = Field(..., description="成员关系ID")
    student_id: str = Field(..., description="学生ID")
    student_name: str = Field(..., description="学生姓名")
    student_email: str = Field(..., description="学生邮箱")
    role: str = Field(..., description="成员角色")
    joined_at: datetime = Field(..., description="加入时间")
    is_active: bool = Field(..., description="是否激活")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


# 班级统计模式
class ClassStats(BaseModel):
    """班级统计模式"""
    class_id: str = Field(..., description="班级ID")
    student_count: int = Field(..., description="学生总数")
    assignment_count: int = Field(..., description="作业总数")
    total_submissions: int = Field(..., description="提交总数")
    average_score: float = Field(..., description="平均分")
    completion_rate: float = Field(..., description="完成率")
    active_students: int = Field(..., description="活跃学生数")
    recent_activity: List[Dict[str, Any]] = Field(..., description="最近活动")
    
    class Config:
        schema_extra = {
            "example": {
                "class_id": "class-uuid",
                "student_count": 25,
                "assignment_count": 8,
                "total_submissions": 180,
                "average_score": 82.5,
                "completion_rate": 0.9,
                "active_students": 23,
                "recent_activity": [
                    {
                        "type": "submission",
                        "student_name": "张三",
                        "assignment_title": "循环结构练习",
                        "timestamp": "2024-01-15T10:30:00"
                    }
                ]
            }
        }


# 导出所有模式
__all__ = [
    "DifficultyLevel",
    "AssignmentStatus",
    "ClassCreate",
    "ClassUpdate", 
    "ClassResponse",
    "ClassListResponse",
    "AssignmentCreate",
    "AssignmentUpdate",
    "AssignmentResponse",
    "AssignmentListResponse",
    "ClassMemberAdd",
    "ClassMemberResponse",
    "ClassStats"
]