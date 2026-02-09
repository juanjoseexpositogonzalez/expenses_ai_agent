# Week 6: Deploy + Docs - Docker, CI/CD, and Documentation

Welcome to the final week! This week you will containerize your application with Docker, set up CI/CD with GitHub Actions, and prepare for production deployment. You will also ensure comprehensive documentation and test coverage.

## What You're Building This Week

```
+------------------------------------------------------------------+
|                    WEEK 6: DEPLOYMENT                            |
+------------------------------------------------------------------+

    +-------------------+      +-------------------+
    |   Dockerfile      |      |  docker-compose   |
    |   (multi-stage)   |      |  (full stack)     |
    +-------------------+      +-------------------+
              |                          |
              v                          v
    +-------------------+      +-------------------+
    |  Docker Image     |      | API + Streamlit   |
    |  - Python 3.12    |      | + SQLite Volume   |
    |  - UV packages    |      +-------------------+
    +-------------------+
              |
              v
    +-------------------+      +-------------------+
    | GitHub Actions    |      |    Fly.io         |
    | - Tests           | ---> |    Deployment     |
    | - Lint            |      |    (optional)     |
    | - Coverage        |      +-------------------+
    +-------------------+

    +-------------------+
    |   Documentation   |
    |   - README.md     |
    |   - API docs      |
    |   - Examples      |
    +-------------------+
```

## Learning Objectives

By the end of this week, you will:

- Create efficient Docker images with multi-stage builds
- Configure docker-compose for local development
- Set up GitHub Actions for CI/CD
- Achieve high test coverage (95%+)
- Write comprehensive documentation
- Understand production deployment considerations


## Week 6 Checklist

### Technical Milestones

- [ ] Create Dockerfile with multi-stage build
- [ ] Configure docker-compose for full stack
- [ ] Set up GitHub Actions workflow for tests and lint
- [ ] Achieve 95%+ test coverage
- [ ] Add missing tests for edge cases
- [ ] Create comprehensive README.md
- [ ] Add usage examples
- [ ] Pass all provided tests

### Deployment Files

- [ ] Dockerfile
- [ ] docker-compose.yml
- [ ] .dockerignore
- [ ] .github/workflows/ci.yml
- [ ] fly.toml (optional, for Fly.io)


## Key Concepts This Week

### 1. Multi-Stage Docker Build

```dockerfile
# Stage 1: Build dependencies
FROM python:3.12-slim as builder

WORKDIR /app
RUN pip install uv

COPY pyproject.toml uv.lock ./
RUN uv pip install --system -e .

# Stage 2: Runtime image
FROM python:3.12-slim as runtime

WORKDIR /app
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY src/ ./src/

# Run the application
CMD ["uvicorn", "expenses_ai_agent.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

Benefits:
- Smaller final image (no build tools)
- Cached dependency layers
- Faster rebuilds

### 2. Docker Compose for Development

```yaml
version: "3.8"

services:
  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=sqlite:///data/expenses.db
      - OPENAI_API_KEY=${OPENAI_API_KEY}
    volumes:
      - ./data:/app/data

  streamlit:
    build:
      context: .
      dockerfile: Dockerfile.streamlit
    ports:
      - "8501:8501"
    environment:
      - API_BASE_URL=http://api:8000/api/v1
    depends_on:
      - api
```

### 3. GitHub Actions CI/CD

```yaml
name: CI

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.12"

      - name: Install dependencies
        run: |
          pip install uv
          uv pip install --system -e ".[dev]"

      - name: Run tests
        run: pytest --cov=src --cov-fail-under=95

      - name: Lint
        run: |
          ruff format --check .
          ruff check .
```

### 4. Test Coverage Strategy

To achieve 95%+ coverage:

1. **Unit tests** for all business logic
2. **Integration tests** for API endpoints
3. **Edge case tests** for error handling
4. **Mock external services** (OpenAI, Telegram)

```python
# Example: Testing error paths
def test_classify_with_api_error(test_client, mock_service):
    mock_service.classify.side_effect = Exception("API Error")

    response = test_client.post(
        "/api/v1/expenses/classify",
        json={"description": "Test"},
    )

    assert response.status_code == 500
