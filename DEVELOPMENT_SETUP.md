# AI Teaching Assistant System - 开发环境设置指南

## 🚀 快速开始

### 1. 自动化环境设置（推荐）

使用我们提供的自动化脚本来设置完整的开发环境：

**Linux/macOS:**
```bash
# 克隆项目
git clone <repository-url>
cd ai-teacher

# 运行环境设置脚本
chmod +x scripts/setup_env.sh
./scripts/setup_env.sh

# 启动开发环境
./scripts/start_dev.sh
```

**Windows:**
```cmd
# 克隆项目
git clone <repository-url>
cd ai-teacher

# 运行环境设置脚本
scripts\setup_env.bat

# 启动开发环境
scripts\start_dev.bat
```

### 2. 手动设置

如果您偏好手动设置或自动化脚本遇到问题，请按照以下步骤操作：

## 📋 系统要求

### 必需组件
- **Python 3.9+** (推荐 3.11)
- **Docker Desktop** (包含 Docker Compose)
- **Git**

### 可选组件
- **Node.js 16+** (用于前端开发)
- **VS Code** (推荐的IDE)
- **PostgreSQL客户端** (用于直接数据库操作)

## 🛠️ 详细安装步骤

### 步骤 1: 系统依赖安装

#### Ubuntu/Debian:
```bash
sudo apt update
sudo apt install -y python3 python3-pip python3-venv git curl wget
```

#### macOS (使用 Homebrew):
```bash
brew install python git curl wget
```

#### Windows:
- 从官网下载并安装 Python 3.11
- 安装 Git for Windows
- 安装 Docker Desktop

### 步骤 2: Docker 安装

#### Linux:
```bash
# 安装 Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# 安装 Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# 重新登录以应用用户组变更
```

#### macOS/Windows:
从 [Docker官网](https://www.docker.com/products/docker-desktop) 下载并安装 Docker Desktop

### 步骤 3: 项目设置

```bash
# 克隆项目
git clone <repository-url>
cd ai-teacher

# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
# Linux/macOS:
source venv/bin/activate
# Windows:
# venv\Scripts\activate

# 升级 pip
pip install --upgrade pip

# 安装依赖
pip install -r requirements.txt
pip install -r requirements-dev.txt

# 创建环境配置文件
cp .env.example .env
```

### 步骤 4: 环境配置

编辑 `.env` 文件，设置必要的配置：

```env
# 数据库配置
DATABASE_URL=postgresql+asyncpg://ai_teacher:dev_password_123@localhost:5432/ai_teacher_dev

# Redis配置
REDIS_URL=redis://:dev_redis_123@localhost:6379/0

# 应用配置
SECRET_KEY=your-generated-secret-key
DEBUG=true
ENVIRONMENT=development

# AI服务配置（可选）
OPENAI_API_KEY=your-openai-api-key
```

### 步骤 5: 启动服务

```bash
# 启动数据库和缓存服务
docker-compose up -d database redis

# 等待服务启动
sleep 10

# 初始化数据库
python scripts/manage_db.py init --env dev

# 启动后端服务
docker-compose up -d backend

# 启动前端服务（如果有Node.js）
cd ai-teacher-frontend
npm ci
npm run dev
```

## 🔧 开发工具配置

### VS Code 设置

项目已包含完整的 VS Code 配置：

- **自动代码格式化** (Black, Prettier)
- **代码检查** (Flake8, ESLint, MyPy)
- **测试支持** (PyTest)
- **调试配置**
- **推荐扩展**

打开项目时，VS Code 会提示安装推荐的扩展。

### Pre-commit Hooks

安装代码质量检查钩子：

```bash
# 激活虚拟环境
source venv/bin/activate

# 安装 pre-commit hooks
pre-commit install

# 运行所有文件检查（首次）
pre-commit run --all-files
```

## 📊 验证安装

### 健康检查

运行系统健康检查：

```bash
python scripts/health_check.py
```

### 运行测试

```bash
# 运行所有测试
pytest

# 运行带覆盖率的测试
pytest --cov=app --cov-report=html

# 运行特定测试
pytest tests/test_api.py -v
```

### 访问服务

安装完成后，您可以访问：

- **后端API**: http://localhost:8000
- **API文档**: http://localhost:8000/docs
- **前端应用**: http://localhost:3000
- **数据库管理**: http://localhost:5050 (admin@aiteacher.local / admin123)
- **Redis管理**: http://localhost:8081 (admin / admin123)

## 🐛 常见问题

### Docker 问题

**问题**: Docker 权限被拒绝
```bash
# Linux 解决方案
sudo usermod -aG docker $USER
# 然后重新登录
```

**问题**: Docker Compose 命令不存在
```bash
# 检查安装
docker-compose --version

# 如果不存在，重新安装
pip install docker-compose
```

### Python 问题

**问题**: Python 版本不兼容
```bash
# 检查 Python 版本
python --version

# 如果版本过低，安装新版本或使用 pyenv
pyenv install 3.11.0
pyenv local 3.11.0
```

**问题**: 虚拟环境问题
```bash
# 删除并重新创建虚拟环境
rm -rf venv
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt -r requirements-dev.txt
```

### 数据库连接问题

**问题**: 无法连接到数据库
```bash
# 检查容器状态
docker-compose ps

# 查看数据库日志
docker-compose logs database

# 重启数据库服务
docker-compose restart database

# 检查连接
python scripts/manage_db.py check --env dev
```

### 端口冲突

如果默认端口被占用，修改 `docker-compose.yml` 中的端口映射：

```yaml
ports:
  - "8001:8000"  # 将后端端口改为8001
  - "3001:3000"  # 将前端端口改为3001
```

## 📝 开发工作流

### 日常开发

1. **启动开发环境**:
   ```bash
   ./scripts/start_dev.sh
   ```

2. **运行测试**:
   ```bash
   pytest tests/ -v
   ```

3. **代码格式化**:
   ```bash
   black app/ scripts/ tests/
   isort app/ scripts/ tests/
   ```

4. **代码检查**:
   ```bash
   flake8 app/ scripts/ tests/
   mypy app/
   ```

### 数据库操作

```bash
# 重置数据库
./scripts/reset_db.sh

# 查看数据库信息
python scripts/manage_db.py info --env dev

# 创建数据库备份
python scripts/manage_db.py backup --env dev
```

### 容器管理

```bash
# 查看服务状态
docker-compose ps

# 查看日志
docker-compose logs -f [service_name]

# 重启服务
docker-compose restart [service_name]

# 停止所有服务
docker-compose down
```

## 🔒 安全注意事项

1. **永远不要提交 .env 文件到版本控制**
2. **使用强密码和密钥**
3. **定期更新依赖包**
4. **运行安全检查**:
   ```bash
   bandit -r app/ -ll
   safety check
   ```

## 📚 更多资源

- [FastAPI 文档](https://fastapi.tiangolo.com/)
- [React 文档](https://reactjs.org/docs/)
- [Docker 文档](https://docs.docker.com/)
- [PostgreSQL 文档](https://www.postgresql.org/docs/)
- [Redis 文档](https://redis.io/documentation)

## 🆘 获取帮助

如果您遇到问题：

1. 检查这个文档的常见问题部分
2. 运行健康检查: `python scripts/health_check.py`
3. 查看日志: `docker-compose logs`
4. 在项目仓库中创建 Issue
5. 联系开发团队

---

**祝您开发愉快！** 🚀