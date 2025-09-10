#!/usr/bin/env python3
"""
AI Teaching Assistant System - Database Management Script
数据库管理和维护脚本
"""

import asyncio
import os
import sys
from pathlib import Path
from typing import Optional
import click
import asyncpg
from loguru import logger

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# 数据库连接配置
DEFAULT_DB_CONFIG = {
    "host": "localhost",
    "port": 5432,
    "user": "ai_teacher",
    "password": "dev_password_123",
    "database": "ai_teacher_dev"
}

TEST_DB_CONFIG = {
    "host": "localhost", 
    "port": 5432,
    "user": "ai_teacher",
    "password": "dev_password_123",
    "database": "ai_teacher_test"
}

class DatabaseManager:
    """数据库管理器"""
    
    def __init__(self, config: dict):
        self.config = config
        
    async def get_connection(self) -> asyncpg.Connection:
        """获取数据库连接"""
        try:
            conn = await asyncpg.connect(**self.config)
            return conn
        except Exception as e:
            logger.error(f"Failed to connect to database: {e}")
            raise
    
    async def check_connection(self) -> bool:
        """检查数据库连接"""
        try:
            conn = await self.get_connection()
            result = await conn.fetchval("SELECT 1")
            await conn.close()
            return result == 1
        except Exception as e:
            logger.error(f"Database connection check failed: {e}")
            return False
    
    async def create_database(self, db_name: str) -> bool:
        """创建数据库"""
        try:
            # 连接到默认postgres数据库
            config = self.config.copy()
            config["database"] = "postgres"
            conn = await asyncpg.connect(**config)
            
            # 检查数据库是否存在
            exists = await conn.fetchval(
                "SELECT 1 FROM pg_database WHERE datname = $1", db_name
            )
            
            if not exists:
                await conn.execute(f"CREATE DATABASE {db_name}")
                logger.info(f"Database '{db_name}' created successfully")
            else:
                logger.info(f"Database '{db_name}' already exists")
                
            await conn.close()
            return True
            
        except Exception as e:
            logger.error(f"Failed to create database '{db_name}': {e}")
            return False
    
    async def drop_database(self, db_name: str) -> bool:
        """删除数据库"""
        try:
            # 连接到默认postgres数据库
            config = self.config.copy()
            config["database"] = "postgres"
            conn = await asyncpg.connect(**config)
            
            # 终止所有连接到目标数据库的会话
            await conn.execute(
                """
                SELECT pg_terminate_backend(pid)
                FROM pg_stat_activity
                WHERE datname = $1 AND pid <> pg_backend_pid()
                """, 
                db_name
            )
            
            # 删除数据库
            await conn.execute(f"DROP DATABASE IF EXISTS {db_name}")
            logger.info(f"Database '{db_name}' dropped successfully")
            
            await conn.close()
            return True
            
        except Exception as e:
            logger.error(f"Failed to drop database '{db_name}': {e}")
            return False
    
    async def reset_database(self) -> bool:
        """重置数据库"""
        try:
            db_name = self.config["database"]
            
            # 删除并重新创建数据库
            await self.drop_database(db_name)
            await self.create_database(db_name)
            
            # 运行初始化脚本
            await self.run_init_script()
            
            logger.info(f"Database '{db_name}' reset successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to reset database: {e}")
            return False
    
    async def run_init_script(self) -> bool:
        """运行初始化脚本"""
        try:
            init_script_path = project_root / "scripts" / "init-db.sql"
            
            if not init_script_path.exists():
                logger.error(f"Init script not found: {init_script_path}")
                return False
            
            # 读取并执行初始化脚本
            with open(init_script_path, 'r', encoding='utf-8') as f:
                script_content = f.read()
            
            conn = await self.get_connection()
            await conn.execute(script_content)
            await conn.close()
            
            logger.info("Database initialization script executed successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to run init script: {e}")
            return False
    
    async def backup_database(self, backup_path: Optional[str] = None) -> bool:
        """备份数据库"""
        try:
            if not backup_path:
                backup_dir = project_root / "backups"
                backup_dir.mkdir(exist_ok=True)
                from datetime import datetime
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                backup_path = backup_dir / f"backup_{self.config['database']}_{timestamp}.sql"
            
            # 使用pg_dump进行备份
            import subprocess
            
            env = os.environ.copy()
            env["PGPASSWORD"] = self.config["password"]
            
            cmd = [
                "pg_dump",
                "-h", self.config["host"],
                "-p", str(self.config["port"]),
                "-U", self.config["user"],
                "-d", self.config["database"],
                "-f", str(backup_path)
            ]
            
            result = subprocess.run(cmd, env=env, capture_output=True, text=True)
            
            if result.returncode == 0:
                logger.info(f"Database backup created: {backup_path}")
                return True
            else:
                logger.error(f"Backup failed: {result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to backup database: {e}")
            return False
    
    async def get_database_info(self) -> dict:
        """获取数据库信息"""
        try:
            conn = await self.get_connection()
            
            # 获取数据库版本
            version = await conn.fetchval("SELECT version()")
            
            # 获取表信息
            tables = await conn.fetch(
                """
                SELECT table_name, 
                       pg_total_relation_size(quote_ident(table_name)) as size
                FROM information_schema.tables 
                WHERE table_schema = 'public' 
                ORDER BY table_name
                """
            )
            
            # 获取数据库大小
            db_size = await conn.fetchval(
                "SELECT pg_size_pretty(pg_database_size($1))",
                self.config["database"]
            )
            
            await conn.close()
            
            return {
                "version": version,
                "database": self.config["database"],
                "size": db_size,
                "tables": [dict(row) for row in tables]
            }
            
        except Exception as e:
            logger.error(f"Failed to get database info: {e}")
            return {}

