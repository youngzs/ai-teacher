# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is the **AI Teaching Assistant System** - a production-ready, AI-powered educational platform designed for university-level programming courses (C and Python). The system uses a multi-agent architecture to provide intelligent code analysis, personalized feedback, and adaptive learning support for students.

## Architecture

### High-Level Structure

```
ai-teacher/
├── app/                    # FastAPI Backend API
│   ├── api/               # REST API endpoints
│   ├── core/              # Configuration and security
│   ├── database/          # SQLAlchemy models and database setup
│   ├── schemas/           # Pydantic request/response schemas
│   ├── services/          # Business logic and AI service integration
│   └── utils/             # Utilities (caching, logging, email)
├── src/                   # AI Multi-Agent System
│   ├── agents/            # AutoGen-based teaching agents
│   ├── analyzers/         # Code analysis tools
│   ├── config/            # Agent configurations
│   ├── models/            # Data models for AI system
│   ├── utils/             # AI utilities
│   └── workflows/         # Teaching workflows
├── ai-teacher-frontend/   # React + TypeScript Frontend
│   ├── src/
│   │   ├── components/    # UI components (ui/, layout/, navigation/)
│   │   ├── pages/         # Page components (auth/, dashboard/, student/, teacher/)
│   │   ├── hooks/         # Custom React hooks
│   │   ├── services/      # API service layer
│   │   ├── store/         # Zustand state management
│   │   └── utils/         # Frontend utilities
│   └── e2e/               # Playwright E2E tests
├── tests/                 # Backend tests (pytest)
├── docs/                  # Documentation
├── scripts/               # Utility scripts
└── .github/workflows/     # CI/CD pipelines
```

### Multi-Agent System

The AI system uses Microsoft's AutoGen framework with specialized agents:

| Agent | Purpose |
|-------|---------|
| **CodeAnalyzer** | Syntax and logic analysis |
| **StudentProfiler** | Learning pattern analysis and personalization |
| **PedagogyExpert** | Teaching methodology and feedback strategies |
| **FeedbackGenerator** | Structured educational feedback generation |
| **QualityController** | Output validation and quality assurance |
| **DebuggingMentor** | Debugging skills instruction |

### Technology Stack

**Backend:**
- Python 3.9+ with FastAPI
- PostgreSQL with SQLAlchemy (async)
- Redis for caching
- AutoGen + OpenAI for AI agents
- uvloop for high-performance async

**Frontend:**
- React 19 with TypeScript
- Vite for build tooling
- Tailwind CSS for styling
- Zustand for state management
- React Router v7 for routing

**Infrastructure:**
- Docker + Docker Compose
- GitHub Actions for CI/CD
- Prometheus for monitoring

## Development Commands

### Quick Start

```bash
# Full setup with Docker
make quickstart

# Or manually:
make setup           # Setup development environment
make install         # Install all dependencies
make start           # Start Docker services
```

### Backend Development

```bash
# Run backend server locally (requires env setup)
python -m uvicorn app.main:app --reload --port 8000

# Or use the provided scripts
python run_backend.py
python run_ai_backend.py       # AI backend with full agent system
```

### Frontend Development

```bash
cd ai-teacher-frontend
npm install         # Install dependencies
npm run dev         # Start dev server (http://localhost:5173)
npm run build       # Production build
npm run preview     # Preview production build
```

### Testing

**Backend Tests:**
```bash
make test           # Run all tests with coverage
make test-fast      # Run fast tests only (skip slow)
pytest tests/ -v    # Run directly

# Specific test markers
pytest -m "unit"           # Unit tests only
pytest -m "integration"    # Integration tests only
pytest -m "api"            # API tests only
```

**Frontend Tests:**
```bash
cd ai-teacher-frontend
npm run test              # Run Vitest tests
npm run test:coverage     # With coverage
npm run test:e2e          # Run Playwright E2E tests
npm run test:e2e:headed   # E2E tests with browser UI
```

### Code Quality

```bash
make lint           # Run all linters (flake8, mypy)
make format         # Auto-format code (black, isort)
make check          # Run format + lint + security checks

# Individual tools
black app/ scripts/ tests/
isort app/ scripts/ tests/ --profile=black
flake8 app/ scripts/ tests/
mypy app/ --ignore-missing-imports
```

### Docker Operations

```bash
make build          # Build Docker images
make start          # Start all services
make stop           # Stop all services
make restart        # Restart services
make logs           # View service logs
make status         # Check service status
make clean-docker   # Clean Docker resources
```

### Database Operations

```bash
make init-db        # Initialize database
make reset-db       # Reset development database
make backup-db      # Create database backup
make db-shell       # Connect to PostgreSQL shell
```

## API Endpoints

The backend API is versioned at `/api/v1/`:

| Endpoint | Purpose |
|----------|---------|
| `/api/v1/auth/*` | Authentication (login, register, tokens) |
| `/api/v1/users/*` | User management |
| `/api/v1/courses/*` | Course and assignment management |
| `/api/v1/submissions/*` | Code submission handling |
| `/api/v1/analysis/*` | AI analysis endpoints |
| `/api/v1/dashboard/*` | Dashboard data |
| `/health` | Health check endpoint |
| `/api/docs` | Swagger UI (dev only) |
| `/api/redoc` | ReDoc (dev only) |

