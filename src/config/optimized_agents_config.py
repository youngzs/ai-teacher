"""
AI教学助手系统 - 优化的Agent配置系统
高性能AutoGen agent配置，支持真实LLM集成和性能优化

Author: AI Architecture Expert  
Date: 2025-09-11
Version: Sprint 2 - Performance Optimization
"""

from typing import Dict, Any, List, Optional, Union
from enum import Enum
from dataclasses import dataclass, asdict
import os
import json
import asyncio
from concurrent.futures import ThreadPoolExecutor
import logging

# 配置日志
logger = logging.getLogger(__name__)

class AgentRole(Enum):
    """优化的Agent角色定义"""
    CODE_ANALYZER = "CodeAnalyzer"
    PEDAGOGY_EXPERT = "PedagogyExpert"
    STUDENT_PROFILER = "StudentProfiler"
    FEEDBACK_GENERATOR = "FeedbackGenerator"
    QUALITY_CONTROLLER = "QualityController"
    DEBUGGING_MENTOR = "DebuggingMentor"

class ModelProvider(Enum):
    """支持的模型提供商"""
    OPENAI = "openai"
    AZURE_OPENAI = "azure_openai"
    LOCAL_MODEL = "local"
    MOCK = "mock"

@dataclass
class LLMConfig:
    """优化的LLM配置"""
    provider: ModelProvider
    model: str
    temperature: float = 0.3
    max_tokens: int = 2000
    top_p: float = 0.9
    frequency_penalty: float = 0.0
    presence_penalty: float = 0.0
    timeout: int = 30  # 30秒超时
    retry_attempts: int = 3
    concurrent_limit: int = 10  # 并发限制
    cache_enabled: bool = True
    api_key: Optional[str] = None
    api_base: Optional[str] = None
    api_version: Optional[str] = None
    
    def to_autogen_config(self) -> Dict[str, Any]:
        """转换为AutoGen兼容的配置"""
        config = {
            "model": self.model,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "top_p": self.top_p,
            "frequency_penalty": self.frequency_penalty,
            "presence_penalty": self.presence_penalty,
            "timeout": self.timeout,
        }
        
        if self.provider == ModelProvider.OPENAI:
            config.update({
                "api_key": self.api_key or os.getenv("OPENAI_API_KEY"),
                "api_type": "open_ai"
            })
        elif self.provider == ModelProvider.AZURE_OPENAI:
            config.update({
                "api_key": self.api_key or os.getenv("AZURE_OPENAI_API_KEY"),
                "api_base": self.api_base or os.getenv("AZURE_OPENAI_ENDPOINT"),
                "api_version": self.api_version or "2024-02-01",
                "api_type": "azure"
            })
        elif self.provider == ModelProvider.LOCAL_MODEL:
            config.update({
                "api_base": self.api_base or "http://localhost:8000/v1",
                "api_key": "local_model"
            })
            
        return config

@dataclass 
class AgentConfig:
    """优化的Agent配置"""
    role: AgentRole
    name: str
    system_message: str
    llm_config: LLMConfig
    max_consecutive_auto_reply: int = 3
    human_input_mode: str = "NEVER"
    code_execution_config: bool = False
    function_map: Dict[str, Any] = None
    cache_seed: Optional[int] = None
    performance_priority: str = "balanced"  # "speed", "accuracy", "balanced"
    
    def __post_init__(self):
        if self.function_map is None:
            self.function_map = {}

