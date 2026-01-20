"""
AI教学助手系统 - 安全加固模块 (Sprint 5)
提供全面的安全功能，包括认证增强、输入验证、审计日志等

Author: AI Backend Architecture Expert
Date: Sprint 5
"""

import re
import hashlib
import hmac
import secrets
import html
from typing import Optional, Dict, Any, List, Set
from datetime import datetime, timedelta
from functools import wraps
from dataclasses import dataclass
from enum import Enum
import ipaddress

from fastapi import Request, HTTPException, status
from pydantic import BaseModel, validator, Field

from ..utils.structured_logging import get_structured_logger

logger = get_structured_logger(__name__)


# ============= 密码策略 =============

class PasswordStrength(Enum):
    """密码强度等级"""
    WEAK = "weak"
    FAIR = "fair"
    GOOD = "good"
    STRONG = "strong"


@dataclass
class PasswordPolicy:
    """密码策略配置"""
    min_length: int = 8
    max_length: int = 128
    require_uppercase: bool = True
    require_lowercase: bool = True
    require_digit: bool = True
    require_special: bool = True
    special_chars: str = "!@#$%^&*()_+-=[]{}|;:,.<>?"
    forbidden_patterns: List[str] = None  # 禁止的模式
    max_consecutive_chars: int = 3  # 最大连续相同字符数

    def __post_init__(self):
        if self.forbidden_patterns is None:
            self.forbidden_patterns = [
                r"password",
                r"123456",
                r"qwerty",
                r"admin",
            ]


DEFAULT_PASSWORD_POLICY = PasswordPolicy()


def validate_password(password: str, policy: PasswordPolicy = DEFAULT_PASSWORD_POLICY) -> tuple[bool, List[str]]:
    """
    验证密码是否符合策略

    Returns:
        (是否有效, 错误消息列表)
    """
    errors = []

    # 长度检查
    if len(password) < policy.min_length:
        errors.append(f"密码长度至少{policy.min_length}位")
    if len(password) > policy.max_length:
        errors.append(f"密码长度最多{policy.max_length}位")

    # 字符类型检查
    if policy.require_uppercase and not re.search(r"[A-Z]", password):
        errors.append("密码需要包含大写字母")
    if policy.require_lowercase and not re.search(r"[a-z]", password):
        errors.append("密码需要包含小写字母")
    if policy.require_digit and not re.search(r"\d", password):
        errors.append("密码需要包含数字")
    if policy.require_special and not re.search(f"[{re.escape(policy.special_chars)}]", password):
        errors.append("密码需要包含特殊字符")

    # 禁止模式检查
    password_lower = password.lower()
    for pattern in policy.forbidden_patterns:
        if re.search(pattern, password_lower):
            errors.append("密码包含常见弱密码模式")
            break

    # 连续字符检查
    for i in range(len(password) - policy.max_consecutive_chars):
        if len(set(password[i:i + policy.max_consecutive_chars + 1])) == 1:
            errors.append(f"密码不能包含超过{policy.max_consecutive_chars}个连续相同字符")
            break

    return (len(errors) == 0, errors)


def get_password_strength(password: str) -> PasswordStrength:
    """评估密码强度"""
    score = 0

    # 长度得分
    if len(password) >= 8:
        score += 1
    if len(password) >= 12:
        score += 1
    if len(password) >= 16:
        score += 1

    # 字符类型得分
    if re.search(r"[a-z]", password):
        score += 1
    if re.search(r"[A-Z]", password):
        score += 1
    if re.search(r"\d", password):
        score += 1
    if re.search(r"[!@#$%^&*()_+\-=\[\]{}|;:,.<>?]", password):
        score += 1

    # 熵得分
    unique_chars = len(set(password))
    if unique_chars >= 8:
        score += 1
    if unique_chars >= 12:
        score += 1

    if score >= 8:
        return PasswordStrength.STRONG
    elif score >= 6:
        return PasswordStrength.GOOD
    elif score >= 4:
        return PasswordStrength.FAIR
    else:
        return PasswordStrength.WEAK


# ============= 输入验证 =============

