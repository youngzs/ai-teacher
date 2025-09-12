#!/bin/bash
# AI Teaching Assistant System - One-Click Docker Startup Script
# 一键启动Docker开发环境脚本

set -e  # 遇到错误立即退出

# 脚本目录和项目根目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$SCRIPT_DIR"

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m' # No Color

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

log_header() {
    echo -e "${CYAN}${BOLD}=== $1 ===${NC}"
}

# 显示横幅
show_banner() {
    echo -e "${CYAN}${BOLD}"
    echo "┌──────────────────────────────────────────────────────────┐"
    echo "│                AI教学助手系统                            │"
    echo "│           Docker开发环境一键启动脚本                    │"
    echo "│                                                          │"
    echo "│  服务包括:                                               │"
    echo "│  • 前端 (React)          - http://localhost:3001        │"
    echo "│  • 后端API              - http://localhost:8000        │"
    echo "│  • AI后端               - http://localhost:8001        │"
    echo "│  • PostgreSQL数据库      - localhost:5432              │"
    echo "│  • Redis缓存            - localhost:6379               │"
    echo "│  • PgAdmin (可选)        - http://localhost:5050        │"
    echo "└──────────────────────────────────────────────────────────┘"
    echo -e "${NC}"
}

# 检查必要的依赖
check_dependencies() {
    log_info "检查系统依赖..."
    
    if ! command -v docker >/dev/null 2>&1; then
        log_error "未找到Docker，请先安装Docker"
        log_info "安装指南: https://docs.docker.com/get-docker/"
        exit 1
    fi
    
    if ! command -v docker-compose >/dev/null 2>&1 && ! docker compose version >/dev/null 2>&1; then
        log_error "未找到Docker Compose，请先安装Docker Compose"
        log_info "安装指南: https://docs.docker.com/compose/install/"
        exit 1
    fi
    
    # 检查Docker是否运行
    if ! docker info >/dev/null 2>&1; then
        log_error "Docker服务未运行，请启动Docker"
        exit 1
    fi
    
    log_success "系统依赖检查通过"
}

# 检查并创建环境文件
setup_environment() {
    log_info "设置环境变量..."
    
    # 检查是否存在.env.docker文件
    if [ ! -f "$PROJECT_ROOT/.env.docker" ]; then
        log_error "未找到.env.docker文件，请确保该文件存在"
        exit 1
    fi
    
    # 检查是否需要配置OpenAI API密钥
    if ! grep -q "OPENAI_API_KEY=sk-" "$PROJECT_ROOT/.env.docker" 2>/dev/null; then
        log_warning "未检测到OpenAI API密钥配置"
        log_info "请在.env.docker文件中设置OPENAI_API_KEY变量"
        
        read -p "是否现在设置OpenAI API密钥? (y/N) " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            read -p "请输入OpenAI API密钥: " -s openai_key
            echo
            if [ ! -z "$openai_key" ]; then
                # 使用sed更新环境文件中的OPENAI_API_KEY
                if grep -q "OPENAI_API_KEY=" "$PROJECT_ROOT/.env.docker"; then
                    sed -i "s/OPENAI_API_KEY=.*/OPENAI_API_KEY=$openai_key/" "$PROJECT_ROOT/.env.docker"
                else
                    echo "OPENAI_API_KEY=$openai_key" >> "$PROJECT_ROOT/.env.docker"
                fi
                log_success "OpenAI API密钥已设置"
            fi
        fi
    fi
    
    log_success "环境设置完成"
}

