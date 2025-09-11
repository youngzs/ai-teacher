#!/usr/bin/env python3
"""
Quick startup script for AI Teaching Assistant Backend
"""
import os
import sys

# Set environment variables before importing anything
os.environ["DATABASE_URL"] = "postgresql+asyncpg://ai_teacher:dev_password_123@localhost:5432/ai_teacher_dev"
os.environ["REDIS_URL"] = "redis://:dev_redis_123@localhost:6379/0"
os.environ["SECRET_KEY"] = "18397d66dcfbd6549be5219c1d90d195849a35f9c402552b4b4e55a13c3f6c32"
os.environ["ENVIRONMENT"] = "development"
os.environ["DEBUG"] = "true"
os.environ["ALLOWED_HOSTS"] = '["*"]'  # JSON array format
os.environ["ALLOWED_EXTENSIONS"] = '["py","c","cpp","java","js","ts","txt"]'  # JSON array format

import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import time
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from sqlalchemy import text

# Database setup
DATABASE_URL = os.environ["DATABASE_URL"]
engine = create_async_engine(DATABASE_URL, echo=False)
SessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
Base = declarative_base()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifecycle management"""
    print("Starting AI Teaching Assistant Backend...")
    print(f"Database: {DATABASE_URL.split('@')[1] if '@' in DATABASE_URL else 'configured'}")
    print(f"Redis: {os.environ['REDIS_URL'].split('@')[1] if '@' in os.environ['REDIS_URL'] else 'configured'}")
    
    # Create database tables
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        print("✅ Database connection verified")
    except Exception as e:
        print(f"⚠️ Database warning: {e}")
    
    yield
    
    print("Shutting down...")
    await engine.dispose()

# Create FastAPI app
app = FastAPI(
    title="AI Teaching Assistant API",
    description="Simplified backend for AI Teaching Assistant System",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "AI Teaching Assistant API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health",
        "status": "running"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        # Test database connection
        async with SessionLocal() as session:
            result = await session.execute(text("SELECT 1"))
            result.scalar()
        
        # Test Redis connection
        redis_status = "not_tested"
        try:
            import redis.asyncio as redis
            r = redis.from_url(os.environ["REDIS_URL"])
            await r.ping()
            await r.close()
            redis_status = "connected"
        except:
            redis_status = "error"
        
        return {
            "status": "healthy",
            "timestamp": time.time(),
            "services": {
                "database": "connected",
                "redis": redis_status,
                "ai_service": "not_configured"
            },
            "version": "1.0.0"
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "timestamp": time.time(),
            "error": str(e),
            "services": {
                "database": "error",
                "redis": "unknown",
                "ai_service": "not_configured"
            }
        }

@app.get("/api/v1/test/db")
async def test_database():
    """Test database connectivity"""
    try:
        async with SessionLocal() as session:
            result = await session.execute(text("SELECT COUNT(*) FROM users"))
            count = result.scalar()
            return {
                "status": "connected",
                "user_count": count,
                "message": f"Database has {count} users"
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/test/redis")
async def test_redis():
    """Test Redis connectivity"""
    try:
        import redis.asyncio as redis
        r = redis.from_url(os.environ["REDIS_URL"])
        await r.ping()
        
        # Test set and get
        await r.set("test_key", "test_value", ex=10)
        value = await r.get("test_key")
        await r.close()
        
        return {
            "status": "connected",
            "test_result": value.decode() if value else None,
            "message": "Redis is working"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    print("\n" + "="*50)
    print("AI Teaching Assistant Backend")
    print("="*50)
    print("Starting server on http://0.0.0.0:8000")
    print("API Documentation: http://localhost:8000/docs")
    print("Health Check: http://localhost:8000/health")
    print("="*50 + "\n")
    
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")