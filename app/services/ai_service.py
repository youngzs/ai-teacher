"""
AI教学助手系统 - AI服务集成
集成现有的AI Agent系统，提供异步API接口

Author: AI Backend Architecture Expert  
Date: 2025-09-10
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
import json
import uuid
from concurrent.futures import ThreadPoolExecutor

# 导入现有的AI系统组件
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from src.agents.teaching_agents import MultiAgentTeachingSystem
from src.workflows.teaching_workflows_simple import WorkflowManager, WorkflowType
from src.models.teaching_models import (
    SubmissionData, StudentProfile, TeachingFeedback,
    ProgrammingLanguage, DifficultyLevel, create_sample_submission
)
from src.utils.logger import get_logger, log_agent_activity, log_performance_metric

from ..core.config import settings
from ..utils.cache import CacheManager

logger = get_logger(__name__)


class AITeachingService:
    """
    AI教学服务类
    
    提供异步的AI教学功能接口，整合现有的多Agent系统
    """
    
    def __init__(self):
        self.teaching_system: Optional[MultiAgentTeachingSystem] = None
        self.workflow_manager: Optional[WorkflowManager] = None
        self.cache_manager = CacheManager()
        self.thread_pool = ThreadPoolExecutor(max_workers=settings.MAX_AI_SESSIONS)
        self.is_initialized = False
        self.session_counter = 0
        
    async def initialize(self):
        """初始化AI服务"""
        try:
            logger.info("Initializing AI Teaching Service...")
            
            # 初始化多Agent教学系统
            self.teaching_system = MultiAgentTeachingSystem("ai_teacher_backend")
            
            # 初始化工作流管理器
            self.workflow_manager = WorkflowManager(self.teaching_system)
            
            # 验证系统状态
            health_check = await self.health_check()
            if not health_check:
                raise Exception("AI system health check failed")
            
            self.is_initialized = True
            logger.info("AI Teaching Service initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize AI Teaching Service: {str(e)}")
            raise
    
    async def cleanup(self):
        """清理AI服务资源"""
        try:
            logger.info("Cleaning up AI Teaching Service...")
            
            if self.thread_pool:
                self.thread_pool.shutdown(wait=True)
            
            if self.cache_manager:
                await self.cache_manager.close()
            
            logger.info("AI Teaching Service cleanup completed")
            
        except Exception as e:
            logger.error(f"Error during AI service cleanup: {str(e)}")
    
    async def health_check(self) -> bool:
        """AI服务健康检查"""
        try:
            if not self.teaching_system:
                return False
            
            # 创建测试提交
            test_submission = create_sample_submission()
            
            # 执行快速测试（使用线程池避免阻塞）
            def test_analysis():
                try:
                    # 这里可以添加更具体的健康检查逻辑
                    return True
                except Exception as e:
                    logger.error(f"AI health check failed: {str(e)}")
                    return False
            
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(self.thread_pool, test_analysis)
            
            return result
            
        except Exception as e:
            logger.error(f"AI health check error: {str(e)}")
            return False
    
    async def process_submission(self, submission_data: SubmissionData) -> TeachingFeedback:
        """
        处理代码提交，进行AI分析并生成反馈
        
        Args:
            submission_data: 提交数据
            
        Returns:
            TeachingFeedback: AI反馈结果
        """
        if not self.is_initialized:
            raise RuntimeError("AI service is not initialized")
        
        # 生成会话ID
        session_id = f"session_{uuid.uuid4().hex[:8]}_{int(datetime.now().timestamp())}"
        
        try:
            start_time = datetime.now()
            
            # 检查缓存
            cache_key = self._generate_cache_key(submission_data)
            cached_result = await self.cache_manager.get(cache_key)
            
            if cached_result and not getattr(submission_data, 'force_reanalyze', False):
                logger.info(f"Returning cached result for submission: {submission_data.student_id}")
                return TeachingFeedback.from_dict(cached_result)
            
            # 记录开始处理
            log_agent_activity("AITeachingService", "started_processing", {
                "session_id": session_id,
                "student_id": submission_data.student_id,
                "assignment_id": submission_data.assignment_id,
                "language": submission_data.language.value
            })
            
            # 异步执行AI分析
            result = await self._execute_assignment_analysis(submission_data, session_id)
            
            # 计算处理时间
            processing_time = (datetime.now() - start_time).total_seconds()
            
            # 记录性能指标
            log_performance_metric("ai_submission_processing_time", processing_time, "s", {
                "language": submission_data.language.value,
                "code_length": len(submission_data.code)
            })
            
            # 缓存结果
            await self.cache_manager.set(
                cache_key, 
                result.to_dict(), 
                expire_time=settings.REDIS_EXPIRE_TIME
            )
            
            logger.info(f"AI analysis completed for session {session_id} in {processing_time:.2f}s")
            
            return result
            
        except Exception as e:
            logger.error(f"AI submission processing failed for session {session_id}: {str(e)}")
            
            # 记录失败
            log_agent_activity("AITeachingService", "processing_failed", {
                "session_id": session_id,
                "student_id": submission_data.student_id,
                "error": str(e)
            })
            
            raise
    
    async def process_debugging_session(self, submission_data: SubmissionData) -> TeachingFeedback:
        """
        处理调试会话
        
        Args:
            submission_data: 提交数据
            
        Returns:
            TeachingFeedback: 调试指导反馈
        """
        if not self.is_initialized:
            raise RuntimeError("AI service is not initialized")
        
        session_id = f"debug_{uuid.uuid4().hex[:8]}_{int(datetime.now().timestamp())}"
        
        try:
            start_time = datetime.now()
            
            logger.info(f"Starting debugging session: {session_id}")
            
            # 执行调试分析
            result = await self._execute_debugging_analysis(submission_data, session_id)
            
            processing_time = (datetime.now() - start_time).total_seconds()
            
            # 记录指标
            log_performance_metric("ai_debugging_processing_time", processing_time, "s", {
                "language": submission_data.language.value
            })
            
            logger.info(f"Debugging session completed: {session_id} in {processing_time:.2f}s")
            
            return result
            
        except Exception as e:
            logger.error(f"Debugging session failed for {session_id}: {str(e)}")
            raise
    
    async def process_personalized_learning(
        self, 
        submission_data: SubmissionData, 
        learning_history: List[Dict[str, Any]]
    ) -> TeachingFeedback:
        """
        处理个性化学习分析
        
        Args:
            submission_data: 提交数据
            learning_history: 学习历史数据
            
        Returns:
            TeachingFeedback: 个性化学习反馈
        """
        if not self.is_initialized:
            raise RuntimeError("AI service is not initialized")
        
        session_id = f"personalized_{uuid.uuid4().hex[:8]}_{int(datetime.now().timestamp())}"
        
        try:
            start_time = datetime.now()
            
            logger.info(f"Starting personalized learning session: {session_id}")
            
            # 执行个性化分析
            result = await self._execute_personalized_analysis(
                submission_data, learning_history, session_id
            )
            
            processing_time = (datetime.now() - start_time).total_seconds()
            
            # 记录指标
            log_performance_metric("ai_personalized_processing_time", processing_time, "s", {
                "history_length": len(learning_history)
            })
            
            logger.info(f"Personalized learning session completed: {session_id} in {processing_time:.2f}s")
            
            return result
            
        except Exception as e:
            logger.error(f"Personalized learning session failed for {session_id}: {str(e)}")
            raise
    
    async def batch_process_submissions(
        self, 
        submissions: List[SubmissionData],
        analysis_type: str = "assignment"
    ) -> List[TeachingFeedback]:
        """
        批量处理提交
        
        Args:
            submissions: 提交数据列表
            analysis_type: 分析类型
            
        Returns:
            List[TeachingFeedback]: 反馈结果列表
        """
        if not self.is_initialized:
            raise RuntimeError("AI service is not initialized")
        
        if len(submissions) > 20:
            raise ValueError("Maximum 20 submissions allowed for batch processing")
        
        batch_id = f"batch_{uuid.uuid4().hex[:8]}"
        
        try:
            logger.info(f"Starting batch processing: {batch_id} with {len(submissions)} submissions")
            
            # 根据分析类型选择工作流
            if analysis_type == "debugging":
                workflow_type = WorkflowType.DEBUGGING_GUIDANCE
            else:
                workflow_type = WorkflowType.ASSIGNMENT_ANALYSIS
            
            # 执行批量分析
            results = await self._execute_batch_analysis(submissions, workflow_type, batch_id)
            
            logger.info(f"Batch processing completed: {batch_id}")
            
            return [result.feedback for result in results if result.feedback]
            
        except Exception as e:
            logger.error(f"Batch processing failed for {batch_id}: {str(e)}")
            raise
    
    async def get_student_insights(self, student_id: str, submission_history: List[Dict]) -> Dict[str, Any]:
        """
        获取学生学习洞察
        
        Args:
            student_id: 学生ID
            submission_history: 提交历史
            
        Returns:
            Dict: 学习洞察数据
        """
        try:
            # 分析学习模式和趋势
            insights = {
                "competency_assessment": await self._assess_competency_level(submission_history),
                "learning_patterns": await self._analyze_learning_patterns(submission_history),
                "improvement_suggestions": await self._generate_improvement_suggestions(submission_history),
                "skill_gaps": await self._identify_skill_gaps(submission_history),
                "progress_trends": await self._calculate_progress_trends(submission_history)
            }
            
            return insights
            
        except Exception as e:
            logger.error(f"Failed to generate student insights for {student_id}: {str(e)}")
            raise
    
    # 私有方法
    
    async def _execute_assignment_analysis(
        self, 
        submission_data: SubmissionData, 
        session_id: str
    ) -> TeachingFeedback:
        """执行作业分析"""
        def run_analysis():
            return asyncio.run(
                self.workflow_manager.execute_assignment_analysis(submission_data)
            )
        
        loop = asyncio.get_event_loop()
        workflow_result = await loop.run_in_executor(self.thread_pool, run_analysis)
        
        if workflow_result.feedback is None:
            raise RuntimeError(f"Analysis failed: {workflow_result.error_message}")
        
        return workflow_result.feedback
    
    async def _execute_debugging_analysis(
        self, 
        submission_data: SubmissionData, 
        session_id: str
    ) -> TeachingFeedback:
        """执行调试分析"""
        def run_debugging():
            return asyncio.run(
                self.workflow_manager.execute_debugging_guidance(submission_data)
            )
        
        loop = asyncio.get_event_loop()
        workflow_result = await loop.run_in_executor(self.thread_pool, run_debugging)
        
        if workflow_result.feedback is None:
            raise RuntimeError(f"Debugging analysis failed: {workflow_result.error_message}")
        
        return workflow_result.feedback
    
    async def _execute_personalized_analysis(
        self, 
        submission_data: SubmissionData, 
        learning_history: List[Dict], 
        session_id: str
    ) -> TeachingFeedback:
        """执行个性化分析"""
        def run_personalized():
            return asyncio.run(
                self.workflow_manager.execute_personalized_learning(submission_data, learning_history)
            )
        
        loop = asyncio.get_event_loop()
        workflow_result = await loop.run_in_executor(self.thread_pool, run_personalized)
        
        if workflow_result.feedback is None:
            raise RuntimeError(f"Personalized analysis failed: {workflow_result.error_message}")
        
        return workflow_result.feedback
    
    async def _execute_batch_analysis(
        self, 
        submissions: List[SubmissionData], 
        workflow_type: WorkflowType, 
        batch_id: str
    ):
        """执行批量分析"""
        def run_batch():
            return asyncio.run(
                self.workflow_manager.execute_batch_workflows(submissions, workflow_type)
            )
        
        loop = asyncio.get_event_loop()
        results = await loop.run_in_executor(self.thread_pool, run_batch)
        
        return results
    
    def _generate_cache_key(self, submission_data: SubmissionData) -> str:
        """生成缓存键"""
        import hashlib
        
        content = f"{submission_data.assignment_id}_{submission_data.code}_{submission_data.language.value}"
        return f"ai_analysis_{hashlib.md5(content.encode()).hexdigest()}"
    
    async def _assess_competency_level(self, history: List[Dict]) -> Dict[str, Any]:
        """评估能力水平"""
        if not history:
            return {"level": "beginner", "confidence": 0.0}
        
        scores = [h.get("score", 0) for h in history if "score" in h]
        if not scores:
            return {"level": "beginner", "confidence": 0.0}
        
        avg_score = sum(scores) / len(scores)
        
        if avg_score >= 90:
            level = "expert"
        elif avg_score >= 80:
            level = "proficient"
        elif avg_score >= 70:
            level = "competent"
        elif avg_score >= 60:
            level = "advanced_beginner"
        else:
            level = "novice"
        
        return {
            "level": level,
            "average_score": avg_score,
            "confidence": min(1.0, len(scores) / 10.0),
            "total_submissions": len(scores)
        }
    
    async def _analyze_learning_patterns(self, history: List[Dict]) -> Dict[str, Any]:
        """分析学习模式"""
        if len(history) < 3:
            return {"pattern": "insufficient_data"}
        
        # 简化的学习模式分析
        scores = [h.get("score", 0) for h in history[-10:] if "score" in h]  # 最近10次
        
        if len(scores) < 3:
            return {"pattern": "insufficient_data"}
        
        # 计算趋势
        if scores[-1] > scores[0]:
            trend = "improving"
        elif scores[-1] < scores[0]:
            trend = "declining"
        else:
            trend = "stable"
        
        # 计算一致性
        variance = sum((s - sum(scores)/len(scores))**2 for s in scores) / len(scores)
        consistency = "high" if variance < 100 else "medium" if variance < 400 else "low"
        
        return {
            "pattern": trend,
            "consistency": consistency,
            "variance": variance,
            "recent_scores": scores
        }
    
    async def _generate_improvement_suggestions(self, history: List[Dict]) -> List[str]:
        """生成改进建议"""
        if not history:
            return ["开始练习基础编程概念"]
        
        suggestions = []
        
        # 基于历史数据生成建议
        recent_errors = []
        for h in history[-5:]:  # 最近5次提交
            if "analysis_summary" in h and "weaknesses" in h["analysis_summary"]:
                recent_errors.extend(h["analysis_summary"]["weaknesses"])
        
        if "syntax" in str(recent_errors).lower():
            suggestions.append("加强语法基础练习")
        
        if "logic" in str(recent_errors).lower():
            suggestions.append("多练习算法思维和逻辑推理")
        
        if "style" in str(recent_errors).lower():
            suggestions.append("学习代码规范和最佳实践")
        
        if not suggestions:
            suggestions.append("继续保持良好的学习节奏")
        
        return suggestions
    
    async def _identify_skill_gaps(self, history: List[Dict]) -> Dict[str, float]:
        """识别技能缺口"""
        skill_scores = {
            "syntax": 0.0,
            "logic": 0.0,
            "style": 0.0,
            "debugging": 0.0
        }
        
        count = 0
        for h in history:
            if "analysis_summary" in h:
                count += 1
                # 这里应该有更复杂的技能评估逻辑
                # 现在使用简化版本
                base_score = h.get("score", 0) / 100.0
                for skill in skill_scores:
                    skill_scores[skill] += base_score
        
        if count > 0:
            for skill in skill_scores:
                skill_scores[skill] /= count
        
        return skill_scores
    
    async def _calculate_progress_trends(self, history: List[Dict]) -> Dict[str, Any]:
        """计算进度趋势"""
        if len(history) < 2:
            return {"trend": "insufficient_data"}
        
        scores = [h.get("score", 0) for h in history if "score" in h]
        timestamps = [h.get("submitted_at") for h in history if "submitted_at" in h]
        
        if len(scores) < 2:
            return {"trend": "insufficient_data"}
        
        # 简化的线性趋势计算
        n = len(scores)
        slope = (scores[-1] - scores[0]) / n if n > 1 else 0
        
        return {
            "trend": "improving" if slope > 0 else "declining" if slope < 0 else "stable",
            "slope": slope,
            "score_range": {"min": min(scores), "max": max(scores)},
            "recent_average": sum(scores[-5:]) / min(5, len(scores)),
            "overall_average": sum(scores) / len(scores)
        }


# 全局AI服务实例
_ai_service_instance: Optional[AITeachingService] = None


def get_ai_service_instance() -> AITeachingService:
    """获取AI服务单例"""
    global _ai_service_instance
    if _ai_service_instance is None:
        _ai_service_instance = AITeachingService()
    return _ai_service_instance


# 导出
__all__ = ["AITeachingService", "get_ai_service_instance"]