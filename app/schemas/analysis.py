"""
AI教学助手系统 - AI分析相关模式定义
定义AI代码分析、反馈生成等相关的Pydantic模式

Author: AI Backend Architecture Expert
Date: 2025-09-10
"""

from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any, Union
from datetime import datetime
from enum import Enum

from .submissions import ProgrammingLanguage
from .common import validate_non_empty_string


class AnalysisType(str, Enum):
    """分析类型"""
    ASSIGNMENT = "assignment"
    DEBUGGING = "debugging"
    PERSONALIZED = "personalized"
    COMPARISON = "comparison"


class FeedbackStatus(str, Enum):
    """反馈状态"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class AnalysisRequest(BaseModel):
    """AI分析请求模式"""
    code: str = Field(..., min_length=1, description="代码内容")
    language: ProgrammingLanguage = Field(..., description="编程语言")
    analysis_type: AnalysisType = Field(AnalysisType.ASSIGNMENT, description="分析类型")
    
    # 可选参数
    submission_id: Optional[str] = Field(None, description="提交ID")
    assignment_id: Optional[str] = Field(None, description="作业ID")
    assignment_description: Optional[str] = Field(None, description="作业描述")
    student_message: Optional[str] = Field(None, description="学生留言")
    force_reanalyze: bool = Field(False, description="强制重新分析")
    
    @validator('code')
    def validate_code_content(cls, v):
        """验证代码内容"""
        if not v.strip():
            raise ValueError('Code cannot be empty')
        if len(v) > 100000:  # 100KB限制
            raise ValueError('Code is too long for analysis')
        return v
    
    class Config:
        schema_extra = {
            "example": {
                "code": "def fibonacci(n):\n    if n <= 1:\n        return n\n    return fibonacci(n-1) + fibonacci(n-2)\n\nprint(fibonacci(10))",
                "language": "python",
                "analysis_type": "assignment",
                "assignment_description": "实现斐波那契数列函数",
                "student_message": "这个递归实现对吗？"
            }
        }


class CodeError(BaseModel):
    """代码错误模式"""
    error_type: str = Field(..., description="错误类型")
    line_number: int = Field(..., description="错误行号")
    column_number: Optional[int] = Field(None, description="错误列号")
    severity: str = Field(..., description="严重程度")
    description: str = Field(..., description="错误描述")
    suggestion: str = Field(..., description="修复建议")
    code_snippet: Optional[str] = Field(None, description="错误代码片段")
    
    class Config:
        schema_extra = {
            "example": {
                "error_type": "logic",
                "line_number": 5,
                "column_number": 12,
                "severity": "medium",
                "description": "可能导致栈溢出的递归调用",
                "suggestion": "考虑使用动态规划或迭代方法",
                "code_snippet": "return fibonacci(n-1) + fibonacci(n-2)"
            }
        }


class CodeSuggestion(BaseModel):
    """代码建议模式"""
    category: str = Field(..., description="建议类别")
    priority: str = Field(..., description="优先级")
    title: str = Field(..., description="建议标题")
    description: str = Field(..., description="详细描述")
    example_code: Optional[str] = Field(None, description="示例代码")
    learning_resource: Optional[str] = Field(None, description="学习资源链接")


class AnalysisResponse(BaseModel):
    """AI分析响应模式"""
    submission_id: str = Field(..., description="提交ID")
    analysis_id: str = Field(..., description="分析ID")
    status: FeedbackStatus = Field(..., description="分析状态")
    overall_score: float = Field(..., ge=0, le=100, description="总体评分")
    analysis_result: Dict[str, Any] = Field(..., description="完整分析结果")
    created_at: datetime = Field(..., description="分析时间")
    processing_time: float = Field(..., description="处理时间（秒）")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
        schema_extra = {
            "example": {
                "submission_id": "submission-uuid",
                "analysis_id": "analysis-uuid",
                "status": "completed",
                "overall_score": 85.0,
                "analysis_result": {
                    "syntax_score": 95,
                    "logic_score": 80,
                    "style_score": 85,
                    "performance_score": 70,
                    "errors": [],
                    "suggestions": [],
                    "strengths": ["正确的语法", "清晰的变量命名"]
                },
                "created_at": "2023-09-10T10:00:00",
                "processing_time": 1.5
            }
        }


class FeedbackResponse(BaseModel):
    """反馈响应模式"""
    feedback_id: str = Field(..., description="反馈ID")
    submission_id: str = Field(..., description="提交ID")
    overall_score: float = Field(..., ge=0, le=100, description="总体评分")
    analysis_result: Dict[str, Any] = Field(..., description="分析结果")
    status: FeedbackStatus = Field(..., description="反馈状态")
    created_at: datetime = Field(..., description="创建时间")
    processing_time: Optional[float] = Field(None, description="处理时间")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class DebuggingRequest(BaseModel):
    """调试请求模式"""
    code: str = Field(..., min_length=1, description="代码内容")
    language: ProgrammingLanguage = Field(..., description="编程语言")
    problem_description: str = Field(..., description="问题描述")
    specific_issue: Optional[str] = Field(None, description="具体问题")
    expected_behavior: Optional[str] = Field(None, description="期望行为")
    actual_behavior: Optional[str] = Field(None, description="实际行为")
    
    @validator('code')
    def validate_code_content(cls, v):
        """验证代码内容"""
        if not v.strip():
            raise ValueError('Code cannot be empty')
        return v
    
    @validator('problem_description')
    def validate_problem_description(cls, v):
        """验证问题描述"""
        return validate_non_empty_string(v)
    
    class Config:
        schema_extra = {
            "example": {
                "code": "def divide(a, b):\n    return a / b\n\nresult = divide(10, 0)\nprint(result)",
                "language": "python",
                "problem_description": "程序运行时出现错误",
                "specific_issue": "除零错误",
                "expected_behavior": "应该处理除零的情况",
                "actual_behavior": "程序崩溃并显示ZeroDivisionError"
            }
        }


class DebuggingResponse(BaseModel):
    """调试响应模式"""
    session_id: str = Field(..., description="调试会话ID")
    debugging_guidance: Dict[str, Any] = Field(..., description="调试指导")
    errors_found: int = Field(..., description="发现的错误数量")
    suggestions_count: int = Field(..., description="建议数量")
    processing_time: float = Field(..., description="处理时间")
    next_steps: List[str] = Field(..., description="下一步建议")
    
    class Config:
        schema_extra = {
            "example": {
                "session_id": "debug-session-uuid",
                "debugging_guidance": {
                    "errors_identified": ["除零错误"],
                    "root_cause": "未检查除数是否为零",
                    "fix_suggestions": ["添加条件检查", "使用异常处理"],
                    "learning_points": ["异常处理的重要性", "边界条件检查"]
                },
                "errors_found": 1,
                "suggestions_count": 3,
                "processing_time": 0.8,
                "next_steps": [
                    "添加if语句检查除数",
                    "学习try-except异常处理",
                    "测试边界情况"
                ]
            }
        }


class BatchAnalysisRequest(BaseModel):
    """批量分析请求模式"""
    submission_ids: List[str] = Field(..., description="提交ID列表")
    analysis_type: AnalysisType = Field(AnalysisType.ASSIGNMENT, description="分析类型")
    priority: str = Field("normal", description="处理优先级")
    
    @validator('submission_ids')
    def validate_submission_ids(cls, v):
        """验证提交ID列表"""
        if len(v) == 0:
            raise ValueError('At least one submission ID is required')
        if len(v) > 20:
            raise ValueError('Maximum 20 submissions allowed per batch')
        return v
    
    class Config:
        schema_extra = {
            "example": {
                "submission_ids": ["uuid1", "uuid2", "uuid3"],
                "analysis_type": "assignment",
                "priority": "high"
            }
        }


class StudentInsights(BaseModel):
    """学生学习洞察模式"""
    student_id: str = Field(..., description="学生ID")
    competency_assessment: Dict[str, Any] = Field(..., description="能力评估")
    learning_patterns: Dict[str, Any] = Field(..., description="学习模式")
    improvement_suggestions: List[str] = Field(..., description="改进建议")
    skill_gaps: Dict[str, float] = Field(..., description="技能缺口")
    progress_trends: Dict[str, Any] = Field(..., description="进步趋势")
    generated_at: datetime = Field(default_factory=datetime.utcnow, description="生成时间")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
        schema_extra = {
            "example": {
                "student_id": "student-uuid",
                "competency_assessment": {
                    "level": "competent",
                    "average_score": 78.5,
                    "confidence": 0.85
                },
                "learning_patterns": {
                    "pattern": "improving",
                    "consistency": "high"
                },
                "improvement_suggestions": [
                    "加强算法思维训练",
                    "多练习异常处理"
                ],
                "skill_gaps": {
                    "syntax": 0.9,
                    "logic": 0.7,
                    "style": 0.8
                },
                "progress_trends": {
                    "trend": "improving",
                    "recent_average": 82.0,
                    "overall_average": 75.5
                },
                "generated_at": "2023-09-10T10:00:00"
            }
        }


class QualityMetrics(BaseModel):
    """质量指标模式"""
    code_quality_score: float = Field(..., ge=0, le=100, description="代码质量分数")
    maintainability: float = Field(..., ge=0, le=100, description="可维护性")
    readability: float = Field(..., ge=0, le=100, description="可读性")
    performance: float = Field(..., ge=0, le=100, description="性能")
    security: float = Field(..., ge=0, le=100, description="安全性")
    test_coverage: Optional[float] = Field(None, ge=0, le=100, description="测试覆盖率")
    complexity_score: float = Field(..., ge=0, le=100, description="复杂度分数")


class LearningResource(BaseModel):
    """学习资源模式"""
    resource_type: str = Field(..., description="资源类型")
    title: str = Field(..., description="资源标题")
    description: str = Field(..., description="资源描述")
    url: Optional[str] = Field(None, description="资源链接")
    difficulty: str = Field(..., description="难度等级")
    estimated_time: Optional[str] = Field(None, description="预计学习时间")
    tags: List[str] = Field([], description="标签")


class PersonalizedFeedback(BaseModel):
    """个性化反馈模式"""
    recognition: str = Field(..., description="认可和鼓励")
    reflection: str = Field(..., description="问题反思引导")
    reconstruction: Dict[str, Any] = Field(..., description="重构指导")
    resources: List[LearningResource] = Field(..., description="推荐资源")
    reinforcement: str = Field(..., description="强化鼓励")
    next_challenges: List[str] = Field([], description="下一步挑战")


class AnalysisComparison(BaseModel):
    """分析对比模式"""
    submissions: List[str] = Field(..., description="对比的提交ID")
    comparison_metrics: Dict[str, Any] = Field(..., description="对比指标")
    similarities: Dict[str, float] = Field(..., description="相似度分析")
    differences: List[Dict[str, Any]] = Field(..., description="差异分析")
    improvement_trajectory: Dict[str, Any] = Field(..., description="改进轨迹")


# 导出所有模式
__all__ = [
    "AnalysisType",
    "FeedbackStatus",
    "AnalysisRequest",
    "CodeError",
    "CodeSuggestion", 
    "AnalysisResponse",
    "FeedbackResponse",
    "DebuggingRequest",
    "DebuggingResponse",
    "BatchAnalysisRequest",
    "StudentInsights",
    "QualityMetrics",
    "LearningResource",
    "PersonalizedFeedback",
    "AnalysisComparison"
]