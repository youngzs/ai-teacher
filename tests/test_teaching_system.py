"""
AI教学助手系统 - 完整测试套件
测试多智能体教学系统的各个组件和工作流

Author: AI Architecture Expert  
Date: 2025-09-09
"""

import pytest
import asyncio
import json
import sys
import os
from datetime import datetime
from unittest.mock import Mock, patch, AsyncMock

# 添加项目路径
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from src.agents.teaching_agents import MultiAgentTeachingSystem, TeachingAgentFactory
from src.workflows.teaching_workflows import WorkflowManager, WorkflowType, WorkflowStatus
from src.models.teaching_models import (
    SubmissionData, ProgrammingLanguage, StudentProfile, DifficultyLevel,
    create_sample_submission, create_sample_student_profile
)
from src.utils.code_analyzer import CodeExecutor, StaticCodeAnalyzer
from src.config.agents_config import AgentRole, SYSTEM_CONFIG

class TestAgentFactory:
    """测试Agent工厂类"""
    
    def test_create_single_agent(self):
        """测试创建单个Agent"""
        agent = TeachingAgentFactory.create_agent(AgentRole.CODE_ANALYZER)
        
        assert agent is not None
        assert agent.name == "CodeAnalyzer"
        assert "代码分析专家" in agent.system_message
    
    def test_create_all_agents(self):
        """测试创建所有Agent"""
        agents = TeachingAgentFactory.create_all_agents()
        
        assert len(agents) == 6  # 应该有6个Agent
        expected_agents = [role.value for role in AgentRole]
        
        for agent_name in expected_agents:
            assert agent_name in agents
            assert agents[agent_name].name == agent_name

class TestCodeExecutor:
    """测试代码执行器"""
    
    def __init__(self):
        self.executor = CodeExecutor()
    
    @pytest.mark.asyncio
    async def test_execute_valid_python_code(self):
        """测试执行有效Python代码"""
        code = """
print("Hello, World!")
result = 2 + 2
print(f"2 + 2 = {result}")
"""
        result = await self.executor.execute_safely(code, "python")
        
        assert result.success is True
        assert "Hello, World!" in result.output
        assert "2 + 2 = 4" in result.output
        assert result.execution_time > 0
    
    @pytest.mark.asyncio
    async def test_execute_python_with_syntax_error(self):
        """测试执行有语法错误的Python代码"""
        code = """
print("Hello, World!"  # 缺少闭合括号
result = 2 + 2
"""
        result = await self.executor.execute_safely(code, "python")
        
        assert result.success is False
        assert "SyntaxError" in result.error or "unexpected EOF" in result.error
    
    @pytest.mark.asyncio
    async def test_execute_infinite_loop_timeout(self):
        """测试无限循环超时"""
        code = """
while True:
    pass
"""
        result = await self.executor.execute_safely(code, "python", timeout=2)
        
        assert result.success is False
        assert "超时" in result.error or "timeout" in result.error.lower()
    
    @pytest.mark.asyncio 
    async def test_unsafe_code_blocking(self):
        """测试不安全代码被阻止"""
        unsafe_code = """
import os
os.system("rm -rf /")  # 危险操作
"""
        result = await self.executor.execute_safely(unsafe_code, "python")
        
        assert result.success is False
        assert "不安全" in result.error or result.output == ""

