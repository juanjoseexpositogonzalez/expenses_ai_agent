# CI/CD Pipelines with GitHub Actions

Continuous Integration (CI) and Continuous Deployment (CD) automate the testing, building, and deployment of your application. GitHub Actions provides this functionality directly in your repository.


## Why CI/CD Exists

Without automation, every code change requires manual testing:

1. Developer makes changes locally
2. Runs tests manually (maybe, sometimes)
3. Pushes to repository
4. Another developer pulls, finds tests fail
5. Investigation, hotfix, repeat

This manual process has failure modes:
- Developers forget to run tests
- "It works on my machine" environment differences
- Integration issues discovered late
- Deployments vary based on who performs them

CI/CD eliminates these problems by running the same checks automatically on every commit.


## What CI/CD Achieves

**Continuous Integration:**
- Runs tests on every push and pull request
- Catches regressions immediately
- Ensures code formatting and linting standards
- Prevents broken code from reaching main branch

**Continuous Deployment:**
- Automatically deploys passing builds
- Eliminates manual deployment steps
- Creates audit trail of all deployments
- Enables rapid iteration

```
+--------+    +--------+    +--------+    +--------+
|  Push  | -> |  Test  | -> | Build  | -> | Deploy |
| commit |    | & Lint |    | Image  |    | to Prod|
+--------+    +--------+    +--------+    +--------+
                  |
                  | Fail? Stop here
                  v
             [Notify developer]
```


## GitHub Actions Concepts

### Workflows

A **workflow** is an automated process defined in a YAML file. Workflows live in `.github/workflows/` and run in response to events.

### Events

**Events** trigger workflows:
- `push`: Code pushed to repository
- `pull_request`: PR opened, updated, or merged
- `schedule`: Cron-based scheduling
- `workflow_dispatch`: Manual trigger from GitHub UI

### Jobs

**Jobs** are units of work that run on a virtual machine. Jobs can run in parallel or sequentially.

### Steps

**Steps** are individual commands or actions within a job. Steps run sequentially.

### Actions

**Actions** are reusable units of code. The community provides thousands of actions for common tasks.


## Basic Workflow Structure

```yaml
name: CI  # Workflow name

on:  # Events that trigger this workflow
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  test:  # Job name
    runs-on: ubuntu-latest  # Virtual machine to use

    steps:
      - uses: actions/checkout@v4  # Check out repository code

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.12"

      - name: Install dependencies
        run: pip install -e ".[dev]"

      - name: Run tests
        run: pytest -v
```


## A Complete CI Workflow

Here is a comprehensive workflow for the expense tracker:

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

      - name: Upload coverage report
        uses: codecov/codecov-action@v4
        with:
          files: ./coverage.xml
          fail_ci_if_error: false

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

  docker:
    runs-on: ubuntu-latest
    needs: [test, lint]  # Only run if test and lint pass

    steps:
      - uses: actions/checkout@v4

      - name: Build Docker image
        run: docker build -t expenses-api .

      - name: Verify docker-compose config
        run: docker-compose config
```


## Key Workflow Features

### Matrix Builds

Test across multiple Python versions:

```yaml
jobs:
  test:
    strategy:
      matrix:
        python-version: ["3.11", "3.12"]

    steps:
      - uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python-version }}
```

### Secrets

Store sensitive values in repository settings:

```yaml
- name: Run tests
  run: pytest
  env:
    OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
```

Never hardcode secrets in workflow files.

### Caching

Speed up builds by caching dependencies:

```yaml
- name: Cache pip packages
  uses: actions/cache@v4
  with:
    path: ~/.cache/pip
    key: ${{ runner.os }}-pip-${{ hashFiles('**/pyproject.toml') }}
    restore-keys: |
      ${{ runner.os }}-pip-
```

### Job Dependencies

Control execution order:

```yaml
jobs:
  test:
    runs-on: ubuntu-latest
    # ...

  deploy:
    runs-on: ubuntu-latest
    needs: test  # Only runs if test job passes
    if: github.ref == 'refs/heads/main'  # Only on main branch
```

### Branch Protection

Configure GitHub to require CI passes before merging:

1. Go to repository Settings > Branches
2. Add rule for `main` branch
3. Enable "Require status checks to pass"
4. Select your CI workflow jobs


## Handling Integration Tests

Integration tests require API keys. Skip them in CI or provide test keys:

```python
# In conftest.py
import pytest

@pytest.fixture
def requires_openai():
    """Skip test if OpenAI key not available."""
    import os
    if not os.getenv("OPENAI_API_KEY"):
        pytest.skip("OPENAI_API_KEY not set")
```

Or use pytest markers:

```python
@pytest.mark.integration
def test_real_openai_call():
    pass
```

```bash
# Run without integration tests
pytest -m "not integration"
```


## Workflow for the Expense Tracker

The recommended CI workflow:

1. **test** job: Run pytest with coverage, fail if below 95%
2. **lint** job: Check formatting and linting with ruff
3. **docker** job: Build image, verify compose config

All jobs run on every push and PR. The docker job only runs after test and lint pass.


## Debugging Workflow Failures

When a workflow fails:

1. Click on the failed workflow run in GitHub Actions tab
2. Expand the failed step to see logs
3. Look for error messages and stack traces

Common issues:

| Problem | Solution |
|---------|----------|
| "Module not found" | Add package to `.[dev]` dependencies |
| Secret not available | Add secret in repo Settings > Secrets |
| Test timeout | Increase timeout or mock slow operations |
| Coverage too low | Add tests for uncovered code paths |


## Local Testing Before Push

Run the same checks locally before pushing:

```bash
# Run tests with coverage
pytest --cov=src --cov-fail-under=95

# Check formatting
ruff format --check .

# Check linting
ruff check .

# Verify Docker builds
docker build -t expenses-api .
docker-compose config
```

If all pass locally, they should pass in CI.


## Continuous Deployment

Once CI passes, you can automate deployment:

```yaml
deploy:
  runs-on: ubuntu-latest
  needs: [test, lint, docker]
  if: github.ref == 'refs/heads/main'

  steps:
    - uses: actions/checkout@v4

    - name: Deploy to Fly.io
      uses: superfly/flyctl-actions@1.4
      with:
        args: "deploy"
      env:
        FLY_API_TOKEN: ${{ secrets.FLY_API_TOKEN }}
```


## Further Reading

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Workflow Syntax Reference](https://docs.github.com/en/actions/reference/workflow-syntax-for-github-actions)
- [Actions Marketplace](https://github.com/marketplace?type=actions)
- [Codecov GitHub Action](https://github.com/codecov/codecov-action)
