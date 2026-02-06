"""Expense-related Pydantic schemas."""

from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field

from expenses_ai_agent.storage.models import Currency


class ExpenseClassifyRequest(BaseModel):
    """Request body for classifying a new expense."""

    description: str = Field(
        ...,
        min_length=3,
        max_length=500,
        description="Natural language expense description",
        examples=["Coffee at Starbucks $5.50", "Uber ride to airport 25 EUR"],
    )


class ExpenseClassifyResponse(BaseModel):
    """Response after classifying and persisting an expense."""

    id: int
    amount: Decimal
    currency: Currency
    description: str
    category: str
    confidence: float
    date: datetime
    comments: str | None = None

    model_config = {"from_attributes": True}


class ExpenseResponse(BaseModel):
    """Response for a single expense."""

    id: int
    amount: Decimal
    currency: Currency
    description: str | None
    category: str | None
    date: datetime
    created_at: datetime | None
    telegram_user_id: int | None

    model_config = {"from_attributes": True}


class ExpenseListResponse(BaseModel):
    """Paginated list of expenses."""

    items: list[ExpenseResponse]
    total: int
    page: int
    page_size: int
    pages: int