class TestStaticCodeAnalyzer:
    """测试静态代码分析器"""
    
    def __init__(self):
        self.analyzer = StaticCodeAnalyzer(ProgrammingLanguage.PYTHON)
    
    def test_analyze_good_python_code(self):
        """测试分析高质量Python代码"""
        good_code = """
def calculate_fibonacci(n):
    \"\"\"计算斐波那契数列的第n项\"\"\"
    if n <= 1:
        return n
    
    prev, curr = 0, 1
    for i in range(2, n + 1):
        prev, curr = curr, prev + curr
    
    return curr

# 测试函数
for i in range(10):
    print(f"F({i}) = {calculate_fibonacci(i)}")
"""
        result = self.analyzer.analyze_code_quality(good_code)
        
        assert "error" not in result
        assert result["function_count"] >= 1
        assert result["comment_ratio"] > 0
        assert "良好的函数化设计" in result["strengths"]
    
    def test_analyze_python_naming_issues(self):
        """测试Python命名规范问题"""
        bad_naming_code = """
def CalculateAverage(NumberList):  # 应该使用小写+下划线
    Total = 0  # 变量名应该小写
    for Number in NumberList:
        Total += Number
    return Total / len(NumberList)

MyList = [1, 2, 3, 4, 5]
Result = CalculateAverage(MyList)
"""
        result = self.analyzer.analyze_code_quality(bad_naming_code)
        
        naming_issues = [issue for issue in result.get("issues", []) if issue["type"] == "naming"]
        assert len(naming_issues) > 0

class TestDataModels:
    """测试数据模型"""
    
    def test_submission_data_creation(self):
        """测试创建提交数据"""
        submission = create_sample_submission()
        
        assert submission.student_id == "student_001"
        assert submission.language == ProgrammingLanguage.PYTHON
        assert len(submission.code) > 0
        assert isinstance(submission.submitted_at, datetime)
    
    def test_student_profile_creation(self):
        """测试创建学生画像"""
        profile = create_sample_student_profile()
        
        assert profile.student_id == "student_001"
        assert profile.competency_level == DifficultyLevel.ADVANCED_BEGINNER
        assert "syntax" in profile.skill_scores
        assert "confidence" in profile.emotional_state
    
    def test_model_serialization(self):
        """测试模型序列化"""
        submission = create_sample_submission()
        profile = create_sample_student_profile()
        
        # 测试转换为字典
        submission_dict = submission.to_dict()
        profile_dict = profile.to_dict()
        
        assert isinstance(submission_dict, dict)
        assert isinstance(profile_dict, dict)
        assert submission_dict["student_id"] == "student_001"
        assert profile_dict["competency_level"] == "advanced_beginner"
        
        # 测试从字典恢复
        restored_submission = SubmissionData.from_dict(submission_dict)
        restored_profile = StudentProfile.from_dict(profile_dict)
        
        assert restored_submission.student_id == submission.student_id
        assert restored_profile.competency_level == profile.competency_level

