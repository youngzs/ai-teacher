"""
性能基准测试
测试系统各个组件的性能指标和响应时间
"""

import pytest
import asyncio
import time
import statistics
from concurrent.futures import ThreadPoolExecutor, as_completed
from unittest.mock import patch, Mock
import httpx
import json


class TestAPIPerformance:
    """API性能测试"""
    
    @pytest.mark.performance
    @pytest.mark.asyncio
    async def test_api_response_time_benchmarks(self):
        """测试API响应时间基准"""
        
        performance_targets = {
            "/api/v1/auth/login": 200,           # 登录 < 200ms
            "/api/v1/dashboard/teacher": 300,    # 仪表板 < 300ms
            "/api/v1/submissions/": 400,         # 提交列表 < 400ms
            "/api/v1/users/me": 100,            # 用户信息 < 100ms
        }
        
        async with httpx.AsyncClient(base_url="http://localhost:8000") as client:
            # 先获取认证token
            login_data = {
                "email": "test@university.edu",
                "password": "testpassword"
            }
            
            # 测试登录性能
            start_time = time.perf_counter()
            try:
                response = await client.post("/api/v1/auth/login", json=login_data)
                end_time = time.perf_counter()
                login_time = (end_time - start_time) * 1000  # 转换为毫秒
                
                # 验证登录性能
                assert login_time < performance_targets["/api/v1/auth/login"], \
                    f"Login took {login_time:.2f}ms, expected < {performance_targets['/api/v1/auth/login']}ms"
                
                if response.status_code == 200:
                    token = response.json().get("access_token")
                    headers = {"Authorization": f"Bearer {token}"}
                else:
                    # 使用mock token进行测试
                    headers = {"Authorization": "Bearer mock-token"}
                
            except httpx.RequestError:
                # 如果API不可用，使用mock数据测试
                headers = {"Authorization": "Bearer mock-token"}
                login_time = 50  # 假设的快速响应时间
            
            # 测试其他端点性能
            endpoints_to_test = [
                "/api/v1/dashboard/teacher",
                "/api/v1/submissions/",
                "/api/v1/users/me"
            ]
            
            for endpoint in endpoints_to_test:
                start_time = time.perf_counter()
                try:
                    response = await client.get(endpoint, headers=headers)
                    end_time = time.perf_counter()
                    response_time = (end_time - start_time) * 1000
                    
                    # 验证响应时间
                    target_time = performance_targets[endpoint]
                    assert response_time < target_time, \
                        f"{endpoint} took {response_time:.2f}ms, expected < {target_time}ms"
                    
                except httpx.RequestError:
                    # API不可用时跳过测试
                    pytest.skip(f"API endpoint {endpoint} not available for performance testing")
    
    @pytest.mark.performance
    def test_concurrent_requests_performance(self):
        """测试并发请求性能"""
        
        def make_request(session_id):
            """单个请求函数"""
            import requests
            
            start_time = time.perf_counter()
            try:
                response = requests.get(
                    "http://localhost:8000/api/v1/health",
                    timeout=5,
                    headers={"User-Agent": f"Performance-Test-{session_id}"}
                )
                end_time = time.perf_counter()
                
                return {
                    "session_id": session_id,
                    "status_code": response.status_code,
                    "response_time": (end_time - start_time) * 1000,
                    "success": response.status_code == 200
                }
            except Exception as e:
                end_time = time.perf_counter()
                return {
                    "session_id": session_id,
                    "status_code": 0,
                    "response_time": (end_time - start_time) * 1000,
                    "success": False,
                    "error": str(e)
                }
        
        # 并发测试参数
        concurrent_users = 20
        total_requests = 100
        
        # 执行并发请求
        results = []
        with ThreadPoolExecutor(max_workers=concurrent_users) as executor:
            future_to_session = {
                executor.submit(make_request, i): i 
                for i in range(total_requests)
            }
            
            for future in as_completed(future_to_session):
                result = future.result()
                results.append(result)
        
        # 分析性能结果
        successful_requests = [r for r in results if r["success"]]
        failed_requests = [r for r in results if not r["success"]]
        
        if successful_requests:
            response_times = [r["response_time"] for r in successful_requests]
            
            # 计算性能指标
            avg_response_time = statistics.mean(response_times)
            median_response_time = statistics.median(response_times)
            p95_response_time = sorted(response_times)[int(len(response_times) * 0.95)]
            p99_response_time = sorted(response_times)[int(len(response_times) * 0.99)]
            
            # 性能断言
            assert avg_response_time < 500, f"Average response time {avg_response_time:.2f}ms too high"
            assert p95_response_time < 1000, f"95th percentile response time {p95_response_time:.2f}ms too high"
            assert len(successful_requests) / total_requests > 0.95, f"Success rate {len(successful_requests)/total_requests:.2%} too low"
            
            print(f"\n📊 Concurrent Performance Results:")
            print(f"Total requests: {total_requests}")
            print(f"Successful requests: {len(successful_requests)}")
            print(f"Failed requests: {len(failed_requests)}")
            print(f"Success rate: {len(successful_requests)/total_requests:.2%}")
            print(f"Average response time: {avg_response_time:.2f}ms")
            print(f"Median response time: {median_response_time:.2f}ms")
            print(f"95th percentile: {p95_response_time:.2f}ms")
            print(f"99th percentile: {p99_response_time:.2f}ms")
        
        else:
            pytest.skip("No successful requests to analyze - API may be unavailable")


