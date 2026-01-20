#!/usr/bin/env python3
"""
Curriculum Import Verification Script
验证课程数据导入的完整性和正确性

Author: AI Backend Architecture Expert
Date: Sprint 3
"""

import sys
import os
from pathlib import Path
from typing import Dict, List, Any

# 添加项目根目录到Python路径
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

import asyncio
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select, func

from app.core.config import settings
from app.database.models import Course, Lesson, CourseExercise, LearningPath

console = Console()


class CurriculumVerifier:
    """课程导入验证器"""

    def __init__(self):
        self.engine = None
        self.session_factory = None
        self.verification_results = {
            "courses": {"passed": 0, "failed": 0, "warnings": []},
            "lessons": {"passed": 0, "failed": 0, "warnings": []},
            "exercises": {"passed": 0, "failed": 0, "warnings": []},
            "overall": {"status": "unknown", "issues": []}
        }

    async def connect(self):
        """连接数据库"""
        try:
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

            console.print("[green]数据库连接成功[/green]")
            return True
        except Exception as e:
            console.print(f"[red]数据库连接失败: {e}[/red]")
            return False

    async def disconnect(self):
        """断开连接"""
        if self.engine:
            await self.engine.dispose()

    async def verify_courses(self) -> Dict[str, Any]:
        """验证课程数据"""
        async with self.session_factory() as session:
            try:
                # 获取所有课程
                result = await session.execute(select(Course))
                courses = result.scalars().all()

                course_count = len(courses)
                self.verification_results["courses"]["count"] = course_count

                if course_count == 0:
                    self.verification_results["courses"]["failed"] += 1
                    self.verification_results["courses"]["warnings"].append("没有找到任何课程数据")
                    return {"status": "failed", "count": 0, "details": []}

                details = []
                for course in courses:
                    course_status = {"id": str(course.id), "name": course.name, "issues": []}

                    # 验证必要字段
                    if not course.name:
                        course_status["issues"].append("课程名称为空")
                    if not course.language:
                        course_status["issues"].append("编程语言未设置")
                    if course.total_hours <= 0:
                        course_status["issues"].append("总课时无效")

                    # 验证学习目标
                    if not course.learning_objectives or len(course.learning_objectives) == 0:
                        course_status["issues"].append("学习目标为空")

                    if course_status["issues"]:
                        self.verification_results["courses"]["failed"] += 1
                    else:
                        self.verification_results["courses"]["passed"] += 1

                    details.append(course_status)

                return {
                    "status": "passed" if self.verification_results["courses"]["failed"] == 0 else "warning",
                    "count": course_count,
                    "details": details
                }

            except Exception as e:
                console.print(f"[red]课程验证出错: {e}[/red]")
                return {"status": "error", "error": str(e)}

    async def verify_lessons(self) -> Dict[str, Any]:
        """验证课时数据"""
        async with self.session_factory() as session:
            try:
                # 获取所有课时
                result = await session.execute(
                    select(Lesson).order_by(Lesson.course_id, Lesson.lesson_number)
                )
                lessons = result.scalars().all()

                lesson_count = len(lessons)
                self.verification_results["lessons"]["count"] = lesson_count

                if lesson_count == 0:
                    self.verification_results["lessons"]["warnings"].append("没有找到任何课时数据")
                    return {"status": "warning", "count": 0, "details": []}

                # 按课程分组验证
                lessons_by_course = {}
                for lesson in lessons:
                    course_id = str(lesson.course_id)
                    if course_id not in lessons_by_course:
                        lessons_by_course[course_id] = []
                    lessons_by_course[course_id].append(lesson)

                details = []
                for course_id, course_lessons in lessons_by_course.items():
                    # 检查课时序号是否连续
                    lesson_numbers = sorted([l.lesson_number for l in course_lessons])
                    expected_numbers = list(range(1, len(lesson_numbers) + 1))

                    course_status = {
                        "course_id": course_id,
                        "lesson_count": len(course_lessons),
                        "issues": []
                    }

                    # 检查课时序号
                    if lesson_numbers != expected_numbers:
                        missing = set(expected_numbers) - set(lesson_numbers)
                        if missing:
                            course_status["issues"].append(f"缺少课时序号: {missing}")

                    # 检查每个课时内容
                    for lesson in course_lessons:
                        if not lesson.title:
                            course_status["issues"].append(f"课时{lesson.lesson_number}标题为空")
                        if not lesson.content or len(lesson.content) < 50:
                            course_status["issues"].append(f"课时{lesson.lesson_number}内容过少")

                    if course_status["issues"]:
                        self.verification_results["lessons"]["failed"] += 1
                    else:
                        self.verification_results["lessons"]["passed"] += 1

                    details.append(course_status)

                return {
                    "status": "passed" if self.verification_results["lessons"]["failed"] == 0 else "warning",
                    "count": lesson_count,
                    "details": details
                }

            except Exception as e:
                console.print(f"[red]课时验证出错: {e}[/red]")
                return {"status": "error", "error": str(e)}

    async def verify_exercises(self) -> Dict[str, Any]:
        """验证练习数据"""
        async with self.session_factory() as session:
            try:
                # 获取所有练习
                result = await session.execute(select(CourseExercise))
                exercises = result.scalars().all()

                exercise_count = len(exercises)
                self.verification_results["exercises"]["count"] = exercise_count

                if exercise_count == 0:
                    self.verification_results["exercises"]["warnings"].append("没有找到任何练习数据")
                    return {"status": "warning", "count": 0, "details": []}

                # 统计各类型练习
                type_stats = {}
                difficulty_stats = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
                issues = []

                for exercise in exercises:
                    # 统计类型
                    ex_type = exercise.exercise_type or "unknown"
                    type_stats[ex_type] = type_stats.get(ex_type, 0) + 1

                    # 统计难度
                    diff = exercise.difficulty_level
                    if 1 <= diff <= 5:
                        difficulty_stats[diff] += 1

                    # 验证内容
                    if not exercise.question or len(exercise.question) < 10:
                        issues.append(f"练习{exercise.exercise_number}题目内容过短")
                    if not exercise.title:
                        issues.append(f"练习{exercise.exercise_number}标题为空")

                if issues:
                    self.verification_results["exercises"]["failed"] += len(issues)
                    self.verification_results["exercises"]["warnings"].extend(issues[:10])  # 只显示前10个问题
                else:
                    self.verification_results["exercises"]["passed"] = exercise_count

                return {
                    "status": "passed" if not issues else "warning",
                    "count": exercise_count,
                    "type_stats": type_stats,
                    "difficulty_stats": difficulty_stats,
                    "issues": issues[:10]
                }

            except Exception as e:
                console.print(f"[red]练习验证出错: {e}[/red]")
                return {"status": "error", "error": str(e)}

    async def verify_data_integrity(self) -> Dict[str, Any]:
        """验证数据完整性"""
        async with self.session_factory() as session:
            try:
                integrity_checks = []

                # 检查课程-课时关联
                orphan_lessons = await session.execute(
                    select(func.count(Lesson.id))
                    .where(~Lesson.course_id.in_(select(Course.id)))
                )
                orphan_lesson_count = orphan_lessons.scalar() or 0

                if orphan_lesson_count > 0:
                    integrity_checks.append(f"发现{orphan_lesson_count}个孤立课时（无关联课程）")

                # 检查课程-练习关联
                orphan_exercises = await session.execute(
                    select(func.count(CourseExercise.id))
                    .where(~CourseExercise.course_id.in_(select(Course.id)))
                )
                orphan_exercise_count = orphan_exercises.scalar() or 0

                if orphan_exercise_count > 0:
                    integrity_checks.append(f"发现{orphan_exercise_count}个孤立练习（无关联课程）")

                return {
                    "status": "passed" if not integrity_checks else "warning",
                    "integrity_issues": integrity_checks
                }

            except Exception as e:
                console.print(f"[red]数据完整性验证出错: {e}[/red]")
                return {"status": "error", "error": str(e)}

    def generate_report(self, results: Dict[str, Any]) -> None:
        """生成验证报告"""
        console.print("\n")
        console.print(Panel.fit(
            "[bold blue]课程数据导入验证报告[/bold blue]",
            border_style="blue"
        ))

        # 概览表格
        overview_table = Table(title="验证概览")
        overview_table.add_column("数据类型", style="cyan")
        overview_table.add_column("数量", style="green")
        overview_table.add_column("状态", style="yellow")

        course_status = "[green]通过[/green]" if results.get("courses", {}).get("status") == "passed" else "[yellow]警告[/yellow]"
        lesson_status = "[green]通过[/green]" if results.get("lessons", {}).get("status") == "passed" else "[yellow]警告[/yellow]"
        exercise_status = "[green]通过[/green]" if results.get("exercises", {}).get("status") == "passed" else "[yellow]警告[/yellow]"

        overview_table.add_row("课程", str(results.get("courses", {}).get("count", 0)), course_status)
        overview_table.add_row("课时", str(results.get("lessons", {}).get("count", 0)), lesson_status)
        overview_table.add_row("练习", str(results.get("exercises", {}).get("count", 0)), exercise_status)

        console.print(overview_table)

        # 练习类型统计
        if "exercises" in results and "type_stats" in results["exercises"]:
            type_table = Table(title="练习类型分布")
            type_table.add_column("类型", style="cyan")
            type_table.add_column("数量", style="green")

            for ex_type, count in results["exercises"]["type_stats"].items():
                type_table.add_row(ex_type, str(count))

            console.print(type_table)

        # 练习难度统计
        if "exercises" in results and "difficulty_stats" in results["exercises"]:
            diff_table = Table(title="练习难度分布")
            diff_table.add_column("难度", style="cyan")
            diff_table.add_column("数量", style="green")

            for diff, count in results["exercises"]["difficulty_stats"].items():
                diff_table.add_row(f"{'⭐' * diff}", str(count))

            console.print(diff_table)

        # 问题列表
        all_issues = []
        for category in ["courses", "lessons", "exercises"]:
            if category in results:
                if "issues" in results[category]:
                    all_issues.extend(results[category]["issues"])
                if "warnings" in self.verification_results[category]:
                    all_issues.extend(self.verification_results[category]["warnings"])

        if results.get("integrity", {}).get("integrity_issues"):
            all_issues.extend(results["integrity"]["integrity_issues"])

        if all_issues:
            console.print("\n[yellow]发现的问题:[/yellow]")
            for i, issue in enumerate(all_issues[:20], 1):
                console.print(f"  {i}. {issue}")
            if len(all_issues) > 20:
                console.print(f"  ... 还有 {len(all_issues) - 20} 个问题")

        # 总体状态
        overall_status = "PASSED"
        if any(r.get("status") == "error" for r in results.values() if isinstance(r, dict)):
            overall_status = "ERROR"
        elif any(r.get("status") == "warning" for r in results.values() if isinstance(r, dict)):
            overall_status = "WARNING"

        console.print("\n")
        if overall_status == "PASSED":
            console.print(Panel.fit("[bold green]✓ 验证通过[/bold green]", border_style="green"))
        elif overall_status == "WARNING":
            console.print(Panel.fit("[bold yellow]⚠ 验证通过（有警告）[/bold yellow]", border_style="yellow"))
        else:
            console.print(Panel.fit("[bold red]✗ 验证失败[/bold red]", border_style="red"))


