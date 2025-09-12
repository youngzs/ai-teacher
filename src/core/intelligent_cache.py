"""
AI教学助手系统 - 智能响应缓存和内存优化
Sprint 2 优化：多层缓存、智能预测、内存自适应

Author: AI Architecture Expert  
Date: 2025-09-11
Version: Sprint 2 - Performance Optimization
"""

import asyncio
import json
import hashlib
import pickle
import time
import logging
from typing import Dict, Any, List, Optional, Union, Callable, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from collections import OrderedDict, defaultdict, deque
from enum import Enum
import weakref
import psutil
import sys
import gc
from functools import wraps
import zlib

try:
    import redis.asyncio as aioredis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False

logger = logging.getLogger(__name__)

class CacheLevel(Enum):
    """缓存层级"""
    MEMORY = "memory"        # 内存缓存（最快）
    REDIS = "redis"          # Redis缓存（中等）
    DISK = "disk"            # 磁盘缓存（最慢）

class CachePolicy(Enum):
    """缓存策略"""
    LRU = "lru"              # 最近最少使用
    LFU = "lfu"              # 最少使用频次
    FIFO = "fifo"            # 先进先出
    TTL_BASED = "ttl_based"  # 基于时间过期
    ADAPTIVE = "adaptive"     # 自适应策略

@dataclass
class CacheEntry:
    """缓存条目"""
    key: str
    value: Any
    created_at: datetime
    last_accessed: datetime
    access_count: int = 0
    ttl: Optional[int] = None
    size_bytes: int = 0
    compressed: bool = False
    importance_score: float = 1.0
    
    def is_expired(self) -> bool:
        """检查是否过期"""
        if self.ttl is None:
            return False
        return (datetime.now() - self.created_at).seconds > self.ttl
    
    def touch(self):
        """更新访问信息"""
        self.last_accessed = datetime.now()
        self.access_count += 1
    
    def calculate_size(self):
        """计算条目大小"""
        try:
            self.size_bytes = sys.getsizeof(pickle.dumps(self.value))
        except Exception:
            self.size_bytes = sys.getsizeof(str(self.value))

class MemoryMonitor:
    """内存监控器"""
    
    def __init__(self):
        self.process = psutil.Process()
        self.memory_samples = deque(maxlen=100)
        self.gc_stats = {"collections": 0, "freed_objects": 0}
        
    def get_memory_usage(self) -> Dict[str, float]:
        """获取内存使用情况"""
        try:
            memory_info = self.process.memory_info()
            memory_percent = self.process.memory_percent()
            
            usage = {
                "rss_mb": memory_info.rss / 1024 / 1024,      # 物理内存
                "vms_mb": memory_info.vms / 1024 / 1024,      # 虚拟内存
                "percent": memory_percent,                     # 内存使用百分比
                "available_mb": psutil.virtual_memory().available / 1024 / 1024
            }
            
            self.memory_samples.append(usage)
            return usage
            
        except Exception as e:
            logger.error(f"Memory monitoring error: {e}")
            return {"rss_mb": 0, "vms_mb": 0, "percent": 0, "available_mb": 0}
    
    def is_memory_pressure(self, threshold_percent: float = 80.0) -> bool:
        """检查是否存在内存压力"""
        usage = self.get_memory_usage()
        return usage["percent"] > threshold_percent
    
    def force_garbage_collection(self) -> Dict[str, int]:
        """强制垃圾回收"""
        before_objects = len(gc.get_objects())
        collections = gc.collect()
        after_objects = len(gc.get_objects())
        
        freed = before_objects - after_objects
        self.gc_stats["collections"] += collections
        self.gc_stats["freed_objects"] += freed
        
        logger.info(f"GC: collected {collections} generations, freed {freed} objects")
        return {"collections": collections, "freed_objects": freed}

