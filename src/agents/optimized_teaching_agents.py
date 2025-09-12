"""
AI教学助手系统 - 优化的Teaching Agents实现
Sprint 2 性能优化版本：高并发、低延迟、智能缓存

Author: AI Architecture Expert  
Date: 2025-09-11
Version: Sprint 2 - Performance Optimization
"""

from typing import Dict, Any, List, Optional, Tuple, Callable, Union
import json
import asyncio
import logging
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from concurrent.futures import ThreadPoolExecutor, as_completed
import hashlib
import time
from functools import wraps
import aiohttp
import redis.asyncio as redis
from collections import defaultdict, deque

# 性能优化导入
try:
    from autogen import AssistantAgent, UserProxyAgent, GroupChat, GroupChatManager
    AUTOGEN_AVAILABLE = True
except ImportError:
    AUTOGEN_AVAILABLE = False
    print("Warning: autogen not installed. Using optimized mock classes for development.")
    
    class AssistantAgent:
        def __init__(self, name, system_message, llm_config, **kwargs):
            self.name = name
            self.system_message = system_message
            self.llm_config = llm_config
            self._setup_mock_response()
            
        def _setup_mock_response(self):
            """设置模拟响应"""
            agent_responses = {
                "CodeAnalyzer": {
                    "syntax_analysis": {"score": 85, "errors": ["Minor indentation issue"], "warnings": ["Consider adding comments"]},
                    "logic_analysis": {"score": 90, "algorithm_correctness": "Mostly correct", "suggestions": ["Handle edge cases"]},
                    "style_analysis": {"score": 80, "issues": ["Variable naming"], "best_practices": ["Use meaningful names"]},
                    "performance_analysis": {"time_complexity": "O(n)", "space_complexity": "O(1)"},
                    "overall_assessment": {"total_score": 85, "level": "intermediate", "main_strengths": ["Good logic"], "main_weaknesses": ["Code style"]}
                },
                "PedagogyExpert": {
                    "strategy_recommendation": {"primary_strategy": "HINT", "reasoning": "Student shows good understanding", "confidence": 0.8},
                    "cognitive_analysis": {"student_level": "advanced_beginner", "learning_obstacles": ["Syntax precision"]},
                    "pedagogical_design": {"learning_objectives": ["Improve code quality"], "feedback_structure": {"recognition": "Good problem-solving approach", "reconstruction": "Focus on code style", "reflection": "How can you make code more readable?"}}
                },
                "StudentProfiler": {
                    "competency_profile": {"overall_level": "advanced_beginner", "skill_areas": {"syntax_mastery": 75, "problem_solving": 85}},
                    "learning_style": {"preferred_feedback": "step-by-step", "challenge_preference": "moderate"},
                    "personalization_recommendations": {"content_difficulty": "current", "feedback_frequency": "normal"}
                },
                "FeedbackGenerator": {
                    "feedback_structure": {
                        "recognition": {"positive_aspects": ["Clear problem approach"], "progress_acknowledgment": "Good improvement"},
                        "reconstruction": {"critical_issues": [{"issue": "Code style", "solution": "Add more comments", "priority": "medium"}]},
                        "reflection": {"thinking_questions": ["What makes code readable?"]}
                    },
                    "personalization": {"estimated_time": "15 minutes"}
                },
                "QualityController": {
                    "quality_assessment": {"overall_score": 88, "dimension_scores": {"technical_accuracy": 90, "pedagogical_effectiveness": 85}},
                    "approval_status": {"approved": True, "confidence_level": 0.88}
                },
                "DebuggingMentor": {
                    "debugging_guidance": {"problem_analysis": {"error_category": "logic", "complexity_level": 2}},
                    "skill_development": {"current_debugging_level": 2, "targeted_skills": ["Error tracing"]}
                }
            }
            self._mock_response = agent_responses.get(self.name, {"mock": "response"})
            
        async def a_generate_reply(self, messages=None, sender=None, config=None):
            """异步生成回复的模拟实现"""
            await asyncio.sleep(0.1)  # 模拟网络延迟
            return json.dumps(self._mock_response, ensure_ascii=False)
    
    class GroupChat:
        def __init__(self, agents, messages, max_round=10, **kwargs):
            self.agents = agents
            self.messages = messages
            self.max_round = max_round
    
    class GroupChatManager:
        def __init__(self, groupchat, **kwargs):
            self.groupchat = groupchat
        
        async def a_initiate_chat(self, message, max_turns=None):
            """模拟群聊对话"""
            agent_responses = {}
            for agent in self.groupchat.agents:
                response = await agent.a_generate_reply()
                agent_responses[agent.name] = json.loads(response)
            
            return {
                "summary": "Optimized mock analysis completed",
                "chat_history": [
                    {"name": agent.name, "content": json.dumps(response)}
                    for agent, response in zip(self.groupchat.agents, agent_responses.values())
                ],
                "agent_responses": agent_responses
            }

