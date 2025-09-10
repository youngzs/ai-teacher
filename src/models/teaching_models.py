"""
AI教学助手系统 - 数据模型定义
定义系统中使用的各种数据结构和模型

Author: AI Architecture Expert
Date: 2025-09-09  
"""

from typing import Dict, List, Any, Optional, Union
from datetime import datetime
from dataclasses import dataclass, field, asdict
from enum import Enum
import json

class ProgrammingLanguage(Enum):
    """支持的编程语言"""
    PYTHON = "python"
    C = "c"
    JAVA = "java"
    JAVASCRIPT = "javascript"
    CPP = "cpp"

class DifficultyLevel(Enum):
    """难度等级"""
    NOVICE = "novice"
    ADVANCED_BEGINNER = "advanced_beginner"
    COMPETENT = "competent"
    PROFICIENT = "proficient"
    EXPERT = "expert"

class LearningStyle(Enum):
    """学习风格类型（基于VARK模型）"""
    VISUAL = "visual"
    AUDITORY = "auditory" 
    READING_WRITING = "reading_writing"
    KINESTHETIC = "kinesthetic"

class TeachingStrategy(Enum):
    """教学策略类型"""
    ENCOURAGE = "encourage"
    HINT = "hint"
    REFINE = "refine"
    CHALLENGE = "challenge"
    EXPLAIN = "explain"
    DEBUGGING = "debugging"
    PERSONALIZED = "personalized"

class ErrorType(Enum):
    """错误类型分类"""
    SYNTAX = "syntax"
    LOGIC = "logic"
    RUNTIME = "runtime"
    STYLE = "style"
    PERFORMANCE = "performance"

@dataclass
class StudentProfile:
    """学生画像数据模型"""
    student_id: str
    competency_level: DifficultyLevel
    skill_scores: Dict[str, int]  # {"syntax": 75, "algorithm": 60, "debugging": 50, "style": 65}
    learning_style: Dict[str, str]  # {"primary": "visual", "secondary": "kinesthetic"}
    error_patterns: Dict[str, Any]  # {"most_common": ["loop_boundary", "variable_scope"]}
    emotional_state: Dict[str, int]  # {"confidence": 70, "motivation": 85, "frustration": 30}
    learning_history: List[Dict[str, Any]] = field(default_factory=list)
    last_updated: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        data = asdict(self)
        data['competency_level'] = self.competency_level.value
        data['last_updated'] = self.last_updated.isoformat()
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'StudentProfile':
        """从字典创建实例"""
        data['competency_level'] = DifficultyLevel(data['competency_level'])
        data['last_updated'] = datetime.fromisoformat(data['last_updated'])
        return cls(**data)

@dataclass
class CodeError:
    """代码错误信息模型"""
    error_type: ErrorType
    line_number: int
    description: str
    severity: str  # "high", "medium", "low"
    suggestion: str
    code_snippet: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            "error_type": self.error_type.value,
            "line_number": self.line_number,
            "description": self.description,
            "severity": self.severity,
            "suggestion": self.suggestion,
            "code_snippet": self.code_snippet
        }

@dataclass 
class SubmissionData:
    """学生作业提交数据模型"""
    student_id: str
    assignment_id: str
    assignment_description: str
    code: str
    language: ProgrammingLanguage
    submitted_at: datetime
    student_history: Dict[str, Any] = field(default_factory=dict)
    test_results: Optional[Dict[str, Any]] = None
    student_message: Optional[str] = None  # 学生的问题或说明
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        data = asdict(self)
        data['language'] = self.language.value
        data['submitted_at'] = self.submitted_at.isoformat()
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SubmissionData':
        """从字典创建实例"""
        data['language'] = ProgrammingLanguage(data['language'])
        data['submitted_at'] = datetime.fromisoformat(data['submitted_at'])
        return cls(**data)