@click.group()
def cli():
    """AI Teaching Assistant System Database Management CLI"""
    pass

@cli.command()
@click.option('--env', default='dev', help='Environment: dev or test')
def check(env):
    """检查数据库连接"""
    config = DEFAULT_DB_CONFIG if env == 'dev' else TEST_DB_CONFIG
    db_manager = DatabaseManager(config)
    
    async def _check():
        is_connected = await db_manager.check_connection()
        if is_connected:
            logger.info(f"✅ Database connection successful ({env} environment)")
            info = await db_manager.get_database_info()
            if info:
                logger.info(f"Database: {info['database']}")
                logger.info(f"Size: {info['size']}")
                logger.info(f"Tables: {len(info['tables'])}")
        else:
            logger.error(f"❌ Database connection failed ({env} environment)")
    
    asyncio.run(_check())

@cli.command()
@click.option('--env', default='dev', help='Environment: dev or test')
def reset(env):
    """重置数据库"""
    config = DEFAULT_DB_CONFIG if env == 'dev' else TEST_DB_CONFIG
    db_manager = DatabaseManager(config)
    
    if click.confirm(f"Are you sure you want to reset the {env} database? This will delete all data."):
        async def _reset():
            success = await db_manager.reset_database()
            if success:
                logger.info(f"✅ Database reset successful ({env} environment)")
            else:
                logger.error(f"❌ Database reset failed ({env} environment)")
        
        asyncio.run(_reset())

@cli.command()
@click.option('--env', default='dev', help='Environment: dev or test')
@click.option('--path', help='Backup file path')
def backup(env, path):
    """备份数据库"""
    config = DEFAULT_DB_CONFIG if env == 'dev' else TEST_DB_CONFIG
    db_manager = DatabaseManager(config)
    
    async def _backup():
        success = await db_manager.backup_database(path)
        if success:
            logger.info(f"✅ Database backup successful ({env} environment)")
        else:
            logger.error(f"❌ Database backup failed ({env} environment)")
    
    asyncio.run(_backup())

@cli.command()
@click.option('--env', default='dev', help='Environment: dev or test')
def info(env):
    """显示数据库信息"""
    config = DEFAULT_DB_CONFIG if env == 'dev' else TEST_DB_CONFIG
    db_manager = DatabaseManager(config)
    
    async def _info():
        info = await db_manager.get_database_info()
        if info:
            click.echo(f"\n🗄️  Database Information ({env} environment)")
            click.echo("=" * 50)
            click.echo(f"Database: {info['database']}")
            click.echo(f"Size: {info['size']}")
            click.echo(f"Version: {info['version']}")
            click.echo(f"\n📊 Tables ({len(info['tables'])}):")
            for table in info['tables']:
                size_mb = table['size'] / 1024 / 1024 if table['size'] else 0
                click.echo(f"  • {table['table_name']}: {size_mb:.2f} MB")
        else:
            logger.error("Failed to get database information")
    
    asyncio.run(_info())

@cli.command()
@click.option('--env', default='dev', help='Environment: dev or test')
def init(env):
    """初始化数据库"""
    config = DEFAULT_DB_CONFIG if env == 'dev' else TEST_DB_CONFIG
    db_manager = DatabaseManager(config)
    
    async def _init():
        success = await db_manager.run_init_script()
        if success:
            logger.info(f"✅ Database initialization successful ({env} environment)")
        else:
            logger.error(f"❌ Database initialization failed ({env} environment)")
    
    asyncio.run(_init())

if __name__ == "__main__":
    cli()