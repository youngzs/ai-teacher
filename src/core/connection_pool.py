"""
AI教学助手系统 - 高性能连接池和并发请求处理
Sprint 2 优化：支持高并发、连接复用、智能负载均衡

Author: AI Architecture Expert  
Date: 2025-09-11
Version: Sprint 2 - Performance Optimization
"""

import asyncio
import aiohttp
import time
import logging
from typing import Dict, Any, List, Optional, Callable, Union
from dataclasses import dataclass, field
from enum import Enum
from collections import deque, defaultdict
from contextlib import asynccontextmanager
import json
import ssl
import weakref
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class ConnectionState(Enum):
    """连接状态枚举"""
    IDLE = "idle"
    BUSY = "busy" 
    CLOSED = "closed"
    ERROR = "error"

class LoadBalanceStrategy(Enum):
    """负载均衡策略"""
    ROUND_ROBIN = "round_robin"
    LEAST_CONNECTIONS = "least_connections"
    WEIGHTED_ROUND_ROBIN = "weighted_round_robin"
    RANDOM = "random"

@dataclass
class ConnectionMetrics:
    """连接性能指标"""
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    average_response_time: float = 0.0
    last_used: datetime = field(default_factory=datetime.now)
    created_at: datetime = field(default_factory=datetime.now)
    
    @property
    def success_rate(self) -> float:
        """成功率"""
        if self.total_requests == 0:
            return 0.0
        return self.successful_requests / self.total_requests
    
    @property
    def error_rate(self) -> float:
        """错误率"""
        return 1.0 - self.success_rate

@dataclass  
class ConnectionConfig:
    """连接配置"""
    max_connections: int = 50
    max_keepalive_connections: int = 30
    keepalive_expiry: int = 30
    timeout: aiohttp.ClientTimeout = field(default_factory=lambda: aiohttp.ClientTimeout(total=30))
    connector_limit: int = 100
    connector_limit_per_host: int = 30
    enable_cleanup_closed: bool = True
    force_close: bool = False
    
class Connection:
    """连接包装器"""
    
    def __init__(self, session: aiohttp.ClientSession, connection_id: str):
        self.session = session
        self.connection_id = connection_id
        self.state = ConnectionState.IDLE
        self.metrics = ConnectionMetrics()
        self._lock = asyncio.Lock()
        self._last_health_check = datetime.now()
        
    async def is_healthy(self) -> bool:
        """检查连接健康状态"""
        try:
            if self.session.closed:
                return False
                
            # 简单健康检查 - 可以配置具体的健康检查端点
            now = datetime.now()
            if (now - self._last_health_check).seconds < 60:  # 1分钟内检查过
                return True
                
            self._last_health_check = now
            return True  # 简化版本直接返回True
            
        except Exception as e:
            logger.warning(f"Connection {self.connection_id} health check failed: {e}")
            return False
    
    async def execute_request(self, method: str, url: str, **kwargs) -> aiohttp.ClientResponse:
        """执行HTTP请求"""
        async with self._lock:
            if self.state != ConnectionState.IDLE:
                raise RuntimeError(f"Connection {self.connection_id} is not idle")
                
            self.state = ConnectionState.BUSY
            start_time = time.time()
            
            try:
                response = await self.session.request(method, url, **kwargs)
                
                # 更新指标
                self.metrics.total_requests += 1
                self.metrics.successful_requests += 1
                response_time = time.time() - start_time
                self.metrics.average_response_time = (
                    (self.metrics.average_response_time * (self.metrics.total_requests - 1) + response_time) 
                    / self.metrics.total_requests
                )
                self.metrics.last_used = datetime.now()
                
                return response
                
            except Exception as e:
                self.metrics.total_requests += 1
                self.metrics.failed_requests += 1
                logger.error(f"Connection {self.connection_id} request failed: {e}")
                raise
            finally:
                self.state = ConnectionState.IDLE
                
    def close(self):
        """关闭连接"""
        if not self.session.closed:
            asyncio.create_task(self.session.close())
        self.state = ConnectionState.CLOSED

