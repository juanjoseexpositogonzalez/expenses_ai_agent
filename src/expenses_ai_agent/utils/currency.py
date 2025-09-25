from decimal import Decimal
from typing import Final

import requests
from decouple import config

from expenses_ai_agent.storage.models import Currency

EXCHANGE_RATE_API_KEY: Final[str] = config(
    "EXCHANGE_RATE_API_KEY", default="", cast=str
)  # type: ignore
API_ENDPOINT: Final[str] = (
    f"https://v6.exchangerate-api.com/v6/{EXCHANGE_RATE_API_KEY}/pair"
)


def convert_currency(
    amount: Decimal, from_currency: Currency, to_currency: Currency = Currency.EUR
) -> Decimal:
    """Convert an amount from one currency to another using an external API.

    Args:
        amount (Decimal): The amount to convert.
        from_currency (Currency): The currency to convert from.
        to_currency (Currency): The currency to convert to. Defaults to Currency.EUR.

    Returns:
        Decimal: The converted amount in the target currency.

    Raises:
        ValueError: If the API key is not set or if the conversion fails.
    """

    if not EXCHANGE_RATE_API_KEY:
        raise ValueError("Exchange rate API key is not set.")

    url = f"{API_ENDPOINT}/{from_currency}/{to_currency}/{amount}"
    response = requests.get(url, timeout=10)
    data = response.json()

    if response.status_code != 200 or data.get("result") != "success":
        raise ValueError(
            f"Currency conversion failed: {data.get('error-type', 'Unknown error')}"
        )

    conversion_result = Decimal(str(data["conversion_result"]))
    return conversion_result
