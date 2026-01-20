#!/usr/bin/env python3
"""
数据库初始化脚本 - Sprint 3
完整的数据库初始化、表创建和验证

Author: AI Teaching Assistant Team
Date: 2026-01-19
"""

import asyncio
import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn

console = Console()


async def main():
    """主初始化函数"""
    console.print("\n" + "=" * 60, style="bold blue")
    console.print("  AI Teaching Assistant - Database Initialization", style="bold white")
    console.print("=" * 60 + "\n", style="bold blue")

    # 延迟导入以确保环境变量已加载
    from app.database.database import (
        engine, Base, init_db, comprehensive_health_check, db_manager
    )
    from app.database import models  # 导入所有模型
    from app.core.config import settings

    success = True

    # Step 1: 健康检查
    console.print("[1/5] 检查数据库连接...", style="yellow")
    try:
        health = await comprehensive_health_check()

        if health["status"] == "healthy":
            console.print(f"  ✅ 数据库连接成功 (响应时间: {health['response_time_ms']}ms)", style="green")
            if health.get("database_info", {}).get("version"):
                console.print(f"  📊 数据库版本: {health['database_info']['version'][:50]}...", style="dim")
        else:
            console.print(f"  ❌ 数据库连接失败: {health.get('errors', ['Unknown error'])}", style="red")
            console.print(f"\n  连接URL: {settings.DATABASE_URL.split('@')[-1]}", style="dim")
            console.print("  请检查数据库是否运行并且配置正确。", style="yellow")
            return False

    except Exception as e:
        console.print(f"  ❌ 健康检查异常: {e}", style="red")
        success = False
        return False

    # Step 2: 创建数据表
    console.print("\n[2/5] 创建数据库表...", style="yellow")
    try:
        await init_db()
        console.print("  ✅ 数据表创建/更新完成", style="green")
    except Exception as e:
        console.print(f"  ❌ 表创建失败: {e}", style="red")
        success = False

    # Step 3: 验证表结构
    console.print("\n[3/5] 验证数据表结构...", style="yellow")
    try:
        table_info = await db_manager.get_table_info()

        expected_tables = [
            'users', 'classes', 'class_memberships', 'assignments',
            'submissions', 'ai_feedback', 'student_profiles',
            'teaching_sessions', 'courses', 'lessons',
            'course_exercises', 'learning_paths', 'lesson_exercises',
            'student_exercise_attempts', 'system_metrics', 'api_keys', 'audit_logs'
        ]

        existing_tables = list(table_info.keys())
        missing_tables = [t for t in expected_tables if t not in existing_tables]

        if missing_tables:
            console.print(f"  ⚠️  缺失的表: {', '.join(missing_tables)}", style="yellow")
        else:
            console.print(f"  ✅ 所有 {len(expected_tables)} 个预期表都已存在", style="green")

    except Exception as e:
        console.print(f"  ❌ 表结构验证失败: {e}", style="red")
        success = False

    # Step 4: 显示表统计
    console.print("\n[4/5] 数据表统计...", style="yellow")
    try:
        table = Table(title="数据表信息")
        table.add_column("表名", style="cyan")
        table.add_column("列数", justify="right")
        table.add_column("行数", justify="right", style="green")

        total_rows = 0
        for table_name, info in sorted(table_info.items()):
            table.add_row(table_name, str(info.get('columns', 0)), str(info.get('rows', 0)))
            total_rows += info.get('rows', 0)

        console.print(table)
        console.print(f"\n  📊 共 {len(table_info)} 个表，{total_rows} 条记录", style="dim")

    except Exception as e:
        console.print(f"  ⚠️  统计信息获取失败: {e}", style="yellow")

    # Step 5: 连接池状态
    console.print("\n[5/5] 连接池状态...", style="yellow")
    try:
        pool = engine.pool
        pool_stats = {
            "池大小": pool.size(),
            "已检入": pool.checkedin(),
            "已检出": pool.checkedout(),
            "溢出": pool.overflow(),
            "无效": pool.invalid()
        }

        for key, value in pool_stats.items():
            console.print(f"  • {key}: {value}", style="dim")

    except Exception as e:
        console.print(f"  ⚠️  连接池状态获取失败: {e}", style="yellow")

    # 总结
    console.print("\n" + "=" * 60, style="bold blue")
    if success:
        console.print("  ✅ 数据库初始化完成!", style="bold green")
    else:
        console.print("  ⚠️  初始化完成，但存在一些问题", style="bold yellow")
    console.print("=" * 60 + "\n", style="bold blue")

    return success


async def create_test_data():
    """创建测试数据"""
    from app.database.database import SessionLocal
    from app.database.models import User, Course
    from passlib.context import CryptContext
    import uuid

    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    console.print("\n创建测试数据...", style="yellow")

    async with SessionLocal() as session:
        try:
            # 检查是否已有管理员
            from sqlalchemy import select
            result = await session.execute(
                select(User).where(User.username == "admin")
            )
            admin = result.scalar_one_or_none()

            if not admin:
                # 创建管理员账号
                admin = User(
                    id=uuid.uuid4(),
                    username="admin",
                    email="admin@example.com",
                    hashed_password=pwd_context.hash("admin123"),
                    full_name="系统管理员",
                    role="admin",
                    is_active=True
                )
                session.add(admin)
                console.print("  ✅ 创建管理员账号: admin / admin123", style="green")

            # 检查是否已有测试教师
            result = await session.execute(
                select(User).where(User.username == "teacher1")
            )
            teacher = result.scalar_one_or_none()

            if not teacher:
                teacher = User(
                    id=uuid.uuid4(),
                    username="teacher1",
                    email="teacher1@example.com",
                    hashed_password=pwd_context.hash("teacher123"),
                    full_name="测试教师",
                    role="teacher",
                    is_active=True
                )
                session.add(teacher)
                console.print("  ✅ 创建测试教师: teacher1 / teacher123", style="green")

            # 检查是否已有测试学生
            result = await session.execute(
                select(User).where(User.username == "student1")
            )
            student = result.scalar_one_or_none()

            if not student:
                student = User(
                    id=uuid.uuid4(),
                    username="student1",
                    email="student1@example.com",
                    hashed_password=pwd_context.hash("student123"),
                    full_name="测试学生",
                    role="student",
                    is_active=True
                )
                session.add(student)
                console.print("  ✅ 创建测试学生: student1 / student123", style="green")

            await session.commit()
            console.print("  ✅ 测试数据创建完成", style="green")

        except Exception as e:
            console.print(f"  ❌ 测试数据创建失败: {e}", style="red")
            await session.rollback()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="数据库初始化脚本")
    parser.add_argument("--with-test-data", action="store_true", help="创建测试数据")
    args = parser.parse_args()

    result = asyncio.run(main())

    if result and args.with_test_data:
        asyncio.run(create_test_data())

    sys.exit(0 if result else 1)
