"""
AI教学助手系统 - 数据库优化模块 (Sprint 5)
提供数据库查询优化、索引管理和性能监控

Author: AI Backend Architecture Expert
Date: Sprint 5
"""

import time
import asyncio
from typing import Dict, List, Any, Optional, TypeVar, Generic
from functools import wraps
from contextlib import asynccontextmanager
from sqlalchemy import text, Index, inspect
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload, joinedload, Query

from ..core.metrics import (
    db_query_duration_seconds,
    db_query_errors_total,
    db_connections_active,
    db_connections_idle,
    db_pool_size,
    record_db_query,
    update_db_pool_stats,
)
from ..utils.structured_logging import get_structured_logger

logger = get_structured_logger(__name__)


# ============= 索引定义 =============

# 推荐的索引列表
RECOMMENDED_INDEXES = [
    # 提交表索引
    {
        "name": "idx_submissions_user_created",
        "table": "submissions",
        "columns": ["user_id", "created_at DESC"],
        "description": "优化用户提交历史查询"
    },
    {
        "name": "idx_submissions_assignment_status",
        "table": "submissions",
        "columns": ["assignment_id", "status"],
        "description": "优化作业提交状态查询"
    },
    {
        "name": "idx_submissions_created",
        "table": "submissions",
        "columns": ["created_at DESC"],
        "description": "优化按时间排序查询"
    },

    # AI反馈表索引
    {
        "name": "idx_ai_feedback_submission",
        "table": "ai_feedback",
        "columns": ["submission_id"],
        "description": "优化提交-反馈关联查询"
    },
    {
        "name": "idx_ai_feedback_created",
        "table": "ai_feedback",
        "columns": ["created_at DESC"],
        "description": "优化反馈时间排序"
    },

    # 用户表索引
    {
        "name": "idx_users_email",
        "table": "users",
        "columns": ["email"],
        "description": "优化邮箱查询（登录）",
        "unique": True
    },
    {
        "name": "idx_users_role",
        "table": "users",
        "columns": ["role"],
        "description": "优化角色筛选"
    },

    # 学习进度索引
    {
        "name": "idx_learning_progress_student_course",
        "table": "learning_progress",
        "columns": ["student_id", "course_id"],
        "description": "优化学生课程进度查询"
    },
    {
        "name": "idx_learning_progress_updated",
        "table": "learning_progress",
        "columns": ["updated_at DESC"],
        "description": "优化进度更新时间查询"
    },

    # 课程表索引
    {
        "name": "idx_courses_teacher",
        "table": "courses",
        "columns": ["teacher_id"],
        "description": "优化教师课程查询"
    },
    {
        "name": "idx_courses_status",
        "table": "courses",
        "columns": ["status", "start_date"],
        "description": "优化课程状态筛选"
    },

    # 作业表索引
    {
        "name": "idx_assignments_course_due",
        "table": "assignments",
        "columns": ["course_id", "due_date"],
        "description": "优化课程作业查询"
    },

    # 练习表索引
    {
        "name": "idx_exercises_chapter_order",
        "table": "exercises",
        "columns": ["chapter_id", "order_index"],
        "description": "优化章节练习排序查询"
    },
]


async def create_indexes(session: AsyncSession, indexes: List[Dict] = None) -> Dict[str, Any]:
    """
    创建数据库索引

    Args:
        session: 数据库会话
        indexes: 索引定义列表，默认使用RECOMMENDED_INDEXES

    Returns:
        创建结果统计
    """
    if indexes is None:
        indexes = RECOMMENDED_INDEXES

    results = {
        "created": [],
        "existing": [],
        "failed": []
    }

    for idx_def in indexes:
        try:
            # 检查索引是否已存在
            check_sql = text(f"""
                SELECT 1 FROM pg_indexes
                WHERE indexname = :name
            """)
            result = await session.execute(check_sql, {"name": idx_def["name"]})

            if result.fetchone():
                results["existing"].append(idx_def["name"])
                logger.info(f"Index already exists: {idx_def['name']}")
                continue

            # 构建CREATE INDEX语句
            unique = "UNIQUE " if idx_def.get("unique") else ""
            columns = ", ".join(idx_def["columns"])
            create_sql = text(f"""
                CREATE {unique}INDEX {idx_def['name']}
                ON {idx_def['table']} ({columns})
            """)

            await session.execute(create_sql)
            await session.commit()

            results["created"].append(idx_def["name"])
            logger.info(f"Created index: {idx_def['name']} - {idx_def['description']}")

        except Exception as e:
            results["failed"].append({"name": idx_def["name"], "error": str(e)})
            logger.error(f"Failed to create index {idx_def['name']}: {e}")
            await session.rollback()

    return results


async def analyze_tables(session: AsyncSession, tables: List[str] = None) -> Dict[str, Any]:
    """
    分析表统计信息以优化查询计划

    Args:
        session: 数据库会话
        tables: 要分析的表列表
    """
    if tables is None:
        tables = ["submissions", "ai_feedback", "users", "courses", "assignments"]

    results = {}

    for table in tables:
        try:
            await session.execute(text(f"ANALYZE {table}"))
            results[table] = "analyzed"
            logger.info(f"Analyzed table: {table}")
        except Exception as e:
            results[table] = f"error: {e}"
            logger.error(f"Failed to analyze table {table}: {e}")

    return results


# ============= 查询优化工具 =============

