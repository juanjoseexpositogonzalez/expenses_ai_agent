"""Analytics endpoints for dashboard charts."""

from decimal import Decimal

from fastapi import APIRouter

from expenses_ai_agent.api.deps import ExpenseRepoDep, UserIdDep
from expenses_ai_agent.api.schemas.analytics import (
    AnalyticsSummary,
    CategoryTotal,
    MonthlyTotal,
)

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("/summary", response_model=AnalyticsSummary)
def get_analytics_summary(
    expense_repo: ExpenseRepoDep,
    user_id: UserIdDep,
    months: int = 12,
) -> AnalyticsSummary:
    """Get analytics summary for dashboard charts.

    Args:
        expense_repo: Expense repository dependency.
        user_id: User ID from header.
        months: Number of months of data to include (default: 12).

    Returns:
        Summary with category and monthly totals.
    """
    # Get category totals
    category_data = expense_repo.get_category_totals(user_id)
    category_totals = [
        CategoryTotal(category=cat, total=total) for cat, total in category_data
    ]

    # Get monthly totals
    monthly_data = expense_repo.get_monthly_totals(user_id, months=months)
    monthly_totals = [
        MonthlyTotal(month=month, total=total) for month, total in monthly_data
    ]

    # Calculate totals
    total_expenses = sum((ct.total for ct in category_totals), Decimal("0"))
    expense_count = len(expense_repo.list_by_user(user_id))

    return AnalyticsSummary(
        total_expenses=total_expenses,
        expense_count=expense_count,
        category_totals=category_totals,
        monthly_totals=monthly_totals,
    )
