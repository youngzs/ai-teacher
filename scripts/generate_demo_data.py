#!/usr/bin/env python3
"""
Demo Data Generator - Course Content Integration
生成课程演示数据，用于系统展示和测试

Author: Product Manager Coordinator
Date: 2025-09-12
"""

import sys
import os
import json
import uuid
from pathlib import Path
from typing import Dict, List, Any
from datetime import datetime, timezone

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.import_curriculum import CurriculumParser, ExerciseParser

def generate_demo_course_data() -> Dict[str, Any]:
    """生成演示课程数据"""
    
    # 使用解析器提取真实课程内容
    curriculum_file = Path("docs/education/c_language_detailed_curriculum.md")
    exercise_file = Path("docs/education/c_language_exercise_bank.md")
    
    demo_data = {
        "course": {},
        "lessons": [],
        "exercises": [],
        "learning_paths": [],
        "student_progress": []
    }
    
    if curriculum_file.exists():
        print("📚 解析课程内容...")
        curriculum_parser = CurriculumParser(curriculum_file)
        curriculum_parser.load_file()
        
        # 获取课程数据
        course_data = curriculum_parser.parse_course_info()
        lessons = curriculum_parser.parse_lessons()
        
        demo_data["course"] = course_data
        demo_data["lessons"] = lessons
        
        print(f"  - 课程: {course_data['name']}")
        print(f"  - 课时: {len(lessons)} 个")
    
    if exercise_file.exists():
        print("📝 解析练习内容...")
        exercise_parser = ExerciseParser(exercise_file)
        exercise_parser.load_file()
        
        exercises = exercise_parser.parse_exercises()
        demo_data["exercises"] = exercises
        
        print(f"  - 练习: {len(exercises)} 个")
    
    # 生成学习路径示例数据
    demo_data["learning_paths"] = generate_learning_paths(demo_data["course"].get("id"))
    
    # 生成学生进度数据
    demo_data["student_progress"] = generate_student_progress()
    
    return demo_data

def generate_learning_paths(course_id: str) -> List[Dict[str, Any]]:
    """生成学习路径数据"""
    
    learning_paths = []
    
    # 模拟3个不同水平的学生学习路径
    students = [
        {
            "name": "张小明", 
            "level": "beginner",
            "progress": 0.2,
            "current_lesson": 3,
            "completed_lessons": [1, 2]
        },
        {
            "name": "李小红", 
            "level": "intermediate", 
            "progress": 0.6,
            "current_lesson": 12,
            "completed_lessons": list(range(1, 12))
        },
        {
            "name": "王小刚", 
            "level": "advanced",
            "progress": 0.9, 
            "current_lesson": 20,
            "completed_lessons": list(range(1, 20))
        }
    ]
    
    for student in students:
        path = {
            "id": str(uuid.uuid4()),
            "student_id": str(uuid.uuid4()),
            "student_name": student["name"],
            "course_id": course_id,
            "current_lesson": student["current_lesson"],
            "completed_lessons": student["completed_lessons"],
            "progress_percentage": student["progress"] * 100,
            "learning_hours": student["progress"] * 56,
            "learning_style": {
                "visual": 0.8 if student["level"] == "beginner" else 0.6,
                "auditory": 0.3,
                "kinesthetic": 0.7 if student["level"] == "advanced" else 0.4
            },
            "difficulty_adjustment": 0.8 if student["level"] == "beginner" else 1.2 if student["level"] == "advanced" else 1.0,
            "recommended_exercises": generate_recommended_exercises(student["level"]),
            "last_study_time": datetime.now(timezone.utc),
            "status": "active",
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc)
        }
        learning_paths.append(path)
    
    return learning_paths

def generate_recommended_exercises(level: str) -> List[str]:
    """根据学生水平生成推荐练习"""
    
    if level == "beginner":
        return ["1.1", "1.2", "1.3", "2.1", "2.2"]
    elif level == "intermediate":
        return ["3.1", "3.2", "4.1", "5.1", "6.1"]
    else:  # advanced
        return ["7.1", "8.1", "9.1", "10.1", "项目1"]

