"""
AI教学助手系统 - 简化版教学工作流管理
实现核心教学工作流的简化版本

Author: AI Teaching System Architecture  
Date: 2025-09-11
"""

from typing import Dict, List, Any, Optional
from datetime import datetime
from dataclasses import dataclass
from enum import Enum
import asyncio

from ..models.teaching_models import SubmissionData, TeachingFeedback
from ..agents.teaching_agents import MultiAgentTeachingSystem
from ..utils.logger import get_logger, log_agent_activity

logger = get_logger(__name__)


class WorkflowType(Enum):
    """工作流类型"""
    ASSIGNMENT_ANALYSIS = "assignment_analysis"
    DEBUGGING_GUIDANCE = "debugging_guidance"
    PERSONALIZED_LEARNING = "personalized_learning"


class WorkflowStatus(Enum):
    """工作流状态"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class WorkflowResult:
    """工作流执行结果"""
    workflow_id: str
    workflow_type: WorkflowType
    status: WorkflowStatus
    feedback: Optional[TeachingFeedback]
    execution_time: float
    error_message: Optional[str] = None


class WorkflowManager:
    """简化版工作流管理器"""
    
    def __init__(self, teaching_system: MultiAgentTeachingSystem):
        self.teaching_system = teaching_system
        self.active_workflows: Dict[str, Any] = {}
        
    async def execute_assignment_analysis(self, submission_data: SubmissionData) -> WorkflowResult:
        """执行作业分析工作流"""
        workflow_id = f"assignment_{submission_data.student_id}_{int(datetime.now().timestamp())}"
        start_time = datetime.now()
        
        try:
            logger.info(f"Starting assignment analysis workflow: {workflow_id}")
            
            # 调用教学系统处理提交
            feedback = await self.teaching_system.process_submission(submission_data)
            
            # 记录活动
            log_agent_activity("AssignmentAnalysisWorkflow", "completed_analysis", {
                "student_id": submission_data.student_id,
                "assignment_id": submission_data.assignment_id,
                "overall_score": feedback.overall_score
            })
            
            execution_time = (datetime.now() - start_time).total_seconds()
            logger.info(f"Assignment analysis completed in {execution_time:.2f}s")
            
            return WorkflowResult(
                workflow_id=workflow_id,
                workflow_type=WorkflowType.ASSIGNMENT_ANALYSIS,
                status=WorkflowStatus.COMPLETED,
                feedback=feedback,
                execution_time=execution_time
            )
            
        except Exception as e:
            execution_time = (datetime.now() - start_time).total_seconds()
            logger.error(f"Assignment analysis workflow failed: {e}")
            
            return WorkflowResult(
                workflow_id=workflow_id,
                workflow_type=WorkflowType.ASSIGNMENT_ANALYSIS,
                status=WorkflowStatus.FAILED,
                feedback=None,
                execution_time=execution_time,
                error_message=str(e)
            )
    
    async def execute_debugging_guidance(self, submission_data: SubmissionData) -> WorkflowResult:
        """执行调试指导工作流"""
        workflow_id = f"debugging_{submission_data.student_id}_{int(datetime.now().timestamp())}"
        start_time = datetime.now()
        
        try:
            logger.info(f"Starting debugging guidance workflow: {workflow_id}")
            
            # 调用调试会话处理
            feedback = await self.teaching_system.process_debugging_session(submission_data)
            
            # 记录活动
            log_agent_activity("DebuggingGuidanceWorkflow", "completed_debugging_guidance", {
                "student_id": submission_data.student_id,
                "guidance_quality": feedback.quality_score
            })
            
            execution_time = (datetime.now() - start_time).total_seconds()
            logger.info(f"Debugging guidance completed in {execution_time:.2f}s")
            
            return WorkflowResult(
                workflow_id=workflow_id,
                workflow_type=WorkflowType.DEBUGGING_GUIDANCE,
                status=WorkflowStatus.COMPLETED,
                feedback=feedback,
                execution_time=execution_time
            )
            
        except Exception as e:
            execution_time = (datetime.now() - start_time).total_seconds()
            logger.error(f"Debugging guidance workflow failed: {e}")
            
            return WorkflowResult(
                workflow_id=workflow_id,
                workflow_type=WorkflowType.DEBUGGING_GUIDANCE,
                status=WorkflowStatus.FAILED,
                feedback=None,
                execution_time=execution_time,
                error_message=str(e)
            )
    
    async def execute_personalized_learning(self, submission_data: SubmissionData, learning_history: List[Dict]) -> WorkflowResult:
        """执行个性化学习工作流"""
        workflow_id = f"personalized_{submission_data.student_id}_{int(datetime.now().timestamp())}"
        start_time = datetime.now()
        
        try:
            logger.info(f"Starting personalized learning workflow: {workflow_id}")
            
            # 调用个性化学习处理
            feedback = await self.teaching_system.process_personalized_learning(submission_data, learning_history)
            
            # 记录活动
            log_agent_activity("PersonalizedLearningWorkflow", "completed_personalization", {
                "student_id": submission_data.student_id,
                "history_length": len(learning_history)
            })
            
            execution_time = (datetime.now() - start_time).total_seconds()
            logger.info(f"Personalized learning completed in {execution_time:.2f}s")
            
            return WorkflowResult(
                workflow_id=workflow_id,
                workflow_type=WorkflowType.PERSONALIZED_LEARNING,
                status=WorkflowStatus.COMPLETED,
                feedback=feedback,
                execution_time=execution_time
            )
            
        except Exception as e:
            execution_time = (datetime.now() - start_time).total_seconds()
            logger.error(f"Personalized learning workflow failed: {e}")
            
            return WorkflowResult(
                workflow_id=workflow_id,
                workflow_type=WorkflowType.PERSONALIZED_LEARNING,
                status=WorkflowStatus.FAILED,
                feedback=None,
                execution_time=execution_time,
                error_message=str(e)
            )
    
    async def execute_batch_workflows(self, submissions: List[SubmissionData], workflow_type: WorkflowType = WorkflowType.ASSIGNMENT_ANALYSIS) -> List[WorkflowResult]:
        """批量执行工作流"""
        tasks = []
        
        for submission in submissions:
            if workflow_type == WorkflowType.ASSIGNMENT_ANALYSIS:
                task = self.execute_assignment_analysis(submission)
            elif workflow_type == WorkflowType.DEBUGGING_GUIDANCE:
                task = self.execute_debugging_guidance(submission)
            else:
                continue  # 个性化学习需要额外的历史数据
            
            tasks.append(task)
        
        # 并发执行，但限制并发数
        semaphore = asyncio.Semaphore(10)
        
        async def limited_execution(task):
            async with semaphore:
                return await task
        
        results = await asyncio.gather(*[limited_execution(task) for task in tasks])
        
        # 记录批量处理结果
        successful = sum(1 for r in results if r.status == WorkflowStatus.COMPLETED)
        logger.info(f"Batch workflow completed: {successful}/{len(results)} successful")
        
        return results


# 导出
__all__ = [
    'WorkflowType', 'WorkflowStatus', 'WorkflowResult', 'WorkflowManager'
]