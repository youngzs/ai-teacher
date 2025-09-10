"""
Locust负载测试配置
测试AI教学助手系统的并发负载能力
"""

from locust import HttpUser, task, between, events
import json
import random
import time
from datetime import datetime, timedelta


class TeacherUser(HttpUser):
    """模拟教师用户行为"""
    
    weight = 3  # 教师用户权重
    wait_time = between(5, 15)  # 操作间隔5-15秒
    
    def on_start(self):
        """用户开始时的设置"""
        self.login_as_teacher()
    
    def login_as_teacher(self):
        """教师登录"""
        login_data = {
            "email": f"teacher_{random.randint(1, 100)}@university.edu",
            "password": "TestPassword123!"
        }
        
        with self.client.post(
            "/api/v1/auth/login",
            json=login_data,
            catch_response=True,
            name="Teacher Login"
        ) as response:
            if response.status_code == 200:
                self.token = response.json().get("access_token")
                self.headers = {"Authorization": f"Bearer {self.token}"}
                response.success()
            else:
                response.failure(f"Login failed: {response.status_code}")
    
    @task(3)
    def view_dashboard(self):
        """查看教师仪表板"""
        with self.client.get(
            "/api/v1/dashboard/teacher",
            headers=self.headers,
            catch_response=True,
            name="Teacher Dashboard"
        ) as response:
            if response.status_code == 200:
                data = response.json()
                if "totalStudents" in data and "pendingReviews" in data:
                    response.success()
                else:
                    response.failure("Invalid dashboard data")
            else:
                response.failure(f"Dashboard load failed: {response.status_code}")
    
    @task(2)
    def view_submissions(self):
        """查看学生提交"""
        with self.client.get(
            "/api/v1/submissions/?page=1&size=20",
            headers=self.headers,
            catch_response=True,
            name="View Submissions"
        ) as response:
            if response.status_code == 200:
                data = response.json()
                if "items" in data:
                    response.success()
                else:
                    response.failure("Invalid submissions data")
            else:
                response.failure(f"Submissions load failed: {response.status_code}")
    
    @task(2)
    def review_submission(self):
        """审核学生提交（模拟）"""
        # 模拟审核一个提交
        submission_id = random.randint(1, 100)
        
        with self.client.get(
            f"/api/v1/submissions/{submission_id}",
            headers=self.headers,
            catch_response=True,
            name="Review Submission"
        ) as response:
            if response.status_code in [200, 404]:  # 404也算正常，因为是模拟数据
                response.success()
            else:
                response.failure(f"Review failed: {response.status_code}")
    
    @task(1)
    def create_assignment(self):
        """创建新作业"""
        assignment_data = {
            "title": f"Load Test Assignment {random.randint(1, 1000)}",
            "description": "This is a load testing assignment",
            "language": random.choice(["c", "python"]),
            "difficulty": random.choice(["beginner", "intermediate", "advanced"]),
            "due_date": (datetime.now() + timedelta(days=7)).isoformat(),
            "max_attempts": random.randint(1, 5),
            "points": random.randint(50, 100)
        }
        
        with self.client.post(
            "/api/v1/assignments/",
            json=assignment_data,
            headers=self.headers,
            catch_response=True,
            name="Create Assignment"
        ) as response:
            if response.status_code in [201, 200]:
                response.success()
            else:
                response.failure(f"Assignment creation failed: {response.status_code}")