class InputSanitizer:
    """输入净化器"""

    # XSS危险字符
    XSS_PATTERNS = [
        r"<script\b[^>]*>[\s\S]*?</script>",
        r"javascript:",
        r"on\w+\s*=",
        r"<\s*img[^>]+onerror",
        r"<\s*iframe",
        r"<\s*embed",
        r"<\s*object",
    ]

    # SQL注入模式
    SQL_PATTERNS = [
        r"(\b(SELECT|INSERT|UPDATE|DELETE|DROP|UNION|CREATE|ALTER)\b)",
        r"(--|#|/\*)",
        r"(\bOR\b\s+\d+\s*=\s*\d+)",
        r"(\bAND\b\s+\d+\s*=\s*\d+)",
    ]

    @classmethod
    def sanitize_html(cls, text: str) -> str:
        """净化HTML内容，防止XSS"""
        return html.escape(text)

    @classmethod
    def check_xss(cls, text: str) -> bool:
        """检查是否包含XSS攻击特征"""
        text_lower = text.lower()
        for pattern in cls.XSS_PATTERNS:
            if re.search(pattern, text_lower, re.IGNORECASE):
                return True
        return False

    @classmethod
    def check_sql_injection(cls, text: str) -> bool:
        """检查是否包含SQL注入特征"""
        for pattern in cls.SQL_PATTERNS:
            if re.search(pattern, text, re.IGNORECASE):
                return True
        return False

    @classmethod
    def sanitize_filename(cls, filename: str) -> str:
        """净化文件名"""
        # 移除路径分隔符
        filename = re.sub(r"[/\\]", "", filename)
        # 移除危险字符
        filename = re.sub(r"[<>:\"|?*]", "", filename)
        # 移除控制字符
        filename = re.sub(r"[\x00-\x1f\x7f]", "", filename)
        # 移除前导点（防止隐藏文件）
        filename = filename.lstrip(".")
        # 限制长度
        return filename[:255]

    @classmethod
    def validate_email(cls, email: str) -> bool:
        """验证邮箱格式"""
        pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        return bool(re.match(pattern, email))

    @classmethod
    def validate_url(cls, url: str) -> bool:
        """验证URL格式"""
        pattern = r"^https?://[a-zA-Z0-9.-]+(?:/[a-zA-Z0-9._~:/?#\[\]@!$&'()*+,;=-]*)?$"
        return bool(re.match(pattern, url))


# ============= 速率限制 =============

class RateLimiter:
    """
    速率限制器

    基于令牌桶算法
    """

    def __init__(self):
        self._buckets: Dict[str, Dict] = {}

    def _get_bucket(self, key: str, limit: int, window: int) -> Dict:
        """获取或创建令牌桶"""
        now = datetime.utcnow()

        if key not in self._buckets:
            self._buckets[key] = {
                "tokens": limit,
                "last_refill": now,
                "limit": limit,
                "window": window,
            }
        return self._buckets[key]

    def _refill_tokens(self, bucket: Dict) -> None:
        """补充令牌"""
        now = datetime.utcnow()
        elapsed = (now - bucket["last_refill"]).total_seconds()

        # 计算应该补充的令牌数
        refill_rate = bucket["limit"] / bucket["window"]
        new_tokens = elapsed * refill_rate

        bucket["tokens"] = min(bucket["limit"], bucket["tokens"] + new_tokens)
        bucket["last_refill"] = now

    def check_rate_limit(
        self,
        key: str,
        limit: int = 100,
        window: int = 60
    ) -> tuple[bool, Dict[str, Any]]:
        """
        检查速率限制

        Args:
            key: 限制键（如用户ID或IP）
            limit: 窗口内允许的请求数
            window: 时间窗口（秒）

        Returns:
            (是否允许, 限制信息)
        """
        bucket = self._get_bucket(key, limit, window)
        self._refill_tokens(bucket)

        info = {
            "remaining": int(bucket["tokens"]),
            "limit": limit,
            "reset": int(bucket["window"] - (datetime.utcnow() - bucket["last_refill"]).total_seconds()),
        }

        if bucket["tokens"] >= 1:
            bucket["tokens"] -= 1
            return (True, info)
        else:
            return (False, info)

    def cleanup_expired(self, max_age: int = 3600) -> int:
        """清理过期的桶"""
        now = datetime.utcnow()
        expired_keys = [
            key for key, bucket in self._buckets.items()
            if (now - bucket["last_refill"]).total_seconds() > max_age
        ]

        for key in expired_keys:
            del self._buckets[key]

        return len(expired_keys)


# 预配置的速率限制
RATE_LIMITS = {
    "auth_login": {"limit": 5, "window": 60},  # 每分钟5次登录尝试
    "auth_register": {"limit": 3, "window": 300},  # 每5分钟3次注册
    "api_default": {"limit": 100, "window": 60},  # 每分钟100次API调用
    "code_execution": {"limit": 10, "window": 60},  # 每分钟10次代码执行
    "ai_analysis": {"limit": 20, "window": 60},  # 每分钟20次AI分析
}


