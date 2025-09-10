"""
AI教学助手系统 - 数据库配置
配置SQLAlchemy异步数据库连接和会话管理

Author: AI Backend Architecture Expert
Date: 2025-09-10
"""

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.pool import StaticPool
from typing import AsyncGenerator
import logging

from ..core.config import settings

logger = logging.getLogger(__name__)

# 创建异步数据库引擎
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DATABASE_ECHO,
    pool_size=settings.DATABASE_POOL_SIZE,
    max_overflow=settings.DATABASE_MAX_OVERFLOW,
    pool_pre_ping=True,  # 验证连接有效性
    pool_recycle=3600,   # 1小时后回收连接
    connect_args={
        "server_settings": {
            "application_name": "ai_teaching_assistant",
        }
    } if "postgresql" in settings.DATABASE_URL else {}
)

# 创建会话制造器
SessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=True,
    autocommit=False
)

# 创建基类
Base = declarative_base()


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    获取数据库会话依赖项
    
    用于FastAPI的依赖注入系统，确保每个请求都有独立的数据库会话，
    并在请求结束后正确关闭会话。
    """
    async with SessionLocal() as session:
        try:
            yield session
        except Exception as e:
            logger.error(f"Database session error: {str(e)}")
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_db():
    """
    初始化数据库
    
    创建所有表和初始数据
    """
    try:
        logger.info("Initializing database...")
        
        async with engine.begin() as conn:
            # 导入所有模型以确保它们被注册到Base.metadata
            from . import models
            
            # 创建所有表
            await conn.run_sync(Base.metadata.create_all)
            
        logger.info("Database initialized successfully")
        
    except Exception as e:
        logger.error(f"Database initialization failed: {str(e)}")
        raise


async def close_db():
    """
    关闭数据库连接
    
    在应用关闭时调用，确保所有连接被正确释放
    """
    try:
        logger.info("Closing database connections...")
        await engine.dispose()
        logger.info("Database connections closed")
    except Exception as e:
        logger.error(f"Error closing database connections: {str(e)}")


async def check_db_connection():
    """
    检查数据库连接状态
    
    Returns:
        bool: 连接是否正常
    """
    try:
        async with SessionLocal() as session:
            result = await session.execute("SELECT 1")
            return result.scalar() == 1
    except Exception as e:
        logger.error(f"Database connection check failed: {str(e)}")
        return False


# 数据库健康检查
async def db_health_check() -> dict:
    """
    数据库健康检查
    
    Returns:
        dict: 健康检查结果
    """
    try:
        start_time = time.time()
        
        async with SessionLocal() as session:
            # 执行简单查询测试连接
            await session.execute("SELECT 1")
            
            # 获取数据库版本信息
            version_result = await session.execute("SELECT version()")
            db_version = version_result.scalar()
            
            # 检查连接池状态
            pool_status = {
                "size": engine.pool.size(),
                "checked_in": engine.pool.checkedin(),
                "checked_out": engine.pool.checkedout(),
                "overflow": engine.pool.overflow(),
                "invalid": engine.pool.invalid()
            }
            
        response_time = (time.time() - start_time) * 1000  # 转换为毫秒
        
        return {
            "status": "healthy",
            "response_time_ms": round(response_time, 2),
            "database_version": db_version,
            "connection_pool": pool_status,
            "engine_url": str(engine.url).replace(engine.url.password or "", "****")
        }
        
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "response_time_ms": 0
        }


# 数据库事务装饰器
from functools import wraps
from typing import Callable, Any
import time


def db_transaction(func: Callable) -> Callable:
    """
    数据库事务装饰器
    
    自动处理数据库事务的提交和回滚
    """
    @wraps(func)
    async def wrapper(*args, **kwargs) -> Any:
        # 查找AsyncSession参数
        session = None
        for arg in args:
            if isinstance(arg, AsyncSession):
                session = arg
                break
        
        if not session:
            for key, value in kwargs.items():
                if isinstance(value, AsyncSession):
                    session = value
                    break
        
        if not session:
            raise ValueError("No AsyncSession found in function arguments")
        
        try:
            result = await func(*args, **kwargs)
            await session.commit()
            return result
        except Exception as e:
            await session.rollback()
            logger.error(f"Transaction failed in {func.__name__}: {str(e)}")
            raise
    
    return wrapper


class DatabaseManager:
    """
    数据库管理器
    
    提供数据库连接管理、健康检查、统计信息等功能
    """
    
    def __init__(self):
        self.engine = engine
        self.session_factory = SessionLocal
        
    async def create_tables(self):
        """创建所有数据表"""
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
    
    async def drop_tables(self):
        """删除所有数据表（谨慎使用）"""
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
    
    async def get_table_info(self) -> dict:
        """获取数据表信息"""
        try:
            async with self.session_factory() as session:
                # 获取表列表和行数统计
                tables_query = """
                SELECT 
                    table_name,
                    (SELECT COUNT(*) FROM information_schema.columns 
                     WHERE table_name = t.table_name) as column_count
                FROM information_schema.tables t
                WHERE table_schema = 'public' AND table_type = 'BASE TABLE'
                ORDER BY table_name;
                """
                
                result = await session.execute(tables_query)
                tables = result.fetchall()
                
                table_info = {}
                for table in tables:
                    # 获取每个表的行数
                    count_result = await session.execute(
                        f"SELECT COUNT(*) FROM {table.table_name}"
                    )
                    row_count = count_result.scalar()
                    
                    table_info[table.table_name] = {
                        "columns": table.column_count,
                        "rows": row_count
                    }
                
                return table_info
                
        except Exception as e:
            logger.error(f"Failed to get table info: {str(e)}")
            return {}
    
    async def execute_raw_query(self, query: str, params: dict = None):
        """执行原生SQL查询"""
        async with self.session_factory() as session:
            result = await session.execute(query, params or {})
            await session.commit()
            return result
    
    async def backup_database(self, backup_path: str = None):
        """数据库备份（PostgreSQL）"""
        if "postgresql" not in settings.DATABASE_URL:
            raise NotImplementedError("Backup only supported for PostgreSQL")
        
        import subprocess
        import os
        from urllib.parse import urlparse
        
        # 解析数据库URL
        parsed = urlparse(settings.DATABASE_URL.replace("postgresql+asyncpg://", "postgresql://"))
        
        backup_path = backup_path or f"backup_{int(time.time())}.sql"
        
        env = os.environ.copy()
        env['PGPASSWORD'] = parsed.password
        
        cmd = [
            'pg_dump',
            '-h', parsed.hostname,
            '-p', str(parsed.port or 5432),
            '-U', parsed.username,
            '-d', parsed.path.lstrip('/'),
            '-f', backup_path,
            '--no-password'
        ]
        
        try:
            subprocess.run(cmd, env=env, check=True)
            logger.info(f"Database backup created: {backup_path}")
            return backup_path
        except subprocess.CalledProcessError as e:
            logger.error(f"Database backup failed: {str(e)}")
            raise


# 全局数据库管理器实例
db_manager = DatabaseManager()


# 数据库连接池监控
class ConnectionPoolMonitor:
    """连接池监控器"""
    
    @staticmethod
    def get_pool_stats() -> dict:
        """获取连接池统计信息"""
        pool = engine.pool
        return {
            "pool_size": pool.size(),
            "checked_in_connections": pool.checkedin(),
            "checked_out_connections": pool.checkedout(),
            "overflow_connections": pool.overflow(),
            "invalid_connections": pool.invalid(),
            "total_connections": pool.size() + pool.overflow()
        }
    
    @staticmethod
    def log_pool_stats():
        """记录连接池状态到日志"""
        stats = ConnectionPoolMonitor.get_pool_stats()
        logger.info(f"Connection Pool Stats: {stats}")


# 导出主要组件
__all__ = [
    "Base",
    "engine", 
    "SessionLocal",
    "get_db",
    "init_db",
    "close_db",
    "check_db_connection",
    "db_health_check",
    "db_transaction",
    "db_manager",
    "ConnectionPoolMonitor"
]