def generate_student_progress() -> List[Dict[str, Any]]:
    """生成学生进度数据"""
    
    progress_data = []
    
    # 模拟不同学生的学习进度和表现
    student_performances = [
        {
            "name": "张小明",
            "submissions": 15,
            "average_score": 72.5,
            "improvement_rate": 0.15,
            "competency_level": "novice",
            "error_patterns": ["语法错误", "逻辑错误", "变量未初始化"],
            "emotional_state": {"confidence": 0.6, "motivation": 0.8, "frustration": 0.3}
        },
        {
            "name": "李小红", 
            "submissions": 28,
            "average_score": 85.2,
            "improvement_rate": 0.25,
            "competency_level": "intermediate",
            "error_patterns": ["指针使用错误", "内存管理问题"],
            "emotional_state": {"confidence": 0.8, "motivation": 0.9, "frustration": 0.2}
        },
        {
            "name": "王小刚",
            "submissions": 42,
            "average_score": 91.8,
            "improvement_rate": 0.35,
            "competency_level": "advanced", 
            "error_patterns": ["复杂算法优化", "边界条件处理"],
            "emotional_state": {"confidence": 0.9, "motivation": 0.95, "frustration": 0.1}
        }
    ]
    
    for perf in student_performances:
        profile = {
            "id": str(uuid.uuid4()),
            "student_id": str(uuid.uuid4()),
            "student_name": perf["name"],
            "competency_level": perf["competency_level"],
            "skill_scores": {
                "syntax": perf["average_score"] * 0.9,
                "logic": perf["average_score"] * 0.95,
                "algorithm": perf["average_score"] * 0.85,
                "debugging": perf["average_score"] * 0.8
            },
            "learning_style": {
                "preferred_feedback": "ENCOURAGE" if perf["competency_level"] == "novice" else "GUIDE",
                "learning_pace": "slow" if perf["competency_level"] == "novice" else "fast"
            },
            "error_patterns": perf["error_patterns"],
            "emotional_state": perf["emotional_state"],
            "total_submissions": perf["submissions"],
            "average_score": perf["average_score"],
            "improvement_rate": perf["improvement_rate"],
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc),
            "last_analyzed": datetime.now(timezone.utc)
        }
        progress_data.append(profile)
    
    return progress_data

def generate_ai_feedback_examples() -> List[Dict[str, Any]]:
    """生成AI反馈示例"""
    
    feedback_examples = [
        {
            "exercise_id": "1.1",
            "exercise_title": "Hello World程序",
            "student_code": '''#include <stdio.h>
int main() {
    printf("Hello World");
    return 0;
}''',
            "student_level": "beginner",
            "ai_feedback": {
                "overall_score": 85,
                "feedback_type": "ENCOURAGE",
                "positive_aspects": [
                    "程序结构正确",
                    "基本语法掌握良好",
                    "成功输出了预期结果"
                ],
                "suggestions": [
                    "建议在字符串末尾添加换行符\\n，这是良好的编程习惯",
                    "可以尝试添加注释来解释代码功能"
                ],
                "learning_tips": [
                    "printf函数是C语言中最基本的输出函数",
                    "main函数是程序的入口点"
                ],
                "next_steps": ["尝试输出不同的信息", "学习变量的使用"]
            }
        },
        {
            "exercise_id": "3.1", 
            "exercise_title": "数组操作",
            "student_code": '''#include <stdio.h>
int main() {
    int arr[5] = {1,2,3,4,5};
    for(int i=0; i<=5; i++) {
        printf("%d ", arr[i]);
    }
    return 0;
}''',
            "student_level": "intermediate",
            "ai_feedback": {
                "overall_score": 65,
                "feedback_type": "GUIDE",
                "issues_found": [
                    {
                        "type": "逻辑错误",
                        "description": "数组越界访问",
                        "line": 4,
                        "suggestion": "循环条件应该是 i < 5，而不是 i <= 5"
                    }
                ],
                "positive_aspects": [
                    "数组声明和初始化正确",
                    "for循环结构使用恰当"
                ],
                "code_analysis": {
                    "potential_runtime_errors": ["数组越界可能导致程序崩溃"],
                    "best_practices": ["使用数组长度常量代替硬编码数字"]
                },
                "corrected_code_hint": "思考一下数组索引的有效范围是什么？"
            }
        }
    ]
    
    return feedback_examples