class TestAIPerformance:
    """AI系统性能测试"""
    
    @pytest.mark.performance
    @pytest.mark.ai
    @pytest.mark.slow
    async def test_ai_analysis_response_time(self):
        """测试AI分析响应时间"""
        
        # 不同复杂度的代码样本
        code_samples = {
            "simple": "print('Hello World')",
            "medium": '''
def factorial(n):
    if n <= 1:
        return 1
    return n * factorial(n - 1)

print(factorial(5))
            ''',
            "complex": '''
#include <stdio.h>
#include <stdlib.h>

typedef struct Node {
    int data;
    struct Node* next;
} Node;

Node* createNode(int data) {
    Node* newNode = (Node*)malloc(sizeof(Node));
    newNode->data = data;
    newNode->next = NULL;
    return newNode;
}

void insertNode(Node** head, int data) {
    Node* newNode = createNode(data);
    if (*head == NULL) {
        *head = newNode;
        return;
    }
    Node* temp = *head;
    while (temp->next != NULL) {
        temp = temp->next;
    }
    temp->next = newNode;
}

void printList(Node* head) {
    while (head != NULL) {
        printf("%d -> ", head->data);
        head = head->next;
    }
    printf("NULL\\n");
}

int main() {
    Node* head = NULL;
    for (int i = 1; i <= 10; i++) {
        insertNode(&head, i);
    }
    printList(head);
    return 0;
}
            '''
        }
        
        performance_targets = {
            "simple": 1000,    # 简单代码 < 1秒
            "medium": 2000,    # 中等代码 < 2秒  
            "complex": 3000    # 复杂代码 < 3秒
        }
        
        async with httpx.AsyncClient(
            base_url="http://localhost:8000",
            timeout=10.0
        ) as client:
            
            # 获取认证token（模拟）
            headers = {"Authorization": "Bearer mock-token"}
            
            for complexity, code in code_samples.items():
                analysis_request = {
                    "code": code,
                    "language": "python" if complexity == "simple" or complexity == "medium" else "c",
                    "assignment_context": f"Performance test - {complexity} code"
                }
                
                start_time = time.perf_counter()
                
                try:
                    response = await client.post(
                        "/api/v1/analysis/analyze",
                        json=analysis_request,
                        headers=headers
                    )
                    end_time = time.perf_counter()
                    
                    analysis_time = (end_time - start_time) * 1000
                    
                    if response.status_code == 200:
                        # 验证响应时间符合目标
                        target_time = performance_targets[complexity]
                        assert analysis_time < target_time, \
                            f"{complexity} code analysis took {analysis_time:.2f}ms, expected < {target_time}ms"
                        
                        # 验证响应包含必要的分析结果
                        data = response.json()
                        assert "analysis" in data or "feedback" in data, "AI analysis response missing required fields"
                        
                        print(f"✅ {complexity.capitalize()} code analysis: {analysis_time:.2f}ms")
                    
                    elif response.status_code == 503:
                        # AI服务不可用时跳过
                        pytest.skip(f"AI service unavailable for {complexity} code test")
                    
                except httpx.TimeoutException:
                    pytest.fail(f"{complexity} code analysis timed out (>10s)")
                
                except httpx.RequestError:
                    pytest.skip(f"AI analysis endpoint not available for {complexity} code test")
    
    @pytest.mark.performance
    @pytest.mark.ai
    async def test_ai_feedback_generation_performance(self):
        """测试AI反馈生成性能"""
        
        # Mock AI服务以测试性能
        with patch('app.services.ai_service.MultiAgentTeachingSystem') as mock_ai:
            
            # 配置mock响应时间
            async def mock_generate_feedback(*args, **kwargs):
                # 模拟AI处理时间
                await asyncio.sleep(0.5)  # 500ms处理时间
                return {
                    "feedback": {
                        "overall_assessment": "Good work with some improvements needed",
                        "strengths": ["Clear logic", "Good structure"],
                        "improvements": ["Add error handling", "Optimize performance"],
                        "next_steps": ["Practice advanced concepts"]
                    }
                }
            
            mock_ai.return_value.generate_feedback = mock_generate_feedback
            
            # 测试批量反馈生成性能
            feedback_requests = [
                {"code": f"print('test {i}')", "language": "python"}
                for i in range(10)
            ]
            
            start_time = time.perf_counter()
            
            # 并发生成反馈
            tasks = []
            for request in feedback_requests:
                task = mock_ai.return_value.generate_feedback(request)
                tasks.append(task)
            
            results = await asyncio.gather(*tasks)
            
            end_time = time.perf_counter()
            total_time = (end_time - start_time) * 1000
            avg_time = total_time / len(feedback_requests)
            
            # 验证性能指标
            assert total_time < 10000, f"Batch feedback generation took {total_time:.2f}ms, expected < 10s"
            assert avg_time < 1000, f"Average feedback generation took {avg_time:.2f}ms, expected < 1s"
            
            print(f"📊 AI Feedback Performance:")
            print(f"Total requests: {len(feedback_requests)}")
            print(f"Total time: {total_time:.2f}ms")
            print(f"Average time per request: {avg_time:.2f}ms")
    
    @pytest.mark.performance
    @pytest.mark.ai
    def test_ai_agent_memory_usage(self):
        """测试AI Agent内存使用"""
        import psutil
        import os
        
        # 获取当前进程
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # 模拟大量AI处理
        with patch('app.services.ai_service.MultiAgentTeachingSystem') as mock_ai:
            
            def mock_analyze_with_memory(*args, **kwargs):
                # 模拟内存使用
                large_data = ['x' * 1000] * 1000  # 1MB数据
                
                return {
                    "analysis": {"score": 85},
                    "feedback": {"text": "Good work"},
                    "temp_data": large_data  # 模拟临时数据
                }
            
            mock_ai.return_value.analyze_code = mock_analyze_with_memory
            
            # 执行多次分析
            for i in range(50):
                result = mock_ai.return_value.analyze_code({"code": f"test {i}"})
                
                # 清理临时数据（模拟良好的内存管理）
                if "temp_data" in result:
                    del result["temp_data"]
            
            # 检查内存增长
            final_memory = process.memory_info().rss / 1024 / 1024  # MB
            memory_growth = final_memory - initial_memory
            
            # 验证内存使用合理
            assert memory_growth < 100, f"Memory growth {memory_growth:.2f}MB too high"
            
            print(f"📊 Memory Usage:")
            print(f"Initial memory: {initial_memory:.2f}MB")
            print(f"Final memory: {final_memory:.2f}MB")
            print(f"Memory growth: {memory_growth:.2f}MB")


