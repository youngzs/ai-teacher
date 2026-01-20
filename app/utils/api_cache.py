"""
AI教学助手系统 - API响应缓存优化 (Sprint 5)
提供高级缓存策略，包括内容寻址缓存和多层缓存

Author: AI Backend Architecture Expert
Date: Sprint 5
"""

import hashlib
import json
import time
from typing import Any, Callable, Optional, Dict, Union
from functools import wraps
from dataclasses import dataclass
from enum import Enum

from .cache import CacheManager
from ..core.metrics import (
    ai_cache_operations_total,
    record_cache_operation,
)
from ..utils.structured_logging import get_structured_logger

logger = get_structured_logger(__name__)


class CacheStrategy(Enum):
    """缓存策略"""
    CACHE_ASIDE = "cache_aside"  # 常规缓存
    CONTENT_HASH = "content_hash"  # 内容哈希寻址
    WRITE_THROUGH = "write_through"  # 写穿缓存
    READ_THROUGH = "read_through"  # 读穿缓存


@dataclass
class CacheConfig:
    """缓存配置"""
    ttl: int  # 过期时间（秒）
    strategy: CacheStrategy
    key_prefix: str = ""
    warmup: bool = False  # 是否预热
    compress: bool = False  # 是否压缩


# 预定义的缓存配置
CACHE_CONFIGS: Dict[str, CacheConfig] = {
    # 静态数据 - 长期缓存
    "course_list": CacheConfig(
        ttl=3600,  # 1小时
        strategy=CacheStrategy.CACHE_ASIDE,
        key_prefix="courses"
    ),
    "supported_languages": CacheConfig(
        ttl=86400,  # 24小时
        strategy=CacheStrategy.CACHE_ASIDE,
        key_prefix="languages"
    ),
    "exercise_list": CacheConfig(
        ttl=1800,  # 30分钟
        strategy=CacheStrategy.CACHE_ASIDE,
        key_prefix="exercises"
    ),

    # 用户数据 - 短期缓存
    "user_profile": CacheConfig(
        ttl=300,  # 5分钟
        strategy=CacheStrategy.CACHE_ASIDE,
        key_prefix="user"
    ),
    "user_submissions": CacheConfig(
        ttl=60,  # 1分钟
        strategy=CacheStrategy.CACHE_ASIDE,
        key_prefix="submissions"
    ),
    "user_progress": CacheConfig(
        ttl=120,  # 2分钟
        strategy=CacheStrategy.CACHE_ASIDE,
        key_prefix="progress"
    ),

    # AI分析 - 内容寻址缓存
    "ai_analysis": CacheConfig(
        ttl=1800,  # 30分钟
        strategy=CacheStrategy.CONTENT_HASH,
        key_prefix="ai_analysis"
    ),
    "ai_feedback": CacheConfig(
        ttl=1800,  # 30分钟
        strategy=CacheStrategy.CONTENT_HASH,
        key_prefix="ai_feedback"
    ),

    # 仪表盘数据
    "dashboard_stats": CacheConfig(
        ttl=60,  # 1分钟
        strategy=CacheStrategy.CACHE_ASIDE,
        key_prefix="dashboard"
    ),
    "class_analytics": CacheConfig(
        ttl=300,  # 5分钟
        strategy=CacheStrategy.CACHE_ASIDE,
        key_prefix="analytics"
    ),
}


