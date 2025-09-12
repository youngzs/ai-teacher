#!/bin/bash
# AI Teaching Assistant System - Development Environment Health Check
# 开发环境健康检查脚本

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

# 全局变量
CHECKS_PASSED=0
CHECKS_FAILED=0
CHECKS_WARNING=0

# 检查结果记录
record_result() {
    local status="$1"
    local message="$2"
    
    case "$status" in
        "PASS")
            log_success "$message"
            ((CHECKS_PASSED++))
            ;;
        "FAIL")
            log_error "$message"
            ((CHECKS_FAILED++))
            ;;
        "WARN")
            log_warning "$message"
            ((CHECKS_WARNING++))
            ;;
    esac
}

# 显示横幅
show_banner() {
    echo -e "${CYAN}${BOLD}"
    echo "┌──────────────────────────────────────────────────────────┐"
    echo "│                AI教学助手系统                            │"
    echo "│              开发环境健康检查                            │"
    echo "└──────────────────────────────────────────────────────────┘"
    echo -e "${NC}"
}

# 检查系统依赖
check_system_dependencies() {
    log_header "系统依赖检查"
    
    # 检查Docker
    if command -v docker >/dev/null 2>&1; then
        if docker info >/dev/null 2>&1; then
            local docker_version=$(docker --version | cut -d' ' -f3 | tr -d ',')
            record_result "PASS" "Docker已安装且运行正常 (版本: $docker_version)"
        else
            record_result "FAIL" "Docker已安装但未运行"
        fi
    else
        record_result "FAIL" "Docker未安装"
    fi
    
    # 检查Docker Compose
    if command -v docker-compose >/dev/null 2>&1; then
        local compose_version=$(docker-compose --version | grep -o '[0-9]\+\.[0-9]\+\.[0-9]\+' | head -1)
        record_result "PASS" "Docker Compose已安装 (版本: $compose_version)"
    elif docker compose version >/dev/null 2>&1; then
        local compose_version=$(docker compose version | grep -o '[0-9]\+\.[0-9]\+\.[0-9]\+' | head -1)
        record_result "PASS" "Docker Compose (plugin)已安装 (版本: $compose_version)"
    else
        record_result "FAIL" "Docker Compose未安装"
    fi
    
    # 检查Git
    if command -v git >/dev/null 2>&1; then
        local git_version=$(git --version | cut -d' ' -f3)
        record_result "PASS" "Git已安装 (版本: $git_version)"
    else
        record_result "WARN" "Git未安装（推荐安装用于版本控制）"
    fi
    
    # 检查Python（开发环境）
    if command -v python3 >/dev/null 2>&1; then
        local python_version=$(python3 --version | cut -d' ' -f2)
        record_result "PASS" "Python3已安装 (版本: $python_version)"
    else
        record_result "WARN" "Python3未安装（仅Docker环境不需要）"
    fi
    
    # 检查Node.js（开发环境）
    if command -v node >/dev/null 2>&1; then
        local node_version=$(node --version)
        record_result "PASS" "Node.js已安装 (版本: $node_version)"
    else
        record_result "WARN" "Node.js未安装（仅Docker环境不需要）"
    fi
}

# 检查项目文件结构
check_project_structure() {
    log_header "项目文件结构检查"
    
    cd "$PROJECT_ROOT"
    
    # 必需的文件
    local required_files=(
        "docker-compose.yml"
        ".env.docker"
        "Dockerfile"
        "requirements.txt"
        "start_docker.sh"
        "stop_docker.sh"
    )
    
    for file in "${required_files[@]}"; do
        if [ -f "$file" ]; then
            record_result "PASS" "必需文件存在: $file"
        else
            record_result "FAIL" "缺少必需文件: $file"
        fi
    done
    
    # 必需的目录
    local required_dirs=(
        "ai-teacher-frontend"
        "app"
        "src"
        "scripts"
        "tests"
    )
    
    for dir in "${required_dirs[@]}"; do
        if [ -d "$dir" ]; then
            record_result "PASS" "必需目录存在: $dir"
        else
            record_result "FAIL" "缺少必需目录: $dir"
        fi
    done
    
    # 前端项目检查
    if [ -f "ai-teacher-frontend/package.json" ]; then
        record_result "PASS" "前端项目配置存在"
        
        # 检查node_modules（如果是开发环境）
        if [ -d "ai-teacher-frontend/node_modules" ]; then
            record_result "PASS" "前端依赖已安装"
        else
            record_result "WARN" "前端依赖未安装（Docker环境不需要）"
        fi
    else
        record_result "FAIL" "前端项目配置缺失"
    fi
}