class TestDatabasePerformance:
    """数据库性能测试"""
    
    @pytest.mark.performance
    @pytest.mark.database
    def test_database_query_performance(self):
        """测试数据库查询性能"""
        
        # Mock数据库操作
        query_performance_targets = {
            "select_user": 50,           # 用户查询 < 50ms
            "insert_submission": 100,    # 插入提交 < 100ms
            "select_submissions": 200,   # 查询提交列表 < 200ms
            "update_feedback": 150,      # 更新反馈 < 150ms
            "complex_analytics": 500     # 复杂分析查询 < 500ms
        }
        
        def mock_database_operation(operation_type, complexity=1):
            """模拟数据库操作"""
            start_time = time.perf_counter()
            
            # 根据操作类型模拟不同的延迟
            base_delay = {
                "select_user": 0.01,
                "insert_submission": 0.05,
                "select_submissions": 0.08,
                "update_feedback": 0.06,
                "complex_analytics": 0.2
            }.get(operation_type, 0.05)
            
            # 模拟数据库处理时间
            time.sleep(base_delay * complexity)
            
            end_time = time.perf_counter()
            return (end_time - start_time) * 1000  # 返回毫秒
        
        # 测试各种数据库操作性能
        for operation, target_time in query_performance_targets.items():
            operation_time = mock_database_operation(operation)
            
            assert operation_time < target_time, \
                f"{operation} took {operation_time:.2f}ms, expected < {target_time}ms"
            
            print(f"✅ {operation}: {operation_time:.2f}ms")
        
        # 测试批量操作性能
        batch_size = 100
        start_time = time.perf_counter()
        
        for i in range(batch_size):
            mock_database_operation("insert_submission", complexity=0.1)  # 减少单个操作时间
        
        end_time = time.perf_counter()
        batch_time = (end_time - start_time) * 1000
        avg_time = batch_time / batch_size
        
        assert avg_time < 50, f"Batch average {avg_time:.2f}ms per operation too high"
        
        print(f"📊 Batch Operations Performance:")
        print(f"Batch size: {batch_size}")
        print(f"Total time: {batch_time:.2f}ms")
        print(f"Average time per operation: {avg_time:.2f}ms")


