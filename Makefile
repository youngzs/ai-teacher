# AI Teaching Assistant System - Makefile
# 简化开发任务的 Makefile

.PHONY: help install setup start stop clean test lint format check health reset-db backup-db

# 默认目标
help: ## 显示帮助信息
	@echo "AI Teaching Assistant System - 开发工具"
	@echo "========================================"
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "\033[36m%-15s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)

# 环境设置
setup: ## 设置开发环境
	@echo "🔧 Setting up development environment..."
	@if [ -f "scripts/setup_env.sh" ]; then \
		chmod +x scripts/setup_env.sh && ./scripts/setup_env.sh; \
	else \
		echo "❌ Setup script not found"; \
	fi

install: ## 安装项目依赖
	@echo "📦 Installing dependencies..."
	@python -m pip install --upgrade pip
	@pip install -r requirements.txt -r requirements-dev.txt
	@if [ -d "ai-teacher-frontend" ] && command -v npm >/dev/null 2>&1; then \
		cd ai-teacher-frontend && npm ci; \
	fi

# 开发服务器
start: ## 启动开发环境
	@echo "🚀 Starting development environment..."
	@if [ -f "scripts/start_dev.sh" ]; then \
		chmod +x scripts/start_dev.sh && ./scripts/start_dev.sh; \
	else \
		docker-compose up -d; \
	fi

stop: ## 停止所有服务
	@echo "🛑 Stopping all services..."
	@docker-compose down

restart: ## 重启所有服务
	@echo "🔄 Restarting all services..."
	@docker-compose restart

# 测试和质量检查
test: ## 运行所有测试
	@echo "🧪 Running tests..."
	@pytest tests/ -v --cov=app --cov-report=term-missing

test-fast: ## 运行快速测试（跳过慢测试）
	@echo "⚡ Running fast tests..."
	@pytest tests/ -v -m "not slow" -x

lint: ## 代码检查
	@echo "🔍 Running linting..."
	@flake8 app/ scripts/ tests/
	@mypy app/ --ignore-missing-imports

format: ## 代码格式化
	@echo "✨ Formatting code..."
	@black app/ scripts/ tests/
	@isort app/ scripts/ tests/ --profile=black

check: format lint ## 运行所有代码质量检查
	@echo "✅ Running all quality checks..."
	@bandit -r app/ scripts/ -ll

# 数据库操作
reset-db: ## 重置开发数据库
	@echo "🔄 Resetting development database..."
	@if [ -f "scripts/reset_db.sh" ]; then \
		chmod +x scripts/reset_db.sh && ./scripts/reset_db.sh --env dev; \
	else \
		python scripts/manage_db.py reset --env dev; \
	fi

backup-db: ## 备份开发数据库
	@echo "💾 Creating database backup..."
	@python scripts/manage_db.py backup --env dev

init-db: ## 初始化数据库
	@echo "🗄️ Initializing database..."
	@python scripts/manage_db.py init --env dev

# 健康检查和监控
health: ## 运行系统健康检查
	@echo "🏥 Running health checks..."
	@python scripts/health_check.py

logs: ## 显示服务日志
	@echo "📋 Showing service logs..."
	@docker-compose logs -f --tail=100

status: ## 显示服务状态
	@echo "📊 Service status:"
	@docker-compose ps

# 清理操作
clean: ## 清理临时文件和缓存
	@echo "🧹 Cleaning up..."
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name "*.pyc" -delete 2>/dev/null || true
	@find . -type f -name "*.pyo" -delete 2>/dev/null || true
	@find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	@rm -rf .pytest_cache .mypy_cache .coverage htmlcov/ 2>/dev/null || true
	@if [ -d "ai-teacher-frontend" ]; then \
		cd ai-teacher-frontend && rm -rf node_modules/.cache dist/ 2>/dev/null || true; \
	fi

clean-docker: ## 清理Docker资源
	@echo "🐳 Cleaning Docker resources..."
	@docker-compose down -v
	@docker system prune -f