class StudentUser(HttpUser):
    """模拟学生用户行为"""
    
    weight = 7  # 学生用户权重（学生比教师多）
    wait_time = between(10, 30)  # 学生思考时间更长
    
    def on_start(self):
        """用户开始时的设置"""
        self.login_as_student()
    
    def login_as_student(self):
        """学生登录"""
        login_data = {
            "email": f"student_{random.randint(1, 500)}@university.edu",
            "password": "TestPassword123!"
        }
        
        with self.client.post(
            "/api/v1/auth/login",
            json=login_data,
            catch_response=True,
            name="Student Login"
        ) as response:
            if response.status_code == 200:
                self.token = response.json().get("access_token")
                self.headers = {"Authorization": f"Bearer {self.token}"}
                response.success()
            else:
                response.failure(f"Login failed: {response.status_code}")
    
    @task(3)
    def view_dashboard(self):
        """查看学生仪表板"""
        with self.client.get(
            "/api/v1/dashboard/student",
            headers=self.headers,
            catch_response=True,
            name="Student Dashboard"
        ) as response:
            if response.status_code == 200:
                data = response.json()
                if "totalSubmissions" in data and "averageScore" in data:
                    response.success()
                else:
                    response.failure("Invalid dashboard data")
            else:
                response.failure(f"Dashboard load failed: {response.status_code}")
    
    @task(2)
    def view_assignments(self):
        """查看可用作业"""
        with self.client.get(
            "/api/v1/assignments/?status=published",
            headers=self.headers,
            catch_response=True,
            name="View Assignments"
        ) as response:
            if response.status_code == 200:
                data = response.json()
                if "items" in data:
                    response.success()
                else:
                    response.failure("Invalid assignments data")
            else:
                response.failure(f"Assignments load failed: {response.status_code}")
    
    @task(4)
    def submit_code(self):
        """提交代码（最重要的操作）"""
        code_samples = [
            '''#include <stdio.h>
int main() {
    printf("Hello World\\n");
    return 0;
}''',
            '''#include <stdio.h>
int factorial(int n) {
    if (n <= 1) return 1;
    return n * factorial(n - 1);
}
int main() {
    printf("%d", factorial(5));
    return 0;
}''',
            '''def hello():
    print("Hello World")

hello()''',
            '''def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)

print(fibonacci(10))'''
        ]
        
        submission_data = {
            "code": random.choice(code_samples),
            "language": random.choice(["c", "python"]),
            "assignment_id": f"assignment_{random.randint(1, 50)}"
        }
        
        with self.client.post(
            "/api/v1/submissions/",
            json=submission_data,
            headers=self.headers,
            catch_response=True,
            name="Submit Code"
        ) as response:
            if response.status_code in [201, 200]:
                self.last_submission_id = response.json().get("id")
                response.success()
            else:
                response.failure(f"Code submission failed: {response.status_code}")
    
    @task(3)
    def request_ai_analysis(self):
        """请求AI分析（高负载操作）"""
        if hasattr(self, 'last_submission_id') and self.last_submission_id:
            with self.client.post(
                f"/api/v1/submissions/{self.last_submission_id}/analyze",
                headers=self.headers,
                catch_response=True,
                name="AI Analysis Request"
            ) as response:
                if response.status_code == 200:
                    response.success()
                elif response.status_code == 202:  # 异步处理中
                    response.success()
                else:
                    response.failure(f"AI analysis failed: {response.status_code}")
    
    @task(1)
    def check_ai_feedback(self):
        """查看AI反馈"""
        if hasattr(self, 'last_submission_id') and self.last_submission_id:
            with self.client.get(
                f"/api/v1/submissions/{self.last_submission_id}/feedback",
                headers=self.headers,
                catch_response=True,
                name="Check AI Feedback"
            ) as response:
                if response.status_code in [200, 404]:  # 可能还在处理中
                    response.success()
                else:
                    response.failure(f"Feedback check failed: {response.status_code}")


class AIAnalysisStressTest(HttpUser):
    """专门测试AI分析系统的压力测试用户"""
    
    weight = 2
    wait_time = between(1, 5)  # 快速发送请求
    
    def on_start(self):
        self.login_as_student()
    
    def login_as_student(self):
        login_data = {
            "email": f"stress_test_user_{random.randint(1, 100)}@university.edu",
            "password": "TestPassword123!"
        }
        
        with self.client.post("/api/v1/auth/login", json=login_data) as response:
            if response.status_code == 200:
                self.token = response.json().get("access_token")
                self.headers = {"Authorization": f"Bearer {self.token}"}
    
    @task
    def stress_test_ai_analysis(self):
        """压力测试AI分析API"""
        stress_codes = [
            "int main() { return 0; }",
            "print('hello')",
            "#include <stdio.h>\nint main() { printf('test'); return 0; }",
            "def test(): pass",
            "for i in range(10): print(i)"
        ]
        
        analysis_request = {
            "code": random.choice(stress_codes),
            "language": random.choice(["c", "python"]),
            "assignment_context": "Stress test analysis"
        }
        
        with self.client.post(
            "/api/v1/analysis/analyze",
            json=analysis_request,
            headers=self.headers,
            catch_response=True,
            name="AI Analysis Stress Test"
        ) as response:
            if response.status_code == 200:
                response.success()
            elif response.status_code == 503:  # 服务暂时不可用
                response.success()  # 在压力测试中这是可以接受的
            else:
                response.failure(f"AI stress test failed: {response.status_code}")