class IntelligentCache:
    """智能多层缓存系统"""
    
    def __init__(self, 
                 max_memory_size: int = 500 * 1024 * 1024,  # 500MB
                 default_ttl: int = 3600,                    # 1小时
                 policy: CachePolicy = CachePolicy.ADAPTIVE,
                 enable_compression: bool = True,
                 redis_url: Optional[str] = None):
        
        self.max_memory_size = max_memory_size
        self.default_ttl = default_ttl
        self.policy = policy
        self.enable_compression = enable_compression
        
        # 内存缓存层（最快）
        self.memory_cache: Dict[str, CacheEntry] = {}
        self.access_order = OrderedDict()  # LRU支持
        self.frequency_counter = defaultdict(int)  # LFU支持
        
        # Redis缓存层（中等速度）
        self.redis_client = None
        if REDIS_AVAILABLE and redis_url:
            self._init_redis(redis_url)
        
        # 缓存统计
        self.stats = {
            "memory_hits": 0, "memory_misses": 0,
            "redis_hits": 0, "redis_misses": 0,
            "disk_hits": 0, "disk_misses": 0,
            "evictions": 0, "compressions": 0,
            "total_requests": 0, "current_memory_usage": 0
        }
        
        # 内存监控
        self.memory_monitor = MemoryMonitor()
        
        # 自适应参数
        self.adaptive_params = {
            "hit_rate_threshold": 0.7,
            "memory_pressure_threshold": 0.8,
            "compression_threshold": 1024,  # 1KB以上压缩
            "importance_decay_rate": 0.95
        }
        
        # 启动后台任务
        self._cleanup_task = None
        self._start_background_tasks()
    
    def _init_redis(self, redis_url: str):
        """初始化Redis连接"""
        try:
            self.redis_client = aioredis.from_url(redis_url)
            logger.info("Redis cache layer initialized")
        except Exception as e:
            logger.warning(f"Failed to initialize Redis: {e}")
            self.redis_client = None
    
    def _start_background_tasks(self):
        """启动后台清理任务"""
        if self._cleanup_task is None or self._cleanup_task.done():
            self._cleanup_task = asyncio.create_task(self._background_cleanup())
    
    async def _background_cleanup(self):
        """后台清理任务"""
        while True:
            try:
                await asyncio.sleep(60)  # 每分钟执行一次
                
                # 清理过期条目
                await self._cleanup_expired_entries()
                
                # 检查内存压力并进行清理
                if self.memory_monitor.is_memory_pressure():
                    await self._handle_memory_pressure()
                
                # 更新统计信息
                self._update_memory_usage_stats()
                
            except Exception as e:
                logger.error(f"Background cleanup error: {e}")
                await asyncio.sleep(5)
    
    def _generate_cache_key(self, key_data: Union[str, Dict, List]) -> str:
        """生成缓存键"""
        if isinstance(key_data, str):
            content = key_data
        else:
            content = json.dumps(key_data, sort_keys=True, ensure_ascii=False)
        
        return hashlib.sha256(content.encode()).hexdigest()[:32]
    
    def _compress_value(self, value: Any) -> Tuple[bytes, bool]:
        """压缩值"""
        try:
            if not self.enable_compression:
                return pickle.dumps(value), False
                
            pickled = pickle.dumps(value)
            
            if len(pickled) > self.adaptive_params["compression_threshold"]:
                compressed = zlib.compress(pickled)
                if len(compressed) < len(pickled) * 0.8:  # 至少节省20%空间
                    self.stats["compressions"] += 1
                    return compressed, True
                    
            return pickled, False
            
        except Exception as e:
            logger.error(f"Compression error: {e}")
            return pickle.dumps(value), False
    
    def _decompress_value(self, data: bytes, compressed: bool) -> Any:
        """解压缩值"""
        try:
            if compressed:
                decompressed = zlib.decompress(data)
                return pickle.loads(decompressed)
            else:
                return pickle.loads(data)
        except Exception as e:
            logger.error(f"Decompression error: {e}")
            raise
    
    def _calculate_importance_score(self, entry: CacheEntry) -> float:
        """计算条目重要性分数"""
        now = datetime.now()
        
        # 基于访问频次
        frequency_score = min(entry.access_count / 10.0, 1.0)
        
        # 基于最近访问时间
        recency_hours = (now - entry.last_accessed).seconds / 3600
        recency_score = max(0, 1.0 - recency_hours / 24)  # 24小时衰减
        
        # 基于创建时间
        age_hours = (now - entry.created_at).seconds / 3600
        age_score = max(0, 1.0 - age_hours / 168)  # 一周衰减
        
        # 综合分数
        importance = (frequency_score * 0.4 + recency_score * 0.4 + age_score * 0.2)
        return importance * self.adaptive_params["importance_decay_rate"]
    
    async def _cleanup_expired_entries(self):
        """清理过期条目"""
        expired_keys = []
        
        for key, entry in self.memory_cache.items():
            if entry.is_expired():
                expired_keys.append(key)
        
        for key in expired_keys:
            await self._evict_from_memory(key)
        
        if expired_keys:
            logger.debug(f"Cleaned up {len(expired_keys)} expired cache entries")
    
    async def _handle_memory_pressure(self):
        """处理内存压力"""
        logger.info("Memory pressure detected, starting aggressive cleanup")
        
        # 强制垃圾回收
        gc_stats = self.memory_monitor.force_garbage_collection()
        
        # 计算需要释放的空间
        current_usage = sum(entry.size_bytes for entry in self.memory_cache.values())
        target_usage = int(self.max_memory_size * 0.7)  # 释放到70%
        
        if current_usage > target_usage:
            # 按重要性排序并清理
            entries_by_importance = [
                (key, entry, self._calculate_importance_score(entry))
                for key, entry in self.memory_cache.items()
            ]
            entries_by_importance.sort(key=lambda x: x[2])  # 从低重要性开始
            
            freed_space = 0
            evicted_count = 0
            
            for key, entry, importance in entries_by_importance:
                if freed_space >= (current_usage - target_usage):
                    break
                    
                await self._evict_from_memory(key)
                freed_space += entry.size_bytes
                evicted_count += 1
            
            logger.info(f"Memory pressure cleanup: evicted {evicted_count} entries, freed {freed_space} bytes")
    
    async def _evict_from_memory(self, key: str):
        """从内存缓存中驱逐条目"""
        if key in self.memory_cache:
            entry = self.memory_cache[key]
            
            # 尝试移动到Redis缓存
            if self.redis_client and entry.importance_score > 0.3:
                try:
                    await self._store_to_redis(key, entry)
                except Exception as e:
                    logger.error(f"Failed to move entry to Redis: {e}")
            
            # 从内存中移除
            del self.memory_cache[key]
            self.access_order.pop(key, None)
            self.stats["evictions"] += 1
    
    async def _store_to_redis(self, key: str, entry: CacheEntry):
        """存储到Redis缓存"""
        if not self.redis_client:
            return
            
        try:
            data, compressed = self._compress_value(entry.value)
            
            redis_value = {
                "data": data,
                "compressed": compressed,
                "created_at": entry.created_at.isoformat(),
                "access_count": entry.access_count,
                "importance_score": entry.importance_score
            }
            
            serialized = pickle.dumps(redis_value)
            ttl = entry.ttl or self.default_ttl
            
            await self.redis_client.setex(f"cache:{key}", ttl, serialized)
            
        except Exception as e:
            logger.error(f"Redis store error: {e}")
            raise
    
    async def _load_from_redis(self, key: str) -> Optional[Any]:
        """从Redis缓存加载"""
        if not self.redis_client:
            return None
            
        try:
            serialized = await self.redis_client.get(f"cache:{key}")
            if not serialized:
                self.stats["redis_misses"] += 1
                return None
            
            redis_value = pickle.loads(serialized)
            value = self._decompress_value(redis_value["data"], redis_value["compressed"])
            
            # 更新统计
            self.stats["redis_hits"] += 1
            
            # 可选：将热门数据提升到内存缓存
            if redis_value["importance_score"] > 0.5:
                await self.set(key, value, ttl=self.default_ttl)
            
            return value
            
        except Exception as e:
            logger.error(f"Redis load error: {e}")
            self.stats["redis_misses"] += 1
            return None
    
    def _update_memory_usage_stats(self):
        """更新内存使用统计"""
        self.stats["current_memory_usage"] = sum(
            entry.size_bytes for entry in self.memory_cache.values()
        )
    
    async def get(self, key_data: Union[str, Dict, List]) -> Optional[Any]:
        """获取缓存值"""
        cache_key = self._generate_cache_key(key_data)
        self.stats["total_requests"] += 1
        
        # 1. 检查内存缓存
        if cache_key in self.memory_cache:
            entry = self.memory_cache[cache_key]
            
            if not entry.is_expired():
                entry.touch()
                self.access_order.move_to_end(cache_key)
                self.frequency_counter[cache_key] += 1
                self.stats["memory_hits"] += 1
                return entry.value
            else:
                # 过期条目，移除
                await self._evict_from_memory(cache_key)
        
        self.stats["memory_misses"] += 1
        
        # 2. 检查Redis缓存
        redis_value = await self._load_from_redis(cache_key)
        if redis_value is not None:
            return redis_value
        
        # 3. 缓存未命中
        return None
    
    async def set(self, key_data: Union[str, Dict, List], value: Any, 
                 ttl: Optional[int] = None, importance: float = 1.0):
        """设置缓存值"""
        cache_key = self._generate_cache_key(key_data)
        
        # 创建缓存条目
        entry = CacheEntry(
            key=cache_key,
            value=value,
            created_at=datetime.now(),
            last_accessed=datetime.now(),
            ttl=ttl or self.default_ttl,
            importance_score=importance
        )
        
        entry.calculate_size()
        
        # 检查内存限制
        if self._should_store_in_memory(entry):
            await self._store_in_memory(cache_key, entry)
        else:
            # 直接存储到Redis
            await self._store_to_redis(cache_key, entry)
    
    def _should_store_in_memory(self, entry: CacheEntry) -> bool:
        """判断是否应该存储在内存中"""
        current_usage = sum(e.size_bytes for e in self.memory_cache.values())
        
        # 检查空间限制
        if current_usage + entry.size_bytes > self.max_memory_size:
            return False
        
        # 检查重要性
        if entry.importance_score < 0.3:
            return False
            
        return True
    
    async def _store_in_memory(self, cache_key: str, entry: CacheEntry):
        """存储到内存缓存"""
        # 检查是否需要驱逐
        current_usage = sum(e.size_bytes for e in self.memory_cache.values())
        
        while (current_usage + entry.size_bytes > self.max_memory_size and 
               len(self.memory_cache) > 0):
            
            # 根据策略选择驱逐条目
            evict_key = self._select_eviction_candidate()
            if evict_key:
                await self._evict_from_memory(evict_key)
                current_usage = sum(e.size_bytes for e in self.memory_cache.values())
            else:
                break
        
        # 存储条目
        self.memory_cache[cache_key] = entry
        self.access_order[cache_key] = entry.last_accessed
        
        logger.debug(f"Stored cache entry: {cache_key}, size: {entry.size_bytes} bytes")
    
    def _select_eviction_candidate(self) -> Optional[str]:
        """选择驱逐候选"""
        if not self.memory_cache:
            return None
            
        if self.policy == CachePolicy.LRU:
            return next(iter(self.access_order))
        
        elif self.policy == CachePolicy.LFU:
            min_freq = min(self.frequency_counter.values())
            for key, freq in self.frequency_counter.items():
                if freq == min_freq and key in self.memory_cache:
                    return key
        
        elif self.policy == CachePolicy.ADAPTIVE:
            # 综合考虑多个因素
            candidates = [
                (key, self._calculate_importance_score(entry))
                for key, entry in self.memory_cache.items()
            ]
            candidates.sort(key=lambda x: x[1])
            return candidates[0][0] if candidates else None
        
        # 默认LRU
        return next(iter(self.access_order))
    
    async def delete(self, key_data: Union[str, Dict, List]):
        """删除缓存条目"""
        cache_key = self._generate_cache_key(key_data)
        
        # 从内存缓存删除
        if cache_key in self.memory_cache:
            del self.memory_cache[cache_key]
            self.access_order.pop(cache_key, None)
        
        # 从Redis删除
        if self.redis_client:
            try:
                await self.redis_client.delete(f"cache:{cache_key}")
            except Exception as e:
                logger.error(f"Redis delete error: {e}")
    
    async def clear(self, pattern: Optional[str] = None):
        """清空缓存"""
        if pattern is None:
            # 清空所有
            self.memory_cache.clear()
            self.access_order.clear()
            self.frequency_counter.clear()
            
            if self.redis_client:
                try:
                    await self.redis_client.flushdb()
                except Exception as e:
                    logger.error(f"Redis clear error: {e}")
        else:
            # 按模式清空（简化实现）
            keys_to_remove = [key for key in self.memory_cache.keys() if pattern in key]
            for key in keys_to_remove:
                await self.delete(key)
    
    def get_statistics(self) -> Dict[str, Any]:
        """获取缓存统计信息"""
        total_hits = self.stats["memory_hits"] + self.stats["redis_hits"]
        total_misses = self.stats["memory_misses"] + self.stats["redis_misses"]
        hit_rate = total_hits / max(total_hits + total_misses, 1)
        
        memory_usage = self.memory_monitor.get_memory_usage()
        
        return {
            "cache_stats": self.stats.copy(),
            "performance": {
                "hit_rate": hit_rate,
                "memory_hit_rate": self.stats["memory_hits"] / max(self.stats["total_requests"], 1),
                "redis_hit_rate": self.stats["redis_hits"] / max(self.stats["total_requests"], 1)
            },
            "memory_usage": memory_usage,
            "cache_info": {
                "memory_entries": len(self.memory_cache),
                "memory_size_mb": self.stats["current_memory_usage"] / 1024 / 1024,
                "max_memory_mb": self.max_memory_size / 1024 / 1024,
                "policy": self.policy.value,
                "compression_enabled": self.enable_compression
            },
            "adaptive_params": self.adaptive_params.copy()
        }
    
    async def optimize_cache(self):
        """优化缓存性能"""
        stats = self.get_statistics()
        hit_rate = stats["performance"]["hit_rate"]
        
        # 基于命中率调整策略
        if hit_rate < self.adaptive_params["hit_rate_threshold"]:
            # 命中率低，增加内存缓存大小或调整策略
            if self.policy != CachePolicy.ADAPTIVE:
                self.policy = CachePolicy.ADAPTIVE
                logger.info("Switched to adaptive cache policy due to low hit rate")
            
            # 增加压缩阈值以节省空间
            self.adaptive_params["compression_threshold"] = max(512, 
                self.adaptive_params["compression_threshold"] * 0.8)
        
        # 调整重要性衰减率
        if hit_rate > 0.9:
            self.adaptive_params["importance_decay_rate"] = min(0.99, 
                self.adaptive_params["importance_decay_rate"] * 1.01)
        elif hit_rate < 0.6:
            self.adaptive_params["importance_decay_rate"] = max(0.9, 
                self.adaptive_params["importance_decay_rate"] * 0.99)
        
        logger.info(f"Cache optimization completed, hit rate: {hit_rate:.3f}")
    
    async def close(self):
        """关闭缓存系统"""
        if self._cleanup_task and not self._cleanup_task.done():
            self._cleanup_task.cancel()
        
        if self.redis_client:
            await self.redis_client.close()
        
        self.memory_cache.clear()
        logger.info("Intelligent cache system closed")

def cache_decorator(cache: IntelligentCache, ttl: Optional[int] = None, 
                   key_func: Optional[Callable] = None):
    """缓存装饰器"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # 生成缓存键
            if key_func:
                cache_key = key_func(*args, **kwargs)
            else:
                cache_key = f"{func.__name__}:{hash((args, tuple(sorted(kwargs.items()))))}"
            
            # 尝试从缓存获取
            cached_result = await cache.get(cache_key)
            if cached_result is not None:
                return cached_result
            
            # 执行原函数
            result = await func(*args, **kwargs)
            
            # 存储到缓存
            await cache.set(cache_key, result, ttl=ttl)
            
            return result
        return wrapper
    return decorator

# 导出主要类和函数
__all__ = [
    'IntelligentCache', 'CacheLevel', 'CachePolicy', 
    'CacheEntry', 'MemoryMonitor', 'cache_decorator'
]