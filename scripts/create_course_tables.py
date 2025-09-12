#!/usr/bin/env python3
"""
Course Content Integration Database Migration
创建课程内容相关的数据表

Author: Product Manager Coordinator
Date: 2025-09-12
"""

import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database.database import db_manager
import asyncio

async def create_course_tables():
    """创建课程相关数据表"""
    try:
        print("开始创建课程相关数据表...")
        
        # 使用数据库管理器创建表
        await db_manager.create_tables()
        print("数据表创建完成")
        
        # 获取表信息验证
        table_info = await db_manager.get_table_info()
        
        # 检查新建的表
        tables_to_check = [
            'courses', 
            'lessons', 
            'course_exercises', 
            'lesson_exercises',
            'learning_paths',
            'student_exercise_attempts'
        ]
        
        print("\n📋 表创建验证结果:")
        for table in tables_to_check:
            if table in table_info:
                print(f"✅ 表 {table} 创建成功 (列数: {table_info[table]['columns']}, 行数: {table_info[table]['rows']})")
            else:
                print(f"❌ 表 {table} 创建失败")
        
        print("\n🎉 数据库课程表结构创建完成！")
        
        # 显示表结构信息
        print("\n📋 新增表结构概览:")
        print("1. courses - 课程表 (存储课程基本信息)")
        print("2. lessons - 课时表 (存储具体课时内容)")  
        print("3. course_exercises - 课程练习表 (存储练习题目)")
        print("4. lesson_exercises - 课时练习关联表")
        print("5. learning_paths - 学习路径表 (学生学习进度)")
        print("6. student_exercise_attempts - 学生练习尝试记录表")
        
        return True
        
    except Exception as e:
        print(f"❌ 创建数据表失败: {str(e)}")
        import traceback
        print(traceback.format_exc())
        return False

if __name__ == "__main__":
    result = asyncio.run(create_course_tables())
    sys.exit(0 if result else 1)