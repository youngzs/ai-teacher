"""
AI教学助手系统 - 简化版FastAPI主应用
用于快速启动和测试
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import time
import os
from typing import Optional
from sqlalchemy.sql import text

# 设置环境变量 - 使用新的数据库来避免外键冲突
os.environ.setdefault("DATABASE_URL", "postgresql+asyncpg://ai_teacher:dev_password_123@localhost:5432/ai_teacher_dev_v2")
os.environ.setdefault("REDIS_URL", "redis://:dev_redis_123@localhost:6379/0")

from .database import engine, SessionLocal, Base
from .core.config import settings

@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    print("Starting AI Teaching Assistant System (Simplified)...")
    
    # 创建数据库表
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        print("Database tables created/verified")
    except Exception as e:
        print(f"Warning: Database initialization issue: {e}")
    
    yield
    
    # 关闭时清理
    print("Shutting down AI Teaching Assistant System...")
    await engine.dispose()

# 创建FastAPI应用实例
app = FastAPI(
    title="AI Teaching Assistant API (Simplified)",
    description="AI驱动的编程教学助手系统API - 简化版",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS中间件配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 健康检查端点
@app.get("/health")
async def health_check():
    """系统健康检查"""
    try:
        # 检查数据库连接
        async with SessionLocal() as session:
            await session.execute(text("SELECT 1"))
        
        return {
            "status": "healthy",
            "timestamp": time.time(),
            "services": {
                "database": "connected",
                "ai_service": "not_configured"
            },
            "version": "1.0.0",
            "environment": settings.ENVIRONMENT
        }
    except Exception as e:
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "timestamp": time.time(),
                "error": str(e)
            }
        )

@app.get("/")
async def root():
    """根路径响应"""
    return {
        "message": "AI Teaching Assistant API (Simplified)",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health",
        "status": "running"
    }

# 测试数据库连接端点
@app.get("/api/v1/test/db")
async def test_database():
    """测试数据库连接"""
    try:
        async with SessionLocal() as session:
            result = await session.execute(text("SELECT COUNT(*) FROM users"))
            count = result.scalar()
            return {
                "status": "connected",
                "user_count": count,
                "database": settings.DATABASE_URL.split("@")[1] if "@" in settings.DATABASE_URL else "unknown"
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# 测试Redis连接端点
@app.get("/api/v1/test/redis")
async def test_redis():
    """测试Redis连接"""
    try:
        import redis.asyncio as redis
        r = redis.from_url(settings.REDIS_URL)
        await r.ping()
        await r.close()
        return {
            "status": "connected",
            "redis_url": settings.REDIS_URL.split("@")[1] if "@" in settings.REDIS_URL else "unknown"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# 系统信息端点
@app.get("/api/v1/info")
async def system_info():
    """获取系统信息"""
    return {
        "project_name": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "environment": settings.ENVIRONMENT,
        "debug": settings.DEBUG,
        "host": settings.HOST,
        "port": settings.PORT,
        "features": {
            "signup_enabled": settings.ENABLE_SIGNUP,
            "debugging_mode": settings.ENABLE_DEBUGGING_MODE,
            "batch_processing": settings.ENABLE_BATCH_PROCESSING,
            "metrics_collection": settings.ENABLE_METRICS_COLLECTION
        }
    }

if __name__ == "__main__":
    import uvicorn
    
    print("Starting development server...")
    uvicorn.run(
        "app.main_simple:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=True,
        log_level="info"
    )