@dataclass
class AnalysisResult:
    """代码分析结果模型"""
    syntax_score: int
    logic_score: int
    quality_score: int
    performance_score: int
    critical_errors: List[CodeError]
    suggestions: List[str]
    strengths: List[str]
    complexity_analysis: str
    execution_successful: bool
    execution_output: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            "syntax_score": self.syntax_score,
            "logic_score": self.logic_score,
            "quality_score": self.quality_score,
            "performance_score": self.performance_score,
            "critical_errors": [error.to_dict() for error in self.critical_errors],
            "suggestions": self.suggestions,
            "strengths": self.strengths,
            "complexity_analysis": self.complexity_analysis,
            "execution_successful": self.execution_successful,
            "execution_output": self.execution_output
        }

@dataclass
class LearningResource:
    """学习资源模型"""
    resource_type: str  # "concept", "example", "tutorial", "tool", "reference"
    title: str
    description: str
    url: Optional[str] = None
    difficulty: Optional[DifficultyLevel] = None
    estimated_time: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            "resource_type": self.resource_type,
            "title": self.title,
            "description": self.description,
            "url": self.url,
            "difficulty": self.difficulty.value if self.difficulty else None,
            "estimated_time": self.estimated_time
        }

@dataclass
class FeedbackContent:
    """反馈内容模型（基于5R模型）"""
    recognition: str  # Recognition - 认可和鼓励
    reflection: str  # Reflection - 问题反思引导
    reconstruction: Dict[str, Any]  # Reconstruction - 重构指导
    resources: List[LearningResource]  # Resources - 资源推荐
    reinforcement: str  # Reinforcement - 鼓励强化
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            "recognition": self.recognition,
            "reflection": self.reflection,
            "reconstruction": self.reconstruction,
            "resources": [resource.to_dict() for resource in self.resources],
            "reinforcement": self.reinforcement
        }

@dataclass
class TeachingFeedback:
    """完整的教学反馈模型"""
    session_id: str
    student_id: str
    overall_score: float
    code_analysis: Dict[str, Any]
    student_profile: Dict[str, Any]
    teaching_strategy: str
    feedback_content: Dict[str, Any]
    recommendations: Dict[str, Any]
    quality_score: int
    next_steps: List[str]
    estimated_completion_time: str
    created_at: datetime
    reviewed_by_teacher: bool = False
    teacher_modifications: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            "session_id": self.session_id,
            "student_id": self.student_id,
            "overall_score": self.overall_score,
            "code_analysis": self.code_analysis,
            "student_profile": self.student_profile,
            "teaching_strategy": self.teaching_strategy,
            "feedback_content": self.feedback_content,
            "recommendations": self.recommendations,
            "quality_score": self.quality_score,
            "next_steps": self.next_steps,
            "estimated_completion_time": self.estimated_completion_time,
            "created_at": self.created_at.isoformat(),
            "reviewed_by_teacher": self.reviewed_by_teacher,
            "teacher_modifications": self.teacher_modifications
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TeachingFeedback':
        """从字典创建实例"""
        data['created_at'] = datetime.fromisoformat(data['created_at'])
        return cls(**data)

@dataclass
class ClassroomMetrics:
    """班级整体指标模型"""
    class_id: str
    student_count: int
    average_score: float
    common_errors: List[Dict[str, Any]]
    skill_distribution: Dict[str, int]  # {"novice": 15, "advanced_beginner": 20, ...}
    progress_trends: Dict[str, List[float]]  # 时间序列数据
    teacher_interventions: List[Dict[str, Any]]
    last_updated: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        data = asdict(self)
        data['last_updated'] = self.last_updated.isoformat()
        return data

@dataclass
class AssignmentTemplate:
    """作业模板模型"""
    assignment_id: str
    title: str
    description: str
    language: ProgrammingLanguage
    difficulty_level: DifficultyLevel
    learning_objectives: List[str]
    test_cases: List[Dict[str, Any]]
    expected_concepts: List[str]  # 期望学生掌握的概念
    common_mistakes: List[str]  # 常见错误
    grading_rubric: Dict[str, Any]
    estimated_time: str
    created_at: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        data = asdict(self)
        data['language'] = self.language.value
        data['difficulty_level'] = self.difficulty_level.value
        data['created_at'] = self.created_at.isoformat()
        return data

