# Pydantic Schemas for API Contracts

Pydantic models define the contract between API clients and your backend. This lesson covers designing request and response schemas for type-safe, validated data exchange.


## Why Schemas Exist

Without schemas, you handle raw dictionaries and hope for the best:

```python
@router.post("/classify")
def classify_expense(request: dict):
    description = request.get("description")  # Might be None
    if not description:
        raise HTTPException(400, "description required")
    if not isinstance(description, str):
        raise HTTPException(400, "description must be string")
    if len(description) < 3:
        raise HTTPException(400, "description too short")
    # ... more validation
```

With Pydantic schemas, validation is declarative:

```python
from pydantic import BaseModel, Field

class ExpenseClassifyRequest(BaseModel):
    description: str = Field(..., min_length=3, max_length=500)

@router.post("/classify")
def classify_expense(request: ExpenseClassifyRequest):
    # Validation already done! request.description is a valid string
    ...
```

FastAPI automatically returns 422 Unprocessable Entity with detailed error messages if validation fails.


## Request Schemas

Request schemas define what clients must send:

```python
from pydantic import BaseModel, Field

class ExpenseClassifyRequest(BaseModel):
    """Request body for expense classification."""
    description: str = Field(
        ...,  # Required field
        min_length=3,
        max_length=500,
        examples=["Coffee at Starbucks $5.50"],
    )
```

**Key points:**
- `...` (Ellipsis) marks required fields
- `Field()` adds validation constraints and metadata
- `examples` appear in OpenAPI documentation


## Response Schemas

Response schemas define what the API returns:

```python
from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel

class ExpenseClassifyResponse(BaseModel):
    """Response body after expense classification."""
    id: int
    category: str
    amount: Decimal
    currency: str
    confidence: float
    created_at: datetime

    model_config = {"from_attributes": True}
```

The `from_attributes = True` config (formerly `orm_mode`) allows creating the response directly from SQLModel objects:

```python
expense = repo.get(expense_id)  # SQLModel object
return ExpenseClassifyResponse.model_validate(expense)  # Converts to schema
```


## Pagination Schema

For list endpoints, include pagination metadata:

```python
class ExpenseResponse(BaseModel):
    """Single expense in a list."""
    id: int
    amount: Decimal
    currency: str
    category: str
    description: str | None
    created_at: datetime

    model_config = {"from_attributes": True}

class ExpenseListResponse(BaseModel):
    """Paginated list of expenses."""
    items: list[ExpenseResponse]
    total: int
    page: int
    page_size: int
```

Usage in route:

```python
@router.get("/", response_model=ExpenseListResponse)
def list_expenses(
    page: int = 1,
    page_size: int = 20,
    expense_repo: ExpenseRepository = Depends(get_expense_repo),
    user_id: int = Depends(get_user_id),
):
    expenses = expense_repo.list_by_user(user_id)
    # Apply pagination...
    return ExpenseListResponse(
        items=expenses[start:end],
        total=len(expenses),
        page=page,
        page_size=page_size,
    )
```


## Analytics Schemas

For aggregated data, create dedicated schemas:

```python
class CategoryTotal(BaseModel):
    """Spending total for a category."""
    category: str
    total: Decimal

class MonthlyTotal(BaseModel):
    """Spending total for a month."""
    month: str  # "2025-01"
    total: Decimal

class AnalyticsSummary(BaseModel):
    """Dashboard analytics data."""
    category_totals: list[CategoryTotal]
    monthly_totals: list[MonthlyTotal]
```


## Schema Organization

Organize schemas by resource:

```
api/schemas/
    __init__.py
    expense.py       # ExpenseClassifyRequest, ExpenseResponse, etc.
    analytics.py     # CategoryTotal, MonthlyTotal, AnalyticsSummary
```

Export from `__init__.py`:

```python
from .expense import (
    ExpenseClassifyRequest,
    ExpenseClassifyResponse,
    ExpenseResponse,
    ExpenseListResponse,
)
from .analytics import AnalyticsSummary, CategoryTotal, MonthlyTotal
```


## Validation Examples

Pydantic provides many validation options:

```python
from pydantic import BaseModel, Field, field_validator

class ExpenseClassifyRequest(BaseModel):
    description: str = Field(..., min_length=3, max_length=500)

    @field_validator("description")
    @classmethod
    def description_not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("description cannot be empty or whitespace")
        return v.strip()
```


## Python Comparison

| Raw dict handling | Pydantic schema |
|-------------------|-----------------|
| `request.get("field")` | `request.field` (type-safe) |
| Manual type checking | Automatic type coercion |
| Manual error messages | Automatic 422 responses |
| No documentation | OpenAPI examples |
| Runtime surprises | Caught at validation |


## Schemas in Our Project

| Schema | File | Purpose |
|--------|------|---------|
| `ExpenseClassifyRequest` | `schemas/expense.py` | Classification input |
| `ExpenseClassifyResponse` | `schemas/expense.py` | Classification result |
| `ExpenseResponse` | `schemas/expense.py` | Single expense |
| `ExpenseListResponse` | `schemas/expense.py` | Paginated list |
| `AnalyticsSummary` | `schemas/analytics.py` | Dashboard data |


## Further Reading

- [Pydantic Documentation](https://docs.pydantic.dev/)
- [FastAPI Request Body](https://fastapi.tiangolo.com/tutorial/body/)
- [FastAPI Response Model](https://fastapi.tiangolo.com/tutorial/response-model/)