class TestWorkflowSystem:
    """测试工作流系统"""
    
    def __init__(self):
        # 使用Mock对象避免实际的LLM调用
        self.mock_teaching_system = Mock(spec=MultiAgentTeachingSystem)
        self.workflow_manager = WorkflowManager(self.mock_teaching_system)
    
    def _create_mock_feedback(self):
        """创建模拟的教学反馈"""
        from src.models.teaching_models import TeachingFeedback
        
        return TeachingFeedback(
            session_id="test_session_001",
            student_id="test_student_001",
            overall_score=85.0,
            code_analysis={"syntax_score": 90, "logic_score": 80},
            student_profile={"competency_level": "intermediate"},
            teaching_strategy="HINT",
            feedback_content={"recognition": "Good effort!"},
            recommendations={"focus_areas": ["loops"]},
            quality_score=88,
            next_steps=["Practice more loop exercises"],
            estimated_completion_time="20分钟",
            created_at=datetime.now()
        )
    
    @pytest.mark.asyncio
    async def test_assignment_analysis_workflow(self):
        """测试作业分析工作流"""
        # 设置mock返回值
        mock_feedback = self._create_mock_feedback()
        self.mock_teaching_system.process_submission = AsyncMock(return_value=mock_feedback)
        
        # 创建测试提交
        submission = create_sample_submission()
        
        # 执行工作流
        result = await self.workflow_manager.execute_assignment_analysis(submission)
        
        # 验证结果
        assert result.status == WorkflowStatus.COMPLETED
        assert result.workflow_type == WorkflowType.ASSIGNMENT_ANALYSIS
        assert result.feedback is not None
        assert result.execution_time > 0
        
        # 验证mock被调用
        self.mock_teaching_system.process_submission.assert_called_once_with(submission)
    
    @pytest.mark.asyncio
    async def test_debugging_guidance_workflow(self):
        """测试调试指导工作流"""
        mock_feedback = self._create_mock_feedback()
        mock_feedback.teaching_strategy = "DEBUGGING"
        self.mock_teaching_system.process_debugging_session = AsyncMock(return_value=mock_feedback)
        
        submission = create_sample_submission()
        submission.student_message = "我的代码有bug，不知道如何调试"
        
        result = await self.workflow_manager.execute_debugging_guidance(submission)
        
        assert result.status == WorkflowStatus.COMPLETED
        assert result.workflow_type == WorkflowType.DEBUGGING_GUIDANCE
        assert result.feedback.teaching_strategy == "DEBUGGING"
    
    @pytest.mark.asyncio
    async def test_personalized_learning_workflow(self):
        """测试个性化学习工作流"""
        mock_feedback = self._create_mock_feedback()
        mock_feedback.teaching_strategy = "PERSONALIZED"
        self.mock_teaching_system.process_personalized_learning = AsyncMock(return_value=mock_feedback)
        
        submission = create_sample_submission()
        learning_history = [
            {"assignment_id": "test_1", "score": 85, "time": "30min"},
            {"assignment_id": "test_2", "score": 90, "time": "25min"}
        ]
        
        result = await self.workflow_manager.execute_personalized_learning(submission, learning_history)
        
        assert result.status == WorkflowStatus.COMPLETED
        assert result.workflow_type == WorkflowType.PERSONALIZED_LEARNING
        assert result.feedback.teaching_strategy == "PERSONALIZED"
    
    @pytest.mark.asyncio
    async def test_batch_processing(self):
        """测试批量处理"""
        mock_feedback = self._create_mock_feedback()
        self.mock_teaching_system.process_submission = AsyncMock(return_value=mock_feedback)
        
        # 创建多个提交
        submissions = []
        for i in range(5):
            submission = create_sample_submission()
            submission.student_id = f"batch_student_{i}"
            submissions.append(submission)
        
        results = await self.workflow_manager.execute_batch_workflows(
            submissions, WorkflowType.ASSIGNMENT_ANALYSIS
        )
        
        assert len(results) == 5
        assert all(r.status == WorkflowStatus.COMPLETED for r in results)
        
        # 验证性能指标
        summary = self.workflow_manager.get_performance_summary()
        assert summary["total_workflows"] >= 5
        assert summary["success_rate"] > 0

class TestSystemConfiguration:
    """测试系统配置"""
    
    def test_system_config_values(self):
        """测试系统配置值"""
        assert SYSTEM_CONFIG["max_concurrent_sessions"] > 0
        assert SYSTEM_CONFIG["target_response_time"] > 0
        assert SYSTEM_CONFIG["target_accuracy"] <= 1.0
    
    def test_agent_configurations(self):
        """测试Agent配置"""
        from src.config.agents_config import AgentConfigurations
        
        all_configs = AgentConfigurations.get_all_configs()
        assert len(all_configs) == 6
        
        for role in AgentRole:
            config = AgentConfigurations.get_agent_config(role)
            assert "name" in config
            assert "system_message" in config
            assert "llm_config" in config

class TestPerformanceMetrics:
    """测试性能指标"""
    
    def test_response_time_measurement(self):
        """测试响应时间测量"""
        from src.utils.logger import LogExecutionTime
        
        with LogExecutionTime("test_operation") as timer:
            import time
            time.sleep(0.1)  # 模拟操作
        
        # 测试执行时间大致正确（允许一些误差）
        assert 0.08 <= (datetime.now() - timer.start_time).total_seconds() <= 0.15
    
    def test_workflow_metrics_collection(self):
        """测试工作流指标收集"""
        mock_system = Mock(spec=MultiAgentTeachingSystem)
        manager = WorkflowManager(mock_system)
        
        # 检查初始指标
        summary = manager.get_performance_summary()
        assert summary["total_workflows"] == 0
        assert summary["success_rate"] == 0.0

