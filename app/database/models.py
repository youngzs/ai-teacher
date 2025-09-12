"""
AI教学助手系统 - 数据库模型定义
定义所有数据表的SQLAlchemy模型

Author: AI Backend Architecture Expert
Date: 2025-09-10
"""

from sqlalchemy import Column, String, DateTime, Float, Integer, Text, Boolean, JSON, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func, text
from datetime import datetime
import uuid

from .database import Base


class User(Base):
    """用户表模型"""
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(100), nullable=True)
    role = Column(String(20), nullable=False, default="student")  # student, teacher, admin
    is_active = Column(Boolean, default=True, nullable=False)
    
    # 时间戳
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_login_at = Column(DateTime(timezone=True))
    
    # 用户配置
    preferences = Column(JSONB, default={})  # 用户偏好设置
    profile_data = Column(JSONB, default={})  # 额外的用户信息
    
    # 关系定义
    submissions = relationship("Submission", back_populates="student", cascade="all, delete-orphan")
    classes_taught = relationship("Class", back_populates="teacher", foreign_keys="Class.teacher_id")
    class_memberships = relationship("ClassMembership", back_populates="student")
    
    # 索引
    __table_args__ = (
        Index('idx_user_email_active', 'email', 'is_active'),
        Index('idx_user_role_active', 'role', 'is_active'),
    )


class Class(Base):
    """班级表模型"""
    __tablename__ = "classes"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    teacher_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    course_code = Column(String(20), nullable=True)  # 课程代码
    semester = Column(String(20), nullable=True)     # 学期
    academic_year = Column(String(10), nullable=True)  # 学年
    
    # 班级设置
    settings = Column(JSONB, default={})  # 班级配置
    is_active = Column(Boolean, default=True, nullable=False)
    
    # 时间戳
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # 关系定义
    teacher = relationship("User", back_populates="classes_taught", foreign_keys=[teacher_id])
    memberships = relationship("ClassMembership", back_populates="class_obj", cascade="all, delete-orphan")
    assignments = relationship("Assignment", back_populates="class_obj", cascade="all, delete-orphan")


class ClassMembership(Base):
    """班级成员关系表"""
    __tablename__ = "class_memberships"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    class_id = Column(UUID(as_uuid=True), ForeignKey("classes.id"), nullable=False)
    student_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    
    # 成员信息
    role = Column(String(20), default="student")  # student, assistant
    joined_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    
    # 关系定义
    class_obj = relationship("Class", back_populates="memberships")
    student = relationship("User", back_populates="class_memberships")
    
    # 约束
    __table_args__ = (
        Index('idx_class_student', 'class_id', 'student_id', unique=True),
    )


class Assignment(Base):
    """作业表模型"""
    __tablename__ = "assignments"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=False)
    class_id = Column(UUID(as_uuid=True), ForeignKey("classes.id"), nullable=False)
    
    # 作业配置
    language = Column(String(20), nullable=False)  # 编程语言
    difficulty_level = Column(String(20), nullable=True)  # 难度级别
    estimated_time = Column(String(50), nullable=True)  # 预计完成时间
    
    # 作业内容
    requirements = Column(JSONB, default={})  # 作业要求
    test_cases = Column(JSONB, default=[])    # 测试用例
    grading_rubric = Column(JSONB, default={})  # 评分标准
    
    # 时间设置
    due_date = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # 状态
    is_active = Column(Boolean, default=True, nullable=False)
    
    # 关系定义
    class_obj = relationship("Class", back_populates="assignments")
    submissions = relationship("Submission", back_populates="assignment", cascade="all, delete-orphan")


class Submission(Base):
    """代码提交表模型"""
    __tablename__ = "submissions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    student_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    assignment_id = Column(UUID(as_uuid=True), ForeignKey("assignments.id"), nullable=True)  # 可为空，支持自由提交
    
    # 提交内容
    assignment_description = Column(Text, nullable=False)  # 作业描述
    code = Column(Text, nullable=False)  # 代码内容
    language = Column(String(20), nullable=False)  # 编程语言
    student_message = Column(Text, nullable=True)  # 学生留言
    
    # 状态信息
    status = Column(String(20), default="submitted", nullable=False)  # submitted, analyzing, analyzed, failed
    version = Column(Integer, default=1, nullable=False)  # 提交版本号
    
    # 时间戳
    submitted_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    processed_at = Column(DateTime(timezone=True), nullable=True)  # AI处理完成时间
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # 关系定义
    student = relationship("User", back_populates="submissions")
    assignment = relationship("Assignment", back_populates="submissions")
    ai_feedback = relationship("AIFeedback", back_populates="submission", cascade="all, delete-orphan")
    
    # 索引
    __table_args__ = (
        Index('idx_submission_student_time', 'student_id', 'submitted_at'),
        Index('idx_submission_assignment', 'assignment_id', 'submitted_at'),
        Index('idx_submission_status', 'status', 'submitted_at'),
    )


