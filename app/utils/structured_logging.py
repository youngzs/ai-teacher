"""
AI教学助手系统 - 结构化日志模块 (Sprint 5)
提供结构化日志记录，支持trace ID追踪和日志聚合

Author: AI Backend Architecture Expert
Date: Sprint 5
"""

import json
import uuid
import logging
import sys
from datetime import datetime
from typing import Optional, Dict, Any, Callable
from contextvars import ContextVar
from functools import wraps
from pathlib import Path

from loguru import logger as loguru_logger

# 上下文变量用于存储trace信息
trace_id_var: ContextVar[Optional[str]] = ContextVar('trace_id', default=None)
span_id_var: ContextVar[Optional[str]] = ContextVar('span_id', default=None)
user_id_var: ContextVar[Optional[str]] = ContextVar('user_id', default=None)


def generate_trace_id() -> str:
    """生成唯一的trace ID"""
    return str(uuid.uuid4())


def generate_span_id() -> str:
    """生成唯一的span ID"""
    return str(uuid.uuid4())[:8]


def get_trace_id() -> Optional[str]:
    """获取当前trace ID"""
    return trace_id_var.get()


def get_span_id() -> Optional[str]:
    """获取当前span ID"""
    return span_id_var.get()


def get_user_id() -> Optional[str]:
    """获取当前用户ID"""
    return user_id_var.get()


def set_trace_context(
    trace_id: Optional[str] = None,
    span_id: Optional[str] = None,
    user_id: Optional[str] = None
):
    """设置trace上下文"""
    if trace_id:
        trace_id_var.set(trace_id)
    if span_id:
        span_id_var.set(span_id)
    if user_id:
        user_id_var.set(user_id)


def clear_trace_context():
    """清除trace上下文"""
    trace_id_var.set(None)
    span_id_var.set(None)
    user_id_var.set(None)


class JSONLogFormatter(logging.Formatter):
    """JSON格式日志格式化器"""

    def __init__(self, service_name: str = "ai-teacher-api"):
        super().__init__()
        self.service_name = service_name

    def format(self, record: logging.LogRecord) -> str:
        """格式化日志记录为JSON"""
        log_data = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "service": self.service_name,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }

        # 添加trace信息
        trace_id = get_trace_id()
        span_id = get_span_id()
        user_id = get_user_id()

        if trace_id:
            log_data["trace_id"] = trace_id
        if span_id:
            log_data["span_id"] = span_id
        if user_id:
            log_data["user_id"] = user_id

        # 添加异常信息
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)

        # 添加额外字段
        if hasattr(record, 'extra_data'):
            log_data["extra"] = record.extra_data

        return json.dumps(log_data, ensure_ascii=False)


class StructuredLogger:
    """结构化日志记录器"""

    def __init__(self, name: str, service_name: str = "ai-teacher-api"):
        self.name = name
        self.service_name = service_name
        self._logger = logging.getLogger(name)

    def _log(
        self,
        level: int,
        message: str,
        extra: Optional[Dict[str, Any]] = None,
        exc_info: bool = False
    ):
        """内部日志记录方法"""
        record_extra = {}
        if extra:
            record_extra['extra_data'] = extra

        self._logger.log(level, message, exc_info=exc_info, extra=record_extra)

    def debug(self, message: str, **kwargs):
        """调试日志"""
        self._log(logging.DEBUG, message, kwargs if kwargs else None)

    def info(self, message: str, **kwargs):
        """信息日志"""
        self._log(logging.INFO, message, kwargs if kwargs else None)

    def warning(self, message: str, **kwargs):
        """警告日志"""
        self._log(logging.WARNING, message, kwargs if kwargs else None)

    def error(self, message: str, exc_info: bool = False, **kwargs):
        """错误日志"""
        self._log(logging.ERROR, message, kwargs if kwargs else None, exc_info)

    def critical(self, message: str, exc_info: bool = False, **kwargs):
        """严重错误日志"""
        self._log(logging.CRITICAL, message, kwargs if kwargs else None, exc_info)

    def log_request(
        self,
        method: str,
        path: str,
        status_code: int,
        duration_ms: float,
        **kwargs
    ):
        """记录HTTP请求"""
        self.info(
            f"HTTP {method} {path} - {status_code} - {duration_ms:.2f}ms",
            method=method,
            path=path,
            status_code=status_code,
            duration_ms=duration_ms,
            **kwargs
        )

    def log_ai_analysis(
        self,
        analysis_type: str,
        language: str,
        duration_ms: float,
        success: bool,
        **kwargs
    ):
        """记录AI分析"""
        status = "success" if success else "failed"
        self.info(
            f"AI Analysis [{analysis_type}] - {language} - {status} - {duration_ms:.2f}ms",
            analysis_type=analysis_type,
            language=language,
            duration_ms=duration_ms,
            success=success,
            **kwargs
        )

    def log_code_execution(
        self,
        language: str,
        status: str,
        duration_ms: float,
        **kwargs
    ):
        """记录代码执行"""
        self.info(
            f"Code Execution [{language}] - {status} - {duration_ms:.2f}ms",
            language=language,
            execution_status=status,
            duration_ms=duration_ms,
            **kwargs
        )

    def log_db_query(
        self,
        operation: str,
        table: str,
        duration_ms: float,
        rows_affected: Optional[int] = None,
        **kwargs
    ):
        """记录数据库查询"""
        msg = f"DB {operation} on {table} - {duration_ms:.2f}ms"
        if rows_affected is not None:
            msg += f" - {rows_affected} rows"
        self.debug(
            msg,
            db_operation=operation,
            table=table,
            duration_ms=duration_ms,
            rows_affected=rows_affected,
            **kwargs
        )

    def log_user_action(
        self,
        action: str,
        user_id: str,
        **kwargs
    ):
        """记录用户操作"""
        self.info(
            f"User Action: {action}",
            action=action,
            action_user_id=user_id,
            **kwargs
        )