def track_query_time(operation: str, table: str):
    """
    追踪数据库查询时间的装饰器

    Usage:
        @track_query_time("select", "submissions")
        async def get_submissions(...):
            ...
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            start_time = time.time()
            error = None

            try:
                result = await func(*args, **kwargs)
                return result
            except Exception as e:
                error = type(e).__name__
                raise
            finally:
                duration = time.time() - start_time

                # 记录到Prometheus
                db_query_duration_seconds.labels(
                    operation=operation,
                    table=table
                ).observe(duration)

                if error:
                    db_query_errors_total.labels(
                        operation=operation,
                        error_type=error
                    ).inc()

                # 记录到日志
                record_db_query(operation, table, duration, error)

        return wrapper
    return decorator


@asynccontextmanager
async def query_timer(operation: str, table: str):
    """
    查询计时上下文管理器

    Usage:
        async with query_timer("select", "submissions"):
            result = await session.execute(query)
    """
    start_time = time.time()
    error = None

    try:
        yield
    except Exception as e:
        error = type(e).__name__
        raise
    finally:
        duration = time.time() - start_time

        db_query_duration_seconds.labels(
            operation=operation,
            table=table
        ).observe(duration)

        if error:
            db_query_errors_total.labels(
                operation=operation,
                error_type=error
            ).inc()

        record_db_query(operation, table, duration, error)


class QueryBuilder:
    """
    查询构建器，提供优化的查询构建方法
    """

    @staticmethod
    def with_eager_loading(query, *relationships):
        """
        添加预加载关系（避免N+1问题）

        Usage:
            query = QueryBuilder.with_eager_loading(
                select(Submission),
                Submission.ai_feedback,
                Submission.user
            )
        """
        for rel in relationships:
            query = query.options(selectinload(rel))
        return query

    @staticmethod
    def with_joined_loading(query, *relationships):
        """
        添加联合加载关系

        Usage:
            query = QueryBuilder.with_joined_loading(
                select(Submission),
                Submission.assignment
            )
        """
        for rel in relationships:
            query = query.options(joinedload(rel))
        return query

    @staticmethod
    def paginate(query, page: int, page_size: int):
        """
        添加分页

        Usage:
            query = QueryBuilder.paginate(query, page=1, page_size=20)
        """
        offset = (page - 1) * page_size
        return query.offset(offset).limit(page_size)


# ============= 连接池监控 =============

async def get_pool_stats(engine) -> Dict[str, int]:
    """
    获取连接池统计信息

    Returns:
        包含active, idle, pool_size的字典
    """
    pool = engine.pool

    stats = {
        "active": pool.checkedout(),
        "idle": pool.checkedin(),
        "pool_size": pool.size(),
        "overflow": pool.overflow(),
    }

    # 更新Prometheus指标
    update_db_pool_stats(
        active=stats["active"],
        idle=stats["idle"],
        pool_size=stats["pool_size"]
    )

    return stats


async def monitor_pool_stats(engine, interval: int = 30):
    """
    定期监控连接池状态

    Args:
        engine: 数据库引擎
        interval: 监控间隔（秒）
    """
    while True:
        try:
            stats = await get_pool_stats(engine)
            logger.debug(
                f"DB Pool Stats - Active: {stats['active']}, "
                f"Idle: {stats['idle']}, Size: {stats['pool_size']}"
            )
        except Exception as e:
            logger.error(f"Failed to get pool stats: {e}")

        await asyncio.sleep(interval)


# ============= 查询分析工具 =============

async def explain_query(session: AsyncSession, query_sql: str) -> List[Dict]:
    """
    分析查询执行计划

    Args:
        session: 数据库会话
        query_sql: SQL查询语句

    Returns:
        执行计划列表
    """
    try:
        result = await session.execute(
            text(f"EXPLAIN ANALYZE {query_sql}")
        )
        return [{"plan": row[0]} for row in result.fetchall()]
    except Exception as e:
        logger.error(f"Failed to explain query: {e}")
        return []


async def get_slow_queries(session: AsyncSession, min_duration_ms: float = 100) -> List[Dict]:
    """
    获取慢查询（需要pg_stat_statements扩展）

    Args:
        session: 数据库会话
        min_duration_ms: 最小执行时间阈值（毫秒）

    Returns:
        慢查询列表
    """
    try:
        result = await session.execute(text("""
            SELECT
                query,
                calls,
                total_exec_time,
                mean_exec_time,
                rows
            FROM pg_stat_statements
            WHERE mean_exec_time > :min_duration
            ORDER BY mean_exec_time DESC
            LIMIT 20
        """), {"min_duration": min_duration_ms})

        return [
            {
                "query": row[0],
                "calls": row[1],
                "total_time_ms": row[2],
                "mean_time_ms": row[3],
                "rows": row[4]
            }
            for row in result.fetchall()
        ]
    except Exception as e:
        logger.warning(f"Failed to get slow queries (pg_stat_statements might not be enabled): {e}")
        return []


# ============= 数据库健康检查 =============

async def health_check(session: AsyncSession) -> Dict[str, Any]:
    """
    数据库健康检查

    Returns:
        健康状态信息
    """
    health = {
        "status": "healthy",
        "checks": {}
    }

    # 检查连接
    try:
        start = time.time()
        await session.execute(text("SELECT 1"))
        health["checks"]["connection"] = {
            "status": "ok",
            "latency_ms": (time.time() - start) * 1000
        }
    except Exception as e:
        health["status"] = "unhealthy"
        health["checks"]["connection"] = {
            "status": "error",
            "error": str(e)
        }

    # 检查表是否存在
    try:
        result = await session.execute(text("""
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = 'public'
        """))
        tables = [row[0] for row in result.fetchall()]
        health["checks"]["tables"] = {
            "status": "ok",
            "count": len(tables)
        }
    except Exception as e:
        health["checks"]["tables"] = {
            "status": "error",
            "error": str(e)
        }

    return health
