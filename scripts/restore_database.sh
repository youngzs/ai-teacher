#!/bin/bash
# AI Teaching Assistant System - Database Restore Script
# 数据库恢复脚本

set -e  # 遇到错误立即退出

# 配置项
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
BACKUP_DIR="${PROJECT_ROOT}/backups"

# 从环境变量或默认值读取数据库配置
DB_HOST=${DB_HOST:-"localhost"}
DB_PORT=${DB_PORT:-"5432"}
DB_NAME=${POSTGRES_DB:-"ai_teacher_dev"}
DB_USER=${POSTGRES_USER:-"ai_teacher"}

# Docker容器名称（如果使用Docker）
DOCKER_CONTAINER=${DOCKER_CONTAINER:-"ai-teacher-db"}

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
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

# 检查Docker容器是否运行
check_docker_container() {
    if ! docker ps | grep -q "$DOCKER_CONTAINER"; then
        log_error "Docker容器 $DOCKER_CONTAINER 未运行"
        return 1
    fi
    log_info "检测到运行中的Docker容器: $DOCKER_CONTAINER"
}

# 列出可用的备份文件
list_backups() {
    log_info "可用的备份文件:"
    if [ -d "$BACKUP_DIR" ]; then
        find "$BACKUP_DIR" -name "ai_teacher_backup_*.sql.gz" -printf "%T@ %Tc %p\n" | sort -n | cut -d' ' -f2- | nl
    else
        log_warning "备份目录不存在: $BACKUP_DIR"
    fi
}

# 验证备份文件
verify_backup_file() {
    local backup_file="$1"
    
    if [ ! -f "$backup_file" ]; then
        log_error "备份文件不存在: $backup_file"
        return 1
    fi
    
    # 检查文件扩展名
    if [[ "$backup_file" != *.sql.gz && "$backup_file" != *.sql ]]; then
        log_error "无效的备份文件格式，支持的格式: .sql 或 .sql.gz"
        return 1
    fi
    
    # 检查压缩文件是否完整（如果是.gz文件）
    if [[ "$backup_file" == *.gz ]]; then
        if ! gzip -t "$backup_file" 2>/dev/null; then
            log_error "备份文件损坏: $backup_file"
            return 1
        fi
    fi
    
    log_success "备份文件验证通过: $backup_file"
    return 0
}

# 创建数据库备份（恢复前的安全备份）
create_safety_backup() {
    log_info "创建恢复前的安全备份..."
    
    local safety_backup="$BACKUP_DIR/safety_backup_$(date +%Y%m%d_%H%M%S).sql"
    
    if check_docker_container; then
        docker exec "$DOCKER_CONTAINER" pg_dump -U "$DB_USER" -d "$DB_NAME" > "$safety_backup"
    else
        PGPASSWORD="$POSTGRES_PASSWORD" pg_dump -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" > "$safety_backup"
    fi
    
    gzip "$safety_backup"
    log_success "安全备份创建完成: ${safety_backup}.gz"
}

# 恢复数据库
restore_database() {
    local backup_file="$1"
    local skip_safety_backup="${2:-false}"
    
    log_info "=== 开始数据库恢复 ==="
    log_info "源文件: $backup_file"
    log_info "目标数据库: $DB_NAME"
    
    # 验证备份文件
    if ! verify_backup_file "$backup_file"; then
        return 1
    fi
    
    # 创建安全备份（除非明确跳过）
    if [ "$skip_safety_backup" != "true" ]; then
        create_safety_backup
    fi
    
    # 准备恢复命令
    local restore_cmd
    if [[ "$backup_file" == *.gz ]]; then
        restore_cmd="zcat '$backup_file'"
    else
        restore_cmd="cat '$backup_file'"
    fi
    
    # 确认恢复操作
    if [ "${FORCE_RESTORE:-false}" != "true" ]; then
        log_warning "此操作将覆盖数据库 $DB_NAME 中的所有数据！"
        read -p "确定要继续吗？(y/N) " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            log_info "恢复操作已取消"
            return 0
        fi
    fi
    
    # 终止现有连接（可选）
    log_info "终止数据库的现有连接..."
    if check_docker_container; then
        docker exec "$DOCKER_CONTAINER" psql -U postgres -c "SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname = '$DB_NAME' AND pid <> pg_backend_pid();"
    else
        PGPASSWORD="$POSTGRES_PASSWORD" psql -h "$DB_HOST" -p "$DB_PORT" -U postgres -c "SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname = '$DB_NAME' AND pid <> pg_backend_pid();"
    fi
    
    # 删除并重新创建数据库
    log_info "重新创建数据库..."
    if check_docker_container; then
        docker exec "$DOCKER_CONTAINER" psql -U postgres -c "DROP DATABASE IF EXISTS $DB_NAME;"
        docker exec "$DOCKER_CONTAINER" psql -U postgres -c "CREATE DATABASE $DB_NAME OWNER $DB_USER;"
    else
        PGPASSWORD="$POSTGRES_PASSWORD" psql -h "$DB_HOST" -p "$DB_PORT" -U postgres -c "DROP DATABASE IF EXISTS $DB_NAME;"
        PGPASSWORD="$POSTGRES_PASSWORD" psql -h "$DB_HOST" -p "$DB_PORT" -U postgres -c "CREATE DATABASE $DB_NAME OWNER $DB_USER;"
    fi
    
    # 恢复数据
    log_info "开始恢复数据..."
    if check_docker_container; then
        eval "$restore_cmd" | docker exec -i "$DOCKER_CONTAINER" psql -U "$DB_USER" -d "$DB_NAME"
    else
        eval "$restore_cmd" | PGPASSWORD="$POSTGRES_PASSWORD" psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME"
    fi
    
    log_success "数据库恢复完成！"
}

