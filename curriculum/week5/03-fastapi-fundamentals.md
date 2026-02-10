# FastAPI Fundamentals

FastAPI is a modern Python web framework that combines high performance with developer productivity. This lesson covers the core concepts you'll use to build the expense API.


## Why FastAPI Exists

Building REST APIs in Python traditionally meant choosing between:

- **Flask** - Simple but manual validation, no async, no automatic docs
- **Django REST Framework** - Powerful but heavy, steep learning curve
- **Tornado/aiohttp** - Async but low-level, lots of boilerplate

FastAPI provides:

1. **Automatic validation** - Pydantic models validate request/response data
2. **Automatic documentation** - OpenAPI/Swagger docs generated from code
3. **Async support** - Native async/await for high concurrency
4. **Type safety** - Type hints drive behavior, not just documentation


## Creating a FastAPI Application

```python
from fastapi import FastAPI
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifecycle handler."""
    # Startup: create database tables
    SQLModel.metadata.create_all(engine)
    yield
    # Shutdown: cleanup resources (if needed)

app = FastAPI(
    title="Expense API",
    version="1.0.0",
    lifespan=lifespan,
)
```

The lifespan context manager replaces the deprecated `on_event("startup")` pattern. Code before `yield` runs at startup; code after runs at shutdown.


## CORS Middleware

Cross-Origin Resource Sharing (CORS) allows the Streamlit frontend (port 8501) to call the API (port 8000):

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8501"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

Without CORS, browsers block cross-origin requests for security. The middleware adds headers that tell browsers it's safe.

**When to configure CORS:** Any time your frontend runs on a different origin (domain, port, or protocol) than your backend.


## Routers for Modular Code

Split routes into separate files with `APIRouter`:

```python
# api/routes/expenses.py
from fastapi import APIRouter

router = APIRouter(prefix="/expenses", tags=["Expenses"])

@router.get("/")
def list_expenses():
    ...

@router.post("/classify")
def classify_expense():
    ...
```

```python
# api/main.py
from expenses_ai_agent.api.routes import expenses, categories, analytics, health

app.include_router(expenses.router, prefix="/api/v1")
app.include_router(categories.router, prefix="/api/v1")
app.include_router(analytics.router, prefix="/api/v1")
app.include_router(health.router, prefix="/api/v1")
```

This organizes your API into logical groups, each with its own file.


## Dependency Injection with Depends()

Dependencies provide reusable components to route handlers:

```python
from fastapi import Depends

def get_db_session():
    """Dependency that yields a database session."""
    engine = create_engine(DATABASE_URL)
    with Session(engine) as session:
        yield session

def get_expense_repo(
    session: Session = Depends(get_db_session)
) -> ExpenseRepository:
    """Dependency that provides expense repository."""
    return DBExpenseRepo(db_url=DATABASE_URL, session=session)

@router.get("/")
def list_expenses(
    expense_repo: ExpenseRepository = Depends(get_expense_repo),
):
    return expense_repo.list()
```

When FastAPI calls `list_expenses`:
1. It sees `expense_repo` needs `get_expense_repo`
2. `get_expense_repo` needs a session from `get_db_session`
3. FastAPI calls them in order, injecting results

**Why dependency injection matters:**
- Route handlers stay focused on HTTP logic
- Dependencies are easy to mock for testing
- Resources (database sessions) are properly managed


## Request Header Dependencies

Extract data from HTTP headers:

```python
from fastapi import Header

def get_user_id(
    x_user_id: str = Header(default=None, alias="X-User-ID")
) -> int:
    """Extract user ID from request header."""
    if x_user_id:
        return int(x_user_id)
    return config("DEFAULT_USER_ID", cast=int, default=12345)

@router.get("/")
def list_expenses(
    user_id: int = Depends(get_user_id),
    expense_repo: ExpenseRepository = Depends(get_expense_repo),
):
    return expense_repo.list_by_user(user_id)
```

This pattern enables multiuser support without authentication complexity.


## Python Comparison

| Flask | FastAPI |
|-------|---------|
| `@app.route("/", methods=["GET"])` | `@app.get("/")` |
| `request.json` (manual) | Function parameters (automatic) |
| Manual validation | Pydantic validation |
| No built-in docs | Automatic OpenAPI docs |
| `flask run` | `uvicorn app:app` |


## FastAPI in Our Project

The expense API uses these patterns:

| File | Purpose |
|------|---------|
| `api/main.py` | FastAPI app with CORS, lifespan, routers |
| `api/deps.py` | Dependency injection functions |
| `api/routes/*.py` | Route handlers grouped by resource |
| `api/schemas/*.py` | Pydantic request/response models |


## Further Reading

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [FastAPI Dependencies](https://fastapi.tiangolo.com/tutorial/dependencies/)
- [Starlette Middleware](https://www.starlette.io/middleware/)
