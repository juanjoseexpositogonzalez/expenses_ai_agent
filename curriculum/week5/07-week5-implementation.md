# Week 5 Implementation: Web Interface

This implementation exercise teaches you to build the complete web interface with FastAPI backend and Streamlit frontend.


## Learning Goals

By the end of this implementation, you will:

- Create a FastAPI application with CORS and lifespan handlers
- Implement dependency injection for clean, testable routes
- Build Pydantic schemas for request/response validation
- Create REST endpoints for expenses, categories, and analytics
- Build a Streamlit dashboard with Plotly visualizations
- Connect the frontend to the backend with an HTTP client


## What You're Building

**FastAPI Backend:**
```bash
curl -X POST "http://localhost:8000/api/v1/expenses/classify" \
  -H "Content-Type: application/json" \
  -H "X-User-ID: 12345" \
  -d '{"description": "Coffee at Starbucks $5.50"}'
```

**Response:**
```json
{
  "id": 1,
  "category": "Food",
  "amount": "5.50",
  "currency": "USD",
  "confidence": 0.95
}
```

**Streamlit Dashboard:**
- Navigation sidebar with three pages
- Dashboard with Plotly charts
- Expense list with delete functionality
- Add expense form with AI classification


## Test Suite: FastAPI API

Copy this to `tests/unit/test_week5_api.py`:

```python
"""
Week 5 - Definition of Done: FastAPI REST API

Copy this file to your project's tests/unit/ directory.
Run: pytest tests/unit/test_week5_api.py -v
All tests must pass to complete Week 5's API milestone.

These tests verify your implementation of:
- FastAPI application structure
- Expense routes (CRUD + classify)
- Analytics routes
- Dependency injection
"""

from datetime import datetime, timezone
from decimal import Decimal
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def mock_expense_repo():
    """Create a mock expense repository."""
    from expenses_ai_agent.storage.models import Currency, Expense, ExpenseCategory

    repo = MagicMock()
    category = ExpenseCategory(id=1, name="Food")
    expenses = [
        Expense(id=1, amount=Decimal("10.00"), currency=Currency.EUR, category=category, telegram_user_id=12345),
        Expense(id=2, amount=Decimal("20.00"), currency=Currency.USD, category=category, telegram_user_id=12345),
    ]
    repo.list_by_user.return_value = expenses
    repo.get.return_value = expenses[0]
    repo.list.return_value = expenses
    return repo


@pytest.fixture
def mock_category_repo():
    """Create a mock category repository."""
    from expenses_ai_agent.storage.models import ExpenseCategory

    repo = MagicMock()
    repo.list.return_value = ["Food", "Transport", "Entertainment"]
    repo.get.return_value = ExpenseCategory(id=1, name="Food")
    return repo


@pytest.fixture
def test_client(mock_expense_repo, mock_category_repo):
    """Create a test client with mocked dependencies."""
    from expenses_ai_agent.api.deps import get_category_repo, get_expense_repo
    from expenses_ai_agent.api.main import app

    app.dependency_overrides[get_expense_repo] = lambda: mock_expense_repo
    app.dependency_overrides[get_category_repo] = lambda: mock_category_repo

    with TestClient(app) as client:
        yield client

    app.dependency_overrides.clear()


class TestFastAPIApp:
    """Tests for the FastAPI application structure."""

    def test_app_exists(self):
        """FastAPI app should be importable."""
        from expenses_ai_agent.api.main import app

        assert app is not None

    def test_app_has_cors(self, test_client):
        """App should have CORS middleware configured."""
        # OPTIONS request should work
        response = test_client.options("/api/v1/health")
        # CORS headers should be present or request should succeed
        assert response.status_code in [200, 405]

    def test_health_endpoint(self, test_client):
        """Health endpoint should return OK status."""
        response = test_client.get("/api/v1/health")

        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert data["status"] in ["ok", "healthy", "OK"]


class TestExpenseRoutes:
    """Tests for expense CRUD routes."""

    def test_list_expenses(self, test_client, mock_expense_repo):
        """GET /expenses/ should return paginated expenses."""
        response = test_client.get("/api/v1/expenses/")

        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "total" in data

    def test_list_expenses_with_user_header(self, test_client, mock_expense_repo):
        """List should filter by X-User-ID header."""
        response = test_client.get(
            "/api/v1/expenses/",
            headers={"X-User-ID": "12345"}
        )

        assert response.status_code == 200
        mock_expense_repo.list_by_user.assert_called()

    def test_get_expense_by_id(self, test_client, mock_expense_repo):
        """GET /expenses/{id} should return single expense."""
        response = test_client.get("/api/v1/expenses/1")

        assert response.status_code == 200
        data = response.json()
        assert "id" in data
        assert "amount" in data

    def test_get_nonexistent_expense_returns_404(self, test_client, mock_expense_repo):
        """GET /expenses/{id} should return 404 if not found."""
        from expenses_ai_agent.storage.exceptions import ExpenseNotFoundError

        mock_expense_repo.get.side_effect = ExpenseNotFoundError(999)

        response = test_client.get("/api/v1/expenses/999")

        assert response.status_code == 404

    def test_delete_expense(self, test_client, mock_expense_repo):
        """DELETE /expenses/{id} should remove expense."""
        response = test_client.delete("/api/v1/expenses/1")

        assert response.status_code == 204
        mock_expense_repo.delete.assert_called_with(1)

    def test_classify_expense(self, test_client, mock_expense_repo, mock_category_repo):
        """POST /expenses/classify should classify and store expense."""
        from expenses_ai_agent.llms.output import ExpenseCategorizationResponse
        from expenses_ai_agent.storage.models import Currency

        with patch("expenses_ai_agent.api.routes.expenses.ClassificationService") as mock_cls:
            mock_service = MagicMock()
            mock_result = MagicMock()
            mock_result.response = ExpenseCategorizationResponse(
                category="Food",
                total_amount=Decimal("5.50"),
                currency=Currency.USD,
                confidence=0.95,
                cost=Decimal("0.001"),
            )
            mock_result.persisted = True
            mock_service.classify.return_value = mock_result
            mock_cls.return_value = mock_service

            response = test_client.post(
                "/api/v1/expenses/classify",
                json={"description": "Coffee $5.50"},
                headers={"X-User-ID": "12345"},
            )

            assert response.status_code == 201
            data = response.json()
            assert "category" in data


class TestCategoryRoutes:
    """Tests for category routes."""

    def test_list_categories(self, test_client, mock_category_repo):
        """GET /categories/ should return all category names."""
        response = test_client.get("/api/v1/categories/")

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert "Food" in data


class TestAnalyticsRoutes:
    """Tests for analytics routes."""

    def test_get_summary(self, test_client, mock_expense_repo):
        """GET /analytics/summary should return aggregated data."""
        mock_expense_repo.get_category_totals.return_value = {
            "Food": Decimal("100.00"),
            "Transport": Decimal("50.00"),
        }
        mock_expense_repo.get_monthly_totals.return_value = {
            "2024-01": Decimal("150.00"),
        }

        response = test_client.get(
            "/api/v1/analytics/summary",
            headers={"X-User-ID": "12345"}
        )

        assert response.status_code == 200
        data = response.json()
        assert "category_totals" in data or "categories" in str(data).lower()


class TestAPISchemas:
    """Tests for Pydantic request/response schemas."""

    def test_expense_classify_request_exists(self):
        """ExpenseClassifyRequest schema should exist."""
        from expenses_ai_agent.api.schemas.expense import ExpenseClassifyRequest

        request = ExpenseClassifyRequest(description="Test")
        assert request.description == "Test"

    def test_expense_response_exists(self):
        """ExpenseResponse schema should exist."""
        from expenses_ai_agent.api.schemas.expense import ExpenseResponse

        assert ExpenseResponse is not None

    def test_expense_list_response_has_pagination(self):
        """ExpenseListResponse should include pagination fields."""
        from expenses_ai_agent.api.schemas.expense import ExpenseListResponse

        # Check the model has expected fields
        fields = ExpenseListResponse.model_fields
        assert "items" in fields
        assert "total" in fields


class TestDependencyInjection:
    """Tests for dependency injection functions."""

    def test_get_expense_repo_exists(self):
        """get_expense_repo dependency should be importable."""
        from expenses_ai_agent.api.deps import get_expense_repo

        assert callable(get_expense_repo)

    def test_get_user_id_exists(self):
        """get_user_id dependency should be importable."""
        from expenses_ai_agent.api.deps import get_user_id

        assert callable(get_user_id)
```


