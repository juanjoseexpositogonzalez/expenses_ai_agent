# Week 6 Success Criteria

This document defines the requirements for completing Week 6. Verify each criterion before considering the week complete.


## Definition of Done

Week 6 is complete when all of the following criteria are satisfied.


## Tests to Pass

Copy the test files from `curriculum/week6/tests/` into your `tests/unit/` directory:

- `test_week6_docker.py` (4 tests)
- `test_week6_coverage.py` (6 tests)

Run them to verify your implementation:

```bash
pytest tests/unit/test_week6_docker.py -v
pytest tests/unit/test_week6_coverage.py -v
```


## Required Files

| File | Purpose | Validation |
|------|---------|------------|
| `Dockerfile` | Container build instructions | `docker build -t expenses-api .` |
| `docker-compose.yml` | Multi-service orchestration | `docker-compose config` |
| `.dockerignore` | Exclude files from builds | File exists and contains exclusions |


## Command Validation

All commands must succeed. Run each one and verify the expected outcome.

### Test Suite

```bash
pytest tests/unit/test_week6_*.py -v
```

**Expected:** All 10 tests pass (green).

### Test Coverage

```bash
pytest --cov=src --cov-fail-under=95
```

**Expected:** Exit code 0, coverage report shows 95%+ overall.

### Docker Build

```bash
docker build -t expenses-api .
```

**Expected:** Image builds successfully, final message shows image name.

### Docker Compose Configuration

```bash
docker-compose config
```

**Expected:** Valid YAML output, no errors.

### Code Formatting

```bash
ruff format --check .
```

**Expected:** No files would be reformatted.

### Code Linting

```bash
ruff check .
```

**Expected:** No linting errors.


## Running the Full Stack

Verify the containerized application works:

```bash
# Start services
docker-compose up --build

# In another terminal, test the API
curl http://localhost:8000/api/v1/health
```

**Expected:** Health endpoint returns `{"status": "healthy"}`.


## Coverage Report Review

Generate a detailed coverage report:

```bash
pytest --cov=src --cov-report=term-missing --cov-report=html
```

Open `htmlcov/index.html` in a browser to review coverage visually.

Key areas that should have high coverage:
- `src/expenses_ai_agent/storage/` - 95%+
- `src/expenses_ai_agent/services/` - 95%+
- `src/expenses_ai_agent/llms/` - 95%+
- `src/expenses_ai_agent/api/` - 95%+
- `src/expenses_ai_agent/telegram/` - 95%+


## Week 6 Checklist

### Docker Configuration

- [ ] `Dockerfile` exists and uses Python 3.12 base image
- [ ] `docker-compose.yml` exists and is valid
- [ ] `.dockerignore` exists and excludes development files
- [ ] Docker image builds without errors
- [ ] Container runs and responds to health checks

### CI/CD Pipeline (Optional but Recommended)

- [ ] `.github/workflows/ci.yml` exists
- [ ] Workflow runs tests on push
- [ ] Workflow runs linting on push
- [ ] Coverage threshold enforced in CI

### Test Coverage

- [ ] Overall coverage is 95% or higher
- [ ] All major components are tested
- [ ] Error handling paths are covered
- [ ] Edge cases are covered

### Code Quality

- [ ] No ruff formatting issues
- [ ] No ruff linting errors
- [ ] All imports work correctly


## Verification Script

Run this comprehensive verification:

```bash
#!/bin/bash
set -e

echo "=== Week 6 Verification ==="

echo "1. Checking required files..."
test -f Dockerfile && echo "   Dockerfile: OK" || echo "   Dockerfile: MISSING"
test -f docker-compose.yml && echo "   docker-compose.yml: OK" || echo "   docker-compose.yml: MISSING"
test -f .dockerignore && echo "   .dockerignore: OK" || echo "   .dockerignore: MISSING"

echo "2. Running Week 6 tests..."
pytest tests/unit/test_week6_*.py -v

echo "3. Checking test coverage..."
pytest --cov=src --cov-fail-under=95 -q

echo "4. Building Docker image..."
docker build -t expenses-api . -q

echo "5. Validating docker-compose..."
docker-compose config > /dev/null

echo "6. Checking code formatting..."
ruff format --check .

echo "7. Checking linting..."
ruff check .

echo "=== All checks passed! ==="
```

Save as `scripts/verify_week6.sh` and run with `bash scripts/verify_week6.sh`.


## Troubleshooting

### Tests Fail: "Dockerfile not found"

Ensure Dockerfile is in the project root, not in a subdirectory.

```bash
ls -la Dockerfile
```

### Coverage Below 95%

Run detailed report to find gaps:

```bash
pytest --cov=src --cov-report=term-missing | grep -E "^\w.*Miss"
```

Add tests for the uncovered lines.

### Docker Build Fails

Check the error message. Common issues:

| Error | Solution |
|-------|----------|
| "COPY failed: file not found" | Check file exists and not in .dockerignore |
| "pip install failed" | Verify pyproject.toml is valid |
| "Permission denied" | Check file permissions, use non-root user correctly |

### docker-compose Errors

Validate YAML syntax:

```bash
python -c "import yaml; yaml.safe_load(open('docker-compose.yml'))"
```


## What You Have Accomplished

By completing Week 6, you have:

1. **Containerized the application** - Portable, reproducible deployment
2. **Orchestrated multiple services** - API and database work together
3. **Automated quality checks** - Tests and linting run on every commit
4. **Achieved high test coverage** - Confidence in code correctness
5. **Prepared for production** - Ready to deploy anywhere

Your expense tracker is now production-ready.


## Next Steps

With Week 6 complete, you can:

1. Deploy to a cloud platform (Fly.io, Railway, AWS)
2. Add the optional Streamlit container
3. Set up production monitoring
4. Extend with new features

Continue to the Capstone Project ideas for inspiration.