async def main():
    """主函数"""
    console.print("\n[bold blue]🔍 开始验证课程数据导入...[/bold blue]\n")

    verifier = CurriculumVerifier()

    if not await verifier.connect():
        return False

    try:
        results = {}

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:

            # 验证课程
            task = progress.add_task("[cyan]验证课程数据...", total=None)
            results["courses"] = await verifier.verify_courses()
            progress.update(task, completed=True)

            # 验证课时
            task = progress.add_task("[cyan]验证课时数据...", total=None)
            results["lessons"] = await verifier.verify_lessons()
            progress.update(task, completed=True)

            # 验证练习
            task = progress.add_task("[cyan]验证练习数据...", total=None)
            results["exercises"] = await verifier.verify_exercises()
            progress.update(task, completed=True)

            # 验证数据完整性
            task = progress.add_task("[cyan]验证数据完整性...", total=None)
            results["integrity"] = await verifier.verify_data_integrity()
            progress.update(task, completed=True)

        # 生成报告
        verifier.generate_report(results)

        return True

    except Exception as e:
        console.print(f"\n[red]验证过程中发生错误: {e}[/red]")
        import traceback
        console.print(f"[dim]{traceback.format_exc()}[/dim]")
        return False

    finally:
        await verifier.disconnect()


if __name__ == "__main__":
    result = asyncio.run(main())
    sys.exit(0 if result else 1)
