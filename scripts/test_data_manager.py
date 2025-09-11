#!/usr/bin/env python3
"""
测试数据管理器
用于创建、清理和管理各种测试场景的数据
"""

import asyncio
import argparse
import json
import sys
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from faker import Faker
import random

# 添加项目路径
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

# 数据库相关
try:
    from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
    from sqlalchemy.orm import sessionmaker
    from app.database.session import Base, get_db
    from app.models import User, Submission, Assignment, Feedback
except ImportError:
    print("⚠️  Database models not available, using mock data")
    Base = None


class TestDataManager:
    """测试数据管理器"""
    
    def __init__(self, database_url: str = None):
        self.fake = Faker(['en_US', 'zh_CN'])
        self.database_url = database_url or os.getenv(
            "DATABASE_URL", 
            "sqlite+aiosqlite:///./test_data.db"
        )
        self.engine = None
        self.session_maker = None
        
        # 代码样本库
        self.code_samples = {
            "c": {
                "beginner": [
                    '''#include <stdio.h>
int main() {
    printf("Hello World\\n");
    return 0;
}''',
                    '''#include <stdio.h>
int main() {
    int n = 5;
    printf("Number: %d\\n", n);
    return 0;
}''',
                    '''#include <stdio.h>
int main() {
    int sum = 0;
    for(int i = 1; i <= 10; i++) {
        sum += i;
    }
    printf("Sum: %d\\n", sum);
    return 0;
}'''
                ],
                "intermediate": [
                    '''#include <stdio.h>
int factorial(int n) {
    if (n <= 1) return 1;
    return n * factorial(n - 1);
}
int main() {
    printf("5! = %d\\n", factorial(5));
    return 0;
}''',
                    '''#include <stdio.h>
#include <string.h>
int main() {
    char str[100];
    printf("Enter a string: ");
    fgets(str, sizeof(str), stdin);
    printf("Length: %lu\\n", strlen(str) - 1);
    return 0;
}''',
                    '''#include <stdio.h>
void bubbleSort(int arr[], int n) {
    for(int i = 0; i < n-1; i++) {
        for(int j = 0; j < n-i-1; j++) {
            if(arr[j] > arr[j+1]) {
                int temp = arr[j];
                arr[j] = arr[j+1];
                arr[j+1] = temp;
            }
        }
    }
}
int main() {
    int arr[] = {64, 34, 25, 12, 22, 11, 90};
    int n = 7;
    bubbleSort(arr, n);
    printf("Sorted array: ");
    for(int i = 0; i < n; i++) {
        printf("%d ", arr[i]);
    }
    return 0;
}'''
                ],
                "advanced": [
                    '''#include <stdio.h>
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

void printList(Node* head) {
    while(head) {
        printf("%d -> ", head->data);
        head = head->next;
    }
    printf("NULL\\n");
}

int main() {
    Node* head = createNode(1);
    head->next = createNode(2);
    head->next->next = createNode(3);
    printList(head);
    return 0;
}'''
                ]
            },
            "python": {
                "beginner": [
                    '''print("Hello World")''',
                    '''name = input("Enter your name: ")
print(f"Hello, {name}!")''',
                    '''numbers = [1, 2, 3, 4, 5]
total = sum(numbers)
print(f"Sum: {total}")'''
                ],
                "intermediate": [
                    '''def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)

for i in range(10):
    print(f"F({i}) = {fibonacci(i)}")''',
                    '''def factorial(n):
    if n <= 1:
        return 1
    return n * factorial(n-1)

print(f"5! = {factorial(5)}")''',
                    '''def bubble_sort(arr):
    n = len(arr)
    for i in range(n):
        for j in range(0, n-i-1):
            if arr[j] > arr[j+1]:
                arr[j], arr[j+1] = arr[j+1], arr[j]
    return arr

numbers = [64, 34, 25, 12, 22, 11, 90]
sorted_numbers = bubble_sort(numbers)
print("Sorted array:", sorted_numbers)'''
                ],
                "advanced": [
                    '''class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right

def inorder_traversal(root):
    if not root:
        return []
    
    return (inorder_traversal(root.left) + 
            [root.val] + 
            inorder_traversal(root.right))

# Create a sample tree
root = TreeNode(1)
root.right = TreeNode(2)
root.right.left = TreeNode(3)

print(inorder_traversal(root))''',
                    '''import heapq
from collections import defaultdict

def dijkstra(graph, start):
    distances = defaultdict(lambda: float('inf'))
    distances[start] = 0
    pq = [(0, start)]
    
    while pq:
        current_distance, current_node = heapq.heappop(pq)
        
        if current_distance > distances[current_node]:
            continue
            
        for neighbor, weight in graph[current_node].items():
            distance = current_distance + weight
            
            if distance < distances[neighbor]:
                distances[neighbor] = distance
                heapq.heappush(pq, (distance, neighbor))
    
    return dict(distances)

# Example usage
graph = {
    'A': {'B': 1, 'C': 4},
    'B': {'A': 1, 'C': 2, 'D': 5},
    'C': {'A': 4, 'B': 2, 'D': 1},
    'D': {'B': 5, 'C': 1}
}

print(dijkstra(graph, 'A'))'''
                ]
            }
        }
        
        # 常见错误代码模板
        self.buggy_code_samples = {
            "c": [
                '''#include <stdio.h>
int main() {
    int n = 5;
    for(int i = 0; i <= n; i++) {  // Off-by-one error
        printf("%d ", i);
    }
    return 0;
}''',
                '''#include <stdio.h>
int main() {
    int x;  // Uninitialized variable
    printf("Value: %d\\n", x);
    return 0;
}''',
                '''#include <stdio.h>
int factorial(int n) {
    return n * factorial(n - 1);  // Missing base case
}
int main() {
    printf("%d\\n", factorial(5));
    return 0;
}'''
            ],
            "python": [
                '''def divide(a, b):
    return a / b  # No zero division check

print(divide(10, 0))''',
                '''numbers = [1, 2, 3]
for i in range(4):  # Index out of range
    print(numbers[i])''',
                '''def factorial(n):
    if n == 0:
        return 1
    return n * factorial(n - 1)  # Missing case for n < 0

print(factorial(-5))  # Infinite recursion'''
            ]
        }
    
    async def initialize_database(self):
        """初始化数据库连接"""
        try:
            from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
            
            self.engine = create_async_engine(
                self.database_url,
                echo=False,
                future=True
            )
            
            self.session_maker = async_sessionmaker(
                self.engine,
                expire_on_commit=False
            )
            
            # 创建表
            if Base:
                async with self.engine.begin() as conn:
                    await conn.run_sync(Base.metadata.create_all)
            
            print("✅ Database initialized successfully")
            return True
            
        except Exception as e:
            print(f"⚠️  Database initialization failed: {e}")
            return False
    
    async def create_test_users(self, count: int = 50) -> List[Dict]:
        """创建测试用户"""
        users = []
        
        # 创建教师用户 (20%)
        teacher_count = max(1, count // 5)
        for i in range(teacher_count):
            user = {
                "id": f"teacher_{i+1}",
                "email": f"teacher_{i+1}@university.edu",
                "password": "TestPassword123!",
                "full_name": self.fake.name(),
                "role": "teacher",
                "university": self.fake.company() + " University",
                "department": random.choice([
                    "Computer Science", "Information Technology", 
                    "Software Engineering", "Data Science"
                ]),
                "created_at": self.fake.date_time_between(start_date='-1y', end_date='now'),
                "is_active": True
            }
            users.append(user)
        
        # 创建学生用户 (80%)
        student_count = count - teacher_count
        for i in range(student_count):
            user = {
                "id": f"student_{i+1}",
                "email": f"student_{i+1}@university.edu", 
                "password": "TestPassword123!",
                "full_name": self.fake.name(),
                "role": "student",
                "university": self.fake.company() + " University",
                "department": random.choice([
                    "Computer Science", "Information Technology",
                    "Software Engineering", "Data Science"
                ]),
                "student_id": f"CS{2024}{i+1:04d}",
                "year": random.randint(1, 4),
                "created_at": self.fake.date_time_between(start_date='-1y', end_date='now'),
                "is_active": True
            }
            users.append(user)
        
        print(f"✅ Created {len(users)} test users ({teacher_count} teachers, {student_count} students)")
        return users
    
    async def create_test_assignments(self, teacher_count: int = 10) -> List[Dict]:
        """创建测试作业"""
        assignments = []
        
        assignment_templates = [
            {
                "title": "Hello World Program",
                "description": "Write a simple program that prints 'Hello World' to the console.",
                "language": "c",
                "difficulty": "beginner",
                "points": 10
            },
            {
                "title": "Factorial Calculator", 
                "description": "Implement a function to calculate the factorial of a number.",
                "language": "c",
                "difficulty": "intermediate",
                "points": 25
            },
            {
                "title": "Bubble Sort Implementation",
                "description": "Implement the bubble sort algorithm to sort an array of integers.",
                "language": "c", 
                "difficulty": "intermediate",
                "points": 30
            },
            {
                "title": "Linked List Operations",
                "description": "Implement basic linked list operations (insert, delete, search).",
                "language": "c",
                "difficulty": "advanced",
                "points": 50
            },
            {
                "title": "Python Basics",
                "description": "Complete basic Python programming exercises.",
                "language": "python",
                "difficulty": "beginner", 
                "points": 15
            },
            {
                "title": "Data Structures in Python",
                "description": "Implement various data structures in Python.",
                "language": "python",
                "difficulty": "advanced",
                "points": 45
            }
        ]
        
        for i, template in enumerate(assignment_templates):
            assignment = {
                "id": f"assignment_{i+1}",
                "title": template["title"],
                "description": template["description"],
                "language": template["language"],
                "difficulty": template["difficulty"],
                "points": template["points"],
                "max_attempts": random.randint(3, 10),
                "due_date": (datetime.now() + timedelta(days=random.randint(7, 30))).isoformat(),
                "created_at": self.fake.date_time_between(start_date='-3m', end_date='now').isoformat(),
                "created_by": f"teacher_{random.randint(1, min(teacher_count, 10))}",
                "is_published": True,
                "test_cases": [
                    {
                        "input": "sample input",
                        "expected_output": "sample output",
                        "description": "Basic test case"
                    }
                ]
            }
            assignments.append(assignment)
        
        print(f"✅ Created {len(assignments)} test assignments")
        return assignments
    
    async def create_test_submissions(
        self, 
        student_count: int = 40, 
        assignment_count: int = 6,
        submissions_per_student: int = 3
    ) -> List[Dict]:
        """创建测试提交"""
        submissions = []
        
        for student_id in range(1, student_count + 1):
            # 每个学生提交部分作业
            assignments_to_submit = random.sample(
                range(1, assignment_count + 1), 
                random.randint(2, min(assignment_count, submissions_per_student))
            )
            
            for assignment_id in assignments_to_submit:
                # 每个作业可能有多次提交
                attempt_count = random.randint(1, 3)
                
                for attempt in range(attempt_count):
                    # 选择代码质量级别
                    if attempt == 0:
                        # 第一次提交通常质量较低
                        quality_level = random.choice(["beginner", "beginner", "intermediate"])
                        use_buggy = random.random() < 0.3  # 30%概率有bug
                    else:
                        # 后续提交质量提高
                        quality_level = random.choice(["intermediate", "intermediate", "advanced"])
                        use_buggy = random.random() < 0.1  # 10%概率有bug
                    
                    # 选择编程语言
                    language = random.choice(["c", "python"])
                    
                    # 选择代码
                    if use_buggy:
                        code = random.choice(self.buggy_code_samples[language])
                        expected_score = random.randint(30, 60)
                    else:
                        code = random.choice(self.code_samples[language][quality_level])
                        expected_score = {
                            "beginner": random.randint(60, 80),
                            "intermediate": random.randint(75, 90),
                            "advanced": random.randint(85, 100)
                        }[quality_level]
                    
                    submission = {
                        "id": f"submission_{len(submissions) + 1}",
                        "student_id": f"student_{student_id}",
                        "assignment_id": f"assignment_{assignment_id}",
                        "code": code,
                        "language": language,
                        "attempt_number": attempt + 1,
                        "status": random.choice(["pending", "completed", "completed", "completed"]),
                        "score": expected_score if random.random() > 0.1 else None,  # 90%已评分
                        "submitted_at": self.fake.date_time_between(
                            start_date='-2m', 
                            end_date='now'
                        ).isoformat(),
                        "ai_analysis": {
                            "syntax_errors": [] if not use_buggy else ["Syntax error on line X"],
                            "logic_issues": [] if not use_buggy else ["Potential logic error"],
                            "style_suggestions": [
                                "Add comments for better readability",
                                "Consider using more descriptive variable names"
                            ],
                            "complexity_score": random.randint(1, 5),
                            "correctness_score": expected_score
                        } if random.random() > 0.1 else None
                    }
                    submissions.append(submission)
        
        print(f"✅ Created {len(submissions)} test submissions")
        return submissions
    
    async def create_test_feedback(self, submissions: List[Dict]) -> List[Dict]:
        """创建测试AI反馈"""
        feedback_list = []
        
        feedback_templates = {
            "positive": [
                "Excellent work! Your code demonstrates a clear understanding of the concepts.",
                "Great implementation! The logic is correct and the code is well-structured.",
                "Very good! Your solution is efficient and readable."
            ],
            "constructive": [
                "Good attempt! Consider adding error handling to make your code more robust.",
                "Nice work! Try to add comments to explain your logic for better readability.",
                "Good progress! Think about edge cases that your code should handle."
            ],
            "improvement_needed": [
                "You're on the right track! Review the algorithm and fix the logical errors.",
                "Good effort! Check your syntax carefully and test with different inputs.",
                "Keep trying! Focus on understanding the problem requirements first."
            ]
        }
        
        for submission in submissions:
            if submission.get("score"):
                score = submission["score"]
                
                # 确定反馈类型
                if score >= 85:
                    feedback_type = "positive"
                elif score >= 65:
                    feedback_type = "constructive"
                else:
                    feedback_type = "improvement_needed"
                
                feedback = {
                    "id": f"feedback_{len(feedback_list) + 1}",
                    "submission_id": submission["id"],
                    "overall_assessment": random.choice(feedback_templates[feedback_type]),
                    "strengths": self._generate_strengths(score),
                    "improvements": self._generate_improvements(score),
                    "next_steps": self._generate_next_steps(score),
                    "ai_generated": True,
                    "teacher_reviewed": random.random() < 0.3,  # 30%经过教师审核
                    "created_at": submission["submitted_at"],
                    "difficulty_level": submission.get("difficulty", "intermediate")
                }
                feedback_list.append(feedback)
        
        print(f"✅ Created {len(feedback_list)} test feedback entries")
        return feedback_list
    
    def _generate_strengths(self, score: int) -> List[str]:
        """根据分数生成优点"""
        all_strengths = [
            "Clear and readable code structure",
            "Correct algorithm implementation", 
            "Good variable naming conventions",
            "Proper use of control structures",
            "Efficient solution approach",
            "Good error handling",
            "Well-commented code",
            "Follows coding standards"
        ]
        
        # 高分获得更多优点
        strength_count = min(len(all_strengths), max(1, score // 20))
        return random.sample(all_strengths, strength_count)
    
    def _generate_improvements(self, score: int) -> List[str]:
        """根据分数生成改进建议"""
        all_improvements = [
            "Add input validation",
            "Include more detailed comments",
            "Handle edge cases better", 
            "Optimize algorithm efficiency",
            "Improve variable naming",
            "Add error handling",
            "Follow consistent indentation",
            "Consider boundary conditions"
        ]
        
        # 低分获得更多改进建议
        improvement_count = min(len(all_improvements), max(0, (100 - score) // 15))
        return random.sample(all_improvements, improvement_count) if improvement_count > 0 else []
    
    def _generate_next_steps(self, score: int) -> List[str]:
        """根据分数生成下一步建议"""
        if score >= 90:
            return [
                "Try implementing more complex algorithms",
                "Explore advanced data structures", 
                "Consider performance optimization techniques"
            ]
        elif score >= 75:
            return [
                "Practice with more challenging problems",
                "Focus on code optimization",
                "Learn about advanced programming concepts"
            ]
        else:
            return [
                "Review fundamental programming concepts",
                "Practice basic algorithm implementation",
                "Focus on understanding problem requirements"
            ]
    
    async def save_test_data(self, data: Dict[str, List], output_file: str = None):
        """保存测试数据到文件"""
        if output_file:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False, default=str)
            print(f"✅ Test data saved to {output_file}")
        else:
            # 保存到多个文件
            for data_type, items in data.items():
                filename = f"test_data_{data_type}.json"
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(items, f, indent=2, ensure_ascii=False, default=str)
                print(f"✅ {data_type} data saved to {filename}")
    
    async def load_test_data_to_database(self, data: Dict[str, List]):
        """将测试数据加载到数据库"""
        if not self.session_maker:
            print("❌ Database not initialized")
            return False
        
        try:
            async with self.session_maker() as session:
                # 这里需要根据实际的ORM模型来实现
                # 由于模型可能不存在，这里只是示例
                print("ℹ️  Database loading would be implemented here")
                print(f"- Users: {len(data.get('users', []))}")
                print(f"- Assignments: {len(data.get('assignments', []))}")
                print(f"- Submissions: {len(data.get('submissions', []))}")
                print(f"- Feedback: {len(data.get('feedback', []))}")
                
                await session.commit()
                
            return True
            
        except Exception as e:
            print(f"❌ Failed to load data to database: {e}")
            return False
    
    async def cleanup_test_data(self, prefix: str = "test_"):
        """清理测试数据"""
        if not self.session_maker:
            print("⚠️  Database not initialized, skipping cleanup")
            return
        
        try:
            async with self.session_maker() as session:
                # 清理逻辑需要根据实际模型实现
                print(f"🗑️  Cleaning up test data with prefix '{prefix}'")
                await session.commit()
                print("✅ Test data cleanup completed")
                
        except Exception as e:
            print(f"❌ Failed to cleanup test data: {e}")
    
    async def generate_performance_test_data(self, scale: str = "medium") -> Dict[str, List]:
        """生成性能测试数据"""
        scale_config = {
            "small": {"users": 20, "assignments": 5, "submissions_per_student": 2},
            "medium": {"users": 100, "assignments": 10, "submissions_per_student": 5},
            "large": {"users": 500, "assignments": 20, "submissions_per_student": 10},
            "xlarge": {"users": 1000, "assignments": 50, "submissions_per_student": 15}
        }
        
        config = scale_config.get(scale, scale_config["medium"])
        
        print(f"🚀 Generating {scale} scale performance test data...")
        
        users = await self.create_test_users(config["users"])
        assignments = await self.create_test_assignments(config["assignments"])
        submissions = await self.create_test_submissions(
            student_count=int(config["users"] * 0.8),  # 80% students
            assignment_count=config["assignments"],
            submissions_per_student=config["submissions_per_student"]
        )
        feedback = await self.create_test_feedback(submissions)
        
        return {
            "users": users,
            "assignments": assignments, 
            "submissions": submissions,
            "feedback": feedback
        }
    
    async def close(self):
        """关闭数据库连接"""
        if self.engine:
            await self.engine.dispose()


async def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="AI教学助手系统测试数据管理器")
    parser.add_argument("action", choices=["generate", "cleanup", "load"], help="操作类型")
    parser.add_argument("--scale", choices=["small", "medium", "large", "xlarge"], 
                       default="medium", help="数据规模")
    parser.add_argument("--output", help="输出文件路径")
    parser.add_argument("--database-url", help="数据库连接URL")
    parser.add_argument("--prefix", default="test_", help="测试数据前缀")
    
    args = parser.parse_args()
    
    # 创建数据管理器
    manager = TestDataManager(args.database_url)
    
    try:
        if args.action == "generate":
            print(f"🎯 Generating {args.scale} scale test data...")
            
            # 初始化数据库
            await manager.initialize_database()
            
            # 生成测试数据
            if args.scale in ["large", "xlarge"]:
                # 大规模数据用于性能测试
                data = await manager.generate_performance_test_data(args.scale)
            else:
                # 常规测试数据
                data = {
                    "users": await manager.create_test_users(50),
                    "assignments": await manager.create_test_assignments(10),
                    "submissions": await manager.create_test_submissions(40, 6, 3),
                }
                data["feedback"] = await manager.create_test_feedback(data["submissions"])
            
            # 保存数据
            await manager.save_test_data(data, args.output)
            
            # 如果有数据库，也加载到数据库
            if manager.session_maker:
                await manager.load_test_data_to_database(data)
            
            print("🎉 Test data generation completed!")
            
        elif args.action == "cleanup":
            print("🗑️  Cleaning up test data...")
            await manager.initialize_database()
            await manager.cleanup_test_data(args.prefix)
            print("✅ Cleanup completed!")
            
        elif args.action == "load":
            print("📥 Loading test data to database...")
            await manager.initialize_database()
            
            if args.output and os.path.exists(args.output):
                with open(args.output, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                await manager.load_test_data_to_database(data)
            else:
                print("❌ No data file specified or file not found")
            
            print("✅ Data loading completed!")
    
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)
    
    finally:
        await manager.close()


if __name__ == "__main__":
    asyncio.run(main())