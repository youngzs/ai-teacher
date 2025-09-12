#!/bin/bash
# AI Teaching Assistant System - Database Backup Script
# 数据库备份脚本

set -e  # 遇到错误立即退出

# 配置项
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
BACKUP_DIR="${PROJECT_ROOT}/backups"
DATE=$(date +%Y%m%d_%H%M%S)

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

# 创建备份目录
create_backup_dir() {
    if [ ! -d "$BACKUP_DIR" ]; then
        mkdir -p "$BACKUP_DIR"
        log_info "创建备份目录: $BACKUP_DIR"
    fi
}

# 检查Docker容器是否运行
check_docker_container() {
    if ! docker ps | grep -q "$DOCKER_CONTAINER"; then
        log_error "Docker容器 $DOCKER_CONTAINER 未运行"
        return 1
    fi
    log_info "检测到运行中的Docker容器: $DOCKER_CONTAINER"
}

# 执行数据库备份
backup_database() {
    local backup_file="$BACKUP_DIR/ai_teacher_backup_${DATE}.sql"
    local compressed_file="${backup_file}.gz"
    
    log_info "开始备份数据库 $DB_NAME 到 $backup_file"
    
    if check_docker_container; then
        # 使用Docker执行备份
        docker exec "$DOCKER_CONTAINER" pg_dump -U "$DB_USER" -d "$DB_NAME" > "$backup_file"
    else
        # 直接连接数据库备份
        PGPASSWORD="$POSTGRES_PASSWORD" pg_dump -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" > "$backup_file"
    fi
    
    # 压缩备份文件
    gzip "$backup_file"
    
    local file_size=$(du -h "$compressed_file" | cut -f1)
    log_success "数据库备份完成: $compressed_file (大小: $file_size)"
    
    echo "$compressed_file"
}

# 备份数据库模式（只备份结构，不包括数据）
backup_schema_only() {
    local schema_file="$BACKUP_DIR/ai_teacher_schema_${DATE}.sql"
    
    log_info "开始备份数据库模式到 $schema_file"
    
    if check_docker_container; then
        docker exec "$DOCKER_CONTAINER" pg_dump -U "$DB_USER" -d "$DB_NAME" --schema-only > "$schema_file"
    else
        PGPASSWORD="$POSTGRES_PASSWORD" pg_dump -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" --schema-only > "$schema_file"
    fi
    
    gzip "$schema_file"
    log_success "数据库模式备份完成: ${schema_file}.gz"
    
    echo "${schema_file}.gz"
}

# 清理旧备份文件（保留最近7天的备份）
cleanup_old_backups() {
    log_info "清理超过7天的旧备份文件"
    
    find "$BACKUP_DIR" -name "ai_teacher_backup_*.sql.gz" -mtime +7 -delete
    find "$BACKUP_DIR" -name "ai_teacher_schema_*.sql.gz" -mtime +7 -delete
    
    log_success "旧备份文件清理完成"
}

# 验证备份文件完整性
verify_backup() {
    local backup_file="$1"
    
    if [ ! -f "$backup_file" ]; then
        log_error "备份文件不存在: $backup_file"
        return 1
    fi
    
    # 检查压缩文件是否完整
    if ! gzip -t "$backup_file" 2>/dev/null; then
        log_error "备份文件损坏: $backup_file"
        return 1
    fi
    
    log_success "备份文件验证通过: $backup_file"
    return 0
}

# 主函数
main() {
    log_info "=== AI教学助手系统数据库备份 ==="
    log_info "开始时间: $(date)"
    
    # 创建备份目录
    create_backup_dir
    
    # 执行完整备份
    backup_file=$(backup_database)
    
    # 验证备份
    if verify_backup "$backup_file"; then
        log_success "数据库备份成功完成"
    else
        log_error "数据库备份验证失败"
        exit 1
    fi
    
    # 执行模式备份（可选）
    if [ "${BACKUP_SCHEMA:-false}" = "true" ]; then
        schema_file=$(backup_schema_only)
        verify_backup "$schema_file"
    fi
    
    # 清理旧备份
    cleanup_old_backups
    
    log_info "备份完成时间: $(date)"
    log_success "=== 数据库备份任务完成 ==="
}

# 显示使用方法
show_usage() {
    echo "用法: $0 [选项]"
    echo ""
    echo "选项:"
    echo "  -s, --schema-only    仅备份数据库模式（结构）"
    echo "  -h, --help          显示此帮助信息"
    echo ""
    echo "环境变量:"
    echo "  DB_HOST             数据库主机 (默认: localhost)"
    echo "  DB_PORT             数据库端口 (默认: 5432)"
    echo "  POSTGRES_DB         数据库名称 (默认: ai_teacher_dev)"
    echo "  POSTGRES_USER       数据库用户 (默认: ai_teacher)"
    echo "  POSTGRES_PASSWORD   数据库密码"
    echo "  DOCKER_CONTAINER    Docker容器名称 (默认: ai-teacher-db)"
    echo "  BACKUP_SCHEMA       是否备份模式 (默认: false)"
}

# 解析命令行参数
while [[ $# -gt 0 ]]; do
    case $1 in
        -s|--schema-only)
            BACKUP_SCHEMA=true
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

# 检查必要的依赖
command -v pg_dump >/dev/null 2>&1 || {
    if ! command -v docker >/dev/null 2>&1; then
        log_error "需要安装 postgresql-client 或 docker"
        exit 1
    fi
}

# 执行主函数
main