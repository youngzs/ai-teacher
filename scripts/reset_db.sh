#!/bin/bash
# AI Teaching Assistant System - Database Reset Script
# 数据库重置脚本

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

# 显示帮助信息
show_help() {
    echo "AI Teaching Assistant System - Database Reset Script"
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  --env ENV        Environment (dev|test|prod) [default: dev]"
    echo "  --backup         Create backup before reset"
    echo "  --seed-data      Load seed data after reset"
    echo "  --force          Skip confirmation prompt"
    echo "  --docker         Use Docker database (default)"
    echo "  --local          Use local database"
    echo "  -h, --help       Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0                              # Reset dev database with confirmation"
    echo "  $0 --env test --force          # Reset test database without confirmation"
    echo "  $0 --backup --seed-data        # Backup, reset, and load seed data"
}

# 创建数据库备份
create_backup() {
    local env=$1
    log_info "Creating database backup..."
    
    # 激活虚拟环境（如果存在）
    if [ -d "venv" ]; then
        source venv/bin/activate
    fi
    
    python scripts/manage_db.py backup --env $env
    
    if [ $? -eq 0 ]; then
        log_success "Database backup created"
    else
        log_error "Failed to create backup"
        return 1
    fi
}

# 重置数据库
reset_database() {
    local env=$1
    log_info "Resetting database ($env environment)..."
    
    # 激活虚拟环境（如果存在）
    if [ -d "venv" ]; then
        source venv/bin/activate
    fi
    
    python scripts/manage_db.py reset --env $env
    
    if [ $? -eq 0 ]; then
        log_success "Database reset completed"
    else
        log_error "Failed to reset database"
        return 1
    fi
}

# 加载种子数据
load_seed_data() {
    local env=$1
    log_info "Loading seed data..."
    
    # 检查种子数据文件
    seed_file="scripts/seed_data.sql"
    if [ ! -f "$seed_file" ]; then
        log_warning "Seed data file not found: $seed_file"
        return 0
    fi
    
    # 激活虚拟环境（如果存在）
    if [ -d "venv" ]; then
        source venv/bin/activate
    fi
    
    # 执行种子数据脚本
    case $env in
        dev)
            DB_URL="postgresql+asyncpg://ai_teacher:dev_password_123@localhost:5432/ai_teacher_dev"
            ;;
        test)
            DB_URL="postgresql+asyncpg://ai_teacher:dev_password_123@localhost:5432/ai_teacher_test"
            ;;
        prod)
            log_error "Cannot load seed data in production environment"
            return 1
            ;;
        *)
            log_error "Unknown environment: $env"
            return 1
            ;;
    esac
    
    # 使用psql执行种子数据
    if [ "$USE_DOCKER" = true ]; then
        docker-compose exec database psql -U ai_teacher -d ai_teacher_${env} -f /docker-entrypoint-initdb.d/seed_data.sql
    else
        psql $DB_URL -f $seed_file
    fi
    
    if [ $? -eq 0 ]; then
        log_success "Seed data loaded"
    else
        log_error "Failed to load seed data"
        return 1
    fi
}

# 验证数据库连接
verify_connection() {
    local env=$1
    log_info "Verifying database connection..."
    
    # 激活虚拟环境（如果存在）
    if [ -d "venv" ]; then
        source venv/bin/activate
    fi
    
    python scripts/manage_db.py check --env $env
    
    if [ $? -eq 0 ]; then
        log_success "Database connection verified"
        python scripts/manage_db.py info --env $env
    else
        log_error "Database connection failed"
        return 1
    fi
}