class AIFeedback(Base):
    """AI反馈表模型"""
    __tablename__ = "ai_feedback"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    submission_id = Column(UUID(as_uuid=True), ForeignKey("submissions.id"), nullable=False)
    
    # AI分析结果
    overall_score = Column(Float, nullable=False, default=0.0)  # 总体评分 (0-100)
    analysis_result = Column(JSONB, nullable=False, default={})  # 完整的AI分析结果
    
    # 反馈状态
    status = Column(String(20), default="processing", nullable=False)  # processing, completed, failed
    error_message = Column(Text, nullable=True)  # 错误信息
    
    # 性能指标
    processing_time = Column(Float, nullable=True)  # 处理时间（秒）
    ai_model_version = Column(String(50), nullable=True)  # AI模型版本
    
    # 时间戳
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # 关系定义
    submission = relationship("Submission", back_populates="ai_feedback")
    
    # 索引
    __table_args__ = (
        Index('idx_feedback_submission', 'submission_id', 'created_at'),
        Index('idx_feedback_status', 'status', 'created_at'),
        Index('idx_feedback_score', 'overall_score'),
    )


class StudentProfile(Base):
    """学生画像表模型"""
    __tablename__ = "student_profiles"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    student_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, unique=True)
    
    # 能力评估
    competency_level = Column(String(20), nullable=False, default="novice")  # 技能水平
    skill_scores = Column(JSONB, default={})  # 各项技能得分
    
    # 学习特征
    learning_style = Column(JSONB, default={})  # 学习风格
    error_patterns = Column(JSONB, default={})  # 错误模式
    emotional_state = Column(JSONB, default={})  # 情感状态
    
    # 历史记录
    learning_history = Column(JSONB, default=[])  # 学习历史
    progress_trends = Column(JSONB, default={})  # 进步趋势
    
    # 统计信息
    total_submissions = Column(Integer, default=0, nullable=False)
    average_score = Column(Float, default=0.0, nullable=False)
    improvement_rate = Column(Float, default=0.0, nullable=False)
    
    # 时间戳
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_analyzed = Column(DateTime(timezone=True), nullable=True)
    
    # 关系定义
    student = relationship("User")


class TeachingSession(Base):
    """教学会话表模型"""
    __tablename__ = "teaching_sessions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    student_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    session_type = Column(String(30), nullable=False)  # assignment, debugging, personalized
    
    # 会话数据
    input_data = Column(JSONB, nullable=False, default={})  # 输入数据
    ai_response = Column(JSONB, nullable=False, default={})  # AI响应
    workflow_result = Column(JSONB, nullable=True, default={})  # 工作流结果
    
    # 会话状态
    status = Column(String(20), default="active", nullable=False)  # active, completed, failed
    quality_score = Column(Float, nullable=True)  # 质量评分
    
    # 性能指标
    response_time = Column(Float, nullable=True)  # 响应时间
    agent_interactions = Column(JSONB, default=[])  # Agent交互记录
    
    # 时间戳
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # 索引
    __table_args__ = (
        Index('idx_session_student_type', 'student_id', 'session_type', 'created_at'),
        Index('idx_session_status', 'status', 'created_at'),
    )


class SystemMetrics(Base):
    """系统指标表模型"""
    __tablename__ = "system_metrics"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    metric_type = Column(String(50), nullable=False)  # performance, usage, error, quality
    metric_name = Column(String(100), nullable=False)
    
    # 指标数据
    value = Column(Float, nullable=False)
    unit = Column(String(20), nullable=True)
    extra_data = Column(JSONB, default={})  # 额外的元数据
    
    # 时间戳
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # 索引
    __table_args__ = (
        Index('idx_metrics_type_name', 'metric_type', 'metric_name', 'timestamp'),
        Index('idx_metrics_timestamp', 'timestamp'),
    )