# 全局事件处理器
@events.test_start.add_listener
def on_test_start(environment, **kwargs):
    """测试开始时的设置"""
    print("🚀 Starting AI Teaching Assistant Load Test")
    print(f"Target host: {environment.host}")
    print(f"Expected users: {environment.parsed_options.num_users if hasattr(environment, 'parsed_options') else 'N/A'}")


@events.test_stop.add_listener  
def on_test_stop(environment, **kwargs):
    """测试结束时的清理和报告"""
    print("🏁 Load test completed")
    
    # 获取统计信息
    stats = environment.stats
    
    print("\n📊 Test Summary:")
    print(f"Total requests: {stats.total.num_requests}")
    print(f"Failed requests: {stats.total.num_failures}")
    print(f"Average response time: {stats.total.avg_response_time:.2f}ms")
    print(f"Max response time: {stats.total.max_response_time:.2f}ms")
    print(f"Requests per second: {stats.total.current_rps:.2f}")
    
    # 检查是否达到性能目标
    performance_targets = {
        "avg_response_time": 2000,  # 平均响应时间 < 2秒
        "failure_rate": 0.05,       # 失败率 < 5%
        "ai_response_time": 3000    # AI分析响应时间 < 3秒
    }
    
    failure_rate = stats.total.num_failures / max(stats.total.num_requests, 1)
    
    print("\n🎯 Performance Target Analysis:")
    print(f"Average response time: {stats.total.avg_response_time:.2f}ms (target: <{performance_targets['avg_response_time']}ms) {'✅' if stats.total.avg_response_time < performance_targets['avg_response_time'] else '❌'}")
    print(f"Failure rate: {failure_rate:.2%} (target: <{performance_targets['failure_rate']:.1%}) {'✅' if failure_rate < performance_targets['failure_rate'] else '❌'}")
    
    # AI特定指标
    ai_stats = stats.entries.get(("POST", "/api/v1/analysis/analyze"))
    if ai_stats:
        print(f"AI analysis avg response: {ai_stats.avg_response_time:.2f}ms (target: <{performance_targets['ai_response_time']}ms) {'✅' if ai_stats.avg_response_time < performance_targets['ai_response_time'] else '❌'}")


# 负载测试场景配置
class LoadTestScenarios:
    """不同的负载测试场景"""
    
    @staticmethod
    def normal_usage():
        """正常使用场景"""
        return {
            "users": 50,
            "spawn_rate": 5,
            "run_time": "10m",
            "description": "模拟正常教学期间的用户负载"
        }
    
    @staticmethod
    def peak_submission_time():
        """作业提交高峰期场景"""
        return {
            "users": 200,
            "spawn_rate": 20,
            "run_time": "15m",
            "description": "模拟作业截止日期前的高峰负载"
        }
    
    @staticmethod
    def stress_test():
        """压力测试场景"""
        return {
            "users": 500,
            "spawn_rate": 50,
            "run_time": "20m",
            "description": "系统极限负载测试"
        }
    
    @staticmethod
    def ai_analysis_focused():
        """AI分析重点测试"""
        return {
            "users": 100,
            "spawn_rate": 10,
            "run_time": "15m",
            "description": "重点测试AI分析系统的负载能力",
            "user_classes": [AIAnalysisStressTest]
        }


# 使用说明:
# 1. 正常负载测试: locust -f locustfile.py --users 50 --spawn-rate 5 -t 10m --host http://localhost:8000
# 2. 高峰负载测试: locust -f locustfile.py --users 200 --spawn-rate 20 -t 15m --host http://localhost:8000
# 3. 压力测试: locust -f locustfile.py --users 500 --spawn-rate 50 -t 20m --host http://localhost:8000
# 4. Web UI模式: locust -f locustfile.py --host http://localhost:8000