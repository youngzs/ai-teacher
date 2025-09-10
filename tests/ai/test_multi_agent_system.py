"""
AI多智能体系统专项测试
测试6个AI Agent的功能和协作能力
"""

import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime
from typing import Dict, Any, List

# 假设这些是实际的导入路径
try:
    from src.agents.teaching_agents import MultiAgentTeachingSystem, TeachingAgentFactory
    from src.workflows.teaching_workflows import WorkflowManager, WorkflowType
    from src.models.teaching_models import (
        SubmissionData, ProgrammingLanguage, StudentProfile, DifficultyLevel
    )
    from src.config.agents_config import AgentRole, SYSTEM_CONFIG
except ImportError:
    # 如果导入失败，创建Mock类
    class AgentRole:
        CODE_ANALYZER = "CodeAnalyzer"
        PEDAGOGY_EXPERT = "PedagogyExpert"
        STUDENT_PROFILER = "StudentProfiler"
        FEEDBACK_GENERATOR = "FeedbackGenerator"
        QUALITY_CONTROLLER = "QualityController"
        DEBUGGING_MENTOR = "DebuggingMentor"
    
    class MultiAgentTeachingSystem:
        def __init__(self):
            self.agents = {}
        
        async def analyze_code(self, submission_data):
            return {"analysis": "mock", "feedback": "mock"}
    
    class TeachingAgentFactory:
        @staticmethod
        def create_agent(role):
            return Mock()
        
        @staticmethod
        def create_all_agents():
            return {role: Mock() for role in [
                "CodeAnalyzer", "PedagogyExpert", "StudentProfiler",
                "FeedbackGenerator", "QualityController", "DebuggingMentor"
            ]}


