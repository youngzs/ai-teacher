#!/usr/bin/env python3
"""
AI Teaching Assistant System - Health Check Script
系统健康检查脚本
"""

import asyncio
import os
import sys
import json
import time
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any
import click
import aiohttp
import asyncpg
import redis
from loguru import logger

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

class HealthChecker:
    """系统健康检查器"""
    
    def __init__(self):
        self.checks = []
        self.results = {}
    
    def add_check(self, name: str, check_func, critical: bool = True):
        """添加健康检查项"""
        self.checks.append({
            'name': name,
            'func': check_func,
            'critical': critical
        })
    
    async def run_all_checks(self) -> Dict[str, Any]:
        """运行所有健康检查"""
        results = {
            'timestamp': datetime.now().isoformat(),
            'overall_status': 'healthy',
            'checks': {}
        }
        
        critical_failures = 0
        
        for check in self.checks:
            start_time = time.time()
            
            try:
                status, message, details = await check['func']()
                
                results['checks'][check['name']] = {
                    'status': status,
                    'message': message,
                    'details': details,
                    'critical': check['critical'],
                    'duration_ms': round((time.time() - start_time) * 1000, 2)
                }
                
                if status != 'healthy' and check['critical']:
                    critical_failures += 1
                    
            except Exception as e:
                results['checks'][check['name']] = {
                    'status': 'error',
                    'message': f'Health check failed: {str(e)}',
                    'details': {},
                    'critical': check['critical'],
                    'duration_ms': round((time.time() - start_time) * 1000, 2)
                }
                
                if check['critical']:
                    critical_failures += 1
        
        # 设置总体状态
        if critical_failures > 0:
            results['overall_status'] = 'unhealthy'
        elif any(check['status'] == 'warning' for check in results['checks'].values()):
            results['overall_status'] = 'warning'
        
        results['critical_failures'] = critical_failures
        results['total_checks'] = len(self.checks)
        
        return results

async def check_database() -> tuple:
    """检查数据库连接和状态"""
    try:
        config = {
            "host": os.getenv("DB_HOST", "localhost"),
            "port": int(os.getenv("DB_PORT", 5432)),
            "user": os.getenv("DB_USER", "ai_teacher"),
            "password": os.getenv("DB_PASSWORD", "dev_password_123"),
            "database": os.getenv("DB_NAME", "ai_teacher_dev")
        }
        
        conn = await asyncpg.connect(**config)
        
        # 基本连接测试
        version = await conn.fetchval("SELECT version()")
        
        # 检查表是否存在
        table_count = await conn.fetchval(
            "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public'"
        )
        
        # 检查数据库大小
        db_size = await conn.fetchval(
            "SELECT pg_size_pretty(pg_database_size($1))", config["database"]
        )
        
        # 检查活跃连接数
        active_connections = await conn.fetchval(
            "SELECT count(*) FROM pg_stat_activity WHERE state = 'active'"
        )
        
        await conn.close()
        
        details = {
            "version": version.split(" ")[1] if version else "unknown",
            "tables": table_count,
            "database_size": db_size,
            "active_connections": active_connections
        }
        
        return "healthy", f"Database connection successful ({table_count} tables)", details
        
    except Exception as e:
        return "error", f"Database connection failed: {str(e)}", {}

async def check_redis() -> tuple:
    """检查Redis连接和状态"""
    try:
        redis_url = os.getenv("REDIS_URL", "redis://:dev_redis_123@localhost:6379/0")
        
        r = redis.from_url(redis_url)
        
        # 基本连接测试
        r.ping()
        
        # 获取Redis信息
        info = r.info()
        
        # 检查内存使用
        used_memory = info.get('used_memory_human', 'unknown')
        max_memory = info.get('maxmemory_human', 'unlimited')
        
        # 检查连接数
        connected_clients = info.get('connected_clients', 0)
        
        details = {
            "version": info.get('redis_version', 'unknown'),
            "used_memory": used_memory,
            "max_memory": max_memory,
            "connected_clients": connected_clients,
            "total_commands_processed": info.get('total_commands_processed', 0)
        }
        
        return "healthy", "Redis connection successful", details
        
    except Exception as e:
        return "error", f"Redis connection failed: {str(e)}", {}

async def check_backend_api() -> tuple:
    """检查后端API服务"""
    try:
        backend_url = os.getenv("BACKEND_URL", "http://localhost:8000")
        
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=10)) as session:
            # 检查健康端点
            async with session.get(f"{backend_url}/health") as response:
                if response.status == 200:
                    data = await response.json()
                    
                    details = {
                        "status_code": response.status,
                        "response_time_ms": data.get("response_time", 0),
                        "version": data.get("version", "unknown"),
                        "environment": data.get("environment", "unknown")
                    }
                    
                    return "healthy", "Backend API is responding", details
                else:
                    return "warning", f"Backend API returned status {response.status}", {"status_code": response.status}
                    
    except aiohttp.ClientConnectorError:
        return "error", "Cannot connect to backend API", {}
    except asyncio.TimeoutError:
        return "warning", "Backend API response timeout", {}
    except Exception as e:
        return "error", f"Backend API check failed: {str(e)}", {}

