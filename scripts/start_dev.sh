#!/bin/bash
# AI Teaching Assistant System - 开发环境启动脚本
# Development Environment Startup Script

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 日志函数
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 检查依赖
check_dependencies() {
    log_info "Checking dependencies..."
    
    # 检查Docker
    if ! command -v docker &> /dev/null; then
        log_error "Docker is not installed. Please install Docker first."
        exit 1
    fi
    
    # 检查Docker Compose
    if ! command -v docker-compose &> /dev/null; then
        log_error "Docker Compose is not installed. Please install Docker Compose first."
        exit 1
    fi
    
    # 检查Python
    if ! command -v python &> /dev/null && ! command -v python3 &> /dev/null; then
        log_error "Python is not installed. Please install Python 3.9+ first."
        exit 1
    fi
    
    # 检查Node.js
    if ! command -v node &> /dev/null; then
        log_warning "Node.js is not installed. Frontend development may not work."
    fi
    
    log_success "Dependencies check completed"
}

# 环境设置
setup_environment() {
    log_info "Setting up environment..."
    
    # 复制环境变量文件
    if [ ! -f .env ]; then
        cp .env.example .env
        log_success "Environment file created from template"
    else
        log_info "Environment file already exists"
    fi
    
    # 创建必要的目录
    mkdir -p logs uploads backups
    log_success "Required directories created"
}

# Docker服务启动
start_docker_services() {
    log_info "Starting Docker services..."
    
    # 拉取最新镜像
    log_info "Pulling latest Docker images..."
    docker-compose pull
    
    # 启动服务
    log_info "Starting services with Docker Compose..."
    docker-compose up -d database redis
    
    # 等待服务启动
    log_info "Waiting for services to be ready..."
    sleep 10
    
    # 检查服务状态
    if docker-compose ps | grep -q "Up"; then
        log_success "Docker services started successfully"
    else
        log_error "Failed to start Docker services"
        docker-compose logs
        exit 1
    fi
}

# 数据库初始化
initialize_database() {
    log_info "Initializing database..."
    
    # 等待数据库服务
    log_info "Waiting for database to be ready..."
    while ! docker-compose exec database pg_isready -U ai_teacher > /dev/null 2>&1; do
        sleep 2
    done
    
    # 运行数据库初始化
    python scripts/manage_db.py check --env dev
    if [ $? -ne 0 ]; then
        log_info "Database not initialized, running setup..."
        python scripts/manage_db.py init --env dev
    fi
    
    log_success "Database initialization completed"
}

# 安装Python依赖
install_python_dependencies() {
    log_info "Installing Python dependencies..."
    
    # 检查虚拟环境
    if [ ! -d "venv" ]; then
        log_info "Creating virtual environment..."
        python -m venv venv
        log_success "Virtual environment created"
    fi
    
    # 激活虚拟环境
    source venv/bin/activate
    
    # 升级pip
    pip install --upgrade pip
    
    # 安装依赖
    pip install -r requirements.txt
    pip install -r requirements-dev.txt
    
    log_success "Python dependencies installed"
}

# 安装前端依赖
install_frontend_dependencies() {
    if [ -d "ai-teacher-frontend" ]; then
        log_info "Installing frontend dependencies..."
        cd ai-teacher-frontend
        
        if [ -f "package-lock.json" ]; then
            npm ci
        else
            npm install
        fi
        
        cd ..
        log_success "Frontend dependencies installed"
    else
        log_warning "Frontend directory not found, skipping"
    fi
}

# 运行健康检查
run_health_check() {
    log_info "Running health checks..."
    
    # 激活虚拟环境（如果存在）
    if [ -d "venv" ]; then
        source venv/bin/activate
    fi
    
    # 运行健康检查
    python scripts/health_check.py
    
    if [ $? -eq 0 ]; then
        log_success "Health check passed"
    else
        log_warning "Some health checks failed, but continuing..."
    fi
}

# 启动开发服务器
start_dev_servers() {
    log_info "Starting development servers..."
    
    # 启动后端服务
    log_info "Starting backend API server..."
    docker-compose up -d backend
    
    # 启动前端服务（如果存在）
    if [ -d "ai-teacher-frontend" ]; then
        log_info "Starting frontend development server..."
        docker-compose up -d frontend
    fi
    
    # 等待服务启动
    sleep 5
    
    log_success "Development servers started"
}

# 显示服务状态
show_service_status() {
    log_info "Service Status:"
    echo "================================"
    docker-compose ps
    echo "================================"
    
    log_info "Service URLs:"
    echo "• Backend API: http://localhost:8000"
    echo "• API Documentation: http://localhost:8000/docs"
    echo "• Frontend App: http://localhost:3000"
    echo "• PgAdmin: http://localhost:5050 (admin@aiteacher.local / admin123)"
    echo "• Redis Commander: http://localhost:8081 (admin / admin123)"
    echo "================================"
}

# 主函数
main() {
    echo "🚀 AI Teaching Assistant System - Development Environment Setup"
    echo "==============================================================="
    
    # 解析命令行参数
    SKIP_DEPS=false
    SKIP_DB=false
    QUICK_START=false
    
    while [[ $# -gt 0 ]]; do
        case $1 in
            --skip-deps)
                SKIP_DEPS=true
                shift
                ;;
            --skip-db)
                SKIP_DB=true
                shift
                ;;
            --quick)
                QUICK_START=true
                SKIP_DEPS=true
                shift
                ;;
            -h|--help)
                echo "Usage: $0 [OPTIONS]"
                echo "Options:"
                echo "  --skip-deps    Skip dependency installation"
                echo "  --skip-db      Skip database initialization"
                echo "  --quick        Quick start (skip deps, minimal setup)"
                echo "  -h, --help     Show this help message"
                exit 0
                ;;
            *)
                log_error "Unknown option: $1"
                exit 1
                ;;
        esac
    done
    
    # 执行启动步骤
    check_dependencies
    setup_environment
    
    if [ "$QUICK_START" = false ]; then
        start_docker_services
        
        if [ "$SKIP_DB" = false ]; then
            initialize_database
        fi
        
        if [ "$SKIP_DEPS" = false ]; then
            install_python_dependencies
            install_frontend_dependencies
        fi
        
        run_health_check
    else
        log_info "Quick start mode - starting services only..."
        start_docker_services
    fi
    
    start_dev_servers
    show_service_status
    
    log_success "🎉 Development environment is ready!"
    echo ""
    echo "💡 Tips:"
    echo "  - Use 'docker-compose logs -f' to view logs"
    echo "  - Use 'docker-compose down' to stop services"
    echo "  - Use './scripts/health_check.py' to check system health"
    echo "  - Use './scripts/manage_db.py --help' for database management"
    echo ""
    echo "Happy coding! 🎯"
}

# 错误处理
trap 'log_error "Script failed at line $LINENO"' ERR

# 运行主函数
main "$@"