# 全局速率限制器实例
rate_limiter = RateLimiter()


# ============= CSRF保护 =============

class CSRFProtection:
    """CSRF保护"""

    TOKEN_LENGTH = 32
    COOKIE_NAME = "csrf_token"
    HEADER_NAME = "X-CSRF-Token"

    @classmethod
    def generate_token(cls) -> str:
        """生成CSRF令牌"""
        return secrets.token_urlsafe(cls.TOKEN_LENGTH)

    @classmethod
    def validate_token(cls, token: str, expected: str) -> bool:
        """验证CSRF令牌（时间常量比较）"""
        if not token or not expected:
            return False
        return hmac.compare_digest(token, expected)


# ============= IP黑名单 =============

class IPBlacklist:
    """IP黑名单管理"""

    def __init__(self):
        self._blacklist: Set[str] = set()
        self._whitelist: Set[str] = set()
        # 可疑IP计数
        self._suspicious: Dict[str, int] = {}
        self._threshold = 10  # 可疑行为阈值

    def add_to_blacklist(self, ip: str, reason: str = "") -> None:
        """添加到黑名单"""
        self._blacklist.add(ip)
        logger.warning(f"IP added to blacklist: {ip}", reason=reason)

    def add_to_whitelist(self, ip: str) -> None:
        """添加到白名单"""
        self._whitelist.add(ip)

    def is_blocked(self, ip: str) -> bool:
        """检查IP是否被封禁"""
        if ip in self._whitelist:
            return False
        return ip in self._blacklist

    def record_suspicious_activity(self, ip: str) -> bool:
        """
        记录可疑活动

        Returns:
            是否触发自动封禁
        """
        self._suspicious[ip] = self._suspicious.get(ip, 0) + 1

        if self._suspicious[ip] >= self._threshold:
            self.add_to_blacklist(ip, "Automatic: exceeded suspicious activity threshold")
            return True
        return False

    def remove_from_blacklist(self, ip: str) -> None:
        """从黑名单移除"""
        self._blacklist.discard(ip)

    def clear_suspicious(self, ip: str) -> None:
        """清除可疑计数"""
        self._suspicious.pop(ip, None)


# 全局IP黑名单实例
ip_blacklist = IPBlacklist()


# ============= 审计日志 =============

class AuditAction(Enum):
    """审计动作类型"""
    USER_LOGIN = "user_login"
    USER_LOGOUT = "user_logout"
    USER_REGISTER = "user_register"
    PASSWORD_CHANGE = "password_change"
    PERMISSION_CHANGE = "permission_change"
    DATA_ACCESS = "data_access"
    DATA_MODIFY = "data_modify"
    DATA_DELETE = "data_delete"
    SECURITY_VIOLATION = "security_violation"
    ADMIN_ACTION = "admin_action"


@dataclass
class AuditLog:
    """审计日志条目"""
    timestamp: datetime
    action: AuditAction
    user_id: Optional[str]
    ip_address: str
    resource: str
    details: Dict[str, Any]
    success: bool


class AuditLogger:
    """审计日志记录器"""

    def __init__(self):
        self._logs: List[AuditLog] = []
        self._max_logs = 10000

    def log(
        self,
        action: AuditAction,
        user_id: Optional[str],
        ip_address: str,
        resource: str,
        details: Dict[str, Any] = None,
        success: bool = True
    ) -> None:
        """记录审计日志"""
        log_entry = AuditLog(
            timestamp=datetime.utcnow(),
            action=action,
            user_id=user_id,
            ip_address=ip_address,
            resource=resource,
            details=details or {},
            success=success,
        )

        self._logs.append(log_entry)

        # 限制内存中的日志数量
        if len(self._logs) > self._max_logs:
            self._logs = self._logs[-self._max_logs:]

        # 同时写入结构化日志
        logger.info(
            f"Audit: {action.value}",
            action=action.value,
            user_id=user_id,
            ip_address=ip_address,
            resource=resource,
            details=details,
            success=success,
        )

    def get_logs(
        self,
        user_id: Optional[str] = None,
        action: Optional[AuditAction] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        limit: int = 100
    ) -> List[AuditLog]:
        """查询审计日志"""
        filtered = self._logs

        if user_id:
            filtered = [log for log in filtered if log.user_id == user_id]
        if action:
            filtered = [log for log in filtered if log.action == action]
        if start_time:
            filtered = [log for log in filtered if log.timestamp >= start_time]
        if end_time:
            filtered = [log for log in filtered if log.timestamp <= end_time]

        return filtered[-limit:]


