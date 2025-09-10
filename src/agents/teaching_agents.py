"""
AI教学助手系统 - 核心Teaching Agents实现
基于AutoGen框架的专业化教学智能体

Author: AI Architecture Expert  
Date: 2025-09-09
"""

from typing import Dict, Any, List, Optional, Tuple
import json
import asyncio
import logging
from datetime import datetime

try:
    from autogen import AssistantAgent, UserProxyAgent, GroupChat, GroupChatManager
except ImportError:
    # 如果autogen未安装，提供mock类以便开发时使用
    print("Warning: autogen not installed. Using mock classes for development.")
    class AssistantAgent:
        def __init__(self, name, system_message, llm_config, **kwargs):
            self.name = name
            self.system_message = system_message
            self.llm_config = llm_config
    
    class UserProxyAgent:
        def __init__(self, name, **kwargs):
            self.name = name
    
    class GroupChat:
        def __init__(self, agents, messages, max_round=10, **kwargs):
            self.agents = agents
            self.messages = messages
            self.max_round = max_round
    
    class GroupChatManager:
        def __init__(self, groupchat, **kwargs):
            self.groupchat = groupchat
        
        async def a_initiate_chat(self, message, max_turns=None):
            # Mock implementation for development
            return {"summary": "Mock response"}

from ..config.agents_config import AgentConfigurations, AgentRole, SYSTEM_CONFIG
from ..models.teaching_models import SubmissionData, AnalysisResult, TeachingFeedback
from ..utils.code_analyzer import CodeExecutor
from ..utils.logger import get_logger

logger = get_logger(__name__)

class TeachingAgentFactory:
    """教学智能体工厂类"""
    
    @staticmethod
    def create_agent(agent_role: AgentRole) -> AssistantAgent:
        """创建指定角色的Agent"""
        config = AgentConfigurations.get_agent_config(agent_role)
        
        if not config:
            raise ValueError(f"No configuration found for agent role: {agent_role}")
        
        return AssistantAgent(
            name=config["name"],
            system_message=config["system_message"],
            llm_config=config["llm_config"],
            max_consecutive_auto_reply=config.get("max_consecutive_auto_reply", 3),
            human_input_mode="NEVER"
        )
    
    @staticmethod
    def create_all_agents() -> Dict[str, AssistantAgent]:
        """创建所有教学Agent"""
        agents = {}
        for role in AgentRole:
            try:
                agent = TeachingAgentFactory.create_agent(role)
                agents[role.value] = agent
                logger.info(f"Created agent: {role.value}")
            except Exception as e:
                logger.error(f"Failed to create agent {role.value}: {e}")
                
        return agents

class TeachingGroupChatManager(GroupChatManager):
    """自定义的教学群聊管理器"""
    
    def __init__(self, groupchat, **kwargs):
        super().__init__(groupchat, **kwargs)
        self.conversation_history = []
        
    def select_speaker(self, last_speaker=None, selector=None):
        """自定义Agent发言顺序，确保教学逻辑的连贯性"""
        
        # 定义教学工作流的标准顺序
        teaching_flow = [
            "CodeAnalyzer",      # 先分析代码
            "StudentProfiler",   # 再分析学生
            "PedagogyExpert",   # 然后确定教学策略
            "FeedbackGenerator", # 生成反馈内容
            "QualityController", # 最后质量检查
        ]
        
        if last_speaker is None:
            # 开始对话，选择第一个Agent
            return next((agent for agent in self.groupchat.agents 
                        if agent.name == teaching_flow[0]), None)
        
        try:
            current_index = teaching_flow.index(last_speaker.name)
            if current_index < len(teaching_flow) - 1:
                next_agent_name = teaching_flow[current_index + 1]
                return next((agent for agent in self.groupchat.agents 
                            if agent.name == next_agent_name), None)
        except (ValueError, IndexError):
            pass
            
        return None  # 流程结束
    
    def _extract_agent_response(self, chat_history: List[Dict]) -> Dict[str, Any]:
        """从对话历史中提取每个Agent的响应"""
        agent_responses = {}
        
        for message in chat_history:
            speaker = message.get('name', 'unknown')
            content = message.get('content', '')
            
            # 尝试解析JSON响应
            try:
                parsed_content = json.loads(content)
                agent_responses[speaker] = parsed_content
            except json.JSONDecodeError:
                # 如果不是JSON，保存原始文本
                agent_responses[speaker] = {"raw_response": content}
        
        return agent_responses

