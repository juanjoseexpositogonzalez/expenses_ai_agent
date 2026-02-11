# Week 5 Success Criteria

Use this checklist to verify you've completed all Week 5 requirements.


## Validation Commands

All of these commands must succeed:

| Command | Expected Result |
|---------|-----------------|
| `pytest tests/unit/test_week5_api.py -v` | All 16 tests pass |
| `pytest tests/unit/test_week5_streamlit.py -v` | All 8 tests pass |
| `ruff format --check .` | No formatting issues |
| `ruff check .` | No linting errors |
| `uvicorn expenses_ai_agent.api.main:app` | Server starts on port 8000 |


## Running the Stack

Start both services:

**Terminal 1 - API:**
```bash
uvicorn expenses_ai_agent.api.main:app --reload --port 8000
```

**Terminal 2 - Dashboard:**
```bash
streamlit run src/expenses_ai_agent/streamlit/app.py
```

**Verify:**
- API docs: http://localhost:8000/docs (should show Swagger UI)
- Dashboard: http://localhost:8501 (should show expense tracker)


## Technical Checklist

### FastAPI Application (`api/main.py`)

- [ ] FastAPI app with title and version
- [ ] CORS middleware configured for Streamlit origin
- [ ] Lifespan handler creates database tables on startup
- [ ] All routers included with `/api/v1` prefix

### Dependencies (`api/deps.py`)

- [ ] `get_db_session()` yields SQLModel Session
- [ ] `get_expense_repo()` returns DBExpenseRepo with injected session
- [ ] `get_category_repo()` returns DBCategoryRepo with injected session
- [ ] `get_user_id()` extracts from X-User-ID header with default fallback

### Schemas (`api/schemas/`)

- [ ] `ExpenseClassifyRequest` with description field
- [ ] `ExpenseClassifyResponse` with id, category, amount, currency, confidence
- [ ] `ExpenseResponse` with from_attributes config
- [ ] `ExpenseListResponse` with items list, total, page, page_size
- [ ] `AnalyticsSummary` with category_totals and monthly_totals

### Expense Routes (`api/routes/expenses.py`)

- [ ] `GET /expenses/` returns paginated list
- [ ] `GET /expenses/` filters by X-User-ID header
- [ ] `GET /expenses/{id}` returns single expense
- [ ] `GET /expenses/{id}` returns 404 for nonexistent
- [ ] `DELETE /expenses/{id}` returns 204
- [ ] `POST /expenses/classify` returns 201 with classification

### Category Routes (`api/routes/categories.py`)

- [ ] `GET /categories/` returns list of category names

### Analytics Routes (`api/routes/analytics.py`)

- [ ] `GET /analytics/summary` returns category and monthly totals

### Health Routes (`api/routes/health.py`)

- [ ] `GET /health` returns status: ok/healthy

### Streamlit API Client (`streamlit/api_client.py`)

- [ ] `ExpenseAPIClient` class with base_url attribute
- [ ] `get_expenses()` method
- [ ] `classify_expense()` method
- [ ] `get_summary()` method
- [ ] `delete_expense()` method
- [ ] `health_check()` method

### Streamlit Views (`streamlit/views/`)

- [ ] `dashboard.py` module exists
- [ ] `expenses.py` module exists
- [ ] `add_expense.py` module exists

### Streamlit App (`streamlit/app.py`)

- [ ] Main app module importable
- [ ] Sidebar navigation
- [ ] Health check on startup


## API Endpoints Reference

| Method | Endpoint | Status | Description |
|--------|----------|--------|-------------|
| GET | `/api/v1/expenses/` | 200 | Paginated expense list |
| POST | `/api/v1/expenses/classify` | 201 | Classify and store |
| GET | `/api/v1/expenses/{id}` | 200/404 | Single expense |
| DELETE | `/api/v1/expenses/{id}` | 204 | Remove expense |
| GET | `/api/v1/categories/` | 200 | All category names |
| GET | `/api/v1/analytics/summary` | 200 | Dashboard data |
| GET | `/api/v1/health` | 200 | Health check |


## Conceptual Understanding

You should be able to answer:

1. **Why use dependency injection?**
   - Decouples route logic from resource creation
   - Easy to mock for testing
   - Resources (sessions) are properly managed
   - Same dependencies reused across routes

2. **Why separate schemas from models?**
   - API contracts differ from database schema
   - Validation rules specific to API
   - Hide internal fields from clients
   - Version API independently of database

3. **Why use Streamlit instead of React/Vue?**
   - Rapid prototyping in Python
   - No JavaScript/frontend build required
   - Ideal for data apps and internal tools
   - Production dashboards may need full SPA

4. **Why an API client class?**
   - Single source of API configuration
   - Consistent error handling
   - Easy to test and mock
   - Clean separation from view logic


## You Are Done When

- All 24 tests pass (green)
- No ruff warnings
- API docs load at http://localhost:8000/docs
- Streamlit dashboard shows data at http://localhost:8501
- You can classify an expense through the web form
- You can view expenses in the list and delete one


## Common Issues and Solutions

| Issue | Solution |
|-------|----------|
| "ModuleNotFoundError: api" | Add `__init__.py` to api/ and subdirectories |
| CORS errors in browser | Check middleware is added before routers |
| "422 Unprocessable Entity" | Check request body matches Pydantic schema |
| "Connection refused" in Streamlit | Start FastAPI server first |
| Empty Plotly chart | Ensure data is in DataFrame format |
| Session closed errors | Use `yield` in get_db_session, not return |
| Test client not working | Use `app.dependency_overrides` correctly |


## Environment Variables

Ensure these are in your `.env`:

```bash
DATABASE_URL=sqlite:///expenses.db
OPENAI_API_KEY=your_key_here
API_BASE_URL=http://localhost:8000/api/v1
CORS_ORIGINS=http://localhost:8501
DEFAULT_USER_ID=12345
```
