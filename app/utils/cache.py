"""
AI教学助手系统 - 缓存管理器
提供Redis缓存功能，用于提高AI分析性能

Author: AI Backend Architecture Expert
Date: 2025-09-10
"""

import asyncio
import json
import logging
from typing import Any, Optional, Dict, List
from datetime import datetime, timedelta
import redis.asyncio as redis
import pickle

from ..core.config import settings

logger = logging.getLogger(__name__)


class CacheManager:
    """
    缓存管理器
    
    提供Redis缓存功能，支持JSON和Pickle序列化
    """
    
    def __init__(self):
        self.redis_client: Optional[redis.Redis] = None
        self.is_connected = False
        self.default_expire_time = settings.REDIS_EXPIRE_TIME
    
    async def connect(self):
        """连接Redis"""
        try:
            self.redis_client = redis.from_url(
                settings.REDIS_URL,
                encoding="utf-8",
                decode_responses=False,  # 使用bytes以支持pickle
                socket_connect_timeout=5,
                socket_timeout=5,
                retry_on_timeout=True
            )
            
            # 测试连接
            await self.redis_client.ping()
            self.is_connected = True
            
            logger.info("Redis connection established successfully")
            
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {str(e)}")
            self.is_connected = False
            raise
    
    async def disconnect(self):
        """断开Redis连接"""
        if self.redis_client:
            await self.redis_client.close()
            self.is_connected = False
            logger.info("Redis connection closed")
    
    async def _ensure_connection(self):
        """确保Redis连接"""
        if not self.is_connected or not self.redis_client:
            await self.connect()
    
    async def set(
        self, 
        key: str, 
        value: Any, 
        expire_time: Optional[int] = None,
        serializer: str = "json"
    ) -> bool:
        """
        设置缓存值
        
        Args:
            key: 缓存键
            value: 缓存值
            expire_time: 过期时间（秒）
            serializer: 序列化方式（json/pickle）
            
        Returns:
            bool: 是否设置成功
        """
        try:
            await self._ensure_connection()
            
            # 序列化数据
            if serializer == "json":
                serialized_value = json.dumps(value, ensure_ascii=False)
            elif serializer == "pickle":
                serialized_value = pickle.dumps(value)
            else:
                raise ValueError(f"Unsupported serializer: {serializer}")
            
            # 设置过期时间
            ex = expire_time if expire_time is not None else self.default_expire_time
            
            # 存储到Redis
            result = await self.redis_client.set(
                self._make_key(key), 
                serialized_value, 
                ex=ex
            )
            
            return result is True
            
        except Exception as e:
            logger.error(f"Failed to set cache key {key}: {str(e)}")
            return False
    
    async def get(
        self, 
        key: str, 
        serializer: str = "json"
    ) -> Optional[Any]:
        """
        获取缓存值
        
        Args:
            key: 缓存键
            serializer: 序列化方式（json/pickle）
            
        Returns:
            Any: 缓存值，不存在时返回None
        """
        try:
            await self._ensure_connection()
            
            value = await self.redis_client.get(self._make_key(key))
            
            if value is None:
                return None
            
            # 反序列化数据
            if serializer == "json":
                return json.loads(value.decode('utf-8'))
            elif serializer == "pickle":
                return pickle.loads(value)
            else:
                raise ValueError(f"Unsupported serializer: {serializer}")
                
        except Exception as e:
            logger.error(f"Failed to get cache key {key}: {str(e)}")
            return None
    
    async def delete(self, key: str) -> bool:
        """
        删除缓存键
        
        Args:
            key: 缓存键
            
        Returns:
            bool: 是否删除成功
        """
        try:
            await self._ensure_connection()
            result = await self.redis_client.delete(self._make_key(key))
            return result > 0
            
        except Exception as e:
            logger.error(f"Failed to delete cache key {key}: {str(e)}")
            return False
    
    async def exists(self, key: str) -> bool:
        """
        检查缓存键是否存在
        
        Args:
            key: 缓存键
            
        Returns:
            bool: 是否存在
        """
        try:
            await self._ensure_connection()
            result = await self.redis_client.exists(self._make_key(key))
            return result > 0
            
        except Exception as e:
            logger.error(f"Failed to check cache key existence {key}: {str(e)}")
            return False
    
    async def expire(self, key: str, expire_time: int) -> bool:
        """
        设置缓存键过期时间
        
        Args:
            key: 缓存键
            expire_time: 过期时间（秒）
            
        Returns:
            bool: 是否设置成功
        """
        try:
            await self._ensure_connection()
            result = await self.redis_client.expire(self._make_key(key), expire_time)
            return result is True
            
        except Exception as e:
            logger.error(f"Failed to set expiry for cache key {key}: {str(e)}")
            return False
    
    async def ttl(self, key: str) -> int:
        """
        获取缓存键剩余生存时间
        
        Args:
            key: 缓存键
            
        Returns:
            int: 剩余生存时间（秒），-1表示永不过期，-2表示不存在
        """
        try:
            await self._ensure_connection()
            return await self.redis_client.ttl(self._make_key(key))
            
        except Exception as e:
            logger.error(f"Failed to get TTL for cache key {key}: {str(e)}")
            return -2
    
    async def increment(self, key: str, amount: int = 1) -> int:
        """
        递增缓存值
        
        Args:
            key: 缓存键
            amount: 递增量
            
        Returns:
            int: 递增后的值
        """
        try:
            await self._ensure_connection()
            return await self.redis_client.incrby(self._make_key(key), amount)
            
        except Exception as e:
            logger.error(f"Failed to increment cache key {key}: {str(e)}")
            raise
    
    async def decrement(self, key: str, amount: int = 1) -> int:
        """
        递减缓存值
        
        Args:
            key: 缓存键
            amount: 递减量
            
        Returns:
            int: 递减后的值
        """
        try:
            await self._ensure_connection()
            return await self.redis_client.decrby(self._make_key(key), amount)
            
        except Exception as e:
            logger.error(f"Failed to decrement cache key {key}: {str(e)}")
            raise
    
    async def hash_set(self, name: str, mapping: Dict[str, Any]) -> int:
        """
        设置Hash结构
        
        Args:
            name: Hash名称
            mapping: 字段映射
            
        Returns:
            int: 新添加的字段数量
        """
        try:
            await self._ensure_connection()
            
            # 序列化值
            serialized_mapping = {}
            for field, value in mapping.items():
                serialized_mapping[field] = json.dumps(value, ensure_ascii=False)
            
            return await self.redis_client.hset(
                self._make_key(name), 
                mapping=serialized_mapping
            )
            
        except Exception as e:
            logger.error(f"Failed to set hash {name}: {str(e)}")
            return 0
    
    async def hash_get(self, name: str, field: str) -> Optional[Any]:
        """
        获取Hash字段值
        
        Args:
            name: Hash名称
            field: 字段名
            
        Returns:
            Any: 字段值
        """
        try:
            await self._ensure_connection()
            value = await self.redis_client.hget(self._make_key(name), field)
            
            if value is None:
                return None
            
            return json.loads(value.decode('utf-8'))
            
        except Exception as e:
            logger.error(f"Failed to get hash field {name}:{field}: {str(e)}")
            return None
    
    async def hash_get_all(self, name: str) -> Dict[str, Any]:
        """
        获取Hash所有字段
        
        Args:
            name: Hash名称
            
        Returns:
            Dict: 所有字段的映射
        """
        try:
            await self._ensure_connection()
            hash_data = await self.redis_client.hgetall(self._make_key(name))
            
            result = {}
            for field, value in hash_data.items():
                try:
                    result[field.decode('utf-8')] = json.loads(value.decode('utf-8'))
                except json.JSONDecodeError:
                    result[field.decode('utf-8')] = value.decode('utf-8')
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to get all hash fields {name}: {str(e)}")
            return {}
    
    async def list_push(self, key: str, *values: Any) -> int:
        """
        向列表末尾添加元素
        
        Args:
            key: 列表键
            values: 要添加的值
            
        Returns:
            int: 列表长度
        """
        try:
            await self._ensure_connection()
            
            # 序列化值
            serialized_values = [json.dumps(v, ensure_ascii=False) for v in values]
            
            return await self.redis_client.rpush(
                self._make_key(key), 
                *serialized_values
            )
            
        except Exception as e:
            logger.error(f"Failed to push to list {key}: {str(e)}")
            return 0
    
    async def list_pop(self, key: str, from_left: bool = False) -> Optional[Any]:
        """
        从列表弹出元素
        
        Args:
            key: 列表键
            from_left: 是否从左侧弹出
            
        Returns:
            Any: 弹出的元素
        """
        try:
            await self._ensure_connection()
            
            if from_left:
                value = await self.redis_client.lpop(self._make_key(key))
            else:
                value = await self.redis_client.rpop(self._make_key(key))
            
            if value is None:
                return None
            
            return json.loads(value.decode('utf-8'))
            
        except Exception as e:
            logger.error(f"Failed to pop from list {key}: {str(e)}")
            return None
    
    async def list_range(self, key: str, start: int = 0, end: int = -1) -> List[Any]:
        """
        获取列表范围内的元素
        
        Args:
            key: 列表键
            start: 开始索引
            end: 结束索引
            
        Returns:
            List: 元素列表
        """
        try:
            await self._ensure_connection()
            values = await self.redis_client.lrange(self._make_key(key), start, end)
            
            result = []
            for value in values:
                try:
                    result.append(json.loads(value.decode('utf-8')))
                except json.JSONDecodeError:
                    result.append(value.decode('utf-8'))
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to get list range {key}: {str(e)}")
            return []
    
    async def set_add(self, key: str, *values: Any) -> int:
        """
        向集合添加元素
        
        Args:
            key: 集合键
            values: 要添加的值
            
        Returns:
            int: 新增元素数量
        """
        try:
            await self._ensure_connection()
            
            # 序列化值
            serialized_values = [json.dumps(v, ensure_ascii=False) for v in values]
            
            return await self.redis_client.sadd(
                self._make_key(key), 
                *serialized_values
            )
            
        except Exception as e:
            logger.error(f"Failed to add to set {key}: {str(e)}")
            return 0
    
    async def set_members(self, key: str) -> set:
        """
        获取集合所有成员
        
        Args:
            key: 集合键
            
        Returns:
            set: 成员集合
        """
        try:
            await self._ensure_connection()
            members = await self.redis_client.smembers(self._make_key(key))
            
            result = set()
            for member in members:
                try:
                    result.add(json.loads(member.decode('utf-8')))
                except json.JSONDecodeError:
                    result.add(member.decode('utf-8'))
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to get set members {key}: {str(e)}")
            return set()
    
    async def clear_pattern(self, pattern: str) -> int:
        """
        清除匹配模式的所有键
        
        Args:
            pattern: 匹配模式
            
        Returns:
            int: 删除的键数量
        """
        try:
            await self._ensure_connection()
            
            keys = await self.redis_client.keys(self._make_key(pattern))
            if keys:
                return await self.redis_client.delete(*keys)
            return 0
            
        except Exception as e:
            logger.error(f"Failed to clear pattern {pattern}: {str(e)}")
            return 0
    
    async def get_stats(self) -> Dict[str, Any]:
        """
        获取缓存统计信息
        
        Returns:
            Dict: 统计信息
        """
        try:
            await self._ensure_connection()
            
            info = await self.redis_client.info()
            
            return {
                "connected_clients": info.get("connected_clients", 0),
                "used_memory": info.get("used_memory", 0),
                "used_memory_human": info.get("used_memory_human", "0B"),
                "keyspace_hits": info.get("keyspace_hits", 0),
                "keyspace_misses": info.get("keyspace_misses", 0),
                "total_commands_processed": info.get("total_commands_processed", 0),
                "redis_version": info.get("redis_version", "unknown"),
                "uptime_in_seconds": info.get("uptime_in_seconds", 0)
            }
            
        except Exception as e:
            logger.error(f"Failed to get cache stats: {str(e)}")
            return {}
    
    def _make_key(self, key: str) -> str:
        """生成完整的缓存键"""
        return f"ai_teacher:{key}"
    
    async def close(self):
        """关闭缓存连接"""
        await self.disconnect()


# 缓存装饰器
def cache_result(
    expire_time: int = None,
    key_prefix: str = "cache",
    serializer: str = "json"
):
    """
    缓存结果装饰器
    
    Args:
        expire_time: 过期时间
        key_prefix: 键前缀
        serializer: 序列化方式
    """
    def decorator(func):
        async def wrapper(*args, **kwargs):
            # 生成缓存键
            import hashlib
            key_data = f"{func.__name__}:{str(args)}:{str(kwargs)}"
            cache_key = f"{key_prefix}:{hashlib.md5(key_data.encode()).hexdigest()}"
            
            # 尝试获取缓存
            cache_manager = CacheManager()
            cached_result = await cache_manager.get(cache_key, serializer)
            
            if cached_result is not None:
                await cache_manager.close()
                return cached_result
            
            # 执行函数并缓存结果
            result = await func(*args, **kwargs)
            await cache_manager.set(cache_key, result, expire_time, serializer)
            await cache_manager.close()
            
            return result
            
        return wrapper
    return decorator


# 导出
__all__ = ["CacheManager", "cache_result"]