def create_demo_scenarios() -> Dict[str, Any]:
    """创建完整的演示场景"""
    
    scenarios = {
        "student_submission_flow": {
            "description": "学生提交代码的完整流程演示",
            "steps": [
                {
                    "step": 1,
                    "action": "学生登录系统",
                    "data": {"username": "zhang_xiaoming", "role": "student"}
                },
                {
                    "step": 2, 
                    "action": "选择课程和练习",
                    "data": {"course": "C语言程序设计", "exercise": "1.1 Hello World程序"}
                },
                {
                    "step": 3,
                    "action": "提交代码",
                    "data": {
                        "code": "#include <stdio.h>\\nint main() {\\n    printf(\"Hello World\");\\n    return 0;\\n}",
                        "language": "C"
                    }
                },
                {
                    "step": 4,
                    "action": "AI系统分析代码",
                    "data": {"analysis_time": "0.5s", "agents_involved": ["CodeAnalyzer", "PedagogyExpert"]}
                },
                {
                    "step": 5,
                    "action": "生成个性化反馈", 
                    "data": {"feedback_type": "ENCOURAGE", "score": 85}
                },
                {
                    "step": 6,
                    "action": "更新学习进度",
                    "data": {"progress_increase": 0.05, "new_recommendations": ["变量使用练习"]}
                }
            ]
        },
        "teacher_review_flow": {
            "description": "教师批改和审核的完整流程演示",
            "steps": [
                {
                    "step": 1,
                    "action": "教师登录系统",
                    "data": {"username": "prof_wang", "role": "teacher"}
                },
                {
                    "step": 2,
                    "action": "查看班级提交情况",
                    "data": {"total_submissions": 45, "pending_review": 12}
                },
                {
                    "step": 3,
                    "action": "查看AI生成的反馈",
                    "data": {"ai_feedback_quality": 4.2, "flagged_for_review": 3}
                },
                {
                    "step": 4,
                    "action": "审核和调整反馈",
                    "data": {"approved": 9, "modified": 3}
                },
                {
                    "step": 5,
                    "action": "发布最终反馈给学生",
                    "data": {"notification_sent": True}
                }
            ]
        },
        "learning_path_adaptation": {
            "description": "学习路径个性化调整演示",
            "student_profile": {
                "name": "李小红",
                "current_performance": {"average_score": 85, "strong_areas": ["语法", "逻辑"], "weak_areas": ["指针", "内存管理"]},
                "learning_style": {"visual": 0.8, "hands_on": 0.9},
                "emotional_state": {"confidence": 0.7, "motivation": 0.85}
            },
            "ai_recommendations": [
                "增加指针相关的可视化练习",
                "提供内存管理的实际项目案例",
                "适当降低练习难度建立信心",
                "推荐同伴学习和代码讨论"
            ],
            "adjusted_path": {
                "next_lessons": ["指针基础概念", "指针与数组", "动态内存分配"],
                "practice_exercises": ["4.1", "4.2", "5.1"],
                "estimated_completion": "2周"
            }
        }
    }
    
    return scenarios

def main():
    """主函数"""
    print("🎯 生成课程演示数据...")
    
    # 生成完整的演示数据
    demo_data = generate_demo_course_data()
    
    # 添加AI反馈示例
    demo_data["ai_feedback_examples"] = generate_ai_feedback_examples()
    
    # 添加演示场景
    demo_data["demo_scenarios"] = create_demo_scenarios()
    
    # 保存演示数据
    output_file = Path("demo_data/course_integration_demo.json")
    output_file.parent.mkdir(exist_ok=True)
    
    # 处理datetime序列化问题
    def json_serializer(obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        raise TypeError(f"Object of type {type(obj)} is not JSON serializable")
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(demo_data, f, ensure_ascii=False, indent=2, default=json_serializer)
    
    print(f"✅ 演示数据已保存到: {output_file}")
    
    # 生成数据统计
    stats = {
        "course_count": 1 if demo_data["course"] else 0,
        "lesson_count": len(demo_data["lessons"]),
        "exercise_count": len(demo_data["exercises"]),
        "learning_path_count": len(demo_data["learning_paths"]),
        "student_profile_count": len(demo_data["student_progress"]),
        "ai_feedback_examples": len(demo_data["ai_feedback_examples"]),
        "demo_scenarios": len(demo_data["demo_scenarios"])
    }
    
    print("\\n📊 生成数据统计:")
    for key, value in stats.items():
        print(f"  - {key}: {value}")
    
    # 创建API测试数据文件
    create_api_test_data(demo_data)
    
    print("\\n🎉 课程演示数据生成完成!")
    return True

def create_api_test_data(demo_data: Dict[str, Any]):
    """创建API测试数据"""
    
    api_test_data = {
        "test_course_creation": {
            "method": "POST",
            "endpoint": "/api/v1/courses",
            "payload": demo_data["course"]
        },
        "test_lesson_creation": {
            "method": "POST", 
            "endpoint": "/api/v1/lessons",
            "payload": demo_data["lessons"][0] if demo_data["lessons"] else {}
        },
        "test_student_submission": {
            "method": "POST",
            "endpoint": "/api/v1/submissions",
            "payload": {
                "student_id": demo_data["learning_paths"][0]["student_id"] if demo_data["learning_paths"] else str(uuid.uuid4()),
                "assignment_description": "编写一个Hello World程序",
                "code": "#include <stdio.h>\\nint main() {\\n    printf(\"Hello World\\\\n\");\\n    return 0;\\n}",
                "language": "C",
                "student_message": "这是我的第一个C程序"
            }
        },
        "test_learning_path": {
            "method": "GET",
            "endpoint": "/api/v1/learning-paths/{student_id}",
            "expected_response": demo_data["learning_paths"][0] if demo_data["learning_paths"] else {}
        }
    }
    
    # 保存API测试数据
    api_test_file = Path("demo_data/api_test_data.json")
    with open(api_test_file, 'w', encoding='utf-8') as f:
        json.dump(api_test_data, f, ensure_ascii=False, indent=2, default=lambda x: x.isoformat() if isinstance(x, datetime) else str(x))
    
    print(f"✅ API测试数据已保存到: {api_test_file}")

if __name__ == "__main__":
    result = main()
    sys.exit(0 if result else 1)