#!/bin/bash
# AI Teaching Assistant System - Docker Stop Script
# Docker停止脚本

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
    echo "│             Docker环境停止脚本                          │"
    echo "└──────────────────────────────────────────────────────────┘"
    echo -e "${NC}"
}

# 检查Docker和Docker Compose
check_dependencies() {
    if ! command -v docker >/dev/null 2>&1; then
        log_error "未找到Docker"
        exit 1
    fi
    
    if ! command -v docker-compose >/dev/null 2>&1 && ! docker compose version >/dev/null 2>&1; then
        log_error "未找到Docker Compose"
        exit 1
    fi
    
    # 检查Docker是否运行
    if ! docker info >/dev/null 2>&1; then
        log_error "Docker服务未运行"
        exit 1
    fi
}

# 停止服务
stop_services() {
    log_header "停止Docker服务"
    
    cd "$PROJECT_ROOT"
    
    # 检查使用的Docker Compose命令
    if command -v docker-compose >/dev/null 2>&1; then
        COMPOSE_CMD="docker-compose"
    else
        COMPOSE_CMD="docker compose"
    fi
    
    log_info "使用命令: $COMPOSE_CMD"
    
    # 显示当前运行的服务
    log_info "当前运行的服务:"
    $COMPOSE_CMD ps --filter "status=running" --format table || true
    
    # 停止服务
    if [ "${REMOVE_VOLUMES:-false}" = "true" ]; then
        log_warning "停止服务并删除卷..."
        $COMPOSE_CMD down -v --remove-orphans
    elif [ "${REMOVE_CONTAINERS:-false}" = "true" ]; then
        log_info "停止服务并删除容器..."
        $COMPOSE_CMD down --remove-orphans
    else
        log_info "停止服务（保留容器和卷）..."
        $COMPOSE_CMD stop
    fi
    
    log_success "服务停止完成"
}

# 清理Docker资源
cleanup_docker_resources() {
    if [ "${CLEANUP_RESOURCES:-false}" = "true" ]; then
        log_header "清理Docker资源"
        
        # 清理未使用的容器
        log_info "清理停止的容器..."
        docker container prune -f
        
        # 清理未使用的镜像
        if [ "${CLEANUP_IMAGES:-false}" = "true" ]; then
            log_info "清理未使用的镜像..."
            docker image prune -f
            
            if [ "${CLEANUP_ALL_IMAGES:-false}" = "true" ]; then
                log_info "清理所有未使用的镜像..."
                docker image prune -af
            fi
        fi
        
        # 清理未使用的网络
        log_info "清理未使用的网络..."
        docker network prune -f
        
        # 清理未使用的卷（如果指定）
        if [ "${CLEANUP_VOLUMES:-false}" = "true" ]; then
            log_warning "清理未使用的卷..."
            docker volume prune -f
        fi
        
        log_success "Docker资源清理完成"
    fi
}

# 显示服务状态
show_status() {
    log_header "当前服务状态"
    
    cd "$PROJECT_ROOT"
    
    # 检查使用的Docker Compose命令
    if command -v docker-compose >/dev/null 2>&1; then
        COMPOSE_CMD="docker-compose"
    else
        COMPOSE_CMD="docker compose"
    fi
    
    $COMPOSE_CMD ps --all || true
    
    echo
    log_info "Docker系统信息:"
    docker system df
}

# 显示使用方法
show_usage() {
    echo "用法: $0 [选项]"
    echo ""
    echo "选项:"
    echo "  --remove-containers    停止并删除容器"
    echo "  --remove-volumes      停止并删除容器和卷"
    echo "  --cleanup             清理Docker资源（容器、网络等）"
    echo "  --cleanup-images      清理未使用的镜像"
    echo "  --cleanup-all         清理所有未使用的资源（包括镜像）"
    echo "  --cleanup-volumes     清理未使用的卷（谨慎使用）"
    echo "  --status-only         只显示状态信息"
    echo "  -h, --help           显示此帮助信息"
    echo ""
    echo "示例:"
    echo "  $0                           正常停止服务"
    echo "  $0 --remove-containers       停止并删除容器"
    echo "  $0 --remove-volumes          停止并删除容器和卷"
    echo "  $0 --cleanup --cleanup-images 停止并清理资源"
}

# 主函数
main() {
    local status_only=false
    
    # 解析命令行参数
    while [[ $# -gt 0 ]]; do
        case $1 in
            --remove-containers)
                export REMOVE_CONTAINERS=true
                shift
                ;;
            --remove-volumes)
                export REMOVE_VOLUMES=true
                shift
                ;;
            --cleanup)
                export CLEANUP_RESOURCES=true
                shift
                ;;
            --cleanup-images)
                export CLEANUP_IMAGES=true
                export CLEANUP_RESOURCES=true
                shift
                ;;
            --cleanup-all)
                export CLEANUP_RESOURCES=true
                export CLEANUP_IMAGES=true
                export CLEANUP_ALL_IMAGES=true
                shift
                ;;
            --cleanup-volumes)
                export CLEANUP_VOLUMES=true
                export CLEANUP_RESOURCES=true
                shift
                ;;
            --status-only)
                status_only=true
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
    
    # 检查依赖
    check_dependencies
    
    if [ "$status_only" = "true" ]; then
        show_status
        exit 0
    fi
    
    # 确认操作（对于危险操作）
    if [ "${REMOVE_VOLUMES:-false}" = "true" ] || [ "${CLEANUP_VOLUMES:-false}" = "true" ]; then
        log_warning "此操作将删除数据卷，数据库数据将丢失！"
        read -p "确定要继续吗？(y/N) " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            log_info "操作已取消"
            exit 0
        fi
    fi
    
    # 执行停止流程
    stop_services
    cleanup_docker_resources
    show_status
    
    log_success "AI教学助手系统已停止"
    
    if [ "${REMOVE_VOLUMES:-false}" != "true" ]; then
        log_info "数据已保留，可以通过 ./start_docker.sh 重新启动"
    fi
}

# 执行主函数
main "$@"