# 开发工具
shell: ## 进入Python shell
	@echo "🐍 Starting Python shell..."
	@python -i -c "import sys; sys.path.insert(0, '.'); print('Python shell ready!')"

db-shell: ## 进入数据库shell
	@echo "🗄️ Connecting to database..."
	@docker-compose exec database psql -U ai_teacher -d ai_teacher_dev

redis-shell: ## 进入Redis shell
	@echo "⚡ Connecting to Redis..."
	@docker-compose exec redis redis-cli -a dev_redis_123

# 构建和部署
build: ## 构建Docker镜像
	@echo "🔨 Building Docker images..."
	@docker-compose build

build-prod: ## 构建生产环境镜像
	@echo "🏭 Building production images..."
	@docker-compose -f docker-compose.prod.yml build

deploy-dev: ## 部署到开发环境
	@echo "🚀 Deploying to development..."
	@docker-compose -f docker-compose.yml up -d

# 前端操作
frontend-install: ## 安装前端依赖
	@if [ -d "ai-teacher-frontend" ] && command -v npm >/dev/null 2>&1; then \
		echo "📦 Installing frontend dependencies..."; \
		cd ai-teacher-frontend && npm ci; \
	else \
		echo "❌ Frontend directory not found or npm not available"; \
	fi

frontend-dev: ## 启动前端开发服务器
	@if [ -d "ai-teacher-frontend" ] && command -v npm >/dev/null 2>&1; then \
		echo "🎨 Starting frontend dev server..."; \
		cd ai-teacher-frontend && npm run dev; \
	else \
		echo "❌ Frontend directory not found or npm not available"; \
	fi

frontend-build: ## 构建前端
	@if [ -d "ai-teacher-frontend" ] && command -v npm >/dev/null 2>&1; then \
		echo "🔨 Building frontend..."; \
		cd ai-teacher-frontend && npm run build; \
	else \
		echo "❌ Frontend directory not found or npm not available"; \
	fi

# 文档和报告
docs: ## 生成文档
	@echo "📚 Generating documentation..."
	@if command -v mkdocs >/dev/null 2>&1; then \
		mkdocs build; \
	else \
		echo "❌ MkDocs not available. Install with: pip install mkdocs mkdocs-material"; \
	fi

coverage: ## 生成测试覆盖率报告
	@echo "📊 Generating coverage report..."
	@pytest tests/ --cov=app --cov-report=html --cov-report=term
	@echo "📋 Coverage report generated in htmlcov/"

# 安全检查
security: ## 运行安全检查
	@echo "🔒 Running security checks..."
	@bandit -r app/ scripts/ -f json -o bandit-report.json || true
	@bandit -r app/ scripts/ -ll
	@safety check || true

# 性能测试
performance: ## 运行性能测试
	@echo "⚡ Running performance tests..."
	@if [ -f "tests/performance/locustfile.py" ]; then \
		locust --headless --users 10 --spawn-rate 2 --run-time 1m --host http://localhost:8000 -f tests/performance/locustfile.py; \
	else \
		echo "❌ Performance tests not found"; \
	fi

# 版本管理
version: ## 显示当前版本信息
	@echo "📋 Version Information:"
	@echo "Python: $$(python --version)"
	@echo "Docker: $$(docker --version)"
	@echo "Docker Compose: $$(docker-compose --version)"
	@if command -v node >/dev/null 2>&1; then echo "Node.js: $$(node --version)"; fi
	@if command -v npm >/dev/null 2>&1; then echo "npm: $$(npm --version)"; fi

# 全面检查
full-check: clean install format lint test health ## 运行完整的质量检查流程
	@echo "🎉 All checks completed successfully!"

# 快速开始
quickstart: setup start health ## 快速设置并启动开发环境
	@echo ""
	@echo "🎉 Development environment is ready!"
	@echo "📋 Available services:"
	@echo "  • Backend API: http://localhost:8000"
	@echo "  • API Docs: http://localhost:8000/docs"
	@echo "  • Frontend: http://localhost:3000"
	@echo "  • PgAdmin: http://localhost:5050"
	@echo ""
	@echo "💡 Use 'make help' to see all available commands"