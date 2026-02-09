# Week 5: Web Interface - FastAPI and Streamlit

Welcome to Week 5! This week you will build a complete web interface for the expense tracker. You will create a FastAPI REST API backend with dependency injection, and a Streamlit dashboard frontend with data visualizations using Plotly.

## What You're Building This Week

```
+------------------------------------------------------------------+
|                    WEEK 5: WEB INTERFACE                         |
+------------------------------------------------------------------+

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
    | - GET /     |     | - GET /     |     | - GET       |
    | - POST      |     +-------------+     |   /summary  |
    | - GET /{id} |                         +-------------+
    | - DELETE    |
    +-------------+
          |
          v
    +-------------------+
    | Dependency        |
    | Injection         |
    | (deps.py)         |
    +-------------------+
          |
          +-- get_db_session()
          +-- get_expense_repo()
          +-- get_category_repo()
          +-- get_classification_service()
          +-- get_user_id()
```

## Learning Objectives

By the end of this week, you will:

- Build a REST API with FastAPI and automatic OpenAPI documentation
- Implement dependency injection for clean, testable code
- Create Pydantic schemas for request/response validation
- Build a Streamlit dashboard with Plotly visualizations
- Implement multiuser support with user ID from headers
- Create analytics endpoints with aggregated data
- Write integration tests with FastAPI TestClient


## Week 5 Checklist

### Technical Milestones

- [ ] Create FastAPI application with CORS and lifespan
- [ ] Implement dependency injection in `deps.py`
- [ ] Create expense routes (list, classify, get, delete)
- [ ] Create categories route
- [ ] Create analytics route (summary with totals)
- [ ] Build Streamlit dashboard with navigation
- [ ] Add expense list view with pagination
- [ ] Add analytics visualizations (Plotly charts)
- [ ] Implement API client for Streamlit
- [ ] Pass all provided tests

### Concepts to Master

- [ ] FastAPI dependency injection with `Depends()`
- [ ] Pydantic request/response schemas
- [ ] FastAPI routers for modular routes
- [ ] Streamlit session state and caching
- [ ] Plotly for data visualization


## Key Concepts This Week

### 1. FastAPI Dependency Injection

```python
from fastapi import Depends
from sqlmodel import Session

def get_db_session():
    """Dependency that provides a database session."""
    engine = create_engine(DATABASE_URL)
    with Session(engine) as session:
        yield session

def get_expense_repo(session: Session = Depends(get_db_session)):
    """Dependency that provides expense repository."""
    return DBExpenseRepo(db_url=DATABASE_URL, session=session)

def get_user_id(x_user_id: str = Header(default=None)):
    """Extract user ID from request header."""
    return int(x_user_id) if x_user_id else DEFAULT_USER_ID

# Usage in route
@router.get("/")
def list_expenses(
    expense_repo: ExpenseRepository = Depends(get_expense_repo),
    user_id: int = Depends(get_user_id),
):
    return expense_repo.list_by_user(user_id)
```

### 2. Pydantic Schemas for API

```python
from pydantic import BaseModel

class ExpenseClassifyRequest(BaseModel):
    description: str

class ExpenseClassifyResponse(BaseModel):
    id: int
    category: str
    amount: Decimal
    currency: str
    confidence: float

class ExpenseListResponse(BaseModel):
    items: list[ExpenseResponse]
    total: int
    page: int
    page_size: int
```

### 3. FastAPI Routers

```python
from fastapi import APIRouter

router = APIRouter(prefix="/expenses", tags=["Expenses"])

@router.get("/", response_model=ExpenseListResponse)
def list_expenses(...):
    pass

@router.post("/classify", response_model=ExpenseClassifyResponse)
def classify_expense(...):
    pass
```

### 4. Streamlit with Plotly

```python
import streamlit as st
import plotly.express as px

def render_dashboard():
    st.title("Expense Dashboard")

    # Fetch data from API
    summary = api_client.get_summary()

    # Category bar chart
    fig = px.bar(
        summary["category_totals"],
        x="category",
        y="total",
        title="Spending by Category"
    )
    st.plotly_chart(fig)
```


## Project Structure After Week 5

```
expenses_ai_agent/
+-- src/
|   +-- expenses_ai_agent/
|       +-- api/
|       |   +-- __init__.py
|       |   +-- main.py           # FastAPI app
|       |   +-- deps.py           # Dependency injection
|       |   +-- routes/
|       |   |   +-- __init__.py
|       |   |   +-- expenses.py   # Expense CRUD + classify
|       |   |   +-- categories.py # List categories
|       |   |   +-- analytics.py  # Summary endpoint
|       |   |   +-- health.py     # Health check
|       |   +-- schemas/
|       |       +-- __init__.py
|       |       +-- expense.py    # Request/response models
|       |       +-- analytics.py  # Summary models
|       +-- streamlit/
|           +-- __init__.py
|           +-- app.py            # Main Streamlit app
|           +-- api_client.py     # HTTP client for API
|           +-- views/
|               +-- __init__.py
|               +-- dashboard.py  # Analytics view
|               +-- expenses.py   # Expense list view
|               +-- add_expense.py # Add expense form
+-- tests/
    +-- unit/
        +-- test_week5_api.py
        +-- test_week5_streamlit.py
```


## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/expenses/` | List expenses (paginated, filtered by user) |
| POST | `/api/v1/expenses/classify` | Classify and store expense |
| GET | `/api/v1/expenses/{id}` | Get single expense |
| DELETE | `/api/v1/expenses/{id}` | Delete expense |
| GET | `/api/v1/categories/` | List all categories |
| GET | `/api/v1/analytics/summary` | Get category and monthly totals |
| GET | `/api/v1/health` | Health check |


## Environment Variables

Add to your `.env` file:

```bash
API_BASE_URL=http://localhost:8000/api/v1
CORS_ORIGINS=http://localhost:8501
DEFAULT_USER_ID=12345
```


## Build Guide

### Step 1: FastAPI Application (`api/main.py`)

Create the FastAPI app:
- Configure CORS middleware
- Add lifespan handler for DB table creation
- Include routers

### Step 2: Dependencies (`api/deps.py`)

Create dependency functions:
- `get_db_session()` - yields SQLModel session
- `get_expense_repo()` - returns DBExpenseRepo
- `get_category_repo()` - returns DBCategoryRepo
- `get_classification_service()` - returns ClassificationService
- `get_user_id()` - extracts user ID from X-User-ID header

### Step 3: Request/Response Schemas (`api/schemas/`)

Create Pydantic models:
- `ExpenseClassifyRequest` - description field
- `ExpenseClassifyResponse` - full response with ID
- `ExpenseResponse` - for GET endpoints
- `ExpenseListResponse` - paginated list
- `CategoryTotal`, `MonthlyTotal`, `AnalyticsSummary`

### Step 4: Routes (`api/routes/`)

Implement route handlers:
- `expenses.py` - CRUD + classify
- `categories.py` - list categories
- `analytics.py` - summary endpoint
- `health.py` - simple health check

### Step 5: Streamlit App (`streamlit/`)

Create views:
- `app.py` - main app with sidebar navigation
- `api_client.py` - httpx client for API
- `views/dashboard.py` - Plotly charts
- `views/expenses.py` - expense list with delete
- `views/add_expense.py` - classification form


## Multiuser Support

Users are identified by the `X-User-ID` header:

```python
# In deps.py
def get_user_id(
    x_user_id: str = Header(default=None, alias="X-User-ID")
) -> int:
    if x_user_id:
        return int(x_user_id)
    return config("DEFAULT_USER_ID", cast=int, default=12345)

# In expense repo - filter by user
def list_by_user(self, telegram_user_id: int) -> Sequence[Expense]:
    statement = select(Expense).where(Expense.telegram_user_id == telegram_user_id)
    return self._session.exec(statement).all()
```


## Definition of Done

### Tests to Pass

Copy the test files from `curriculum/week5/tests/` into your `tests/unit/` directory:

- `test_week5_api.py` (16 tests)
- `test_week5_streamlit.py` (8 tests)

### Commands - All Must Succeed

| Command | Expected Result |
|---------|-----------------|
| `pytest tests/unit/test_week5_*.py -v` | All 24 tests pass |
| `ruff format --check .` | No formatting issues |
| `ruff check .` | No linting errors |
| `uvicorn expenses_ai_agent.api.main:app --reload` | Server starts on :8000 |

### You Are Done When

- All 24 tests pass (green)
- No ruff warnings
- FastAPI docs available at http://localhost:8000/docs
- Streamlit app runs with `streamlit run src/expenses_ai_agent/streamlit/app.py`


## Running the Stack

Terminal 1 (API):
```bash
uvicorn expenses_ai_agent.api.main:app --reload --port 8000
```

Terminal 2 (Streamlit):
```bash
streamlit run src/expenses_ai_agent/streamlit/app.py
```

Open:
- API docs: http://localhost:8000/docs
- Dashboard: http://localhost:8501


## Common Issues and Solutions

| Issue | Solution |
|-------|----------|
| CORS errors | Add Streamlit origin to CORS_ORIGINS |
| "Connection refused" in Streamlit | Ensure API is running on port 8000 |
| Session errors | Use `yield` in get_db_session, not return |
| Plotly not displaying | Ensure `plotly` is in dependencies |
| Test client issues | Use `TestClient(app)` from fastapi.testclient |


## Looking Ahead

In Week 6, you will add deployment infrastructure:

- Docker and docker-compose
- GitHub Actions CI/CD
- Production deployment to Fly.io
- Documentation and examples

Your API and dashboard will be containerized and deployed!

---

**Testing tip**: Use FastAPI's TestClient with dependency overrides:

```python
from fastapi.testclient import TestClient

app.dependency_overrides[get_expense_repo] = lambda: mock_repo
client = TestClient(app)
response = client.get("/api/v1/expenses/")
```