class HighPerformanceConnectionPool:
    """高性能连接池"""
    
    def __init__(self, config: ConnectionConfig):
        self.config = config
        self.connections: Dict[str, Connection] = {}
        self.idle_connections: deque = deque()
        self.busy_connections: set = set()
        
        # 负载均衡
        self.load_balance_strategy = LoadBalanceStrategy.LEAST_CONNECTIONS
        self._round_robin_index = 0
        
        # 并发控制
        self.semaphore = asyncio.Semaphore(config.max_connections)
        self.connection_lock = asyncio.Lock()
        
        # 监控和清理
        self.pool_metrics = {
            "total_connections_created": 0,
            "total_connections_closed": 0,
            "total_requests": 0,
            "active_connections": 0,
            "pool_hits": 0,
            "pool_misses": 0
        }
        
        self._cleanup_task = None
        self._start_cleanup_task()
        
    def _start_cleanup_task(self):
        """启动清理任务"""
        if self._cleanup_task is None or self._cleanup_task.done():
            self._cleanup_task = asyncio.create_task(self._cleanup_expired_connections())
    
    async def _cleanup_expired_connections(self):
        """清理过期连接"""
        while True:
            try:
                await asyncio.sleep(30)  # 每30秒清理一次
                
                async with self.connection_lock:
                    expired_connections = []
                    now = datetime.now()
                    
                    for conn_id, connection in self.connections.items():
                        # 检查是否过期或不健康
                        if (connection.state == ConnectionState.IDLE and 
                            (now - connection.metrics.last_used).seconds > self.config.keepalive_expiry):
                            expired_connections.append(conn_id)
                        elif not await connection.is_healthy():
                            expired_connections.append(conn_id)
                    
                    # 清理过期连接
                    for conn_id in expired_connections:
                        await self._close_connection(conn_id)
                        
                    if expired_connections:
                        logger.info(f"Cleaned up {len(expired_connections)} expired connections")
                        
            except Exception as e:
                logger.error(f"Connection cleanup error: {e}")
                await asyncio.sleep(5)  # 错误后短暂等待
    
    async def _create_connection(self) -> Connection:
        """创建新连接"""
        connector = aiohttp.TCPConnector(
            limit=self.config.connector_limit,
            limit_per_host=self.config.connector_limit_per_host,
            keepalive_timeout=self.config.keepalive_expiry,
            enable_cleanup_closed=self.config.enable_cleanup_closed,
            force_close=self.config.force_close,
            ssl=False  # 可以根据需要配置SSL
        )
        
        session = aiohttp.ClientSession(
            connector=connector,
            timeout=self.config.timeout
        )
        
        connection_id = f"conn_{self.pool_metrics['total_connections_created']}"
        connection = Connection(session, connection_id)
        
        self.pool_metrics["total_connections_created"] += 1
        self.pool_metrics["active_connections"] += 1
        
        logger.debug(f"Created new connection: {connection_id}")
        return connection
    
    async def _close_connection(self, connection_id: str):
        """关闭指定连接"""
        if connection_id in self.connections:
            connection = self.connections[connection_id]
            connection.close()
            
            # 从各个集合中移除
            del self.connections[connection_id]
            if connection_id in self.busy_connections:
                self.busy_connections.remove(connection_id)
            
            # 从空闲队列中移除
            idle_connections_to_remove = []
            for conn_id in self.idle_connections:
                if conn_id == connection_id:
                    idle_connections_to_remove.append(conn_id)
            for conn_id in idle_connections_to_remove:
                self.idle_connections.remove(conn_id)
            
            self.pool_metrics["total_connections_closed"] += 1
            self.pool_metrics["active_connections"] -= 1
    
    def _select_connection_by_strategy(self) -> Optional[str]:
        """根据负载均衡策略选择连接"""
        if not self.idle_connections:
            return None
            
        if self.load_balance_strategy == LoadBalanceStrategy.ROUND_ROBIN:
            # 轮询策略
            if self.idle_connections:
                self._round_robin_index = (self._round_robin_index + 1) % len(self.idle_connections)
                return list(self.idle_connections)[self._round_robin_index]
                
        elif self.load_balance_strategy == LoadBalanceStrategy.LEAST_CONNECTIONS:
            # 最少连接策略
            best_conn_id = None
            min_requests = float('inf')
            
            for conn_id in self.idle_connections:
                if conn_id in self.connections:
                    conn = self.connections[conn_id]
                    if conn.metrics.total_requests < min_requests:
                        min_requests = conn.metrics.total_requests
                        best_conn_id = conn_id
                        
            return best_conn_id
            
        # 默认返回第一个空闲连接
        return list(self.idle_connections)[0] if self.idle_connections else None
    
    @asynccontextmanager
    async def get_connection(self):
        """获取连接的上下文管理器"""
        async with self.semaphore:  # 并发控制
            connection = None
            connection_id = None
            
            try:
                async with self.connection_lock:
                    # 尝试获取空闲连接
                    connection_id = self._select_connection_by_strategy()
                    
                    if connection_id and connection_id in self.connections:
                        connection = self.connections[connection_id]
                        self.idle_connections.remove(connection_id)
                        self.busy_connections.add(connection_id)
                        self.pool_metrics["pool_hits"] += 1
                    else:
                        # 创建新连接
                        if len(self.connections) >= self.config.max_connections:
                            raise RuntimeError("Connection pool exhausted")
                            
                        connection = await self._create_connection()
                        connection_id = connection.connection_id
                        self.connections[connection_id] = connection
                        self.busy_connections.add(connection_id)
                        self.pool_metrics["pool_misses"] += 1
                
                # 检查连接健康状态
                if not await connection.is_healthy():
                    await self._close_connection(connection_id)
                    raise RuntimeError("Unhealthy connection")
                
                yield connection
                
            finally:
                # 归还连接
                if connection and connection_id:
                    async with self.connection_lock:
                        if connection_id in self.busy_connections:
                            self.busy_connections.remove(connection_id)
                            
                        if connection_id in self.connections and connection.state != ConnectionState.CLOSED:
                            self.idle_connections.append(connection_id)
    
    async def execute_request(self, method: str, url: str, **kwargs) -> aiohttp.ClientResponse:
        """执行HTTP请求"""
        async with self.get_connection() as connection:
            self.pool_metrics["total_requests"] += 1
            return await connection.execute_request(method, url, **kwargs)
    
    def get_pool_stats(self) -> Dict[str, Any]:
        """获取连接池统计信息"""
        total_successful = sum(
            conn.metrics.successful_requests 
            for conn in self.connections.values()
        )
        total_failed = sum(
            conn.metrics.failed_requests 
            for conn in self.connections.values()
        )
        
        return {
            "pool_metrics": self.pool_metrics.copy(),
            "connection_stats": {
                "total_connections": len(self.connections),
                "idle_connections": len(self.idle_connections),
                "busy_connections": len(self.busy_connections),
                "max_connections": self.config.max_connections
            },
            "request_stats": {
                "total_successful": total_successful,
                "total_failed": total_failed,
                "success_rate": total_successful / max(total_successful + total_failed, 1)
            },
            "pool_efficiency": {
                "hit_rate": self.pool_metrics["pool_hits"] / max(
                    self.pool_metrics["pool_hits"] + self.pool_metrics["pool_misses"], 1
                )
            }
        }
    
    async def close_all(self):
        """关闭所有连接"""
        async with self.connection_lock:
            connection_ids = list(self.connections.keys())
            
        for conn_id in connection_ids:
            await self._close_connection(conn_id)
            
        if self._cleanup_task and not self._cleanup_task.done():
            self._cleanup_task.cancel()
            
        logger.info("All connections closed")