from ..config.optimized_agents_config import (
    optimized_config_manager, AgentRole, ModelProvider, AgentConfig
)
from ..models.teaching_models import SubmissionData, AnalysisResult, TeachingFeedback
from ..utils.code_analyzer import CodeExecutor
from ..utils.logger import get_logger

logger = get_logger(__name__)

@dataclass
class PerformanceMetrics:
    """性能指标数据类"""
    response_time: float
    memory_usage: float
    cache_hit_rate: float
    error_rate: float
    concurrent_requests: int
    timestamp: datetime

class PerformanceMonitor:
    """性能监控器"""
    
    def __init__(self):
        self.metrics_history = deque(maxlen=1000)  # 保存最近1000条记录
        self.response_times = deque(maxlen=100)
        self.error_count = 0
        self.total_requests = 0
        
    def record_request(self, response_time: float, memory_usage: float = 0, 
                      cache_hit: bool = False, error: bool = False):
        """记录请求性能指标"""
        self.total_requests += 1
        if error:
            self.error_count += 1
            
        self.response_times.append(response_time)
        
        metrics = PerformanceMetrics(
            response_time=response_time,
            memory_usage=memory_usage,
            cache_hit_rate=1.0 if cache_hit else 0.0,
            error_rate=self.error_count / self.total_requests,
            concurrent_requests=1,  # 简化版
            timestamp=datetime.now()
        )
        self.metrics_history.append(metrics)
        
    def get_performance_summary(self) -> Dict[str, Any]:
        """获取性能摘要"""
        if not self.response_times:
            return {"status": "no_data"}
            
        avg_response_time = sum(self.response_times) / len(self.response_times)
        p95_response_time = sorted(self.response_times)[int(len(self.response_times) * 0.95)]
        
        return {
            "avg_response_time": avg_response_time,
            "p95_response_time": p95_response_time,
            "error_rate": self.error_count / max(self.total_requests, 1),
            "total_requests": self.total_requests,
            "cache_efficiency": "not_implemented"  # 后续实现
        }

class IntelligentCache:
    """智能缓存系统"""
    
    def __init__(self, max_size: int = 1000, ttl: int = 3600):
        self.cache: Dict[str, Tuple[Any, datetime]] = {}
        self.max_size = max_size
        self.ttl = ttl  # 生存时间(秒)
        self.hit_count = 0
        self.miss_count = 0
        
    def _generate_key(self, submission_data: SubmissionData, workflow_type: str) -> str:
        """生成缓存键"""
        content = f"{submission_data.code}_{submission_data.language}_{workflow_type}"
        return hashlib.md5(content.encode()).hexdigest()
        
    def get(self, key: str) -> Optional[Any]:
        """获取缓存内容"""
        if key in self.cache:
            data, timestamp = self.cache[key]
            if datetime.now() - timestamp < timedelta(seconds=self.ttl):
                self.hit_count += 1
                return data
            else:
                del self.cache[key]  # 过期删除
                
        self.miss_count += 1
        return None
        
    def set(self, key: str, value: Any):
        """设置缓存内容"""
        if len(self.cache) >= self.max_size:
            # 简单LRU: 删除最旧的条目
            oldest_key = min(self.cache.keys(), 
                           key=lambda k: self.cache[k][1])
            del self.cache[oldest_key]
            
        self.cache[key] = (value, datetime.now())
        
    def get_stats(self) -> Dict[str, Any]:
        """获取缓存统计"""
        total_requests = self.hit_count + self.miss_count
        hit_rate = self.hit_count / max(total_requests, 1)
        
        return {
            "hit_rate": hit_rate,
            "total_requests": total_requests,
            "cache_size": len(self.cache),
            "max_size": self.max_size
        }

