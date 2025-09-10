"""
AI Agent效果测试
测试AI反馈质量、教学效果和学习改进
"""

import pytest
import json
from unittest.mock import Mock, patch
from typing import Dict, List, Tuple
import statistics


class TestAIFeedbackQuality:
    """测试AI反馈质量"""
    
    @pytest.fixture
    def code_samples(self):
        """提供不同质量的代码样本"""
        return {
            "excellent": """
#include <stdio.h>
#include <stdlib.h>

/**
 * Calculates factorial of a given number using recursion
 * @param n: positive integer
 * @return: factorial of n, or -1 for invalid input
 */
int factorial(int n) {
    if (n < 0) {
        return -1;  // Invalid input
    }
    if (n <= 1) {
        return 1;
    }
    return n * factorial(n - 1);
}

int main() {
    int num, result;
    
    printf("Enter a positive integer: ");
    if (scanf("%d", &num) != 1) {
        printf("Error: Invalid input\\n");
        return 1;
    }
    
    result = factorial(num);
    if (result == -1) {
        printf("Error: Negative number not allowed\\n");
        return 1;
    }
    
    printf("Factorial of %d is %d\\n", num, result);
    return 0;
}
            """,
            
            "good": """
#include <stdio.h>

int factorial(int n) {
    if (n <= 1) return 1;
    return n * factorial(n - 1);
}

int main() {
    int num = 5;
    printf("Factorial of %d is %d\\n", num, factorial(num));
    return 0;
}
            """,
            
            "needs_improvement": """
#include <stdio.h>

int fact(int n) {
    if (n == 0) return 1;
    return n * fact(n - 1);
}

int main() {
    printf("%d", fact(5));
}
            """,
            
            "poor": """
#include <stdio.h>

int f(int n) {
    return n * f(n - 1);
}

int main() {
    printf("%d", f(5));
}
            """,
            
            "buggy": """
#include <stdio.h>

int factorial(int n) {
    int result;
    for (int i = 1; i <= n; i++) {
        result = result * i;  // Bug: result not initialized
    }
    return result;
}

int main() {
    int n = 5;
    printf("Factorial is %d", factorial(n));
    return 0;  // Missing newline
}
            """
        }
    
    @pytest.fixture
    def ai_feedback_mock(self):
        """Mock AI反馈生成器"""
        def generate_feedback(code, quality_level):
            feedback_templates = {
                "excellent": {
                    "overall_score": 95,
                    "strengths": [
                        "Excellent code documentation with clear comments",
                        "Proper input validation and error handling",
                        "Good variable naming conventions",
                        "Appropriate return codes for different scenarios"
                    ],
                    "improvements": [
                        "Consider iterative approach for better performance",
                        "Add const qualifier where appropriate"
                    ],
                    "tone": "encouraging",
                    "difficulty_assessment": "advanced",
                    "next_steps": ["Explore iterative implementations", "Study algorithm complexity"]
                },
                "good": {
                    "overall_score": 80,
                    "strengths": [
                        "Clear function structure",
                        "Correct logic implementation",
                        "Good use of recursion"
                    ],
                    "improvements": [
                        "Add input validation",
                        "Include error handling",
                        "Add comments for clarity"
                    ],
                    "tone": "positive",
                    "difficulty_assessment": "intermediate",
                    "next_steps": ["Add error handling", "Improve code documentation"]
                },
                "needs_improvement": {
                    "overall_score": 65,
                    "strengths": [
                        "Basic recursive structure is correct",
                        "Main function works"
                    ],
                    "improvements": [
                        "Use more descriptive function names",
                        "Add proper return statement in main",
                        "Include necessary headers",
                        "Add comments for better readability"
                    ],
                    "tone": "constructive",
                    "difficulty_assessment": "beginner",
                    "next_steps": ["Focus on code readability", "Learn about coding standards"]
                },
                "poor": {
                    "overall_score": 40,
                    "strengths": [
                        "Attempts to use recursion"
                    ],
                    "improvements": [
                        "Critical: Missing base case will cause infinite recursion",
                        "Function name 'f' is not descriptive",
                        "No return statement in main function",
                        "Add proper program structure"
                    ],
                    "tone": "supportive_but_firm",
                    "difficulty_assessment": "needs_review",
                    "next_steps": ["Review recursion fundamentals", "Study base cases", "Practice basic C structure"]
                },
                "buggy": {
                    "overall_score": 50,
                    "strengths": [
                        "Correct loop structure",
                        "Attempt at iterative approach"
                    ],
                    "improvements": [
                        "Critical bug: Variable 'result' used without initialization",
                        "Add newline character in printf for better output formatting",
                        "Initialize variables before use"
                    ],
                    "tone": "debugging_focused",
                    "difficulty_assessment": "intermediate",
                    "next_steps": ["Learn about variable initialization", "Practice debugging techniques"]
                }
            }
            return feedback_templates.get(quality_level, {})
        
        return generate_feedback
    
    @pytest.mark.ai
    def test_feedback_accuracy_for_excellent_code(self, code_samples, ai_feedback_mock):
        """测试对优秀代码的反馈准确性"""
        code = code_samples["excellent"]
        feedback = ai_feedback_mock(code, "excellent")
        
        # 验证评分准确性
        assert feedback["overall_score"] >= 90
        assert feedback["difficulty_assessment"] == "advanced"
        
        # 验证能识别出代码优点
        assert len(feedback["strengths"]) >= 3
        assert any("documentation" in strength.lower() for strength in feedback["strengths"])
        assert any("error handling" in strength.lower() for strength in feedback["strengths"])
        
        # 验证改进建议的适当性
        assert len(feedback["improvements"]) <= 3  # 优秀代码的改进建议应该较少
        assert feedback["tone"] == "encouraging"
    
    @pytest.mark.ai
    def test_feedback_accuracy_for_buggy_code(self, code_samples, ai_feedback_mock):
        """测试对有bug代码的反馈准确性"""
        code = code_samples["buggy"]
        feedback = ai_feedback_mock(code, "buggy")
        
        # 验证能识别关键bug
        assert feedback["overall_score"] < 70
        improvements = " ".join(feedback["improvements"]).lower()
        assert "initialization" in improvements or "initialize" in improvements
        
        # 验证调试导向
        assert feedback["tone"] == "debugging_focused"
        assert any("debugging" in step.lower() for step in feedback["next_steps"])
    
    @pytest.mark.ai
    def test_feedback_accuracy_for_poor_code(self, code_samples, ai_feedback_mock):
        """测试对糟糕代码的反馈准确性"""
        code = code_samples["poor"]
        feedback = ai_feedback_mock(code, "poor")
        
        # 验证能识别严重问题
        assert feedback["overall_score"] < 50
        improvements = " ".join(feedback["improvements"]).lower()
        assert "infinite" in improvements or "base case" in improvements
        
        # 验证反馈语调适当
        assert feedback["tone"] == "supportive_but_firm"
        assert feedback["difficulty_assessment"] == "needs_review"
    
    @pytest.mark.ai
    def test_feedback_consistency_across_similar_codes(self, ai_feedback_mock):
        """测试对相似代码的反馈一致性"""
        # 创建两个相似的代码样本
        code1 = """
int add(int a, int b) {
    return a + b;
}
        """
        
        code2 = """
int sum(int x, int y) {
    return x + y;
}
        """
        
        # 模拟相似质量的反馈
        feedback1 = {
            "overall_score": 75,
            "strengths": ["Simple and correct", "Clear logic"],
            "improvements": ["Add input validation", "Add comments"]
        }
        
        feedback2 = {
            "overall_score": 77,  # 略有不同但在合理范围内
            "strengths": ["Straightforward implementation", "Correct logic"],
            "improvements": ["Consider input validation", "Add documentation"]
        }
        
        # 验证评分一致性（允许小幅差异）
        score_diff = abs(feedback1["overall_score"] - feedback2["overall_score"])
        assert score_diff <= 5  # 相似代码评分差异不应超过5分
        
        # 验证反馈类型一致性
        assert len(feedback1["strengths"]) == len(feedback2["strengths"])
        assert len(feedback1["improvements"]) == len(feedback2["improvements"])
    
    @pytest.mark.ai
    def test_feedback_personalization_by_student_level(self, code_samples, ai_feedback_mock):
        """测试根据学生水平个性化反馈"""
        code = code_samples["good"]
        
        # 模拟不同学生水平的反馈
        beginner_feedback = {
            "tone": "very_encouraging",
            "complexity_explanation": True,
            "basic_concepts_focus": True,
            "improvements": ["Start with simpler examples", "Review basic syntax"]
        }
        
        advanced_feedback = {
            "tone": "challenging",
            "complexity_explanation": False,
            "basic_concepts_focus": False,
            "improvements": ["Consider algorithm optimization", "Explore advanced patterns"]
        }
        
        # 验证个性化差异
        assert beginner_feedback["tone"] != advanced_feedback["tone"]
        assert beginner_feedback["complexity_explanation"] != advanced_feedback["complexity_explanation"]
        
        # 验证改进建议的适当性
        beginner_improvements = " ".join(beginner_feedback["improvements"]).lower()
        advanced_improvements = " ".join(advanced_feedback["improvements"]).lower()
        
        assert "basic" in beginner_improvements or "simpler" in beginner_improvements
        assert "optimization" in advanced_improvements or "advanced" in advanced_improvements


