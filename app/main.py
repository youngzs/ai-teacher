"""
AI教学助手系统 - FastAPI主应用
提供RESTful API服务，整合AI Agent系统与前端交互

Author: AI Backend Architecture Expert
Date: 2025-09-10
"""

from fastapi import FastAPI, Middleware, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import logging
import time
from typing import Any, Dict
import asyncio
import uvloop

from .database import engine, SessionLocal
from .database.models import Base
from .api import auth, submissions, analysis, users, dashboard
from .core.config import settings
from .core.security import create_access_token
from .services.ai_service import AITeachingService
from .utils.logger import setup_logging, get_logger

# 设置日志
setup_logging()
logger = get_logger(__name__)

# AI服务实例（全局）
ai_service: AITeachingService = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时初始化
    logger.info("Starting AI Teaching Assistant System...")
    
    # 设置事件循环策略
    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
    
    # 创建数据库表
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    # 初始化AI服务
    global ai_service
    ai_service = AITeachingService()
    await ai_service.initialize()
    
    logger.info("AI Teaching Assistant System started successfully")
    yield
    
    # 关闭时清理
    logger.info("Shutting down AI Teaching Assistant System...")
    if ai_service:
        await ai_service.cleanup()
    await engine.dispose()
    logger.info("AI Teaching Assistant System shut down complete")


# 创建FastAPI应用实例
app = FastAPI(
    title="AI Teaching Assistant API",
    description="AI驱动的编程教学助手系统API",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/api/docs" if settings.ENVIRONMENT == "development" else None,
    redoc_url="/api/redoc" if settings.ENVIRONMENT == "development" else None,
)

# 中间件配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_HOSTS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=settings.ALLOWED_HOSTS
)


@app.middleware("http")
async def log_requests(request: Request, call_next):
    """请求日志中间件"""
    start_time = time.time()
    
    # 记录请求信息
    logger.info(f"Request: {request.method} {request.url}")
    
    response = await call_next(request)
    
    # 记录响应时间
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    
    logger.info(f"Response: {response.status_code} - {process_time:.3f}s")
    
    return response


@app.middleware("http")
async def error_handling_middleware(request: Request, call_next):
    """全局错误处理中间件"""
    try:
        response = await call_next(request)
        return response
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unhandled exception: {str(e)}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={
                "error": "Internal Server Error",
                "message": "系统内部错误，请稍后重试",
                "detail": str(e) if settings.ENVIRONMENT == "development" else None
            }
        )


# 健康检查端点
@app.get("/health", tags=["Health"])
async def health_check():
    """系统健康检查"""
    try:
        # 检查数据库连接
        async with SessionLocal() as session:
            await session.execute("SELECT 1")
        
        # 检查AI服务状态
        ai_status = await ai_service.health_check() if ai_service else False
        
        return {
            "status": "healthy",
            "timestamp": time.time(),
            "services": {
                "database": "connected",
                "ai_service": "active" if ai_status else "inactive"
            },
            "version": "1.0.0"
        }
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "timestamp": time.time(),
                "error": str(e)
            }
        )


@app.get("/", tags=["Root"])
async def root():
    """根路径响应"""
    return {
        "message": "AI Teaching Assistant API",
        "version": "1.0.0",
        "docs": "/api/docs",
        "health": "/health"
    }


# API路由注册
app.include_router(
    auth.router,
    prefix="/api/v1/auth",
    tags=["Authentication"]
)

app.include_router(
    submissions.router,
    prefix="/api/v1/submissions",
    tags=["Code Submissions"]
)

app.include_router(
    analysis.router,
    prefix="/api/v1/analysis",
    tags=["AI Analysis"]
)

app.include_router(
    users.router,
    prefix="/api/v1/users",
    tags=["User Management"]
)

app.include_router(
    dashboard.router,
    prefix="/api/v1/dashboard",
    tags=["Dashboard"]
)


# 获取AI服务实例的依赖
def get_ai_service() -> AITeachingService:
    """获取AI服务实例"""
    if ai_service is None:
        raise HTTPException(
            status_code=503,
            detail="AI service is not available"
        )
    return ai_service


# 导出给其他模块使用
__all__ = ["app", "get_ai_service"]


if __name__ == "__main__":
    import uvicorn
    
    logger.info("Starting development server...")
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.ENVIRONMENT == "development",
        log_level="info",
        loop="uvloop"
    )