class ConcurrentRequestProcessor:
    """并发请求处理器"""
    
    def __init__(self, connection_pool: HighPerformanceConnectionPool, 
                 max_concurrent_requests: int = 100):
        self.connection_pool = connection_pool
        self.max_concurrent_requests = max_concurrent_requests
        self.request_semaphore = asyncio.Semaphore(max_concurrent_requests)
        
        # 请求队列和优先级
        self.request_queues = {
            "high": asyncio.Queue(maxsize=100),
            "normal": asyncio.Queue(maxsize=500),
            "low": asyncio.Queue(maxsize=200)
        }
        
        # 请求处理器
        self.request_processors = []
        self.is_running = False
        
        # 性能指标
        self.processing_metrics = {
            "total_requests": 0,
            "completed_requests": 0,
            "failed_requests": 0,
            "queued_requests": 0,
            "average_processing_time": 0.0
        }
        
    async def start_processors(self, num_processors: int = 10):
        """启动请求处理器"""
        self.is_running = True
        
        for i in range(num_processors):
            processor = asyncio.create_task(self._request_processor(f"processor_{i}"))
            self.request_processors.append(processor)
            
        logger.info(f"Started {num_processors} request processors")
        
    async def stop_processors(self):
        """停止请求处理器"""
        self.is_running = False
        
        for processor in self.request_processors:
            processor.cancel()
            
        await asyncio.gather(*self.request_processors, return_exceptions=True)
        self.request_processors.clear()
        
        logger.info("Stopped all request processors")
    
    async def _request_processor(self, processor_id: str):
        """请求处理器工作循环"""
        logger.debug(f"Request processor {processor_id} started")
        
        while self.is_running:
            try:
                # 按优先级处理请求
                request_item = None
                
                for priority in ["high", "normal", "low"]:
                    try:
                        request_item = await asyncio.wait_for(
                            self.request_queues[priority].get(), 
                            timeout=0.1
                        )
                        break
                    except asyncio.TimeoutError:
                        continue
                
                if request_item is None:
                    await asyncio.sleep(0.01)  # 短暂休眠
                    continue
                
                # 解析请求项
                request_data, response_future = request_item
                method = request_data["method"]
                url = request_data["url"]
                kwargs = request_data.get("kwargs", {})
                
                start_time = time.time()
                
                try:
                    # 执行请求
                    async with self.request_semaphore:
                        response = await self.connection_pool.execute_request(method, url, **kwargs)
                        
                        # 读取响应数据
                        response_data = {
                            "status": response.status,
                            "headers": dict(response.headers),
                            "data": await response.text()
                        }
                        
                        if not response_future.cancelled():
                            response_future.set_result(response_data)
                        
                        self.processing_metrics["completed_requests"] += 1
                        
                except Exception as e:
                    if not response_future.cancelled():
                        response_future.set_exception(e)
                    self.processing_metrics["failed_requests"] += 1
                    logger.error(f"Request processing failed: {e}")
                    
                finally:
                    # 更新处理时间指标
                    processing_time = time.time() - start_time
                    completed = self.processing_metrics["completed_requests"]
                    if completed > 0:
                        self.processing_metrics["average_processing_time"] = (
                            (self.processing_metrics["average_processing_time"] * (completed - 1) + processing_time)
                            / completed
                        )
                        
            except asyncio.CancelledError:
                logger.debug(f"Request processor {processor_id} cancelled")
                break
            except Exception as e:
                logger.error(f"Request processor {processor_id} error: {e}")
                await asyncio.sleep(0.1)
    
    async def submit_request(self, method: str, url: str, priority: str = "normal", 
                           timeout: float = 30.0, **kwargs) -> Dict[str, Any]:
        """提交请求"""
        if not self.is_running:
            raise RuntimeError("Request processors not started")
            
        if priority not in self.request_queues:
            priority = "normal"
            
        request_data = {
            "method": method,
            "url": url,
            "kwargs": kwargs
        }
        
        response_future = asyncio.Future()
        request_item = (request_data, response_future)
        
        try:
            # 提交到队列
            await asyncio.wait_for(
                self.request_queues[priority].put(request_item),
                timeout=5.0  # 队列提交超时
            )
            
            self.processing_metrics["total_requests"] += 1
            self.processing_metrics["queued_requests"] += 1
            
            # 等待处理结果
            result = await asyncio.wait_for(response_future, timeout=timeout)
            self.processing_metrics["queued_requests"] -= 1
            
            return result
            
        except asyncio.TimeoutError:
            self.processing_metrics["queued_requests"] -= 1
            raise TimeoutError(f"Request timeout after {timeout}s")
        except asyncio.QueueFull:
            raise RuntimeError(f"Request queue ({priority}) is full")
    
    def get_processing_stats(self) -> Dict[str, Any]:
        """获取处理统计信息"""
        queue_sizes = {
            priority: queue.qsize() 
            for priority, queue in self.request_queues.items()
        }
        
        return {
            "processing_metrics": self.processing_metrics.copy(),
            "queue_stats": {
                "queue_sizes": queue_sizes,
                "total_queued": sum(queue_sizes.values()),
                "max_concurrent": self.max_concurrent_requests
            },
            "processor_stats": {
                "active_processors": len([p for p in self.request_processors if not p.done()]),
                "total_processors": len(self.request_processors)
            }
        }

