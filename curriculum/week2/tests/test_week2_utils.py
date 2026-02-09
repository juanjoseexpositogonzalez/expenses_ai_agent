"""
Week 2 - Definition of Done: Utility Functions

Copy this file to your project's tests/unit/ directory.
Run: pytest tests/unit/test_week2_utils.py -v
All tests must pass to complete Week 2's utilities milestone.

These tests verify your implementation of:
- Currency conversion utility
- Date formatting utility
- Tool schema definitions
"""

from datetime import datetime, timezone
from decimal import Decimal
from unittest.mock import MagicMock, patch

import pytest


class TestCurrencyConversion:
    """Tests for the currency conversion utility."""

    def test_convert_currency_function_exists(self):
        """convert_currency function should exist."""
        from expenses_ai_agent.utils.currency import convert_currency

        assert callable(convert_currency)

    def test_convert_currency_returns_decimal(self):
        """Currency conversion should return a Decimal value."""
        from expenses_ai_agent.utils.currency import convert_currency

        # Mock the API call for unit testing
        with patch("expenses_ai_agent.utils.currency.requests.get") as mock_get:
            mock_response = MagicMock()
            mock_response.json.return_value = {
                "result": "success",
                "conversion_rate": 1.1,
            }
            mock_response.raise_for_status = MagicMock()
            mock_get.return_value = mock_response

            result = convert_currency(Decimal("100"), "EUR", "USD")

            assert isinstance(result, Decimal)

    def test_convert_currency_same_currency(self):
        """Converting to the same currency should return the original amount."""
        from expenses_ai_agent.utils.currency import convert_currency

        # No API call needed for same currency
        result = convert_currency(Decimal("50.00"), "EUR", "EUR")

        assert result == Decimal("50.00")

    def test_convert_currency_applies_rate(self):
        """Conversion should apply the exchange rate correctly."""
        from expenses_ai_agent.utils.currency import convert_currency

        with patch("expenses_ai_agent.utils.currency.requests.get") as mock_get:
            mock_response = MagicMock()
            mock_response.json.return_value = {
                "result": "success",
                "conversion_rate": 1.5,  # 1 EUR = 1.5 USD
            }
            mock_response.raise_for_status = MagicMock()
            mock_get.return_value = mock_response

            result = convert_currency(Decimal("100"), "EUR", "USD")

            assert result == Decimal("150")


class TestDateFormatter:
    """Tests for the date formatting utility."""

    def test_format_datetime_function_exists(self):
        """format_datetime function should exist."""
        from expenses_ai_agent.utils.date_formatter import format_datetime

        assert callable(format_datetime)

    def test_format_datetime_returns_string(self):
        """Date formatting should return a string."""
        from expenses_ai_agent.utils.date_formatter import format_datetime

        dt = datetime(2024, 6, 15, 14, 30, 0, tzinfo=timezone.utc)
        result = format_datetime(dt)

        assert isinstance(result, str)

    def test_format_datetime_includes_date_components(self):
        """Formatted datetime should include readable date components."""
        from expenses_ai_agent.utils.date_formatter import format_datetime

        dt = datetime(2024, 6, 15, 14, 30, 0, tzinfo=timezone.utc)
        result = format_datetime(dt)

        # Should contain year, month, day in some format
        assert "2024" in result or "24" in result
        # Should contain some indication of June
        assert "Jun" in result or "06" in result or "6" in result

    def test_format_datetime_with_timezone(self):
        """Should support timezone conversion."""
        from expenses_ai_agent.utils.date_formatter import format_datetime

        dt = datetime(2024, 6, 15, 12, 0, 0, tzinfo=timezone.utc)

        # Format with specific timezone
        result = format_datetime(dt, timezone_str="Europe/Madrid")

        # Result should be a string (timezone handling may vary)
        assert isinstance(result, str)


class TestToolSchemas:
    """Tests for OpenAI-compatible tool schemas."""

    def test_currency_tool_schema_exists(self):
        """Currency conversion tool schema should be defined."""
        from expenses_ai_agent.tools.tools import CURRENCY_CONVERSION_TOOL

        assert isinstance(CURRENCY_CONVERSION_TOOL, dict)

    def test_currency_tool_has_function_type(self):
        """Tool schema should have type: function."""
        from expenses_ai_agent.tools.tools import CURRENCY_CONVERSION_TOOL

        assert CURRENCY_CONVERSION_TOOL.get("type") == "function"

    def test_currency_tool_has_required_structure(self):
        """Tool schema should follow OpenAI function calling format."""
        from expenses_ai_agent.tools.tools import CURRENCY_CONVERSION_TOOL

        assert "function" in CURRENCY_CONVERSION_TOOL
        func = CURRENCY_CONVERSION_TOOL["function"]

        assert "name" in func
        assert "description" in func
        assert "parameters" in func

        params = func["parameters"]
        assert "type" in params
        assert "properties" in params

    def test_datetime_tool_schema_exists(self):
        """Datetime formatter tool schema should be defined."""
        from expenses_ai_agent.tools.tools import DATETIME_FORMATTER_TOOL

        assert isinstance(DATETIME_FORMATTER_TOOL, dict)
        assert DATETIME_FORMATTER_TOOL.get("type") == "function"
