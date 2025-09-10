#!/bin/bash
# AI Teaching Assistant System - Environment Setup Script
# 环境初始化和配置脚本

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
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

log_step() {
    echo -e "${PURPLE}[STEP]${NC} $1"
}

# 显示横幅
show_banner() {
    echo -e "${CYAN}"
    cat << "EOF"
    ___    ____   ______              __              
   /   |  /  _/  /_  __/___  ____ _ ___/ /____  _____  
  / /| |  / /     / / / __ \/ __ `// __/ __/ / / ___/ 
 / ___ |_/ /     / / / /_/ / /_/ // /_/ / / /_/ / /    
/_/  |_/___/    /_/  \____/\__,_/ \__/  \__,_/_/     
                                                     
    Teaching Assistant System - Environment Setup    
EOF
    echo -e "${NC}"
}

# 检查操作系统
detect_os() {
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        OS="linux"
        DISTRO=$(lsb_release -si 2>/dev/null || echo "Unknown")
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        OS="macos"
        DISTRO="macOS"
    elif [[ "$OSTYPE" == "cygwin" ]] || [[ "$OSTYPE" == "msys" ]]; then
        OS="windows"
        DISTRO="Windows"
    else
        OS="unknown"
        DISTRO="Unknown"
    fi
    
    log_info "Detected OS: $DISTRO ($OS)"
}

# 检查和安装系统依赖
install_system_dependencies() {
    log_step "Installing system dependencies..."
    
    case $OS in
        linux)
            if command -v apt-get &> /dev/null; then
                sudo apt-get update
                sudo apt-get install -y curl wget git build-essential python3-dev python3-pip python3-venv postgresql-client redis-tools
            elif command -v yum &> /dev/null; then
                sudo yum update -y
                sudo yum install -y curl wget git gcc gcc-c++ python3-devel python3-pip postgresql redis
            elif command -v pacman &> /dev/null; then
                sudo pacman -Syu --noconfirm curl wget git base-devel python python-pip postgresql redis
            else
                log_warning "Unsupported Linux distribution. Please install dependencies manually."
            fi
            ;;
        macos)
            if ! command -v brew &> /dev/null; then
                log_info "Installing Homebrew..."
                /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
            fi
            brew update
            brew install curl wget git python postgresql redis
            ;;
        windows)
            log_warning "Windows detected. Please ensure you have the following installed:"
            echo "  - Git for Windows"
            echo "  - Python 3.9+"
            echo "  - Docker Desktop"
            echo "  - Node.js (optional, for frontend)"
            ;;
        *)
            log_error "Unsupported operating system: $OS"
            exit 1
            ;;
    esac
    
    log_success "System dependencies installation completed"
}

# 检查和安装Docker
install_docker() {
    log_step "Checking Docker installation..."
    
    if command -v docker &> /dev/null; then
        log_info "Docker is already installed"
        docker --version
    else
        log_info "Installing Docker..."
        
        case $OS in
            linux)
                curl -fsSL https://get.docker.com -o get-docker.sh
                sudo sh get-docker.sh
                sudo usermod -aG docker $USER
                rm get-docker.sh
                
                # Install Docker Compose
                sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
                sudo chmod +x /usr/local/bin/docker-compose
                ;;
            macos)
                log_info "Please install Docker Desktop from https://www.docker.com/products/docker-desktop"
                log_warning "After installation, please restart this script"
                exit 1
                ;;
            windows)
                log_info "Please install Docker Desktop from https://www.docker.com/products/docker-desktop"
                log_warning "After installation, please restart this script"
                exit 1
                ;;
        esac
        
        log_success "Docker installation completed"
        log_warning "Please log out and log back in for Docker group changes to take effect"
    fi
    
    # 检查Docker Compose
    if command -v docker-compose &> /dev/null; then
        log_info "Docker Compose is available"
        docker-compose --version
    else
        log_error "Docker Compose is not available"
        exit 1
    fi
}

# 安装Python和虚拟环境
setup_python_environment() {
    log_step "Setting up Python environment..."
    
    # 检查Python版本
    if command -v python3 &> /dev/null; then
        PYTHON_CMD=python3
    elif command -v python &> /dev/null; then
        PYTHON_CMD=python
    else
        log_error "Python is not installed"
        exit 1
    fi
    
    # 检查Python版本
    PYTHON_VERSION=$($PYTHON_CMD --version 2>&1 | cut -d' ' -f2)
    MAJOR_VERSION=$(echo $PYTHON_VERSION | cut -d'.' -f1)
    MINOR_VERSION=$(echo $PYTHON_VERSION | cut -d'.' -f2)
    
    if [ "$MAJOR_VERSION" -lt 3 ] || [ "$MAJOR_VERSION" -eq 3 -a "$MINOR_VERSION" -lt 9 ]; then
        log_error "Python 3.9+ is required. Current version: $PYTHON_VERSION"
        exit 1
    fi
    
    log_info "Python version: $PYTHON_VERSION"
    
    # 创建虚拟环境
    if [ ! -d "venv" ]; then
        log_info "Creating virtual environment..."
        $PYTHON_CMD -m venv venv
        log_success "Virtual environment created"
    else
        log_info "Virtual environment already exists"
    fi
    
    # 激活虚拟环境并升级pip
    source venv/bin/activate
    pip install --upgrade pip setuptools wheel
    
    log_success "Python environment setup completed"
}

# 安装Node.js（可选）
install_nodejs() {
    log_step "Checking Node.js installation..."
    
    if command -v node &> /dev/null; then
        NODE_VERSION=$(node --version)
        log_info "Node.js is already installed: $NODE_VERSION"
        
        # 检查版本是否符合要求
        MAJOR_VERSION=$(echo $NODE_VERSION | cut -d'v' -f2 | cut -d'.' -f1)
        if [ "$MAJOR_VERSION" -lt 16 ]; then
            log_warning "Node.js version is too old. Please update to Node.js 16+"
        fi
    else
        log_info "Node.js is not installed"
        read -p "Do you want to install Node.js? (y/N) " -n 1 -r
        echo
        
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            case $OS in
                linux)
                    curl -fsSL https://deb.nodesource.com/setup_lts.x | sudo -E bash -
                    sudo apt-get install -y nodejs
                    ;;
                macos)
                    brew install node
                    ;;
                windows)
                    log_info "Please install Node.js from https://nodejs.org/"
                    ;;
            esac
            log_success "Node.js installation completed"
        else
            log_warning "Node.js installation skipped. Frontend development may not work."
        fi
    fi
    
    # 检查npm
    if command -v npm &> /dev/null; then
        log_info "npm is available: $(npm --version)"
    fi
}

# 配置Git（如果需要）
configure_git() {
    log_step "Configuring Git..."
    
    if ! command -v git &> /dev/null; then
        log_error "Git is not installed"
        return 1
    fi
    
    # 检查Git配置
    if [ -z "$(git config --global user.name)" ]; then
        read -p "Enter your Git username: " git_username
        git config --global user.name "$git_username"
    fi
    
    if [ -z "$(git config --global user.email)" ]; then
        read -p "Enter your Git email: " git_email
        git config --global user.email "$git_email"
    fi
    
    log_info "Git user: $(git config --global user.name) <$(git config --global user.email)>"
    log_success "Git configuration completed"
}

# 设置项目环境
setup_project_environment() {
    log_step "Setting up project environment..."
    
    # 创建环境变量文件
    if [ ! -f ".env" ]; then
        log_info "Creating environment file from template..."
        cp .env.example .env
        
        # 生成随机密钥
        SECRET_KEY=$(openssl rand -hex 32 2>/dev/null || python -c "import secrets; print(secrets.token_hex(32))")
        
        # 更新.env文件
        if [[ "$OS" == "macos" ]]; then
            sed -i '' "s/your-super-secret-key-change-in-production/$SECRET_KEY/" .env
        else
            sed -i "s/your-super-secret-key-change-in-production/$SECRET_KEY/" .env
        fi
        
        log_success "Environment file created with generated secret key"
    else
        log_info "Environment file already exists"
    fi
    
    # 创建必要的目录
    mkdir -p logs uploads backups docs/assets
    
    # 设置权限
    chmod +x scripts/*.sh 2>/dev/null || true
    
    log_success "Project environment setup completed"
}

# 安装项目依赖
install_project_dependencies() {
    log_step "Installing project dependencies..."
    
    # 激活虚拟环境
    source venv/bin/activate
    
    # 安装Python依赖
    log_info "Installing Python dependencies..."
    pip install -r requirements.txt
    pip install -r requirements-dev.txt
    
    # 安装前端依赖（如果存在Node.js和前端目录）
    if command -v npm &> /dev/null && [ -d "ai-teacher-frontend" ]; then
        log_info "Installing frontend dependencies..."
        cd ai-teacher-frontend
        npm ci
        cd ..
    else
        log_warning "Skipping frontend dependencies (Node.js not available or frontend directory not found)"
    fi
    
    log_success "Project dependencies installed"
}

# 初始化开发工具
setup_development_tools() {
    log_step "Setting up development tools..."
    
    # 激活虚拟环境
    source venv/bin/activate
    
    # 安装pre-commit hooks
    if command -v pre-commit &> /dev/null; then
        log_info "Installing pre-commit hooks..."
        pre-commit install
        log_success "Pre-commit hooks installed"
    else
        log_warning "pre-commit not available, skipping hooks setup"
    fi
    
    # 创建IDE配置文件
    create_ide_configs
    
    log_success "Development tools setup completed"
}

# 创建IDE配置文件
create_ide_configs() {
    log_info "Creating IDE configuration files..."
    
    # VS Code配置
    mkdir -p .vscode
    
    # VS Code设置
    cat > .vscode/settings.json << 'EOF'
{
    "python.defaultInterpreterPath": "./venv/bin/python",
    "python.formatting.provider": "black",
    "python.linting.enabled": true,
    "python.linting.flake8Enabled": true,
    "python.linting.mypyEnabled": true,
    "editor.formatOnSave": true,
    "files.exclude": {
        "**/__pycache__": true,
        "**/*.pyc": true,
        "**/venv": true,
        "**/node_modules": true
    },
    "python.testing.pytestEnabled": true,
    "python.testing.pytestArgs": [
        "tests"
    ]
}
EOF

    # VS Code扩展推荐
    cat > .vscode/extensions.json << 'EOF'
{
    "recommendations": [
        "ms-python.python",
        "ms-python.black-formatter",
        "ms-python.flake8",
        "ms-python.mypy-type-checker",
        "bradlc.vscode-tailwindcss",
        "esbenp.prettier-vscode",
        "ms-vscode.vscode-typescript-next",
        "ms-vscode-remote.remote-containers"
    ]
}
EOF

    # PyCharm配置提示
    cat > .idea-config.txt << 'EOF'
PyCharm Configuration Tips:
1. Set Python interpreter to ./venv/bin/python
2. Enable "Black" as code formatter
3. Enable "flake8" and "mypy" as linters
4. Set test runner to "pytest"
5. Mark "app" directory as Sources Root
EOF

    log_info "IDE configuration files created"
}

# 运行初始验证
run_initial_verification() {
    log_step "Running initial verification..."
    
    # 验证Docker
    if ! docker info &> /dev/null; then
        log_error "Docker is not running"
        return 1
    fi
    
    # 验证Python环境
    source venv/bin/activate
    python -c "import fastapi, sqlalchemy, redis; print('✅ Core Python packages imported successfully')"
    
    # 验证项目结构
    for dir in app scripts tests; do
        if [ -d "$dir" ]; then
            log_info "✅ Directory exists: $dir"
        else
            log_warning "❌ Directory missing: $dir"
        fi
    done
    
    for file in requirements.txt requirements-dev.txt .env; do
        if [ -f "$file" ]; then
            log_info "✅ File exists: $file"
        else
            log_warning "❌ File missing: $file"
        fi
    done
    
    log_success "Initial verification completed"
}

# 显示下一步指南
show_next_steps() {
    echo ""
    log_success "🎉 Environment setup completed successfully!"
    echo ""
    echo -e "${CYAN}📋 Next Steps:${NC}"
    echo "1. Review and customize your .env file if needed"
    echo "2. Start the development environment:"
    echo "   ./scripts/start_dev.sh"
    echo ""
    echo "3. Alternative Docker-only start:"
    echo "   docker-compose up -d"
    echo ""
    echo "4. Run health checks:"
    echo "   python scripts/health_check.py"
    echo ""
    echo "5. Access the application:"
    echo "   • Backend API: http://localhost:8000"
    echo "   • API Docs: http://localhost:8000/docs"
    echo "   • Frontend: http://localhost:3000"
    echo ""
    echo -e "${YELLOW}💡 Useful commands:${NC}"
    echo "• Database management: python scripts/manage_db.py --help"
    echo "• Reset database: ./scripts/reset_db.sh"
    echo "• View logs: docker-compose logs -f"
    echo "• Stop services: docker-compose down"
    echo ""
    echo -e "${GREEN}Happy coding! 🚀${NC}"
}

# 主函数
main() {
    show_banner
    
    log_info "Starting AI Teaching Assistant System environment setup..."
    echo ""
    
    # 检查参数
    SKIP_DOCKER=false
    SKIP_NODEJS=false
    MINIMAL=false
    
    while [[ $# -gt 0 ]]; do
        case $1 in
            --skip-docker)
                SKIP_DOCKER=true
                shift
                ;;
            --skip-nodejs)
                SKIP_NODEJS=true
                shift
                ;;
            --minimal)
                MINIMAL=true
                shift
                ;;
            -h|--help)
                echo "Usage: $0 [OPTIONS]"
                echo "Options:"
                echo "  --skip-docker    Skip Docker installation"
                echo "  --skip-nodejs    Skip Node.js installation"
                echo "  --minimal        Minimal setup (skip optional components)"
                echo "  -h, --help       Show this help message"
                exit 0
                ;;
            *)
                log_error "Unknown option: $1"
                exit 1
                ;;
        esac
    done
    
    # 执行设置步骤
    detect_os
    install_system_dependencies
    
    if [ "$SKIP_DOCKER" = false ]; then
        install_docker
    fi
    
    setup_python_environment
    
    if [ "$SKIP_NODEJS" = false ] && [ "$MINIMAL" = false ]; then
        install_nodejs
    fi
    
    if [ "$MINIMAL" = false ]; then
        configure_git
    fi
    
    setup_project_environment
    install_project_dependencies
    
    if [ "$MINIMAL" = false ]; then
        setup_development_tools
    fi
    
    run_initial_verification
    show_next_steps
}

# 错误处理
trap 'log_error "Setup failed at line $LINENO"' ERR

# 运行主函数
main "$@"