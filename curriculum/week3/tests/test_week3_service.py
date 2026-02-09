"""
Week 3 - Definition of Done: Classification Service

Copy this file to your project's tests/unit/ directory.
Run: pytest tests/unit/test_week3_service.py -v
All tests must pass to complete Week 3's service milestone.

These tests verify your implementation of:
- ClassificationService class
- ClassificationResult dataclass
- Integration with Assistant and repositories
"""

from datetime import datetime, timezone
from decimal import Decimal
from unittest.mock import MagicMock, Mock

import pytest


class TestClassificationResult:
    """Tests for the ClassificationResult dataclass."""

    def test_classification_result_has_response(self):
        """ClassificationResult should contain the LLM response."""
        from expenses_ai_agent.llms.output import ExpenseCategorizationResponse
        from expenses_ai_agent.services.classification import ClassificationResult
        from expenses_ai_agent.storage.models import Currency

        response = ExpenseCategorizationResponse(
            category="Food",
            total_amount=Decimal("10.00"),
            currency=Currency.EUR,
            confidence=0.9,
            cost=Decimal("0.001"),
        )

        result = ClassificationResult(response=response, persisted=False)

        assert result.response == response
        assert result.persisted is False

    def test_classification_result_tracks_persistence(self):
        """ClassificationResult should track whether expense was persisted."""
        from expenses_ai_agent.llms.output import ExpenseCategorizationResponse
        from expenses_ai_agent.services.classification import ClassificationResult
        from expenses_ai_agent.storage.models import Currency

        response = ExpenseCategorizationResponse(
            category="Transport",
            total_amount=Decimal("25.00"),
            currency=Currency.USD,
            confidence=0.85,
            cost=Decimal("0.002"),
        )

        result_persisted = ClassificationResult(response=response, persisted=True)
        result_not_persisted = ClassificationResult(response=response, persisted=False)

        assert result_persisted.persisted is True
        assert result_not_persisted.persisted is False


class TestClassificationService:
    """Tests for the ClassificationService class."""

    @pytest.fixture
    def mock_assistant(self):
        """Create a mock assistant for testing."""
        from expenses_ai_agent.llms.output import ExpenseCategorizationResponse
        from expenses_ai_agent.storage.models import Currency

        assistant = MagicMock()
        assistant.completion.return_value = ExpenseCategorizationResponse(
            category="Food",
            total_amount=Decimal("5.50"),
            currency=Currency.USD,
            confidence=0.95,
            cost=Decimal("0.001"),
        )
        return assistant

    @pytest.fixture
    def mock_category_repo(self):
        """Create a mock category repository."""
        from expenses_ai_agent.storage.models import ExpenseCategory

        repo = MagicMock()
        repo.get.return_value = ExpenseCategory(id=1, name="Food")
        return repo

    @pytest.fixture
    def mock_expense_repo(self):
        """Create a mock expense repository."""
        repo = MagicMock()
        return repo

    def test_service_initialization(self, mock_assistant):
        """ClassificationService should accept an assistant."""
        from expenses_ai_agent.services.classification import ClassificationService

        service = ClassificationService(assistant=mock_assistant)

        assert service.assistant == mock_assistant

    def test_classify_calls_assistant(self, mock_assistant):
        """classify() should call the assistant's completion method."""
        from expenses_ai_agent.services.classification import ClassificationService

        service = ClassificationService(assistant=mock_assistant)
        result = service.classify("Coffee at Starbucks $5.50")

        mock_assistant.completion.assert_called_once()
        assert result.response.category == "Food"
        assert result.response.total_amount == Decimal("5.50")

    def test_classify_without_persistence(self, mock_assistant):
        """classify() without persist flag should not save to database."""
        from expenses_ai_agent.services.classification import ClassificationService

        service = ClassificationService(assistant=mock_assistant)
        result = service.classify("Test expense", persist=False)

        assert result.persisted is False

    def test_classify_with_persistence(
        self, mock_assistant, mock_category_repo, mock_expense_repo
    ):
        """classify() with persist=True should save to database."""
        from expenses_ai_agent.services.classification import ClassificationService

        service = ClassificationService(
            assistant=mock_assistant,
            category_repo=mock_category_repo,
            expense_repo=mock_expense_repo,
        )

        result = service.classify("Coffee $5.50", persist=True)

        assert result.persisted is True
        mock_expense_repo.add.assert_called_once()

    def test_persist_with_category_override(
        self, mock_assistant, mock_category_repo, mock_expense_repo
    ):
        """persist_with_category() should allow manual category override (HITL)."""
        from expenses_ai_agent.llms.output import ExpenseCategorizationResponse
        from expenses_ai_agent.services.classification import ClassificationService
        from expenses_ai_agent.storage.models import Currency

        service = ClassificationService(
            assistant=mock_assistant,
            category_repo=mock_category_repo,
            expense_repo=mock_expense_repo,
        )

        response = ExpenseCategorizationResponse(
            category="Food",  # Original classification
            total_amount=Decimal("10.00"),
            currency=Currency.EUR,
            confidence=0.6,  # Low confidence
            cost=Decimal("0.001"),
        )

        # User overrides to "Entertainment"
        service.persist_with_category(
            expense_description="Movie snacks",
            category_name="Entertainment",
            response=response,
        )

        # Should have called expense_repo.add with the overridden category
        mock_expense_repo.add.assert_called_once()

    def test_service_builds_correct_messages(self, mock_assistant):
        """Service should build messages with system and user prompts."""
        from expenses_ai_agent.services.classification import ClassificationService

        service = ClassificationService(assistant=mock_assistant)
        service.classify("Test expense")

        # Check the messages passed to completion
        call_args = mock_assistant.completion.call_args
        messages = call_args[0][0]  # First positional argument

        assert len(messages) >= 2
        assert messages[0]["role"] == "system"
        assert messages[1]["role"] == "user"
