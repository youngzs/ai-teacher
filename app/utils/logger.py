"""
AI教学助手系统 - 日志配置
提供统一的日志记录功能

Author: AI Backend Architecture Expert
Date: 2025-09-10
"""

import logging
import sys
from pathlib import Path
from typing import Optional
from loguru import logger
from datetime import datetime

from ..core.config import settings


def setup_logging():
    """设置日志配置"""
    # 移除默认的loguru处理器
    logger.remove()
    
    # 控制台日志格式
    console_format = (
        "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
        "<level>{level: <8}</level> | "
        "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
        "<level>{message}</level>"
    )
    
    # 文件日志格式
    file_format = (
        "{time:YYYY-MM-DD HH:mm:ss} | "
        "{level: <8} | "
        "{name}:{function}:{line} | "
        "{message}"
    )
    
    # 添加控制台处理器
    logger.add(
        sys.stderr,
        format=console_format,
        level=settings.LOG_LEVEL,
        colorize=True,
        backtrace=True,
        diagnose=True
    )
    
    # 添加文件处理器
    log_file = settings.LOG_DIR / "ai_teacher.log"
    logger.add(
        log_file,
        format=file_format,
        level=settings.LOG_LEVEL,
        rotation=settings.LOG_ROTATION,
        retention=settings.LOG_RETENTION,
        compression="zip",
        backtrace=True,
        diagnose=True
    )
    
    # 错误日志单独文件
    error_log_file = settings.LOG_DIR / "errors.log"
    logger.add(
        error_log_file,
        format=file_format,
        level="ERROR",
        rotation="1 week",
        retention="1 month",
        compression="zip",
        backtrace=True,
        diagnose=True
    )
    
    # API访问日志
    access_log_file = settings.LOG_DIR / "access.log"
    logger.add(
        access_log_file,
        format="{time:YYYY-MM-DD HH:mm:ss} | {message}",
        level="INFO",
        rotation="1 day",
        retention="1 month",
        filter=lambda record: "access" in record["extra"]
    )


def get_logger(name: str) -> logging.Logger:
    """获取logger实例"""
    return logging.getLogger(name)


# 与现有日志系统的兼容函数
def log_agent_activity(agent_name: str, activity: str, details: dict):
    """记录Agent活动"""
    logger.bind(extra="agent_activity").info(
        f"Agent:{agent_name} Activity:{activity} Details:{details}"
    )


def log_performance_metric(metric_name: str, value: float, unit: str, metadata: dict = None):
    """记录性能指标"""
    logger.bind(extra="performance_metric").info(
        f"Metric:{metric_name} Value:{value}{unit} Metadata:{metadata or {}}"
    )


class LogExecutionTime:
    """执行时间记录上下文管理器"""
    
    def __init__(self, operation_name: str):
        self.operation_name = operation_name
        self.start_time = None
    
    def __enter__(self):
        self.start_time = datetime.now()
        logger.info(f"Starting operation: {self.operation_name}")
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.start_time:
            execution_time = (datetime.now() - self.start_time).total_seconds()
            if exc_type is None:
                logger.info(f"Completed operation: {self.operation_name} in {execution_time:.2f}s")
            else:
                logger.error(f"Failed operation: {self.operation_name} in {execution_time:.2f}s - {exc_val}")