# 检查环境配置
check_environment_config() {
    log_header "环境配置检查"
    
    cd "$PROJECT_ROOT"
    
    # 检查.env.docker文件
    if [ -f ".env.docker" ]; then
        record_result "PASS" "Docker环境配置文件存在"
        
        # 检查关键配置项
        local required_vars=(
            "POSTGRES_DB"
            "POSTGRES_USER"
            "POSTGRES_PASSWORD"
            "REDIS_PASSWORD"
            "SECRET_KEY"
        )
        
        for var in "${required_vars[@]}"; do
            if grep -q "^${var}=" ".env.docker" 2>/dev/null; then
                record_result "PASS" "环境变量已配置: $var"
            else
                record_result "FAIL" "缺少环境变量: $var"
            fi
        done
        
        # 检查OpenAI API密钥配置
        if grep -q "^OPENAI_API_KEY=sk-" ".env.docker" 2>/dev/null; then
            record_result "PASS" "OpenAI API密钥已配置"
        else
            record_result "WARN" "OpenAI API密钥未配置（AI功能将无法使用）"
        fi
        
    else
        record_result "FAIL" "Docker环境配置文件不存在"
    fi
    
    # 检查开发环境配置
    if [ -f ".env" ]; then
        record_result "PASS" "开发环境配置文件存在"
    else
        record_result "WARN" "开发环境配置文件不存在（仅Docker环境不需要）"
    fi
}

# 检查Docker服务状态
check_docker_services() {
    log_header "Docker服务状态检查"
    
    cd "$PROJECT_ROOT"
    
    # 检查Docker Compose命令
    if command -v docker-compose >/dev/null 2>&1; then
        COMPOSE_CMD="docker-compose"
    elif docker compose version >/dev/null 2>&1; then
        COMPOSE_CMD="docker compose"
    else
        record_result "FAIL" "无法找到Docker Compose命令"
        return
    fi
    
    # 检查服务定义
    if $COMPOSE_CMD config >/dev/null 2>&1; then
        record_result "PASS" "Docker Compose配置有效"
    else
        record_result "FAIL" "Docker Compose配置无效"
        return
    fi
    
    # 检查服务状态
    local services=(
        "database"
        "redis"
        "backend"
        "ai-backend"
        "frontend"
    )
    
    for service in "${services[@]}"; do
        local status=$($COMPOSE_CMD ps --filter "name=$service" --format json 2>/dev/null | jq -r '.State' 2>/dev/null || echo "not_found")
        
        case "$status" in
            "running")
                record_result "PASS" "服务运行中: $service"
                ;;
            "exited"|"dead"|"paused")
                record_result "WARN" "服务已停止: $service"
                ;;
            "not_found"|"")
                record_result "WARN" "服务未启动: $service"
                ;;
            *)
                record_result "WARN" "服务状态未知: $service ($status)"
                ;;
        esac
    done
}

# 检查端口可用性
check_ports() {
    log_header "端口检查"
    
    local ports=(
        "3001:前端应用"
        "8000:后端API"
        "8001:AI后端"
        "5432:PostgreSQL"
        "6379:Redis"
        "5050:PgAdmin"
    )
    
    for port_info in "${ports[@]}"; do
        local port=$(echo "$port_info" | cut -d':' -f1)
        local service=$(echo "$port_info" | cut -d':' -f2)
        
        if netstat -tuln 2>/dev/null | grep -q ":$port " || ss -tuln 2>/dev/null | grep -q ":$port "; then
            record_result "PASS" "端口 $port 正在使用 ($service)"
        else
            record_result "WARN" "端口 $port 未使用 ($service)"
        fi
    done
}

# 检查服务连通性
check_service_connectivity() {
    log_header "服务连通性检查"
    
    # 检查后端API
    if curl -f -s --max-time 5 http://localhost:8000/health >/dev/null 2>&1; then
        record_result "PASS" "后端API可访问 (http://localhost:8000)"
    else
        record_result "WARN" "后端API不可访问或未启动"
    fi
    
    # 检查AI后端
    if curl -f -s --max-time 5 http://localhost:8001/health >/dev/null 2>&1; then
        record_result "PASS" "AI后端可访问 (http://localhost:8001)"
    else
        record_result "WARN" "AI后端不可访问或未启动"
    fi
    
    # 检查前端
    if curl -f -s --max-time 5 http://localhost:3001 >/dev/null 2>&1; then
        record_result "PASS" "前端应用可访问 (http://localhost:3001)"
    else
        record_result "WARN" "前端应用不可访问或未启动"
    fi
    
    # 检查数据库连接（如果Docker容器运行）
    if docker ps --format "table {{.Names}}" | grep -q "ai-teacher-db"; then
        if docker exec ai-teacher-db pg_isready -U ai_teacher -d ai_teacher_dev >/dev/null 2>&1; then
            record_result "PASS" "PostgreSQL数据库连接正常"
        else
            record_result "FAIL" "PostgreSQL数据库连接失败"
        fi
    else
        record_result "WARN" "PostgreSQL容器未运行"
    fi
    
    # 检查Redis连接（如果Docker容器运行）
    if docker ps --format "table {{.Names}}" | grep -q "ai-teacher-redis"; then
        if docker exec ai-teacher-redis redis-cli ping >/dev/null 2>&1; then
            record_result "PASS" "Redis连接正常"
        else
            record_result "FAIL" "Redis连接失败"
        fi
    else
        record_result "WARN" "Redis容器未运行"
    fi
}

