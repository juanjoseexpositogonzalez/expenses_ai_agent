# Week 6 Implementation: Docker and CI/CD

This implementation lesson guides you through containerizing the expense tracker and setting up automated testing. You will create Docker configuration files and a GitHub Actions workflow, then verify everything works with the provided test suite.


## Learning Goals

By the end of this implementation, you will:

- Create a Dockerfile with multi-stage builds
- Configure docker-compose for the full application stack
- Set up GitHub Actions for automated testing
- Achieve 95%+ test coverage
- Understand production deployment patterns


## What You Are Building

**Input:** Your existing expense tracker application from Weeks 1-5

**Output:** A containerized, CI/CD-enabled application:

```bash
# Single command to run the entire stack
docker-compose up --build

# Automated tests on every commit
# (via GitHub Actions)

# Verified 95%+ test coverage
pytest --cov=src --cov-fail-under=95
```


## What Is Containerization?

Containerization packages your application with all dependencies into a portable unit. The container includes:

- Python runtime (3.12)
- All pip packages (from pyproject.toml)
- Application source code
- Configuration for running the app

Anyone with Docker can run your containerized application without installing Python, dependencies, or configuring their environment. The container provides a consistent runtime everywhere.


## What You Are Creating

This week you will create four new files:

| File | Purpose |
|------|---------|
| `Dockerfile` | Instructions to build the API container |
| `docker-compose.yml` | Orchestration for multi-service deployment |
| `.dockerignore` | Exclude files from container builds |
| `.github/workflows/ci.yml` | GitHub Actions CI pipeline |


## Test Suite

Copy these test files to your `tests/unit/` directory. They define the requirements your implementation must satisfy.

### Test File: test_week6_docker.py

```python
"""
Week 6 - Definition of Done: Docker Configuration

Copy this file to your project's tests/unit/ directory.
Run: pytest tests/unit/test_week6_docker.py -v
All tests must pass to complete Week 6's Docker milestone.

These tests verify the existence and basic structure of:
- Dockerfile
- docker-compose.yml
- .dockerignore
"""

import os
from pathlib import Path

import pytest


# Get project root (assumes tests are in tests/unit/)
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent


class TestDockerfiles:
    """Tests for Docker configuration files."""

    def test_dockerfile_exists(self):
        """Dockerfile should exist in project root."""
        dockerfile = PROJECT_ROOT / "Dockerfile"
        assert dockerfile.exists(), f"Dockerfile not found at {dockerfile}"

    def test_dockerfile_has_python_base(self):
        """Dockerfile should use Python base image."""
        dockerfile = PROJECT_ROOT / "Dockerfile"
        content = dockerfile.read_text()

        assert "FROM python" in content or "FROM python:" in content.lower()

    def test_docker_compose_exists(self):
        """docker-compose.yml should exist."""
        compose_file = PROJECT_ROOT / "docker-compose.yml"
        assert compose_file.exists(), f"docker-compose.yml not found at {compose_file}"

    def test_dockerignore_exists(self):
        """dockerignore should exist to reduce image size."""
        dockerignore = PROJECT_ROOT / ".dockerignore"
        assert dockerignore.exists(), f".dockerignore not found at {dockerignore}"
```

### Test File: test_week6_coverage.py

