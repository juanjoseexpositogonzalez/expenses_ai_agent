# Welcome to Week 6: Deploy and Document

You have reached the final week of the Expense AI Agent Cohort. Over the past five weeks, you built a complete AI-powered expense classification system: data models, LLM integration, a CLI, a Telegram bot with human-in-the-loop confirmation, and a full web interface with FastAPI and Streamlit. This week, you will transform your project from a development prototype into a production-ready, deployable application.


## What You Will Learn

Week 6 introduces the operational side of software development:

- **Docker Containerization** - Package your application into portable, reproducible containers
- **Docker Compose** - Orchestrate multiple services (API, Streamlit, database) together
- **CI/CD with GitHub Actions** - Automate testing, linting, and deployment
- **Test Coverage** - Measure and improve your test suite to 95%+ coverage
- **Production Readiness** - Environment configuration, logging, and deployment patterns


## The Mental Model Shift

**Week 5 mindset:** "It works on my machine."

**Week 6 mindset:** "It works everywhere, and I can prove it."

Think of the difference between building a prototype car in your garage versus manufacturing it for customers. The prototype only needs to run for you, with your specific tools and environment. But a production vehicle must start reliably for any customer, in any climate, without you present to tweak it. Docker provides that manufacturing consistency: your application runs identically whether on your laptop, a colleague's machine, or a cloud server in Singapore.


## What Success Looks Like

By the end of this week, your project will be fully containerized and deployable:

```bash
# Build and run the entire stack with one command
docker-compose up --build

# API available at http://localhost:8000
# Streamlit dashboard at http://localhost:8501
# All tests passing in CI/CD pipeline

# Verify high test coverage
pytest --cov=src --cov-fail-under=95
# ==================== 193 passed ====================
# TOTAL COVERAGE: 95%
```


## Why Containerization Matters

Without containers, deploying an application requires recreating your entire development environment on the target machine: the correct Python version, all dependencies with exact versions, system libraries, environment variables, and file permissions. Each deployment becomes a unique snowflake that may break unexpectedly.

Docker solves this by packaging your application with all its dependencies into an immutable image. The same image that passes your tests locally is the exact image that runs in production. No more "works on my machine" bugs.

```dockerfile
# Your application's entire runtime environment defined in code
FROM python:3.12-slim

WORKDIR /app
COPY . .
RUN pip install -e .

CMD ["uvicorn", "expenses_ai_agent.api.main:app", "--host", "0.0.0.0"]
```


## Why CI/CD Matters

Manual testing catches bugs, but only the bugs you remember to test for. Continuous Integration runs your full test suite on every commit, catching regressions before they reach production. Continuous Deployment automates the release process, reducing human error and speeding up delivery.

A well-configured CI/CD pipeline is like having a meticulous quality assurance team that works 24/7, never gets tired, and applies the same rigorous checks to every change.

```yaml
# Every push triggers automated checks
on:
  push:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - run: pytest --cov=src --cov-fail-under=95
      - run: ruff format --check .
      - run: ruff check .
```


## Why 95% Test Coverage Matters

Test coverage is not a vanity metric. It represents the percentage of your code that is exercised by tests. At 50% coverage, half your codebase could contain bugs you would never catch. At 95%, only edge cases slip through.

More importantly, high coverage enables confident refactoring. When you need to change how the classification service works, comprehensive tests verify you did not break existing functionality. Without that safety net, every change becomes a gamble.

```python
# Coverage report shows what is tested
---------- coverage: platform linux, python 3.12 ----------
Name                                    Stmts   Miss  Cover
-----------------------------------------------------------
src/expenses_ai_agent/llms/openai.py      87      4    95%
src/expenses_ai_agent/services/...        54      2    96%
-----------------------------------------------------------
TOTAL                                    1247     62    95%
```


## Technical Milestones

By the end of Week 6, you will have:

- [ ] Created a Dockerfile with multi-stage build for efficient images
- [ ] Configured docker-compose.yml for the full application stack
- [ ] Added .dockerignore to exclude unnecessary files from images
- [ ] Set up GitHub Actions workflow for automated testing and linting
- [ ] Achieved 95%+ test coverage with pytest-cov
- [ ] Verified all components pass the Week 6 definition-of-done tests
- [ ] Prepared your project for production deployment


## Ready?

You have built something substantial over the past five weeks. The architecture is clean, the features work, and the tests are passing. Now it is time to package it properly and ship it.

Let us begin with a brief review of what you built in Week 5, then dive into Docker fundamentals.

Continue to the Week 5 review.
