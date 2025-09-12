#!/usr/bin/env python3
"""
Curriculum Import Script - C Language Course
解析和导入C语言课程内容到数据库

Author: Product Manager Coordinator  
Date: 2025-09-12
"""

import sys
import os
import re
import json
import uuid
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import asyncio
import asyncpg
from app.core.config import settings

class CurriculumParser:
    """课程内容解析器"""
    
    def __init__(self, curriculum_file: Path):
        self.curriculum_file = curriculum_file
        self.content = ""
        self.course_data = {}
        self.lessons = []
        self.exercises = []
        
    def load_file(self):
        """加载课程文件"""
        with open(self.curriculum_file, 'r', encoding='utf-8') as f:
            self.content = f.read()
    
    def parse_course_info(self) -> Dict[str, Any]:
        """解析课程基本信息"""
        course_title_match = re.search(r'# ([^#\n]+)', self.content)
        course_title = course_title_match.group(1).strip() if course_title_match else "C语言程序设计课程"
        
        # 提取总课时数
        hours_match = re.search(r'(\d+)课时', course_title)
        total_hours = int(hours_match.group(1)) if hours_match else 56
        
        # 提取课程概览信息
        overview_section = re.search(r'## 🎯 课程概览与教育理论基础(.*?)(?=##|$)', self.content, re.DOTALL)
        description = overview_section.group(1).strip() if overview_section else ""
        
        return {
            "id": str(uuid.uuid4()),
            "name": course_title,
            "code": "C001", 
            "language": "C",
            "description": description[:500] + "..." if len(description) > 500 else description,
            "total_hours": total_hours,
            "difficulty_level": "beginner",
            "prerequisites": [],
            "curriculum_data": {
                "design_principles": self._extract_design_principles(),
                "learning_theory": "建构主义学习理论 + 最近发展区理论 + 认知负荷理论",
                "target_audience": "18-22岁大学生"
            },
            "learning_objectives": self._extract_learning_objectives(),
            "is_active": True,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
    
    def _extract_design_principles(self) -> List[str]:
        """提取设计原则"""
        principles = []
        
        principles_section = re.search(r'### 课程总体设计原则(.*?)(?=###|##|$)', self.content, re.DOTALL)
        if principles_section:
            # 查找所有**开头的项目
            principle_matches = re.findall(r'\*\*([^*]+)\*\*：?', principles_section.group(1))
            principles = [p.strip() for p in principle_matches]
        
        return principles
    
    def _extract_learning_objectives(self) -> List[str]:
        """提取学习目标"""
        objectives = []
        
        # 查找所有学习目标部分
        objective_sections = re.findall(r'#### 🎯 学习目标(.*?)(?=####|###|##|$)', self.content, re.DOTALL)
        
        for section in objective_sections:
            # 提取知识目标、技能目标、素质目标
            for obj_type in ['知识目标', '技能目标', '素质目标']:
                obj_match = re.search(f'{obj_type}.*?：(.*?)(?={obj_type}|$)', section, re.DOTALL)
                if obj_match:
                    # 提取列表项
                    items = re.findall(r'- (.+)', obj_match.group(1))
                    objectives.extend([f"[{obj_type}] {item.strip()}" for item in items])
        
        return objectives
    
    def parse_lessons(self) -> List[Dict[str, Any]]:
        """解析课时内容"""
        lessons = []
        
        # 查找所有模块
        module_pattern = r'## 📚 模块(\d+)：([^#\n]+) \((\d+)课时\)'
        modules = re.finditer(module_pattern, self.content)
        
        for module_match in modules:
            module_num = int(module_match.group(1))
            module_title = module_match.group(2).strip()
            module_hours = int(module_match.group(3))
            
            # 获取模块内容
            module_start = module_match.end()
            next_module = re.search(r'## 📚 模块\d+', self.content[module_start:])
            module_end = module_start + next_module.start() if next_module else len(self.content)
            module_content = self.content[module_start:module_end]
            
            # 解析模块中的课时
            lesson_pattern = r'### 课时(\d+)-?(\d+)?：([^#\n]+) \((\d+)学时\)'
            lesson_matches = re.finditer(lesson_pattern, module_content)
            
            for lesson_match in lesson_matches:
                lesson_start_num = int(lesson_match.group(1))
                lesson_end_num = int(lesson_match.group(2)) if lesson_match.group(2) else lesson_start_num
                lesson_title = lesson_match.group(3).strip()
                lesson_duration = int(lesson_match.group(4)) * 45  # 转换为分钟
                
                # 获取课时内容
                lesson_start_pos = lesson_match.end()
                next_lesson = re.search(r'### 课时\d+', module_content[lesson_start_pos:])
                lesson_end_pos = lesson_start_pos + next_lesson.start() if next_lesson else len(module_content)
                lesson_content = module_content[lesson_start_pos:lesson_end_pos]
                
                # 解析课时详细信息
                lesson_data = {
                    "id": str(uuid.uuid4()),
                    "lesson_number": lesson_start_num,
                    "title": lesson_title,
                    "subtitle": f"模块{module_num} - {lesson_title}",
                    "duration": lesson_duration,
                    "content": lesson_content.strip(),
                    "learning_objectives": self._extract_lesson_objectives(lesson_content),
                    "key_concepts": self._extract_key_concepts(lesson_content),
                    "teaching_structure": self._extract_teaching_structure(lesson_content),
                    "ai_support_strategies": self._extract_ai_strategies(lesson_content),
                    "is_active": True,
                    "created_at": datetime.utcnow(),
                    "updated_at": datetime.utcnow()
                }
                
                lessons.append(lesson_data)
        
        return lessons
    
    def _extract_lesson_objectives(self, content: str) -> List[str]:
        """提取课时学习目标"""
        objectives = []
        
        objectives_section = re.search(r'#### 🎯 学习目标(.*?)(?=####|###|$)', content, re.DOTALL)
        if objectives_section:
            obj_content = objectives_section.group(1)
            
            # 提取各类目标
            for obj_type in ['知识目标', '技能目标', '素质目标']:
                obj_match = re.search(f'\\*\\*{obj_type}\\*\\*[：:]\\s*\\n(.*?)(?=\\*\\*|$)', obj_content, re.DOTALL)
                if obj_match:
                    items = re.findall(r'[-*] (.+)', obj_match.group(1))
                    objectives.extend(items)
        
        return objectives
    
    def _extract_key_concepts(self, content: str) -> List[str]:
        """提取关键概念"""
        concepts = []
        
        # 查找课程结构中的概念
        struct_match = re.search(r'```\s*课程结构[：:]?\s*\n(.*?)\n```', content, re.DOTALL)
        if struct_match:
            # 提取结构中的概念点
            concept_matches = re.findall(r'[├└]── (.+)', struct_match.group(1))
            concepts.extend([c.strip() for c in concept_matches])
        
        # 查找其他关键概念标记
        concept_matches = re.findall(r'[**]([A-Za-z]+\s*[语言|程序|函数|变量|指针|结构|数组]+)[**]', content)
        concepts.extend(concept_matches)
        
        return list(set(concepts))  # 去重
    
    def _extract_teaching_structure(self, content: str) -> Dict[str, Any]:
        """提取教学结构"""
        structure = {}
        
        # 查找课程结构
        struct_match = re.search(r'```\s*课程结构[：:]?\s*\n(.*?)\n```', content, re.DOTALL)
        if struct_match:
            structure["course_structure"] = struct_match.group(1).strip()
        
        # 查找教学环节
        phases = ["导入环节", "知识建构", "核心内容", "应用拓展", "总结反思"]
        for phase in phases:
            phase_match = re.search(f'[├└]── {phase} \\((\\d+)分钟\\)', content)
            if phase_match:
                structure[phase] = {"duration": int(phase_match.group(1))}
        
        return structure
    
    def _extract_ai_strategies(self, content: str) -> Dict[str, Any]:
        """提取AI支持策略"""
        strategies = {}
        
        # 查找AI Agent教学支持策略
        strategy_match = re.search(r'\\*\\*AI Agent教学支持策略\\*\\*[：:]\\s*\\n(.*?)(?=\\*\\*|$)', content, re.DOTALL)
        if strategy_match:
            strategy_content = strategy_match.group(1)
            
            # 提取各个Agent的策略
            agents = ["PedagogyExpert", "StudentProfiler", "FeedbackGenerator", "CodeAnalyzer", "QualityController", "DebuggingMentor"]
            for agent in agents:
                agent_match = re.search(f'- \\*\\*{agent}\\*\\*[：:](.+)', strategy_content)
                if agent_match:
                    strategies[agent] = agent_match.group(1).strip()
        
        return strategies

class ExerciseParser:
    """练习题解析器"""
    
    def __init__(self, exercise_file: Path):
        self.exercise_file = exercise_file
        self.content = ""
        self.exercises = []
        
    def load_file(self):
        """加载练习文件"""
        with open(self.exercise_file, 'r', encoding='utf-8') as f:
            self.content = f.read()
    
    def parse_exercises(self) -> List[Dict[str, Any]]:
        """解析练习题"""
        exercises = []
        
        # 查找模块练习
        module_pattern = r'## 📚 模块(\d+)：([^#\n]+) - 练习题库 \((\d+)题\)'
        modules = re.finditer(module_pattern, self.content)
        
        for module_match in modules:
            module_num = int(module_match.group(1))
            module_title = module_match.group(2).strip()
            total_exercises = int(module_match.group(3))
            
            # 获取模块内容
            module_start = module_match.end()
            next_module = re.search(r'## 📚 模块\d+', self.content[module_start:])
            module_end = module_start + next_module.start() if next_module else len(self.content)
            module_content = self.content[module_start:module_end]
            
            # 解析各层级练习
            exercises.extend(self._parse_level_exercises(module_content, module_num, "基础练习层"))
            exercises.extend(self._parse_level_exercises(module_content, module_num, "综合练习层"))
            exercises.extend(self._parse_level_exercises(module_content, module_num, "项目练习层"))
        
        return exercises
    
    def _parse_level_exercises(self, content: str, module_num: int, level_name: str) -> List[Dict[str, Any]]:
        """解析特定层级的练习"""
        exercises = []
        
        # 查找层级内容
        level_pattern = f'### {level_name} \\((\\d+)题\\)'
        level_match = re.search(level_pattern, content)
        
        if not level_match:
            return exercises
            
        level_start = level_match.end()
        next_level = re.search(r'### \w+练习层', content[level_start:])
        level_end = level_start + next_level.start() if next_level else len(content)
        level_content = content[level_start:level_end]
        
        # 解析具体题目
        exercise_pattern = r'\\*\\*题目(\\d+)\\.(\\d+)[：:]([^*]+)\\*\\*\\s*\\n```\\s*(.*?)\\n题目类型[：:](.+?)\\n难度等级[：:](.+?)\\n知识点[：:](.+?)\\n\\n题目[：:](.+?)\\n'
        exercise_matches = re.finditer(exercise_pattern, level_content, re.DOTALL)
        
        for exercise_match in exercise_matches:
            module_ex_num = exercise_match.group(1)
            ex_num = exercise_match.group(2)
            title = exercise_match.group(3).strip()
            exercise_type = exercise_match.group(5).strip()
            difficulty_stars = exercise_match.group(6).count('⭐')
            knowledge_point = exercise_match.group(7).strip()
            question = exercise_match.group(8).strip()
            
            # 解析选项和答案（如果是选择题）
            options = []
            correct_answer = ""
            
            if exercise_type == "选择题":
                # 查找选项
                options_match = re.search(r'A\\.(.+?)\\nB\\.(.+?)\\nC\\.(.+?)\\nD\\.(.+?)\\n', question)
                if options_match:
                    options = [f"A. {options_match.group(1)}", f"B. {options_match.group(2)}", 
                              f"C. {options_match.group(3)}", f"D. {options_match.group(4)}"]
                    
                    # 查找答案
                    answer_match = re.search(r'答案[：:]\\s*([ABCD])', level_content[exercise_match.end():])
                    if answer_match:
                        correct_answer = answer_match.group(1)
            
            exercise_data = {
                "id": str(uuid.uuid4()),
                "exercise_number": f"{module_num}.{ex_num}",
                "title": title,
                "exercise_type": self._normalize_exercise_type(exercise_type),
                "difficulty_level": difficulty_stars,
                "question": question,
                "options": options,
                "correct_answer": correct_answer,
                "sample_code": "",
                "knowledge_points": [knowledge_point],
                "ai_feedback_config": self._generate_feedback_config(exercise_type, difficulty_stars),
                "teaching_hints": [],
                "is_active": True,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
            
            exercises.append(exercise_data)
        
        return exercises
    
    def _normalize_exercise_type(self, exercise_type: str) -> str:
        """规范化练习类型"""
        type_mapping = {
            "选择题": "choice",
            "编程题": "coding", 
            "填空题": "fill_blank",
            "简答题": "essay",
            "代码分析题": "code_analysis",
            "调试题": "debugging"
        }
        return type_mapping.get(exercise_type, "choice")
    
    def _generate_feedback_config(self, exercise_type: str, difficulty: int) -> Dict[str, Any]:
        """生成AI反馈配置"""
        config = {
            "feedback_style": "ENCOURAGE" if difficulty <= 2 else "GUIDE" if difficulty <= 3 else "HINT",
            "max_attempts": 3 if difficulty <= 2 else 2 if difficulty <= 3 else 1,
            "hint_available": difficulty <= 3,
            "detailed_explanation": True
        }
        
        if exercise_type == "编程题":
            config["code_analysis"] = True
            config["syntax_check"] = True
            config["performance_check"] = difficulty >= 3
            
        return config

class DatabaseImporter:
    """数据库导入器"""
    
    def __init__(self):
        self.db_url = settings.DATABASE_URL.replace("postgresql+asyncpg://", "postgresql://")
        self.conn = None
        
    async def connect(self):
        """连接数据库"""
        try:
            self.conn = await asyncpg.connect(self.db_url)
            print("✅ 数据库连接成功")
        except Exception as e:
            print(f"❌ 数据库连接失败: {e}")
            raise
    
    async def disconnect(self):
        """断开数据库连接"""
        if self.conn:
            await self.conn.close()
            print("✅ 数据库连接已关闭")
    
    async def import_course(self, course_data: Dict[str, Any]) -> str:
        """导入课程数据"""
        try:
            course_id = course_data["id"]
            
            await self.conn.execute("""
                INSERT INTO courses (
                    id, name, code, language, description, total_hours, 
                    difficulty_level, prerequisites, curriculum_data, 
                    learning_objectives, is_active, created_at, updated_at
                ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13)
                ON CONFLICT (id) DO UPDATE SET
                    name = EXCLUDED.name,
                    description = EXCLUDED.description,
                    updated_at = EXCLUDED.updated_at
            """, 
                course_id, course_data["name"], course_data["code"], 
                course_data["language"], course_data["description"], 
                course_data["total_hours"], course_data["difficulty_level"], 
                json.dumps(course_data["prerequisites"]), 
                json.dumps(course_data["curriculum_data"]), 
                json.dumps(course_data["learning_objectives"]), 
                course_data["is_active"], course_data["created_at"], 
                course_data["updated_at"]
            )
            
            print(f"✅ 课程导入成功: {course_data['name']} (ID: {course_id})")
            return course_id
            
        except Exception as e:
            print(f"❌ 课程导入失败: {e}")
            raise
    
    async def import_lessons(self, course_id: str, lessons: List[Dict[str, Any]]):
        """导入课时数据"""
        try:
            for lesson in lessons:
                lesson["course_id"] = course_id
                
                await self.conn.execute("""
                    INSERT INTO lessons (
                        id, course_id, lesson_number, title, subtitle, duration,
                        content, learning_objectives, key_concepts, teaching_structure,
                        ai_support_strategies, is_active, created_at, updated_at
                    ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14)
                    ON CONFLICT (course_id, lesson_number) DO UPDATE SET
                        title = EXCLUDED.title,
                        content = EXCLUDED.content,
                        updated_at = EXCLUDED.updated_at
                """,
                    lesson["id"], lesson["course_id"], lesson["lesson_number"],
                    lesson["title"], lesson["subtitle"], lesson["duration"],
                    lesson["content"], json.dumps(lesson["learning_objectives"]),
                    json.dumps(lesson["key_concepts"]), json.dumps(lesson["teaching_structure"]),
                    json.dumps(lesson["ai_support_strategies"]), lesson["is_active"],
                    lesson["created_at"], lesson["updated_at"]
                )
            
            print(f"✅ {len(lessons)} 个课时导入成功")
            
        except Exception as e:
            print(f"❌ 课时导入失败: {e}")
            raise
    
    async def import_exercises(self, course_id: str, exercises: List[Dict[str, Any]]):
        """导入练习数据"""
        try:
            for exercise in exercises:
                exercise["course_id"] = course_id
                
                await self.conn.execute("""
                    INSERT INTO course_exercises (
                        id, course_id, exercise_number, title, exercise_type,
                        difficulty_level, question, options, correct_answer,
                        sample_code, knowledge_points, ai_feedback_config,
                        teaching_hints, is_active, created_at, updated_at
                    ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15, $16)
                    ON CONFLICT (course_id, exercise_number) DO UPDATE SET
                        title = EXCLUDED.title,
                        question = EXCLUDED.question,
                        updated_at = EXCLUDED.updated_at
                """,
                    exercise["id"], exercise["course_id"], exercise["exercise_number"],
                    exercise["title"], exercise["exercise_type"], exercise["difficulty_level"],
                    exercise["question"], json.dumps(exercise["options"]), exercise["correct_answer"],
                    exercise["sample_code"], json.dumps(exercise["knowledge_points"]),
                    json.dumps(exercise["ai_feedback_config"]), json.dumps(exercise["teaching_hints"]),
                    exercise["is_active"], exercise["created_at"], exercise["updated_at"]
                )
            
            print(f"✅ {len(exercises)} 个练习题导入成功")
            
        except Exception as e:
            print(f"❌ 练习题导入失败: {e}")
            raise

async def main():
    """主函数"""
    print("🚀 开始导入C语言课程内容...")
    
    # 文件路径
    curriculum_file = Path("docs/education/c_language_detailed_curriculum.md")
    exercise_file = Path("docs/education/c_language_exercise_bank.md")
    
    # 检查文件存在
    if not curriculum_file.exists():
        print(f"❌ 课程文件不存在: {curriculum_file}")
        return False
        
    if not exercise_file.exists():
        print(f"❌ 练习文件不存在: {exercise_file}")
        return False
    
    try:
        # 解析课程内容
        print("📖 解析课程内容...")
        curriculum_parser = CurriculumParser(curriculum_file)
        curriculum_parser.load_file()
        
        course_data = curriculum_parser.parse_course_info()
        lessons = curriculum_parser.parse_lessons()
        
        print(f"  - 课程信息: {course_data['name']}")
        print(f"  - 课时数量: {len(lessons)}")
        
        # 解析练习内容  
        print("📝 解析练习内容...")
        exercise_parser = ExerciseParser(exercise_file)
        exercise_parser.load_file()
        
        exercises = exercise_parser.parse_exercises()
        print(f"  - 练习数量: {len(exercises)}")
        
        # 导入数据库
        print("💾 导入数据库...")
        importer = DatabaseImporter()
        await importer.connect()
        
        # 导入课程
        course_id = await importer.import_course(course_data)
        
        # 导入课时
        if lessons:
            await importer.import_lessons(course_id, lessons)
        
        # 导入练习
        if exercises:
            await importer.import_exercises(course_id, exercises)
        
        await importer.disconnect()
        
        print("\n🎉 课程内容导入完成!")
        print(f"📊 导入统计:")
        print(f"  - 课程: 1")
        print(f"  - 课时: {len(lessons)}")
        print(f"  - 练习: {len(exercises)}")
        
        return True
        
    except Exception as e:
        print(f"❌ 导入过程中发生错误: {e}")
        import traceback
        print(traceback.format_exc())
        return False

if __name__ == "__main__":
    result = asyncio.run(main())
    sys.exit(0 if result else 1)