"""
AI教学助手系统 - 日志管理工具
提供统一的日志记录功能

Author: AI Architecture Expert
Date: 2025-09-09
"""

import logging
import sys
import os
from datetime import datetime
from typing import Optional
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler

class TeachingSystemLogger:
    """教学系统日志管理类"""
    
    _instance = None
    _initialized = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not self._initialized:
            self._setup_logging()
            TeachingSystemLogger._initialized = True
    
    def _setup_logging(self):
        """设置日志配置"""
        
        # 创建日志目录
        log_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'logs')
        os.makedirs(log_dir, exist_ok=True)
        
        # 配置根日志器
        root_logger = logging.getLogger()
        root_logger.setLevel(logging.INFO)
        
        # 清除现有处理器
        for handler in root_logger.handlers[:]:
            root_logger.removeHandler(handler)
        
        # 创建格式化器
        detailed_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
        )
        
        simple_formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s'
        )
        
        # 控制台处理器
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(simple_formatter)
        root_logger.addHandler(console_handler)
        
        # 文件处理器 - 详细日志
        detailed_handler = TimedRotatingFileHandler(
            filename=os.path.join(log_dir, 'teaching_system.log'),
            when='midnight',
            interval=1,
            backupCount=30,
            encoding='utf-8'
        )
        detailed_handler.setLevel(logging.DEBUG)
        detailed_handler.setFormatter(detailed_formatter)
        root_logger.addHandler(detailed_handler)
        
        # 错误日志处理器
        error_handler = RotatingFileHandler(
            filename=os.path.join(log_dir, 'errors.log'),
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5,
            encoding='utf-8'
        )
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(detailed_formatter)
        root_logger.addHandler(error_handler)
        
        # Agent活动日志处理器
        agent_handler = TimedRotatingFileHandler(
            filename=os.path.join(log_dir, 'agent_activities.log'),
            when='midnight',
            interval=1,
            backupCount=7,
            encoding='utf-8'
        )
        agent_handler.setLevel(logging.INFO)
        agent_handler.setFormatter(detailed_formatter)
        
        # 为Agent活动创建专门的日志器
        agent_logger = logging.getLogger('agents')
        agent_logger.addHandler(agent_handler)
        agent_logger.setLevel(logging.INFO)
        agent_logger.propagate = False  # 不向根日志器传播
        
        # 性能监控日志处理器
        performance_handler = TimedRotatingFileHandler(
            filename=os.path.join(log_dir, 'performance.log'),
            when='midnight',
            interval=1,
            backupCount=30,
            encoding='utf-8'
        )
        performance_handler.setLevel(logging.INFO)
        performance_handler.setFormatter(logging.Formatter(
            '%(asctime)s - PERFORMANCE - %(message)s'
        ))
        
        performance_logger = logging.getLogger('performance')
        performance_logger.addHandler(performance_handler)
        performance_logger.setLevel(logging.INFO)
        performance_logger.propagate = False

def get_logger(name: str) -> logging.Logger:
    """获取日志器实例"""
    TeachingSystemLogger()  # 确保日志系统已初始化
    return logging.getLogger(name)

def log_agent_activity(agent_name: str, activity: str, details: Optional[dict] = None):
    """记录Agent活动日志"""
    logger = logging.getLogger('agents')
    message = f"{agent_name} - {activity}"
    if details:
        message += f" - {details}"
    logger.info(message)

def log_performance_metric(metric_name: str, value: float, unit: str = "", context: Optional[dict] = None):
    """记录性能指标"""
    logger = logging.getLogger('performance')
    message = f"{metric_name}: {value}{unit}"
    if context:
        message += f" | Context: {context}"
    logger.info(message)

def log_student_interaction(student_id: str, action: str, details: Optional[dict] = None):
    """记录学生交互日志"""
    logger = get_logger('student_interactions')
    message = f"Student {student_id} - {action}"
    if details:
        message += f" - Details: {details}"
    logger.info(message)

