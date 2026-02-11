# Week 5 Review: FastAPI and Streamlit

Before diving into deployment, let us review what you built in Week 5. The web interface represents the culmination of your backend work, exposing the classification service through a professional REST API and a user-friendly dashboard.


## What You Built

Week 5 added two major components to your expense tracker:

1. **FastAPI REST API** - A production-grade API with automatic documentation, dependency injection, and Pydantic validation
2. **Streamlit Dashboard** - An interactive frontend with data visualizations using Plotly


## Architecture Recap

```
                    +-------------------+
                    |  Streamlit App    |
                    |  (Dashboard)      |
                    +-------------------+
                              |
                              | HTTP (httpx)
                              v
                    +-------------------+
                    |  FastAPI Backend  |
                    |  /api/v1/...      |
                    +-------------------+
                              |
          +-------------------+-------------------+
          |                   |                   |
          v                   v                   v
    +-------------+     +-------------+     +-------------+
    | /expenses   |     | /categories |     | /analytics  |
    +-------------+     +-------------+     +-------------+
          |
          v
    +-------------------+
    | Classification    |
    | Service           |
    +-------------------+
          |
          v
    +-------------------+
    | Repository Layer  |
    | (SQLite)          |
    +-------------------+
```


## Key Components

### FastAPI Application

The API follows REST conventions with versioned endpoints:

| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | `/api/v1/expenses/` | List expenses (paginated) |
| POST | `/api/v1/expenses/classify` | Classify and store expense |
| GET | `/api/v1/expenses/{id}` | Get single expense |
| DELETE | `/api/v1/expenses/{id}` | Delete expense |
| GET | `/api/v1/categories/` | List all categories |
| GET | `/api/v1/analytics/summary` | Dashboard analytics |
| GET | `/api/v1/health` | Health check |

### Dependency Injection

FastAPI's `Depends()` pattern enables clean, testable code:

```python
def get_expense_repo(session: Session = Depends(get_db_session)):
    return DBExpenseRepo(db_url=DATABASE_URL, session=session)

@router.get("/")
def list_expenses(
    expense_repo: ExpenseRepository = Depends(get_expense_repo),
    user_id: int = Depends(get_user_id),
):
    return expense_repo.list_by_user(user_id)
```

This pattern allows you to swap implementations in tests:

```python
app.dependency_overrides[get_expense_repo] = lambda: mock_repo
```

### Streamlit Dashboard

The dashboard provides three views:

1. **Dashboard** - Summary metrics and Plotly charts
2. **Expenses** - Paginated expense list with delete functionality
3. **Add Expense** - Form for classifying new expenses


## API Client Pattern

The Streamlit app communicates with FastAPI through a dedicated client:

```python
class ExpenseAPIClient:
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.client = httpx.Client(timeout=30.0)

    def classify_expense(self, description: str, user_id: int):
        response = self.client.post(
            f"{self.base_url}/expenses/classify",
            json={"description": description},
            headers={"X-User-ID": str(user_id)},
        )
        response.raise_for_status()
        return response.json()
```


## Multiuser Support

Users are identified by the `X-User-ID` header, enabling multitenancy:

```python
def get_user_id(
    x_user_id: str = Header(default=None, alias="X-User-ID")
) -> int:
    if x_user_id:
        return int(x_user_id)
    return config("DEFAULT_USER_ID", cast=int, default=12345)
```

Each user sees only their own expenses in the dashboard.


## Running the Stack Locally

Without Docker, you need two terminals:

```bash
# Terminal 1: API
uvicorn expenses_ai_agent.api.main:app --reload --port 8000

# Terminal 2: Streamlit
streamlit run src/expenses_ai_agent/streamlit/app.py
```

This works for development but creates friction:
- Must remember to start both services
- Different environment variables needed for each
- Database path must be configured consistently
- Port conflicts if anything else uses 8000 or 8501


## The Deployment Challenge

Week 5 gave you a working local stack. But consider what happens when you want to:

- Share your project with a colleague
- Deploy to a cloud server
- Run tests in GitHub Actions
- Scale to multiple instances

Each scenario requires recreating your environment from scratch. The colleague needs the same Python version, the same dependencies, the same environment variables. The cloud server needs everything configured identically to your laptop.

This is exactly the problem Docker solves.


## What Changes in Week 6

Instead of running services manually, you will:

1. **Containerize** - Package each service into a Docker image
2. **Orchestrate** - Use docker-compose to run everything together
3. **Automate** - Set up GitHub Actions to test and deploy automatically
4. **Validate** - Ensure comprehensive test coverage before deployment

The goal is a single command that reproduces your entire environment anywhere:

```bash
docker-compose up --build
```


## Verification: Week 5 Components Working

Before proceeding, verify your Week 5 implementation works:

```bash
# Run Week 5 tests
pytest tests/unit/test_week5_*.py -v

# Start the API (should respond to health checks)
uvicorn expenses_ai_agent.api.main:app --port 8000 &
curl http://localhost:8000/api/v1/health

# Verify the imports work
python -c "from expenses_ai_agent.api.main import app; print('API OK')"
python -c "from expenses_ai_agent.streamlit.app import main; print('Streamlit OK')"
```

If these commands succeed, you are ready to containerize your application.


## Summary

Week 5 delivered a complete web interface:

- REST API with FastAPI, dependency injection, and OpenAPI docs
- Streamlit dashboard with Plotly visualizations
- Multiuser support through header-based authentication
- Pydantic schemas for request/response validation

Now you will package this into containers and set up automated pipelines.

Continue to Docker Fundamentals.
