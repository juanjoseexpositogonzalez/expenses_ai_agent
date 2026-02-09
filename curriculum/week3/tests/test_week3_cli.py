"""
Week 3 - Definition of Done: CLI Interface

Copy this file to your project's tests/unit/ directory.
Run: pytest tests/unit/test_week3_cli.py -v
All tests must pass to complete Week 3's CLI milestone.

These tests verify your implementation of:
- Typer CLI application
- classify command
- Rich output formatting
"""

from decimal import Decimal
from unittest.mock import MagicMock, patch

import pytest
from typer.testing import CliRunner


@pytest.fixture
def cli_runner():
    """Create a Typer CLI test runner."""
    return CliRunner()


@pytest.fixture
def mock_classification_response():
    """Create a mock classification response."""
    from expenses_ai_agent.llms.output import ExpenseCategorizationResponse
    from expenses_ai_agent.storage.models import Currency

    return ExpenseCategorizationResponse(
        category="Food",
        total_amount=Decimal("5.50"),
        currency=Currency.USD,
        confidence=0.95,
        cost=Decimal("0.001"),
        comments="Coffee purchase",
    )


class TestCLIApp:
    """Tests for the Typer CLI application."""

    def test_cli_app_exists(self):
        """CLI app should be importable."""
        from expenses_ai_agent.cli.cli import app

        assert app is not None

    def test_classify_command_exists(self, cli_runner):
        """classify command should be available."""
        from expenses_ai_agent.cli.cli import app

        result = cli_runner.invoke(app, ["classify", "--help"])
        assert result.exit_code == 0
        assert "classify" in result.output.lower() or "expense" in result.output.lower()

    def test_classify_requires_description(self, cli_runner):
        """classify command should require a description argument."""
        from expenses_ai_agent.cli.cli import app

        # Invoke without description
        result = cli_runner.invoke(app, ["classify"])

        # Should fail or show error about missing argument
        assert result.exit_code != 0 or "missing" in result.output.lower() or "required" in result.output.lower()

    def test_classify_with_mocked_service(self, cli_runner, mock_classification_response):
        """classify command should use ClassificationService."""
        from expenses_ai_agent.cli.cli import app

        with patch("expenses_ai_agent.cli.cli.ClassificationService") as mock_service_cls:
            # Set up the mock
            mock_service = MagicMock()
            mock_result = MagicMock()
            mock_result.response = mock_classification_response
            mock_result.persisted = False
            mock_service.classify.return_value = mock_result
            mock_service_cls.return_value = mock_service

            with patch("expenses_ai_agent.cli.cli.OpenAIAssistant"):
                result = cli_runner.invoke(app, ["classify", "Coffee at Starbucks $5.50"])

                # Should complete without error (exit code 0)
                # or show the classification result
                assert result.exit_code == 0 or "Food" in result.output

    def test_classify_db_option_exists(self, cli_runner):
        """classify command should have --db option."""
        from expenses_ai_agent.cli.cli import app

        result = cli_runner.invoke(app, ["classify", "--help"])

        assert "--db" in result.output or "database" in result.output.lower()

    def test_cli_outputs_category_info(self, cli_runner, mock_classification_response):
        """CLI output should include classification results."""
        from expenses_ai_agent.cli.cli import app

        with patch("expenses_ai_agent.cli.cli.ClassificationService") as mock_service_cls:
            mock_service = MagicMock()
            mock_result = MagicMock()
            mock_result.response = mock_classification_response
            mock_result.persisted = False
            mock_service.classify.return_value = mock_result
            mock_service_cls.return_value = mock_service

            with patch("expenses_ai_agent.cli.cli.OpenAIAssistant"):
                result = cli_runner.invoke(app, ["classify", "Test expense"])

                # Output should contain classification info
                output = result.output
                # Should show category, amount, or confidence somewhere
                assert (
                    "Food" in output or
                    "5.50" in output or
                    "Category" in output or
                    "classification" in output.lower()
                )