class APIKey(Base):
    """API密钥表模型"""
    __tablename__ = "api_keys"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    
    # 密钥信息
    name = Column(String(100), nullable=False)  # 密钥名称
    key_hash = Column(String(255), nullable=False, unique=True)  # 密钥哈希
    prefix = Column(String(20), nullable=False)  # 密钥前缀（用于识别）
    
    # 权限和限制
    permissions = Column(JSONB, default=[])  # 权限列表
    rate_limit = Column(Integer, nullable=True)  # 速率限制
    
    # 状态
    is_active = Column(Boolean, default=True, nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=True)
    last_used_at = Column(DateTime(timezone=True), nullable=True)
    
    # 统计
    usage_count = Column(Integer, default=0, nullable=False)
    
    # 时间戳
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # 关系定义
    user = relationship("User")


class AuditLog(Base):
    """审计日志表模型"""
    __tablename__ = "audit_logs"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)  # 可为空，支持系统操作
    
    # 操作信息
    action = Column(String(100), nullable=False)  # 操作类型
    resource_type = Column(String(50), nullable=False)  # 资源类型
    resource_id = Column(UUID(as_uuid=True), nullable=True)  # 资源ID
    
    # 详细信息
    details = Column(JSONB, default={})  # 操作详情
    ip_address = Column(String(45), nullable=True)  # IP地址
    user_agent = Column(String(500), nullable=True)  # 用户代理
    
    # 结果
    success = Column(Boolean, nullable=False, default=True)
    error_message = Column(Text, nullable=True)
    
    # 时间戳
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # 关系定义
    user = relationship("User")
    
    # 索引
    __table_args__ = (
        Index('idx_audit_user_time', 'user_id', 'timestamp'),
        Index('idx_audit_action', 'action', 'timestamp'),
        Index('idx_audit_resource', 'resource_type', 'resource_id', 'timestamp'),
    )


class Course(Base):
    """课程表模型"""
    __tablename__ = "courses"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), nullable=False)  # 课程名称
    code = Column(String(20), nullable=True)    # 课程代码
    language = Column(String(20), nullable=False)  # 编程语言 (C, Python)
    
    # 课程信息
    description = Column(Text, nullable=True)
    total_hours = Column(Integer, nullable=False, default=0)  # 总课时
    difficulty_level = Column(String(20), nullable=True)  # 难度等级
    prerequisites = Column(JSONB, default=[])  # 先修课程
    
    # 课程结构化数据
    curriculum_data = Column(JSONB, default={})  # 课程大纲
    learning_objectives = Column(JSONB, default=[])  # 学习目标
    
    # 状态
    is_active = Column(Boolean, default=True, nullable=False)
    
    # 时间戳
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # 关系定义
    lessons = relationship("Lesson", back_populates="course", cascade="all, delete-orphan")
    learning_paths = relationship("LearningPath", back_populates="course", cascade="all, delete-orphan")
    course_exercises = relationship("CourseExercise", back_populates="course", cascade="all, delete-orphan")
    
    # 索引
    __table_args__ = (
        Index('idx_course_language', 'language', 'is_active'),
        Index('idx_course_difficulty', 'difficulty_level', 'is_active'),
    )


class Lesson(Base):
    """课时表模型"""
    __tablename__ = "lessons"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    course_id = Column(UUID(as_uuid=True), ForeignKey("courses.id"), nullable=False)
    
    # 课时基本信息
    lesson_number = Column(Integer, nullable=False)  # 课时序号
    title = Column(String(200), nullable=False)      # 课时标题
    subtitle = Column(String(300), nullable=True)    # 子标题
    duration = Column(Integer, nullable=True)        # 课时时长(分钟)
    
    # 课时内容
    content = Column(Text, nullable=True)            # 课时内容
    learning_objectives = Column(JSONB, default=[])  # 学习目标
    key_concepts = Column(JSONB, default=[])         # 关键概念
    
    # 教学结构化数据
    teaching_structure = Column(JSONB, default={})   # 教学结构
    ai_support_strategies = Column(JSONB, default={})  # AI支持策略
    
    # 状态
    is_active = Column(Boolean, default=True, nullable=False)
    
    # 时间戳
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # 关系定义
    course = relationship("Course", back_populates="lessons")
    lesson_exercises = relationship("LessonExercise", back_populates="lesson", cascade="all, delete-orphan")
    
    # 索引
    __table_args__ = (
        Index('idx_lesson_course_number', 'course_id', 'lesson_number', unique=True),
        Index('idx_lesson_active', 'is_active', 'lesson_number'),
    )


