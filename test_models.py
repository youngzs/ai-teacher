#!/usr/bin/env python3
"""
测试数据库模型是否正确
使用SQLite快速验证模型定义
"""

import asyncio
import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.sql import text

# 设置SQLite数据库URL以避免PostgreSQL连接问题
test_db_url = "sqlite+aiosqlite:///./test.db"

# 导入模型
from app.database.models import Base

async def test_models():
    """测试模型创建"""
    # 删除现有测试数据库
    if os.path.exists("./test.db"):
        os.remove("./test.db")
    
    # 创建测试引擎
    engine = create_async_engine(test_db_url, echo=True)
    
    try:
        # 创建所有表
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        
        print("✅ 所有模型创建成功！")
        
        # 测试简单查询
        SessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
        async with SessionLocal() as session:
            result = await session.execute(text("SELECT name FROM sqlite_master WHERE type='table'"))
            tables = result.fetchall()
            print(f"✅ 创建的表: {[table[0] for table in tables]}")
            
    except Exception as e:
        print(f"❌ 模型创建失败: {e}")
        return False
    finally:
        await engine.dispose()
    
    return True

if __name__ == "__main__":
    success = asyncio.run(test_models())
    if success:
        print("✅ 数据库模型验证通过")
        # 清理测试文件
        if os.path.exists("./test.db"):
            os.remove("./test.db")
    else:
        print("❌ 数据库模型验证失败")
        exit(1)