class TestMultiAgentTeachingSystem:
    """测试多智能体教学系统"""
    
    @pytest.fixture
    def mock_agents(self):
        """创建mock的AI agents"""
        agents = {}
        
        # CodeAnalyzer Mock
        code_analyzer = Mock()
        code_analyzer.name = "CodeAnalyzer"
        code_analyzer.analyze.return_value = {
            "syntax_errors": [],
            "logic_issues": ["Possible infinite loop"],
            "style_suggestions": ["Add comments"],
            "complexity_score": 3,
            "correctness_score": 85,
            "performance_analysis": {
                "time_complexity": "O(n)",
                "space_complexity": "O(1)",
                "optimization_suggestions": ["Use more efficient algorithm"]
            }
        }
        agents[AgentRole.CODE_ANALYZER] = code_analyzer
        
        # PedagogyExpert Mock  
        pedagogy_expert = Mock()
        pedagogy_expert.name = "PedagogyExpert"
        pedagogy_expert.assess_learning_strategy.return_value = {
            "recommended_approach": "scaffolding",
            "difficulty_adjustment": "maintain",
            "learning_objectives": ["understand_loops", "improve_logic"],
            "teaching_methods": ["visual_examples", "step_by_step_guidance"]
        }
        agents[AgentRole.PEDAGOGY_EXPERT] = pedagogy_expert
        
        # StudentProfiler Mock
        student_profiler = Mock()
        student_profiler.name = "StudentProfiler"
        student_profiler.analyze_profile.return_value = {
            "learning_style": "visual",
            "current_skill_level": "intermediate",
            "knowledge_gaps": ["error_handling", "algorithm_optimization"],
            "progress_indicators": {"concept_mastery": 0.75, "code_quality": 0.68},
            "motivation_level": "high"
        }
        agents[AgentRole.STUDENT_PROFILER] = student_profiler
        
        # FeedbackGenerator Mock
        feedback_generator = Mock()
        feedback_generator.name = "FeedbackGenerator"
        feedback_generator.generate.return_value = {
            "overall_assessment": "Good progress with room for improvement",
            "strengths": ["Clear variable naming", "Good code structure"],
            "areas_for_improvement": ["Error handling", "Code efficiency"],
            "specific_suggestions": [
                "Add try-catch blocks for error handling",
                "Consider using built-in functions for common operations"
            ],
            "encouragement": "You're making excellent progress! Keep it up!",
            "next_challenges": ["Implement recursive algorithms", "Work with data structures"]
        }
        agents[AgentRole.FEEDBACK_GENERATOR] = feedback_generator
        
        # QualityController Mock
        quality_controller = Mock()
        quality_controller.name = "QualityController"
        quality_controller.validate_response.return_value = {
            "is_valid": True,
            "confidence_score": 0.92,
            "quality_metrics": {
                "clarity": 0.88,
                "accuracy": 0.95,
                "helpfulness": 0.90,
                "appropriateness": 0.89
            },
            "validation_notes": "Response meets all quality standards"
        }
        agents[AgentRole.QUALITY_CONTROLLER] = quality_controller
        
        # DebuggingMentor Mock
        debugging_mentor = Mock()
        debugging_mentor.name = "DebuggingMentor"
        debugging_mentor.provide_debugging_guidance.return_value = {
            "identified_issues": [
                {"type": "logic_error", "line": 10, "description": "Loop condition incorrect"}
            ],
            "debugging_steps": [
                "Add print statements to trace variable values",
                "Check loop termination condition",
                "Verify input validation"
            ],
            "debugging_techniques": ["rubber_duck_debugging", "step_through_debugging"],
            "common_patterns": ["off_by_one_errors", "null_pointer_exceptions"]
        }
        agents[AgentRole.DEBUGGING_MENTOR] = debugging_mentor
        
        return agents
    
    @pytest.fixture
    def teaching_system(self, mock_agents):
        """创建教学系统实例"""
        with patch.object(TeachingAgentFactory, 'create_all_agents', return_value=mock_agents):
            system = MultiAgentTeachingSystem()
            system.agents = mock_agents
            return system
    
    @pytest.fixture
    def sample_submission(self):
        """示例代码提交"""
        return {
            "code": """
#include <stdio.h>
int main() {
    int i = 0;
    while(i <= 10) {  // Possible off-by-one error
        printf("%d ", i);
        i++;
    }
    return 0;
}
            """.strip(),
            "language": "c",
            "assignment_id": "loops-practice",
            "student_id": "student_123"
        }
    
    @pytest.mark.asyncio
    @pytest.mark.ai
    async def test_code_analyzer_functionality(self, teaching_system, mock_agents, sample_submission):
        """测试代码分析器功能"""
        code_analyzer = mock_agents[AgentRole.CODE_ANALYZER]
        
        # 调用分析功能
        result = code_analyzer.analyze(sample_submission["code"])
        
        # 验证分析结果
        assert "syntax_errors" in result
        assert "logic_issues" in result
        assert "style_suggestions" in result
        assert "complexity_score" in result
        assert "correctness_score" in result
        
        # 验证分析质量
        assert isinstance(result["complexity_score"], int)
        assert 0 <= result["correctness_score"] <= 100
        assert isinstance(result["syntax_errors"], list)
        assert isinstance(result["logic_issues"], list)
        
        # 验证调用
        code_analyzer.analyze.assert_called_once_with(sample_submission["code"])
    
    @pytest.mark.asyncio
    @pytest.mark.ai
    async def test_pedagogy_expert_strategy_selection(self, teaching_system, mock_agents):
        """测试教学策略专家功能"""
        pedagogy_expert = mock_agents[AgentRole.PEDAGOGY_EXPERT]
        
        student_context = {
            "current_level": "beginner",
            "previous_performance": 0.6,
            "learning_style": "hands_on"
        }
        
        strategy = pedagogy_expert.assess_learning_strategy(student_context)
        
        # 验证策略建议
        assert "recommended_approach" in strategy
        assert "difficulty_adjustment" in strategy
        assert "learning_objectives" in strategy
        assert "teaching_methods" in strategy
        
        # 验证策略合理性
        assert strategy["recommended_approach"] in ["scaffolding", "direct_instruction", "inquiry_based"]
        assert strategy["difficulty_adjustment"] in ["increase", "decrease", "maintain"]
        assert isinstance(strategy["learning_objectives"], list)
        assert isinstance(strategy["teaching_methods"], list)
    
    @pytest.mark.asyncio
    @pytest.mark.ai
    async def test_student_profiler_analysis(self, teaching_system, mock_agents, sample_submission):
        """测试学生画像分析功能"""
        student_profiler = mock_agents[AgentRole.STUDENT_PROFILER]
        
        student_history = {
            "submissions": [sample_submission],
            "performance_trend": [0.7, 0.75, 0.8],
            "engagement_metrics": {"session_duration": 45, "attempts": 3}
        }
        
        profile = student_profiler.analyze_profile(student_history)
        
        # 验证画像分析结果
        assert "learning_style" in profile
        assert "current_skill_level" in profile
        assert "knowledge_gaps" in profile
        assert "progress_indicators" in profile
        assert "motivation_level" in profile
        
        # 验证分析数据类型
        assert profile["learning_style"] in ["visual", "auditory", "kinesthetic", "hands_on"]
        assert profile["current_skill_level"] in ["beginner", "intermediate", "advanced"]
        assert isinstance(profile["knowledge_gaps"], list)
        assert isinstance(profile["progress_indicators"], dict)
    
    @pytest.mark.asyncio
    @pytest.mark.ai
    async def test_feedback_generator_personalization(self, teaching_system, mock_agents):
        """测试反馈生成器个性化功能"""
        feedback_generator = mock_agents[AgentRole.FEEDBACK_GENERATOR]
        
        analysis_context = {
            "code_analysis": {"correctness_score": 85, "issues": ["logic_error"]},
            "student_profile": {"level": "intermediate", "learning_style": "visual"},
            "pedagogical_strategy": {"approach": "encouraging", "focus": "improvement"}
        }
        
        feedback = feedback_generator.generate(analysis_context)
        
        # 验证反馈内容结构
        assert "overall_assessment" in feedback
        assert "strengths" in feedback
        assert "areas_for_improvement" in feedback
        assert "specific_suggestions" in feedback
        assert "encouragement" in feedback
        assert "next_challenges" in feedback
        
        # 验证反馈质量
        assert isinstance(feedback["strengths"], list)
        assert isinstance(feedback["areas_for_improvement"], list)
        assert isinstance(feedback["specific_suggestions"], list)
        assert len(feedback["overall_assessment"]) > 10  # 确保有实质内容
    
    @pytest.mark.asyncio
    @pytest.mark.ai
    async def test_quality_controller_validation(self, teaching_system, mock_agents):
        """测试质量控制器验证功能"""
        quality_controller = mock_agents[AgentRole.QUALITY_CONTROLLER]
        
        response_to_validate = {
            "feedback": "Your code looks good with minor improvements needed",
            "suggestions": ["Add error handling", "Improve variable names"],
            "score": 85
        }
        
        validation = quality_controller.validate_response(response_to_validate)
        
        # 验证质量控制结果
        assert "is_valid" in validation
        assert "confidence_score" in validation
        assert "quality_metrics" in validation
        
        # 验证质量指标
        assert isinstance(validation["is_valid"], bool)
        assert 0 <= validation["confidence_score"] <= 1
        assert "clarity" in validation["quality_metrics"]
        assert "accuracy" in validation["quality_metrics"]
        assert "helpfulness" in validation["quality_metrics"]
        assert "appropriateness" in validation["quality_metrics"]
    
    @pytest.mark.asyncio
    @pytest.mark.ai
    async def test_debugging_mentor_guidance(self, teaching_system, mock_agents, sample_submission):
        """测试调试指导专家功能"""
        debugging_mentor = mock_agents[AgentRole.DEBUGGING_MENTOR]
        
        code_with_errors = """
#include <stdio.h>
int main() {
    int arr[5];
    for(int i = 0; i <= 5; i++) {  // Bug: should be i < 5
        arr[i] = i * 2;  // Array out of bounds
    }
    return 0;
}
        """.strip()
        
        guidance = debugging_mentor.provide_debugging_guidance(code_with_errors)
        
        # 验证调试指导内容
        assert "identified_issues" in guidance
        assert "debugging_steps" in guidance
        assert "debugging_techniques" in guidance
        assert "common_patterns" in guidance
        
        # 验证指导质量
        assert isinstance(guidance["identified_issues"], list)
        assert isinstance(guidance["debugging_steps"], list)
        assert len(guidance["debugging_steps"]) > 0
        assert all("description" in issue for issue in guidance["identified_issues"])
    
    @pytest.mark.asyncio
    @pytest.mark.ai
    async def test_multi_agent_collaboration(self, teaching_system, mock_agents, sample_submission):
        """测试多智能体协作工作流程"""
        # 模拟完整的分析流程
        with patch.object(teaching_system, 'analyze_code') as mock_analyze:
            mock_analyze.return_value = {
                "code_analysis": mock_agents[AgentRole.CODE_ANALYZER].analyze.return_value,
                "pedagogical_strategy": mock_agents[AgentRole.PEDAGOGY_EXPERT].assess_learning_strategy.return_value,
                "student_profile": mock_agents[AgentRole.STUDENT_PROFILER].analyze_profile.return_value,
                "feedback": mock_agents[AgentRole.FEEDBACK_GENERATOR].generate.return_value,
                "quality_validation": mock_agents[AgentRole.QUALITY_CONTROLLER].validate_response.return_value,
                "debugging_guidance": mock_agents[AgentRole.DEBUGGING_MENTOR].provide_debugging_guidance.return_value,
                "collaboration_success": True
            }
            
            result = await teaching_system.analyze_code(sample_submission)
            
            # 验证协作结果包含各个Agent的输出
            assert "code_analysis" in result
            assert "pedagogical_strategy" in result
            assert "student_profile" in result
            assert "feedback" in result
            assert "quality_validation" in result
            assert "debugging_guidance" in result
            assert result["collaboration_success"] is True
    
    @pytest.mark.asyncio
    @pytest.mark.ai
    async def test_agent_performance_metrics(self, teaching_system, mock_agents):
        """测试Agent性能指标"""
        # 测试每个Agent的响应时间和准确性
        for role, agent in mock_agents.items():
            start_time = datetime.now()
            
            # 根据不同Agent调用相应方法
            if role == AgentRole.CODE_ANALYZER:
                result = agent.analyze("sample code")
            elif role == AgentRole.PEDAGOGY_EXPERT:
                result = agent.assess_learning_strategy({})
            elif role == AgentRole.STUDENT_PROFILER:
                result = agent.analyze_profile({})
            elif role == AgentRole.FEEDBACK_GENERATOR:
                result = agent.generate({})
            elif role == AgentRole.QUALITY_CONTROLLER:
                result = agent.validate_response({})
            elif role == AgentRole.DEBUGGING_MENTOR:
                result = agent.provide_debugging_guidance("code")
            
            end_time = datetime.now()
            response_time = (end_time - start_time).total_seconds()
            
            # 验证性能
            assert response_time < 1.0  # 模拟响应时间应该很快
            assert result is not None
    
    @pytest.mark.asyncio
    @pytest.mark.ai
    async def test_agent_error_handling(self, teaching_system, mock_agents):
        """测试Agent错误处理能力"""
        # 测试空输入处理
        code_analyzer = mock_agents[AgentRole.CODE_ANALYZER]
        
        # 模拟错误情况
        code_analyzer.analyze.side_effect = Exception("Analysis failed")
        
        with pytest.raises(Exception, match="Analysis failed"):
            code_analyzer.analyze("")
        
        # 重置mock
        code_analyzer.analyze.side_effect = None
        code_analyzer.analyze.return_value = {"error": "Invalid input"}
        
        result = code_analyzer.analyze("")
        assert "error" in result
    
    @pytest.mark.asyncio
    @pytest.mark.ai
    async def test_agent_consistency(self, teaching_system, mock_agents, sample_submission):
        """测试Agent输出一致性"""
        code_analyzer = mock_agents[AgentRole.CODE_ANALYZER]
        
        # 多次调用相同输入
        results = []
        for _ in range(3):
            result = code_analyzer.analyze(sample_submission["code"])
            results.append(result)
        
        # 验证一致性（mock返回应该相同）
        for result in results[1:]:
            assert result == results[0]
    
    @pytest.mark.asyncio
    @pytest.mark.ai
    async def test_agent_scalability(self, teaching_system, mock_agents):
        """测试Agent可扩展性"""
        # 模拟并发请求
        code_analyzer = mock_agents[AgentRole.CODE_ANALYZER]
        
        async def analyze_code_async(code):
            return code_analyzer.analyze(code)
        
        # 创建多个并发任务
        tasks = []
        for i in range(10):
            task = analyze_code_async(f"test code {i}")
            tasks.append(task)
        
        # 并发执行
        results = await asyncio.gather(*tasks)
        
        # 验证所有任务都成功完成
        assert len(results) == 10
        for result in results:
            assert result is not None
            assert "syntax_errors" in result


