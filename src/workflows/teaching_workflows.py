"""
AI教学助手系统 - 教学工作流管理
实现三个核心教学场景的工作流：作业分析、调试辅导、个性化学习

Author: AI Architecture Expert
Date: 2025-09-09
"""

from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
import asyncio
import json
from abc import ABC, abstractmethod

from ..models.teaching_models import SubmissionData, TeachingFeedback, StudentProfile
from ..agents.teaching_agents import MultiAgentTeachingSystem
from ..utils.logger import get_logger, log_agent_activity, log_performance_metric, LogExecutionTime
from ..config.agents_config import SYSTEM_CONFIG

logger = get_logger(__name__)

class WorkflowType(Enum):
    """工作流类型"""
    ASSIGNMENT_ANALYSIS = "assignment_analysis"
    DEBUGGING_GUIDANCE = "debugging_guidance"
    PERSONALIZED_LEARNING = "personalized_learning"
    BATCH_PROCESSING = "batch_processing"

class WorkflowStatus(Enum):
    """工作流状态"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    TIMEOUT = "timeout"

@dataclass
class WorkflowResult:
    """工作流执行结果"""
    workflow_id: str
    workflow_type: WorkflowType
    status: WorkflowStatus
    feedback: Optional[TeachingFeedback]
    execution_time: float
    error_message: Optional[str] = None
    agent_interactions: List[Dict[str, Any]] = None
    quality_metrics: Dict[str, float] = None

class BaseWorkflow(ABC):
    """工作流基类"""
    
    def __init__(self, workflow_id: str):
        self.workflow_id = workflow_id
        self.status = WorkflowStatus.PENDING
        self.start_time = None
        self.end_time = None
        self.error_message = None
        
    @abstractmethod
    async def execute(self, *args, **kwargs) -> WorkflowResult:
        """执行工作流"""
        pass
    
    def _start_workflow(self):
        """开始工作流"""
        self.status = WorkflowStatus.IN_PROGRESS
        self.start_time = datetime.now()
        logger.info(f"Starting workflow {self.workflow_id}")
    
    def _complete_workflow(self, success: bool = True, error_message: str = None):
        """完成工作流"""
        self.end_time = datetime.now()
        if success:
            self.status = WorkflowStatus.COMPLETED
        else:
            self.status = WorkflowStatus.FAILED
            self.error_message = error_message
        
        execution_time = (self.end_time - self.start_time).total_seconds()
        logger.info(f"Workflow {self.workflow_id} completed in {execution_time:.2f}s with status {self.status}")
        log_performance_metric(f"workflow_{self.__class__.__name__}_execution_time", execution_time, "s")

class AssignmentAnalysisWorkflow(BaseWorkflow):
    """作业分析工作流"""
    
    def __init__(self, workflow_id: str, teaching_system: MultiAgentTeachingSystem):
        super().__init__(workflow_id)
        self.teaching_system = teaching_system
        self.workflow_type = WorkflowType.ASSIGNMENT_ANALYSIS
    
    async def execute(self, submission_data: SubmissionData) -> WorkflowResult:
        """
        执行作业分析工作流
        
        工作流顺序：
        1. CodeAnalyzer: 代码技术分析
        2. StudentProfiler: 学生画像分析  
        3. PedagogyExpert: 教学策略制定
        4. FeedbackGenerator: 反馈内容生成
        5. QualityController: 质量控制检查
        """
        self._start_workflow()
        
        try:
            with LogExecutionTime(f"assignment_analysis_{submission_data.student_id}"):
                # 使用教学系统处理提交
                feedback = await self.teaching_system.process_submission(submission_data)
                
                # 记录Agent活动
                log_agent_activity("AssignmentAnalysisWorkflow", "completed_analysis", {
                    "student_id": submission_data.student_id,
                    "assignment_id": submission_data.assignment_id,
                    "overall_score": feedback.overall_score
                })
                
                # 计算质量指标
                quality_metrics = self._calculate_quality_metrics(feedback)
                
                self._complete_workflow(success=True)
                
                return WorkflowResult(
                    workflow_id=self.workflow_id,
                    workflow_type=self.workflow_type,
                    status=self.status,
                    feedback=feedback,
                    execution_time=(self.end_time - self.start_time).total_seconds(),
                    quality_metrics=quality_metrics
                )
                
        except Exception as e:
            logger.error(f"Assignment analysis workflow failed: {e}")
            self._complete_workflow(success=False, error_message=str(e))
            
            return WorkflowResult(
                workflow_id=self.workflow_id,
                workflow_type=self.workflow_type,
                status=self.status,
                feedback=None,
                execution_time=(self.end_time - self.start_time).total_seconds() if self.end_time else 0.0,
                error_message=str(e)
            )
    
    def _calculate_quality_metrics(self, feedback: TeachingFeedback) -> Dict[str, float]:
        """计算反馈质量指标"""
        return {
            "overall_quality": feedback.quality_score / 100.0,
            "technical_accuracy": min(1.0, feedback.overall_score / 100.0),
            "personalization_level": self._assess_personalization_level(feedback),
            "completeness": self._assess_completeness(feedback)
        }
    
    def _assess_personalization_level(self, feedback: TeachingFeedback) -> float:
        """评估个性化程度"""
        # 简化的个性化评估逻辑
        personalization_score = 0.0
        
        if feedback.student_profile and isinstance(feedback.student_profile, dict):
            personalization_score += 0.3
        
        if feedback.recommendations and isinstance(feedback.recommendations, dict):
            personalization_score += 0.3
        
        if feedback.next_steps and len(feedback.next_steps) > 0:
            personalization_score += 0.4
        
        return min(1.0, personalization_score)
    
    def _assess_completeness(self, feedback: TeachingFeedback) -> float:
        """评估反馈完整性"""
        completeness_score = 0.0
        
        required_fields = ['feedback_content', 'recommendations', 'next_steps']
        for field in required_fields:
            if hasattr(feedback, field) and getattr(feedback, field):
                completeness_score += 1.0 / len(required_fields)
        
        return completeness_score

class DebuggingGuidanceWorkflow(BaseWorkflow):
    """调试指导工作流"""
    
    def __init__(self, workflow_id: str, teaching_system: MultiAgentTeachingSystem):
        super().__init__(workflow_id)
        self.teaching_system = teaching_system
        self.workflow_type = WorkflowType.DEBUGGING_GUIDANCE
    
    async def execute(self, submission_data: SubmissionData) -> WorkflowResult:
        """
        执行调试指导工作流
        
        工作流顺序：
        1. CodeAnalyzer: 识别错误和问题
        2. DebuggingMentor: 设计调试引导策略
        3. StudentProfiler: 分析学生调试能力
        4. FeedbackGenerator: 生成苏格拉底式引导
        5. QualityController: 确保引导质量
        """
        self._start_workflow()
        
        try:
            with LogExecutionTime(f"debugging_guidance_{submission_data.student_id}"):
                # 使用专门的调试会话处理
                feedback = await self.teaching_system.process_debugging_session(submission_data)
                
                # 记录调试指导活动
                log_agent_activity("DebuggingGuidanceWorkflow", "completed_debugging_guidance", {
                    "student_id": submission_data.student_id,
                    "error_types": self._extract_error_types(feedback),
                    "guidance_quality": feedback.quality_score
                })
                
                # 计算调试指导特有的质量指标
                quality_metrics = self._calculate_debugging_quality_metrics(feedback)
                
                self._complete_workflow(success=True)
                
                return WorkflowResult(
                    workflow_id=self.workflow_id,
                    workflow_type=self.workflow_type,
                    status=self.status,
                    feedback=feedback,
                    execution_time=(self.end_time - self.start_time).total_seconds(),
                    quality_metrics=quality_metrics
                )
                
        except Exception as e:
            logger.error(f"Debugging guidance workflow failed: {e}")
            self._complete_workflow(success=False, error_message=str(e))
            
            return WorkflowResult(
                workflow_id=self.workflow_id,
                workflow_type=self.workflow_type,
                status=self.status,
                feedback=None,
                execution_time=(self.end_time - self.start_time).total_seconds() if self.end_time else 0.0,
                error_message=str(e)
            )
    
    def _extract_error_types(self, feedback: TeachingFeedback) -> List[str]:
        """从反馈中提取错误类型"""
        error_types = []
        
        if feedback.code_analysis and isinstance(feedback.code_analysis, dict):
            critical_errors = feedback.code_analysis.get('critical_errors', [])
            for error in critical_errors:
                if isinstance(error, dict) and 'type' in error:
                    error_types.append(error['type'])
        
        return error_types
    
    def _calculate_debugging_quality_metrics(self, feedback: TeachingFeedback) -> Dict[str, float]:
        """计算调试指导质量指标"""
        return {
            "guidance_clarity": feedback.quality_score / 100.0,
            "socratic_approach": self._assess_socratic_approach(feedback),
            "skill_development_focus": self._assess_skill_development(feedback),
            "problem_solving_scaffolding": self._assess_scaffolding(feedback)
        }
    
    def _assess_socratic_approach(self, feedback: TeachingFeedback) -> float:
        """评估苏格拉底式引导程度"""
        # 检查反馈内容中是否包含引导性问题
        if isinstance(feedback.feedback_content, dict):
            content = str(feedback.feedback_content)
            question_indicators = ['为什么', '如何', '什么', '?', '？', '思考', '尝试', '你认为']
            question_count = sum(1 for indicator in question_indicators if indicator in content)
            return min(1.0, question_count / 10.0)  # 标准化为0-1
        return 0.0
    
    def _assess_skill_development(self, feedback: TeachingFeedback) -> float:
        """评估技能发展关注度"""
        if isinstance(feedback.recommendations, dict):
            skill_keywords = ['调试', '方法', '技能', '能力', '思维', '习惯']
            content = str(feedback.recommendations)
            skill_focus = sum(1 for keyword in skill_keywords if keyword in content)
            return min(1.0, skill_focus / 5.0)
        return 0.0
    
    def _assess_scaffolding(self, feedback: TeachingFeedback) -> float:
        """评估脚手架支持程度"""
        if feedback.next_steps and isinstance(feedback.next_steps, list):
            # 步骤越具体、越详细，脚手架支持越好
            total_length = sum(len(step) for step in feedback.next_steps if isinstance(step, str))
            return min(1.0, total_length / 500.0)  # 基于内容详细程度评估
        return 0.0

class PersonalizedLearningWorkflow(BaseWorkflow):
    """个性化学习工作流"""
    
    def __init__(self, workflow_id: str, teaching_system: MultiAgentTeachingSystem):
        super().__init__(workflow_id)
        self.teaching_system = teaching_system
        self.workflow_type = WorkflowType.PERSONALIZED_LEARNING
    
    async def execute(self, submission_data: SubmissionData, learning_history: List[Dict[str, Any]]) -> WorkflowResult:
        """
        执行个性化学习工作流
        
        工作流顺序：
        1. StudentProfiler: 深度分析学生学习模式
        2. PedagogyExpert: 制定个性化教学策略
        3. FeedbackGenerator: 生成个性化学习建议
        4. QualityController: 确保个性化质量
        """
        self._start_workflow()
        
        try:
            with LogExecutionTime(f"personalized_learning_{submission_data.student_id}"):
                # 使用个性化学习处理
                feedback = await self.teaching_system.process_personalized_learning(
                    submission_data, learning_history
                )
                
                # 记录个性化学习活动
                log_agent_activity("PersonalizedLearningWorkflow", "completed_personalization", {
                    "student_id": submission_data.student_id,
                    "history_length": len(learning_history),
                    "personalization_score": self._calculate_personalization_score(feedback)
                })
                
                # 计算个性化质量指标
                quality_metrics = self._calculate_personalization_quality_metrics(feedback, learning_history)
                
                self._complete_workflow(success=True)
                
                return WorkflowResult(
                    workflow_id=self.workflow_id,
                    workflow_type=self.workflow_type,
                    status=self.status,
                    feedback=feedback,
                    execution_time=(self.end_time - self.start_time).total_seconds(),
                    quality_metrics=quality_metrics
                )
                
        except Exception as e:
            logger.error(f"Personalized learning workflow failed: {e}")
            self._complete_workflow(success=False, error_message=str(e))
            
            return WorkflowResult(
                workflow_id=self.workflow_id,
                workflow_type=self.workflow_type,
                status=self.status,
                feedback=None,
                execution_time=(self.end_time - self.start_time).total_seconds() if self.end_time else 0.0,
                error_message=str(e)
            )
    
    def _calculate_personalization_score(self, feedback: TeachingFeedback) -> float:
        """计算个性化程度评分"""
        score = 0.0
        
        # 学生画像的详细程度
        if feedback.student_profile:
            score += 0.3
        
        # 个性化推荐的丰富程度
        if feedback.recommendations and isinstance(feedback.recommendations, dict):
            score += 0.3 * min(1.0, len(feedback.recommendations) / 5.0)
        
        # 学习路径的具体性
        if feedback.next_steps and len(feedback.next_steps) > 0:
            score += 0.4
        
        return min(1.0, score)
    
    def _calculate_personalization_quality_metrics(self, feedback: TeachingFeedback, learning_history: List[Dict]) -> Dict[str, float]:
        """计算个性化质量指标"""
        return {
            "personalization_depth": self._calculate_personalization_score(feedback),
            "learning_pattern_recognition": self._assess_pattern_recognition(learning_history),
            "adaptive_difficulty": self._assess_difficulty_adaptation(feedback),
            "resource_relevance": self._assess_resource_relevance(feedback)
        }
    
    def _assess_pattern_recognition(self, learning_history: List[Dict]) -> float:
        """评估学习模式识别程度"""
        if len(learning_history) < 3:
            return 0.3  # 历史数据不足
        elif len(learning_history) < 10:
            return 0.7  # 有一定历史数据
        else:
            return 1.0  # 充足的历史数据
    
    def _assess_difficulty_adaptation(self, feedback: TeachingFeedback) -> float:
        """评估难度适应性"""
        # 简化的难度适应性评估
        if isinstance(feedback.recommendations, dict):
            difficulty_keywords = ['难度', '挑战', '基础', '进阶', '适合']
            content = str(feedback.recommendations)
            adaptation_indicators = sum(1 for keyword in difficulty_keywords if keyword in content)
            return min(1.0, adaptation_indicators / 3.0)
        return 0.0
    
    def _assess_resource_relevance(self, feedback: TeachingFeedback) -> float:
        """评估资源推荐相关性"""
        if feedback.next_steps and len(feedback.next_steps) > 0:
            # 基于推荐资源的数量和详细程度评估
            total_resources = len(feedback.next_steps)
            return min(1.0, total_resources / 5.0)
        return 0.0

class WorkflowManager:
    """工作流管理器"""
    
    def __init__(self, teaching_system: MultiAgentTeachingSystem):
        self.teaching_system = teaching_system
        self.active_workflows: Dict[str, BaseWorkflow] = {}
        self.completed_workflows: Dict[str, WorkflowResult] = {}
        self.performance_metrics = {
            "total_workflows": 0,
            "successful_workflows": 0,
            "failed_workflows": 0,
            "average_execution_time": 0.0
        }
    
    async def execute_assignment_analysis(self, submission_data: SubmissionData) -> WorkflowResult:
        """执行作业分析工作流"""
        workflow_id = f"assignment_{submission_data.student_id}_{int(datetime.now().timestamp())}"
        
        workflow = AssignmentAnalysisWorkflow(workflow_id, self.teaching_system)
        self.active_workflows[workflow_id] = workflow
        
        try:
            result = await workflow.execute(submission_data)
            self._record_workflow_completion(result)
            return result
        finally:
            if workflow_id in self.active_workflows:
                del self.active_workflows[workflow_id]
    
    async def execute_debugging_guidance(self, submission_data: SubmissionData) -> WorkflowResult:
        """执行调试指导工作流"""
        workflow_id = f"debugging_{submission_data.student_id}_{int(datetime.now().timestamp())}"
        
        workflow = DebuggingGuidanceWorkflow(workflow_id, self.teaching_system)
        self.active_workflows[workflow_id] = workflow
        
        try:
            result = await workflow.execute(submission_data)
            self._record_workflow_completion(result)
            return result
        finally:
            if workflow_id in self.active_workflows:
                del self.active_workflows[workflow_id]
    
    async def execute_personalized_learning(self, submission_data: SubmissionData, learning_history: List[Dict]) -> WorkflowResult:
        """执行个性化学习工作流"""
        workflow_id = f"personalized_{submission_data.student_id}_{int(datetime.now().timestamp())}"
        
        workflow = PersonalizedLearningWorkflow(workflow_id, self.teaching_system)
        self.active_workflows[workflow_id] = workflow
        
        try:
            result = await workflow.execute(submission_data, learning_history)
            self._record_workflow_completion(result)
            return result
        finally:
            if workflow_id in self.active_workflows:
                del self.active_workflows[workflow_id]
    
    async def execute_batch_workflows(self, submissions: List[SubmissionData], workflow_type: WorkflowType = WorkflowType.ASSIGNMENT_ANALYSIS) -> List[WorkflowResult]:
        """批量执行工作流"""
        tasks = []
        
        for submission in submissions:
            if workflow_type == WorkflowType.ASSIGNMENT_ANALYSIS:
                task = self.execute_assignment_analysis(submission)
            elif workflow_type == WorkflowType.DEBUGGING_GUIDANCE:
                task = self.execute_debugging_guidance(submission)
            else:
                continue  # 个性化学习需要额外的历史数据，暂不支持批量
            
            tasks.append(task)
        
        # 控制并发数量，避免系统过载
        max_concurrent = SYSTEM_CONFIG.get("max_concurrent_sessions", 10)
        semaphore = asyncio.Semaphore(max_concurrent)
        
        async def limited_execution(task):
            async with semaphore:
                return await task
        
        results = await asyncio.gather(*[limited_execution(task) for task in tasks])
        
        # 记录批量处理性能
        successful = sum(1 for r in results if r.status == WorkflowStatus.COMPLETED)
        log_performance_metric("batch_workflow_success_rate", successful / len(results), "", {
            "total": len(results),
            "successful": successful,
            "workflow_type": workflow_type.value
        })
        
        return results
    
    def _record_workflow_completion(self, result: WorkflowResult):
        """记录工作流完成情况"""
        self.completed_workflows[result.workflow_id] = result
        
        # 更新性能指标
        self.performance_metrics["total_workflows"] += 1
        
        if result.status == WorkflowStatus.COMPLETED:
            self.performance_metrics["successful_workflows"] += 1
        else:
            self.performance_metrics["failed_workflows"] += 1
        
        # 更新平均执行时间
        total_time = self.performance_metrics["average_execution_time"] * (self.performance_metrics["total_workflows"] - 1)
        self.performance_metrics["average_execution_time"] = (total_time + result.execution_time) / self.performance_metrics["total_workflows"]
        
        # 记录性能指标
        log_performance_metric("workflow_execution_time", result.execution_time, "s", {
            "workflow_type": result.workflow_type.value,
            "status": result.status.value
        })
    
    def get_workflow_status(self, workflow_id: str) -> Optional[WorkflowStatus]:
        """获取工作流状态"""
        if workflow_id in self.active_workflows:
            return self.active_workflows[workflow_id].status
        elif workflow_id in self.completed_workflows:
            return self.completed_workflows[workflow_id].status
        return None
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """获取性能摘要"""
        success_rate = 0.0
        if self.performance_metrics["total_workflows"] > 0:
            success_rate = self.performance_metrics["successful_workflows"] / self.performance_metrics["total_workflows"]
        
        return {
            **self.performance_metrics,
            "success_rate": success_rate,
            "active_workflows": len(self.active_workflows),
            "completed_workflows": len(self.completed_workflows)
        }

# 使用示例
async def example_workflow_usage():
    """工作流使用示例"""
    from ..models.teaching_models import create_sample_submission
    
    # 创建教学系统和工作流管理器
    teaching_system = MultiAgentTeachingSystem("python_basics")
    workflow_manager = WorkflowManager(teaching_system)
    
    # 创建示例提交
    submission = create_sample_submission()
    
    # 执行作业分析工作流
    result = await workflow_manager.execute_assignment_analysis(submission)
    print(f"Assignment analysis result: {result.status}")
    
    # 执行调试指导工作流（如果代码有错误）
    debugging_result = await workflow_manager.execute_debugging_guidance(submission)
    print(f"Debugging guidance result: {debugging_result.status}")
    
    # 查看性能摘要
    performance = workflow_manager.get_performance_summary()
    print(f"Workflow performance: {performance}")

if __name__ == "__main__":
    asyncio.run(example_workflow_usage())