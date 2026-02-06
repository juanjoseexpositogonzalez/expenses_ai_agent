from telegram import InlineKeyboardButton, InlineKeyboardMarkup

CATEGORY_CALLBACK_PREFIX = "category:"

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
