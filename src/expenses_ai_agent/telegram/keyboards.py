from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from expenses_ai_agent.storage.models import Currency

CATEGORY_CALLBACK_PREFIX = "category:"
CURRENCY_CALLBACK_PREFIX = "setcurrency:"

# Currency symbols for display
CURRENCY_SYMBOLS: dict[Currency, str] = {
    Currency.USD: "$",
    Currency.EUR: "€",
    Currency.GBP: "£",
    Currency.JPY: "¥",
    Currency.AUD: "A$",
    Currency.CAD: "C$",
    Currency.CHF: "Fr",
    Currency.CNY: "¥",
    Currency.SEK: "kr",
    Currency.NZD: "NZ$",
}

ALL_CATEGORIES: list[str] = [
    "Food & Dining",
    "Transportation",
    "Utilities",
    "Entertainment",
    "Healthcare",
    "Shopping",
    "Housing",
    "Education",
    "Travel",
    "Personal Care",
    "Subscriptions",
    "Other",
]


def build_category_confirmation_keyboard(
    suggested_category: str,
    alternatives: list[str] | None = None,
    max_alternatives: int = 3,
) -> InlineKeyboardMarkup:
    """Build an inline keyboard for category confirmation.

    Row 1: checkmark + suggested category.
    Row 2: up to *max_alternatives* other categories.

    Args:
        suggested_category: The LLM-suggested category.
        alternatives: Explicit list of alternatives.  When ``None`` the
            function picks from ``ALL_CATEGORIES``.
        max_alternatives: How many alternative buttons to show.

    Returns:
        Ready-to-use InlineKeyboardMarkup.
    """
    keyboard: list[list[InlineKeyboardButton]] = []

    # Row 1 - confirm suggested
    keyboard.append(
        [
            InlineKeyboardButton(
                text=f"\u2705 {suggested_category}",
                callback_data=f"{CATEGORY_CALLBACK_PREFIX}{suggested_category}",
            )
        ]
    )

    # Row 2 - alternatives
    if alternatives is None:
        alternatives = [cat for cat in ALL_CATEGORIES if cat != suggested_category][
            :max_alternatives
        ]

    alt_buttons = [
        InlineKeyboardButton(
            text=cat,
            callback_data=f"{CATEGORY_CALLBACK_PREFIX}{cat}",
        )
        for cat in alternatives[:max_alternatives]
    ]
    if alt_buttons:
        keyboard.append(alt_buttons)

    return InlineKeyboardMarkup(keyboard)


def build_currency_selection_keyboard(
    current_currency: Currency | None = None,
) -> InlineKeyboardMarkup:
    """Build an inline keyboard for currency selection.

    Displays 10 currencies in a 3-3-3-1 layout.
    The current selection is highlighted with a checkmark.

    Args:
        current_currency: The user's current preferred currency.

    Returns:
        Ready-to-use InlineKeyboardMarkup.
    """
    currencies = list(Currency)
    keyboard: list[list[InlineKeyboardButton]] = []

    # Layout: 3-3-3-1
    row_sizes = [3, 3, 3, 1]
    idx = 0

    for row_size in row_sizes:
        row: list[InlineKeyboardButton] = []
        for _ in range(row_size):
            if idx >= len(currencies):
                break
            curr = currencies[idx]
            symbol = CURRENCY_SYMBOLS.get(curr, "")

            # Highlight current selection
            if curr == current_currency:
                label = f"✅ {symbol} {curr.value}"
            else:
                label = f"{symbol} {curr.value}"

            row.append(
                InlineKeyboardButton(
                    text=label,
                    callback_data=f"{CURRENCY_CALLBACK_PREFIX}{curr.value}",
                )
            )
            idx += 1

        if row:
            keyboard.append(row)

    return InlineKeyboardMarkup(keyboard)
