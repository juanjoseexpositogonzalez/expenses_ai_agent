import logging
from decimal import Decimal, getcontext

from expenses_ai_agent.utils.currency import Currency, convert_currency

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def main() -> None:
    getcontext().prec = 2
    amount = Decimal(100)
    from_currency: Currency = Currency.USD
    to_currency: Currency = Currency.GBP
    logger.info("Running currency conversion tests...")
    logger.info("Converting %d %s to %s", amount, from_currency, to_currency)
    converted_amount = convert_currency(amount, from_currency, to_currency)
    assert isinstance(converted_amount, Decimal)
    assert converted_amount > 0
    logger.info(
        "Conversion successful: %.2f %s = %.2f %s",
        amount,
        from_currency,
        converted_amount,
        to_currency,
    )


if __name__ == "__main__":
    main()