# 清理旧容器和卷（可选）
cleanup_if_needed() {
    if [ "${CLEAN_START:-false}" = "true" ]; then
        log_warning "执行清理操作，停止并删除所有容器和卷..."
        
        # 使用docker-compose或docker compose
        if command -v docker-compose >/dev/null 2>&1; then
            COMPOSE_CMD="docker-compose"
        else
            COMPOSE_CMD="docker compose"
        fi
        
        cd "$PROJECT_ROOT"
        $COMPOSE_CMD down -v --remove-orphans 2>/dev/null || true
        
        # 清理相关的Docker镜像（可选）
        if [ "${CLEAN_IMAGES:-false}" = "true" ]; then
            log_info "清理Docker镜像..."
            docker rmi $(docker images "ai-teacher*" -q) 2>/dev/null || true
        fi
        
        log_success "清理完成"
    fi
}

# 启动服务
start_services() {
    log_header "启动Docker服务"
    
    cd "$PROJECT_ROOT"
    
    # 检查使用的Docker Compose命令
    if command -v docker-compose >/dev/null 2>&1; then
        COMPOSE_CMD="docker-compose"
    else
        COMPOSE_CMD="docker compose"
    fi
    
    log_info "使用命令: $COMPOSE_CMD"
    
    # 构建和启动核心服务
    log_info "构建和启动核心服务..."
    $COMPOSE_CMD up -d --build database redis backend ai-backend frontend
    
    # 等待数据库启动
    log_info "等待数据库启动..."
    for i in {1..30}; do
        if $COMPOSE_CMD exec database pg_isready -U ai_teacher -d ai_teacher_dev >/dev/null 2>&1; then
            log_success "数据库已就绪"
            break
        fi
        if [ $i -eq 30 ]; then
            log_error "数据库启动超时"
            exit 1
        fi
        sleep 2
        echo -n "."
    done
    echo
    
    # 可选服务（如果指定了profile）
    if [ "${WITH_TOOLS:-false}" = "true" ]; then
        log_info "启动管理工具..."
        $COMPOSE_CMD --profile tools up -d
    fi
    
    if [ "${WITH_MONITORING:-false}" = "true" ]; then
        log_info "启动监控服务..."
        $COMPOSE_CMD --profile monitoring up -d
    fi
    
    log_success "所有服务启动完成"
}

# 等待服务就绪
wait_for_services() {
    log_header "等待服务就绪"
    
    # 等待后端API就绪
    log_info "等待后端API服务..."
    for i in {1..60}; do
        if curl -f http://localhost:8000/health >/dev/null 2>&1; then
            log_success "后端API已就绪"
            break
        fi
        if [ $i -eq 60 ]; then
            log_warning "后端API启动超时，但将继续..."
            break
        fi
        sleep 2
        echo -n "."
    done
    echo
    
    # 等待AI后端服务
    log_info "等待AI后端服务..."
    for i in {1..60}; do
        if curl -f http://localhost:8001/health >/dev/null 2>&1; then
            log_success "AI后端已就绪"
            break
        fi
        if [ $i -eq 60 ]; then
            log_warning "AI后端启动超时，但将继续..."
            break
        fi
        sleep 2
        echo -n "."
    done
    echo
    
    # 等待前端服务
    log_info "等待前端服务..."
    for i in {1..60}; do
        if curl -f http://localhost:3001 >/dev/null 2>&1; then
            log_success "前端服务已就绪"
            break
        fi
        if [ $i -eq 60 ]; then
            log_warning "前端服务启动超时，但将继续..."
            break
        fi
        sleep 2
        echo -n "."
    done
    echo
}