class OptimizedTeachingAgentFactory:
    """优化的教学智能体工厂"""
    
    def __init__(self):
        self.agent_pool: Dict[str, List[AssistantAgent]] = defaultdict(list)
        self.config_manager = optimized_config_manager
        self.performance_mode = "balanced"  # speed, balanced, accuracy
        
    async def create_optimized_agent(self, agent_role: AgentRole, 
                                   performance_mode: str = "balanced") -> AssistantAgent:
        """创建优化的Agent实例"""
        try:
            # 从配置管理器获取优化配置
            if agent_role == AgentRole.CODE_ANALYZER:
                config = self.config_manager.get_code_analyzer_config(performance_mode)
            elif agent_role == AgentRole.PEDAGOGY_EXPERT:
                config = self.config_manager.get_pedagogy_expert_config(performance_mode)
            elif agent_role == AgentRole.STUDENT_PROFILER:
                config = self.config_manager.get_student_profiler_config(performance_mode)
            elif agent_role == AgentRole.FEEDBACK_GENERATOR:
                config = self.config_manager.get_feedback_generator_config(performance_mode)
            elif agent_role == AgentRole.QUALITY_CONTROLLER:
                config = self.config_manager.get_quality_controller_config(performance_mode)
            elif agent_role == AgentRole.DEBUGGING_MENTOR:
                config = self.config_manager.get_debugging_mentor_config(performance_mode)
            else:
                raise ValueError(f"Unsupported agent role: {agent_role}")
                
            # 验证配置
            validation_result = await self.config_manager.validate_configuration(config)
            if not validation_result["valid"]:
                logger.warning(f"Agent configuration validation failed: {validation_result}")
                
            # 创建Agent实例
            agent = AssistantAgent(
                name=config.name,
                system_message=config.system_message,
                llm_config=config.llm_config.to_autogen_config(),
                max_consecutive_auto_reply=config.max_consecutive_auto_reply,
                human_input_mode=config.human_input_mode,
                code_execution_config=config.code_execution_config
            )
            
            logger.info(f"Created optimized agent: {config.name} in {performance_mode} mode")
            return agent
            
        except Exception as e:
            logger.error(f"Failed to create optimized agent {agent_role}: {e}")
            raise
            
    async def get_agent_pool(self, workflow_type: str = "standard") -> Dict[str, AssistantAgent]:
        """获取Agent池 - 根据工作流类型优化Agent组合"""
        if workflow_type == "debugging":
            roles = [
                AgentRole.CODE_ANALYZER,
                AgentRole.DEBUGGING_MENTOR, 
                AgentRole.STUDENT_PROFILER,
                AgentRole.FEEDBACK_GENERATOR,
                AgentRole.QUALITY_CONTROLLER
            ]
            performance_mode = "balanced"
        elif workflow_type == "quick_analysis":
            roles = [
                AgentRole.CODE_ANALYZER,
                AgentRole.FEEDBACK_GENERATOR,
                AgentRole.QUALITY_CONTROLLER
            ]
            performance_mode = "speed"
        else:  # standard workflow
            roles = [
                AgentRole.CODE_ANALYZER,
                AgentRole.PEDAGOGY_EXPERT,
                AgentRole.STUDENT_PROFILER,
                AgentRole.FEEDBACK_GENERATOR,
                AgentRole.QUALITY_CONTROLLER
            ]
            performance_mode = self.performance_mode
            
        agents = {}
        tasks = []
        
        # 并发创建所有Agent
        for role in roles:
            task = self.create_optimized_agent(role, performance_mode)
            tasks.append((role, task))
            
        # 等待所有Agent创建完成
        for role, task in tasks:
            try:
                agent = await task
                agents[role.value] = agent
            except Exception as e:
                logger.error(f"Failed to create agent {role}: {e}")
                
        return agents

