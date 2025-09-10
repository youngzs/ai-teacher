"""
AI教学助手系统 - 服务器启动脚本
用于启动FastAPI开发服务器

Author: AI Backend Architecture Expert
Date: 2025-09-10
"""

import uvicorn
import asyncio
import sys
import os
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from app.core.config import settings
from app.utils.logger import setup_logging

def main():
    """启动服务器"""
    # 设置日志
    setup_logging()
    
    print(f"""
    ==========================================
    AI Teaching Assistant System
    ==========================================
    Environment: {settings.ENVIRONMENT}
    Host: {settings.HOST}
    Port: {settings.PORT}
    Debug: {settings.DEBUG}
    
    API Documentation: http://{settings.HOST}:{settings.PORT}/api/docs
    Health Check: http://{settings.HOST}:{settings.PORT}/health
    ==========================================
    """)
    
    # 启动服务器
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.ENVIRONMENT == "development",
        log_level=settings.LOG_LEVEL.lower(),
        access_log=True,
        loop="uvloop" if sys.platform != "win32" else "asyncio"
    )


if __name__ == "__main__":
    main()