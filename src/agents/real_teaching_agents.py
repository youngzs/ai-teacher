"""
真实的AI Teaching Agents实现 - Sprint 3
使用OpenAI API提供真正的AI分析能力

Author: AI Teaching Assistant Team
Date: 2026-01-19
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
from dataclasses import dataclass, field
import json
import asyncio
import uuid

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.core.openai_client import get_openai_client, OpenAIClient
from src.models.teaching_models import (
    SubmissionData, TeachingFeedback, ProgrammingLanguage
)
from src.config.agents_config import AgentRole
from src.utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class AgentResult:
    """Agent处理结果"""
    agent_name: str
    success: bool
    data: Dict[str, Any] = field(default_factory=dict)
    error: Optional[str] = None
    processing_time: float = 0.0
    tokens_used: int = 0


class BaseTeachingAgent:
    """教学Agent基类"""

    def __init__(self, name: str, role: AgentRole, openai_client: OpenAIClient):
        self.name = name
        self.role = role
        self.client = openai_client

    async def process(self, context: Dict[str, Any]) -> AgentResult:
        """处理输入并返回结果"""
        raise NotImplementedError

    def _get_system_prompt(self) -> str:
        """获取系统提示"""
        raise NotImplementedError


class CodeAnalyzerAgent(BaseTeachingAgent):
    """代码分析Agent - 负责代码质量分析"""

    def __init__(self, openai_client: OpenAIClient):
        super().__init__("CodeAnalyzer", AgentRole.CODE_ANALYZER, openai_client)

    async def process(self, context: Dict[str, Any]) -> AgentResult:
        """分析代码质量"""
        start_time = datetime.now()

        try:
            code = context.get("code", "")
            language = context.get("language", "python")
            assignment_description = context.get("assignment_description", "")

            result = await self.client.analyze_code(
                code=code,
                language=language,
                assignment_description=assignment_description,
                student_context=context.get("student_context")
            )

            processing_time = (datetime.now() - start_time).total_seconds()

            if result["success"]:
                return AgentResult(
                    agent_name=self.name,
                    success=True,
                    data=result.get("parsed_content", {}),
                    processing_time=processing_time,
                    tokens_used=result.get("usage", {}).get("total_tokens", 0)
                )
            else:
                return AgentResult(
                    agent_name=self.name,
                    success=False,
                    error="Code analysis failed",
                    processing_time=processing_time
                )

        except Exception as e:
            logger.error(f"CodeAnalyzer error: {e}")
            return AgentResult(
                agent_name=self.name,
                success=False,
                error=str(e),
                processing_time=(datetime.now() - start_time).total_seconds()
            )


class StudentProfilerAgent(BaseTeachingAgent):
    """学生画像Agent - 分析学生学习模式"""

    def __init__(self, openai_client: OpenAIClient):
        super().__init__("StudentProfiler", AgentRole.STUDENT_PROFILER, openai_client)

    async def process(self, context: Dict[str, Any]) -> AgentResult:
        """分析学生画像"""
        start_time = datetime.now()

        try:
            student_history = context.get("student_history", [])
            current_submission = context.get("code_analysis", {})

            # 如果没有历史数据，返回默认画像
            if not student_history:
                default_profile = {
                    "competency_level": "beginner",
                    "learning_style": "visual",
                    "strengths": ["愿意尝试"],
                    "areas_for_improvement": ["需要更多练习"],
                    "recommended_approach": "step_by_step",
                    "emotional_support_level": "high"
                }
                return AgentResult(
                    agent_name=self.name,
                    success=True,
                    data=default_profile,
                    processing_time=(datetime.now() - start_time).total_seconds()
                )

            # 分析历史数据
            scores = [h.get("score", 0) for h in student_history if h.get("score")]
            avg_score = sum(scores) / len(scores) if scores else 50

            # 确定能力水平
            if avg_score >= 90:
                level = "expert"
            elif avg_score >= 80:
                level = "proficient"
            elif avg_score >= 70:
                level = "competent"
            elif avg_score >= 60:
                level = "developing"
            else:
                level = "beginner"

            # 分析进步趋势
            if len(scores) >= 3:
                recent = scores[:3]
                older = scores[3:6] if len(scores) >= 6 else scores[3:]
                recent_avg = sum(recent) / len(recent)
                older_avg = sum(older) / len(older) if older else recent_avg
                trend = "improving" if recent_avg > older_avg else "stable"
            else:
                trend = "insufficient_data"

            profile = {
                "competency_level": level,
                "average_score": round(avg_score, 1),
                "total_submissions": len(student_history),
                "progress_trend": trend,
                "learning_style": self._infer_learning_style(student_history),
                "strengths": self._identify_strengths(current_submission),
                "areas_for_improvement": self._identify_weaknesses(current_submission),
                "recommended_approach": "detailed" if level in ["beginner", "developing"] else "concise",
                "emotional_support_level": "high" if level == "beginner" else "medium"
            }

            return AgentResult(
                agent_name=self.name,
                success=True,
                data=profile,
                processing_time=(datetime.now() - start_time).total_seconds()
            )

        except Exception as e:
            logger.error(f"StudentProfiler error: {e}")
            return AgentResult(
                agent_name=self.name,
                success=False,
                error=str(e)
            )

    def _infer_learning_style(self, history: List[Dict]) -> str:
        """推断学习风格"""
        # 简化的学习风格推断
        return "visual"

    def _identify_strengths(self, analysis: Dict) -> List[str]:
        """识别优势"""
        strengths = []
        code_analysis = analysis.get("code_analysis", {})

        if code_analysis.get("syntax_score", 0) >= 80:
            strengths.append("语法准确")
        if code_analysis.get("logic_score", 0) >= 80:
            strengths.append("逻辑清晰")
        if code_analysis.get("style_score", 0) >= 80:
            strengths.append("代码风格良好")

        return strengths if strengths else ["积极尝试"]

    def _identify_weaknesses(self, analysis: Dict) -> List[str]:
        """识别需要改进的地方"""
        weaknesses = []
        code_analysis = analysis.get("code_analysis", {})

        if code_analysis.get("syntax_score", 100) < 70:
            weaknesses.append("语法基础")
        if code_analysis.get("logic_score", 100) < 70:
            weaknesses.append("程序逻辑")
        if code_analysis.get("style_score", 100) < 70:
            weaknesses.append("代码规范")

        return weaknesses if weaknesses else ["继续保持"]


class FeedbackGeneratorAgent(BaseTeachingAgent):
    """反馈生成Agent - 生成个性化教学反馈"""

    def __init__(self, openai_client: OpenAIClient):
        super().__init__("FeedbackGenerator", AgentRole.FEEDBACK_GENERATOR, openai_client)

    async def process(self, context: Dict[str, Any]) -> AgentResult:
        """生成个性化反馈"""
        start_time = datetime.now()

        try:
            code_analysis = context.get("code_analysis", {})
            student_profile = context.get("student_profile", {})

            # 使用分析结果中的反馈，或生成新的
            if "feedback" in code_analysis:
                feedback = code_analysis["feedback"]
            else:
                feedback = self._generate_feedback(code_analysis, student_profile)

            # 根据学生画像调整反馈风格
            adjusted_feedback = self._adjust_feedback_style(feedback, student_profile)

            return AgentResult(
                agent_name=self.name,
                success=True,
                data=adjusted_feedback,
                processing_time=(datetime.now() - start_time).total_seconds()
            )

        except Exception as e:
            logger.error(f"FeedbackGenerator error: {e}")
            return AgentResult(
                agent_name=self.name,
                success=False,
                error=str(e)
            )

    def _generate_feedback(self, analysis: Dict, profile: Dict) -> Dict[str, Any]:
        """生成基础反馈"""
        code_analysis = analysis.get("code_analysis", {})
        overall_score = analysis.get("overall_score", 70)

        # 根据分数生成反馈
        if overall_score >= 90:
            recognition = "优秀的代码！你展示了对编程概念的深刻理解。"
            reinforcement = "继续挑战更复杂的问题，你有成为优秀程序员的潜力！"
        elif overall_score >= 80:
            recognition = "很好的尝试！你的代码展示了扎实的基础。"
            reinforcement = "再接再厉，注意一些细节可以让代码更加完美。"
        elif overall_score >= 70:
            recognition = "不错的进展！你正在正确的道路上。"
            reinforcement = "多练习可以帮助你更加熟练，加油！"
        else:
            recognition = "感谢你的努力尝试！每一次练习都是进步。"
            reinforcement = "编程需要时间和耐心，坚持下去，你一定会进步的！"

        return {
            "recognition": recognition,
            "reconstruction": {
                "issues": code_analysis.get("suggestions", ["继续练习"]),
                "steps": ["逐步理解每个概念", "多做练习巩固知识"]
            },
            "reinforcement": reinforcement
        }

    def _adjust_feedback_style(self, feedback: Dict, profile: Dict) -> Dict[str, Any]:
        """根据学生画像调整反馈风格"""
        support_level = profile.get("emotional_support_level", "medium")

        if support_level == "high":
            # 增加更多鼓励性语言
            if isinstance(feedback.get("reinforcement"), str):
                feedback["reinforcement"] += " 记住，每个优秀的程序员都是从初学者开始的！"

        return feedback


class QualityControllerAgent(BaseTeachingAgent):
    """质量控制Agent - 验证反馈质量"""

    def __init__(self, openai_client: OpenAIClient):
        super().__init__("QualityController", AgentRole.QUALITY_CONTROLLER, openai_client)

    async def process(self, context: Dict[str, Any]) -> AgentResult:
        """验证反馈质量"""
        start_time = datetime.now()

        try:
            feedback = context.get("feedback", {})
            code_analysis = context.get("code_analysis", {})

            # 质量检查
            quality_score = 100
            issues = []

            # 检查反馈完整性
            if not feedback.get("recognition"):
                quality_score -= 20
                issues.append("缺少肯定性反馈")

            if not feedback.get("reconstruction"):
                quality_score -= 20
                issues.append("缺少改进建议")

            if not feedback.get("reinforcement"):
                quality_score -= 20
                issues.append("缺少鼓励性反馈")

            # 检查分数合理性
            overall_score = code_analysis.get("overall_score", 0)
            if overall_score < 0 or overall_score > 100:
                quality_score -= 10
                issues.append("评分超出有效范围")

            return AgentResult(
                agent_name=self.name,
                success=True,
                data={
                    "quality_score": quality_score,
                    "issues": issues,
                    "passed": quality_score >= 70,
                    "recommendation": "approved" if quality_score >= 70 else "needs_review"
                },
                processing_time=(datetime.now() - start_time).total_seconds()
            )

        except Exception as e:
            logger.error(f"QualityController error: {e}")
            return AgentResult(
                agent_name=self.name,
                success=False,
                error=str(e)
            )


class DebuggingMentorAgent(BaseTeachingAgent):
    """调试导师Agent - 提供调试指导"""

    def __init__(self, openai_client: OpenAIClient):
        super().__init__("DebuggingMentor", AgentRole.DEBUGGING_MENTOR, openai_client)

    async def process(self, context: Dict[str, Any]) -> AgentResult:
        """提供调试指导"""
        start_time = datetime.now()

        try:
            code = context.get("code", "")
            language = context.get("language", "python")
            error_message = context.get("error_message", "")
            student_question = context.get("student_question")

            result = await self.client.generate_debugging_guidance(
                code=code,
                language=language,
                error_message=error_message,
                student_question=student_question
            )

            processing_time = (datetime.now() - start_time).total_seconds()

            if result["success"]:
                try:
                    guidance = json.loads(result["content"])
                except json.JSONDecodeError:
                    guidance = {"raw_guidance": result["content"]}

                return AgentResult(
                    agent_name=self.name,
                    success=True,
                    data=guidance,
                    processing_time=processing_time,
                    tokens_used=result.get("usage", {}).get("total_tokens", 0)
                )
            else:
                return AgentResult(
                    agent_name=self.name,
                    success=False,
                    error="Debugging guidance generation failed",
                    processing_time=processing_time
                )

        except Exception as e:
            logger.error(f"DebuggingMentor error: {e}")
            return AgentResult(
                agent_name=self.name,
                success=False,
                error=str(e)
            )


class RealMultiAgentTeachingSystem:
    """
    真实的多Agent教学系统

    协调多个AI Agent完成代码分析和反馈生成
    """

    def __init__(self):
        self.openai_client: Optional[OpenAIClient] = None
        self.agents: Dict[str, BaseTeachingAgent] = {}
        self._initialized = False

    async def initialize(self):
        """初始化系统"""
        if self._initialized:
            return

        self.openai_client = await get_openai_client()

        # 创建所有Agent
        self.agents = {
            "CodeAnalyzer": CodeAnalyzerAgent(self.openai_client),
            "StudentProfiler": StudentProfilerAgent(self.openai_client),
            "FeedbackGenerator": FeedbackGeneratorAgent(self.openai_client),
            "QualityController": QualityControllerAgent(self.openai_client),
            "DebuggingMentor": DebuggingMentorAgent(self.openai_client),
        }

        self._initialized = True
        mode = "MOCK" if self.openai_client.is_mock_mode else "REAL API"
        logger.info(f"RealMultiAgentTeachingSystem initialized ({mode}) with {len(self.agents)} agents")

    @property
    def is_mock_mode(self) -> bool:
        """是否在Mock模式"""
        return self.openai_client.is_mock_mode if self.openai_client else True

    async def process_submission(self, submission_data: SubmissionData) -> TeachingFeedback:
        """
        处理学生代码提交

        Args:
            submission_data: 提交数据

        Returns:
            教学反馈结果
        """
        if not self._initialized:
            await self.initialize()

        start_time = datetime.now()
        session_id = f"session_{submission_data.student_id}_{int(start_time.timestamp())}"

        logger.info(f"Processing submission for student {submission_data.student_id}")

        # 构建初始上下文
        context = {
            "code": submission_data.code,
            "language": submission_data.language.value if isinstance(submission_data.language, ProgrammingLanguage) else submission_data.language,
            "assignment_description": submission_data.assignment_description,
            "student_id": submission_data.student_id,
            "student_context": getattr(submission_data, 'student_history', None),
            "student_message": submission_data.student_message
        }

        total_tokens = 0
        agent_results = {}

        # Step 1: 代码分析
        code_result = await self.agents["CodeAnalyzer"].process(context)
        agent_results["CodeAnalyzer"] = code_result
        if code_result.success:
            context["code_analysis"] = code_result.data
            total_tokens += code_result.tokens_used

        # Step 2: 学生画像分析
        profile_result = await self.agents["StudentProfiler"].process(context)
        agent_results["StudentProfiler"] = profile_result
        if profile_result.success:
            context["student_profile"] = profile_result.data

        # Step 3: 生成反馈
        feedback_result = await self.agents["FeedbackGenerator"].process(context)
        agent_results["FeedbackGenerator"] = feedback_result
        if feedback_result.success:
            context["feedback"] = feedback_result.data

        # Step 4: 质量控制
        qc_result = await self.agents["QualityController"].process(context)
        agent_results["QualityController"] = qc_result

        # 构建最终结果
        processing_time = (datetime.now() - start_time).total_seconds()

        code_analysis = context.get("code_analysis", {})
        feedback = context.get("feedback", {})
        student_profile = context.get("student_profile", {})
        quality_check = qc_result.data if qc_result.success else {}

        return TeachingFeedback(
            session_id=session_id,
            student_id=submission_data.student_id,
            overall_score=code_analysis.get("overall_score", 0),
            code_analysis=code_analysis.get("code_analysis", {}),
            student_profile=student_profile,
            teaching_strategy=student_profile.get("recommended_approach", "standard"),
            feedback_content=feedback,
            recommendations=code_analysis.get("learning_points", []),
            quality_score=quality_check.get("quality_score", 0),
            next_steps=feedback.get("reconstruction", {}).get("steps", []),
            estimated_completion_time=code_analysis.get("estimated_fix_time", "15-20分钟"),
            created_at=datetime.now(),
            processing_time=processing_time
        )

    async def process_debugging_session(self, submission_data: SubmissionData) -> TeachingFeedback:
        """
        处理调试会话

        Args:
            submission_data: 提交数据

        Returns:
            调试指导反馈
        """
        if not self._initialized:
            await self.initialize()

        start_time = datetime.now()
        session_id = f"debug_{submission_data.student_id}_{int(start_time.timestamp())}"

        context = {
            "code": submission_data.code,
            "language": submission_data.language.value if isinstance(submission_data.language, ProgrammingLanguage) else submission_data.language,
            "error_message": submission_data.assignment_description,  # 在调试模式下，description存储错误信息
            "student_question": submission_data.student_message
        }

        # 使用调试导师
        debug_result = await self.agents["DebuggingMentor"].process(context)

        processing_time = (datetime.now() - start_time).total_seconds()

        guidance = debug_result.data if debug_result.success else {}

        return TeachingFeedback(
            session_id=session_id,
            student_id=submission_data.student_id,
            overall_score=0,  # 调试模式不评分
            code_analysis=guidance.get("error_analysis", {}),
            student_profile={},
            teaching_strategy="debugging",
            feedback_content={
                "guided_questions": guidance.get("guided_questions", []),
                "hints": guidance.get("hints", []),
                "learning_opportunity": guidance.get("learning_opportunity", ""),
                "debugging_steps": guidance.get("debugging_steps", [])
            },
            recommendations=guidance.get("similar_patterns", []),
            quality_score=85,
            next_steps=guidance.get("debugging_steps", []),
            estimated_completion_time="10-15分钟",
            created_at=datetime.now(),
            processing_time=processing_time
        )


# 全局实例
_teaching_system: Optional[RealMultiAgentTeachingSystem] = None


async def get_teaching_system() -> RealMultiAgentTeachingSystem:
    """获取教学系统单例"""
    global _teaching_system

    if _teaching_system is None:
        _teaching_system = RealMultiAgentTeachingSystem()
        await _teaching_system.initialize()

    return _teaching_system
