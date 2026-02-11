# Looking Ahead: Week 6

Congratulations on completing Week 5! You now have a complete web interface with FastAPI backend and Streamlit dashboard.


## What's Next

In Week 6, you will deploy and document your application:

- **Docker Containers** - Containerize all services
- **Docker Compose** - Orchestrate multiple containers
- **CI/CD Pipeline** - Automated testing and deployment
- **Test Coverage** - Achieve 95%+ coverage


## How Week 5 Connects to Week 6

Your FastAPI and Streamlit applications become Docker services:

```
Week 5 Components              Week 6 Containerization
------------------             ----------------------
FastAPI app           -->      fastapi:8000 container
Streamlit dashboard   -->      streamlit:8501 container
SQLite database       -->      Mounted volume
.env configuration    -->      Docker environment variables
```


## Docker Compose Architecture

```yaml
services:
  fastapi:
    build: .
    ports:
      - "8000:8000"
    volumes:
      - ./data:/app/data
    environment:
      - DATABASE_URL=sqlite:///data/expenses.db

  streamlit:
    build: .
    ports:
      - "8501:8501"
    depends_on:
      - fastapi
    environment:
      - API_BASE_URL=http://fastapi:8000/api/v1
```


## CI/CD Pipeline Preview

```yaml
# .github/workflows/ci.yml
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Set up Python
        uses: actions/setup-python@v5
      - name: Install dependencies
        run: pip install -e ".[dev]"
      - name: Run tests with coverage
        run: pytest --cov=src --cov-fail-under=95
```


## Prepare for Week 6

Before starting Week 6, make sure you:

1. Have all 24 Week 5 tests passing
2. Can start FastAPI and Streamlit locally
3. Understand the API integration between frontend and backend
4. Have Docker installed on your machine

See you in the final week!
