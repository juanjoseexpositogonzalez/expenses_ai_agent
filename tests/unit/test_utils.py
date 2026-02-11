"""Tests for utility modules: logging_config, date_formatter, and currency."""

import logging
from decimal import Decimal
from unittest.mock import MagicMock, patch

import pytest

from expenses_ai_agent.storage.models import Currency
from expenses_ai_agent.utils.date_formatter import format_datetime
from expenses_ai_agent.utils.logging_config import setup_logging


class TestSetupLogging:
    """Tests for setup_logging function."""

    def test_setup_logging_runs_without_error(self) -> None:
        """Test that setup_logging executes without raising exceptions."""
        # setup_logging configures basicConfig - doesn't override if already configured
        setup_logging()
        # Should not raise

    def test_setup_logging_accepts_custom_level(self) -> None:
        """Test that setup_logging accepts custom log level parameter."""
        # Verify function accepts the level parameter without error
        setup_logging(level=logging.DEBUG)
        setup_logging(level=logging.WARNING)
        setup_logging(level=logging.ERROR)
        # Should not raise

    def test_setup_logging_suppresses_http_libraries(self) -> None:
        """Test that HTTP library loggers are set to WARNING."""
        setup_logging()
        httpx_logger = logging.getLogger("httpx")
        httpcore_logger = logging.getLogger("httpcore")
        assert httpx_logger.level == logging.WARNING
        assert httpcore_logger.level == logging.WARNING

    def test_log_format_constants_defined(self) -> None:
        """Test that log format constants are properly defined."""
        from expenses_ai_agent.utils.logging_config import DATE_FORMAT, LOG_FORMAT

        assert "%(asctime)s" in LOG_FORMAT
        assert "%(name)s" in LOG_FORMAT
        assert "%(levelname)s" in LOG_FORMAT
        assert "%Y-%m-%d" in DATE_FORMAT


class TestFormatDatetime:
    """Tests for format_datetime function."""

    def test_format_datetime_with_utc_timezone(self) -> None:
        """Test formatting a UTC datetime to Europe/Madrid."""
        # UTC time -> Europe/Madrid (UTC+1 in winter, UTC+2 in summer)
        result = format_datetime("2024-01-15T10:30:00Z", output_tz="Europe/Madrid")
        # Z means UTC, Europe/Madrid is UTC+1 in January
        assert result == "15/01/2024 11:30"

    def test_format_datetime_with_offset(self) -> None:
        """Test formatting a datetime with explicit timezone offset."""
        result = format_datetime("2024-06-15T14:00:00+02:00", output_tz="UTC")
        # +02:00 converted to UTC
        assert result == "15/06/2024 12:00"

    def test_format_datetime_without_timezone_assumes_output_tz(self) -> None:
        """Test that datetime without timezone assumes output_tz."""
        result = format_datetime("2024-03-15T09:00:00", output_tz="Europe/Madrid")
        # No timezone info, assumes Europe/Madrid
        assert result == "15/03/2024 09:00"

    def test_format_datetime_different_output_timezone(self) -> None:
        """Test converting to different output timezone."""
        result = format_datetime("2024-07-20T18:00:00Z", output_tz="America/New_York")
        # UTC to America/New_York (UTC-4 in summer)
        assert result == "20/07/2024 14:00"

    def test_format_datetime_with_naive_datetime_and_tz(self) -> None:
        """Test formatting naive datetime assumes output timezone."""
        # This tests the ValueError exception path and naive datetime handling
        result = format_datetime("2024-03-15 09:00:00", output_tz="Europe/Madrid")
        # No timezone, should assume Europe/Madrid
        assert result == "15/03/2024 09:00"

    def test_format_datetime_already_in_target_timezone(self) -> None:
        """Test datetime already in target timezone."""
        result = format_datetime("2024-06-15T14:00:00+02:00", output_tz="Europe/Madrid")
        # Already in Europe/Madrid summer time
        assert result == "15/06/2024 14:00"

    def test_format_datetime_z_suffix_conversion(self) -> None:
        """Test Z suffix is properly converted to +00:00."""
        result = format_datetime("2024-12-25T12:00:00Z", output_tz="UTC")
        assert result == "25/12/2024 12:00"

    def test_format_datetime_naive_datetime_no_tz(self) -> None:
        """Test naive datetime without explicit timezone falls back to output_tz."""
        # This specifically tests the ValueError path and naive datetime handling
        result = format_datetime("2024-11-10T08:30:00", output_tz="America/Los_Angeles")
        # Should assume America/Los_Angeles timezone
        assert result == "10/11/2024 08:30"

    def test_format_datetime_with_microseconds(self) -> None:
        """Test datetime with microseconds is handled correctly."""
        result = format_datetime("2024-05-20T15:45:30.123456Z", output_tz="Europe/London")
        # Z is UTC, Europe/London in May is UTC+1 (BST)
        assert result == "20/05/2024 16:45"

    def test_format_datetime_negative_offset(self) -> None:
        """Test datetime with negative timezone offset."""
        result = format_datetime("2024-08-01T10:00:00-05:00", output_tz="UTC")
        # -05:00 to UTC means add 5 hours
        assert result == "01/08/2024 15:00"

    def test_format_datetime_tokyo_timezone(self) -> None:
        """Test conversion to Asia/Tokyo timezone."""
        result = format_datetime("2024-01-01T00:00:00Z", output_tz="Asia/Tokyo")
        # UTC to Asia/Tokyo is +9 hours
        assert result == "01/01/2024 09:00"