```python
"""
Week 6 - Definition of Done: Test Coverage Verification

Copy this file to your project's tests/unit/ directory.
Run: pytest tests/unit/test_week6_coverage.py -v
All tests must pass to complete Week 6's coverage milestone.

These tests verify that all major components are importable and testable.
They serve as a checklist for what should be covered by your test suite.
"""

import pytest


class TestImportability:
    """Verify all major components are importable (ensures they exist)."""

    def test_storage_models_importable(self):
        """Storage models should be importable."""
        from expenses_ai_agent.storage.models import (
            Currency,
            Expense,
            ExpenseCategory,
            UserPreference,
        )

        assert Currency is not None
        assert Expense is not None
        assert ExpenseCategory is not None
        assert UserPreference is not None

    def test_storage_repos_importable(self):
        """Storage repositories should be importable."""
        from expenses_ai_agent.storage.repo import (
            CategoryRepository,
            DBCategoryRepo,
            DBExpenseRepo,
            ExpenseRepository,
            InMemoryCategoryRepository,
            InMemoryExpenseRepository,
        )

        assert CategoryRepository is not None
        assert ExpenseRepository is not None
        assert InMemoryCategoryRepository is not None
        assert InMemoryExpenseRepository is not None
        assert DBCategoryRepo is not None
        assert DBExpenseRepo is not None

    def test_llm_components_importable(self):
        """LLM components should be importable."""
        from expenses_ai_agent.llms.base import Assistant, LLMProvider, MESSAGES
        from expenses_ai_agent.llms.openai import OpenAIAssistant
        from expenses_ai_agent.llms.output import ExpenseCategorizationResponse

        assert Assistant is not None
        assert LLMProvider is not None
        assert MESSAGES is not None
        assert OpenAIAssistant is not None
        assert ExpenseCategorizationResponse is not None

    def test_services_importable(self):
        """Services should be importable."""
        from expenses_ai_agent.services.classification import (
            ClassificationResult,
            ClassificationService,
        )
        from expenses_ai_agent.services.preprocessing import (
            InputPreprocessor,
            PreprocessingResult,
        )

        assert ClassificationService is not None
        assert ClassificationResult is not None
        assert InputPreprocessor is not None
        assert PreprocessingResult is not None

    def test_api_components_importable(self):
        """API components should be importable."""
        from expenses_ai_agent.api.main import app
        from expenses_ai_agent.api.deps import get_expense_repo, get_user_id
        from expenses_ai_agent.api.schemas.expense import (
            ExpenseClassifyRequest,
            ExpenseResponse,
        )

        assert app is not None
        assert get_expense_repo is not None
        assert get_user_id is not None
        assert ExpenseClassifyRequest is not None
        assert ExpenseResponse is not None

    def test_telegram_components_importable(self):
        """Telegram components should be importable."""
        from expenses_ai_agent.telegram.bot import ExpenseTelegramBot
        from expenses_ai_agent.telegram.handlers import (
            CurrencyHandler,
            ExpenseConversationHandler,
        )
        from expenses_ai_agent.telegram.keyboards import (
            build_category_confirmation_keyboard,
            build_currency_selection_keyboard,
        )

        assert ExpenseTelegramBot is not None
        assert ExpenseConversationHandler is not None
        assert CurrencyHandler is not None
        assert build_category_confirmation_keyboard is not None
        assert build_currency_selection_keyboard is not None
```


## Implementation Strategy

Work through these steps in order. Each step targets specific functionality.

### Step 1: Create .dockerignore

Create `.dockerignore` in the project root to exclude unnecessary files from Docker builds.

**Target tests:** `test_dockerignore_exists`

The `.dockerignore` file should exclude:
- Version control (`.git`)
- Virtual environments (`.venv`, `venv/`)
- Python cache (`__pycache__`, `*.pyc`)
- IDE files (`.vscode`, `.idea`)
- Local data (`.env`, `*.db`, `.coverage`)
- Documentation (`curriculum/`, `*.md`)
- Test files (if not needed in production image)

Example structure:

```
# Version control
.git
.gitignore

# Virtual environments
.venv
venv/
.python-version

# Python cache
__pycache__
*.pyc
*.pyo
.pytest_cache
.ruff_cache

# IDE files
.vscode
.idea
*.swp

# Local data and secrets
.env
*.db
.coverage

# Documentation
curriculum/
docs/
*.md
!README.md

# Build artifacts
*.egg-info
dist/
build/
```

### Step 2: Create Dockerfile

Create `Dockerfile` in the project root. Use a multi-stage build for efficiency.

**Target tests:** `test_dockerfile_exists`, `test_dockerfile_has_python_base`

The Dockerfile should:
1. Start from `python:3.12-slim` base image
2. Install UV for fast package installation
3. Copy and install dependencies first (for layer caching)
4. Copy application source code
5. Define the command to run the API

Example structure:

```dockerfile
# Stage 1: Builder
FROM python:3.12-slim AS builder

WORKDIR /app

# Install UV package manager
RUN pip install uv

# Copy dependency files first (for caching)
COPY pyproject.toml uv.lock ./

# Install dependencies
RUN uv pip install --system -e .

# Stage 2: Runtime
FROM python:3.12-slim AS runtime

WORKDIR /app

# Copy installed packages from builder
COPY --from=builder /usr/local/lib/python3.12/site-packages \
                    /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy application source
COPY src/ ./src/
COPY pyproject.toml ./

# Create non-root user for security
RUN useradd --create-home appuser
USER appuser

# Expose port
EXPOSE 8000

# Run the application
CMD ["uvicorn", "expenses_ai_agent.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Step 3: Create docker-compose.yml

Create `docker-compose.yml` for orchestrating the full stack.

**Target tests:** `test_docker_compose_exists`

The compose file should:
1. Define an `api` service that builds from the Dockerfile
2. Map port 8000
3. Pass through environment variables
4. Mount a volume for database persistence

Example structure:

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
      - OPENAI_MODEL=${OPENAI_MODEL:-gpt-4o-mini}
      - EXCHANGE_RATE_API_KEY=${EXCHANGE_RATE_API_KEY}
    volumes:
      - ./data:/app/data
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/api/v1/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  # Optional: Streamlit service
  # streamlit:
  #   build:
  #     context: .
  #     dockerfile: Dockerfile.streamlit
  #   ports:
  #     - "8501:8501"
  #   environment:
  #     - API_BASE_URL=http://api:8000/api/v1
  #   depends_on:
  #     - api
```

