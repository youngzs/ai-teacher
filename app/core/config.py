"""
AI教学助手系统 - 核心配置
包含数据库、安全、AI服务等配置设置

Author: AI Backend Architecture Expert  
Date: 2025-09-10
"""

from typing import List, Optional, Any, Dict
from pydantic_settings import BaseSettings
from pydantic import Field, validator
import secrets
import os
from pathlib import Path


class Settings(BaseSettings):
    """应用配置设置"""
    
    # 应用基本配置
    PROJECT_NAME: str = "AI Teaching Assistant System"
    VERSION: str = "1.0.0"
    ENVIRONMENT: str = Field(default="development", env="ENVIRONMENT")
    DEBUG: bool = Field(default=True, env="DEBUG")
    
    # 服务器配置
    HOST: str = Field(default="0.0.0.0", env="HOST")
    PORT: int = Field(default=8000, env="PORT")
    ALLOWED_HOSTS: List[str] = Field(default=["*"], env="ALLOWED_HOSTS")
    
    # 安全配置
    SECRET_KEY: str = Field(default_factory=lambda: secrets.token_urlsafe(32), env="SECRET_KEY")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=1440, env="ACCESS_TOKEN_EXPIRE_MINUTES")  # 24小时
    REFRESH_TOKEN_EXPIRE_DAYS: int = Field(default=30, env="REFRESH_TOKEN_EXPIRE_DAYS")
    ALGORITHM: str = "HS256"
    
    # 数据库配置
    DATABASE_URL: str = Field(
        default="postgresql+asyncpg://ai_teacher:password@localhost:5432/ai_teacher_db",
        env="DATABASE_URL"
    )
    DATABASE_ECHO: bool = Field(default=False, env="DATABASE_ECHO")
    DATABASE_POOL_SIZE: int = Field(default=10, env="DATABASE_POOL_SIZE")
    DATABASE_MAX_OVERFLOW: int = Field(default=20, env="DATABASE_MAX_OVERFLOW")
    
    # Redis配置（缓存和会话存储）
    REDIS_URL: str = Field(default="redis://localhost:6379/0", env="REDIS_URL")
    REDIS_EXPIRE_TIME: int = Field(default=3600, env="REDIS_EXPIRE_TIME")  # 1小时
    
    # AI服务配置
    OPENAI_API_KEY: Optional[str] = Field(default=None, env="OPENAI_API_KEY")
    OPENAI_MODEL: str = Field(default="gpt-4", env="OPENAI_MODEL")
    MAX_AI_SESSIONS: int = Field(default=50, env="MAX_AI_SESSIONS")
    AI_RESPONSE_TIMEOUT: int = Field(default=30, env="AI_RESPONSE_TIMEOUT")  # 秒
    
    # 文件上传配置
    UPLOAD_DIR: Path = Field(default=Path("uploads"), env="UPLOAD_DIR")
    MAX_FILE_SIZE: int = Field(default=10 * 1024 * 1024, env="MAX_FILE_SIZE")  # 10MB
    ALLOWED_EXTENSIONS: List[str] = Field(
        default=["py", "c", "cpp", "java", "js", "ts", "txt"],
        env="ALLOWED_EXTENSIONS"
    )
    
    # 日志配置
    LOG_LEVEL: str = Field(default="INFO", env="LOG_LEVEL")
    LOG_DIR: Path = Field(default=Path("logs"), env="LOG_DIR")
    LOG_ROTATION: str = Field(default="1 day", env="LOG_ROTATION")
    LOG_RETENTION: str = Field(default="30 days", env="LOG_RETENTION")
    
    # 邮件配置（用于通知）
    SMTP_SERVER: Optional[str] = Field(default=None, env="SMTP_SERVER")
    SMTP_PORT: int = Field(default=587, env="SMTP_PORT")
    SMTP_USERNAME: Optional[str] = Field(default=None, env="SMTP_USERNAME")
    SMTP_PASSWORD: Optional[str] = Field(default=None, env="SMTP_PASSWORD")
    EMAIL_FROM: Optional[str] = Field(default=None, env="EMAIL_FROM")
    
    # 性能配置
    MAX_CONCURRENT_REQUESTS: int = Field(default=100, env="MAX_CONCURRENT_REQUESTS")
    REQUEST_TIMEOUT: int = Field(default=30, env="REQUEST_TIMEOUT")  # 秒
    RATE_LIMIT_PER_MINUTE: int = Field(default=60, env="RATE_LIMIT_PER_MINUTE")
    
    # 功能开关
    ENABLE_SIGNUP: bool = Field(default=True, env="ENABLE_SIGNUP")
    ENABLE_DEBUGGING_MODE: bool = Field(default=True, env="ENABLE_DEBUGGING_MODE")
    ENABLE_BATCH_PROCESSING: bool = Field(default=True, env="ENABLE_BATCH_PROCESSING")
    ENABLE_METRICS_COLLECTION: bool = Field(default=True, env="ENABLE_METRICS_COLLECTION")

    @validator("ALLOWED_HOSTS", pre=True)
    def parse_hosts(cls, v):
        """解析允许的主机列表"""
        if isinstance(v, str):
            return [host.strip() for host in v.split(",")]
        return v

    @validator("ALLOWED_EXTENSIONS", pre=True)
    def parse_extensions(cls, v):
        """解析允许的文件扩展名"""
        if isinstance(v, str):
            return [ext.strip().lower() for ext in v.split(",")]
        return v

    @validator("UPLOAD_DIR", "LOG_DIR", pre=True)
    def create_directories(cls, v):
        """确保目录存在"""
        if isinstance(v, str):
            v = Path(v)
        v.mkdir(parents=True, exist_ok=True)
        return v

    @property
    def database_url_sync(self) -> str:
        """同步数据库URL（用于Alembic）"""
        return self.DATABASE_URL.replace("postgresql+asyncpg://", "postgresql://")

    @property
    def is_development(self) -> bool:
        """是否为开发环境"""
        return self.ENVIRONMENT.lower() == "development"

    @property
    def is_production(self) -> bool:
        """是否为生产环境"""
        return self.ENVIRONMENT.lower() == "production"

    def get_ai_config(self) -> Dict[str, Any]:
        """获取AI配置字典"""
        return {
            "openai_api_key": self.OPENAI_API_KEY,
            "openai_model": self.OPENAI_MODEL,
            "max_sessions": self.MAX_AI_SESSIONS,
            "response_timeout": self.AI_RESPONSE_TIMEOUT,
            "enable_debugging": self.ENABLE_DEBUGGING_MODE,
            "enable_batch": self.ENABLE_BATCH_PROCESSING,
        }

    def get_database_config(self) -> Dict[str, Any]:
        """获取数据库配置字典"""
        return {
            "url": self.DATABASE_URL,
            "echo": self.DATABASE_ECHO,
            "pool_size": self.DATABASE_POOL_SIZE,
            "max_overflow": self.DATABASE_MAX_OVERFLOW,
        }

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