class MultiAgentTeachingSystem:
    """多智能体教学系统核心类"""
    
    def __init__(self, course_type: str = "python_basics"):
        """
        初始化多智能体教学系统
        
        Args:
            course_type: 课程类型 (python_basics, c_programming等)
        """
        self.course_type = course_type
        self.agents = TeachingAgentFactory.create_all_agents()
        self.code_executor = CodeExecutor()
        self.session_history = {}
        
        logger.info(f"Initialized TeachingSystem for {course_type} with {len(self.agents)} agents")
    
    async def process_submission(self, submission_data: SubmissionData) -> TeachingFeedback:
        """
        处理学生提交的作业，生成教学反馈
        
        Args:
            submission_data: 学生提交的数据
            
        Returns:
            TeachingFeedback: 结构化的教学反馈
        """
        try:
            logger.info(f"Processing submission from student {submission_data.student_id}")
            
            # 创建教学会话
            session_id = f"session_{submission_data.student_id}_{int(datetime.now().timestamp())}"
            
            # 预处理：代码执行和基础分析
            execution_result = await self._execute_code_safely(submission_data.code)
            
            # 创建群聊进行多Agent协作
            group_chat = GroupChat(
                agents=list(self.agents.values()),
                messages=[],
                max_round=6,
                speaker_selection_method="manual"
            )
            
            manager = TeachingGroupChatManager(
                groupchat=group_chat,
                llm_config={"model": "gpt-4", "temperature": 0.3}
            )
            
            # 构建初始提示信息
            initial_message = self._build_analysis_prompt(submission_data, execution_result)
            
            # 启动多Agent协作对话
            chat_result = await manager.a_initiate_chat(
                message=initial_message,
                max_turns=6
            )
            
            # 提取和整合各Agent的分析结果
            agent_responses = manager._extract_agent_response(chat_result.get("chat_history", []))
            
            # 生成最终的教学反馈
            final_feedback = self._synthesize_feedback(agent_responses, submission_data)
            
            # 记录会话历史
            self.session_history[session_id] = {
                "submission": submission_data,
                "agent_responses": agent_responses,
                "feedback": final_feedback,
                "timestamp": datetime.now()
            }
            
            logger.info(f"Successfully processed submission {session_id}")
            return final_feedback
            
        except Exception as e:
            logger.error(f"Error processing submission: {e}")
            return self._generate_error_feedback(str(e))
    
    async def process_debugging_session(self, submission_data: SubmissionData) -> TeachingFeedback:
        """
        专门处理调试辅导场景
        
        Args:
            submission_data: 包含错误代码的提交数据
            
        Returns:
            TeachingFeedback: 调试指导反馈
        """
        try:
            logger.info(f"Starting debugging session for student {submission_data.student_id}")
            
            # 选择调试专门的Agent组合
            debugging_agents = [
                self.agents[AgentRole.CODE_ANALYZER.value],
                self.agents[AgentRole.DEBUGGING_MENTOR.value],
                self.agents[AgentRole.STUDENT_PROFILER.value],
                self.agents[AgentRole.FEEDBACK_GENERATOR.value],
                self.agents[AgentRole.QUALITY_CONTROLLER.value]
            ]
            
            group_chat = GroupChat(
                agents=debugging_agents,
                messages=[],
                max_round=5,
                speaker_selection_method="manual"
            )
            
            manager = TeachingGroupChatManager(
                groupchat=group_chat,
                llm_config={"model": "gpt-4", "temperature": 0.2}
            )
            
            # 构建调试专用提示
            debugging_message = self._build_debugging_prompt(submission_data)
            
            # 启动调试指导对话
            chat_result = await manager.a_initiate_chat(
                message=debugging_message,
                max_turns=5
            )
            
            # 提取调试指导结果
            agent_responses = manager._extract_agent_response(chat_result.get("chat_history", []))
            
            # 生成调试指导反馈
            debugging_feedback = self._synthesize_debugging_feedback(agent_responses, submission_data)
            
            logger.info(f"Completed debugging session for student {submission_data.student_id}")
            return debugging_feedback
            
        except Exception as e:
            logger.error(f"Error in debugging session: {e}")
            return self._generate_error_feedback(f"调试会话错误: {str(e)}")
    
    async def process_personalized_learning(self, submission_data: SubmissionData, learning_history: List[Dict]) -> TeachingFeedback:
        """
        个性化学习路径推荐场景
        
        Args:
            submission_data: 当前提交数据
            learning_history: 学生历史学习记录
            
        Returns:
            TeachingFeedback: 个性化学习建议
        """
        try:
            logger.info(f"Generating personalized learning path for student {submission_data.student_id}")
            
            # 选择个性化学习专门的Agent组合
            personalization_agents = [
                self.agents[AgentRole.STUDENT_PROFILER.value],
                self.agents[AgentRole.PEDAGOGY_EXPERT.value],
                self.agents[AgentRole.FEEDBACK_GENERATOR.value],
                self.agents[AgentRole.QUALITY_CONTROLLER.value]
            ]
            
            group_chat = GroupChat(
                agents=personalization_agents,
                messages=[],
                max_round=4,
                speaker_selection_method="manual"
            )
            
            manager = TeachingGroupChatManager(
                groupchat=group_chat,
                llm_config={"model": "gpt-4", "temperature": 0.3}
            )
            
            # 构建个性化学习提示
            personalization_message = self._build_personalization_prompt(submission_data, learning_history)
            
            # 启动个性化学习对话
            chat_result = await manager.a_initiate_chat(
                message=personalization_message,
                max_turns=4
            )
            
            # 提取个性化建议结果
            agent_responses = manager._extract_agent_response(chat_result.get("chat_history", []))
            
            # 生成个性化学习反馈
            personalized_feedback = self._synthesize_personalized_feedback(agent_responses, submission_data)
            
            logger.info(f"Generated personalized learning path for student {submission_data.student_id}")
            return personalized_feedback
            
        except Exception as e:
            logger.error(f"Error in personalized learning session: {e}")
            return self._generate_error_feedback(f"个性化学习会话错误: {str(e)}")
    
    async def _execute_code_safely(self, code: str) -> Dict[str, Any]:
        """安全执行学生代码并返回结果"""
        try:
            result = await self.code_executor.execute_safely(code, timeout=10)
            return {
                "success": result.get("success", False),
                "output": result.get("output", ""),
                "error": result.get("error", ""),
                "execution_time": result.get("execution_time", 0)
            }
        except Exception as e:
            logger.warning(f"Code execution failed: {e}")
            return {
                "success": False,
                "output": "",
                "error": str(e),
                "execution_time": 0
            }
    
    def _build_analysis_prompt(self, submission_data: SubmissionData, execution_result: Dict) -> str:
        """构建代码分析提示信息"""
        return f"""
请分析以下学生编程作业提交：

**学生信息：**
- 学生ID: {submission_data.student_id}
- 课程: {self.course_type}
- 提交时间: {submission_data.submitted_at}

**作业要求：**
{submission_data.assignment_description}

**学生代码：**
```{submission_data.language}
{submission_data.code}
```

**代码执行结果：**
- 执行成功: {execution_result['success']}
- 输出结果: {execution_result['output']}
- 错误信息: {execution_result['error']}
- 执行时间: {execution_result['execution_time']}ms

**学生历史表现：**
{json.dumps(submission_data.student_history, ensure_ascii=False, indent=2)}

请各位专家按照既定的分析流程，为这位学生提供专业、个性化的教学反馈。
"""
    
    def _build_debugging_prompt(self, submission_data: SubmissionData) -> str:
        """构建调试指导提示信息"""
        return f"""
学生遇到编程问题，需要调试指导：

**学生信息：**
- 学生ID: {submission_data.student_id}  
- 编程经验: {submission_data.student_history.get('programming_experience', '初学者')}

**问题代码：**
```{submission_data.language}
{submission_data.code}
```

**遇到的问题：**
{submission_data.assignment_description}

**学生反馈：**
"{submission_data.student_message}"

请DebuggingMentor主导，通过苏格拉底式提问引导学生自主发现和解决问题，培养调试思维。
"""
    
    def _build_personalization_prompt(self, submission_data: SubmissionData, learning_history: List[Dict]) -> str:
        """构建个性化学习提示信息"""
        return f"""
为学生制定个性化学习路径：

**学生当前状态：**
- 学生ID: {submission_data.student_id}
- 当前代码水平: 请根据代码质量评估

**当前提交代码：**
```{submission_data.language}
{submission_data.code}
```

**历史学习记录：**
{json.dumps(learning_history, ensure_ascii=False, indent=2)}

请分析学生的学习模式、能力水平和兴趣特点，制定个性化的学习路径和资源推荐。
"""
    
    def _synthesize_feedback(self, agent_responses: Dict[str, Any], submission_data: SubmissionData) -> TeachingFeedback:
        """综合各Agent响应，生成最终教学反馈"""
        
        # 提取各Agent的分析结果
        code_analysis = agent_responses.get("CodeAnalyzer", {})
        student_profile = agent_responses.get("StudentProfiler", {})
        teaching_strategy = agent_responses.get("PedagogyExpert", {})
        generated_feedback = agent_responses.get("FeedbackGenerator", {})
        quality_check = agent_responses.get("QualityController", {})
        
        # 构建综合反馈
        return TeachingFeedback(
            session_id=f"session_{submission_data.student_id}_{int(datetime.now().timestamp())}",
            student_id=submission_data.student_id,
            overall_score=code_analysis.get("syntax_score", 0) + code_analysis.get("logic_score", 0) / 2,
            code_analysis=code_analysis,
            student_profile=student_profile,
            teaching_strategy=teaching_strategy.get("strategy_type", "HINT"),
            feedback_content=generated_feedback.get("feedback_structure", {}),
            recommendations=generated_feedback.get("personalization", {}),
            quality_score=quality_check.get("quality_assessment", {}).get("overall_score", 75),
            next_steps=generated_feedback.get("feedback_structure", {}).get("resources", []),
            estimated_completion_time=generated_feedback.get("personalization", {}).get("estimated_time", "15-20分钟"),
            created_at=datetime.now()
        )
    
    def _synthesize_debugging_feedback(self, agent_responses: Dict[str, Any], submission_data: SubmissionData) -> TeachingFeedback:
        """综合调试指导反馈"""
        
        debugging_guidance = agent_responses.get("DebuggingMentor", {})
        code_analysis = agent_responses.get("CodeAnalyzer", {})
        
        return TeachingFeedback(
            session_id=f"debug_{submission_data.student_id}_{int(datetime.now().timestamp())}",
            student_id=submission_data.student_id,
            overall_score=0,  # 调试场景不评分
            code_analysis=code_analysis,
            student_profile=agent_responses.get("StudentProfiler", {}),
            teaching_strategy="DEBUGGING",
            feedback_content=debugging_guidance.get("debugging_guidance", {}),
            recommendations=debugging_guidance.get("skill_development", {}),
            quality_score=agent_responses.get("QualityController", {}).get("quality_assessment", {}).get("overall_score", 80),
            next_steps=debugging_guidance.get("debugging_guidance", {}).get("debugging_steps", []),
            estimated_completion_time="20-30分钟",
            created_at=datetime.now()
        )
    
    def _synthesize_personalized_feedback(self, agent_responses: Dict[str, Any], submission_data: SubmissionData) -> TeachingFeedback:
        """综合个性化学习反馈"""
        
        student_profile = agent_responses.get("StudentProfiler", {})
        teaching_strategy = agent_responses.get("PedagogyExpert", {})
        
        return TeachingFeedback(
            session_id=f"personal_{submission_data.student_id}_{int(datetime.now().timestamp())}",
            student_id=submission_data.student_id,
            overall_score=0,  # 个性化推荐不评分
            code_analysis={},
            student_profile=student_profile,
            teaching_strategy=teaching_strategy.get("strategy_type", "PERSONALIZED"),
            feedback_content=agent_responses.get("FeedbackGenerator", {}).get("feedback_structure", {}),
            recommendations=student_profile.get("recommendations", {}),
            quality_score=agent_responses.get("QualityController", {}).get("quality_assessment", {}).get("overall_score", 85),
            next_steps=student_profile.get("recommendations", {}).get("immediate_focus", []),
            estimated_completion_time="1-2小时",
            created_at=datetime.now()
        )
    
    def _generate_error_feedback(self, error_message: str) -> TeachingFeedback:
        """生成错误反馈"""
        return TeachingFeedback(
            session_id=f"error_{int(datetime.now().timestamp())}",
            student_id="unknown",
            overall_score=0,
            code_analysis={"error": error_message},
            student_profile={},
            teaching_strategy="ERROR_HANDLING",
            feedback_content={
                "recognition": "抱歉，系统在处理您的提交时遇到了技术问题。",
                "reconstruction": {
                    "critical_issues": [{"issue": "系统错误", "solution": "请联系技术支持", "priority": "high"}]
                }
            },
            recommendations={},
            quality_score=0,
            next_steps=["联系技术支持", "重新提交代码"],
            estimated_completion_time="5分钟",
            created_at=datetime.now()
        )

# 使用示例和测试用例将在后续模块中实现