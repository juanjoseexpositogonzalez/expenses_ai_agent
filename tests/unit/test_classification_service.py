from decimal import Decimal
from unittest.mock import Mock

import pytest

from expenses_ai_agent.llms.output import ExpenseCategorizationResponse
from expenses_ai_agent.services.classification import (
    ClassificationResult,
    ClassificationService,
)
from expenses_ai_agent.storage.exceptions import CategoryNotFoundError
from expenses_ai_agent.storage.models import Currency, ExpenseCategory


# ------------------------------------------------------------------
# Fixtures
# ------------------------------------------------------------------


def _make_response(
    category: str = "Food & Dining",
    amount: Decimal = Decimal("5.50"),
    currency: Currency = Currency.USD,
    confidence: float = 0.95,
) -> ExpenseCategorizationResponse:
    return ExpenseCategorizationResponse(
        category=category,
        total_amount=amount,
        currency=currency,
        confidence=confidence,
        cost=Decimal("0.0001"),
        comments="test",
    )


@pytest.fixture()
def mock_assistant() -> Mock:
    assistant = Mock()
    assistant.completion.return_value = _make_response()
    return assistant


@pytest.fixture()
def mock_category_repo() -> Mock:
    return Mock()


@pytest.fixture()
def mock_expense_repo() -> Mock:
    return Mock()


# ------------------------------------------------------------------
# classify() - without persistence
# ------------------------------------------------------------------


def test_classify_returns_result(mock_assistant: Mock) -> None:
    service = ClassificationService(assistant=mock_assistant)
    result = service.classify("Coffee at Starbucks $5.50", persist=False)

    assert isinstance(result, ClassificationResult)
    assert result.response.category == "Food & Dining"
    assert result.response.total_amount == Decimal("5.50")
    assert result.is_persisted is False
    assert result.expense is None
    assert result.category is None


def test_classify_calls_assistant(mock_assistant: Mock) -> None:
    service = ClassificationService(assistant=mock_assistant)
    service.classify("Coffee $5", persist=False)

    mock_assistant.completion.assert_called_once()
    messages = mock_assistant.completion.call_args[0][0]
    assert messages[0]["role"] == "system"
    assert messages[1]["role"] == "user"
    assert "Coffee $5" in messages[1]["content"]


# ------------------------------------------------------------------
# classify() - with persistence
# ------------------------------------------------------------------


def test_classify_with_persist_creates_category_and_expense(
    mock_assistant: Mock,
    mock_category_repo: Mock,
    mock_expense_repo: Mock,
) -> None:
    # Category does not exist yet
    mock_category_repo.get.side_effect = CategoryNotFoundError()

    service = ClassificationService(
        assistant=mock_assistant,
        category_repo=mock_category_repo,
        expense_repo=mock_expense_repo,
    )
    result = service.classify("Coffee $5.50", persist=True)

    assert result.is_persisted is True
    mock_category_repo.add.assert_called_once()
    mock_expense_repo.add.assert_called_once()

    expense_arg = mock_expense_repo.add.call_args[0][0]
    assert expense_arg.amount == Decimal("5.50")
    assert expense_arg.currency == Currency.USD


def test_classify_reuses_existing_category(
    mock_assistant: Mock,
    mock_category_repo: Mock,
    mock_expense_repo: Mock,
) -> None:
    existing = ExpenseCategory(id=1, name="Food & Dining")
    mock_category_repo.get.return_value = existing

    service = ClassificationService(
        assistant=mock_assistant,
        category_repo=mock_category_repo,
        expense_repo=mock_expense_repo,
    )
    result = service.classify("Coffee $5.50", persist=True)

    assert result.is_persisted is True
    assert result.category is existing
    mock_category_repo.add.assert_not_called()


# ------------------------------------------------------------------
# classify() - error cases
# ------------------------------------------------------------------


def test_classify_empty_description_raises(mock_assistant: Mock) -> None:
    service = ClassificationService(assistant=mock_assistant)

    with pytest.raises(ValueError, match="cannot be empty"):
        service.classify("   ", persist=False)


def test_classify_persist_without_repos_raises(mock_assistant: Mock) -> None:
    service = ClassificationService(assistant=mock_assistant)

    with pytest.raises(RuntimeError, match="Cannot persist"):
        service.classify("Coffee $5", persist=True)


def test_classify_persist_without_expense_repo_raises(
    mock_assistant: Mock, mock_category_repo: Mock
) -> None:
    service = ClassificationService(
        assistant=mock_assistant, category_repo=mock_category_repo
    )

    with pytest.raises(RuntimeError, match="Cannot persist"):
        service.classify("Coffee $5", persist=True)


# ------------------------------------------------------------------
# persist_with_category() - HITL override
# ------------------------------------------------------------------


def test_persist_with_same_category(
    mock_assistant: Mock,
    mock_category_repo: Mock,
    mock_expense_repo: Mock,
) -> None:
    original = _make_response(category="Food & Dining")
    mock_category_repo.get.return_value = ExpenseCategory(id=1, name="Food & Dining")

    service = ClassificationService(
        assistant=mock_assistant,
        category_repo=mock_category_repo,
        expense_repo=mock_expense_repo,
    )
    result = service.persist_with_category(
        expense_description="Coffee $5.50",
        llm_response=original,
        selected_category="Food & Dining",
    )

    assert result.is_persisted is True
    assert result.response.category == "Food & Dining"
    # Original confidence preserved when no override
    assert result.response.confidence == 0.95


def test_persist_with_override_category(
    mock_assistant: Mock,
    mock_category_repo: Mock,
    mock_expense_repo: Mock,
) -> None:
    original = _make_response(category="Food & Dining")
    mock_category_repo.get.side_effect = CategoryNotFoundError()

    service = ClassificationService(
        assistant=mock_assistant,
        category_repo=mock_category_repo,
        expense_repo=mock_expense_repo,
    )
    result = service.persist_with_category(
        expense_description="Coffee $5.50",
        llm_response=original,
        selected_category="Transportation",
    )

    assert result.is_persisted is True
    assert result.response.category == "Transportation"
    assert result.response.confidence == 1.0
    assert "User override" in (result.response.comments or "")


def test_persist_with_category_without_repos_raises(
    mock_assistant: Mock,
) -> None:
    service = ClassificationService(assistant=mock_assistant)

    with pytest.raises(RuntimeError, match="Cannot persist"):
        service.persist_with_category(
            expense_description="Coffee $5",
            llm_response=_make_response(),
            selected_category="Food & Dining",
        )
