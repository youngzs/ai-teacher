"""
OpenAI API 客户端封装 - Sprint 3
支持多种调用模式、错误处理和Mock降级

Author: AI Teaching Assistant Team
Date: 2026-01-19
"""

from typing import Dict, Any, List, Optional
import asyncio
import json
import time
from datetime import datetime
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

try:
    from openai import AsyncOpenAI, APIError, RateLimitError, APIConnectionError
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    AsyncOpenAI = None
    APIError = Exception
    RateLimitError = Exception
    APIConnectionError = Exception

try:
    import tiktoken
    TIKTOKEN_AVAILABLE = True
except ImportError:
    TIKTOKEN_AVAILABLE = False
    tiktoken = None

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from app.core.config import settings
from src.utils.logger import get_logger

logger = get_logger(__name__)


class OpenAIClient:
    """
    OpenAI API 客户端

    特性:
    - 支持真实API和Mock模式自动切换
    - 自动重试和错误处理
    - Token计数和成本监控
    - 响应缓存支持
    """

    def __init__(self):
        self.client: Optional[AsyncOpenAI] = None
        self.model = settings.OPENAI_MODEL
        self.max_tokens = 4000
        self.temperature = 0.3
        self._initialized = False
        self._use_mock = False

        # Token计数器
        self.encoding = None
        if TIKTOKEN_AVAILABLE:
            try:
                self.encoding = tiktoken.encoding_for_model(self.model)
            except KeyError:
                self.encoding = tiktoken.get_encoding("cl100k_base")

        # 使用统计
        self._stats = {
            "total_requests": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "total_tokens": 0,
            "total_cost_usd": 0.0,
            "mock_requests": 0
        }

    async def initialize(self) -> bool:
        """
        初始化OpenAI客户端

        Returns:
            bool: 是否成功初始化真实API
        """
        if self._initialized:
            return not self._use_mock

        api_key = settings.OPENAI_API_KEY

        if not api_key or not OPENAI_AVAILABLE:
            logger.warning("OpenAI API not available, using mock mode")
            self._use_mock = True
            self._initialized = True
            return False

        try:
            self.client = AsyncOpenAI(
                api_key=api_key,
                timeout=settings.AI_RESPONSE_TIMEOUT,
                max_retries=2
            )

            # 验证API连接
            await self.client.models.list()
            logger.info(f"OpenAI API initialized successfully (model: {self.model})")
            self._initialized = True
            self._use_mock = False
            return True

        except Exception as e:
            logger.error(f"OpenAI API initialization failed: {e}")
            logger.info("Falling back to mock mode")
            self._use_mock = True
            self._initialized = True
            return False

    def count_tokens(self, text: str) -> int:
        """计算文本的token数量"""
        if self.encoding:
            return len(self.encoding.encode(text))
        # 简单估算: 约4个字符一个token
        return len(text) // 4

    @property
    def is_mock_mode(self) -> bool:
        """是否在Mock模式下运行"""
        return self._use_mock

    @property
    def stats(self) -> Dict[str, Any]:
        """获取使用统计"""
        return self._stats.copy()

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((APIConnectionError, RateLimitError)) if OPENAI_AVAILABLE else retry_if_exception_type(Exception),
        before_sleep=lambda retry_state: logger.warning(
            f"OpenAI API retry attempt {retry_state.attempt_number}"
        )
    )
    async def chat_completion(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        response_format: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        执行聊天补全请求

        Args:
            messages: 消息列表
            model: 模型名称
            temperature: 温度参数
            max_tokens: 最大token数
            response_format: 响应格式

        Returns:
            API响应结果
        """
        if not self._initialized:
            await self.initialize()

        self._stats["total_requests"] += 1

        if self._use_mock:
            return await self._mock_completion(messages)

        try:
            params = {
                "model": model or self.model,
                "messages": messages,
                "temperature": temperature or self.temperature,
                "max_tokens": max_tokens or self.max_tokens,
            }

            if response_format:
                params["response_format"] = response_format

            response = await self.client.chat.completions.create(**params)

            # 更新统计
            self._stats["successful_requests"] += 1
            usage = response.usage
            self._stats["total_tokens"] += usage.total_tokens

            # 估算成本 (GPT-4 Turbo pricing)
            prompt_cost = usage.prompt_tokens * 0.01 / 1000
            completion_cost = usage.completion_tokens * 0.03 / 1000
            self._stats["total_cost_usd"] += prompt_cost + completion_cost

            return {
                "success": True,
                "content": response.choices[0].message.content,
                "usage": {
                    "prompt_tokens": usage.prompt_tokens,
                    "completion_tokens": usage.completion_tokens,
                    "total_tokens": usage.total_tokens
                },
                "model": response.model,
                "finish_reason": response.choices[0].finish_reason,
                "is_mock": False
            }

        except Exception as e:
            self._stats["failed_requests"] += 1
            logger.error(f"OpenAI API call failed: {e}")

            # 降级到Mock模式
            logger.info("Falling back to mock completion")
            return await self._mock_completion(messages)

    async def _mock_completion(self, messages: List[Dict[str, str]]) -> Dict[str, Any]:
        """Mock模式的响应生成"""
        self._stats["mock_requests"] += 1
        logger.debug("Using mock completion mode")

        # 模拟API延迟
        await asyncio.sleep(0.3)

        # 分析消息内容以生成相关的Mock响应
        last_message = messages[-1]["content"] if messages else ""

        # 基于消息内容生成适当的Mock响应
        mock_response = self._generate_mock_analysis(last_message)

        return {
            "success": True,
            "content": json.dumps(mock_response, ensure_ascii=False, indent=2),
            "usage": {
                "prompt_tokens": self.count_tokens(str(messages)),
                "completion_tokens": self.count_tokens(json.dumps(mock_response)),
                "total_tokens": 0
            },
            "model": "mock-model",
            "finish_reason": "stop",
            "is_mock": True
        }

    def _generate_mock_analysis(self, content: str) -> Dict[str, Any]:
        """生成Mock分析结果"""
        # 检测代码语言
        language = "python"
        if "int main" in content or "#include" in content:
            language = "c"

        # 检测一些常见问题
        has_syntax_issue = ";" not in content and language == "c"
        has_print = "print" in content or "printf" in content

        # 基础评分
        base_score = 75 if has_print else 65
        if has_syntax_issue:
            base_score -= 10

        return {
            "code_analysis": {
                "syntax_score": min(100, base_score + 10),
                "logic_score": base_score,
                "style_score": base_score - 5,
                "performance_score": base_score - 10,
                "critical_errors": [] if not has_syntax_issue else [
                    {"type": "syntax", "message": "可能缺少分号", "line": 1}
                ],
                "warnings": [
                    {"type": "style", "message": "建议添加更多注释"}
                ],
                "suggestions": [
                    "代码结构清晰",
                    "建议添加输入验证",
                    "考虑添加错误处理"
                ]
            },
            "feedback": {
                "recognition": "你的代码展示了对基本概念的理解，程序能够正确执行基本功能。",
                "reconstruction": {
                    "issues": [
                        "代码可以增加一些注释来提高可读性",
                        "考虑处理边界情况"
                    ],
                    "steps": [
                        "在关键逻辑处添加注释说明",
                        "添加输入有效性检查",
                        "测试边界值情况"
                    ]
                },
                "reinforcement": "继续保持良好的编程习惯！建议多练习不同类型的题目来巩固知识。"
            },
            "learning_points": [
                "基本语法结构",
                "输入输出操作",
                "程序流程控制"
            ],
            "overall_score": base_score,
            "difficulty_assessment": "beginner",
            "estimated_fix_time": "10-15分钟"
        }

    async def analyze_code(
        self,
        code: str,
        language: str,
        assignment_description: str,
        student_context: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        专门的代码分析方法

        Args:
            code: 待分析的代码
            language: 编程语言
            assignment_description: 作业描述
            student_context: 学生上下文信息

        Returns:
            代码分析结果
        """
        system_prompt = self._build_code_analysis_system_prompt(language)
        user_prompt = self._build_code_analysis_user_prompt(
            code, assignment_description, student_context
        )

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]

        result = await self.chat_completion(
            messages=messages,
            response_format={"type": "json_object"}
        )

        if result["success"]:
            try:
                result["parsed_content"] = json.loads(result["content"])
            except json.JSONDecodeError:
                result["parsed_content"] = {"raw": result["content"]}

        return result

    def _build_code_analysis_system_prompt(self, language: str) -> str:
        """构建代码分析系统提示"""
        lang_name = {"c": "C语言", "python": "Python"}.get(language.lower(), language)

        return f"""你是一位专业的{lang_name}编程教学助手，专门帮助大学生学习编程。

你的任务是分析学生提交的代码，并提供教育性的反馈。

请以JSON格式返回分析结果，包含以下字段：
{{
    "code_analysis": {{
        "syntax_score": <0-100的语法评分>,
        "logic_score": <0-100的逻辑评分>,
        "style_score": <0-100的代码风格评分>,
        "performance_score": <0-100的性能评分>,
        "critical_errors": [
            {{"type": "<错误类型>", "message": "<错误描述>", "line": <行号>, "suggestion": "<修复建议>"}}
        ],
        "warnings": [
            {{"type": "<警告类型>", "message": "<警告描述>"}}
        ],
        "suggestions": ["<改进建议列表>"]
    }},
    "feedback": {{
        "recognition": "<肯定学生做得好的地方，要具体>",
        "reconstruction": {{
            "issues": ["<需要改进的问题列表>"],
            "steps": ["<具体改进步骤>"]
        }},
        "reinforcement": "<鼓励语和下一步学习建议>"
    }},
    "learning_points": ["<本次作业涉及的知识点>"],
    "overall_score": <0-100的总体评分>,
    "difficulty_assessment": "<novice|beginner|intermediate|advanced>",
    "estimated_fix_time": "<预计修复时间>"
}}

反馈原则：
1. 使用鼓励性语言，建立学生信心
2. 错误反馈要具体，给出可操作的改正方法
3. 根据学生水平调整反馈深度
4. 每个问题都提供学习资源或示例代码
5. 先肯定做得好的地方，再指出需要改进的地方"""

    def _build_code_analysis_user_prompt(
        self,
        code: str,
        assignment_description: str,
        student_context: Optional[Dict]
    ) -> str:
        """构建代码分析用户提示"""
        prompt = f"""请分析以下学生代码提交：

## 作业要求
{assignment_description}

## 学生代码
```
{code}
```
"""

        if student_context:
            prompt += f"""
## 学生背景信息
- 技能水平: {student_context.get('competency_level', '未知')}
- 历史平均分: {student_context.get('average_score', '未知')}
- 常见错误模式: {', '.join(student_context.get('error_patterns', ['未知'])[:3])}
- 学习风格: {student_context.get('learning_style', '未知')}
"""

        prompt += "\n请严格按照JSON格式返回分析结果。"
        return prompt

    async def generate_debugging_guidance(
        self,
        code: str,
        language: str,
        error_message: str,
        student_question: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        生成调试指导

        Args:
            code: 有问题的代码
            language: 编程语言
            error_message: 错误信息
            student_question: 学生的具体问题

        Returns:
            调试指导结果
        """
        system_prompt = """你是一位耐心的编程导师，专门帮助学生学习调试技巧。

你的目标不是直接给出答案，而是引导学生自己发现和解决问题。

请以JSON格式返回，包含：
{
    "error_analysis": {
        "error_type": "<错误类型>",
        "root_cause": "<根本原因>",
        "affected_lines": [<受影响的行号>]
    },
    "guided_questions": [
        "<引导学生思考的问题，帮助他们自己发现问题>"
    ],
    "hints": [
        {"level": 1, "hint": "<最小提示>"},
        {"level": 2, "hint": "<中等提示>"},
        {"level": 3, "hint": "<详细提示，但不给答案>"}
    ],
    "learning_opportunity": "<这个错误可以学到什么>",
    "similar_patterns": ["<类似的常见错误模式>"],
    "debugging_steps": ["<调试步骤建议>"]
}"""

        user_prompt = f"""学生的代码出现了问题，请帮助引导他们解决：

## 代码
```{language}
{code}
```

## 错误信息
{error_message}
"""

        if student_question:
            user_prompt += f"\n## 学生的问题\n{student_question}"

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]

        return await self.chat_completion(
            messages=messages,
            response_format={"type": "json_object"}
        )


# 全局客户端实例
_openai_client: Optional[OpenAIClient] = None


async def get_openai_client() -> OpenAIClient:
    """获取OpenAI客户端单例"""
    global _openai_client

    if _openai_client is None:
        _openai_client = OpenAIClient()
        await _openai_client.initialize()

    return _openai_client


def reset_openai_client():
    """重置OpenAI客户端（用于测试）"""
    global _openai_client
    _openai_client = None
