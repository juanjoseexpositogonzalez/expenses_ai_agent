"""Integration tests for Currency Conversion API.

These tests require a real EXCHANGE_RATE_API_KEY and make actual API calls.
Run with: pytest -m integration

To skip in CI: pytest -m "not integration"
"""

from decimal import Decimal

import pytest
from decouple import config

from expenses_ai_agent.storage.models import Currency


# Check if API key is available
EXCHANGE_RATE_API_KEY = config("EXCHANGE_RATE_API_KEY", default="")
SKIP_REASON = "EXCHANGE_RATE_API_KEY not configured"


@pytest.mark.integration
@pytest.mark.skipif(not EXCHANGE_RATE_API_KEY, reason=SKIP_REASON)
class TestCurrencyConversionIntegration:
    """Integration tests for currency conversion API calls."""

    def test_convert_usd_to_eur(self) -> None:
        """Test real USD to EUR conversion."""
        from expenses_ai_agent.utils.currency import convert_currency

        result = convert_currency(
            amount=Decimal("100"),
            from_currency=Currency.USD,
            to_currency=Currency.EUR,
        )

        # Result should be a positive Decimal
        assert isinstance(result, Decimal)
        assert result > 0
        # USD to EUR rate is typically between 0.8 and 1.2
        assert Decimal("50") < result < Decimal("150")

    def test_convert_gbp_to_usd(self) -> None:
        """Test real GBP to USD conversion."""
        from expenses_ai_agent.utils.currency import convert_currency

        result = convert_currency(
            amount=Decimal("50"),
            from_currency=Currency.GBP,
            to_currency=Currency.USD,
        )

        assert isinstance(result, Decimal)
        assert result > 0

    def test_convert_same_currency(self) -> None:
        """Test converting same currency returns same amount."""
        from expenses_ai_agent.utils.currency import convert_currency

        result = convert_currency(
            amount=Decimal("100"),
            from_currency=Currency.EUR,
            to_currency=Currency.EUR,
        )

        # Same currency should return same amount (or very close)
        assert abs(result - Decimal("100")) < Decimal("1")
