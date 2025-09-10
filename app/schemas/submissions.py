"""
AI教学助手系统 - 提交相关模式定义
定义代码提交、批量处理等相关的Pydantic模式

Author: AI Backend Architecture Expert
Date: 2025-09-10
"""

from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum

from .common import validate_non_empty_string


class ProgrammingLanguage(str, Enum):
    """支持的编程语言"""
    PYTHON = "python"
    C = "c"
    CPP = "cpp"
    JAVA = "java"
    JAVASCRIPT = "javascript"
    TYPESCRIPT = "typescript"


class SubmissionStatus(str, Enum):
    """提交状态"""
    SUBMITTED = "submitted"
    ANALYZING = "analyzing"
    ANALYZED = "analyzed"
    FAILED = "failed"


class SubmissionCreate(BaseModel):
    """创建提交模式"""
    assignment_id: Optional[str] = Field(None, description="作业ID")
    assignment_description: str = Field(..., description="作业描述")
    code: str = Field(..., min_length=1, description="代码内容")
    language: ProgrammingLanguage = Field(..., description="编程语言")
    student_message: Optional[str] = Field(None, description="学生留言")
    
    @validator('assignment_description')
    def validate_assignment_description(cls, v):
        """验证作业描述"""
        return validate_non_empty_string(v)
    
    @validator('code')
    def validate_code_content(cls, v):
        """验证代码内容"""
        if not v.strip():
            raise ValueError('Code cannot be empty')
        if len(v) > 50000:  # 50KB限制
            raise ValueError('Code is too long. Maximum 50KB allowed.')
        return v
    
    class Config:
        schema_extra = {
            "example": {
                "assignment_id": "python_loops_001",
                "assignment_description": "编写一个程序，使用for循环打印1到10的所有偶数",
                "code": "for i in range(1, 11):\n    if i % 2 == 0:\n        print(i)",
                "language": "python",
                "student_message": "请帮我检查这个解决方案是否正确"
            }
        }


class SubmissionUpdate(BaseModel):
    """更新提交模式"""
    code: Optional[str] = Field(None, description="代码内容")
    student_message: Optional[str] = Field(None, description="学生留言")
    status: Optional[SubmissionStatus] = Field(None, description="提交状态")
    
    @validator('code')
    def validate_code_content(cls, v):
        """验证代码内容"""
        if v is not None and not v.strip():
            raise ValueError('Code cannot be empty')
        return v


class SubmissionResponse(BaseModel):
    """提交响应模式"""
    id: str = Field(..., description="提交ID")
    student_id: str = Field(..., description="学生ID")
    assignment_id: Optional[str] = Field(None, description="作业ID")
    assignment_description: str = Field(..., description="作业描述")
    code: str = Field(..., description="代码内容")
    language: ProgrammingLanguage = Field(..., description="编程语言")
    student_message: Optional[str] = Field(None, description="学生留言")
    status: SubmissionStatus = Field(..., description="提交状态")
    
    # 时间信息
    submitted_at: datetime = Field(..., description="提交时间")
    processed_at: Optional[datetime] = Field(None, description="处理完成时间")
    
    # AI分析状态
    ai_analysis_status: Optional[str] = Field(None, description="AI分析状态")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
        schema_extra = {
            "example": {
                "id": "submission-uuid",
                "student_id": "student-uuid", 
                "assignment_id": "python_loops_001",
                "assignment_description": "编写一个程序，使用for循环打印1到10的所有偶数",
                "code": "for i in range(1, 11):\n    if i % 2 == 0:\n        print(i)",
                "language": "python",
                "student_message": "请帮我检查这个解决方案是否正确",
                "status": "analyzed",
                "submitted_at": "2023-09-10T10:00:00",
                "processed_at": "2023-09-10T10:01:30",
                "ai_analysis_status": "completed"
            }
        }


class SubmissionListResponse(BaseModel):
    """提交列表响应模式（简化版）"""
    id: str = Field(..., description="提交ID")
    assignment_id: Optional[str] = Field(None, description="作业ID")
    assignment_description: str = Field(..., description="作业描述")
    language: ProgrammingLanguage = Field(..., description="编程语言")
    status: SubmissionStatus = Field(..., description="提交状态")
    submitted_at: datetime = Field(..., description="提交时间")
    ai_analysis_status: Optional[str] = Field(None, description="AI分析状态")
    code_preview: str = Field(..., description="代码预览")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class BatchSubmissionItem(BaseModel):
    """批量提交项目模式"""
    student_id: str = Field(..., description="学生ID")
    assignment_id: str = Field(..., description="作业ID")
    assignment_description: str = Field(..., description="作业描述")
    code: str = Field(..., min_length=1, description="代码内容")
    language: ProgrammingLanguage = Field(..., description="编程语言")
    student_message: Optional[str] = Field(None, description="学生留言")
    
    @validator('assignment_description')
    def validate_assignment_description(cls, v):
        """验证作业描述"""
        return validate_non_empty_string(v)
    
    @validator('code')
    def validate_code_content(cls, v):
        """验证代码内容"""
        if not v.strip():
            raise ValueError('Code cannot be empty')
        return v


