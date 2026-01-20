"""
AI教学助手系统 - Prometheus监控指标 (Sprint 5)
提供系统监控指标收集和导出

Author: AI Backend Architecture Expert
Date: Sprint 5
"""

import time
from typing import Callable, Optional
from functools import wraps
from prometheus_client import (
    Counter,
    Histogram,
    Gauge,
    Info,
    CollectorRegistry,
    generate_latest,
    CONTENT_TYPE_LATEST,
    multiprocess,
)
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
import os

# 创建自定义注册表（支持多进程环境）
REGISTRY = CollectorRegistry()


# ============= HTTP请求指标 =============

http_requests_total = Counter(
    'http_requests_total',
    'Total number of HTTP requests',
    ['method', 'endpoint', 'status_code'],
    registry=REGISTRY,
)

http_request_duration_seconds = Histogram(
    'http_request_duration_seconds',
    'HTTP request duration in seconds',
    ['method', 'endpoint'],
    buckets=[0.005, 0.01, 0.025, 0.05, 0.075, 0.1, 0.25, 0.5, 0.75, 1.0, 2.5, 5.0, 7.5, 10.0],
    registry=REGISTRY,
)

http_request_size_bytes = Histogram(
    'http_request_size_bytes',
    'HTTP request size in bytes',
    ['method', 'endpoint'],
    buckets=[100, 500, 1000, 5000, 10000, 50000, 100000, 500000],
    registry=REGISTRY,
)

http_response_size_bytes = Histogram(
    'http_response_size_bytes',
    'HTTP response size in bytes',
    ['method', 'endpoint'],
    buckets=[100, 500, 1000, 5000, 10000, 50000, 100000, 500000, 1000000],
    registry=REGISTRY,
)

http_active_connections = Gauge(
    'http_active_connections',
    'Number of active HTTP connections',
    registry=REGISTRY,
)


# ============= AI服务指标 =============

ai_analysis_requests_total = Counter(
    'ai_analysis_requests_total',
    'Total number of AI analysis requests',
    ['analysis_type', 'language', 'status'],
    registry=REGISTRY,
)

ai_analysis_duration_seconds = Histogram(
    'ai_analysis_duration_seconds',
    'AI analysis duration in seconds',
    ['analysis_type', 'language'],
    buckets=[0.1, 0.25, 0.5, 1.0, 2.0, 3.0, 5.0, 10.0, 15.0, 30.0],
    registry=REGISTRY,
)

ai_api_calls_total = Counter(
    'ai_api_calls_total',
    'Total number of OpenAI API calls',
    ['model', 'endpoint'],
    registry=REGISTRY,
)

ai_api_cost_usd_total = Counter(
    'ai_api_cost_usd_total',
    'Total AI API cost in USD',
    ['model'],
    registry=REGISTRY,
)

ai_api_tokens_used_total = Counter(
    'ai_api_tokens_used_total',
    'Total tokens used by AI API',
    ['model', 'token_type'],  # token_type: prompt, completion
    registry=REGISTRY,
)

ai_cache_operations_total = Counter(
    'ai_cache_operations_total',
    'Total AI cache operations',
    ['operation'],  # operation: hit, miss, set
    registry=REGISTRY,
)


# ============= 代码执行指标 =============

code_execution_total = Counter(
    'code_execution_total',
    'Total number of code executions',
    ['language', 'status'],
    registry=REGISTRY,
)

code_execution_duration_seconds = Histogram(
    'code_execution_duration_seconds',
    'Code execution duration in seconds',
    ['language'],
    buckets=[0.1, 0.25, 0.5, 1.0, 2.0, 3.0, 5.0, 10.0, 15.0, 30.0],
    registry=REGISTRY,
)

code_compilation_errors_total = Counter(
    'code_compilation_errors_total',
    'Total number of compilation errors',
    ['language', 'error_type'],
    registry=REGISTRY,
)