# 全局审计日志实例
audit_logger = AuditLogger()


# ============= 安全装饰器 =============

def require_rate_limit(limit_type: str = "api_default"):
    """
    速率限制装饰器

    Usage:
        @require_rate_limit("auth_login")
        async def login(...):
            ...
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(request: Request, *args, **kwargs):
            # 获取客户端IP
            client_ip = request.client.host if request.client else "unknown"

            # 检查IP黑名单
            if ip_blacklist.is_blocked(client_ip):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Access denied"
                )

            # 检查速率限制
            limit_config = RATE_LIMITS.get(limit_type, RATE_LIMITS["api_default"])
            allowed, info = rate_limiter.check_rate_limit(
                f"{limit_type}:{client_ip}",
                limit_config["limit"],
                limit_config["window"]
            )

            if not allowed:
                ip_blacklist.record_suspicious_activity(client_ip)
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail="Rate limit exceeded",
                    headers={
                        "X-RateLimit-Remaining": str(info["remaining"]),
                        "X-RateLimit-Limit": str(info["limit"]),
                        "X-RateLimit-Reset": str(info["reset"]),
                    }
                )

            return await func(request, *args, **kwargs)
        return wrapper
    return decorator


def audit_action(action: AuditAction, resource: str):
    """
    审计日志装饰器

    Usage:
        @audit_action(AuditAction.DATA_MODIFY, "user_profile")
        async def update_profile(...):
            ...
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(request: Request, *args, **kwargs):
            client_ip = request.client.host if request.client else "unknown"
            user_id = getattr(request.state, "user_id", None)

            success = False
            try:
                result = await func(request, *args, **kwargs)
                success = True
                return result
            finally:
                audit_logger.log(
                    action=action,
                    user_id=user_id,
                    ip_address=client_ip,
                    resource=resource,
                    details={"args": str(args)[:100]},
                    success=success,
                )
        return wrapper
    return decorator


def validate_input(*validators):
    """
    输入验证装饰器

    Usage:
        @validate_input(check_xss, check_sql_injection)
        async def process_input(data: str):
            ...
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # 验证所有字符串参数
            for arg in args:
                if isinstance(arg, str):
                    for validator in validators:
                        if validator(arg):
                            raise HTTPException(
                                status_code=status.HTTP_400_BAD_REQUEST,
                                detail="Invalid input detected"
                            )

            for key, value in kwargs.items():
                if isinstance(value, str):
                    for validator in validators:
                        if validator(value):
                            raise HTTPException(
                                status_code=status.HTTP_400_BAD_REQUEST,
                                detail=f"Invalid input in {key}"
                            )

            return await func(*args, **kwargs)
        return wrapper
    return decorator


# ============= 安全头部增强 =============

class EnhancedSecurityHeaders:
    """增强的安全头部"""

    @staticmethod
    def get_headers() -> Dict[str, str]:
        """获取所有安全头部"""
        return {
            # 防止XSS
            "X-XSS-Protection": "1; mode=block",
            "X-Content-Type-Options": "nosniff",

            # 防止点击劫持
            "X-Frame-Options": "DENY",

            # CSP策略
            "Content-Security-Policy": (
                "default-src 'self'; "
                "script-src 'self' 'unsafe-inline' 'unsafe-eval'; "
                "style-src 'self' 'unsafe-inline'; "
                "img-src 'self' data: https:; "
                "connect-src 'self' https:; "
                "font-src 'self'; "
                "frame-ancestors 'none';"
            ),

            # 传输安全
            "Strict-Transport-Security": "max-age=31536000; includeSubDomains; preload",

            # 引用策略
            "Referrer-Policy": "strict-origin-when-cross-origin",

            # 权限策略
            "Permissions-Policy": (
                "accelerometer=(), "
                "camera=(), "
                "geolocation=(), "
                "gyroscope=(), "
                "magnetometer=(), "
                "microphone=(), "
                "payment=(), "
                "usb=()"
            ),

            # 缓存控制
            "Cache-Control": "no-store, no-cache, must-revalidate, proxy-revalidate",
            "Pragma": "no-cache",
        }