def setup_structured_logging(
    service_name: str = "ai-teacher-api",
    log_level: str = "INFO",
    log_dir: Optional[Path] = None,
    json_format: bool = True
):
    """
    设置结构化日志

    Args:
        service_name: 服务名称
        log_level: 日志级别
        log_dir: 日志目录
        json_format: 是否使用JSON格式
    """
    # 配置根日志器
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, log_level.upper()))

    # 清除现有处理器
    root_logger.handlers.clear()

    # 控制台处理器
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(getattr(logging, log_level.upper()))

    if json_format:
        console_handler.setFormatter(JSONLogFormatter(service_name))
    else:
        console_handler.setFormatter(
            logging.Formatter(
                '%(asctime)s | %(levelname)-8s | %(name)s:%(funcName)s:%(lineno)d | %(message)s'
            )
        )

    root_logger.addHandler(console_handler)

    # 文件处理器（如果指定了日志目录）
    if log_dir:
        log_dir.mkdir(parents=True, exist_ok=True)

        # JSON日志文件
        json_handler = logging.FileHandler(
            log_dir / "app.json.log",
            encoding='utf-8'
        )
        json_handler.setLevel(getattr(logging, log_level.upper()))
        json_handler.setFormatter(JSONLogFormatter(service_name))
        root_logger.addHandler(json_handler)

        # 错误日志文件
        error_handler = logging.FileHandler(
            log_dir / "error.json.log",
            encoding='utf-8'
        )
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(JSONLogFormatter(service_name))
        root_logger.addHandler(error_handler)


def get_structured_logger(name: str) -> StructuredLogger:
    """获取结构化日志记录器实例"""
    return StructuredLogger(name)


def with_trace(func: Callable) -> Callable:
    """
    为函数添加trace上下文的装饰器

    Usage:
        @with_trace
        async def my_function():
            ...
    """
    @wraps(func)
    async def async_wrapper(*args, **kwargs):
        trace_id = generate_trace_id()
        span_id = generate_span_id()
        set_trace_context(trace_id=trace_id, span_id=span_id)
        try:
            return await func(*args, **kwargs)
        finally:
            clear_trace_context()

    @wraps(func)
    def sync_wrapper(*args, **kwargs):
        trace_id = generate_trace_id()
        span_id = generate_span_id()
        set_trace_context(trace_id=trace_id, span_id=span_id)
        try:
            return func(*args, **kwargs)
        finally:
            clear_trace_context()

    if hasattr(func, '__code__') and func.__code__.co_flags & 0x80:  # 检查是否为async函数
        return async_wrapper
    return sync_wrapper


class TraceContextMiddleware:
    """
    Trace上下文中间件

    为每个请求自动设置trace ID
    """

    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] == "http":
            # 从请求头获取或生成trace ID
            headers = dict(scope.get("headers", []))
            trace_id = headers.get(b"x-trace-id", b"").decode() or generate_trace_id()
            span_id = generate_span_id()

            set_trace_context(trace_id=trace_id, span_id=span_id)

            # 添加trace ID到响应头
            async def send_wrapper(message):
                if message["type"] == "http.response.start":
                    headers = list(message.get("headers", []))
                    headers.append((b"x-trace-id", trace_id.encode()))
                    message["headers"] = headers
                await send(message)

            try:
                await self.app(scope, receive, send_wrapper)
            finally:
                clear_trace_context()
        else:
            await self.app(scope, receive, send)


# 预定义的日志事件类型
class LogEvents:
    """日志事件常量"""
    # 用户事件
    USER_LOGIN = "user_login"
    USER_LOGOUT = "user_logout"
    USER_REGISTER = "user_register"

    # 提交事件
    CODE_SUBMITTED = "code_submitted"
    CODE_EXECUTED = "code_executed"
    SUBMISSION_GRADED = "submission_graded"

    # AI事件
    AI_ANALYSIS_START = "ai_analysis_start"
    AI_ANALYSIS_COMPLETE = "ai_analysis_complete"
    AI_ANALYSIS_ERROR = "ai_analysis_error"

    # 课程事件
    COURSE_CREATED = "course_created"
    ASSIGNMENT_CREATED = "assignment_created"
    ASSIGNMENT_SUBMITTED = "assignment_submitted"

    # 系统事件
    SERVICE_START = "service_start"
    SERVICE_STOP = "service_stop"
    HEALTH_CHECK = "health_check"
