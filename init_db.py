"""
AI教学助手系统 - 数据库初始化脚本
用于创建数据库表和初始数据

Author: AI Backend Architecture Expert
Date: 2025-09-10
"""

import asyncio
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from app.database.database import engine, init_db, Base
from app.database.models import User
from app.core.security import create_password_hash, UserRole
from app.core.config import settings
from app.utils.logger import setup_logging, get_logger

# 设置日志
setup_logging()
logger = get_logger(__name__)


async def create_admin_user():
    """创建默认管理员用户"""
    from app.database.database import SessionLocal
    
    async with SessionLocal() as session:
        try:
            # 检查是否已存在管理员用户
            from sqlalchemy import select
            result = await session.execute(
                select(User).where(User.role == UserRole.ADMIN.value).limit(1)
            )
            existing_admin = result.scalar_one_or_none()
            
            if existing_admin:
                logger.info("Admin user already exists")
                return
            
            # 创建默认管理员用户
            admin_user = User(
                username="admin",
                email="admin@aiteacher.local",
                hashed_password=create_password_hash("admin123456"),
                full_name="系统管理员",
                role=UserRole.ADMIN.value,
                is_active=True
            )
            
            session.add(admin_user)
            await session.commit()
            
            logger.info("Default admin user created successfully")
            logger.info("Username: admin")
            logger.info("Password: admin123456")
            logger.info("Email: admin@aiteacher.local")
            
        except Exception as e:
            logger.error(f"Failed to create admin user: {str(e)}")
            await session.rollback()
            raise


async def create_sample_data():
    """创建示例数据"""
    from app.database.database import SessionLocal
    
    async with SessionLocal() as session:
        try:
            # 创建示例教师用户
            teacher_user = User(
                username="teacher1",
                email="teacher@aiteacher.local",
                hashed_password=create_password_hash("teacher123"),
                full_name="张教师",
                role=UserRole.TEACHER.value,
                is_active=True
            )
            
            # 创建示例学生用户
            student_user = User(
                username="student1",
                email="student@aiteacher.local",
                hashed_password=create_password_hash("student123"),
                full_name="李同学",
                role=UserRole.STUDENT.value,
                is_active=True
            )
            
            session.add_all([teacher_user, student_user])
            await session.commit()
            
            logger.info("Sample users created successfully")
            logger.info("Teacher - Username: teacher1, Password: teacher123")
            logger.info("Student - Username: student1, Password: student123")
            
        except Exception as e:
            logger.error(f"Failed to create sample data: {str(e)}")
            await session.rollback()


async def main():
    """主函数"""
    try:
        logger.info("Starting database initialization...")
        
        # 初始化数据库
        await init_db()
        logger.info("Database tables created successfully")
        
        # 创建管理员用户
        await create_admin_user()
        
        # 创建示例数据（仅在开发环境）
        if settings.ENVIRONMENT == "development":
            await create_sample_data()
        
        logger.info("Database initialization completed successfully")
        
    except Exception as e:
        logger.error(f"Database initialization failed: {str(e)}")
        raise


if __name__ == "__main__":
    asyncio.run(main())