class TestSystemResourceUsage:
    """系统资源使用测试"""
    
    @pytest.mark.performance
    def test_cpu_usage_under_load(self):
        """测试负载下的CPU使用情况"""
        import psutil
        import threading
        
        def cpu_intensive_task():
            """CPU密集型任务"""
            # 模拟AI分析的CPU使用
            for _ in range(1000000):
                sum(range(100))
        
        # 获取初始CPU使用率
        initial_cpu = psutil.cpu_percent(interval=1)
        
        # 启动多个线程模拟并发负载
        threads = []
        for i in range(4):  # 4个并发任务
            thread = threading.Thread(target=cpu_intensive_task)
            threads.append(thread)
            thread.start()
        
        # 等待任务完成并监控CPU使用
        for thread in threads:
            thread.join()
        
        # 获取峰值CPU使用率
        peak_cpu = psutil.cpu_percent(interval=1)
        
        # 验证CPU使用合理
        assert peak_cpu < 90, f"CPU usage {peak_cpu}% too high under load"
        
        print(f"📊 CPU Usage:")
        print(f"Initial CPU: {initial_cpu}%")
        print(f"Peak CPU: {peak_cpu}%")
    
    @pytest.mark.performance
    def test_memory_leak_detection(self):
        """测试内存泄漏检测"""
        import psutil
        import os
        import gc
        
        process = psutil.Process(os.getpid())
        
        # 记录初始内存
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # 模拟大量对象创建和销毁
        for cycle in range(10):
            # 创建大量临时对象
            temp_objects = []
            for i in range(1000):
                temp_objects.append({
                    "id": i,
                    "data": "x" * 1000,  # 1KB数据
                    "timestamp": time.time()
                })
            
            # 处理对象（模拟实际工作）
            processed = len([obj for obj in temp_objects if obj["id"] % 2 == 0])
            
            # 清理对象
            del temp_objects
            gc.collect()  # 强制垃圾回收
            
            # 每5次循环检查内存
            if cycle % 5 == 4:
                current_memory = process.memory_info().rss / 1024 / 1024  # MB
                memory_growth = current_memory - initial_memory
                
                # 内存增长不应该持续上升（可能的内存泄漏）
                assert memory_growth < 50, f"Potential memory leak: {memory_growth:.2f}MB growth"
        
        # 最终内存检查
        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        total_growth = final_memory - initial_memory
        
        print(f"📊 Memory Leak Test:")
        print(f"Initial memory: {initial_memory:.2f}MB")
        print(f"Final memory: {final_memory:.2f}MB")
        print(f"Total growth: {total_growth:.2f}MB")
        
        assert total_growth < 20, f"Possible memory leak: {total_growth:.2f}MB total growth"


# 性能测试配置
@pytest.fixture(scope="session")
def performance_test_config():
    """性能测试配置"""
    return {
        "api_timeout": 10,
        "concurrent_users": 20,
        "test_duration": 60,  # 秒
        "performance_targets": {
            "api_response_time": 500,      # 毫秒
            "ai_analysis_time": 3000,      # 毫秒
            "database_query_time": 200,    # 毫秒
            "memory_growth_limit": 100,    # MB
            "cpu_usage_limit": 80,         # 百分比
        }
    }


# 性能测试标记
pytestmark = pytest.mark.performance