async def check_disk_space() -> tuple:
    """检查磁盘空间"""
    try:
        import shutil
        
        # 检查项目目录磁盘空间
        total, used, free = shutil.disk_usage(project_root)
        
        # 转换为GB
        total_gb = total / (1024**3)
        used_gb = used / (1024**3)
        free_gb = free / (1024**3)
        
        # 计算使用百分比
        usage_percent = (used / total) * 100
        
        details = {
            "total_gb": round(total_gb, 2),
            "used_gb": round(used_gb, 2),
            "free_gb": round(free_gb, 2),
            "usage_percent": round(usage_percent, 2)
        }
        
        # 判断状态
        if usage_percent > 90:
            return "error", f"Disk usage critical: {usage_percent:.1f}%", details
        elif usage_percent > 80:
            return "warning", f"Disk usage high: {usage_percent:.1f}%", details
        else:
            return "healthy", f"Disk usage normal: {usage_percent:.1f}%", details
            
    except Exception as e:
        return "error", f"Disk space check failed: {str(e)}", {}

async def check_memory_usage() -> tuple:
    """检查内存使用情况"""
    try:
        import psutil
        
        # 获取系统内存信息
        memory = psutil.virtual_memory()
        
        details = {
            "total_gb": round(memory.total / (1024**3), 2),
            "available_gb": round(memory.available / (1024**3), 2),
            "used_gb": round(memory.used / (1024**3), 2),
            "usage_percent": memory.percent
        }
        
        # 判断状态
        if memory.percent > 90:
            return "error", f"Memory usage critical: {memory.percent}%", details
        elif memory.percent > 80:
            return "warning", f"Memory usage high: {memory.percent}%", details
        else:
            return "healthy", f"Memory usage normal: {memory.percent}%", details
            
    except ImportError:
        return "warning", "psutil not available for memory check", {}
    except Exception as e:
        return "error", f"Memory check failed: {str(e)}", {}

async def check_log_files() -> tuple:
    """检查日志文件状态"""
    try:
        log_dir = project_root / "logs"
        
        if not log_dir.exists():
            return "warning", "Log directory does not exist", {"log_dir": str(log_dir)}
        
        # 检查日志文件大小
        log_files = list(log_dir.glob("*.log"))
        total_size = sum(f.stat().st_size for f in log_files)
        
        # 检查最新日志文件的修改时间
        latest_log = None
        latest_time = 0
        
        for log_file in log_files:
            mtime = log_file.stat().st_mtime
            if mtime > latest_time:
                latest_time = mtime
                latest_log = log_file
        
        details = {
            "log_directory": str(log_dir),
            "log_files_count": len(log_files),
            "total_size_mb": round(total_size / (1024**2), 2),
            "latest_log": str(latest_log) if latest_log else None,
            "latest_modified": datetime.fromtimestamp(latest_time).isoformat() if latest_time > 0 else None
        }
        
        # 判断状态
        if total_size > 100 * 1024 * 1024:  # 100MB
            return "warning", f"Log files size large: {details['total_size_mb']} MB", details
        else:
            return "healthy", f"Log files normal: {len(log_files)} files, {details['total_size_mb']} MB", details
            
    except Exception as e:
        return "error", f"Log files check failed: {str(e)}", {}

@click.command()
@click.option('--output', '-o', type=click.Choice(['console', 'json']), default='console', help='Output format')
@click.option('--save', '-s', help='Save results to file')
def health_check(output, save):
    """Run system health checks"""
    
    async def run_checks():
        checker = HealthChecker()
        
        # 添加各种健康检查
        checker.add_check("database", check_database, critical=True)
        checker.add_check("redis", check_redis, critical=True)
        checker.add_check("backend_api", check_backend_api, critical=False)
        checker.add_check("disk_space", check_disk_space, critical=True)
        checker.add_check("memory_usage", check_memory_usage, critical=False)
        checker.add_check("log_files", check_log_files, critical=False)
        
        results = await checker.run_all_checks()
        
        # 输出结果
        if output == 'json':
            result_json = json.dumps(results, indent=2, ensure_ascii=False)
            click.echo(result_json)
        else:
            # 控制台输出
            status_emoji = {
                'healthy': '✅',
                'warning': '⚠️',
                'unhealthy': '❌'
            }
            
            click.echo(f"\n{status_emoji.get(results['overall_status'], '❓')} System Health Check Results")
            click.echo(f"Timestamp: {results['timestamp']}")
            click.echo(f"Overall Status: {results['overall_status'].upper()}")
            click.echo(f"Checks: {results['total_checks']}, Critical Failures: {results['critical_failures']}")
            click.echo("=" * 60)
            
            for check_name, check_result in results['checks'].items():
                status_icon = {
                    'healthy': '✅',
                    'warning': '⚠️',
                    'error': '❌'
                }.get(check_result['status'], '❓')
                
                critical_mark = ' [CRITICAL]' if check_result['critical'] else ''
                
                click.echo(f"\n{status_icon} {check_name.upper()}{critical_mark}")
                click.echo(f"   Status: {check_result['status']}")
                click.echo(f"   Message: {check_result['message']}")
                click.echo(f"   Duration: {check_result['duration_ms']}ms")
                
                if check_result['details']:
                    click.echo("   Details:")
                    for key, value in check_result['details'].items():
                        click.echo(f"     • {key}: {value}")
        
        # 保存结果到文件
        if save:
            save_path = Path(save)
            save_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(save_path, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, ensure_ascii=False)
            
            click.echo(f"\nResults saved to: {save_path}")
        
        # 根据结果设置退出码
        exit_code = 0 if results['overall_status'] == 'healthy' else 1
        sys.exit(exit_code)
    
    asyncio.run(run_checks())

if __name__ == "__main__":
    health_check()