# 显示数据库状态
show_database_status() {
    log_info "数据库状态信息:"
    
    if check_docker_container; then
        docker exec "$DOCKER_CONTAINER" psql -U "$DB_USER" -d "$DB_NAME" -c "\dt"
        docker exec "$DOCKER_CONTAINER" psql -U "$DB_USER" -d "$DB_NAME" -c "SELECT schemaname,tablename,n_tup_ins,n_tup_upd,n_tup_del FROM pg_stat_user_tables;"
    else
        PGPASSWORD="$POSTGRES_PASSWORD" psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -c "\dt"
        PGPASSWORD="$POSTGRES_PASSWORD" psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -c "SELECT schemaname,tablename,n_tup_ins,n_tup_upd,n_tup_del FROM pg_stat_user_tables;"
    fi
}

# 显示使用方法
show_usage() {
    echo "用法: $0 [选项] <备份文件路径>"
    echo ""
    echo "选项:"
    echo "  -l, --list           列出可用的备份文件"
    echo "  -s, --status         显示数据库状态"
    echo "  -f, --force          强制恢复，不询问确认"
    echo "  --no-safety-backup   跳过恢复前的安全备份"
    echo "  -h, --help          显示此帮助信息"
    echo ""
    echo "示例:"
    echo "  $0 /path/to/backup.sql.gz              恢复指定的备份文件"
    echo "  $0 -l                                   列出所有可用备份"
    echo "  $0 -s                                   显示数据库状态"
    echo "  $0 -f --no-safety-backup backup.sql    强制恢复，跳过安全备份"
    echo ""
    echo "环境变量:"
    echo "  DB_HOST             数据库主机 (默认: localhost)"
    echo "  DB_PORT             数据库端口 (默认: 5432)"
    echo "  POSTGRES_DB         数据库名称 (默认: ai_teacher_dev)"
    echo "  POSTGRES_USER       数据库用户 (默认: ai_teacher)"
    echo "  POSTGRES_PASSWORD   数据库密码"
    echo "  DOCKER_CONTAINER    Docker容器名称 (默认: ai-teacher-db)"
    echo "  FORCE_RESTORE       强制恢复模式 (默认: false)"
}

# 主函数
main() {
    local backup_file=""
    local list_backups_only=false
    local show_status_only=false
    local force_restore=false
    local skip_safety_backup=false
    
    # 解析命令行参数
    while [[ $# -gt 0 ]]; do
        case $1 in
            -l|--list)
                list_backups_only=true
                shift
                ;;
            -s|--status)
                show_status_only=true
                shift
                ;;
            -f|--force)
                force_restore=true
                export FORCE_RESTORE=true
                shift
                ;;
            --no-safety-backup)
                skip_safety_backup=true
                shift
                ;;
            -h|--help)
                show_usage
                exit 0
                ;;
            -*)
                log_error "未知选项: $1"
                show_usage
                exit 1
                ;;
            *)
                backup_file="$1"
                shift
                ;;
        esac
    done
    
    # 执行相应的操作
    if [ "$list_backups_only" = true ]; then
        list_backups
        exit 0
    fi
    
    if [ "$show_status_only" = true ]; then
        show_database_status
        exit 0
    fi
    
    # 如果没有指定备份文件，显示使用方法
    if [ -z "$backup_file" ]; then
        log_error "请指定要恢复的备份文件"
        show_usage
        exit 1
    fi
    
    # 检查备份文件是否为相对路径，如果是则添加备份目录前缀
    if [[ "$backup_file" != /* ]]; then
        backup_file="$BACKUP_DIR/$backup_file"
    fi
    
    # 执行恢复
    restore_database "$backup_file" "$skip_safety_backup"
}

# 检查必要的依赖
command -v psql >/dev/null 2>&1 || {
    if ! command -v docker >/dev/null 2>&1; then
        log_error "需要安装 postgresql-client 或 docker"
        exit 1
    fi
}

# 执行主函数
main "$@"