# 创建全局设置实例
settings = Settings()


# 开发环境配置
class DevelopmentConfig(Settings):
    """开发环境配置"""
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    DATABASE_ECHO: bool = True
    LOG_LEVEL: str = "DEBUG"


# 生产环境配置
class ProductionConfig(Settings):
    """生产环境配置"""
    ENVIRONMENT: str = "production"
    DEBUG: bool = False
    DATABASE_ECHO: bool = False
    LOG_LEVEL: str = "INFO"
    ALLOWED_HOSTS: List[str] = ["api.aiteacher.com"]  # 替换为实际域名


# 测试环境配置
class TestingConfig(Settings):
    """测试环境配置"""
    ENVIRONMENT: str = "testing"
    DEBUG: bool = True
    DATABASE_URL: str = "postgresql+asyncpg://test:test@localhost:5432/ai_teacher_test"
    REDIS_URL: str = "redis://localhost:6379/1"  # 使用不同的Redis数据库


def get_settings() -> Settings:
    """根据环境变量获取相应的配置"""
    env = os.getenv("ENVIRONMENT", "development").lower()
    
    if env == "production":
        return ProductionConfig()
    elif env == "testing":
        return TestingConfig()
    else:
        return DevelopmentConfig()


# 验证关键配置
def validate_settings(settings_obj: Settings) -> bool:
    """验证配置的有效性"""
    errors = []
    
    # 验证必需的配置
    if settings_obj.is_production:
        if not settings_obj.OPENAI_API_KEY:
            errors.append("OPENAI_API_KEY is required in production")
        
        if settings_obj.SECRET_KEY == Settings().SECRET_KEY:
            errors.append("SECRET_KEY should be set to a secure value in production")
        
        if "*" in settings_obj.ALLOWED_HOSTS:
            errors.append("ALLOWED_HOSTS should not include '*' in production")
    
    # 验证数据库URL格式
    if not settings_obj.DATABASE_URL.startswith(("postgresql://", "postgresql+asyncpg://")):
        errors.append("DATABASE_URL must be a valid PostgreSQL URL")
    
    # 验证Redis URL格式
    if not settings_obj.REDIS_URL.startswith("redis://"):
        errors.append("REDIS_URL must be a valid Redis URL")
    
    if errors:
        raise ValueError(f"Configuration validation failed: {'; '.join(errors)}")
    
    return True


# 导出配置实例
settings = get_settings()

# 验证配置（仅在生产环境）
if settings.is_production:
    validate_settings(settings)