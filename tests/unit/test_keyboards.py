from expenses_ai_agent.storage.models import Currency
from expenses_ai_agent.telegram.keyboards import (
    CATEGORY_CALLBACK_PREFIX,
    CURRENCY_CALLBACK_PREFIX,
    CURRENCY_SYMBOLS,
    build_category_confirmation_keyboard,
    build_currency_selection_keyboard,
)


def test_keyboard_has_suggested_category() -> None:
    keyboard = build_category_confirmation_keyboard(
        suggested_category="Food & Dining",
    )

    rows = keyboard.inline_keyboard
    assert len(rows) >= 1

    first_button = rows[0][0]
    assert "Food & Dining" in first_button.text
    assert "\u2705" in first_button.text
    assert first_button.callback_data == f"{CATEGORY_CALLBACK_PREFIX}Food & Dining"


def test_keyboard_has_alternative_row() -> None:
    keyboard = build_category_confirmation_keyboard(
        suggested_category="Food & Dining",
        alternatives=["Transportation", "Entertainment", "Shopping"],
    )

    rows = keyboard.inline_keyboard
    assert len(rows) == 2

    alt_row = rows[1]
    assert len(alt_row) == 3
    assert alt_row[0].text == "Transportation"
    assert alt_row[1].text == "Entertainment"
    assert alt_row[2].text == "Shopping"


def test_keyboard_callback_data_prefix() -> None:
    keyboard = build_category_confirmation_keyboard(
        suggested_category="Healthcare",
        alternatives=["Shopping"],
    )

    for row in keyboard.inline_keyboard:
        for button in row:
            assert button.callback_data.startswith(CATEGORY_CALLBACK_PREFIX)


def test_keyboard_no_alternatives() -> None:
    keyboard = build_category_confirmation_keyboard(
        suggested_category="Other",
        alternatives=[],
    )

    rows = keyboard.inline_keyboard
    assert len(rows) == 1


def test_keyboard_auto_alternatives_exclude_suggested() -> None:
    """When no alternatives are given, they are picked from ALL_CATEGORIES."""
    keyboard = build_category_confirmation_keyboard(
        suggested_category="Food & Dining",
    )

    rows = keyboard.inline_keyboard
    assert len(rows) == 2

    for button in rows[1]:
        assert "Food & Dining" not in button.text


def test_keyboard_max_alternatives_respected() -> None:
    keyboard = build_category_confirmation_keyboard(
        suggested_category="Other",
        max_alternatives=2,
    )

    rows = keyboard.inline_keyboard
    if len(rows) > 1:
        assert len(rows[1]) <= 2


# ------------------------------------------------------------------
# Currency Keyboard Tests
# ------------------------------------------------------------------


def test_currency_keyboard_has_all_currencies() -> None:
    """Test that currency keyboard displays all 10 currencies."""
    keyboard = build_currency_selection_keyboard()
    rows = keyboard.inline_keyboard

    # Count all buttons
    total_buttons = sum(len(row) for row in rows)
    assert total_buttons == 10  # All currencies


def test_currency_keyboard_layout() -> None:
    """Test that currency keyboard has 3-3-3-1 layout."""
    keyboard = build_currency_selection_keyboard()
    rows = keyboard.inline_keyboard

    assert len(rows) == 4
    assert len(rows[0]) == 3
    assert len(rows[1]) == 3
    assert len(rows[2]) == 3
    assert len(rows[3]) == 1


def test_currency_keyboard_highlights_current() -> None:
    """Test that current currency is highlighted with checkmark."""
    keyboard = build_currency_selection_keyboard(current_currency=Currency.EUR)
    rows = keyboard.inline_keyboard

    # Find EUR button
    eur_found = False
    for row in rows:
        for button in row:
            if "EUR" in button.text:
                if Currency.EUR.value in button.callback_data:
                    assert "✅" in button.text
                    eur_found = True

    assert eur_found


def test_currency_keyboard_no_current_no_checkmark() -> None:
    """Test that no checkmark appears when current_currency is None."""
    keyboard = build_currency_selection_keyboard(current_currency=None)
    rows = keyboard.inline_keyboard

    for row in rows:
        for button in row:
            assert "✅" not in button.text


def test_currency_keyboard_callback_data_prefix() -> None:
    """Test that all buttons have correct callback prefix."""
    keyboard = build_currency_selection_keyboard()
    rows = keyboard.inline_keyboard

    for row in rows:
        for button in row:
            assert button.callback_data.startswith(CURRENCY_CALLBACK_PREFIX)


def test_currency_keyboard_symbols() -> None:
    """Test that currency symbols are displayed correctly."""
    keyboard = build_currency_selection_keyboard()
    rows = keyboard.inline_keyboard

    # Check USD button has $ symbol
    for row in rows:
        for button in row:
            if "USD" in button.callback_data:
                assert "$" in button.text


def test_currency_symbols_mapping() -> None:
    """Test that CURRENCY_SYMBOLS has all currencies."""
    assert len(CURRENCY_SYMBOLS) == 10
    assert CURRENCY_SYMBOLS[Currency.USD] == "$"
    assert CURRENCY_SYMBOLS[Currency.EUR] == "€"
    assert CURRENCY_SYMBOLS[Currency.GBP] == "£"
    assert CURRENCY_SYMBOLS[Currency.JPY] == "¥"
