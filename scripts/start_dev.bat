@echo off
REM AI Teaching Assistant System - Windows Development Environment Setup
REM Windows开发环境启动脚本

setlocal EnableDelayedExpansion

REM 颜色定义
set "RED=[91m"
set "GREEN=[92m"
set "YELLOW=[93m"
set "BLUE=[94m"
set "NC=[0m"

REM 日志函数
:log_info
echo %BLUE%[INFO]%NC% %~1
goto :eof

:log_success
echo %GREEN%[SUCCESS]%NC% %~1
goto :eof

:log_warning
echo %YELLOW%[WARNING]%NC% %~1
goto :eof

:log_error
echo %RED%[ERROR]%NC% %~1
goto :eof

REM 检查依赖
:check_dependencies
call :log_info "Checking dependencies..."

REM 检查Docker
docker --version >nul 2>&1
if errorlevel 1 (
    call :log_error "Docker is not installed. Please install Docker Desktop first."
    exit /b 1
)

REM 检查Docker Compose
docker-compose --version >nul 2>&1
if errorlevel 1 (
    call :log_error "Docker Compose is not installed. Please install Docker Compose first."
    exit /b 1
)

REM 检查Python
python --version >nul 2>&1
if errorlevel 1 (
    py --version >nul 2>&1
    if errorlevel 1 (
        call :log_error "Python is not installed. Please install Python 3.9+ first."
        exit /b 1
    )
    set PYTHON_CMD=py
) else (
    set PYTHON_CMD=python
)

REM 检查Node.js
node --version >nul 2>&1
if errorlevel 1 (
    call :log_warning "Node.js is not installed. Frontend development may not work."
)

call :log_success "Dependencies check completed"
goto :eof

REM 环境设置
:setup_environment
call :log_info "Setting up environment..."

REM 复制环境变量文件
if not exist .env (
    copy .env.example .env >nul
    call :log_success "Environment file created from template"
) else (
    call :log_info "Environment file already exists"
)

REM 创建必要的目录
if not exist logs mkdir logs
if not exist uploads mkdir uploads
if not exist backups mkdir backups
call :log_success "Required directories created"
goto :eof

REM Docker服务启动
:start_docker_services
call :log_info "Starting Docker services..."

REM 拉取最新镜像
call :log_info "Pulling latest Docker images..."
docker-compose pull

REM 启动服务
call :log_info "Starting services with Docker Compose..."
docker-compose up -d database redis

REM 等待服务启动
call :log_info "Waiting for services to be ready..."
timeout /t 10 /nobreak >nul

REM 检查服务状态
docker-compose ps | findstr "Up" >nul
if errorlevel 1 (
    call :log_error "Failed to start Docker services"
    docker-compose logs
    exit /b 1
) else (
    call :log_success "Docker services started successfully"
)
goto :eof

REM 数据库初始化
:initialize_database
call :log_info "Initializing database..."

REM 等待数据库服务
call :log_info "Waiting for database to be ready..."
:wait_db
docker-compose exec database pg_isready -U ai_teacher >nul 2>&1
if errorlevel 1 (
    timeout /t 2 /nobreak >nul
    goto :wait_db
)

REM 运行数据库初始化
%PYTHON_CMD% scripts\manage_db.py check --env dev
if errorlevel 1 (
    call :log_info "Database not initialized, running setup..."
    %PYTHON_CMD% scripts\manage_db.py init --env dev
)

call :log_success "Database initialization completed"
goto :eof

REM 安装Python依赖
:install_python_dependencies
call :log_info "Installing Python dependencies..."

REM 检查虚拟环境
if not exist venv (
    call :log_info "Creating virtual environment..."
    %PYTHON_CMD% -m venv venv
    call :log_success "Virtual environment created"
)

REM 激活虚拟环境
call venv\Scripts\activate.bat

REM 升级pip
%PYTHON_CMD% -m pip install --upgrade pip

REM 安装依赖
pip install -r requirements.txt
pip install -r requirements-dev.txt

call :log_success "Python dependencies installed"
goto :eof