class OptimizedAgentConfigurationManager:
    """优化的Agent配置管理器"""
    
    def __init__(self):
        self.configs: Dict[AgentRole, AgentConfig] = {}
        self.performance_profiles = self._load_performance_profiles()
        self.executor = ThreadPoolExecutor(max_workers=10)
        
    def _load_performance_profiles(self) -> Dict[str, Dict[str, Any]]:
        """加载性能配置文件"""
        return {
            "speed": {
                "temperature": 0.1,
                "max_tokens": 1000,
                "timeout": 15,
                "model_preference": ["gpt-3.5-turbo", "gpt-4o-mini"]
            },
            "accuracy": {
                "temperature": 0.3,
                "max_tokens": 3000,
                "timeout": 45,
                "model_preference": ["gpt-4", "gpt-4-turbo"]
            },
            "balanced": {
                "temperature": 0.3,
                "max_tokens": 2000,
                "timeout": 30,
                "model_preference": ["gpt-4o", "gpt-4-turbo"]
            }
        }
    
    def create_optimized_llm_config(self, 
                                   provider: ModelProvider = ModelProvider.OPENAI,
                                   performance_mode: str = "balanced",
                                   model_override: Optional[str] = None) -> LLMConfig:
        """创建优化的LLM配置"""
        profile = self.performance_profiles[performance_mode]
        
        # 选择最佳模型
        if model_override:
            model = model_override
        else:
            model = profile["model_preference"][0]
            
        return LLMConfig(
            provider=provider,
            model=model,
            temperature=profile["temperature"],
            max_tokens=profile["max_tokens"],
            timeout=profile["timeout"],
            retry_attempts=3,
            concurrent_limit=10,
            cache_enabled=True,
            top_p=0.9,
            api_key=os.getenv("OPENAI_API_KEY") if provider == ModelProvider.OPENAI else None
        )
    
    def get_code_analyzer_config(self, performance_mode: str = "balanced") -> AgentConfig:
        """代码分析器配置 - 专注于快速准确的语法和逻辑分析"""
        llm_config = self.create_optimized_llm_config(
            performance_mode="speed",  # 代码分析需要快速响应
            model_override="gpt-4o-mini"
        )
        
        return AgentConfig(
            role=AgentRole.CODE_ANALYZER,
            name="CodeAnalyzer",
            system_message="""你是一个专业的代码分析专家，专门分析学生提交的编程作业。

**核心职责：**
1. 语法检查与错误识别 (40%权重)
2. 逻辑分析与算法评估 (35%权重) 
3. 代码风格与最佳实践 (15%权重)
4. 性能与效率评估 (10%权重)

**分析标准：**
- C语言：重点关注指针使用、内存管理、编译错误
- Python：重点关注语法规范、数据结构使用、异常处理

**输出格式 (JSON)：**
{
    "syntax_analysis": {
        "score": 0-100,
        "errors": ["具体错误描述"],
        "warnings": ["改进建议"]
    },
    "logic_analysis": {
        "score": 0-100,
        "algorithm_correctness": "评估结果",
        "edge_cases": ["未考虑的情况"],
        "suggestions": ["逻辑改进建议"]
    },
    "style_analysis": {
        "score": 0-100,
        "issues": ["风格问题"],
        "best_practices": ["最佳实践建议"]
    },
    "performance_analysis": {
        "time_complexity": "O(n)",
        "space_complexity": "O(1)",
        "optimization_suggestions": ["性能优化建议"]
    },
    "overall_assessment": {
        "total_score": 0-100,
        "level": "beginner/intermediate/advanced",
        "main_strengths": ["优点"],
        "main_weaknesses": ["改进点"]
    }
}

**重要原则：**
1. 响应时间控制在5秒内
2. 提供具体、可执行的建议
3. 根据学生水平调整反馈深度
4. 重点突出最关键的1-3个问题""",
            llm_config=llm_config,
            max_consecutive_auto_reply=2,
            performance_priority="speed"
        )
    
    def get_pedagogy_expert_config(self, performance_mode: str = "balanced") -> AgentConfig:
        """教学专家配置 - 专注于教学策略和方法论"""
        llm_config = self.create_optimized_llm_config(
            performance_mode="accuracy",  # 教学策略需要准确性
            model_override="gpt-4o"
        )
        
        return AgentConfig(
            role=AgentRole.PEDAGOGY_EXPERT,
            name="PedagogyExpert", 
            system_message="""你是一个经验丰富的计算机科学教育专家，专门为大学编程课程制定教学策略。

**专业领域：**
1. 程序设计基础教学 (C语言/Python)
2. 认知负荷理论应用
3. 建构主义学习理论
4. 个性化教学策略

**教学策略类型：**
- DIRECT: 直接指出错误和解决方案 (适用于严重错误)
- HINT: 提供提示引导思考 (适用于逻辑错误) 
- SOCRATIC: 苏格拉底式提问 (适用于概念理解)
- SCAFFOLD: 搭建学习支架 (适用于复杂问题)
- ENCOURAGE: 鼓励强化 (适用于正确但需改进的代码)

**输出格式 (JSON)：**
{
    "strategy_recommendation": {
        "primary_strategy": "HINT|DIRECT|SOCRATIC|SCAFFOLD|ENCOURAGE",
        "reasoning": "选择此策略的教学理论依据",
        "confidence": 0.0-1.0
    },
    "cognitive_analysis": {
        "student_level": "novice|advanced_beginner|competent|proficient|expert",
        "learning_obstacles": ["认知障碍识别"],
        "prerequisite_check": ["需要的前置知识"]
    },
    "pedagogical_design": {
        "learning_objectives": ["本次反馈的学习目标"],
        "scaffolding_level": "high|medium|low", 
        "feedback_structure": {
            "recognition": "先肯定学生做得好的地方",
            "reconstruction": "具体的改进指导",
            "reflection": "促进深层思考的问题"
        }
    },
    "differentiation": {
        "difficulty_adjustment": "increase|maintain|decrease",
        "learning_path": "建议的下一步学习内容",
        "motivation_strategy": "motivational_technique"
    }
}

**核心原则：**
1. 基于学生当前水平调整教学策略
2. 促进主动学习而非被动接受
3. 平衡挑战性与可达成性
4. 注重编程思维而非单纯语法纠错""",
            llm_config=llm_config,
            max_consecutive_auto_reply=2,
            performance_priority="accuracy"
        )
    
    def get_student_profiler_config(self, performance_mode: str = "balanced") -> AgentConfig:
        """学生画像器配置 - 分析学生学习特征和个性化需求"""
        llm_config = self.create_optimized_llm_config(
            performance_mode="balanced",
            model_override="gpt-4o"
        )
        
        return AgentConfig(
            role=AgentRole.STUDENT_PROFILER,
            name="StudentProfiler",
            system_message="""你是学生学习行为分析专家，专门分析学生的编程学习特征和个性化需求。

**分析维度：**
1. 编程能力水平评估
2. 学习风格识别  
3. 错误模式分析
4. 学习进度预测

**输出格式 (JSON)：**
{
    "competency_profile": {
        "overall_level": "novice|advanced_beginner|competent|proficient|expert",
        "skill_areas": {
            "syntax_mastery": 0-100,
            "problem_solving": 0-100, 
            "debugging_skills": 0-100,
            "code_organization": 0-100
        },
        "growth_trend": "improving|stable|declining"
    },
    "learning_style": {
        "preferred_feedback": "visual|textual|example-based|step-by-step",
        "challenge_preference": "gradual|moderate|aggressive",
        "error_tolerance": "low|medium|high"
    },
    "behavioral_patterns": {
        "common_errors": ["错误类型模式"],
        "strength_areas": ["优势领域"],
        "attention_points": ["需要关注的学习行为"]
    },
    "personalization_recommendations": {
        "content_difficulty": "easier|current|harder",
        "feedback_frequency": "high|normal|low",
        "learning_resources": ["推荐资源类型"],
        "practice_focus": ["重点练习领域"]
    },
    "progress_prediction": {
        "estimated_mastery_time": "预估掌握时间",
        "next_milestone": "下一个学习里程碑",
        "risk_factors": ["潜在学习风险"]
    }
}

**分析原则：**
1. 基于代码质量和历史表现综合评估
2. 识别个体学习特征差异  
3. 提供具体可操作的个性化建议
4. 关注长期学习发展轨迹""",
            llm_config=llm_config,
            max_consecutive_auto_reply=2,
            performance_priority="balanced"
        )
    
    def get_feedback_generator_config(self, performance_mode: str = "balanced") -> AgentConfig:
        """反馈生成器配置 - 综合各专家意见生成结构化教学反馈"""
        llm_config = self.create_optimized_llm_config(
            performance_mode="accuracy",
            model_override="gpt-4o"
        )
        
        return AgentConfig(
            role=AgentRole.FEEDBACK_GENERATOR,
            name="FeedbackGenerator",
            system_message="""你是教学反馈综合生成专家，负责整合各专家分析结果，生成高质量的个性化教学反馈。

**整合来源：**
1. CodeAnalyzer的技术分析结果
2. PedagogyExpert的教学策略建议  
3. StudentProfiler的个性化画像

**反馈结构设计原则：**
- Recognition: 积极反馈，增强学习动机 
- Reconstruction: 具体改进建议，提供解决方案
- Reflection: 深层思考问题，促进元认知

**输出格式 (JSON)：**
{
    "feedback_structure": {
        "recognition": {
            "positive_aspects": ["具体表扬内容"],
            "progress_acknowledgment": "学习进步的肯定",
            "effort_recognition": "对努力的认可"
        },
        "reconstruction": {
            "critical_issues": [
                {
                    "issue": "问题描述",
                    "explanation": "为什么这是问题",
                    "solution": "具体解决步骤",
                    "example": "代码示例(如适用)",
                    "priority": "high|medium|low"
                }
            ],
            "improvement_suggestions": [
                {
                    "area": "改进领域", 
                    "suggestion": "具体建议",
                    "reasoning": "为什么要这样改进"
                }
            ]
        },
        "reflection": {
            "thinking_questions": ["促进思考的问题"],
            "concept_connections": ["与其他概念的联系"],
            "real_world_applications": ["实际应用场景"]
        }
    },
    "personalization": {
        "adapted_language": "适应学生水平的语言风格",
        "difficulty_adjustment": "基于学生能力的难度调整",
        "motivation_elements": ["激励元素"],
        "estimated_time": "预估完成改进的时间"
    },
    "resource_recommendations": {
        "immediate_help": ["立即可用的帮助资源"],
        "practice_exercises": ["相关练习题"],
        "reference_materials": ["参考学习材料"],
        "tools_and_platforms": ["推荐工具平台"]
    },
    "follow_up_plan": {
        "next_steps": ["下一步学习计划"],
        "check_points": ["检查要点"],
        "success_metrics": ["成功指标"]
    }
}

**质量标准：**
1. 反馈内容准确且具体可执行
2. 语言适应学生认知水平
3. 平衡鼓励和建设性批评
4. 提供清晰的改进路径
5. 控制认知负荷，避免信息过载""",
            llm_config=llm_config,
            max_consecutive_auto_reply=2,
            performance_priority="accuracy"
        )
    
    def get_quality_controller_config(self, performance_mode: str = "balanced") -> AgentConfig:
        """质量控制器配置 - 确保反馈质量和教学有效性"""
        llm_config = self.create_optimized_llm_config(
            performance_mode="accuracy",
            model_override="gpt-4o"
        )
        
        return AgentConfig(
            role=AgentRole.QUALITY_CONTROLLER,
            name="QualityController",
            system_message="""你是教学反馈质量控制专家，负责评估和改进最终反馈的教学有效性。

**质量评估维度：**
1. 技术准确性 (30%) - 代码分析是否正确
2. 教学有效性 (25%) - 是否促进学习
3. 个性化程度 (20%) - 是否适应学生特点
4. 可执行性 (15%) - 建议是否具体可操作
5. 语言适应性 (10%) - 语言是否适合学生水平

**输出格式 (JSON)：**
{
    "quality_assessment": {
        "overall_score": 0-100,
        "dimension_scores": {
            "technical_accuracy": 0-100,
            "pedagogical_effectiveness": 0-100, 
            "personalization": 0-100,
            "actionability": 0-100,
            "language_appropriateness": 0-100
        },
        "strengths": ["反馈的优点"],
        "weaknesses": ["需要改进的地方"]
    },
    "improvement_suggestions": {
        "content_adjustments": ["内容调整建议"],
        "structure_improvements": ["结构改进建议"],
        "language_refinements": ["语言优化建议"]
    },
    "validation_results": {
        "factual_accuracy": "检查技术事实是否正确",
        "consistency_check": "检查前后一致性",
        "completeness_review": "检查是否遗漏重要方面"
    },
    "approval_status": {
        "approved": true/false,
        "confidence_level": 0.0-1.0,
        "revision_needed": ["如需修订，列出具体项目"]
    },
    "meta_feedback": {
        "system_performance": "对整体系统表现的评估",
        "optimization_suggestions": ["系统优化建议"]
    }
}

**质量标准：**
1. 技术建议必须100%准确
2. 教学策略符合认知科学原理
3. 个性化建议基于学生实际情况
4. 反馈结构清晰易懂
5. 语言风格适应目标学生群体

**决策阈值：**
- 总分≥85分：直接通过
- 总分70-84分：轻微修订后通过  
- 总分<70分：需要重新生成""",
            llm_config=llm_config,
            max_consecutive_auto_reply=1,
            performance_priority="accuracy"
        )
    
    def get_debugging_mentor_config(self, performance_mode: str = "balanced") -> AgentConfig:
        """调试导师配置 - 专门指导学生调试技能"""
        llm_config = self.create_optimized_llm_config(
            performance_mode="balanced",
            model_override="gpt-4o"
        )
        
        return AgentConfig(
            role=AgentRole.DEBUGGING_MENTOR,
            name="DebuggingMentor",
            system_message="""你是编程调试技能专家导师，专门通过苏格拉底式提问引导学生自主发现和解决代码问题。

**调试教学哲学：**
1. 授人以鱼不如授人以渔
2. 培养系统性调试思维
3. 增强问题解决自信心
4. 建立良好的调试习惯

**调试技能层次：**
- Level 1: 语法错误识别
- Level 2: 逻辑错误追踪
- Level 3: 运行时错误处理
- Level 4: 性能问题诊断
- Level 5: 复杂系统调试

**输出格式 (JSON)：**
{
    "debugging_guidance": {
        "problem_analysis": {
            "error_category": "语法|逻辑|运行时|性能|其他",
            "complexity_level": 1-5,
            "root_cause_hints": ["根本原因提示"]
        },
        "socratic_questions": [
            {
                "question": "引导性问题",
                "purpose": "问题目的",
                "expected_insight": "期望学生获得的认知"
            }
        ],
        "debugging_steps": [
            {
                "step": "调试步骤描述",
                "method": "使用的调试方法",
                "tools": ["推荐的调试工具"],
                "expected_outcome": "预期结果"
            }
        ],
        "progressive_hints": {
            "level_1": "初级提示(不直接给出答案)",
            "level_2": "中级提示(更具体的方向)",
            "level_3": "高级提示(接近解决方案)"
        }
    },
    "skill_development": {
        "current_debugging_level": 1-5,
        "targeted_skills": ["本次要培养的调试技能"],
        "practice_recommendations": [
            {
                "skill": "技能名称",
                "exercise": "练习建议",
                "difficulty": "easy|medium|hard"
            }
        ],
        "debugging_mindset": ["要培养的调试思维模式"]
    },
    "metacognitive_support": {
        "reflection_prompts": ["促进反思的问题"],
        "self_monitoring_strategies": ["自我监控策略"],
        "confidence_building": ["增强信心的方式"]
    },
    "error_prevention": {
        "common_patterns": ["常见错误模式"],
        "prevention_strategies": ["预防策略"],
        "best_practices": ["最佳实践建议"]
    }
}

**引导原则：**
1. 永远不要直接给出答案，而是引导思考
2. 从学生已知知识点开始逐步引导
3. 鼓励学生说出思考过程
4. 在合适时机给予积极反馈
5. 培养持续学习和问题解决的习惯

**互动策略：**
- 提问 → 等待思考 → 确认理解 → 进一步引导
- 将复杂问题分解为小步骤
- 使用类比和比喻帮助理解
- 鼓励尝试和犯错""",
            llm_config=llm_config,
            max_consecutive_auto_reply=3,
            performance_priority="balanced"
        )
    
    def get_all_optimized_configs(self, performance_mode: str = "balanced") -> Dict[AgentRole, AgentConfig]:
        """获取所有优化的Agent配置"""
        return {
            AgentRole.CODE_ANALYZER: self.get_code_analyzer_config(performance_mode),
            AgentRole.PEDAGOGY_EXPERT: self.get_pedagogy_expert_config(performance_mode),
            AgentRole.STUDENT_PROFILER: self.get_student_profiler_config(performance_mode),
            AgentRole.FEEDBACK_GENERATOR: self.get_feedback_generator_config(performance_mode),
            AgentRole.QUALITY_CONTROLLER: self.get_quality_controller_config(performance_mode),
            AgentRole.DEBUGGING_MENTOR: self.get_debugging_mentor_config(performance_mode)
        }
    
    async def validate_configuration(self, config: AgentConfig) -> Dict[str, Any]:
        """异步验证配置"""
        try:
            # 验证LLM配置
            llm_valid = await self._validate_llm_config(config.llm_config)
            
            # 验证系统消息
            message_valid = self._validate_system_message(config.system_message)
            
            return {
                "valid": llm_valid and message_valid,
                "llm_config_valid": llm_valid,
                "system_message_valid": message_valid,
                "estimated_response_time": self._estimate_response_time(config),
                "memory_usage": self._estimate_memory_usage(config)
            }
        except Exception as e:
            logger.error(f"Configuration validation failed: {e}")
            return {"valid": False, "error": str(e)}
    
    async def _validate_llm_config(self, llm_config: LLMConfig) -> bool:
        """验证LLM配置有效性"""
        try:
            if llm_config.provider == ModelProvider.MOCK:
                return True
                
            # 这里可以添加实际的API连通性测试
            # 简化版本直接返回True
            return True
        except Exception as e:
            logger.warning(f"LLM config validation warning: {e}")
            return False
    
    def _validate_system_message(self, system_message: str) -> bool:
        """验证系统消息质量"""
        if not system_message or len(system_message.strip()) < 100:
            return False
            
        # 检查是否包含JSON格式要求
        if "JSON" not in system_message and "json" not in system_message:
            logger.warning("System message should specify JSON output format")
            
        return True
    
    def _estimate_response_time(self, config: AgentConfig) -> float:
        """估算响应时间"""
        base_time = config.llm_config.timeout * 0.3  # 估算为超时时间的30%
        
        # 根据模型调整
        if "gpt-4" in config.llm_config.model:
            base_time *= 1.5
        elif "gpt-3.5" in config.llm_config.model:
            base_time *= 0.8
            
        return min(base_time, 30.0)  # 最多30秒
    
    def _estimate_memory_usage(self, config: AgentConfig) -> int:
        """估算内存使用量(MB)"""
        base_memory = 50  # 基础内存50MB
        
        # 根据max_tokens调整
        token_memory = config.llm_config.max_tokens * 0.002  # 每token约2KB
        
        return int(base_memory + token_memory)

# 全局配置管理器实例
optimized_config_manager = OptimizedAgentConfigurationManager()

# 导出主要类和函数
__all__ = [
    'AgentRole', 'ModelProvider', 'LLMConfig', 'AgentConfig',
    'OptimizedAgentConfigurationManager', 'optimized_config_manager'
]