code_test_results_total = Counter(
    'code_test_results_total',
    'Total number of test results',
    ['result'],  # result: passed, failed, error, timeout
    registry=REGISTRY,
)


# ============= 数据库指标 =============

db_connections_active = Gauge(
    'db_connections_active',
    'Number of active database connections',
    registry=REGISTRY,
)

db_connections_idle = Gauge(
    'db_connections_idle',
    'Number of idle database connections',
    registry=REGISTRY,
)

db_pool_size = Gauge(
    'db_pool_size',
    'Database connection pool size',
    registry=REGISTRY,
)

db_query_duration_seconds = Histogram(
    'db_query_duration_seconds',
    'Database query duration in seconds',
    ['operation', 'table'],
    buckets=[0.001, 0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0],
    registry=REGISTRY,
)

db_query_errors_total = Counter(
    'db_query_errors_total',
    'Total number of database query errors',
    ['operation', 'error_type'],
    registry=REGISTRY,
)


# ============= 用户活动指标 =============

user_submissions_total = Counter(
    'user_submissions_total',
    'Total number of user submissions',
    ['language', 'assignment_type'],
    registry=REGISTRY,
)

user_logins_total = Counter(
    'user_logins_total',
    'Total number of user logins',
    ['status'],  # status: success, failed
    registry=REGISTRY,
)

user_active_sessions = Gauge(
    'user_active_sessions',
    'Number of active user sessions',
    registry=REGISTRY,
)


# ============= 系统信息 =============

app_info = Info(
    'app',
    'Application information',
    registry=REGISTRY,
)

# 设置应用信息
app_info.info({
    'version': '1.0.0',
    'name': 'ai-teacher',
    'environment': os.getenv('ENVIRONMENT', 'development'),
})


# ============= 工具函数和装饰器 =============

def track_request_metrics(endpoint: str):
    """
    追踪HTTP请求指标的装饰器

    Usage:
        @track_request_metrics("/api/v1/analysis")
        async def analyze_code(...):
            ...
    """
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            start_time = time.time()
            method = "POST"  # 可以从request中获取
            status = "200"

            try:
                result = await func(*args, **kwargs)
                return result
            except Exception as e:
                status = "500"
                raise
            finally:
                duration = time.time() - start_time
                http_requests_total.labels(
                    method=method,
                    endpoint=endpoint,
                    status_code=status
                ).inc()
                http_request_duration_seconds.labels(
                    method=method,
                    endpoint=endpoint
                ).observe(duration)

        return wrapper
    return decorator


def track_ai_analysis(analysis_type: str, language: str):
    """
    追踪AI分析指标的装饰器

    Usage:
        @track_ai_analysis("code_review", "python")
        async def analyze_code(...):
            ...
    """
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            start_time = time.time()
            status = "success"

            try:
                result = await func(*args, **kwargs)
                return result
            except Exception as e:
                status = "error"
                raise
            finally:
                duration = time.time() - start_time
                ai_analysis_requests_total.labels(
                    analysis_type=analysis_type,
                    language=language,
                    status=status
                ).inc()
                ai_analysis_duration_seconds.labels(
                    analysis_type=analysis_type,
                    language=language
                ).observe(duration)

        return wrapper
    return decorator


def track_code_execution(language: str):
    """
    追踪代码执行指标的装饰器
    """
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            start_time = time.time()
            status = "success"

            try:
                result = await func(*args, **kwargs)
                # 尝试从结果中获取状态
                if hasattr(result, 'status'):
                    status = result.status.value if hasattr(result.status, 'value') else str(result.status)
                return result
            except Exception as e:
                status = "error"
                raise
            finally:
                duration = time.time() - start_time
                code_execution_total.labels(
                    language=language,
                    status=status
                ).inc()
                code_execution_duration_seconds.labels(
                    language=language
                ).observe(duration)

        return wrapper
    return decorator