class OptimizedGroupChatManager(GroupChatManager):
    """优化的群聊管理器 - 支持并发和智能路由"""
    
    def __init__(self, groupchat, **kwargs):
        super().__init__(groupchat, **kwargs)
        self.conversation_history = []
        self.performance_monitor = PerformanceMonitor()
        self.response_cache = IntelligentCache()
        
    async def optimized_initiate_chat(self, message: str, workflow_type: str = "standard", 
                                    max_turns: Optional[int] = None) -> Dict[str, Any]:
        """优化的对话启动 - 支持并发处理"""
        start_time = time.time()
        
        try:
            # 检查缓存
            cache_key = hashlib.md5(f"{message}_{workflow_type}".encode()).hexdigest()
            cached_result = self.response_cache.get(cache_key)
            
            if cached_result:
                logger.info("Cache hit for optimized chat")
                self.performance_monitor.record_request(
                    response_time=time.time() - start_time,
                    cache_hit=True
                )
                return cached_result
                
            # 根据工作流类型选择最优的执行策略
            if workflow_type == "quick_analysis":
                result = await self._execute_quick_workflow(message)
            elif workflow_type == "debugging":
                result = await self._execute_debugging_workflow(message)
            else:
                result = await self._execute_standard_workflow(message)
                
            # 缓存结果
            self.response_cache.set(cache_key, result)
            
            # 记录性能指标
            response_time = time.time() - start_time
            self.performance_monitor.record_request(response_time=response_time)
            
            logger.info(f"Optimized chat completed in {response_time:.2f}s")
            return result
            
        except Exception as e:
            response_time = time.time() - start_time
            self.performance_monitor.record_request(
                response_time=response_time,
                error=True
            )
            logger.error(f"Optimized chat failed: {e}")
            raise
            
    async def _execute_quick_workflow(self, message: str) -> Dict[str, Any]:
        """快速分析工作流 - 并发执行关键分析"""
        quick_agents = [
            agent for agent in self.groupchat.agents 
            if agent.name in ["CodeAnalyzer", "FeedbackGenerator", "QualityController"]
        ]
        
        # 并发执行分析
        tasks = []
        for agent in quick_agents:
            task = agent.a_generate_reply(messages=[{"content": message}])
            tasks.append((agent.name, task))
            
        agent_responses = {}
        for agent_name, task in tasks:
            try:
                response = await task
                agent_responses[agent_name] = json.loads(response) if isinstance(response, str) else response
            except Exception as e:
                logger.error(f"Quick workflow agent {agent_name} failed: {e}")
                agent_responses[agent_name] = {"error": str(e)}
                
        return {
            "workflow_type": "quick_analysis",
            "agent_responses": agent_responses,
            "summary": "Quick analysis completed",
            "performance": "optimized_concurrent"
        }
        
    async def _execute_debugging_workflow(self, message: str) -> Dict[str, Any]:
        """调试工作流 - 按序执行但带超时控制"""
        debugging_sequence = ["CodeAnalyzer", "DebuggingMentor", "StudentProfiler", "FeedbackGenerator", "QualityController"]
        agent_responses = {}
        
        for agent_name in debugging_sequence:
            agent = next((a for a in self.groupchat.agents if a.name == agent_name), None)
            if not agent:
                continue
                
            try:
                # 每个Agent都有超时控制
                response = await asyncio.wait_for(
                    agent.a_generate_reply(messages=[{"content": message}]),
                    timeout=15.0  # 15秒超时
                )
                agent_responses[agent_name] = json.loads(response) if isinstance(response, str) else response
                
                # 动态调整后续Agent的输入(传递上下文)
                if agent_name == "CodeAnalyzer" and agent_responses[agent_name]:
                    message += f"\n\n代码分析结果：{json.dumps(agent_responses[agent_name], ensure_ascii=False)}"
                    
            except asyncio.TimeoutError:
                logger.warning(f"Debugging agent {agent_name} timed out")
                agent_responses[agent_name] = {"error": "timeout", "timeout_duration": 15.0}
            except Exception as e:
                logger.error(f"Debugging agent {agent_name} failed: {e}")
                agent_responses[agent_name] = {"error": str(e)}
                
        return {
            "workflow_type": "debugging",
            "agent_responses": agent_responses,
            "summary": "Debugging workflow completed with optimized sequencing",
            "performance": "optimized_sequential_with_timeout"
        }
        
    async def _execute_standard_workflow(self, message: str) -> Dict[str, Any]:
        """标准工作流 - 混合并发和顺序执行"""
        # 第一阶段：并发执行分析类Agent
        analysis_agents = [a for a in self.groupchat.agents if a.name in ["CodeAnalyzer", "StudentProfiler"]]
        analysis_tasks = [(agent.name, agent.a_generate_reply(messages=[{"content": message}])) for agent in analysis_agents]
        
        agent_responses = {}
        
        # 等待分析阶段完成
        for agent_name, task in analysis_tasks:
            try:
                response = await asyncio.wait_for(task, timeout=20.0)
                agent_responses[agent_name] = json.loads(response) if isinstance(response, str) else response
            except Exception as e:
                logger.error(f"Analysis agent {agent_name} failed: {e}")
                agent_responses[agent_name] = {"error": str(e)}
                
        # 第二阶段：基于分析结果的策略制定
        strategy_context = message + f"\n\n分析结果：{json.dumps(agent_responses, ensure_ascii=False)}"
        strategy_agent = next((a for a in self.groupchat.agents if a.name == "PedagogyExpert"), None)
        
        if strategy_agent:
            try:
                response = await asyncio.wait_for(
                    strategy_agent.a_generate_reply(messages=[{"content": strategy_context}]),
                    timeout=20.0
                )
                agent_responses["PedagogyExpert"] = json.loads(response) if isinstance(response, str) else response
            except Exception as e:
                logger.error(f"Strategy agent failed: {e}")
                agent_responses["PedagogyExpert"] = {"error": str(e)}
                
        # 第三阶段：并发执行反馈生成和质量控制
        final_context = strategy_context + f"\n\n教学策略：{json.dumps(agent_responses.get('PedagogyExpert', {}), ensure_ascii=False)}"
        final_agents = [a for a in self.groupchat.agents if a.name in ["FeedbackGenerator", "QualityController"]]
        final_tasks = [(agent.name, agent.a_generate_reply(messages=[{"content": final_context}])) for agent in final_agents]
        
        for agent_name, task in final_tasks:
            try:
                response = await asyncio.wait_for(task, timeout=25.0)
                agent_responses[agent_name] = json.loads(response) if isinstance(response, str) else response
            except Exception as e:
                logger.error(f"Final agent {agent_name} failed: {e}")
                agent_responses[agent_name] = {"error": str(e)}
                
        return {
            "workflow_type": "standard",
            "agent_responses": agent_responses,
            "summary": "Standard workflow completed with hybrid parallel-sequential execution",
            "performance": "optimized_hybrid"
        }