## Test Suite: Streamlit Dashboard

Copy this to `tests/unit/test_week5_streamlit.py`:

```python
"""
Week 5 - Definition of Done: Streamlit Dashboard

Copy this file to your project's tests/unit/ directory.
Run: pytest tests/unit/test_week5_streamlit.py -v
All tests must pass to complete Week 5's Streamlit milestone.

These tests verify your implementation of:
- Streamlit API client
- Dashboard views structure
"""

from decimal import Decimal
from unittest.mock import MagicMock, patch

import pytest


class TestStreamlitAPIClient:
    """Tests for the Streamlit API client."""

    def test_api_client_exists(self):
        """ExpenseAPIClient should be importable."""
        from expenses_ai_agent.streamlit.api_client import ExpenseAPIClient

        assert ExpenseAPIClient is not None

    def test_api_client_has_base_url(self):
        """Client should accept base URL configuration."""
        from expenses_ai_agent.streamlit.api_client import ExpenseAPIClient

        client = ExpenseAPIClient(base_url="http://localhost:8000/api/v1")
        assert "8000" in client.base_url or hasattr(client, "base_url")

    def test_api_client_get_expenses(self):
        """Client should have method to get expenses."""
        from expenses_ai_agent.streamlit.api_client import ExpenseAPIClient

        client = ExpenseAPIClient(base_url="http://test")
        assert hasattr(client, "get_expenses") or hasattr(client, "list_expenses")

    def test_api_client_classify_expense(self):
        """Client should have method to classify expense."""
        from expenses_ai_agent.streamlit.api_client import ExpenseAPIClient

        client = ExpenseAPIClient(base_url="http://test")
        assert hasattr(client, "classify_expense") or hasattr(client, "classify")

    def test_api_client_get_summary(self):
        """Client should have method to get analytics summary."""
        from expenses_ai_agent.streamlit.api_client import ExpenseAPIClient

        client = ExpenseAPIClient(base_url="http://test")
        assert hasattr(client, "get_summary") or hasattr(client, "get_analytics")


class TestStreamlitViews:
    """Tests for Streamlit view modules."""

    def test_dashboard_view_exists(self):
        """Dashboard view module should exist."""
        from expenses_ai_agent.streamlit.views import dashboard

        assert dashboard is not None

    def test_expenses_view_exists(self):
        """Expenses list view module should exist."""
        from expenses_ai_agent.streamlit.views import expenses

        assert expenses is not None

    def test_add_expense_view_exists(self):
        """Add expense view module should exist."""
        from expenses_ai_agent.streamlit.views import add_expense

        assert add_expense is not None


class TestStreamlitApp:
    """Tests for the main Streamlit app."""

    def test_app_module_exists(self):
        """Main app module should be importable."""
        from expenses_ai_agent.streamlit import app

        assert app is not None
```


## Implementation Strategy

Work through these steps in order. Each step targets specific tests.

### Step 1: Create FastAPI Application

Build `api/main.py` with the FastAPI app:

**Target tests:** `TestFastAPIApp` (3 tests)

Create the main application file with:
- FastAPI instance with title and version
- CORS middleware configuration
- Lifespan handler for database setup
- Router includes for all routes

### Step 2: Implement Dependencies

Build `api/deps.py` with dependency functions:

**Target tests:** `TestDependencyInjection` (2 tests)

Create these dependency functions:
- `get_db_session()` - yields SQLModel Session
- `get_expense_repo()` - returns DBExpenseRepo
- `get_category_repo()` - returns DBCategoryRepo
- `get_user_id()` - extracts user ID from X-User-ID header

### Step 3: Create Pydantic Schemas

Build `api/schemas/expense.py` and `api/schemas/analytics.py`:

**Target tests:** `TestAPISchemas` (3 tests)

Define these schemas:
- `ExpenseClassifyRequest` - classification input
- `ExpenseClassifyResponse` - classification result
- `ExpenseResponse` - single expense
- `ExpenseListResponse` - paginated list with items and total
- `CategoryTotal`, `MonthlyTotal`, `AnalyticsSummary` - analytics data

### Step 4: Implement Expense Routes

Build `api/routes/expenses.py`:

**Target tests:** `TestExpenseRoutes` (6 tests)

Implement these endpoints:
- `GET /expenses/` - paginated list filtered by user
- `GET /expenses/{id}` - single expense or 404
- `DELETE /expenses/{id}` - remove expense (204 on success)
- `POST /expenses/classify` - classify and store (201 on success)

### Step 5: Implement Category and Analytics Routes

Build `api/routes/categories.py` and `api/routes/analytics.py`:

**Target tests:** `TestCategoryRoutes` (1 test), `TestAnalyticsRoutes` (1 test)

Implement:
- `GET /categories/` - list all category names
- `GET /analytics/summary` - category totals and monthly totals

### Step 6: Build Streamlit API Client

Build `streamlit/api_client.py`:

**Target tests:** `TestStreamlitAPIClient` (5 tests)

Create `ExpenseAPIClient` with:
- `base_url` attribute
- `get_expenses()` method
- `classify_expense()` method
- `get_summary()` method
- `delete_expense()` method
- `health_check()` method

### Step 7: Create Streamlit Views

Build `streamlit/views/` modules:

**Target tests:** `TestStreamlitViews` (3 tests)

Create these view modules:
- `views/dashboard.py` - analytics with Plotly charts
- `views/expenses.py` - expense list with delete
- `views/add_expense.py` - classification form

### Step 8: Create Main Streamlit App

Build `streamlit/app.py`:

**Target tests:** `TestStreamlitApp` (1 test)

Create the main app with:
- Page configuration
- API health check
- Sidebar navigation
- Page routing


## Helpful Concepts

### FastAPI Route Registration

```python
from fastapi import APIRouter, Depends, HTTPException

router = APIRouter(prefix="/expenses", tags=["Expenses"])

@router.get("/", response_model=ExpenseListResponse)
def list_expenses(
    expense_repo: ExpenseRepository = Depends(get_expense_repo),
    user_id: int = Depends(get_user_id),
):
    expenses = expense_repo.list_by_user(user_id)
    return ExpenseListResponse(items=expenses, total=len(expenses), ...)
```

