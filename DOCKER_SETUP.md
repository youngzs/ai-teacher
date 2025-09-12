# AI教学助手系统 - Docker开发环境设置指南

本指南介绍如何使用Docker快速搭建AI教学助手系统的开发环境。

## 📋 前提条件

### 必需软件
- **Docker** (版本 20.10+) - [安装指南](https://docs.docker.com/get-docker/)
- **Docker Compose** (版本 2.0+) - [安装指南](https://docs.docker.com/compose/install/)

### 系统要求
- **内存**: 4GB+ RAM（推荐8GB+）
- **存储**: 10GB+ 可用磁盘空间
- **操作系统**: Linux, macOS, Windows (with WSL2)

## 🚀 快速启动

### 1. 克隆项目
```bash
git clone <repository-url>
cd ai-teacher
```

### 2. 配置环境变量
```bash
# 复制并编辑环境变量文件
cp .env.docker .env.local  # 可选：创建本地配置

# 编辑.env.docker文件，设置OpenAI API密钥
nano .env.docker
```

在`.env.docker`文件中设置：
```bash
OPENAI_API_KEY=sk-your-openai-api-key-here
```

### 3. 一键启动
```bash
# 启动所有服务
./start_docker.sh

# 或者启动并包含管理工具
./start_docker.sh --with-tools

# 或者清理后重新启动
./start_docker.sh --clean-start
```

### 4. 访问服务
启动完成后，您可以访问：

- **🌐 前端应用**: http://localhost:3001
- **🔧 后端API**: http://localhost:8000 (API文档: `/docs`)
- **🤖 AI后端**: http://localhost:8001 (API文档: `/docs`)
- **🔍 PgAdmin** (可选): http://localhost:5050

## 📂 系统架构

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   前端 (React)  │    │  后端API        │    │  AI后端         │
│   端口: 3001    │────│  端口: 8000     │────│  端口: 8001     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │                       │
                       ┌────────┴────────┐    ┌────────┴────────┐
                       │  PostgreSQL     │    │     Redis       │
                       │  端口: 5432     │    │   端口: 6379    │
                       └─────────────────┘    └─────────────────┘
```

## 🛠 开发工具

### 启动管理工具
```bash
./start_docker.sh --with-tools
```

包含的管理工具：
- **PgAdmin** (http://localhost:5050) - 数据库管理
  - 邮箱: admin@aiteacher.local
  - 密码: admin123
- **Redis Commander** (http://localhost:8081) - Redis管理

### 启动监控服务
```bash
./start_docker.sh --with-monitoring
```

包含的监控工具：
- **Prometheus** (http://localhost:9090) - 指标收集
- **Grafana** (http://localhost:3001) - 监控面板

## 📊 服务管理

### 查看服务状态
```bash
# 检查所有服务状态
docker-compose ps

# 查看特定服务日志
docker-compose logs -f backend
docker-compose logs -f ai-backend
docker-compose logs -f frontend

# 实时查看所有服务日志
docker-compose logs -f
```

### 重启服务
```bash
# 重启特定服务
docker-compose restart backend

# 重启所有服务
docker-compose restart
```

### 停止服务
```bash
# 停止服务（保留数据）
./stop_docker.sh

# 停止并删除容器
./stop_docker.sh --remove-containers

# 停止并删除容器和数据卷
./stop_docker.sh --remove-volumes
```

## 🔍 健康检查

运行完整的环境健康检查：
```bash
./health_check.sh
```

快速检查：
```bash
./health_check.sh --quick
```

只检查服务状态：
```bash
./health_check.sh --services-only
```

## 💾 数据库管理

### 数据库备份
```bash
# 完整备份
./scripts/backup_database.sh

# 只备份模式（结构）
./scripts/backup_database.sh --schema-only
```

### 数据库恢复
```bash
# 列出可用备份
./scripts/restore_database.sh --list

# 恢复指定备份
./scripts/restore_database.sh backup_20231201_120000.sql.gz

# 查看数据库状态
./scripts/restore_database.sh --status
```

## 🐛 故障排除

### 常见问题

#### 1. 端口冲突
如果遇到端口被占用错误：
```bash
# 查看端口使用情况
netstat -tuln | grep -E ":(3001|8000|8001|5432|6379)"

# 或使用ss命令
ss -tuln | grep -E ":(3001|8000|8001|5432|6379)"

# 停止占用端口的服务或修改docker-compose.yml中的端口映射
```

#### 2. Docker容器启动失败
```bash
# 查看失败容器的日志
docker-compose logs 服务名

# 重新构建镜像
docker-compose build --no-cache 服务名

# 清理后重新启动
./start_docker.sh --clean-start
```

#### 3. 数据库连接问题
```bash
# 检查数据库容器状态
docker-compose ps database

# 查看数据库日志
docker-compose logs database

# 手动测试数据库连接
docker exec -it ai-teacher-db psql -U ai_teacher -d ai_teacher_dev
```

#### 4. 前端构建失败
```bash
# 清理前端构建缓存
docker-compose exec frontend rm -rf node_modules/.cache

# 重新安装依赖
docker-compose exec frontend npm install

# 重新构建
docker-compose build frontend
```

#### 5. AI后端API密钥错误
确保在`.env.docker`文件中正确设置了OpenAI API密钥：
```bash
OPENAI_API_KEY=sk-your-actual-api-key-here
```

### 日志分析

#### 查看实时日志
```bash
# 所有服务
docker-compose logs -f

# 特定服务
docker-compose logs -f backend ai-backend

# 最近100行日志
docker-compose logs --tail=100 backend
```

#### 日志存储位置
- 应用日志: `./logs/`
- 上传文件: `./uploads/`
- 数据库数据: Docker卷 `ai-teacher_postgres_data`

## 🔧 高级配置

### 环境变量定制

创建本地环境文件：
```bash
cp .env.docker .env.local
```

在`.env.local`中覆盖特定配置：
```bash
# 开发模式配置
DEBUG=true
LOG_LEVEL=DEBUG

# 自定义端口
FRONTEND_PORT=3002
BACKEND_PORT=8002

# 自定义数据库配置
POSTGRES_DB=ai_teacher_custom
POSTGRES_PASSWORD=your_secure_password
```

使用自定义配置启动：
```bash
docker-compose --env-file .env.local up -d
```

### 性能优化

#### 增加资源限制
在`docker-compose.yml`中为服务添加资源限制：
```yaml
services:
  backend:
    # ... 其他配置
    deploy:
      resources:
        limits:
          cpus: '2.0'
          memory: 2G
        reservations:
          memory: 1G
```

#### 启用缓存
```yaml
services:
  frontend:
    # ... 其他配置
    volumes:
      - ./ai-teacher-frontend:/app
      - node_modules_cache:/app/node_modules  # 缓存node_modules
```

### 开发环境vs生产环境

#### 开发环境特性
- 热重载
- 源码映射
- 详细日志
- 开发工具暴露

#### 切换到生产模式
```bash
# 使用生产配置
docker-compose -f docker-compose.prod.yml up -d

# 或设置环境变量
export NODE_ENV=production
export ENVIRONMENT=production
./start_docker.sh
```

## 📚 开发指南

### 代码修改流程
1. 修改源代码
2. 容器会自动重载（开发模式）
3. 访问相应服务验证更改

### 添加新的Python依赖
```bash
# 进入后端容器
docker-compose exec backend bash

# 安装新依赖
pip install new-package

# 更新requirements.txt
pip freeze > requirements.txt

# 重新构建镜像以持久化更改
docker-compose build backend
```

### 添加新的Node.js依赖
```bash
# 进入前端容器
docker-compose exec frontend bash

# 安装新依赖
npm install new-package

# 退出容器后重新构建
docker-compose build frontend
```

### 数据库迁移
```bash
# 进入后端容器
docker-compose exec backend python manage.py makemigrations
docker-compose exec backend python manage.py migrate
```

## 🔒 安全注意事项

### 开发环境安全
- 默认密码仅用于开发环境
- 不要在生产环境中使用相同的密钥和密码
- OpenAI API密钥应该妥善保管

### 生产部署前检查
- [ ] 更改所有默认密码
- [ ] 生成新的JWT密钥
- [ ] 配置HTTPS
- [ ] 设置防火墙规则
- [ ] 启用日志轮转
- [ ] 配置备份策略

## 📞 支持与帮助

### 获取帮助
```bash
# 查看脚本帮助
./start_docker.sh --help
./stop_docker.sh --help
./health_check.sh --help

# 查看Docker Compose配置
docker-compose config
```

### 常用命令速查
```bash
# 启动开发环境
./start_docker.sh

# 健康检查
./health_check.sh

# 查看日志
docker-compose logs -f

# 停止服务
./stop_docker.sh

# 进入容器Shell
docker-compose exec backend bash
docker-compose exec frontend bash

# 数据库操作
./scripts/backup_database.sh
./scripts/restore_database.sh --list
```

### 项目结构
```
ai-teacher/
├── docker-compose.yml          # Docker编排配置
├── .env.docker                 # Docker环境变量
├── Dockerfile                  # 后端镜像构建文件
├── start_docker.sh             # 一键启动脚本
├── stop_docker.sh              # 停止脚本
├── health_check.sh             # 健康检查脚本
├── ai-teacher-frontend/        # 前端代码
│   └── Dockerfile              # 前端镜像构建文件
├── app/                        # 后端应用代码
├── src/                        # AI系统核心代码
├── scripts/                    # 数据库管理脚本
│   ├── backup_database.sh      # 数据库备份
│   ├── restore_database.sh     # 数据库恢复
│   └── init-db.sql            # 数据库初始化
└── logs/                      # 应用日志目录
```

---

**提示**: 如果您是第一次使用Docker，建议先阅读[Docker官方文档](https://docs.docker.com/get-started/)了解基本概念。