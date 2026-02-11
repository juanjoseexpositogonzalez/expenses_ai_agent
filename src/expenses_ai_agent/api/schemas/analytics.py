"""Analytics-related Pydantic schemas."""

from decimal import Decimal

from pydantic import BaseModel


class MonthlyTotal(BaseModel):
    """Monthly expense total for charts."""

    month: str  # Format: "YYYY-MM"
    total: Decimal


class CategoryTotal(BaseModel):
    """Category expense total for charts."""

    category: str
    total: Decimal


class AnalyticsSummary(BaseModel):
    """Complete analytics summary for dashboard."""

    total_expenses: Decimal
    expense_count: int
    category_totals: list[CategoryTotal]
    monthly_totals: list[MonthlyTotal]