```


## Project Structure After Week 6

```
expenses_ai_agent/
+-- .github/
|   +-- workflows/
|       +-- ci.yml              # GitHub Actions
+-- src/
|   +-- expenses_ai_agent/      # All application code
+-- tests/
|   +-- unit/                   # Unit tests
|   +-- integration/            # Integration tests
+-- curriculum/                 # This curriculum!
+-- Dockerfile                  # API container
+-- Dockerfile.bot              # Telegram bot container (optional)
+-- docker-compose.yml          # Full stack
+-- .dockerignore               # Docker ignore rules
+-- fly.toml                    # Fly.io config (optional)
+-- fly.bot.toml               # Fly.io bot config (optional)
+-- pyproject.toml
+-- README.md                   # Comprehensive docs
+-- .env.example                # Environment template
```


## Build Guide

### Step 1: Dockerfile

Create an efficient Dockerfile:
- Use Python 3.12-slim base
- Use UV for package installation
- Multi-stage build to reduce size
- Non-root user for security

### Step 2: docker-compose.yml

Configure services:
- API service (FastAPI)
- Optional Streamlit service
- Volume for SQLite database
- Environment variable pass-through

### Step 3: .dockerignore

Exclude unnecessary files:
```
.git
.venv
__pycache__
*.pyc
.pytest_cache
.coverage
*.db
.env
curriculum/
```

### Step 4: GitHub Actions

Create `.github/workflows/ci.yml`:
- Trigger on push/PR to main
- Set up Python 3.12
- Install dependencies
- Run tests with coverage
- Run linting (ruff)
- Fail if coverage < 95%

### Step 5: Increase Test Coverage

Add tests for:
- Error handling paths
- Edge cases
- All API endpoints
- Streamlit views
- Utility functions

### Step 6: Documentation

Update README.md:
- Project overview
- Installation instructions
- Usage examples (CLI, API, Telegram)
- Configuration options
- Development setup
- Deployment guide


## Definition of Done

### Tests to Pass

Copy the test files from `curriculum/week6/tests/` into your `tests/unit/` directory:

- `test_week6_docker.py` (4 tests)
- `test_week6_coverage.py` (6 tests)

### Commands - All Must Succeed

| Command | Expected Result |
|---------|-----------------|
| `pytest tests/unit/test_week6_*.py -v` | All 10 tests pass |
| `pytest --cov=src --cov-fail-under=95` | Coverage >= 95% |
| `docker build -t expenses-api .` | Image builds successfully |
| `docker-compose config` | Config is valid |
| `ruff format --check .` | No formatting issues |
| `ruff check .` | No linting errors |

### You Are Done When

- All tests pass (green)
- Test coverage >= 95%
- Docker image builds
- docker-compose works
- README is comprehensive
- GitHub Actions passes


## Running with Docker

```bash
# Build and run with docker-compose
docker-compose up --build

# Or build individually
docker build -t expenses-api .
docker run -p 8000:8000 -e OPENAI_API_KEY=$OPENAI_API_KEY expenses-api
```


## Deployment Options

### Option 1: Fly.io (Recommended)

```bash
# Install flyctl
curl -L https://fly.io/install.sh | sh

# Deploy
fly launch
fly secrets set OPENAI_API_KEY=$OPENAI_API_KEY
fly deploy
```

### Option 2: Railway

```bash
# Connect to Railway and deploy
railway login
railway init
railway up
```

### Option 3: Self-hosted

```bash
# On your server
docker-compose up -d
```


## Common Issues and Solutions

| Issue | Solution |
|-------|----------|
| Docker build fails | Check .dockerignore, ensure all files present |
| Coverage too low | Add tests for error paths and edge cases |
| GitHub Actions fails | Check Python version and dependencies |
| Fly.io secrets | Use `fly secrets set KEY=value` |
| Database persistence | Use volumes in docker-compose |


## Course Completion Checklist

Congratulations on reaching Week 6! Verify you have completed:

- [ ] Week 1: Data models and in-memory repositories
- [ ] Week 2: LLM Protocol and OpenAI client
- [ ] Week 3: Classification service and CLI
- [ ] Week 4: Telegram bot with HITL
- [ ] Week 5: FastAPI + Streamlit web interface
- [ ] Week 6: Docker, CI/CD, and deployment

### Skills Acquired

By completing this curriculum, you now have experience with:

**Python Patterns**
- Protocol-based design (structural typing)
- Repository pattern for data access
- Service layer for business logic
- Dependency injection
- Async/await programming

**AI/ML Integration**
- LLM API integration (OpenAI)
- Prompt engineering for classification
- Structured outputs with Pydantic
- Human-in-the-loop (HITL) patterns
- Tool/function calling

**Web Development**
- FastAPI REST APIs
- Streamlit dashboards
- Telegram bots
- CLI with Typer

**DevOps**
- Docker containerization
- GitHub Actions CI/CD
- Test-driven development
- High test coverage

---

**Final tip**: Your expense AI agent is now production-ready. Deploy it, use it, and extend it. Consider adding features like:
- Budget alerts
- Receipt image parsing (OCR)
- Natural language queries
- Export to spreadsheets
- Multiple LLM providers (Groq, Anthropic)

Congratulations on completing the Expense AI Agent Cohort!