[FastAPI Router Documentation](https://fastapi.tiangolo.com/tutorial/bigger-applications/)

### HTTP Status Codes

```python
from fastapi import status
from fastapi.responses import Response

@router.delete("/{expense_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_expense(expense_id: int, ...):
    repo.delete(expense_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)

@router.post("/classify", status_code=status.HTTP_201_CREATED)
def classify_expense(...):
    # Classify and store...
    return ExpenseClassifyResponse(...)
```

### Exception Handling

```python
from fastapi import HTTPException
from expenses_ai_agent.storage.exceptions import ExpenseNotFoundError

@router.get("/{expense_id}")
def get_expense(expense_id: int, expense_repo = Depends(get_expense_repo)):
    try:
        return expense_repo.get(expense_id)
    except ExpenseNotFoundError:
        raise HTTPException(status_code=404, detail="Expense not found")
```

### Streamlit View Pattern

```python
import streamlit as st
from expenses_ai_agent.streamlit.api_client import ExpenseAPIClient

def render_dashboard(api_client: ExpenseAPIClient):
    st.header("Dashboard")

    try:
        summary = api_client.get_summary()
        # Create Plotly charts...
    except Exception as e:
        st.error(f"Error loading dashboard: {e}")
```


## Validation Checklist

Before moving on, verify:

- [ ] All 24 tests pass: `pytest tests/unit/test_week5_*.py -v`
- [ ] No linting errors: `ruff check src/`
- [ ] Code is formatted: `ruff format .`
- [ ] API starts: `uvicorn expenses_ai_agent.api.main:app --reload`
- [ ] API docs available: http://localhost:8000/docs


## Debugging Tips

### "No module named 'expenses_ai_agent.api'"

Ensure you have `api/__init__.py` and all subdirectories have `__init__.py` files:

```
api/
    __init__.py
    main.py
    deps.py
    routes/
        __init__.py
        expenses.py
        categories.py
        analytics.py
        health.py
    schemas/
        __init__.py
        expense.py
        analytics.py
```

### "CORS error in browser"

Check that CORS middleware is configured before routers are added:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8501"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Then add routers
app.include_router(expenses.router, prefix="/api/v1")
```

### "422 Unprocessable Entity"

Pydantic validation failed. Check:
- Request body matches schema
- Required fields are provided
- Field types are correct (e.g., `description` is a string)

### "Connection refused in Streamlit"

The FastAPI server is not running. Start it in a separate terminal:

```bash
uvicorn expenses_ai_agent.api.main:app --reload --port 8000
```


## Step Hints


### Step 1: FastAPI App Hint

Use the lifespan context manager for startup logic:

```python
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    SQLModel.metadata.create_all(engine)
    yield
    # Shutdown (if needed)

app = FastAPI(title="Expense API", lifespan=lifespan)
```


### Step 2: Dependencies Hint

Use `yield` for session management:

```python
def get_db_session():
    engine = create_engine(DATABASE_URL)
    with Session(engine) as session:
        yield session
```

Chain dependencies:

```python
def get_expense_repo(session: Session = Depends(get_db_session)):
    return DBExpenseRepo(db_url=DATABASE_URL, session=session)
```


### Step 3: Schemas Hint

Use `model_config` for ORM compatibility:

```python
class ExpenseResponse(BaseModel):
    id: int
    amount: Decimal
    currency: str
    category: str

    model_config = {"from_attributes": True}
```


### Step 4: Expense Routes Hint

Handle the classify endpoint:

```python
@router.post("/classify", status_code=201)
def classify_expense(
    request: ExpenseClassifyRequest,
    expense_repo = Depends(get_expense_repo),
    category_repo = Depends(get_category_repo),
    user_id: int = Depends(get_user_id),
):
    # Create service with repos
    service = ClassificationService(
        assistant=OpenAIAssistant(),
        expense_repo=expense_repo,
        category_repo=category_repo,
    )

    # Classify with persistence
    result = service.classify(
        request.description,
        persist=True,
        telegram_user_id=user_id,
    )

    return ExpenseClassifyResponse(
        category=result.response.category,
        # ... other fields
    )
```


### Step 6: API Client Hint

Handle errors gracefully:

```python
def get_expenses(self) -> dict:
    response = httpx.get(
        f"{self.base_url}/expenses/",
        headers=self._headers(),
    )
    response.raise_for_status()  # Raises HTTPStatusError for 4xx/5xx
    return response.json()
```


### Step 7: Views Hint

Use Plotly Express for quick charts:

```python
import plotly.express as px
import streamlit as st

def render_dashboard(api_client):
    summary = api_client.get_summary()

    # Convert to DataFrame for Plotly
    import pandas as pd
    df = pd.DataFrame(summary["category_totals"])

    fig = px.bar(df, x="category", y="total", title="Spending by Category")
    st.plotly_chart(fig, use_container_width=True)
```

---

Your Week 5 web interface is complete when all 24 tests pass and both the API and dashboard are running.