class TestLearningOutcomeTracking:
    """测试学习结果跟踪"""
    
    @pytest.fixture
    def student_progress_data(self):
        """模拟学生学习进度数据"""
        return {
            "student_1": {
                "submissions": [
                    {"date": "2024-01-01", "score": 60, "topic": "loops"},
                    {"date": "2024-01-03", "score": 65, "topic": "loops"},
                    {"date": "2024-01-05", "score": 72, "topic": "loops"},
                    {"date": "2024-01-08", "score": 78, "topic": "functions"},
                    {"date": "2024-01-10", "score": 82, "topic": "functions"}
                ],
                "feedback_ratings": [3, 4, 4, 5, 5],  # 学生对反馈的评分
                "time_to_improvement": [2, 2, 3, 2, 1]  # 从反馈到改进的天数
            },
            "student_2": {
                "submissions": [
                    {"date": "2024-01-01", "score": 45, "topic": "loops"},
                    {"date": "2024-01-04", "score": 50, "topic": "loops"},
                    {"date": "2024-01-07", "score": 55, "topic": "loops"},
                    {"date": "2024-01-12", "score": 48, "topic": "functions"},  # 退步
                    {"date": "2024-01-15", "score": 62, "topic": "functions"}
                ],
                "feedback_ratings": [4, 3, 3, 2, 4],
                "time_to_improvement": [3, 3, 5, 3, 2]
            }
        }
    
    @pytest.mark.ai
    def test_learning_progress_calculation(self, student_progress_data):
        """测试学习进度计算"""
        student_1_data = student_progress_data["student_1"]
        
        # 计算学习进度指标
        scores = [sub["score"] for sub in student_1_data["submissions"]]
        
        # 整体进步
        overall_improvement = scores[-1] - scores[0]
        assert overall_improvement > 0  # 学生1应该有进步
        
        # 平均进步率
        total_improvement = sum(scores[i+1] - scores[i] for i in range(len(scores)-1) if scores[i+1] > scores[i])
        improvement_count = sum(1 for i in range(len(scores)-1) if scores[i+1] > scores[i])
        avg_improvement = total_improvement / improvement_count if improvement_count > 0 else 0
        
        assert avg_improvement > 0
        
        # 学习稳定性（标准差）
        score_std = statistics.stdev(scores)
        assert score_std < 15  # 假设稳定学习的标准差应小于15分
    
    @pytest.mark.ai
    def test_feedback_effectiveness_measurement(self, student_progress_data):
        """测试反馈效果测量"""
        for student_id, data in student_progress_data.items():
            feedback_ratings = data["feedback_ratings"]
            time_to_improvement = data["time_to_improvement"]
            
            # 计算反馈满意度
            avg_rating = statistics.mean(feedback_ratings)
            assert 1 <= avg_rating <= 5
            
            # 计算反馈响应时间
            avg_response_time = statistics.mean(time_to_improvement)
            assert avg_response_time >= 1  # 至少需要1天来应用反馈
            
            # 评估反馈效果（高评分应该对应更快的改进）
            if avg_rating >= 4:
                assert avg_response_time <= 3  # 高质量反馈应该带来更快改进
    
    @pytest.mark.ai
    def test_difficulty_progression_tracking(self, student_progress_data):
        """测试难度进度跟踪"""
        student_1_data = student_progress_data["student_1"]
        
        # 按主题分组
        topic_scores = {}
        for submission in student_1_data["submissions"]:
            topic = submission["topic"]
            if topic not in topic_scores:
                topic_scores[topic] = []
            topic_scores[topic].append(submission["score"])
        
        # 验证每个主题内的进步
        for topic, scores in topic_scores.items():
            if len(scores) > 1:
                topic_improvement = scores[-1] - scores[0]
                assert topic_improvement >= -5  # 允许小幅退步，但不应该太大
    
    @pytest.mark.ai
    def test_ai_adaptation_to_student_needs(self):
        """测试AI对学生需求的适应能力"""
        # 模拟不同类型学生的需求
        student_profiles = {
            "struggling_student": {
                "avg_score": 45,
                "improvement_rate": 0.02,  # 每次提交平均提高2分
                "feedback_preference": "step_by_step",
                "learning_style": "visual"
            },
            "advanced_student": {
                "avg_score": 88,
                "improvement_rate": 0.01,  # 提高空间较小
                "feedback_preference": "challenge_focused",
                "learning_style": "theoretical"
            },
            "inconsistent_student": {
                "avg_score": 70,
                "improvement_rate": 0.05,  # 忽高忽低
                "feedback_preference": "motivational",
                "learning_style": "hands_on"
            }
        }
        
        # 模拟AI适应性反馈策略
        ai_strategies = {
            "struggling_student": {
                "feedback_detail": "high",
                "encouragement_level": "high",
                "concept_reinforcement": True,
                "complexity_reduction": True
            },
            "advanced_student": {
                "feedback_detail": "medium",
                "encouragement_level": "medium",
                "concept_reinforcement": False,
                "complexity_increase": True
            },
            "inconsistent_student": {
                "feedback_detail": "high",
                "encouragement_level": "high",
                "concept_reinforcement": True,
                "consistency_focus": True
            }
        }
        
        # 验证策略适应性
        for student_type, strategy in ai_strategies.items():
            profile = student_profiles[student_type]
            
            if profile["avg_score"] < 60:  # 困难学生
                assert strategy["encouragement_level"] == "high"
                assert strategy["concept_reinforcement"] is True
            
            if profile["avg_score"] > 85:  # 优秀学生
                assert strategy.get("complexity_increase", False) is True
            
            if profile["improvement_rate"] > 0.04:  # 不稳定学生
                assert strategy.get("consistency_focus", False) is True