class CourseExercise(Base):
    """课程练习表模型"""
    __tablename__ = "course_exercises"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    course_id = Column(UUID(as_uuid=True), ForeignKey("courses.id"), nullable=False)
    
    # 练习基本信息
    exercise_number = Column(String(20), nullable=False)  # 练习编号 (如: 1.1, 2.3)
    title = Column(String(200), nullable=False)
    exercise_type = Column(String(30), nullable=False)   # 练习类型: choice, coding, essay
    difficulty_level = Column(Integer, nullable=False, default=1)  # 难度级别 1-5
    
    # 练习内容
    question = Column(Text, nullable=False)              # 题目内容
    options = Column(JSONB, default=[])                  # 选择题选项
    correct_answer = Column(Text, nullable=True)         # 正确答案
    sample_code = Column(Text, nullable=True)            # 示例代码
    
    # 教学设计
    knowledge_points = Column(JSONB, default=[])         # 知识点
    ai_feedback_config = Column(JSONB, default={})       # AI反馈配置
    teaching_hints = Column(JSONB, default=[])           # 教学提示
    
    # 状态
    is_active = Column(Boolean, default=True, nullable=False)
    
    # 时间戳
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # 关系定义
    course = relationship("Course", back_populates="course_exercises")
    
    # 索引
    __table_args__ = (
        Index('idx_exercise_course_number', 'course_id', 'exercise_number'),
        Index('idx_exercise_type_difficulty', 'exercise_type', 'difficulty_level'),
    )


class LessonExercise(Base):
    """课时练习关联表"""
    __tablename__ = "lesson_exercises"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    lesson_id = Column(UUID(as_uuid=True), ForeignKey("lessons.id"), nullable=False)
    exercise_id = Column(UUID(as_uuid=True), ForeignKey("course_exercises.id"), nullable=False)
    
    # 关联信息
    order_number = Column(Integer, nullable=False, default=1)  # 在课时中的顺序
    is_required = Column(Boolean, default=True, nullable=False)  # 是否必做
    
    # 时间戳
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # 关系定义
    lesson = relationship("Lesson", back_populates="lesson_exercises")
    exercise = relationship("CourseExercise")
    
    # 约束
    __table_args__ = (
        Index('idx_lesson_exercise', 'lesson_id', 'exercise_id', unique=True),
    )


class LearningPath(Base):
    """学习路径表模型"""
    __tablename__ = "learning_paths"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    student_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    course_id = Column(UUID(as_uuid=True), ForeignKey("courses.id"), nullable=False)
    
    # 学习进度
    current_lesson = Column(Integer, nullable=False, default=1)  # 当前课时
    completed_lessons = Column(JSONB, default=[])  # 已完成课时列表
    
    # 学习数据
    progress_percentage = Column(Float, nullable=False, default=0.0)  # 进度百分比
    learning_hours = Column(Float, nullable=False, default=0.0)       # 学习时长
    
    # 个性化数据
    learning_style = Column(JSONB, default={})      # 学习风格偏好
    difficulty_adjustment = Column(Float, default=1.0)  # 难度调整系数
    recommended_exercises = Column(JSONB, default=[])   # 推荐练习
    
    # 状态追踪
    last_study_time = Column(DateTime(timezone=True), nullable=True)
    status = Column(String(20), default="active", nullable=False)  # active, paused, completed
    
    # 时间戳
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # 关系定义
    student = relationship("User")
    course = relationship("Course", back_populates="learning_paths")
    
    # 约束
    __table_args__ = (
        Index('idx_learning_path_student_course', 'student_id', 'course_id', unique=True),
        Index('idx_learning_path_progress', 'progress_percentage', 'status'),
    )