### Step 4: Create GitHub Actions Workflow

Create `.github/workflows/ci.yml` for automated testing.

This step is optional for the tests but recommended for your project.

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
      - name: Check out repository
        uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.12"

      - name: Install UV
        run: pip install uv

      - name: Install dependencies
        run: uv pip install --system -e ".[dev]"

      - name: Run tests with coverage
        run: pytest --cov=src --cov-report=xml --cov-fail-under=95
        env:
          OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
          EXCHANGE_RATE_API_KEY: ${{ secrets.EXCHANGE_RATE_API_KEY }}

  lint:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.12"

      - name: Install ruff
        run: pip install ruff

      - name: Check formatting
        run: ruff format --check .

      - name: Check linting
        run: ruff check .
```

### Step 5: Increase Test Coverage

Review the coverage report and add tests for uncovered code paths.

**Target tests:** All `test_*_importable` tests verify components exist

Run coverage report:

```bash
pytest --cov=src --cov-report=term-missing
```

Focus on:
- Error handling paths (try/except blocks)
- Edge cases (empty inputs, invalid data)
- Configuration branches (default values)


## Helpful Concepts

### Docker Build Command

Build and tag an image:

```bash
docker build -t expenses-api .
```

[Docker build documentation](https://docs.docker.com/engine/reference/commandline/build/)

### Docker Compose Up

Start all services:

```bash
docker-compose up --build
```

[Docker Compose up documentation](https://docs.docker.com/compose/reference/up/)

### pytest Coverage

Run with coverage and minimum threshold:

```bash
pytest --cov=src --cov-fail-under=95
```

[pytest-cov documentation](https://pytest-cov.readthedocs.io/)


## Validation Checklist

Before moving on, verify:

- [ ] All tests pass: `pytest tests/unit/test_week6_*.py -v`
- [ ] Docker image builds: `docker build -t expenses-api .`
- [ ] Docker Compose config is valid: `docker-compose config`
- [ ] Coverage meets threshold: `pytest --cov=src --cov-fail-under=95`
- [ ] No formatting issues: `ruff format --check .`
- [ ] No linting errors: `ruff check .`


## Debugging Tips

### "COPY failed: file not found"

The file is not in the build context. Check:
1. File exists in project root
2. File is not in `.dockerignore`
3. Path in COPY is relative to context (the `.` in `docker build .`)

### "Module not found" in container

Dependencies not installed properly. Verify:
1. `pyproject.toml` is copied before `RUN pip install`
2. Multi-stage build copies site-packages correctly
3. COPY paths match your project structure

### Coverage below 95%

Run detailed report to find gaps:

```bash
pytest --cov=src --cov-report=term-missing
```

Look at the "Missing" column to identify uncovered lines.

### docker-compose "connection refused"

Services may not be ready. Add healthcheck and depends_on:

```yaml
api:
  healthcheck:
    test: ["CMD", "curl", "-f", "http://localhost:8000/api/v1/health"]

streamlit:
  depends_on:
    api:
      condition: service_healthy
```


## Step Hints

### Step 1: .dockerignore Hint

Think about what should NOT be in your production image:
- Development files (tests, docs, local configs)
- Generated files (cache, coverage, bytecode)
- Secrets (`.env` should never be in an image)

The goal is a minimal image with only what is needed to run the application.


### Step 2: Dockerfile Hint

The key insight for multi-stage builds: the final image only contains what you explicitly COPY into it. The builder stage installs packages, then you copy just the installed packages to the runtime stage.

For the copy command to work with installed packages:
- Python packages go in `/usr/local/lib/python3.12/site-packages`
- Executable scripts go in `/usr/local/bin`


### Step 3: docker-compose.yml Hint

Environment variables with `${VAR}` syntax are read from the host environment or a `.env` file in the same directory. The syntax `${VAR:-default}` provides a fallback if the variable is not set.

Volumes mount host directories into the container. The format is `host_path:container_path`.


### Step 4: GitHub Actions Hint

Secrets must be configured in your GitHub repository settings (Settings > Secrets and variables > Actions). The workflow accesses them with `${{ secrets.SECRET_NAME }}`.

For pytest to skip integration tests that require real API keys, use markers:

```yaml
run: pytest -m "not integration" --cov=src --cov-fail-under=95
```


### Step 5: Coverage Hint

The coverage report shows exactly which lines are not tested. Common gaps:
- Exception handlers (the `except` block)
- Default parameter paths
- Validation rejection branches

Write tests that trigger each uncovered path. Use mocking to simulate errors without calling real APIs.

---

Run the validation checklist and verify everything passes before continuing.