class TestConvertCurrency:
    """Tests for convert_currency function."""

    @patch("expenses_ai_agent.utils.currency.EXCHANGE_RATE_API_KEY", "")
    def test_convert_currency_no_api_key_raises_error(self) -> None:
        """Test that missing API key raises ValueError."""
        # Need to reimport to pick up the patched value
        from expenses_ai_agent.utils import currency

        # Patch the module-level constant directly
        with patch.object(currency, "EXCHANGE_RATE_API_KEY", ""):
            with pytest.raises(ValueError, match="Exchange rate API key is not set"):
                currency.convert_currency(
                    amount=Decimal("100"),
                    from_currency=Currency.USD,
                    to_currency=Currency.EUR,
                )

    @patch("expenses_ai_agent.utils.currency.requests.get")
    @patch("expenses_ai_agent.utils.currency.EXCHANGE_RATE_API_KEY", "test_key")
    def test_convert_currency_success(self, mock_get: MagicMock) -> None:
        """Test successful currency conversion with mocked API."""
        from expenses_ai_agent.utils import currency

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "result": "success",
            "conversion_result": 85.50,
        }
        mock_get.return_value = mock_response

        with patch.object(currency, "EXCHANGE_RATE_API_KEY", "test_key"):
            result = currency.convert_currency(
                amount=Decimal("100"),
                from_currency=Currency.USD,
                to_currency=Currency.EUR,
            )

        assert result == Decimal("85.50")
        mock_get.assert_called_once()

    @patch("expenses_ai_agent.utils.currency.requests.get")
    @patch("expenses_ai_agent.utils.currency.EXCHANGE_RATE_API_KEY", "test_key")
    def test_convert_currency_api_failure(self, mock_get: MagicMock) -> None:
        """Test handling of API failure response."""
        from expenses_ai_agent.utils import currency

        mock_response = MagicMock()
        mock_response.status_code = 400
        mock_response.json.return_value = {
            "result": "error",
            "error-type": "unsupported-code",
        }
        mock_get.return_value = mock_response

        with patch.object(currency, "EXCHANGE_RATE_API_KEY", "test_key"):
            with pytest.raises(ValueError, match="Currency conversion failed"):
                currency.convert_currency(
                    amount=Decimal("100"),
                    from_currency=Currency.USD,
                    to_currency=Currency.EUR,
                )