## Database Models

Key entities in `app/database/models.py`:

- **User**: Students, teachers, admins with role-based access
- **Class/ClassMembership**: Class enrollment management
- **Course/Lesson/LearningPath**: Curriculum structure
- **Assignment/Submission**: Assignment and code submission tracking
- **AIFeedback**: AI-generated feedback storage
- **StudentProfile**: Learning analytics and progress tracking
- **TeachingSession**: AI interaction sessions
- **SystemMetrics/AuditLog**: Monitoring and audit trails

## Configuration

### Environment Variables

Copy `.env.example` to `.env` and configure:

```bash
# Core settings
ENVIRONMENT=development       # development, production, testing
DEBUG=true
SECRET_KEY=your-secret-key

# Database
DATABASE_URL=postgresql+asyncpg://user:pass@localhost:5432/ai_teacher_db

# Redis
REDIS_URL=redis://localhost:6379/0

# AI Service
OPENAI_API_KEY=sk-your-key
OPENAI_MODEL=gpt-4
```

### Frontend Configuration

Frontend uses Vite environment variables in `.env`:

```bash
VITE_API_BASE_URL=http://localhost:8000
VITE_AI_API_BASE_URL=http://localhost:8001
```

## Code Conventions

### Python (Backend)

- Follow PEP 8 with Black formatting (88 char line length)
- Use type hints for all function signatures
- Async functions for I/O operations
- SQLAlchemy async patterns for database access
- Pydantic models for request/response validation
- Loguru for logging

### TypeScript (Frontend)

- Functional components with hooks
- Zustand for global state (avoid prop drilling)
- Custom hooks in `src/hooks/` for reusable logic
- Tailwind CSS for styling (use `cn()` utility for conditional classes)
- Proper TypeScript types (avoid `any`)

### Testing

- Backend: pytest with pytest-asyncio, 85% coverage target
- Frontend: Vitest for unit tests, Playwright for E2E
- Use markers for test categorization (`@pytest.mark.slow`, `@pytest.mark.integration`)

## CI/CD Pipeline

GitHub Actions workflows in `.github/workflows/`:

| Workflow | Purpose |
|----------|---------|
| `ci.yml` | Main CI pipeline (lint, test, build) |
| `test-automation.yml` | Comprehensive test automation |
| `performance-monitoring.yml` | Performance benchmarks |
| `release.yml` | Release automation |
| `dependency-update.yml` | Dependency security checks |

## Specialized Agents

This project includes Claude Code agent configurations in `.claude/agents/` for specialized development tasks:

- `backend-architect-developer.md` - Backend system design
- `frontend-developer.md` - Frontend implementation
- `ai-architecture-expert.md` - AI system design
- `devops-infrastructure-engineer.md` - Infrastructure and deployment
- `qa-testing-engineer.md` - Testing strategies
- `ux-ui-designer.md` - User experience design
- `education-expert-advisor.md` - Educational pedagogy guidance
- `product-manager-coordinator.md` - Project coordination

## Key Files Reference

| File | Description |
|------|-------------|
| `app/main.py` | FastAPI application entry point |
| `app/core/config.py` | Application configuration |
| `app/database/models.py` | SQLAlchemy ORM models |
| `app/services/ai_service.py` | AI service integration |
| `src/agents/teaching_agents.py` | Multi-agent system implementation |
| `ai-teacher-frontend/src/App.tsx` | React app entry point |
| `Makefile` | Development task automation |
| `docker-compose.yml` | Docker service orchestration |
| `pyproject.toml` | Python project configuration |

## Development Workflow

1. **Setup**: Run `make quickstart` or follow manual setup
2. **Branch**: Create feature branch from `develop`
3. **Develop**: Make changes with tests
4. **Quality**: Run `make check` before committing
5. **Test**: Ensure `make test` passes
6. **PR**: Open PR to `develop` branch
7. **CI**: Wait for CI pipeline to pass
8. **Merge**: Merge after review

## Troubleshooting

### Common Issues

**Database connection errors:**
```bash
# Ensure PostgreSQL is running
docker-compose up -d database
make health
```

**AI service not responding:**
```bash
# Check OpenAI API key is set
echo $OPENAI_API_KEY
# Verify AI service health
curl http://localhost:8000/health
```

**Frontend API connection issues:**
```bash
# Check CORS settings in backend
# Verify VITE_API_BASE_URL in frontend .env
```

### Useful Commands

```bash
make health         # System health check
make logs           # View all service logs
make status         # Docker service status
make shell          # Python interactive shell
make redis-shell    # Redis CLI
```

## Documentation

Additional documentation in `docs/`:
- `docs/architecture/` - System architecture details
- `docs/requirements/` - Feature requirements
- `docs/education/` - Educational design documents
- `docs/management/` - Project management docs

Key markdown files in root:
- `README.md` - Project introduction
- `DEVELOPMENT_SETUP.md` - Detailed setup guide
- `DOCKER_SETUP.md` - Docker configuration
- `ERROR_HANDLING_GUIDE.md` - Error handling patterns
- `BACKEND_README.md` - Backend-specific documentation