class APICacheManager:
    """
    API响应缓存管理器

    提供高级缓存功能：
    - 多层缓存策略
    - 内容寻址缓存
    - 缓存指标收集
    - 缓存预热
    """

    def __init__(self, cache_manager: Optional[CacheManager] = None):
        self._cache = cache_manager or CacheManager()
        self._local_cache: Dict[str, tuple] = {}  # 本地内存缓存 (value, expire_time)
        self._local_cache_max_size = 1000
        self._stats = {
            "hits": 0,
            "misses": 0,
            "local_hits": 0,
        }

    async def connect(self):
        """连接缓存后端"""
        await self._cache.connect()

    async def close(self):
        """关闭缓存连接"""
        await self._cache.close()

    def _generate_content_hash(self, content: Any) -> str:
        """生成内容哈希"""
        content_str = json.dumps(content, sort_keys=True, ensure_ascii=False)
        return hashlib.sha256(content_str.encode()).hexdigest()[:16]

    def _build_cache_key(
        self,
        config: CacheConfig,
        key_parts: list,
        content: Optional[Any] = None
    ) -> str:
        """构建缓存键"""
        if config.strategy == CacheStrategy.CONTENT_HASH and content is not None:
            content_hash = self._generate_content_hash(content)
            return f"{config.key_prefix}:hash:{content_hash}"
        else:
            return f"{config.key_prefix}:{':'.join(str(p) for p in key_parts)}"

    def _check_local_cache(self, key: str) -> Optional[Any]:
        """检查本地缓存"""
        if key in self._local_cache:
            value, expire_time = self._local_cache[key]
            if time.time() < expire_time:
                self._stats["local_hits"] += 1
                return value
            else:
                # 过期，删除
                del self._local_cache[key]
        return None

    def _set_local_cache(self, key: str, value: Any, ttl: int):
        """设置本地缓存"""
        # 简单的LRU：如果满了，删除最旧的
        if len(self._local_cache) >= self._local_cache_max_size:
            oldest_key = next(iter(self._local_cache))
            del self._local_cache[oldest_key]

        self._local_cache[key] = (value, time.time() + ttl)

    async def get(
        self,
        config_name: str,
        key_parts: list,
        content_for_hash: Optional[Any] = None
    ) -> Optional[Any]:
        """
        获取缓存值

        Args:
            config_name: 缓存配置名称
            key_parts: 键组成部分
            content_for_hash: 用于内容哈希的内容

        Returns:
            缓存的值或None
        """
        config = CACHE_CONFIGS.get(config_name)
        if not config:
            logger.warning(f"Unknown cache config: {config_name}")
            return None

        cache_key = self._build_cache_key(config, key_parts, content_for_hash)

        # 先检查本地缓存
        local_value = self._check_local_cache(cache_key)
        if local_value is not None:
            return local_value

        # 从Redis获取
        try:
            value = await self._cache.get(cache_key)

            if value is not None:
                self._stats["hits"] += 1
                record_cache_operation("hit")
                ai_cache_operations_total.labels(operation="hit").inc()

                # 写入本地缓存
                self._set_local_cache(cache_key, value, min(config.ttl, 60))

                return value
            else:
                self._stats["misses"] += 1
                record_cache_operation("miss")
                ai_cache_operations_total.labels(operation="miss").inc()
                return None

        except Exception as e:
            logger.error(f"Cache get error: {e}", cache_key=cache_key)
            return None

    async def set(
        self,
        config_name: str,
        key_parts: list,
        value: Any,
        content_for_hash: Optional[Any] = None
    ) -> bool:
        """
        设置缓存值

        Args:
            config_name: 缓存配置名称
            key_parts: 键组成部分
            value: 要缓存的值
            content_for_hash: 用于内容哈希的内容

        Returns:
            是否设置成功
        """
        config = CACHE_CONFIGS.get(config_name)
        if not config:
            logger.warning(f"Unknown cache config: {config_name}")
            return False

        cache_key = self._build_cache_key(config, key_parts, content_for_hash)

        try:
            success = await self._cache.set(cache_key, value, config.ttl)

            if success:
                record_cache_operation("set")
                ai_cache_operations_total.labels(operation="set").inc()

                # 同时写入本地缓存
                self._set_local_cache(cache_key, value, min(config.ttl, 60))

            return success

        except Exception as e:
            logger.error(f"Cache set error: {e}", cache_key=cache_key)
            return False

    async def invalidate(
        self,
        config_name: str,
        key_parts: list,
        content_for_hash: Optional[Any] = None
    ) -> bool:
        """
        使缓存失效

        Args:
            config_name: 缓存配置名称
            key_parts: 键组成部分
            content_for_hash: 用于内容哈希的内容

        Returns:
            是否成功
        """
        config = CACHE_CONFIGS.get(config_name)
        if not config:
            return False

        cache_key = self._build_cache_key(config, key_parts, content_for_hash)

        # 删除本地缓存
        if cache_key in self._local_cache:
            del self._local_cache[cache_key]

        # 删除Redis缓存
        try:
            return await self._cache.delete(cache_key)
        except Exception as e:
            logger.error(f"Cache invalidate error: {e}", cache_key=cache_key)
            return False

    async def invalidate_pattern(self, config_name: str, pattern: str) -> int:
        """
        按模式使缓存失效

        Args:
            config_name: 缓存配置名称
            pattern: 匹配模式

        Returns:
            删除的键数量
        """
        config = CACHE_CONFIGS.get(config_name)
        if not config:
            return 0

        full_pattern = f"{config.key_prefix}:{pattern}"

        # 清除匹配的本地缓存
        keys_to_delete = [
            k for k in self._local_cache
            if k.startswith(config.key_prefix)
        ]
        for key in keys_to_delete:
            del self._local_cache[key]

        # 清除Redis缓存
        try:
            return await self._cache.clear_pattern(full_pattern)
        except Exception as e:
            logger.error(f"Cache invalidate pattern error: {e}", pattern=full_pattern)
            return 0

    def get_stats(self) -> Dict[str, Any]:
        """获取缓存统计"""
        total = self._stats["hits"] + self._stats["misses"]
        hit_rate = self._stats["hits"] / total if total > 0 else 0

        return {
            **self._stats,
            "hit_rate": hit_rate,
            "local_cache_size": len(self._local_cache),
        }

    def clear_local_cache(self):
        """清除本地缓存"""
        self._local_cache.clear()


