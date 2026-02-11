# Welcome to Week 5: Web Interface with FastAPI and Streamlit

Welcome to Week 5! This week you will build a complete web interface for your expense classification agent. You will create a FastAPI REST API backend with dependency injection and Pydantic schemas, then connect a Streamlit dashboard frontend with Plotly visualizations. By the end of this week, users can view, classify, and analyze expenses through a web browser.


## What You'll Learn

Week 5 introduces these essential patterns:

- **FastAPI Fundamentals** - Build REST APIs with automatic OpenAPI documentation
- **Dependency Injection** - Clean, testable code with FastAPI's Depends() system
- **Pydantic Schemas** - Type-safe request/response validation
- **Streamlit Dashboards** - Rapid prototyping of data applications
- **Plotly Visualizations** - Interactive charts for expense analytics


## The Mental Model Shift

**Week 4 mindset:** "The bot is a conversation - users interact through messages and buttons"

**Week 5 mindset:** "The API is a contract - clients request resources, the server responds with structured data"

Think of the Telegram bot as a phone call: conversational, back-and-forth, stateful. The REST API is more like a mail system. Clients send requests with specific formats, the server processes them independently, and responds with structured data. There is no ongoing conversation - each request stands alone. The Streamlit dashboard is the friendly post office counter that makes it easy for humans to send and receive this mail.


## What Success Looks Like

By the end of this week, you have two running services:

**FastAPI Backend (port 8000):**
```bash
curl -X POST "http://localhost:8000/api/v1/expenses/classify" \
  -H "Content-Type: application/json" \
  -H "X-User-ID: 12345" \
  -d '{"description": "Coffee at Starbucks $5.50"}'
```

Response:
```json
{
  "id": 1,
  "category": "Food",
  "amount": "5.50",
  "currency": "USD",
  "confidence": 0.95,
  "created_at": "2025-02-10T10:30:00Z"
}
```

**Streamlit Dashboard (port 8501):**
- Dashboard view with category totals bar chart and monthly spending line chart
- Expense list with pagination and delete functionality
- Add expense form with AI classification


## Why REST APIs for AI Agents?

The CLI and Telegram bot work well for individual users, but scaling requires a different approach:

1. **Multi-client Support** - Web apps, mobile apps, third-party integrations all use the same API
2. **Stateless Scalability** - Each request is independent; add more servers easily
3. **Documentation** - OpenAPI/Swagger provides interactive API documentation
4. **Testing** - HTTP endpoints are easy to test with standard tools
5. **Separation of Concerns** - Backend logic stays separate from frontend presentation


## Why Streamlit for Prototypes?

Streamlit turns Python scripts into web apps in minutes:

```python
import streamlit as st

st.title("Expense Dashboard")

if st.button("Classify"):
    result = api_client.classify(description)
    st.success(f"Classified as {result.category}")
```

For production dashboards, you might use React or Vue. But for rapid prototyping, internal tools, and data applications, Streamlit gets you from zero to deployed faster than any alternative.


## Architecture: Week 5's Place

```
+------------------------------------------------------------------+
|                    WEEK 5: WEB INTERFACE                          |
+------------------------------------------------------------------+

                    +-------------------+
                    |  Streamlit App    |
                    |  (port 8501)      |
                    +-------------------+
                              |
                              | HTTP (httpx)
                              v
                    +-------------------+
                    |  FastAPI Backend  |
                    |  (port 8000)      |
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
    | ClassificationSvc |  <-- Week 3 (reused)
    +-------------------+
          |
          v
    +-------------------+
    | DB Repositories   |  <-- Week 3 (reused)
    +-------------------+
```


## Technical Milestones

By the end of Week 5, you'll have:

- [ ] FastAPI app with CORS middleware and lifespan handler
- [ ] Dependency injection in `deps.py` (session, repos, services, user ID)
- [ ] Pydantic schemas for request/response validation
- [ ] Expense routes: GET list, POST classify, GET by ID, DELETE
- [ ] Categories route: GET list
- [ ] Analytics route: GET summary with category and monthly totals
- [ ] Health check endpoint
- [ ] Streamlit app with sidebar navigation
- [ ] ExpenseAPIClient for HTTP communication
- [ ] Dashboard view with Plotly charts
- [ ] Expense list view with pagination
- [ ] Add expense form with classification
- [ ] All 24 tests passing


## Ready?

This week adds the web layer to your expense agent. The ClassificationService and repositories from Week 3 will be reused - you are adding new interfaces, not rewriting core logic. The Telegram bot from Week 4 continues to work alongside the web interface.

Let's start by reviewing the Week 4 components you'll build upon.
