#!/usr/bin/env python3
"""
AI Teaching Assistant System Setup Script
"""

from setuptools import setup, find_packages
from pathlib import Path

# 读取README文件
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding='utf-8')

# 读取requirements.txt
def read_requirements(file_path):
    """读取依赖文件"""
    requirements = []
    if Path(file_path).exists():
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    requirements.append(line)
    return requirements

# 基础依赖
install_requires = read_requirements('requirements.txt')

# 开发依赖
dev_requires = read_requirements('requirements-dev.txt')

# 测试依赖
test_requires = [
    'pytest>=7.4.0',
    'pytest-asyncio>=0.21.0',
    'pytest-cov>=4.1.0',
    'httpx>=0.25.0',
    'pytest-mock>=3.12.0'
]

# 文档依赖
docs_requires = [
    'mkdocs>=1.5.0',
    'mkdocs-material>=9.4.0',
    'mkdocs-mermaid2-plugin>=1.1.0'
]

setup(
    name="ai-teaching-assistant",
    version="1.0.0",
    author="AI Teaching Assistant Team",
    author_email="dev@aiteacher.com",
    description="AI-powered teaching assistant system for programming education",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ai-teaching-assistant/ai-teacher",
    
    # 包配置
    packages=find_packages(where=".", include=["app*"]),
    package_dir={"": "."},
    include_package_data=True,
    
    # Python版本要求
    python_requires=">=3.9",
    
    # 依赖配置
    install_requires=install_requires,
    
    extras_require={
        "dev": dev_requires,
        "test": test_requires,
        "docs": docs_requires,
        "all": dev_requires + test_requires + docs_requires,
    },
    
    # 入口点
    entry_points={
        "console_scripts": [
            "ai-teacher-server=app.main:main",
            "ai-teacher-db=scripts.manage_db:cli",
            "ai-teacher-health=scripts.health_check:health_check",
        ],
    },
    
    # 分类信息
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Education",
        "Topic :: Education",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
        "Framework :: FastAPI",
        "Topic :: Internet :: WWW/HTTP :: HTTP Servers",
        "Topic :: Software Development :: Libraries :: Application Frameworks",
    ],
    
    # 关键词
    keywords="ai, education, teaching, programming, assistant, fastapi, react",
    
    # 项目URLs
    project_urls={
        "Bug Reports": "https://github.com/ai-teaching-assistant/ai-teacher/issues",
        "Source": "https://github.com/ai-teaching-assistant/ai-teacher",
        "Documentation": "https://ai-teaching-assistant.github.io/ai-teacher",
    },
    
    # 数据文件
    package_data={
        "app": [
            "templates/*.html",
            "static/**/*",
        ],
    },
    
    # 排除的包
    exclude=["tests*", "docs*", "scripts*"],
    
    # 压缩文件包含
    zip_safe=False,
)