def record_ai_api_usage(model: str, prompt_tokens: int, completion_tokens: int):
    """记录AI API使用情况"""
    ai_api_calls_total.labels(model=model, endpoint="chat/completions").inc()
    ai_api_tokens_used_total.labels(model=model, token_type="prompt").inc(prompt_tokens)
    ai_api_tokens_used_total.labels(model=model, token_type="completion").inc(completion_tokens)

    # 计算成本（基于OpenAI定价）
    cost_per_1k_prompt = 0.0015  # GPT-3.5-turbo
    cost_per_1k_completion = 0.002
    if "gpt-4" in model:
        cost_per_1k_prompt = 0.03
        cost_per_1k_completion = 0.06

    total_cost = (prompt_tokens / 1000 * cost_per_1k_prompt +
                  completion_tokens / 1000 * cost_per_1k_completion)
    ai_api_cost_usd_total.labels(model=model).inc(total_cost)


def record_cache_operation(operation: str):
    """记录缓存操作"""
    ai_cache_operations_total.labels(operation=operation).inc()


def record_db_query(operation: str, table: str, duration: float, error: Optional[str] = None):
    """记录数据库查询"""
    db_query_duration_seconds.labels(operation=operation, table=table).observe(duration)
    if error:
        db_query_errors_total.labels(operation=operation, error_type=error).inc()


def update_db_pool_stats(active: int, idle: int, pool_size: int):
    """更新数据库连接池状态"""
    db_connections_active.set(active)
    db_connections_idle.set(idle)
    db_pool_size.set(pool_size)


# ============= Prometheus中间件 =============

class PrometheusMiddleware(BaseHTTPMiddleware):
    """Prometheus指标收集中间件"""

    # 不追踪的路径
    EXCLUDED_PATHS = {'/health', '/metrics', '/favicon.ico'}

    async def dispatch(self, request: Request, call_next):
        if request.url.path in self.EXCLUDED_PATHS:
            return await call_next(request)

        method = request.method
        endpoint = self._get_endpoint(request)

        # 增加活跃连接数
        http_active_connections.inc()

        # 记录请求大小
        content_length = request.headers.get('content-length', 0)
        if content_length:
            http_request_size_bytes.labels(
                method=method,
                endpoint=endpoint
            ).observe(int(content_length))

        start_time = time.time()
        status_code = "500"

        try:
            response = await call_next(request)
            status_code = str(response.status_code)

            # 记录响应大小
            response_size = response.headers.get('content-length', 0)
            if response_size:
                http_response_size_bytes.labels(
                    method=method,
                    endpoint=endpoint
                ).observe(int(response_size))

            return response

        except Exception as e:
            status_code = "500"
            raise

        finally:
            # 减少活跃连接数
            http_active_connections.dec()

            # 记录请求指标
            duration = time.time() - start_time
            http_requests_total.labels(
                method=method,
                endpoint=endpoint,
                status_code=status_code
            ).inc()
            http_request_duration_seconds.labels(
                method=method,
                endpoint=endpoint
            ).observe(duration)

    def _get_endpoint(self, request: Request) -> str:
        """获取标准化的端点路径"""
        path = request.url.path

        # 移除路径中的ID参数，使指标更聚合
        # /api/v1/users/123 -> /api/v1/users/{id}
        parts = path.split('/')
        normalized_parts = []
        for part in parts:
            if part and self._is_id(part):
                normalized_parts.append('{id}')
            else:
                normalized_parts.append(part)

        return '/'.join(normalized_parts)

    def _is_id(self, part: str) -> bool:
        """判断路径部分是否为ID"""
        # UUID格式
        if len(part) == 36 and part.count('-') == 4:
            return True
        # 纯数字
        if part.isdigit():
            return True
        # 短UUID (8位)
        if len(part) == 8 and all(c.isalnum() for c in part):
            return True
        return False


# ============= 导出指标 =============

def get_metrics() -> bytes:
    """获取Prometheus指标数据"""
    return generate_latest(REGISTRY)


def get_metrics_content_type() -> str:
    """获取Prometheus指标内容类型"""
    return CONTENT_TYPE_LATEST
