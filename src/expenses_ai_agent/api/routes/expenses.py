"""Expense endpoints."""

import logging
import math

from fastapi import APIRouter, HTTPException, status

from expenses_ai_agent.api.deps import (
    ClassificationServiceDep,
    ExpenseRepoDep,
    UserIdDep,
)
from expenses_ai_agent.api.schemas.expense import (
    ExpenseClassifyRequest,
    ExpenseClassifyResponse,
    ExpenseListResponse,
    ExpenseResponse,
)
from expenses_ai_agent.services.preprocessing import InputPreprocessor
from expenses_ai_agent.storage.exceptions import ExpenseNotFoundError

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/expenses", tags=["expenses"])

preprocessor = InputPreprocessor()


@router.get("/", response_model=ExpenseListResponse)
def list_expenses(
    expense_repo: ExpenseRepoDep,
    user_id: UserIdDep,
    page: int = 1,
    page_size: int = 20,
) -> ExpenseListResponse:
    """List user expenses with pagination.

    Args:
        expense_repo: Expense repository dependency.
        user_id: User ID from header.
        page: Page number (1-indexed).
        page_size: Number of items per page.

    Returns:
        Paginated list of expenses.
    """
    all_expenses = expense_repo.list_by_user(user_id)

    # Calculate pagination
    total = len(all_expenses)
    pages = max(1, math.ceil(total / page_size))
    start = (page - 1) * page_size
    end = start + page_size

    items = [
        ExpenseResponse(
            id=e.id,  # type: ignore[arg-type]
            amount=e.amount,
            currency=e.currency,
            description=e.description,
            category=e.category.name if e.category else None,
            date=e.date,
            created_at=e.created_at,
            telegram_user_id=e.telegram_user_id,
        )
        for e in all_expenses[start:end]
    ]

    return ExpenseListResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        pages=pages,
    )


@router.post("/classify", response_model=ExpenseClassifyResponse, status_code=201)
def classify_expense(
    request: ExpenseClassifyRequest,
    service: ClassificationServiceDep,
    user_id: UserIdDep,
) -> ExpenseClassifyResponse:
    """Classify and persist a new expense.

    Args:
        request: Expense description.
        service: Classification service dependency.
        user_id: User ID from header.

    Returns:
        Classified and persisted expense.

    Raises:
        HTTPException: If input is invalid or classification fails.
    """
    # Preprocess input
    result = preprocessor.preprocess(request.description)
    if not result.is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"errors": result.validation_errors},
        )

    # Classify and persist
    try:
        classification = service.classify(
            expense_description=result.cleaned_text,
            persist=True,
            telegram_user_id=user_id,
        )
    except Exception as e:
        logger.exception("Classification failed")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Classification failed: {e!s}",
        ) from e

    resp = classification.response
    expense = classification.expense

    return ExpenseClassifyResponse(
        id=expense.id,  # type: ignore[arg-type]
        amount=resp.total_amount,
        currency=resp.currency,
        description=result.cleaned_text,
        category=resp.category,
        confidence=resp.confidence,
        date=expense.date,  # type: ignore[arg-type]
        comments=resp.comments,
    )


@router.get("/{expense_id}", response_model=ExpenseResponse)
def get_expense(
    expense_id: int,
    expense_repo: ExpenseRepoDep,
    user_id: UserIdDep,
) -> ExpenseResponse:
    """Get a single expense by ID.

    Args:
        expense_id: The expense ID.
        expense_repo: Expense repository dependency.
        user_id: User ID from header.

    Returns:
        The expense if found and owned by user.

    Raises:
        HTTPException: If expense not found or not owned by user.
    """
    try:
        expense = expense_repo.get(expense_id)
    except ExpenseNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Expense {expense_id} not found",
        ) from e

    # Check ownership
    if expense.telegram_user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Expense {expense_id} not found",
        )

    return ExpenseResponse(
        id=expense.id,  # type: ignore[arg-type]
        amount=expense.amount,
        currency=expense.currency,
        description=expense.description,
        category=expense.category.name if expense.category else None,
        date=expense.date,
        created_at=expense.created_at,
        telegram_user_id=expense.telegram_user_id,
    )


@router.delete("/{expense_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_expense(
    expense_id: int,
    expense_repo: ExpenseRepoDep,
    user_id: UserIdDep,
) -> None:
    """Delete an expense.

    Args:
        expense_id: The expense ID to delete.
        expense_repo: Expense repository dependency.
        user_id: User ID from header.

    Raises:
        HTTPException: If expense not found or not owned by user.
    """
    try:
        expense = expense_repo.get(expense_id)
    except ExpenseNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Expense {expense_id} not found",
        ) from e

    # Check ownership
    if expense.telegram_user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Expense {expense_id} not found",
        )

    expense_repo.delete(expense_id)
