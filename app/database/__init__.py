# AI教学助手系统 - 数据库模块初始化文件

from .database import Base, engine, SessionLocal, get_db
from .models import User

__all__ = ["Base", "engine", "SessionLocal", "get_db", "User"]