class OptimizedMultiAgentTeachingSystem:
    """优化的多智能体教学系统 - Sprint 2高性能版本"""
    
    def __init__(self, course_type: str = "python_basics"):
        self.course_type = course_type
        self.agent_factory = OptimizedTeachingAgentFactory()
        self.code_executor = CodeExecutor()
        self.session_history: Dict[str, Any] = {}
        self.performance_monitor = PerformanceMonitor()
        self.response_cache = IntelligentCache()
        
        # 并发控制
        self.max_concurrent_requests = 10
        self.request_semaphore = asyncio.Semaphore(self.max_concurrent_requests)
        
        logger.info(f"Optimized TeachingSystem initialized for {course_type}")
        
    async def process_submission_optimized(self, submission_data: SubmissionData,
                                         workflow_type: str = "standard",
                                         performance_mode: str = "balanced") -> TeachingFeedback:
        """优化的提交处理 - 支持多种工作流和性能模式"""
        async with self.request_semaphore:  # 并发控制
            start_time = time.time()
            session_id = f"session_{submission_data.student_id}_{int(datetime.now().timestamp())}"
            
            try:
                logger.info(f"Processing optimized submission {session_id} with {workflow_type} workflow")
                
                # 检查缓存
                cache_key = self._generate_cache_key(submission_data, workflow_type)
                cached_feedback = self.response_cache.get(cache_key)
                
                if cached_feedback and workflow_type != "debugging":  # 调试工作流不使用缓存
                    logger.info(f"Cache hit for submission {session_id}")
                    self.performance_monitor.record_request(
                        response_time=time.time() - start_time,
                        cache_hit=True
                    )
                    return cached_feedback
                    
                # 预处理：并发执行代码分析和基础检查
                code_execution_task = self._execute_code_safely(submission_data.code)
                agent_pool_task = self.agent_factory.get_agent_pool(workflow_type)
                
                # 等待预处理完成
                execution_result, agents = await asyncio.gather(code_execution_task, agent_pool_task)
                
                if not agents:
                    raise ValueError("Failed to initialize agent pool")
                    
                # 创建优化的群聊
                group_chat = GroupChat(
                    agents=list(agents.values()),
                    messages=[],
                    max_round=6 if workflow_type == "standard" else 4,
                    speaker_selection_method="manual"
                )
                
                manager = OptimizedGroupChatManager(
                    groupchat=group_chat,
                    llm_config={"model": "gpt-4o", "temperature": 0.3}
                )
                
                # 构建优化的提示信息
                initial_message = self._build_optimized_prompt(submission_data, execution_result, workflow_type)
                
                # 执行优化的多Agent协作
                chat_result = await manager.optimized_initiate_chat(
                    message=initial_message,
                    workflow_type=workflow_type,
                    max_turns=6
                )
                
                # 生成最终反馈
                final_feedback = self._synthesize_optimized_feedback(
                    chat_result["agent_responses"], 
                    submission_data,
                    workflow_type
                )
                
                # 缓存结果(非调试工作流)
                if workflow_type != "debugging":
                    self.response_cache.set(cache_key, final_feedback)
                    
                # 记录会话历史
                self.session_history[session_id] = {
                    "submission": submission_data,
                    "workflow_type": workflow_type,
                    "agent_responses": chat_result["agent_responses"],
                    "feedback": final_feedback,
                    "performance": chat_result.get("performance", "unknown"),
                    "timestamp": datetime.now()
                }
                
                # 记录性能指标
                response_time = time.time() - start_time
                self.performance_monitor.record_request(response_time=response_time)
                
                logger.info(f"Optimized submission {session_id} completed in {response_time:.2f}s")
                return final_feedback
                
            except Exception as e:
                response_time = time.time() - start_time
                self.performance_monitor.record_request(response_time=response_time, error=True)
                logger.error(f"Optimized submission processing failed: {e}")
                return self._generate_error_feedback(str(e), session_id)
                
    async def batch_process_submissions(self, submissions: List[SubmissionData],
                                      workflow_type: str = "standard",
                                      max_concurrent: int = 5) -> List[TeachingFeedback]:
        """批量处理提交 - 高并发优化"""
        semaphore = asyncio.Semaphore(max_concurrent)
        
        async def process_with_limit(submission):
            async with semaphore:
                return await self.process_submission_optimized(submission, workflow_type)
                
        tasks = [process_with_limit(sub) for sub in submissions]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # 处理异常结果
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error(f"Batch processing failed for submission {i}: {result}")
                processed_results.append(self._generate_error_feedback(str(result), f"batch_{i}"))
            else:
                processed_results.append(result)
                
        logger.info(f"Batch processing completed: {len(processed_results)} submissions")
        return processed_results
        
    def _generate_cache_key(self, submission_data: SubmissionData, workflow_type: str) -> str:
        """生成缓存键"""
        content = f"{submission_data.code}_{submission_data.language}_{workflow_type}_{submission_data.assignment_id}"
        return hashlib.md5(content.encode()).hexdigest()
        
    def _build_optimized_prompt(self, submission_data: SubmissionData, 
                               execution_result: Dict, workflow_type: str) -> str:
        """构建优化的提示信息"""
        base_prompt = f"""
【优化分析请求 - {workflow_type.upper()}工作流】

**学生信息：**
- ID: {submission_data.student_id}
- 课程: {self.course_type}
- 语言: {submission_data.language}
- 提交时间: {submission_data.submitted_at}

**作业要求：**
{submission_data.assignment_description}

**学生代码：**
```{submission_data.language}
{submission_data.code}
```

**执行结果：**
- 成功: {execution_result['success']}
- 输出: {execution_result['output'][:200]}...
- 错误: {execution_result['error'][:200]}...
- 执行时间: {execution_result['execution_time']}ms

**学生历史：**
{json.dumps(submission_data.student_history, ensure_ascii=False, indent=1)}
"""
        
        if workflow_type == "quick_analysis":
            base_prompt += "\n**优化指令：** 请提供快速、精准的核心问题分析和改进建议。"
        elif workflow_type == "debugging":
            base_prompt += "\n**优化指令：** 专注调试指导，通过提问引导学生自主发现问题。"
        else:
            base_prompt += "\n**优化指令：** 请提供全面、个性化的教学反馈和学习建议。"
            
        return base_prompt
        
    def _synthesize_optimized_feedback(self, agent_responses: Dict[str, Any], 
                                     submission_data: SubmissionData,
                                     workflow_type: str) -> TeachingFeedback:
        """综合优化反馈"""
        # 提取各Agent响应
        code_analysis = agent_responses.get("CodeAnalyzer", {})
        student_profile = agent_responses.get("StudentProfiler", {})
        teaching_strategy = agent_responses.get("PedagogyExpert", {})
        generated_feedback = agent_responses.get("FeedbackGenerator", {})
        quality_check = agent_responses.get("QualityController", {})
        debugging_guidance = agent_responses.get("DebuggingMentor", {})
        
        # 计算综合分数
        overall_score = self._calculate_optimized_score(code_analysis)
        
        # 确定教学策略
        strategy = teaching_strategy.get("strategy_recommendation", {}).get("primary_strategy", "HINT")
        if workflow_type == "debugging":
            strategy = "DEBUGGING"
        elif workflow_type == "quick_analysis":
            strategy = "QUICK_FEEDBACK"
            
        # 构建反馈内容
        feedback_content = generated_feedback.get("feedback_structure", {})
        if workflow_type == "debugging":
            feedback_content = debugging_guidance.get("debugging_guidance", {})
            
        return TeachingFeedback(
            session_id=f"{workflow_type}_{submission_data.student_id}_{int(datetime.now().timestamp())}",
            student_id=submission_data.student_id,
            overall_score=overall_score,
            code_analysis=code_analysis,
            student_profile=student_profile,
            teaching_strategy=strategy,
            feedback_content=feedback_content,
            recommendations=generated_feedback.get("personalization", {}),
            quality_score=quality_check.get("quality_assessment", {}).get("overall_score", 85),
            next_steps=self._extract_next_steps(generated_feedback, debugging_guidance),
            estimated_completion_time=self._estimate_completion_time(workflow_type, code_analysis),
            created_at=datetime.now()
        )
        
    def _calculate_optimized_score(self, code_analysis: Dict[str, Any]) -> float:
        """优化的分数计算算法"""
        if not code_analysis:
            return 0.0
            
        try:
            syntax_score = code_analysis.get("syntax_analysis", {}).get("score", 0)
            logic_score = code_analysis.get("logic_analysis", {}).get("score", 0)
            style_score = code_analysis.get("style_analysis", {}).get("score", 0)
            
            # 加权平均：语法40%，逻辑40%，风格20%
            overall = (syntax_score * 0.4 + logic_score * 0.4 + style_score * 0.2)
            return min(max(overall, 0.0), 100.0)  # 确保在0-100范围内
            
        except (KeyError, TypeError, ValueError):
            return 75.0  # 默认分数
            
    def _extract_next_steps(self, generated_feedback: Dict, debugging_guidance: Dict) -> List[str]:
        """提取下一步建议"""
        steps = []
        
        # 从反馈生成器提取
        if generated_feedback and "follow_up_plan" in generated_feedback:
            steps.extend(generated_feedback["follow_up_plan"].get("next_steps", []))
            
        # 从调试指导提取
        if debugging_guidance and "debugging_steps" in debugging_guidance:
            debug_steps = debugging_guidance["debugging_steps"]
            if isinstance(debug_steps, list):
                steps.extend([step.get("step", "") for step in debug_steps if isinstance(step, dict)])
                
        return steps[:5]  # 限制为最多5个步骤
        
    def _estimate_completion_time(self, workflow_type: str, code_analysis: Dict) -> str:
        """估算完成时间"""
        if workflow_type == "quick_analysis":
            return "5-10分钟"
        elif workflow_type == "debugging":
            return "15-30分钟"
        else:
            complexity = code_analysis.get("overall_assessment", {}).get("level", "beginner")
            time_map = {
                "beginner": "10-15分钟",
                "intermediate": "15-25分钟", 
                "advanced": "25-40分钟"
            }
            return time_map.get(complexity, "15-20分钟")
            
    async def _execute_code_safely(self, code: str) -> Dict[str, Any]:
        """安全执行学生代码"""
        try:
            result = await asyncio.wait_for(
                self.code_executor.execute_safely(code, timeout=5),
                timeout=10.0
            )
            return {
                "success": result.get("success", False),
                "output": result.get("output", "")[:500],  # 限制输出长度
                "error": result.get("error", "")[:500],
                "execution_time": result.get("execution_time", 0)
            }
        except asyncio.TimeoutError:
            return {
                "success": False,
                "output": "",
                "error": "Code execution timeout",
                "execution_time": 10000
            }
        except Exception as e:
            return {
                "success": False,
                "output": "",
                "error": str(e)[:500],
                "execution_time": 0
            }
            
    def _generate_error_feedback(self, error_message: str, session_id: str) -> TeachingFeedback:
        """生成错误反馈"""
        return TeachingFeedback(
            session_id=session_id,
            student_id="unknown",
            overall_score=0,
            code_analysis={"error": f"System error: {error_message}"},
            student_profile={},
            teaching_strategy="ERROR_HANDLING",
            feedback_content={
                "recognition": "系统在处理您的提交时遇到了技术问题，我们正在努力解决。",
                "reconstruction": {
                    "critical_issues": [
                        {
                            "issue": "系统错误", 
                            "solution": "请稍后重试或联系技术支持",
                            "priority": "high"
                        }
                    ]
                }
            },
            recommendations={},
            quality_score=0,
            next_steps=["稍后重试提交", "检查代码格式", "联系技术支持"],
            estimated_completion_time="5分钟",
            created_at=datetime.now()
        )
        
    def get_system_performance(self) -> Dict[str, Any]:
        """获取系统性能报告"""
        return {
            "performance_summary": self.performance_monitor.get_performance_summary(),
            "cache_stats": self.response_cache.get_stats(),
            "system_status": {
                "max_concurrent_requests": self.max_concurrent_requests,
                "active_sessions": len(self.session_history),
                "course_type": self.course_type
            },
            "timestamp": datetime.now().isoformat()
        }

# 导出优化的类
__all__ = [
    'OptimizedMultiAgentTeachingSystem', 
    'OptimizedTeachingAgentFactory',
    'OptimizedGroupChatManager',
    'PerformanceMonitor',
    'IntelligentCache'
]