# Week 4 Review: Bridging to Week 5

Before building the web interface, let's review the components from Week 4 that you'll use.


## What You Built in Week 4

### Input Preprocessing

```python
@dataclass
class PreprocessingResult:
    text: str
    is_valid: bool
    warnings: list[str]
    error: str | None = None

class InputPreprocessor:
    def preprocess(self, text: str) -> PreprocessingResult:
        # Validate, sanitize, normalize
        ...
```

### Human-in-the-Loop Pattern

```python
# 1. Classify with AI
result = service.classify("Coffee $5")  # -> Food, 0.95 confidence

# 2. User confirms or overrides
service.persist_with_category(
    expense_description="Coffee $5",
    category_name="Food",  # User's choice
    response=result.response,
)
```

### User Preferences

```python
class UserPreference(SQLModel, table=True):
    telegram_user_id: int
    preferred_currency: Currency
```


## How Week 5 Uses Week 4

The web API provides the same classification functionality through HTTP:

```python
# Week 4: Telegram bot
async def handle_expense_text(update, context):
    result = service.classify(text, persist=True)
    # Show inline keyboard for HITL...

# Week 5: FastAPI endpoint
@router.post("/classify")
def classify_expense(
    request: ExpenseClassifyRequest,
    service: ClassificationService = Depends(get_classification_service),
):
    result = service.classify(request.description, persist=True)
    return ExpenseClassifyResponse(...)
```

The same ClassificationService works for both interfaces.


## New This Week: HTTP Layer

Week 5 adds HTTP communication between frontend and backend:

```
Streamlit Dashboard
        |
        | HTTP Request: POST /api/v1/expenses/classify
        | Body: {"description": "Coffee $5.50"}
        |
        v
FastAPI Backend
        |
        +-- ClassificationService (Week 3)
        |
        +-- InputPreprocessor (Week 4)
        |
        +-- DB Repositories (Week 3)
        |
        v
HTTP Response: 201 Created
Body: {"id": 1, "category": "Food", ...}
```


## Key Differences: Bot vs API

| Aspect | Telegram Bot (Week 4) | REST API (Week 5) |
|--------|----------------------|-------------------|
| Protocol | Telegram Bot API | HTTP/REST |
| User ID | `update.effective_user.id` | `X-User-ID` header |
| HITL | Inline keyboard callbacks | Client-side confirmation |
| State | ConversationHandler | Stateless (each request independent) |
| Response | Edit message | JSON response |


## Prepare for Week 5

Make sure you:

- [ ] Have all 28 Week 4 tests passing
- [ ] Understand ClassificationService and persist_with_category()
- [ ] Can explain the Repository pattern
- [ ] Have `httpx`, `fastapi`, `streamlit`, and `plotly` in dependencies

The web interface will expose the same functionality through HTTP.