class StudentExerciseAttempt(Base):
    """学生练习尝试记录表"""
    __tablename__ = "student_exercise_attempts"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    student_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    exercise_id = Column(UUID(as_uuid=True), ForeignKey("course_exercises.id"), nullable=False)
    
    # 尝试信息
    attempt_number = Column(Integer, nullable=False, default=1)  # 尝试次数
    student_answer = Column(Text, nullable=False)               # 学生答案
    is_correct = Column(Boolean, nullable=False, default=False) # 是否正确
    score = Column(Float, nullable=False, default=0.0)          # 得分
    
    # AI反馈
    ai_feedback = Column(JSONB, default={})                     # AI反馈内容
    feedback_quality = Column(Float, nullable=True)             # 反馈质量评分
    
    # 学习数据
    time_spent = Column(Integer, nullable=True)                 # 花费时间(秒)
    hint_used = Column(Boolean, default=False, nullable=False)  # 是否使用提示
    
    # 时间戳
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # 关系定义
    student = relationship("User")
    exercise = relationship("CourseExercise")
    
    # 索引
    __table_args__ = (
        Index('idx_attempt_student_exercise', 'student_id', 'exercise_id', 'created_at'),
        Index('idx_attempt_score', 'score', 'is_correct'),
    )


# 视图定义（用于复杂查询）
class StudentStatistics:
    """学生统计信息视图（虚拟模型）"""
    
    @staticmethod
    def get_create_view_sql():
        return """
        CREATE OR REPLACE VIEW student_statistics AS
        SELECT 
            u.id as student_id,
            u.username,
            u.full_name,
            COUNT(s.id) as total_submissions,
            AVG(af.overall_score) as average_score,
            MAX(s.submitted_at) as last_submission,
            COUNT(DISTINCT s.assignment_id) as assignments_completed,
            COUNT(CASE WHEN af.overall_score >= 80 THEN 1 END) as high_score_submissions,
            sp.competency_level,
            sp.improvement_rate
        FROM users u
        LEFT JOIN submissions s ON u.id = s.student_id
        LEFT JOIN ai_feedback af ON s.id = af.submission_id AND af.status = 'completed'
        LEFT JOIN student_profiles sp ON u.id = sp.student_id
        WHERE u.role = 'student' AND u.is_active = true
        GROUP BY u.id, u.username, u.full_name, sp.competency_level, sp.improvement_rate;
        """


# 触发器函数（PostgreSQL）
class DatabaseTriggers:
    """数据库触发器定义"""
    
    @staticmethod
    def get_update_timestamp_trigger():
        """自动更新时间戳的触发器"""
        return """
        CREATE OR REPLACE FUNCTION update_updated_at_column()
        RETURNS TRIGGER AS $$
        BEGIN
            NEW.updated_at = CURRENT_TIMESTAMP;
            RETURN NEW;
        END;
        $$ language 'plpgsql';
        
        -- 为需要的表创建触发器
        DROP TRIGGER IF EXISTS update_users_updated_at ON users;
        CREATE TRIGGER update_users_updated_at 
            BEFORE UPDATE ON users 
            FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
            
        DROP TRIGGER IF EXISTS update_submissions_updated_at ON submissions;
        CREATE TRIGGER update_submissions_updated_at 
            BEFORE UPDATE ON submissions 
            FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
        """
    
    @staticmethod
    def get_audit_trigger():
        """审计日志触发器"""
        return """
        CREATE OR REPLACE FUNCTION audit_changes()
        RETURNS TRIGGER AS $$
        BEGIN
            IF TG_OP = 'INSERT' THEN
                INSERT INTO audit_logs (action, resource_type, resource_id, details, timestamp)
                VALUES (TG_OP, TG_TABLE_NAME, NEW.id, row_to_json(NEW), CURRENT_TIMESTAMP);
                RETURN NEW;
            ELSIF TG_OP = 'UPDATE' THEN
                INSERT INTO audit_logs (action, resource_type, resource_id, details, timestamp)
                VALUES (TG_OP, TG_TABLE_NAME, NEW.id, 
                    json_build_object('old', row_to_json(OLD), 'new', row_to_json(NEW)), 
                    CURRENT_TIMESTAMP);
                RETURN NEW;
            ELSIF TG_OP = 'DELETE' THEN
                INSERT INTO audit_logs (action, resource_type, resource_id, details, timestamp)
                VALUES (TG_OP, TG_TABLE_NAME, OLD.id, row_to_json(OLD), CURRENT_TIMESTAMP);
                RETURN OLD;
            END IF;
            RETURN NULL;
        END;
        $$ language 'plpgsql';
        """