# 显示服务状态和访问信息
show_service_info() {
    log_header "服务状态和访问信息"
    
    # 使用docker-compose或docker compose
    if command -v docker-compose >/dev/null 2>&1; then
        COMPOSE_CMD="docker-compose"
    else
        COMPOSE_CMD="docker compose"
    fi
    
    cd "$PROJECT_ROOT"
    $COMPOSE_CMD ps
    
    echo
    log_success "服务访问地址:"
    echo "  🌐 前端应用:          http://localhost:3001"
    echo "  🔧 后端API:           http://localhost:8000"
    echo "  🤖 AI后端:            http://localhost:8001"
    echo "  🗄️  数据库:            localhost:5432"
    echo "  📊 Redis:             localhost:6379"
    
    if [ "${WITH_TOOLS:-false}" = "true" ]; then
        echo "  🔍 PgAdmin:           http://localhost:5050"
        echo "  📈 Redis Commander:   http://localhost:8081"
    fi
    
    if [ "${WITH_MONITORING:-false}" = "true" ]; then
        echo "  📊 Prometheus:        http://localhost:9090"
        echo "  📈 Grafana:           http://localhost:3001"
    fi
    
    echo
    log_info "默认登录凭据:"
    echo "  Admin用户:    admin@aiteacher.local / password"
    echo "  教师用户:     teacher@aiteacher.local / password"
    echo "  学生用户:     student@aiteacher.local / password"
    
    echo
    log_info "有用的命令:"
    echo "  查看日志:     $COMPOSE_CMD logs -f [服务名]"
    echo "  停止服务:     $COMPOSE_CMD down"
    echo "  重启服务:     $COMPOSE_CMD restart [服务名]"
    echo "  查看状态:     $COMPOSE_CMD ps"
}

# 显示使用方法
show_usage() {
    echo "用法: $0 [选项]"
    echo ""
    echo "选项:"
    echo "  --clean-start       清理旧容器和卷后重新启动"
    echo "  --clean-images      同时清理Docker镜像（需要--clean-start）"
    echo "  --with-tools        启动管理工具（PgAdmin, Redis Commander）"
    echo "  --with-monitoring   启动监控服务（Prometheus, Grafana）"
    echo "  --no-wait          不等待服务就绪"
    echo "  -h, --help         显示此帮助信息"
    echo ""
    echo "环境变量:"
    echo "  CLEAN_START=true       执行清理启动"
    echo "  CLEAN_IMAGES=true      清理Docker镜像"
    echo "  WITH_TOOLS=true        启用管理工具"
    echo "  WITH_MONITORING=true   启用监控服务"
    echo ""
    echo "示例:"
    echo "  $0                     正常启动"
    echo "  $0 --clean-start       清理后启动"
    echo "  $0 --with-tools        启动包含管理工具"
}

# 主函数
main() {
    local no_wait=false
    
    # 解析命令行参数
    while [[ $# -gt 0 ]]; do
        case $1 in
            --clean-start)
                export CLEAN_START=true
                shift
                ;;
            --clean-images)
                export CLEAN_IMAGES=true
                shift
                ;;
            --with-tools)
                export WITH_TOOLS=true
                shift
                ;;
            --with-monitoring)
                export WITH_MONITORING=true
                shift
                ;;
            --no-wait)
                no_wait=true
                shift
                ;;
            -h|--help)
                show_usage
                exit 0
                ;;
            *)
                log_error "未知选项: $1"
                show_usage
                exit 1
                ;;
        esac
    done
    
    # 显示横幅
    show_banner
    
    # 执行启动流程
    check_dependencies
    setup_environment
    cleanup_if_needed
    start_services
    
    if [ "$no_wait" != "true" ]; then
        wait_for_services
    fi
    
    show_service_info
    
    log_success "AI教学助手系统已成功启动！"
    log_info "按 Ctrl+C 可以停止查看日志，服务将继续在后台运行"
    
    # 跟踪日志（可选）
    if [ "${FOLLOW_LOGS:-true}" = "true" ]; then
        echo
        log_info "显示实时日志（按 Ctrl+C 退出日志查看）:"
        
        # 使用docker-compose或docker compose
        if command -v docker-compose >/dev/null 2>&1; then
            COMPOSE_CMD="docker-compose"
        else
            COMPOSE_CMD="docker compose"
        fi
        
        cd "$PROJECT_ROOT"
        $COMPOSE_CMD logs -f --tail=50 backend ai-backend frontend || true
    fi
}

# 信号处理
trap 'log_info "脚本被中断，服务继续在后台运行"; exit 0' INT

# 执行主函数
main "$@"