# 检查Docker服务状态
check_docker_services() {
    if [ "$USE_DOCKER" = true ]; then
        log_info "Checking Docker services..."
        
        # 检查数据库容器状态
        if ! docker-compose ps database | grep -q "Up"; then
            log_error "Database container is not running"
            log_info "Starting database container..."
            docker-compose up -d database
            sleep 5
        fi
        
        # 等待数据库准备就绪
        log_info "Waiting for database to be ready..."
        max_attempts=30
        attempt=1
        
        while [ $attempt -le $max_attempts ]; do
            if docker-compose exec database pg_isready -U ai_teacher > /dev/null 2>&1; then
                log_success "Database is ready"
                break
            fi
            
            if [ $attempt -eq $max_attempts ]; then
                log_error "Database failed to start within timeout"
                return 1
            fi
            
            sleep 2
            ((attempt++))
        done
    fi
}

# 主函数
main() {
    # 默认参数
    ENVIRONMENT="dev"
    CREATE_BACKUP=false
    LOAD_SEED_DATA=false
    FORCE=false
    USE_DOCKER=true
    
    # 解析命令行参数
    while [[ $# -gt 0 ]]; do
        case $1 in
            --env)
                ENVIRONMENT="$2"
                shift 2
                ;;
            --backup)
                CREATE_BACKUP=true
                shift
                ;;
            --seed-data)
                LOAD_SEED_DATA=true
                shift
                ;;
            --force)
                FORCE=true
                shift
                ;;
            --docker)
                USE_DOCKER=true
                shift
                ;;
            --local)
                USE_DOCKER=false
                shift
                ;;
            -h|--help)
                show_help
                exit 0
                ;;
            *)
                log_error "Unknown option: $1"
                show_help
                exit 1
                ;;
        esac
    done
    
    # 验证环境参数
    case $ENVIRONMENT in
        dev|test|prod)
            ;;
        *)
            log_error "Invalid environment: $ENVIRONMENT. Must be dev, test, or prod."
            exit 1
            ;;
    esac
    
    echo "🔄 AI Teaching Assistant System - Database Reset"
    echo "=============================================="
    echo "Environment: $ENVIRONMENT"
    echo "Create backup: $CREATE_BACKUP"
    echo "Load seed data: $LOAD_SEED_DATA"
    echo "Use Docker: $USE_DOCKER"
    echo "=============================================="
    
    # 确认操作
    if [ "$FORCE" = false ]; then
        echo ""
        log_warning "This will permanently delete all data in the $ENVIRONMENT database!"
        read -p "Are you sure you want to continue? [y/N] " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            log_info "Operation cancelled"
            exit 0
        fi
    fi
    
    # 检查Docker服务（如果使用Docker）
    if [ "$USE_DOCKER" = true ]; then
        check_docker_services
        if [ $? -ne 0 ]; then
            exit 1
        fi
    fi
    
    # 创建备份
    if [ "$CREATE_BACKUP" = true ]; then
        create_backup $ENVIRONMENT
        if [ $? -ne 0 ]; then
            exit 1
        fi
    fi
    
    # 重置数据库
    reset_database $ENVIRONMENT
    if [ $? -ne 0 ]; then
        exit 1
    fi
    
    # 加载种子数据
    if [ "$LOAD_SEED_DATA" = true ]; then
        load_seed_data $ENVIRONMENT
        if [ $? -ne 0 ]; then
            log_warning "Failed to load seed data, but database reset was successful"
        fi
    fi
    
    # 验证连接
    verify_connection $ENVIRONMENT
    if [ $? -ne 0 ]; then
        exit 1
    fi
    
    echo ""
    log_success "🎉 Database reset completed successfully!"
    
    if [ "$CREATE_BACKUP" = true ]; then
        echo "💾 Backup was created before reset"
    fi
    
    if [ "$LOAD_SEED_DATA" = true ]; then
        echo "🌱 Seed data was loaded"
    fi
    
    echo ""
    echo "💡 Next steps:"
    echo "  - Use 'python scripts/manage_db.py info --env $ENVIRONMENT' to view database info"
    echo "  - Use 'python scripts/health_check.py' to run system health checks"
    echo "  - Start your development server with './scripts/start_dev.sh'"
}

# 错误处理
trap 'log_error "Script failed at line $LINENO"' ERR

# 运行主函数
main "$@"