class ConnectionPoolManager:
    """连接池管理器 - 管理多个连接池"""
    
    def __init__(self):
        self.pools: Dict[str, HighPerformanceConnectionPool] = {}
        self.processors: Dict[str, ConcurrentRequestProcessor] = {}
        
    async def create_pool(self, pool_name: str, config: ConnectionConfig) -> HighPerformanceConnectionPool:
        """创建连接池"""
        if pool_name in self.pools:
            await self.close_pool(pool_name)
            
        pool = HighPerformanceConnectionPool(config)
        processor = ConcurrentRequestProcessor(pool, max_concurrent_requests=50)
        
        self.pools[pool_name] = pool
        self.processors[pool_name] = processor
        
        await processor.start_processors(num_processors=5)
        
        logger.info(f"Created connection pool: {pool_name}")
        return pool
    
    async def get_pool(self, pool_name: str) -> Optional[HighPerformanceConnectionPool]:
        """获取连接池"""
        return self.pools.get(pool_name)
    
    async def get_processor(self, pool_name: str) -> Optional[ConcurrentRequestProcessor]:
        """获取请求处理器"""
        return self.processors.get(pool_name)
    
    async def close_pool(self, pool_name: str):
        """关闭连接池"""
        if pool_name in self.processors:
            await self.processors[pool_name].stop_processors()
            del self.processors[pool_name]
            
        if pool_name in self.pools:
            await self.pools[pool_name].close_all()
            del self.pools[pool_name]
            
        logger.info(f"Closed connection pool: {pool_name}")
    
    async def close_all_pools(self):
        """关闭所有连接池"""
        pool_names = list(self.pools.keys())
        
        for pool_name in pool_names:
            await self.close_pool(pool_name)
            
        logger.info("Closed all connection pools")
    
    def get_all_stats(self) -> Dict[str, Any]:
        """获取所有连接池统计信息"""
        stats = {}
        
        for pool_name in self.pools:
            pool_stats = self.pools[pool_name].get_pool_stats()
            
            if pool_name in self.processors:
                processing_stats = self.processors[pool_name].get_processing_stats()
                pool_stats["processing"] = processing_stats
                
            stats[pool_name] = pool_stats
            
        return stats

# 全局连接池管理器
connection_pool_manager = ConnectionPoolManager()

# 导出主要类
__all__ = [
    'ConnectionConfig', 'HighPerformanceConnectionPool', 
    'ConcurrentRequestProcessor', 'ConnectionPoolManager',
    'connection_pool_manager', 'LoadBalanceStrategy'
]