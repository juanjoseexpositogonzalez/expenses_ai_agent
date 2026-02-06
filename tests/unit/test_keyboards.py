from expenses_ai_agent.telegram.keyboards import (
    CATEGORY_CALLBACK_PREFIX,
    build_category_confirmation_keyboard,
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