# 集成测试
class TestSystemIntegration:
    """测试系统集成"""
    
    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_end_to_end_workflow(self):
        """端到端工作流测试（需要真实环境）"""
        # 这个测试需要真实的LLM环境，标记为integration
        pytest.skip("需要真实的LLM API密钥")
        
        system = MultiAgentTeachingSystem("python_basics")
        manager = WorkflowManager(system)
        
        submission = create_sample_submission()
        result = await manager.execute_assignment_analysis(submission)
        
        assert result.status == WorkflowStatus.COMPLETED
        assert result.feedback is not None
        assert result.feedback.overall_score >= 0

# 性能测试
class TestPerformance:
    """性能测试"""
    
    @pytest.mark.performance
    @pytest.mark.asyncio
    async def test_concurrent_workflows(self):
        """测试并发工作流处理"""
        mock_system = Mock(spec=MultiAgentTeachingSystem)
        mock_feedback = TeachingFeedback(
            session_id="perf_test",
            student_id="perf_student",
            overall_score=80.0,
            code_analysis={},
            student_profile={},
            teaching_strategy="TEST",
            feedback_content={},
            recommendations={},
            quality_score=85,
            next_steps=[],
            estimated_completion_time="10分钟",
            created_at=datetime.now()
        )
        
        # 模拟快速响应
        async def quick_response(*args, **kwargs):
            await asyncio.sleep(0.1)  # 模拟处理时间
            return mock_feedback
        
        mock_system.process_submission = AsyncMock(side_effect=quick_response)
        
        manager = WorkflowManager(mock_system)
        
        # 创建多个并发任务
        submissions = [create_sample_submission() for _ in range(10)]
        for i, sub in enumerate(submissions):
            sub.student_id = f"perf_student_{i}"
        
        start_time = datetime.now()
        results = await manager.execute_batch_workflows(submissions)
        end_time = datetime.now()
        
        total_time = (end_time - start_time).total_seconds()
        
        # 验证并发处理效果（应该比串行快）
        assert len(results) == 10
        assert all(r.status == WorkflowStatus.COMPLETED for r in results)
        assert total_time < 2.0  # 并发处理应该在2秒内完成

# 测试运行器
def run_all_tests():
    """运行所有测试"""
    print("🧪 开始运行AI教学助手系统测试套件...")
    
    # 基础组件测试
    test_classes = [
        TestAgentFactory,
        TestCodeExecutor,
        TestStaticCodeAnalyzer,
        TestDataModels,
        TestWorkflowSystem,
        TestSystemConfiguration,
        TestPerformanceMetrics
    ]
    
    total_tests = 0
    passed_tests = 0
    
    for test_class in test_classes:
        print(f"\n🔬 测试 {test_class.__name__}...")
        
        test_instance = test_class()
        test_methods = [method for method in dir(test_instance) if method.startswith("test_")]
        
        for method_name in test_methods:
            total_tests += 1
            try:
                method = getattr(test_instance, method_name)
                if asyncio.iscoroutinefunction(method):
                    asyncio.run(method())
                else:
                    method()
                print(f"  ✅ {method_name}")
                passed_tests += 1
            except Exception as e:
                print(f"  ❌ {method_name}: {e}")
    
    print(f"\n📊 测试结果总结:")
    print(f"   总测试数: {total_tests}")
    print(f"   通过: {passed_tests}")
    print(f"   失败: {total_tests - passed_tests}")
    print(f"   成功率: {passed_tests/total_tests*100:.1f}%")
    
    return passed_tests == total_tests

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)