def cached_api_response(
    config_name: str,
    key_builder: Optional[Callable[..., list]] = None,
    content_hash_from: Optional[str] = None
):
    """
    API响应缓存装饰器

    Args:
        config_name: 缓存配置名称
        key_builder: 自定义键构建函数，接收函数参数返回键部分列表
        content_hash_from: 用于内容哈希的参数名

    Usage:
        @cached_api_response("user_profile", key_builder=lambda user_id: [user_id])
        async def get_user_profile(user_id: str):
            ...

        @cached_api_response("ai_analysis", content_hash_from="code")
        async def analyze_code(code: str, language: str):
            ...
    """
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # 构建缓存键
            if key_builder:
                key_parts = key_builder(*args, **kwargs)
            else:
                key_parts = list(args) + [f"{k}={v}" for k, v in sorted(kwargs.items())]

            # 获取内容哈希的内容
            content_for_hash = None
            if content_hash_from and content_hash_from in kwargs:
                content_for_hash = kwargs[content_hash_from]

            # 创建缓存管理器
            cache_mgr = APICacheManager()

            try:
                await cache_mgr.connect()

                # 尝试获取缓存
                cached_value = await cache_mgr.get(
                    config_name,
                    key_parts,
                    content_for_hash
                )

                if cached_value is not None:
                    logger.debug(
                        f"Cache hit for {func.__name__}",
                        config=config_name
                    )
                    return cached_value

                # 执行函数
                result = await func(*args, **kwargs)

                # 缓存结果
                await cache_mgr.set(
                    config_name,
                    key_parts,
                    result,
                    content_for_hash
                )

                return result

            finally:
                await cache_mgr.close()

        return wrapper
    return decorator


def cache_ai_analysis(code: str, language: str, analysis_type: str):
    """
    AI分析结果缓存键生成器

    基于代码内容生成唯一的缓存键
    """
    content = {
        "code": code,
        "language": language,
        "analysis_type": analysis_type
    }
    content_hash = hashlib.sha256(
        json.dumps(content, sort_keys=True).encode()
    ).hexdigest()[:16]

    return f"ai_analysis:{language}:{analysis_type}:{content_hash}"


# 全局缓存实例
_api_cache: Optional[APICacheManager] = None


async def get_api_cache() -> APICacheManager:
    """获取全局API缓存实例"""
    global _api_cache
    if _api_cache is None:
        _api_cache = APICacheManager()
        await _api_cache.connect()
    return _api_cache


async def close_api_cache():
    """关闭全局API缓存"""
    global _api_cache
    if _api_cache:
        await _api_cache.close()
        _api_cache = None