class BatchSubmissionRequest(BaseModel):
    """批量提交请求模式"""
    submissions: List[BatchSubmissionItem] = Field(..., description="提交列表")
    
    @validator('submissions')
    def validate_submissions_count(cls, v):
        """验证提交数量"""
        if len(v) == 0:
            raise ValueError('At least one submission is required')
        if len(v) > 50:
            raise ValueError('Maximum 50 submissions allowed per batch')
        return v
    
    class Config:
        schema_extra = {
            "example": {
                "submissions": [
                    {
                        "student_id": "student1",
                        "assignment_id": "python_basic_001",
                        "assignment_description": "计算两个数的和",
                        "code": "a = 5\nb = 3\nprint(a + b)",
                        "language": "python"
                    },
                    {
                        "student_id": "student2", 
                        "assignment_id": "python_basic_001",
                        "assignment_description": "计算两个数的和",
                        "code": "x = int(input())\ny = int(input())\nprint(x + y)",
                        "language": "python"
                    }
                ]
            }
        }


class SubmissionStats(BaseModel):
    """提交统计模式"""
    total_submissions: int = Field(..., description="总提交数")
    submissions_by_language: Dict[str, int] = Field(..., description="按语言统计")
    submissions_by_status: Dict[str, int] = Field(..., description="按状态统计")
    average_processing_time: float = Field(..., description="平均处理时间")
    success_rate: float = Field(..., description="成功率")
    recent_submissions: List[SubmissionListResponse] = Field(..., description="最近提交")
    
    class Config:
        schema_extra = {
            "example": {
                "total_submissions": 150,
                "submissions_by_language": {
                    "python": 80,
                    "c": 30,
                    "java": 25,
                    "javascript": 15
                },
                "submissions_by_status": {
                    "analyzed": 140,
                    "analyzing": 5,
                    "failed": 5
                },
                "average_processing_time": 1.5,
                "success_rate": 0.93,
                "recent_submissions": []
            }
        }


class CodeExecutionResult(BaseModel):
    """代码执行结果模式"""
    success: bool = Field(..., description="是否执行成功")
    output: Optional[str] = Field(None, description="执行输出")
    error: Optional[str] = Field(None, description="错误信息")
    execution_time: float = Field(..., description="执行时间（秒）")
    memory_usage: Optional[int] = Field(None, description="内存使用（字节）")
    
    class Config:
        schema_extra = {
            "example": {
                "success": True,
                "output": "2\n4\n6\n8\n10\n",
                "error": None,
                "execution_time": 0.05,
                "memory_usage": 1024
            }
        }


class SubmissionFilter(BaseModel):
    """提交筛选模式"""
    assignment_id: Optional[str] = Field(None, description="作业ID")
    language: Optional[ProgrammingLanguage] = Field(None, description="编程语言")
    status: Optional[SubmissionStatus] = Field(None, description="提交状态")
    student_id: Optional[str] = Field(None, description="学生ID（教师可用）")
    start_date: Optional[datetime] = Field(None, description="开始日期")
    end_date: Optional[datetime] = Field(None, description="结束日期")
    min_score: Optional[float] = Field(None, ge=0, le=100, description="最低分数")
    max_score: Optional[float] = Field(None, ge=0, le=100, description="最高分数")
    
    @validator('end_date')
    def validate_date_range(cls, v, values):
        """验证日期范围"""
        if v and 'start_date' in values and values['start_date']:
            if v < values['start_date']:
                raise ValueError('End date cannot be before start date')
        return v
    
    @validator('max_score')
    def validate_score_range(cls, v, values):
        """验证分数范围"""
        if v and 'min_score' in values and values['min_score']:
            if v < values['min_score']:
                raise ValueError('Max score cannot be less than min score')
        return v


class SubmissionComparison(BaseModel):
    """提交对比模式"""
    submission_ids: List[str] = Field(..., description="要对比的提交ID列表")
    comparison_type: str = Field("detailed", description="对比类型")
    
    @validator('submission_ids')
    def validate_submission_ids(cls, v):
        """验证提交ID列表"""
        if len(v) < 2:
            raise ValueError('At least 2 submissions are required for comparison')
        if len(v) > 5:
            raise ValueError('Maximum 5 submissions allowed for comparison')
        return v


class SubmissionComparisonResult(BaseModel):
    """提交对比结果模式"""
    submissions: List[SubmissionResponse] = Field(..., description="提交详情")
    similarities: Dict[str, float] = Field(..., description="相似度分析")
    differences: List[Dict[str, Any]] = Field(..., description="差异分析")
    recommendations: List[str] = Field(..., description="改进建议")


# 导出所有模式
__all__ = [
    "ProgrammingLanguage",
    "SubmissionStatus", 
    "SubmissionCreate",
    "SubmissionUpdate",
    "SubmissionResponse",
    "SubmissionListResponse",
    "BatchSubmissionItem",
    "BatchSubmissionRequest",
    "SubmissionStats",
    "CodeExecutionResult",
    "SubmissionFilter",
    "SubmissionComparison",
    "SubmissionComparisonResult"
]