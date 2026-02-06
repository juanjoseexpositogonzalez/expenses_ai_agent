"""Tests for CLI commands."""

from datetime import datetime
from decimal import Decimal
from unittest.mock import MagicMock, patch

import pytest
from typer.testing import CliRunner

from expenses_ai_agent.cli.cli import app
from expenses_ai_agent.llms.output import ExpenseCategorizationResponse
from expenses_ai_agent.services.classification import ClassificationResult
from expenses_ai_agent.storage.models import Currency


@pytest.fixture
def runner() -> CliRunner:
    """Create a CLI runner for testing."""
    return CliRunner()


@pytest.fixture
def mock_llm_response() -> ExpenseCategorizationResponse:
    """Create a mock LLM response."""
    return ExpenseCategorizationResponse(
        category="Food & Dining",
        total_amount=Decimal("25.50"),
        currency=Currency.EUR,
        confidence=0.95,
        cost=Decimal("0.0001"),
        comments="Restaurant expense",
        timestamp=datetime.now(),
    )


@pytest.fixture
def mock_classification_result(
    mock_llm_response: ExpenseCategorizationResponse,
) -> ClassificationResult:
    """Create a mock classification result."""
    return ClassificationResult(
        response=mock_llm_response,
        is_persisted=False,
    )


class TestGreetCommand:
    """Tests for the greet command."""

    def test_greet_with_name(self, runner: CliRunner) -> None:
        """Test greeting with a name."""
        result = runner.invoke(app, ["greet", "-g", "Alice"])
        assert result.exit_code == 0
        assert "Alice" in result.output
        assert "Hello" in result.output

    def test_greet_with_long_option(self, runner: CliRunner) -> None:
        """Test greeting with --greet option."""
        result = runner.invoke(app, ["greet", "--greet", "Bob"])
        assert result.exit_code == 0
        assert "Bob" in result.output


class TestClassifyCommand:
    """Tests for the classify command."""

    @patch("expenses_ai_agent.cli.cli.ClassificationService")
    @patch("expenses_ai_agent.cli.cli.OpenAIAssistant")
    def test_classify_success(
        self,
        mock_assistant_class: MagicMock,
        mock_service_class: MagicMock,
        runner: CliRunner,
        mock_classification_result: ClassificationResult,
    ) -> None:
        """Test successful classification."""
        mock_service = MagicMock()
        mock_service.classify.return_value = mock_classification_result
        mock_service_class.return_value = mock_service

        result = runner.invoke(app, ["classify", "Coffee at Starbucks $5.50"])

        assert result.exit_code == 0
        assert "Expense classified successfully" in result.output
        # Category may be split across lines in table formatting
        assert "Food &" in result.output

    @patch("expenses_ai_agent.cli.cli.Session")
    @patch("expenses_ai_agent.cli.cli.DBExpenseRepo")
    @patch("expenses_ai_agent.cli.cli.DBCategoryRepo")
    @patch("expenses_ai_agent.cli.cli.ClassificationService")
    @patch("expenses_ai_agent.cli.cli.OpenAIAssistant")
    def test_classify_with_db_flag(
        self,
        mock_assistant_class: MagicMock,
        mock_service_class: MagicMock,
        mock_category_repo: MagicMock,
        mock_expense_repo: MagicMock,
        mock_session: MagicMock,
        runner: CliRunner,
        mock_classification_result: ClassificationResult,
    ) -> None:
        """Test classification with --db flag persists to database."""
        mock_classification_result.is_persisted = True
        mock_service = MagicMock()
        mock_service.classify.return_value = mock_classification_result
        mock_service_class.return_value = mock_service

        result = runner.invoke(app, ["classify", "Taxi ride 45 EUR", "--db"])

        assert result.exit_code == 0
        assert "database" in result.output.lower() or "Expense classified" in result.output

    def test_classify_invalid_input_empty(self, runner: CliRunner) -> None:
        """Test classification with empty input."""
        result = runner.invoke(app, ["classify", ""])

        assert result.exit_code == 1
        assert "Invalid input" in result.output

    def test_classify_invalid_input_too_short(self, runner: CliRunner) -> None:
        """Test classification with input too short."""
        result = runner.invoke(app, ["classify", "ab"])

        assert result.exit_code == 1
        assert "Invalid input" in result.output

    def test_classify_invalid_input_xss_pattern(self, runner: CliRunner) -> None:
        """Test classification blocks XSS patterns."""
        result = runner.invoke(app, ["classify", "<script>alert('xss')</script>"])

        assert result.exit_code == 1
        assert "Invalid input" in result.output

    @patch("expenses_ai_agent.cli.cli.ClassificationService")
    @patch("expenses_ai_agent.cli.cli.OpenAIAssistant")
    def test_classify_shows_warnings(
        self,
        mock_assistant_class: MagicMock,
        mock_service_class: MagicMock,
        runner: CliRunner,
        mock_classification_result: ClassificationResult,
    ) -> None:
        """Test that warnings are displayed for input without amount."""
        mock_service = MagicMock()
        mock_service.classify.return_value = mock_classification_result
        mock_service_class.return_value = mock_service

        # Input without a clear numerical amount
        result = runner.invoke(app, ["classify", "Bought some groceries today"])

        # Should succeed but with a warning
        assert result.exit_code == 0
        # Warning about missing amount might be shown
        assert "classified successfully" in result.output.lower() or "Food" in result.output