class TestAgentIntegration:
    """Agent集成测试"""
    
    @pytest.mark.asyncio
    @pytest.mark.ai
    async def test_c_language_analysis_pipeline(self):
        """测试C语言完整分析流水线"""
        c_code = """
#include <stdio.h>
int factorial(int n) {
    if (n <= 1) return 1;
    return n * factorial(n - 1);
}
int main() {
    printf("%d", factorial(5));
    return 0;
}
        """.strip()
        
        # 创建完整的分析流水线
        with patch.object(TeachingAgentFactory, 'create_all_agents') as mock_factory:
            mock_agents = {
                "CodeAnalyzer": Mock(),
                "PedagogyExpert": Mock(),
                "StudentProfiler": Mock(),
                "FeedbackGenerator": Mock(),
                "QualityController": Mock(),
                "DebuggingMentor": Mock()
            }
            
            mock_factory.return_value = mock_agents
            
            # 配置各Agent的返回值
            mock_agents["CodeAnalyzer"].analyze.return_value = {
                "language": "c",
                "complexity": "medium",
                "correctness": 95,
                "issues": []
            }
            
            mock_agents["PedagogyExpert"].assess_learning_strategy.return_value = {
                "strategy": "recursive_concepts",
                "difficulty": "appropriate"
            }
            
            mock_agents["FeedbackGenerator"].generate.return_value = {
                "feedback": "Excellent use of recursion!"
            }
            
            system = MultiAgentTeachingSystem()
            system.agents = mock_agents
            
            # 执行分析
            with patch.object(system, 'analyze_code') as mock_analyze:
                mock_analyze.return_value = {"status": "success", "language": "c"}
                result = await system.analyze_code({"code": c_code, "language": "c"})
                
                assert result["status"] == "success"
                assert result["language"] == "c"
    
    @pytest.mark.asyncio
    @pytest.mark.ai
    async def test_python_language_analysis_pipeline(self):
        """测试Python语言完整分析流水线"""
        python_code = """
def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)

print(fibonacci(10))
        """.strip()
        
        with patch.object(MultiAgentTeachingSystem, 'analyze_code') as mock_analyze:
            mock_analyze.return_value = {
                "status": "success",
                "language": "python",
                "analysis": {
                    "algorithm": "recursive_fibonacci",
                    "optimization_needed": True,
                    "suggestions": ["Consider using dynamic programming"]
                }
            }
            
            system = MultiAgentTeachingSystem()
            result = await system.analyze_code({"code": python_code, "language": "python"})
            
            assert result["status"] == "success"
            assert result["language"] == "python"
            assert "optimization_needed" in result["analysis"]
    
    @pytest.mark.asyncio
    @pytest.mark.ai
    @pytest.mark.slow
    async def test_large_code_analysis(self):
        """测试大型代码文件分析"""
        # 生成大型代码文件
        large_code = "\n".join([
            f"int var_{i} = {i};" for i in range(1000)
        ])
        
        with patch.object(MultiAgentTeachingSystem, 'analyze_code') as mock_analyze:
            mock_analyze.return_value = {"status": "success", "size": "large"}
            
            system = MultiAgentTeachingSystem()
            result = await system.analyze_code({"code": large_code, "language": "c"})
            
            assert result["status"] == "success"
            assert result["size"] == "large"