#!/usr/bin/env python3
"""
Curriculum Import Script - C Language Course
解析和导入C语言课程内容到数据库

Author: Product Manager Coordinator
Date: 2025-09-12
Updated: Sprint 3 - 使用Repository模式重构
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
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

import asyncio
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import settings
from app.database.models import Course, Lesson, CourseExercise
from app.database.database import Base

console = Console()


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
        if not self.curriculum_file.exists():
            raise FileNotFoundError(f"课程文件不存在: {self.curriculum_file}")
        with open(self.curriculum_file, 'r', encoding='utf-8') as f:
            self.content = f.read()
        console.print(f"[green]已加载文件: {self.curriculum_file}[/green]")

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

        return objectives[:20]  # 限制返回的数量

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
            lesson_pattern = r'### 课时(\d+)-?(\d+)?：([^#\n]+)'
            lesson_matches = re.finditer(lesson_pattern, module_content)

            for lesson_match in lesson_matches:
                lesson_start_num = int(lesson_match.group(1))
                lesson_title = lesson_match.group(3).strip()

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
                    "duration": 90,  # 默认90分钟
                    "content": lesson_content.strip()[:5000],  # 限制内容长度
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
            items = re.findall(r'[-*] (.+)', obj_content)
            objectives = [item.strip() for item in items[:10]]  # 限制数量

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

        return list(set(concepts))[:15]  # 去重并限制数量

    def _extract_teaching_structure(self, content: str) -> Dict[str, Any]:
        """提取教学结构"""
        structure = {}

        # 查找课程结构
        struct_match = re.search(r'```\s*课程结构[：:]?\s*\n(.*?)\n```', content, re.DOTALL)
        if struct_match:
            structure["course_structure"] = struct_match.group(1).strip()[:2000]

        return structure

    def _extract_ai_strategies(self, content: str) -> Dict[str, Any]:
        """提取AI支持策略"""
        strategies = {}

        # 查找AI Agent教学支持策略
        strategy_match = re.search(r'\*\*AI Agent教学支持策略\*\*[：:]\s*\n(.*?)(?=\*\*|$)', content, re.DOTALL)
        if strategy_match:
            strategy_content = strategy_match.group(1)

            # 提取各个Agent的策略
            agents = ["PedagogyExpert", "StudentProfiler", "FeedbackGenerator", "CodeAnalyzer"]
            for agent in agents:
                agent_match = re.search(f'- \\*\\*{agent}\\*\\*[：:](.+)', strategy_content)
                if agent_match:
                    strategies[agent] = agent_match.group(1).strip()[:200]

        return strategies


class ExerciseParser:
    """练习题解析器"""

    def __init__(self, exercise_file: Path):
        self.exercise_file = exercise_file
        self.content = ""
        self.exercises = []

    def load_file(self):
        """加载练习文件"""
        if not self.exercise_file.exists():
            console.print(f"[yellow]练习文件不存在: {self.exercise_file}[/yellow]")
            return False
        with open(self.exercise_file, 'r', encoding='utf-8') as f:
            self.content = f.read()
        console.print(f"[green]已加载练习文件: {self.exercise_file}[/green]")
        return True

    def parse_exercises(self) -> List[Dict[str, Any]]:
        """解析练习题"""
        exercises = []

        # 查找模块练习 - 更宽松的正则匹配
        module_pattern = r'## 📚 模块(\d+)[：:：]([^\n]+)'
        modules = re.finditer(module_pattern, self.content)

        exercise_count = 0
        for module_match in modules:
            module_num = int(module_match.group(1))
            module_title = module_match.group(2).strip()

            # 获取模块内容
            module_start = module_match.end()
            next_module = re.search(r'## 📚 模块\d+', self.content[module_start:])
            module_end = module_start + next_module.start() if next_module else len(self.content)
            module_content = self.content[module_start:module_end]

            # 解析题目 - 简化的正则
            exercise_pattern = r'\*\*题目\s*(\d+)\.?(\d*)[：:]([^\*]+)\*\*'
            exercise_matches = re.finditer(exercise_pattern, module_content)

            for ex_match in exercise_matches:
                exercise_count += 1
                ex_main = ex_match.group(1)
                ex_sub = ex_match.group(2) or "1"
                title = ex_match.group(3).strip()

                # 获取题目内容
                ex_start = ex_match.end()
                next_ex = re.search(r'\*\*题目\s*\d+', module_content[ex_start:])
                ex_end = ex_start + next_ex.start() if next_ex else min(ex_start + 2000, len(module_content))
                ex_content = module_content[ex_start:ex_end]

                # 提取难度
                difficulty = ex_content.count('⭐')
                if difficulty == 0:
                    difficulty = 2  # 默认难度

                # 提取题目类型
                exercise_type = "choice"
                if "编程" in title or "代码" in title:
                    exercise_type = "coding"
                elif "填空" in title:
                    exercise_type = "fill_blank"
                elif "简答" in title:
                    exercise_type = "essay"

                exercise_data = {
                    "id": str(uuid.uuid4()),
                    "exercise_number": f"{module_num}.{ex_sub}",
                    "title": title[:200],
                    "exercise_type": exercise_type,
                    "difficulty_level": min(difficulty, 5),
                    "question": ex_content.strip()[:3000],
                    "options": [],
                    "correct_answer": "",
                    "sample_code": "",
                    "knowledge_points": [f"模块{module_num}: {module_title}"],
                    "ai_feedback_config": {
                        "feedback_style": "ENCOURAGE" if difficulty <= 2 else "GUIDE",
                        "max_attempts": 3,
                        "hint_available": True
                    },
                    "teaching_hints": [],
                    "is_active": True,
                    "created_at": datetime.utcnow(),
                    "updated_at": datetime.utcnow()
                }

                exercises.append(exercise_data)

        console.print(f"[blue]解析到 {len(exercises)} 道练习题[/blue]")
        return exercises


class DatabaseImporter:
    """数据库导入器 - 使用SQLAlchemy"""

    def __init__(self):
        self.engine = None
        self.session_factory = None

    async def connect(self):
        """连接数据库"""
        try:
            # 创建异步引擎
            self.engine = create_async_engine(
                settings.DATABASE_URL,
                echo=False,
                pool_pre_ping=True
            )

            self.session_factory = sessionmaker(
                self.engine,
                class_=AsyncSession,
                expire_on_commit=False
            )

            # 测试连接
            async with self.engine.begin() as conn:
                await conn.run_sync(lambda sync_conn: sync_conn.execute("SELECT 1"))

            console.print("[green]数据库连接成功[/green]")
            return True
        except Exception as e:
            console.print(f"[red]数据库连接失败: {e}[/red]")
            raise

    async def disconnect(self):
        """断开数据库连接"""
        if self.engine:
            await self.engine.dispose()
            console.print("[green]数据库连接已关闭[/green]")

    async def import_course(self, course_data: Dict[str, Any]) -> str:
        """导入课程数据"""
        async with self.session_factory() as session:
            try:
                # 创建Course对象
                course = Course(
                    id=uuid.UUID(course_data["id"]),
                    name=course_data["name"],
                    code=course_data["code"],
                    language=course_data["language"],
                    description=course_data["description"],
                    total_hours=course_data["total_hours"],
                    difficulty_level=course_data["difficulty_level"],
                    prerequisites=course_data["prerequisites"],
                    curriculum_data=course_data["curriculum_data"],
                    learning_objectives=course_data["learning_objectives"],
                    is_active=course_data["is_active"]
                )

                # 检查是否已存在
                from sqlalchemy import select
                existing = await session.execute(
                    select(Course).where(Course.code == course_data["code"])
                )
                if existing.scalar_one_or_none():
                    console.print(f"[yellow]课程已存在，跳过: {course_data['name']}[/yellow]")
                    return course_data["id"]

                session.add(course)
                await session.commit()

                console.print(f"[green]课程导入成功: {course_data['name']} (ID: {course_data['id'][:8]}...)[/green]")
                return course_data["id"]

            except Exception as e:
                await session.rollback()
                console.print(f"[red]课程导入失败: {e}[/red]")
                raise

    async def import_lessons(self, course_id: str, lessons: List[Dict[str, Any]]):
        """导入课时数据"""
        async with self.session_factory() as session:
            try:
                imported_count = 0
                for lesson_data in lessons:
                    lesson = Lesson(
                        id=uuid.UUID(lesson_data["id"]),
                        course_id=uuid.UUID(course_id),
                        lesson_number=lesson_data["lesson_number"],
                        title=lesson_data["title"],
                        subtitle=lesson_data.get("subtitle"),
                        duration=lesson_data.get("duration"),
                        content=lesson_data.get("content"),
                        learning_objectives=lesson_data.get("learning_objectives", []),
                        key_concepts=lesson_data.get("key_concepts", []),
                        teaching_structure=lesson_data.get("teaching_structure", {}),
                        ai_support_strategies=lesson_data.get("ai_support_strategies", {}),
                        is_active=lesson_data.get("is_active", True)
                    )

                    session.add(lesson)
                    imported_count += 1

                await session.commit()
                console.print(f"[green]{imported_count} 个课时导入成功[/green]")

            except Exception as e:
                await session.rollback()
                console.print(f"[red]课时导入失败: {e}[/red]")
                raise

    async def import_exercises(self, course_id: str, exercises: List[Dict[str, Any]]):
        """导入练习数据"""
        if not exercises:
            console.print("[yellow]没有练习题需要导入[/yellow]")
            return

        async with self.session_factory() as session:
            try:
                imported_count = 0
                for exercise_data in exercises:
                    exercise = CourseExercise(
                        id=uuid.UUID(exercise_data["id"]),
                        course_id=uuid.UUID(course_id),
                        exercise_number=exercise_data["exercise_number"],
                        title=exercise_data["title"],
                        exercise_type=exercise_data["exercise_type"],
                        difficulty_level=exercise_data["difficulty_level"],
                        question=exercise_data["question"],
                        options=exercise_data.get("options", []),
                        correct_answer=exercise_data.get("correct_answer", ""),
                        sample_code=exercise_data.get("sample_code", ""),
                        knowledge_points=exercise_data.get("knowledge_points", []),
                        ai_feedback_config=exercise_data.get("ai_feedback_config", {}),
                        teaching_hints=exercise_data.get("teaching_hints", []),
                        is_active=exercise_data.get("is_active", True)
                    )

                    session.add(exercise)
                    imported_count += 1

                await session.commit()
                console.print(f"[green]{imported_count} 个练习题导入成功[/green]")

            except Exception as e:
                await session.rollback()
                console.print(f"[red]练习题导入失败: {e}[/red]")
                raise


async def main():
    """主函数"""
    console.print("\n[bold blue]🚀 开始导入C语言课程内容...[/bold blue]\n")

    # 文件路径 - 使用绝对路径
    curriculum_file = PROJECT_ROOT / "docs" / "education" / "c_language_detailed_curriculum.md"
    exercise_file = PROJECT_ROOT / "docs" / "education" / "c_language_exercise_bank.md"

    # 检查文件存在
    if not curriculum_file.exists():
        console.print(f"[red]课程文件不存在: {curriculum_file}[/red]")
        return False

    try:
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:

            # 解析课程内容
            task = progress.add_task("[cyan]解析课程内容...", total=None)
            curriculum_parser = CurriculumParser(curriculum_file)
            curriculum_parser.load_file()

            course_data = curriculum_parser.parse_course_info()
            lessons = curriculum_parser.parse_lessons()
            progress.update(task, completed=True)

            console.print(f"  - 课程信息: [bold]{course_data['name']}[/bold]")
            console.print(f"  - 课时数量: [bold]{len(lessons)}[/bold]")

            # 解析练习内容
            exercises = []
            if exercise_file.exists():
                task = progress.add_task("[cyan]解析练习内容...", total=None)
                exercise_parser = ExerciseParser(exercise_file)
                if exercise_parser.load_file():
                    exercises = exercise_parser.parse_exercises()
                progress.update(task, completed=True)
                console.print(f"  - 练习数量: [bold]{len(exercises)}[/bold]")

            # 导入数据库
            task = progress.add_task("[cyan]导入数据库...", total=None)
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
            progress.update(task, completed=True)

        # 显示统计信息
        console.print("\n[bold green]🎉 课程内容导入完成![/bold green]\n")

        table = Table(title="导入统计")
        table.add_column("项目", style="cyan")
        table.add_column("数量", style="green")
        table.add_row("课程", "1")
        table.add_row("课时", str(len(lessons)))
        table.add_row("练习", str(len(exercises)))
        console.print(table)

        return True

    except Exception as e:
        console.print(f"\n[red]导入过程中发生错误: {e}[/red]")
        import traceback
        console.print(f"[dim]{traceback.format_exc()}[/dim]")
        return False


if __name__ == "__main__":
    result = asyncio.run(main())
    sys.exit(0 if result else 1)
