"""
AI教学助手系统 - 教学场景演示
提供完整的教学场景演示，展示多智能体系统的教学能力

Author: AI Architecture Expert
Date: 2025-09-09
"""

import asyncio
import json
from datetime import datetime
from typing import Dict, List, Any
import sys
import os

# 添加项目路径
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from src.agents.teaching_agents import MultiAgentTeachingSystem
from src.workflows.teaching_workflows import WorkflowManager
from src.models.teaching_models import (
    SubmissionData, ProgrammingLanguage, create_sample_submission, 
    create_sample_student_profile
)
from src.utils.logger import get_logger

logger = get_logger(__name__)

class TeachingScenarioDemo:
    """教学场景演示类"""
    
    def __init__(self):
        """初始化演示环境"""
        print("🚀 初始化AI教学助手系统演示环境...")
        self.teaching_system = MultiAgentTeachingSystem("python_basics")
        self.workflow_manager = WorkflowManager(self.teaching_system)
        print("✅ 系统初始化完成！\n")
    
    async def run_all_scenarios(self):
        """运行所有教学场景演示"""
        print("=" * 80)
        print("🎓 AI教学助手系统 - 完整场景演示")
        print("=" * 80)
        
        scenarios = [
            ("场景1: 新手学生第一次提交作业", self.scenario_1_novice_first_submission),
            ("场景2: 中级学生遇到调试问题", self.scenario_2_debugging_assistance),
            ("场景3: 优秀学生需要进阶挑战", self.scenario_3_advanced_challenge),
            ("场景4: 个性化学习路径推荐", self.scenario_4_personalized_learning),
            ("场景5: 批量作业处理演示", self.scenario_5_batch_processing)
        ]
        
        for scenario_name, scenario_func in scenarios:
            print(f"\n{'='*60}")
            print(f"▶️  {scenario_name}")
            print(f"{'='*60}")
            
            try:
                await scenario_func()
                print(f"✅ {scenario_name} 执行成功")
            except Exception as e:
                print(f"❌ {scenario_name} 执行失败: {e}")
                logger.error(f"Scenario failed: {scenario_name}", exc_info=True)
        
        print(f"\n{'='*80}")
        print("📊 系统性能摘要")
        print(f"{'='*80}")
        self.print_performance_summary()
    
    async def scenario_1_novice_first_submission(self):
        """场景1: 新手学生第一次提交作业"""
        print("📚 学生背景: 大一新生，第一次学习Python，对编程概念不熟悉")
        print("📝 作业要求: 编写程序打印1到10的所有偶数")
        
        # 新手学生的代码（包含常见错误）
        novice_code = '''
# 我想打印偶数但不知道怎么写
for i in range(1, 11)
    if i % 2 = 0:  # 这里应该用==但我用了=
        print(i)
'''
        
        submission = SubmissionData(
            student_id="novice_001",
            assignment_id="python_even_numbers",
            assignment_description="编写一个程序，使用for循环打印1到10的所有偶数",
            code=novice_code,
            language=ProgrammingLanguage.PYTHON,
            submitted_at=datetime.now(),
            student_history={
                "programming_experience": "none",
                "previous_assignments": 0,
                "confidence_level": "low",
                "learning_style": "visual"
            },
            student_message="这是我第一次写代码，不确定语法对不对。"
        )
        
        print(f"📋 学生提交的代码:")
        print("```python")
        print(novice_code.strip())
        print("```")
        
        # 执行作业分析工作流
        print("\n🔄 正在进行多智能体协作分析...")
        result = await self.workflow_manager.execute_assignment_analysis(submission)
        
        if result.feedback:
            print(f"\n📊 分析结果:")
            print(f"   - 总体评分: {result.feedback.overall_score:.1f}/100")
            print(f"   - 教学策略: {result.feedback.teaching_strategy}")
            print(f"   - 质量评分: {result.feedback.quality_score}/100")
            print(f"   - 处理时间: {result.execution_time:.2f}秒")
            
            print(f"\n💬 AI教学反馈:")
            self._print_formatted_feedback(result.feedback)
        
        return result
    
    async def scenario_2_debugging_assistance(self):
        """场景2: 中级学生遇到调试问题"""
        print("👨‍💻 学生背景: 有一定编程基础，但在复杂问题上需要调试指导")
        print("🐛 问题: 实现斐波那契数列时出现逻辑错误")
        
        debugging_code = '''
def fibonacci(n):
    if n <= 1:
        return n
    
    a, b = 0, 1
    for i in range(2, n):  # 这里少了一次迭代
        a, b = b, a + b
    
    return b

# 测试
print("前10个斐波那契数:")
for i in range(10):
    print(f"F({i}) = {fibonacci(i)}")
'''
        
        submission = SubmissionData(
            student_id="intermediate_001",
            assignment_id="fibonacci_sequence",
            assignment_description="实现斐波那契数列函数并打印前10个数",
            code=debugging_code,
            language=ProgrammingLanguage.PYTHON,
            submitted_at=datetime.now(),
            student_history={
                "programming_experience": "intermediate",
                "previous_assignments": 15,
                "common_errors": ["off-by-one", "logic"],
                "debugging_skill": "developing"
            },
            student_message="我的斐波那契函数输出不对，但不知道哪里出了问题。"
        )
        
        print(f"📋 学生提交的代码:")
        print("```python")
        print(debugging_code.strip())
        print("```")
        
        print("\n🔍 正在启动调试指导工作流...")
        result = await self.workflow_manager.execute_debugging_guidance(submission)
        
        if result.feedback:
            print(f"\n📊 调试分析结果:")
            print(f"   - 发现问题类型: {self._extract_error_types(result.feedback)}")
            print(f"   - 指导质量: {result.feedback.quality_score}/100")
            print(f"   - 处理时间: {result.execution_time:.2f}秒")
            
            print(f"\n🤖 调试导师指导:")
            self._print_formatted_feedback(result.feedback)
        
        return result
    
    async def scenario_3_advanced_challenge(self):
        """场景3: 优秀学生需要进阶挑战"""
        print("🌟 学生背景: 编程基础扎实，完成作业质量高，需要进阶挑战")
        print("✨ 提交: 高质量的排序算法实现")
        
        advanced_code = '''
def quicksort(arr):
    """
    快速排序实现
    时间复杂度: 平均O(n log n), 最坏O(n²)
    空间复杂度: O(log n)
    """
    if len(arr) <= 1:
        return arr
    
    pivot = arr[len(arr) // 2]
    left = [x for x in arr if x < pivot]
    middle = [x for x in arr if x == pivot]
    right = [x for x in arr if x > pivot]
    
    return quicksort(left) + middle + quicksort(right)

# 测试不同情况
test_cases = [
    [64, 34, 25, 12, 22, 11, 90],
    [1],
    [],
    [5, 5, 5, 5],
    list(range(100, 0, -1))  # 反向排序测试
]

for i, case in enumerate(test_cases):
    original = case.copy()
    sorted_result = quicksort(case)
    print(f"测试 {i+1}: {original[:5]}{'...' if len(original) > 5 else ''} -> {sorted_result[:5]}{'...' if len(sorted_result) > 5 else ''}")
'''
        
        submission = SubmissionData(
            student_id="advanced_001",
            assignment_id="sorting_algorithms",
            assignment_description="实现一个高效的排序算法并进行测试",
            code=advanced_code,
            language=ProgrammingLanguage.PYTHON,
            submitted_at=datetime.now(),
            student_history={
                "programming_experience": "advanced",
                "previous_assignments": 25,
                "average_score": 92.5,
                "skill_areas": ["algorithms", "optimization", "testing"],
                "interested_topics": ["algorithms", "data_structures", "performance"]
            },
            student_message="我实现了快速排序，想知道还有什么可以改进的地方。"
        )
        
        print(f"📋 学生提交的代码:")
        print("```python")
        print(advanced_code.strip())
        print("```")
        
        print("\n🚀 正在进行高级代码分析...")
        result = await self.workflow_manager.execute_assignment_analysis(submission)
        
        if result.feedback:
            print(f"\n📊 分析结果:")
            print(f"   - 总体评分: {result.feedback.overall_score:.1f}/100")
            print(f"   - 教学策略: {result.feedback.teaching_strategy}")
            print(f"   - 处理时间: {result.execution_time:.2f}秒")
            
            print(f"\n🎯 进阶挑战建议:")
            self._print_formatted_feedback(result.feedback)
        
        return result
    
    async def scenario_4_personalized_learning(self):
        """场景4: 个性化学习路径推荐"""
        print("📈 学生背景: 学习一段时间后需要个性化指导")
        print("🎯 目标: 基于学习历史制定个性化学习计划")
        
        current_code = '''
def calculate_average(numbers):
    total = sum(numbers)
    return total / len(numbers)

def find_max(numbers):
    max_val = numbers[0]
    for num in numbers:
        if num > max_val:
            max_val = num
    return max_val

# 测试
data = [85, 92, 78, 96, 88]
print(f"平均分: {calculate_average(data)}")
print(f"最高分: {find_max(data)}")
'''
        
        # 学习历史数据
        learning_history = [
            {
                "assignment_id": "variables_basics",
                "score": 85,
                "completion_time": "20分钟",
                "errors": ["syntax"],
                "concepts_mastered": ["variables", "basic_operations"]
            },
            {
                "assignment_id": "conditionals",
                "score": 78,
                "completion_time": "35分钟", 
                "errors": ["logic", "comparison_operators"],
                "concepts_mastered": ["if_statements"]
            },
            {
                "assignment_id": "loops_basic",
                "score": 88,
                "completion_time": "25分钟",
                "errors": ["range_function"],
                "concepts_mastered": ["for_loops", "range"]
            },
            {
                "assignment_id": "functions_intro",
                "score": 92,
                "completion_time": "30分钟",
                "errors": [],
                "concepts_mastered": ["function_definition", "parameters", "return"]
            }
        ]
        
        submission = SubmissionData(
            student_id="regular_001",
            assignment_id="data_analysis_basic",
            assignment_description="编写函数计算数据的平均值和最大值",
            code=current_code,
            language=ProgrammingLanguage.PYTHON,
            submitted_at=datetime.now(),
            student_history={
                "programming_experience": "intermediate_beginner",
                "learning_pattern": "steady_improver",
                "preferred_difficulty": "moderate_challenge",
                "weak_areas": ["logic", "complex_algorithms"],
                "strong_areas": ["syntax", "functions"]
            },
            student_message="我想知道接下来应该学什么内容。"
        )
        
        print(f"📋 学生当前代码:")
        print("```python")
        print(current_code.strip())
        print("```")
        
        print(f"\n📚 学习历史: {len(learning_history)}次作业记录")
        for i, record in enumerate(learning_history, 1):
            print(f"   {i}. {record['assignment_id']}: {record['score']}分 ({record['completion_time']})")
        
        print("\n🧠 正在生成个性化学习建议...")
        result = await self.workflow_manager.execute_personalized_learning(submission, learning_history)
        
        if result.feedback:
            print(f"\n📊 个性化分析结果:")
            print(f"   - 学习能力评估: {self._assess_learning_ability(learning_history)}")
            print(f"   - 推荐质量: {result.feedback.quality_score}/100")
            print(f"   - 处理时间: {result.execution_time:.2f}秒")
            
            print(f"\n🎯 个性化学习路径:")
            self._print_formatted_feedback(result.feedback)
        
        return result
    
    async def scenario_5_batch_processing(self):
        """场景5: 批量作业处理演示"""
        print("🏫 场景: 班级作业批量处理（模拟50人班级）")
        print("📋 作业: Python列表操作练习")
        
        # 生成多样化的学生提交
        submissions = self._generate_diverse_submissions()
        
        print(f"📊 批量处理信息:")
        print(f"   - 学生数量: {len(submissions)}人")
        print(f"   - 代码长度范围: {min(len(s.code) for s in submissions)}-{max(len(s.code) for s in submissions)}字符")
        
        print(f"\n⚡ 正在批量处理作业...")
        start_time = datetime.now()
        
        results = await self.workflow_manager.execute_batch_workflows(
            submissions, 
            workflow_type=self.workflow_manager.teaching_system.workflows.WorkflowType.ASSIGNMENT_ANALYSIS
        )
        
        end_time = datetime.now()
        total_time = (end_time - start_time).total_seconds()
        
        print(f"\n📊 批量处理结果:")
        print(f"   - 总处理时间: {total_time:.2f}秒")
        print(f"   - 平均处理时间: {total_time/len(results):.2f}秒/份")
        print(f"   - 成功处理: {sum(1 for r in results if r.status.value == 'completed')}/{len(results)}")
        
        # 分析批量结果
        self._analyze_batch_results(results)
        
        return results
    
    def _generate_diverse_submissions(self) -> List[SubmissionData]:
        """生成多样化的学生提交"""
        code_samples = [
            # 正确的实现
            '''
def process_list(numbers):
    result = []
    for num in numbers:
        if num % 2 == 0:
            result.append(num * 2)
    return result

test_list = [1, 2, 3, 4, 5, 6]
print(process_list(test_list))
''',
            # 语法错误
            '''
def process_list(numbers):
    result = []
    for num in numbers
        if num % 2 == 0:
            result.append(num * 2)
    return result

test_list = [1, 2, 3, 4, 5, 6]
print(process_list(test_list))
''',
            # 逻辑错误
            '''
def process_list(numbers):
    result = []
    for num in numbers:
        if num % 2 = 0:  # 错误的比较操作符
            result.append(num * 2)
    return result

test_list = [1, 2, 3, 4, 5, 6]
print(process_list(test_list))
''',
            # 优化的实现
            '''
def process_list(numbers):
    """使用列表推导式的优化版本"""
    return [num * 2 for num in numbers if num % 2 == 0]

def process_list_verbose(numbers):
    """详细的实现版本，便于理解"""
    even_numbers = []
    for num in numbers:
        if num % 2 == 0:  # 检查是否为偶数
            doubled = num * 2  # 乘以2
            even_numbers.append(doubled)
    return even_numbers

# 测试两种实现
test_data = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
print("优化版本:", process_list(test_data))
print("详细版本:", process_list_verbose(test_data))
'''
        ]
        
        submissions = []
        for i, code in enumerate(code_samples * 3):  # 复制以产生更多样本
            student_id = f"batch_student_{i+1:02d}"
            submissions.append(SubmissionData(
                student_id=student_id,
                assignment_id="list_processing",
                assignment_description="编写函数处理列表，提取偶数并乘以2",
                code=code.strip(),
                language=ProgrammingLanguage.PYTHON,
                submitted_at=datetime.now(),
                student_history={
                    "programming_experience": ["beginner", "intermediate", "advanced"][i % 3],
                    "previous_assignments": (i % 10) + 1
                }
            ))
        
        return submissions
    
    def _analyze_batch_results(self, results):
        """分析批量处理结果"""
        if not results:
            return
        
        scores = [r.feedback.overall_score for r in results if r.feedback]
        strategies = [r.feedback.teaching_strategy for r in results if r.feedback]
        
        print(f"\n📈 批量结果分析:")
        if scores:
            print(f"   - 平均分: {sum(scores)/len(scores):.1f}")
            print(f"   - 分数范围: {min(scores):.1f}-{max(scores):.1f}")
        
        if strategies:
            strategy_count = {}
            for strategy in strategies:
                strategy_count[strategy] = strategy_count.get(strategy, 0) + 1
            print(f"   - 教学策略分布:")
            for strategy, count in strategy_count.items():
                print(f"     • {strategy}: {count}人 ({count/len(strategies)*100:.1f}%)")
    
    def _extract_error_types(self, feedback) -> str:
        """从反馈中提取错误类型"""
        if not feedback.code_analysis or not isinstance(feedback.code_analysis, dict):
            return "未识别"
        
        errors = feedback.code_analysis.get('critical_errors', [])
        if not errors:
            return "无明显错误"
        
        error_types = [error.get('type', '未知') for error in errors if isinstance(error, dict)]
        return ", ".join(set(error_types))
    
    def _assess_learning_ability(self, learning_history) -> str:
        """评估学习能力"""
        if not learning_history:
            return "数据不足"
        
        scores = [record.get('score', 0) for record in learning_history]
        avg_score = sum(scores) / len(scores)
        
        if avg_score >= 90:
            return "优秀"
        elif avg_score >= 80:
            return "良好" 
        elif avg_score >= 70:
            return "中等"
        else:
            return "需要加强"
    
    def _print_formatted_feedback(self, feedback):
        """格式化打印教学反馈"""
        if not feedback or not feedback.feedback_content:
            print("   - 暂无详细反馈内容")
            return
        
        content = feedback.feedback_content
        
        if isinstance(content, dict):
            if 'recognition' in content:
                print(f"   📝 认可: {content['recognition']}")
            
            if 'reflection' in content:
                print(f"   🤔 引导思考: {content['reflection']}")
            
            if 'reconstruction' in content:
                recon = content['reconstruction']
                if isinstance(recon, dict):
                    if 'critical_issues' in recon:
                        print(f"   🔍 关键问题: {len(recon['critical_issues'])}个")
                        for issue in recon['critical_issues'][:2]:  # 只显示前2个
                            if isinstance(issue, dict):
                                print(f"     • {issue.get('issue', '未知问题')}")
                    
                    if 'step_by_step' in recon:
                        print(f"   📋 改进步骤: {len(recon['step_by_step'])}步")
                        for i, step in enumerate(recon['step_by_step'][:3], 1):
                            print(f"     {i}. {step}")
            
            if 'reinforcement' in content:
                print(f"   💪 鼓励: {content['reinforcement']}")
        
        if feedback.next_steps:
            print(f"   🎯 下一步建议:")
            for step in feedback.next_steps[:3]:  # 只显示前3个
                print(f"     • {step}")
    
    def print_performance_summary(self):
        """打印系统性能摘要"""
        summary = self.workflow_manager.get_performance_summary()
        
        print(f"   总处理数量: {summary['total_workflows']}")
        print(f"   成功率: {summary['success_rate']*100:.1f}%")
        print(f"   平均执行时间: {summary['average_execution_time']:.2f}秒")
        print(f"   当前活跃会话: {summary['active_workflows']}")

async def main():
    """主演示函数"""
    try:
        demo = TeachingScenarioDemo()
        await demo.run_all_scenarios()
        
        print(f"\n{'='*80}")
        print("🎉 AI教学助手系统演示完成！")
        print("💡 该系统展示了多智能体协作在教育领域的强大能力")
        print(f"{'='*80}")
        
    except KeyboardInterrupt:
        print("\n⏹️  演示被用户中断")
    except Exception as e:
        print(f"\n❌ 演示过程中发生错误: {e}")
        logger.error("Demo failed", exc_info=True)

if __name__ == "__main__":
    # 设置事件循环策略（Windows兼容性）
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
    
    asyncio.run(main())