"""
AI教学助手系统 - 通用模式定义
定义通用的Pydantic模式和响应格式

Author: AI Backend Architecture Expert
Date: 2025-09-10
"""

from pydantic import BaseModel, Field, validator
from typing import Generic, TypeVar, Optional, Any, Dict, List
from datetime import datetime
from enum import Enum


T = TypeVar('T')


class ResponseStatus(str, Enum):
    """响应状态枚举"""
    SUCCESS = "success"
    ERROR = "error"
    WARNING = "warning"


class ResponseModel(BaseModel, Generic[T]):
    """通用API响应模式"""
    success: bool = Field(..., description="操作是否成功")
    data: Optional[T] = Field(None, description="响应数据")
    message: str = Field(..., description="响应消息")
    error_code: Optional[str] = Field(None, description="错误代码")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="响应时间")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class PaginatedResponse(BaseModel, Generic[T]):
    """分页响应模式"""
    success: bool = Field(..., description="操作是否成功")
    data: List[T] = Field(..., description="数据列表")
    total: int = Field(..., description="总记录数", ge=0)
    page: int = Field(..., description="当前页码", ge=1)
    page_size: int = Field(..., description="每页记录数", ge=1, le=100)
    total_pages: int = Field(..., description="总页数", ge=0)
    has_next: bool = Field(False, description="是否有下一页")
    has_prev: bool = Field(False, description="是否有上一页")
    message: str = Field("", description="响应消息")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="响应时间")
    
    @validator('has_next', pre=False, always=True)
    def set_has_next(cls, v, values):
        """设置是否有下一页"""
        if 'page' in values and 'total_pages' in values:
            return values['page'] < values['total_pages']
        return False
    
    @validator('has_prev', pre=False, always=True)
    def set_has_prev(cls, v, values):
        """设置是否有上一页"""
        if 'page' in values:
            return values['page'] > 1
        return False
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class ErrorDetail(BaseModel):
    """错误详情模式"""
    field: Optional[str] = Field(None, description="错误字段")
    message: str = Field(..., description="错误消息")
    code: Optional[str] = Field(None, description="错误代码")


class ErrorResponse(BaseModel):
    """错误响应模式"""
    success: bool = Field(False, description="操作是否成功")
    message: str = Field(..., description="错误消息")
    error_code: Optional[str] = Field(None, description="错误代码")
    details: Optional[List[ErrorDetail]] = Field(None, description="详细错误信息")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="响应时间")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class HealthCheckResponse(BaseModel):
    """健康检查响应模式"""
    status: str = Field(..., description="系统状态")
    timestamp: float = Field(..., description="检查时间戳")
    services: Dict[str, str] = Field(..., description="各服务状态")
    version: str = Field(..., description="系统版本")
    uptime: Optional[float] = Field(None, description="运行时间（秒）")
    
    class Config:
        schema_extra = {
            "example": {
                "status": "healthy",
                "timestamp": 1694073600.0,
                "services": {
                    "database": "connected",
                    "ai_service": "active",
                    "redis": "connected"
                },
                "version": "1.0.0",
                "uptime": 3600.0
            }
        }


class PaginationParams(BaseModel):
    """分页参数模式"""
    page: int = Field(1, ge=1, description="页码")
    page_size: int = Field(20, ge=1, le=100, description="每页记录数")
    
    @validator('page_size')
    def validate_page_size(cls, v):
        """验证页面大小"""
        if v > 100:
            raise ValueError('Page size cannot exceed 100')
        return v


class SortParams(BaseModel):
    """排序参数模式"""
    sort_by: str = Field("created_at", description="排序字段")
    sort_order: str = Field("desc", description="排序方向", pattern="^(asc|desc)$")
    
    @validator('sort_order')
    def validate_sort_order(cls, v):
        """验证排序方向"""
        if v.lower() not in ['asc', 'desc']:
            raise ValueError('Sort order must be either "asc" or "desc"')
        return v.lower()


class FilterParams(BaseModel):
    """过滤参数基类"""
    start_date: Optional[datetime] = Field(None, description="开始日期")
    end_date: Optional[datetime] = Field(None, description="结束日期")
    
    @validator('end_date')
    def validate_date_range(cls, v, values):
        """验证日期范围"""
        if v and 'start_date' in values and values['start_date']:
            if v < values['start_date']:
                raise ValueError('End date cannot be before start date')
        return v


class FileUpload(BaseModel):
    """文件上传模式"""
    filename: str = Field(..., description="文件名")
    content_type: str = Field(..., description="文件类型")
    size: int = Field(..., description="文件大小（字节）", ge=0)
    
    @validator('size')
    def validate_file_size(cls, v):
        """验证文件大小"""
        max_size = 10 * 1024 * 1024  # 10MB
        if v > max_size:
            raise ValueError(f'File size cannot exceed {max_size} bytes')
        return v