@dataclass
class SystemPerformanceMetrics:
    """系统性能指标模型"""
    timestamp: datetime
    average_response_time: float  # 秒
    feedback_accuracy_rate: float  # 0.0-1.0
    system_availability: float  # 0.0-1.0
    concurrent_users: int
    total_submissions_processed: int
    error_rate: float  # 0.0-1.0
    agent_performance: Dict[str, Dict[str, float]]  # 各Agent的性能指标
    resource_utilization: Dict[str, float]  # CPU、内存等资源使用率
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        data = asdict(self)
        data['timestamp'] = self.timestamp.isoformat()
        return data

# 工具类和辅助函数

class ModelEncoder(json.JSONEncoder):
    """自定义JSON编码器，处理数据模型的序列化"""
    
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        elif isinstance(obj, (DifficultyLevel, ProgrammingLanguage, LearningStyle, TeachingStrategy, ErrorType)):
            return obj.value
        elif hasattr(obj, 'to_dict'):
            return obj.to_dict()
        return super().default(obj)

def serialize_model(model: Any) -> str:
    """序列化数据模型为JSON字符串"""
    return json.dumps(model, cls=ModelEncoder, ensure_ascii=False, indent=2)

def create_sample_submission() -> SubmissionData:
    """创建示例提交数据，用于测试"""
    return SubmissionData(
        student_id="student_001",
        assignment_id="python_loops_001", 
        assignment_description="编写一个程序，使用for循环打印1到10的所有偶数",
        code="""
# 学生的代码提交
for i in range(1, 11):
    if i % 2 == 0:
        print(i)
""",
        language=ProgrammingLanguage.PYTHON,
        submitted_at=datetime.now(),
        student_history={
            "programming_experience": "beginner",
            "previous_assignments": 3,
            "average_score": 75.5,
            "common_errors": ["syntax", "logic"]
        },
        student_message="我不确定这样写是否正确，请帮我检查一下。"
    )

def create_sample_student_profile() -> StudentProfile:
    """创建示例学生画像，用于测试"""
    return StudentProfile(
        student_id="student_001",
        competency_level=DifficultyLevel.ADVANCED_BEGINNER,
        skill_scores={
            "syntax": 75,
            "algorithm": 60, 
            "debugging": 50,
            "style": 65
        },
        learning_style={
            "primary": "visual",
            "secondary": "kinesthetic"
        },
        error_patterns={
            "most_common": ["loop_boundary", "variable_scope"],
            "frequency": {"syntax": 0.3, "logic": 0.5, "style": 0.2}
        },
        emotional_state={
            "confidence": 70,
            "motivation": 85,
            "frustration": 30,
            "curiosity": 90
        },
        learning_history=[
            {
                "assignment_id": "python_basic_001",
                "score": 80,
                "completion_time": "25分钟",
                "errors": ["syntax"]
            },
            {
                "assignment_id": "python_conditions_001", 
                "score": 75,
                "completion_time": "35分钟",
                "errors": ["logic"]
            }
        ]
    )

# 数据验证函数

def validate_submission_data(data: Dict[str, Any]) -> bool:
    """验证提交数据的完整性和正确性"""
    required_fields = ["student_id", "assignment_id", "assignment_description", "code", "language"]
    
    for field in required_fields:
        if field not in data or not data[field]:
            return False
    
    try:
        ProgrammingLanguage(data["language"])
    except ValueError:
        return False
        
    return True

def validate_student_profile(data: Dict[str, Any]) -> bool:
    """验证学生画像数据的完整性和正确性"""
    required_fields = ["student_id", "competency_level", "skill_scores"]
    
    for field in required_fields:
        if field not in data:
            return False
    
    try:
        DifficultyLevel(data["competency_level"])
    except ValueError:
        return False
    
    return True