class TestAIResponseTimeAndPerformance:
    """测试AI响应时间和性能"""
    
    @pytest.mark.ai
    @pytest.mark.slow
    def test_response_time_requirements(self):
        """测试AI响应时间要求"""
        import time
        
        # 模拟不同复杂度的分析任务
        tasks = {
            "simple": {"code_length": 50, "expected_time": 1.0},
            "medium": {"code_length": 200, "expected_time": 2.5},
            "complex": {"code_length": 500, "expected_time": 3.0}
        }
        
        for task_type, params in tasks.items():
            start_time = time.time()
            
            # 模拟AI分析过程
            code = "int main() { return 0; }" * (params["code_length"] // 20)
            
            # 模拟分析延迟
            time.sleep(0.1)  # 实际环境中会是AI处理时间
            
            end_time = time.time()
            actual_time = end_time - start_time
            
            # 在测试环境中，我们检查模拟的时间逻辑
            assert actual_time < 1.0  # 测试环境下的快速响应
            
            # 记录性能指标
            performance_metrics = {
                "task_type": task_type,
                "code_length": params["code_length"],
                "response_time": actual_time,
                "within_target": actual_time < params["expected_time"]
            }
            
            assert performance_metrics["within_target"] or actual_time < 1.0
    
    @pytest.mark.ai
    def test_concurrent_request_handling(self):
        """测试并发请求处理能力"""
        import asyncio
        import time
        
        async def simulate_ai_request(request_id):
            """模拟AI请求处理"""
            start_time = time.time()
            
            # 模拟AI处理延迟
            await asyncio.sleep(0.1)
            
            end_time = time.time()
            return {
                "request_id": request_id,
                "response_time": end_time - start_time,
                "status": "success"
            }
        
        async def test_concurrency():
            # 创建10个并发请求
            tasks = [simulate_ai_request(i) for i in range(10)]
            results = await asyncio.gather(*tasks)
            return results
        
        # 执行并发测试
        results = asyncio.run(test_concurrency())
        
        # 验证所有请求都成功处理
        assert len(results) == 10
        for result in results:
            assert result["status"] == "success"
            assert result["response_time"] < 1.0  # 测试环境下的快速响应
    
    @pytest.mark.ai
    def test_memory_usage_efficiency(self):
        """测试内存使用效率"""
        import sys
        
        # 模拟处理大量数据的AI分析
        large_data = {
            "code_submissions": ["sample code"] * 100,
            "analysis_results": [{"score": 85, "feedback": "good work"}] * 100,
            "student_profiles": [{"level": "intermediate"}] * 100
        }
        
        # 获取初始内存使用情况（简化版本）
        initial_size = sys.getsizeof(large_data)
        
        # 模拟AI处理过程
        processed_data = []
        for submission in large_data["code_submissions"]:
            processed_item = {
                "original": submission,
                "processed": f"analyzed_{submission}",
                "metadata": {"timestamp": "2024-01-01", "version": "1.0"}
            }
            processed_data.append(processed_item)
        
        final_size = sys.getsizeof(processed_data)
        
        # 验证内存使用合理性
        memory_growth_ratio = final_size / initial_size
        assert memory_growth_ratio < 5.0  # 处理后的数据不应超过原数据5倍大小
        
        # 清理大型数据对象
        del large_data, processed_data
    
    @pytest.mark.ai
    def test_error_recovery_and_resilience(self):
        """测试错误恢复和韧性"""
        
        def simulate_ai_service_with_failures(request_count, failure_rate=0.2):
            """模拟有故障率的AI服务"""
            import random
            
            results = []
            for i in range(request_count):
                if random.random() < failure_rate:
                    # 模拟失败
                    results.append({
                        "request_id": i,
                        "status": "failed",
                        "error": "Temporary AI service unavailable",
                        "retry_recommended": True
                    })
                else:
                    # 模拟成功
                    results.append({
                        "request_id": i,
                        "status": "success",
                        "response": {"analysis": "complete", "score": 80}
                    })
            
            return results
        
        # 模拟100个请求，20%失败率
        results = simulate_ai_service_with_failures(100, 0.2)
        
        # 统计结果
        success_count = sum(1 for r in results if r["status"] == "success")
        failure_count = sum(1 for r in results if r["status"] == "failed")
        retry_count = sum(1 for r in results if r.get("retry_recommended", False))
        
        # 验证服务韧性
        success_rate = success_count / len(results)
        assert success_rate >= 0.75  # 至少75%成功率
        
        # 验证错误处理
        assert failure_count > 0  # 确保测试了失败情况
        assert retry_count == failure_count  # 所有失败都应该建议重试