class APIKeyInfo(BaseModel):
    """API密钥信息模式"""
    key_id: str = Field(..., description="密钥ID")
    name: str = Field(..., description="密钥名称")
    prefix: str = Field(..., description="密钥前缀")
    created_at: datetime = Field(..., description="创建时间")
    last_used_at: Optional[datetime] = Field(None, description="最后使用时间")
    expires_at: Optional[datetime] = Field(None, description="过期时间")
    is_active: bool = Field(..., description="是否激活")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class ValidationError(BaseModel):
    """验证错误模式"""
    loc: List[str] = Field(..., description="错误位置")
    msg: str = Field(..., description="错误消息")
    type: str = Field(..., description="错误类型")
    
    class Config:
        schema_extra = {
            "example": {
                "loc": ["body", "email"],
                "msg": "field required",
                "type": "value_error.missing"
            }
        }


class MetricsData(BaseModel):
    """指标数据模式"""
    metric_name: str = Field(..., description="指标名称")
    value: float = Field(..., description="指标值")
    unit: Optional[str] = Field(None, description="单位")
    timestamp: datetime = Field(..., description="时间戳")
    metadata: Optional[Dict[str, Any]] = Field(None, description="元数据")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class BulkOperation(BaseModel):
    """批量操作模式"""
    operation: str = Field(..., description="操作类型")
    items: List[str] = Field(..., description="操作项目ID列表")
    parameters: Optional[Dict[str, Any]] = Field(None, description="操作参数")
    
    @validator('items')
    def validate_items_count(cls, v):
        """验证批量操作项目数量"""
        if len(v) > 100:
            raise ValueError('Cannot process more than 100 items at once')
        return v


class BulkOperationResult(BaseModel):
    """批量操作结果模式"""
    total_items: int = Field(..., description="总项目数")
    successful_items: int = Field(..., description="成功处理项目数")
    failed_items: int = Field(..., description="失败项目数")
    errors: List[Dict[str, Any]] = Field([], description="错误详情")
    processing_time: float = Field(..., description="处理时间（秒）")


class SystemInfo(BaseModel):
    """系统信息模式"""
    version: str = Field(..., description="系统版本")
    environment: str = Field(..., description="运行环境")
    python_version: str = Field(..., description="Python版本")
    database_version: Optional[str] = Field(None, description="数据库版本")
    uptime: float = Field(..., description="运行时间")
    memory_usage: Optional[Dict[str, float]] = Field(None, description="内存使用情况")
    cpu_usage: Optional[float] = Field(None, description="CPU使用率")


class ConfigUpdate(BaseModel):
    """配置更新模式"""
    key: str = Field(..., description="配置键")
    value: Any = Field(..., description="配置值")
    category: Optional[str] = Field(None, description="配置分类")
    description: Optional[str] = Field(None, description="配置描述")


class NotificationSettings(BaseModel):
    """通知设置模式"""
    email_notifications: bool = Field(True, description="邮件通知开关")
    push_notifications: bool = Field(True, description="推送通知开关")
    notification_types: List[str] = Field([], description="通知类型列表")
    frequency: str = Field("immediate", description="通知频率")


# 常用的字符串验证器
def validate_non_empty_string(value: str) -> str:
    """验证非空字符串"""
    if not value or not value.strip():
        raise ValueError('String cannot be empty')
    return value.strip()


def validate_email_format(email: str) -> str:
    """验证邮箱格式"""
    import re
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(pattern, email):
        raise ValueError('Invalid email format')
    return email.lower()


def validate_username(username: str) -> str:
    """验证用户名格式"""
    import re
    if not re.match(r'^[a-zA-Z0-9_-]{3,20}$', username):
        raise ValueError('Username must be 3-20 characters and contain only letters, numbers, underscore or dash')
    return username


# 通用的配置模式
class DatabaseConfig(BaseModel):
    """数据库配置模式"""
    host: str = Field(..., description="数据库主机")
    port: int = Field(..., description="数据库端口")
    database: str = Field(..., description="数据库名")
    username: str = Field(..., description="用户名")
    pool_size: int = Field(10, description="连接池大小")
    max_overflow: int = Field(20, description="连接池最大溢出")


class RedisConfig(BaseModel):
    """Redis配置模式"""
    host: str = Field(..., description="Redis主机")
    port: int = Field(6379, description="Redis端口")
    database: int = Field(0, description="Redis数据库编号")
    password: Optional[str] = Field(None, description="Redis密码")
    expire_time: int = Field(3600, description="默认过期时间")


class AIServiceConfig(BaseModel):
    """AI服务配置模式"""
    provider: str = Field(..., description="AI服务提供商")
    model: str = Field(..., description="AI模型")
    api_key: str = Field(..., description="API密钥")
    max_tokens: int = Field(4000, description="最大令牌数")
    temperature: float = Field(0.7, description="生成温度")
    timeout: int = Field(30, description="请求超时时间")


# 导出所有模式
__all__ = [
    "ResponseModel",
    "PaginatedResponse", 
    "ErrorResponse",
    "ErrorDetail",
    "HealthCheckResponse",
    "PaginationParams",
    "SortParams",
    "FilterParams",
    "FileUpload",
    "APIKeyInfo",
    "ValidationError",
    "MetricsData",
    "BulkOperation",
    "BulkOperationResult",
    "SystemInfo",
    "ConfigUpdate",
    "NotificationSettings",
    "DatabaseConfig",
    "RedisConfig",
    "AIServiceConfig"
]