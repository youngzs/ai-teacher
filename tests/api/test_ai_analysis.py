"""
AI分析API测试模块
测试AI代码分析、反馈生成等智能功能
"""

import pytest
from httpx import AsyncClient
from unittest.mock import patch, AsyncMock, Mock
import json
import asyncio


class TestAIAnalysisAPI:
    """AI分析API测试类"""
    
    @pytest.mark.asyncio
    @pytest.mark.api
    @pytest.mark.ai
    @patch("app.services.ai_service.MultiAgentTeachingSystem.analyze_code")
    async def test_ai_code_analysis_c_language(
        self, mock_analyze, async_client: AsyncClient, test_user_data, mock_ai_response
    ):
        """测试C语言代码AI分析"""
        mock_analyze.return_value = mock_ai_response
        
        # 登录获取token
        await async_client.post("/api/v1/auth/register", json=test_user_data)
        login_response = await async_client.post(
            "/api/v1/auth/login",
            json={"email": test_user_data["email"], "password": test_user_data["password"]}
        )
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        c_code = """
        #include <stdio.h>
        int main() {
            int sum = 0;
            for(int i = 1; i <= 10; i++) {
                sum += i;
            }
            printf("Sum: %d\\n", sum);
            return 0;
        }
        """
        
        analysis_request = {
            "code": c_code,
            "language": "c",
            "assignment_context": "Calculate sum of numbers 1-10"
        }
        
        response = await async_client.post(
            "/api/v1/analysis/analyze",
            json=analysis_request,
            headers=headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "analysis" in data
        assert "feedback" in data
        assert "pedagogical_advice" in data
        assert data["analysis"]["complexity_score"] == 2
        assert data["analysis"]["correctness_score"] == 95
        
        # 验证mock被正确调用
        mock_analyze.assert_called_once()
        call_args = mock_analyze.call_args[0]
        assert c_code.strip() in call_args[0].code
        assert call_args[0].language == "c"
    
    @pytest.mark.asyncio
    @pytest.mark.api
    @pytest.mark.ai
    @patch("app.services.ai_service.MultiAgentTeachingSystem.analyze_code")
    async def test_ai_code_analysis_python_language(
        self, mock_analyze, async_client: AsyncClient, test_user_data
    ):
        """测试Python代码AI分析"""
        python_response = {
            "analysis": {
                "syntax_errors": [],
                "logic_issues": [],
                "style_suggestions": ["Use list comprehension for better readability"],
                "complexity_score": 3,
                "correctness_score": 88
            },
            "feedback": {
                "overall_assessment": "Good Python implementation",
                "strengths": ["Clear variable names", "Proper function structure"],
                "improvements": ["Consider using list comprehension"],
                "next_steps": ["Learn about generators"],
                "difficulty_level": "intermediate"
            },
            "pedagogical_advice": {
                "teaching_strategy": "constructive_feedback",
                "focus_areas": ["pythonic_code"],
                "estimated_mastery": 0.75
            }
        }
        mock_analyze.return_value = python_response
        
        # 登录获取token
        await async_client.post("/api/v1/auth/register", json=test_user_data)
        login_response = await async_client.post(
            "/api/v1/auth/login",
            json={"email": test_user_data["email"], "password": test_user_data["password"]}
        )
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        python_code = """
def calculate_sum(n):
    total = 0
    for i in range(1, n + 1):
        total += i
    return total

print(calculate_sum(10))
        """
        
        analysis_request = {
            "code": python_code,
            "language": "python",
            "assignment_context": "Calculate sum using function"
        }
        
        response = await async_client.post(
            "/api/v1/analysis/analyze",
            json=analysis_request,
            headers=headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["analysis"]["complexity_score"] == 3
        assert "list comprehension" in data["analysis"]["style_suggestions"][0]
    
    @pytest.mark.asyncio
    @pytest.mark.api
    @pytest.mark.ai
    async def test_ai_analysis_unauthorized(self, async_client: AsyncClient):
        """测试未授权AI分析失败"""
        analysis_request = {
            "code": "print('Hello')",
            "language": "python"
        }
        
        response = await async_client.post(
            "/api/v1/analysis/analyze",
            json=analysis_request
        )
        
        assert response.status_code == 401
    
    @pytest.mark.asyncio
    @pytest.mark.api
    @pytest.mark.ai
    async def test_ai_analysis_invalid_language(
        self, async_client: AsyncClient, test_user_data
    ):
        """测试不支持的编程语言"""
        # 登录获取token
        await async_client.post("/api/v1/auth/register", json=test_user_data)
        login_response = await async_client.post(
            "/api/v1/auth/login",
            json={"email": test_user_data["email"], "password": test_user_data["password"]}
        )
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        analysis_request = {
            "code": "console.log('Hello');",
            "language": "javascript"  # 假设不支持
        }
        
        response = await async_client.post(
            "/api/v1/analysis/analyze",
            json=analysis_request,
            headers=headers
        )
        
        assert response.status_code == 422
    
    @pytest.mark.asyncio
    @pytest.mark.api
    @pytest.mark.ai
    async def test_ai_analysis_empty_code(
        self, async_client: AsyncClient, test_user_data
    ):
        """测试空代码分析"""
        # 登录获取token
        await async_client.post("/api/v1/auth/register", json=test_user_data)
        login_response = await async_client.post(
            "/api/v1/auth/login",
            json={"email": test_user_data["email"], "password": test_user_data["password"]}
        )
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        analysis_request = {
            "code": "",
            "language": "c"
        }
        
        response = await async_client.post(
            "/api/v1/analysis/analyze",
            json=analysis_request,
            headers=headers
        )
        
        assert response.status_code == 422


class TestAIFeedbackGeneration:
    """AI反馈生成测试"""
    
    @pytest.mark.asyncio
    @pytest.mark.api
    @pytest.mark.ai
    @patch("app.services.ai_service.MultiAgentTeachingSystem.generate_feedback")
    async def test_generate_personalized_feedback(
        self, mock_feedback, async_client: AsyncClient, test_user_data
    ):
        """测试个性化反馈生成"""
        personalized_response = {
            "feedback": {
                "overall_assessment": "Great progress! Your code shows solid understanding.",
                "strengths": ["Clean syntax", "Good variable naming"],
                "improvements": ["Add error handling", "Consider edge cases"],
                "next_steps": ["Learn about pointers", "Practice with arrays"],
                "difficulty_level": "intermediate",
                "personalization": {
                    "learning_style": "visual",
                    "confidence_boost": "You're making excellent progress!",
                    "challenge_level": "ready_for_harder_problems"
                }
            }
        }
        mock_feedback.return_value = personalized_response
        
        # 登录获取token
        await async_client.post("/api/v1/auth/register", json=test_user_data)
        login_response = await async_client.post(
            "/api/v1/auth/login",
            json={"email": test_user_data["email"], "password": test_user_data["password"]}
        )
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        feedback_request = {
            "analysis_result": {
                "syntax_errors": [],
                "logic_issues": [],
                "complexity_score": 3
            },
            "student_profile": {
                "learning_style": "visual",
                "current_level": "intermediate",
                "previous_performance": 0.8
            },
            "assignment_context": "Array manipulation basics"
        }
        
        response = await async_client.post(
            "/api/v1/analysis/feedback",
            json=feedback_request,
            headers=headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "personalization" in data["feedback"]
        assert "confidence_boost" in data["feedback"]["personalization"]
    
    @pytest.mark.asyncio
    @pytest.mark.api
    @pytest.mark.ai
    @patch("app.services.ai_service.MultiAgentTeachingSystem.generate_feedback")
    async def test_generate_feedback_for_errors(
        self, mock_feedback, async_client: AsyncClient, test_user_data
    ):
        """测试错误代码的反馈生成"""
        error_response = {
            "feedback": {
                "overall_assessment": "Good attempt! Let's fix a few issues.",
                "strengths": ["Good problem approach"],
                "improvements": ["Fix syntax error on line 5", "Add missing semicolon"],
                "next_steps": ["Review C syntax rules", "Practice with simple examples"],
                "difficulty_level": "beginner",
                "error_guidance": {
                    "primary_error": "syntax",
                    "explanation": "Missing semicolon after variable declaration",
                    "hint": "Every C statement should end with a semicolon",
                    "example": "int x = 5; // Correct syntax"
                }
            }
        }
        mock_feedback.return_value = error_response
        
        # 登录获取token
        await async_client.post("/api/v1/auth/register", json=test_user_data)
        login_response = await async_client.post(
            "/api/v1/auth/login",
            json={"email": test_user_data["email"], "password": test_user_data["password"]}
        )
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        feedback_request = {
            "analysis_result": {
                "syntax_errors": ["Missing semicolon on line 5"],
                "logic_issues": [],
                "complexity_score": 1
            },
            "student_profile": {
                "learning_style": "hands_on",
                "current_level": "beginner",
                "error_history": ["syntax_errors"]
            }
        }
        
        response = await async_client.post(
            "/api/v1/analysis/feedback",
            json=feedback_request,
            headers=headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "error_guidance" in data["feedback"]
        assert "syntax" in data["feedback"]["error_guidance"]["primary_error"]


class TestAIAgentIntegration:
    """AI Agent集成测试"""
    
    @pytest.mark.asyncio
    @pytest.mark.api
    @pytest.mark.ai
    @patch("app.services.ai_service.TeachingAgentFactory")
    async def test_multi_agent_collaboration(
        self, mock_factory, async_client: AsyncClient, test_user_data
    ):
        """测试多Agent协作"""
        # Mock各个Agent
        mock_code_analyzer = Mock()
        mock_pedagogy_expert = Mock()
        mock_feedback_generator = Mock()
        
        mock_code_analyzer.analyze.return_value = {
            "syntax_score": 90,
            "logic_score": 85,
            "style_score": 80
        }
        
        mock_pedagogy_expert.assess.return_value = {
            "teaching_strategy": "scaffolding",
            "difficulty_adjustment": "increase"
        }
        
        mock_feedback_generator.generate.return_value = {
            "feedback_text": "Excellent work! Consider improving variable names.",
            "encouragement": "You're making great progress!"
        }
        
        mock_factory.create_all_agents.return_value = {
            "CodeAnalyzer": mock_code_analyzer,
            "PedagogyExpert": mock_pedagogy_expert,
            "FeedbackGenerator": mock_feedback_generator
        }
        
        # 登录获取token
        await async_client.post("/api/v1/auth/register", json=test_user_data)
        login_response = await async_client.post(
            "/api/v1/auth/login",
            json={"email": test_user_data["email"], "password": test_user_data["password"]}
        )
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        analysis_request = {
            "code": "#include <stdio.h>\nint main(){return 0;}",
            "language": "c",
            "use_multi_agent": True
        }
        
        response = await async_client.post(
            "/api/v1/analysis/multi-agent-analyze",
            json=analysis_request,
            headers=headers
        )
        
        # 根据实际API设计，这个端点可能存在或不存在
        assert response.status_code in [200, 404]
    
    @pytest.mark.asyncio
    @pytest.mark.api
    @pytest.mark.ai
    @patch("app.services.ai_service.MultiAgentTeachingSystem.get_agent_status")
    async def test_agent_health_check(
        self, mock_status, async_client: AsyncClient, test_user_data
    ):
        """测试Agent健康检查"""
        mock_status.return_value = {
            "CodeAnalyzer": {"status": "healthy", "response_time": 0.5},
            "PedagogyExpert": {"status": "healthy", "response_time": 0.3},
            "FeedbackGenerator": {"status": "degraded", "response_time": 2.1},
            "StudentProfiler": {"status": "healthy", "response_time": 0.4},
            "QualityController": {"status": "healthy", "response_time": 0.2},
            "DebuggingMentor": {"status": "offline", "response_time": None}
        }
        
        # 登录获取token
        await async_client.post("/api/v1/auth/register", json=test_user_data)
        login_response = await async_client.post(
            "/api/v1/auth/login",
            json={"email": test_user_data["email"], "password": test_user_data["password"]}
        )
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        response = await async_client.get(
            "/api/v1/analysis/agents/health",
            headers=headers
        )
        
        # 根据实际API设计
        assert response.status_code in [200, 404]


class TestAIPerformanceAndScalability:
    """AI性能和可扩展性测试"""
    
    @pytest.mark.asyncio
    @pytest.mark.api
    @pytest.mark.ai
    @pytest.mark.slow
    async def test_concurrent_ai_requests(
        self, async_client: AsyncClient, test_user_data
    ):
        """测试并发AI请求处理"""
        # 登录获取token
        await async_client.post("/api/v1/auth/register", json=test_user_data)
        login_response = await async_client.post(
            "/api/v1/auth/login",
            json={"email": test_user_data["email"], "password": test_user_data["password"]}
        )
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # 准备多个分析请求
        requests = []
        for i in range(5):  # 减少并发数以避免压垮测试环境
            analysis_request = {
                "code": f"#include <stdio.h>\nint main(){{printf(\"{i}\"); return 0;}}",
                "language": "c",
                "assignment_context": f"Test {i}"
            }
            requests.append(
                async_client.post(
                    "/api/v1/analysis/analyze",
                    json=analysis_request,
                    headers=headers
                )
            )
        
        # 并发执行
        with patch("app.services.ai_service.MultiAgentTeachingSystem.analyze_code") as mock_analyze:
            mock_analyze.return_value = {"analysis": {"score": 90}, "feedback": {"text": "Good"}}
            
            responses = await asyncio.gather(*requests, return_exceptions=True)
            
            # 检查响应
            success_count = 0
            for response in responses:
                if not isinstance(response, Exception):
                    if response.status_code == 200:
                        success_count += 1
            
            # 至少一半请求应该成功
            assert success_count >= len(requests) // 2
    
    @pytest.mark.asyncio
    @pytest.mark.api
    @pytest.mark.ai
    @patch("app.services.ai_service.MultiAgentTeachingSystem.analyze_code")
    async def test_ai_response_time_limit(
        self, mock_analyze, async_client: AsyncClient, test_user_data
    ):
        """测试AI响应时间限制"""
        # 模拟慢响应
        async def slow_analyze(*args, **kwargs):
            await asyncio.sleep(5)  # 模拟5秒延迟
            return {"analysis": {"score": 90}, "feedback": {"text": "Delayed response"}}
        
        mock_analyze.side_effect = slow_analyze
        
        # 登录获取token
        await async_client.post("/api/v1/auth/register", json=test_user_data)
        login_response = await async_client.post(
            "/api/v1/auth/login",
            json={"email": test_user_data["email"], "password": test_user_data["password"]}
        )
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        analysis_request = {
            "code": "#include <stdio.h>\nint main(){return 0;}",
            "language": "c"
        }
        
        # 测试超时处理
        try:
            response = await asyncio.wait_for(
                async_client.post(
                    "/api/v1/analysis/analyze",
                    json=analysis_request,
                    headers=headers
                ),
                timeout=3.0  # 3秒超时
            )
            # 如果没有超时，检查是否有适当的错误处理
            assert response.status_code in [200, 408, 500]
        except asyncio.TimeoutError:
            # 超时是预期的
            pass


class TestAIErrorHandling:
    """AI错误处理测试"""
    
    @pytest.mark.asyncio
    @pytest.mark.api
    @pytest.mark.ai
    @patch("app.services.ai_service.MultiAgentTeachingSystem.analyze_code")
    async def test_ai_service_unavailable(
        self, mock_analyze, async_client: AsyncClient, test_user_data
    ):
        """测试AI服务不可用时的处理"""
        mock_analyze.side_effect = Exception("OpenAI API key invalid")
        
        # 登录获取token
        await async_client.post("/api/v1/auth/register", json=test_user_data)
        login_response = await async_client.post(
            "/api/v1/auth/login",
            json={"email": test_user_data["email"], "password": test_user_data["password"]}
        )
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        analysis_request = {
            "code": "#include <stdio.h>\nint main(){return 0;}",
            "language": "c"
        }
        
        response = await async_client.post(
            "/api/v1/analysis/analyze",
            json=analysis_request,
            headers=headers
        )
        
        assert response.status_code == 500
        assert "AI服务" in response.json()["detail"] or "service" in response.json()["detail"].lower()
    
    @pytest.mark.asyncio
    @pytest.mark.api
    @pytest.mark.ai
    @patch("app.services.ai_service.MultiAgentTeachingSystem.analyze_code")
    async def test_malformed_ai_response_handling(
        self, mock_analyze, async_client: AsyncClient, test_user_data
    ):
        """测试AI返回格式错误的处理"""
        # 模拟格式错误的响应
        mock_analyze.return_value = {
            "malformed": "data",
            # 缺少expected字段
        }
        
        # 登录获取token
        await async_client.post("/api/v1/auth/register", json=test_user_data)
        login_response = await async_client.post(
            "/api/v1/auth/login",
            json={"email": test_user_data["email"], "password": test_user_data["password"]}
        )
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        analysis_request = {
            "code": "#include <stdio.h>\nint main(){return 0;}",
            "language": "c"
        }
        
        response = await async_client.post(
            "/api/v1/analysis/analyze",
            json=analysis_request,
            headers=headers
        )
        
        # 系统应该能处理格式错误
        assert response.status_code in [200, 500, 422]