def log_system_event(event_type: str, message: str, severity: str = "INFO"):
    """记录系统事件"""
    logger = get_logger('system_events')
    
    if severity.upper() == "ERROR":
        logger.error(f"{event_type}: {message}")
    elif severity.upper() == "WARNING":
        logger.warning(f"{event_type}: {message}")
    else:
        logger.info(f"{event_type}: {message}")

# 装饰器：自动记录函数调用
def log_function_call(logger_name: str = None):
    """装饰器：自动记录函数调用"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            func_logger = get_logger(logger_name or func.__module__)
            
            try:
                func_logger.debug(f"Calling {func.__name__} with args={args}, kwargs={kwargs}")
                start_time = datetime.now()
                
                result = func(*args, **kwargs)
                
                end_time = datetime.now()
                execution_time = (end_time - start_time).total_seconds()
                
                func_logger.debug(f"Function {func.__name__} completed in {execution_time:.3f}s")
                log_performance_metric(f"{func.__name__}_execution_time", execution_time, "s")
                
                return result
                
            except Exception as e:
                func_logger.error(f"Error in {func.__name__}: {str(e)}", exc_info=True)
                raise
                
        return wrapper
    return decorator

# 上下文管理器：记录代码块执行时间
class LogExecutionTime:
    """上下文管理器：记录代码块执行时间"""
    
    def __init__(self, operation_name: str, logger_name: str = None):
        self.operation_name = operation_name
        self.logger = get_logger(logger_name or 'performance')
        self.start_time = None
    
    def __enter__(self):
        self.start_time = datetime.now()
        self.logger.debug(f"Starting operation: {self.operation_name}")
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.start_time:
            end_time = datetime.now()
            execution_time = (end_time - self.start_time).total_seconds()
            
            if exc_type is None:
                self.logger.info(f"Operation '{self.operation_name}' completed in {execution_time:.3f}s")
                log_performance_metric(f"{self.operation_name}_execution_time", execution_time, "s")
            else:
                self.logger.error(f"Operation '{self.operation_name}' failed after {execution_time:.3f}s: {exc_val}")

# 专用日志函数
def log_code_submission(student_id: str, assignment_id: str, code_length: int, language: str):
    """记录代码提交事件"""
    details = {
        'assignment_id': assignment_id,
        'code_length': code_length,
        'language': language,
        'timestamp': datetime.now().isoformat()
    }
    log_student_interaction(student_id, 'code_submission', details)

def log_feedback_generation(student_id: str, session_id: str, strategy: str, quality_score: float):
    """记录反馈生成事件"""
    details = {
        'session_id': session_id,
        'strategy': strategy,
        'quality_score': quality_score,
        'timestamp': datetime.now().isoformat()
    }
    log_student_interaction(student_id, 'feedback_generated', details)

def log_agent_response_time(agent_name: str, response_time: float):
    """记录Agent响应时间"""
    log_performance_metric(f"{agent_name}_response_time", response_time, "s", {"agent": agent_name})

def log_system_resource_usage(cpu_percent: float, memory_mb: float, active_sessions: int):
    """记录系统资源使用情况"""
    logger = get_logger('system_resources')
    logger.info(f"CPU: {cpu_percent:.1f}%, Memory: {memory_mb:.1f}MB, Active Sessions: {active_sessions}")

# 错误报告函数
def log_critical_error(error_type: str, error_message: str, context: dict = None):
    """记录严重错误"""
    logger = get_logger('critical_errors')
    message = f"CRITICAL ERROR - {error_type}: {error_message}"
    if context:
        message += f" | Context: {context}"
    logger.critical(message)

# 示例使用方法
if __name__ == "__main__":
    # 基本使用
    logger = get_logger(__name__)
    logger.info("This is a test log message")
    
    # Agent活动日志
    log_agent_activity("CodeAnalyzer", "analyzing_student_code", {"student_id": "test_001"})
    
    # 性能监控
    log_performance_metric("response_time", 2.5, "s", {"endpoint": "/api/analyze"})
    
    # 使用装饰器
    @log_function_call()
    def test_function(x, y):
        return x + y
    
    result = test_function(1, 2)
    
    # 使用上下文管理器
    with LogExecutionTime("database_query"):
        import time
        time.sleep(0.1)  # 模拟数据库查询
    
    print("Logging test completed")