REM 安装前端依赖
:install_frontend_dependencies
if exist ai-teacher-frontend (
    call :log_info "Installing frontend dependencies..."
    cd ai-teacher-frontend
    
    if exist package-lock.json (
        npm ci
    ) else (
        npm install
    )
    
    cd ..
    call :log_success "Frontend dependencies installed"
) else (
    call :log_warning "Frontend directory not found, skipping"
)
goto :eof

REM 运行健康检查
:run_health_check
call :log_info "Running health checks..."

REM 激活虚拟环境（如果存在）
if exist venv call venv\Scripts\activate.bat

REM 运行健康检查
%PYTHON_CMD% scripts\health_check.py

if errorlevel 1 (
    call :log_warning "Some health checks failed, but continuing..."
) else (
    call :log_success "Health check passed"
)
goto :eof

REM 启动开发服务器
:start_dev_servers
call :log_info "Starting development servers..."

REM 启动后端服务
call :log_info "Starting backend API server..."
docker-compose up -d backend

REM 启动前端服务（如果存在）
if exist ai-teacher-frontend (
    call :log_info "Starting frontend development server..."
    docker-compose up -d frontend
)

REM 等待服务启动
timeout /t 5 /nobreak >nul

call :log_success "Development servers started"
goto :eof

REM 显示服务状态
:show_service_status
call :log_info "Service Status:"
echo ================================
docker-compose ps
echo ================================

call :log_info "Service URLs:"
echo • Backend API: http://localhost:8000
echo • API Documentation: http://localhost:8000/docs
echo • Frontend App: http://localhost:3000
echo • PgAdmin: http://localhost:5050 (admin@aiteacher.local / admin123)
echo • Redis Commander: http://localhost:8081 (admin / admin123)
echo ================================
goto :eof

REM 主函数
:main
echo 🚀 AI Teaching Assistant System - Development Environment Setup
echo ===============================================================

REM 解析命令行参数
set SKIP_DEPS=false
set SKIP_DB=false
set QUICK_START=false

:parse_args
if "%1"=="--skip-deps" (
    set SKIP_DEPS=true
    shift
    goto :parse_args
)
if "%1"=="--skip-db" (
    set SKIP_DB=true
    shift
    goto :parse_args
)
if "%1"=="--quick" (
    set QUICK_START=true
    set SKIP_DEPS=true
    shift
    goto :parse_args
)
if "%1"=="-h" goto :show_help
if "%1"=="--help" goto :show_help
if not "%1"=="" (
    call :log_error "Unknown option: %1"
    exit /b 1
)

REM 执行启动步骤
call :check_dependencies
if errorlevel 1 exit /b 1

call :setup_environment
if errorlevel 1 exit /b 1

if "%QUICK_START%"=="false" (
    call :start_docker_services
    if errorlevel 1 exit /b 1
    
    if "%SKIP_DB%"=="false" (
        call :initialize_database
        if errorlevel 1 exit /b 1
    )
    
    if "%SKIP_DEPS%"=="false" (
        call :install_python_dependencies
        if errorlevel 1 exit /b 1
        
        call :install_frontend_dependencies
        if errorlevel 1 exit /b 1
    )
    
    call :run_health_check
) else (
    call :log_info "Quick start mode - starting services only..."
    call :start_docker_services
    if errorlevel 1 exit /b 1
)

call :start_dev_servers
if errorlevel 1 exit /b 1

call :show_service_status

call :log_success "🎉 Development environment is ready!"
echo.
echo 💡 Tips:
echo   - Use 'docker-compose logs -f' to view logs
echo   - Use 'docker-compose down' to stop services
echo   - Use 'python scripts\health_check.py' to check system health
echo   - Use 'python scripts\manage_db.py --help' for database management
echo.
echo Happy coding! 🎯

goto :eof

:show_help
echo Usage: %0 [OPTIONS]
echo Options:
echo   --skip-deps    Skip dependency installation
echo   --skip-db      Skip database initialization
echo   --quick        Quick start (skip deps, minimal setup)
echo   -h, --help     Show this help message
goto :eof

REM 调用主函数
call :main %*