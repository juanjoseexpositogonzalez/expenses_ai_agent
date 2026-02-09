"""
Week 4 - Definition of Done: Telegram Keyboards

Copy this file to your project's tests/unit/ directory.
Run: pytest tests/unit/test_week4_keyboards.py -v
All tests must pass to complete Week 4's keyboards milestone.

These tests verify your implementation of:
- build_category_confirmation_keyboard function
- build_currency_selection_keyboard function
"""

import pytest


class TestCategoryKeyboard:
    """Tests for the category confirmation keyboard builder."""

    def test_keyboard_builder_exists(self):
        """build_category_confirmation_keyboard should be importable."""
        from expenses_ai_agent.telegram.keyboards import build_category_confirmation_keyboard

        assert callable(build_category_confirmation_keyboard)

    def test_keyboard_returns_markup(self):
        """Should return an InlineKeyboardMarkup."""
        from telegram import InlineKeyboardMarkup

        from expenses_ai_agent.telegram.keyboards import build_category_confirmation_keyboard

        categories = ["Food", "Transport", "Entertainment"]
        keyboard = build_category_confirmation_keyboard(
            suggested_category="Food",
            all_categories=categories,
        )

        assert isinstance(keyboard, InlineKeyboardMarkup)

    def test_keyboard_has_all_categories(self):
        """Keyboard should include all provided categories."""
        from expenses_ai_agent.telegram.keyboards import build_category_confirmation_keyboard

        categories = ["Food", "Transport", "Entertainment", "Shopping"]
        keyboard = build_category_confirmation_keyboard(
            suggested_category="Food",
            all_categories=categories,
        )

        # Flatten all buttons
        all_buttons = [btn for row in keyboard.inline_keyboard for btn in row]

        # Each category should appear in button text
        button_texts = [btn.text for btn in all_buttons]
        for cat in categories:
            assert any(cat in text for text in button_texts), f"Category {cat} not in keyboard"

    def test_keyboard_highlights_suggested_category(self):
        """Suggested category should be visually highlighted."""
        from expenses_ai_agent.telegram.keyboards import build_category_confirmation_keyboard

        categories = ["Food", "Transport", "Entertainment"]
        keyboard = build_category_confirmation_keyboard(
            suggested_category="Transport",
            all_categories=categories,
        )

        all_buttons = [btn for row in keyboard.inline_keyboard for btn in row]

        # Find the Transport button
        transport_buttons = [btn for btn in all_buttons if "Transport" in btn.text]
        assert len(transport_buttons) == 1

        # It should be highlighted (e.g., with >> << or different text)
        transport_text = transport_buttons[0].text
        # Check for some form of highlighting
        assert (
            ">>" in transport_text or
            "<<" in transport_text or
            "*" in transport_text or
            transport_text != "Transport"  # Some modification
        )


class TestCurrencyKeyboard:
    """Tests for the currency selection keyboard builder."""

    def test_currency_keyboard_builder_exists(self):
        """build_currency_selection_keyboard should be importable."""
        from expenses_ai_agent.telegram.keyboards import build_currency_selection_keyboard

        assert callable(build_currency_selection_keyboard)

    def test_currency_keyboard_has_common_currencies(self):
        """Currency keyboard should include common currencies."""
        from expenses_ai_agent.telegram.keyboards import build_currency_selection_keyboard

        keyboard = build_currency_selection_keyboard()

        all_buttons = [btn for row in keyboard.inline_keyboard for btn in row]
        button_texts = " ".join([btn.text for btn in all_buttons])

        # Should have major currencies
        assert "EUR" in button_texts or "Euro" in button_texts
        assert "USD" in button_texts or "Dollar" in button_texts
        assert "GBP" in button_texts or "Pound" in button_texts

    def test_currency_keyboard_has_callback_data(self):
        """Each currency button should have callback data."""
        from expenses_ai_agent.telegram.keyboards import build_currency_selection_keyboard

        keyboard = build_currency_selection_keyboard()

        all_buttons = [btn for row in keyboard.inline_keyboard for btn in row]

        for btn in all_buttons:
            assert btn.callback_data is not None
            assert len(btn.callback_data) > 0