# 检查磁盘空间
check_disk_space() {
    log_header "磁盘空间检查"
    
    local available_space=$(df "$PROJECT_ROOT" | awk 'NR==2 {print $4}')
    local available_gb=$((available_space / 1024 / 1024))
    
    if [ "$available_gb" -gt 5 ]; then
        record_result "PASS" "磁盘空间充足 (${available_gb}GB可用)"
    elif [ "$available_gb" -gt 2 ]; then
        record_result "WARN" "磁盘空间较少 (${available_gb}GB可用)"
    else
        record_result "FAIL" "磁盘空间不足 (${available_gb}GB可用)"
    fi
    
    # 检查Docker空间使用情况
    if command -v docker >/dev/null 2>&1 && docker info >/dev/null 2>&1; then
        local docker_space=$(docker system df --format "table {{.Size}}" 2>/dev/null | tail -1 || echo "未知")
        log_info "Docker空间使用: $docker_space"
    fi
}

# 显示总结报告
show_summary() {
    log_header "健康检查总结"
    
    local total_checks=$((CHECKS_PASSED + CHECKS_FAILED + CHECKS_WARNING))
    
    echo -e "${BOLD}检查结果统计:${NC}"
    echo "  ✅ 通过: $CHECKS_PASSED"
    echo "  ❌ 失败: $CHECKS_FAILED"
    echo "  ⚠️  警告: $CHECKS_WARNING"
    echo "  📊 总计: $total_checks"
    
    echo
    if [ "$CHECKS_FAILED" -eq 0 ]; then
        if [ "$CHECKS_WARNING" -eq 0 ]; then
            log_success "🎉 所有检查都通过了！环境完全健康。"
        else
            log_warning "⚠️  大部分检查通过，但有一些警告需要关注。"
        fi
    else
        log_error "❌ 发现 $CHECKS_FAILED 个严重问题需要解决。"
        echo
        log_info "建议操作:"
        echo "  1. 检查失败的项目并按照提示进行修复"
        echo "  2. 运行 ./start_docker.sh 启动服务"
        echo "  3. 重新运行此健康检查脚本"
    fi
    
    echo
    log_info "快速操作指南:"
    echo "  启动服务:     ./start_docker.sh"
    echo "  停止服务:     ./stop_docker.sh"
    echo "  查看日志:     docker-compose logs -f"
    echo "  重新检查:     ./health_check.sh"
    
    # 返回适当的退出代码
    if [ "$CHECKS_FAILED" -gt 0 ]; then
        return 1
    else
        return 0
    fi
}

# 显示使用方法
show_usage() {
    echo "用法: $0 [选项]"
    echo ""
    echo "选项:"
    echo "  --quick        快速检查（跳过服务连通性测试）"
    echo "  --services-only 只检查服务状态"
    echo "  --json         以JSON格式输出结果"
    echo "  -h, --help     显示此帮助信息"
    echo ""
    echo "示例:"
    echo "  $0             完整健康检查"
    echo "  $0 --quick     快速检查"
}

# 主函数
main() {
    local quick_check=false
    local services_only=false
    local json_output=false
    
    # 解析命令行参数
    while [[ $# -gt 0 ]]; do
        case $1 in
            --quick)
                quick_check=true
                shift
                ;;
            --services-only)
                services_only=true
                shift
                ;;
            --json)
                json_output=true
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
    
    # 显示横幅（非JSON模式）
    if [ "$json_output" != "true" ]; then
        show_banner
    fi
    
    # 执行检查
    if [ "$services_only" != "true" ]; then
        check_system_dependencies
        check_project_structure
        check_environment_config
        check_disk_space
    fi
    
    check_docker_services
    check_ports
    
    if [ "$quick_check" != "true" ]; then
        check_service_connectivity
    fi
    
    # 显示结果
    if [ "$json_output" = "true" ]; then
        echo "{"
        echo "  \"checks_passed\": $CHECKS_PASSED,"
        echo "  \"checks_failed\": $CHECKS_FAILED,"
        echo "  \"checks_warning\": $CHECKS_WARNING,"
        echo "  \"total_checks\": $((CHECKS_PASSED + CHECKS_FAILED + CHECKS_WARNING)),"
        echo "  \"status\": \"$([ $CHECKS_FAILED -eq 0 ] && echo "healthy" || echo "unhealthy")\","
        echo "  \"timestamp\": \"$(date -Iseconds)\""
        echo "}"
    else
        show_summary
    fi
}

# 执行主函数
main "$@"