"""
Week 4 - Definition of Done: Telegram Handlers

Copy this file to your project's tests/unit/ directory.
Run: pytest tests/unit/test_week4_handlers.py -v
All tests must pass to complete Week 4's handlers milestone.

These tests verify your implementation of:
- Command handlers (start, help, cancel)
- ExpenseConversationHandler class
- CurrencyHandler class
- Human-in-the-loop category confirmation
"""

from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock, patch

import pytest


@pytest.fixture
def mock_update():
    """Create a mock Telegram Update object."""
    update = MagicMock()
    update.effective_user = MagicMock()
    update.effective_user.id = 12345
    update.effective_user.first_name = "TestUser"
    update.message = MagicMock()
    update.message.text = "Coffee $5.50"
    update.message.reply_text = AsyncMock()
    return update


@pytest.fixture
def mock_context():
    """Create a mock Telegram Context object."""
    context = MagicMock()
    context.user_data = {}
    context.bot_data = {}
    return context


@pytest.fixture
def mock_callback_update():
    """Create a mock Update for callback queries."""
    update = MagicMock()
    update.effective_user = MagicMock()
    update.effective_user.id = 12345
    update.callback_query = MagicMock()
    update.callback_query.data = "cat:Food"
    update.callback_query.answer = AsyncMock()
    update.callback_query.edit_message_text = AsyncMock()
    return update


class TestCommandHandlers:
    """Tests for basic command handlers."""

    @pytest.mark.asyncio
    async def test_start_command_exists(self, mock_update, mock_context):
        """start_command should be importable and callable."""
        from expenses_ai_agent.telegram.handlers import start_command

        await start_command(mock_update, mock_context)

        # Should reply with welcome message
        mock_update.message.reply_text.assert_called_once()
        call_args = mock_update.message.reply_text.call_args
        message = call_args[0][0] if call_args[0] else call_args[1].get("text", "")
        assert len(message) > 10  # Some welcome text

    @pytest.mark.asyncio
    async def test_help_command_exists(self, mock_update, mock_context):
        """help_command should provide usage instructions."""
        from expenses_ai_agent.telegram.handlers import help_command

        await help_command(mock_update, mock_context)

        mock_update.message.reply_text.assert_called_once()

    @pytest.mark.asyncio
    async def test_cancel_command_returns_end(self, mock_update, mock_context):
        """cancel_command should return ConversationHandler.END."""
        from telegram.ext import ConversationHandler

        from expenses_ai_agent.telegram.handlers import cancel_command

        result = await cancel_command(mock_update, mock_context)

        assert result == ConversationHandler.END


class TestExpenseConversationHandler:
    """Tests for the expense conversation handler."""

    def test_handler_class_exists(self):
        """ExpenseConversationHandler class should exist."""
        from expenses_ai_agent.telegram.handlers import ExpenseConversationHandler

        assert ExpenseConversationHandler is not None

    def test_handler_build_returns_conversation_handler(self):
        """build() should return a ConversationHandler."""
        from telegram.ext import ConversationHandler

        from expenses_ai_agent.telegram.handlers import ExpenseConversationHandler

        handler = ExpenseConversationHandler(db_url="sqlite:///:memory:")
        result = handler.build()

        assert isinstance(result, ConversationHandler)

    @pytest.mark.asyncio
    async def test_handle_expense_text_with_valid_input(self, mock_update, mock_context):
        """handle_expense_text should classify and show keyboard."""
        from expenses_ai_agent.llms.output import ExpenseCategorizationResponse
        from expenses_ai_agent.storage.models import Currency
        from expenses_ai_agent.telegram.handlers import ExpenseConversationHandler

        handler = ExpenseConversationHandler(db_url="sqlite:///:memory:")

        # Mock the classification
        with patch.object(handler, "_build_assistant") as mock_build:
            mock_assistant = MagicMock()
            mock_assistant.completion.return_value = ExpenseCategorizationResponse(
                category="Food",
                total_amount=Decimal("5.50"),
                currency=Currency.USD,
                confidence=0.95,
                cost=Decimal("0.001"),
            )
            mock_build.return_value = mock_assistant

            result = await handler.handle_expense_text(mock_update, mock_context)

            # Should reply with classification result and keyboard
            mock_update.message.reply_text.assert_called()

    @pytest.mark.asyncio
    async def test_handle_expense_text_with_invalid_input(self, mock_update, mock_context):
        """Invalid input should return error message."""
        from telegram.ext import ConversationHandler

        from expenses_ai_agent.telegram.handlers import ExpenseConversationHandler

        handler = ExpenseConversationHandler(db_url="sqlite:///:memory:")

        # Set invalid (too short) input
        mock_update.message.text = "ab"

        result = await handler.handle_expense_text(mock_update, mock_context)

        # Should end conversation or reply with error
        mock_update.message.reply_text.assert_called()
        assert result == ConversationHandler.END

    @pytest.mark.asyncio
    async def test_handle_category_selection_persists(self, mock_callback_update, mock_context):
        """handle_category_selection should persist the expense."""
        from expenses_ai_agent.llms.output import ExpenseCategorizationResponse
        from expenses_ai_agent.storage.models import Currency
        from expenses_ai_agent.telegram.handlers import ExpenseConversationHandler

        handler = ExpenseConversationHandler(db_url="sqlite:///:memory:")

        # Store data in context (simulating previous step)
        mock_context.user_data["expense_description"] = "Coffee $5.50"
        mock_context.user_data["classification_response"] = ExpenseCategorizationResponse(
            category="Food",
            total_amount=Decimal("5.50"),
            currency=Currency.USD,
            confidence=0.95,
            cost=Decimal("0.001"),
        )

        with patch("expenses_ai_agent.telegram.handlers.DBCategoryRepo"), \
             patch("expenses_ai_agent.telegram.handlers.DBExpenseRepo") as mock_repo:
            mock_repo_instance = MagicMock()
            mock_repo.return_value = mock_repo_instance

            result = await handler.handle_category_selection(mock_callback_update, mock_context)

            # Should answer callback and edit message
            mock_callback_update.callback_query.answer.assert_called()


class TestCurrencyHandler:
    """Tests for the currency preference handler."""

    def test_currency_handler_exists(self):
        """CurrencyHandler class should exist."""
        from expenses_ai_agent.telegram.handlers import CurrencyHandler

        assert CurrencyHandler is not None

    @pytest.mark.asyncio
    async def test_currency_command_shows_keyboard(self, mock_update, mock_context):
        """currency_command should show currency selection keyboard."""
        from expenses_ai_agent.telegram.handlers import CurrencyHandler

        handler = CurrencyHandler(db_url="sqlite:///:memory:")

        await handler.currency_command(mock_update, mock_context)

        # Should reply with keyboard
        mock_update.message.reply_text.assert_called()
        call_args = mock_update.message.reply_text.call_args
        # Should have reply_markup (keyboard)
        assert "reply_markup" in call_args[1] if call_args[1] else False

    @pytest.mark.asyncio
    async def test_handle_currency_selection(self, mock_callback_update, mock_context):
        """handle_currency_selection should save user preference."""
        from expenses_ai_agent.telegram.handlers import CurrencyHandler

        handler = CurrencyHandler(db_url="sqlite:///:memory:")
        mock_callback_update.callback_query.data = "currency:EUR"

        with patch("expenses_ai_agent.telegram.handlers.DBUserPreferenceRepo"):
            await handler.handle_currency_selection(mock_callback_update, mock_context)

            mock_callback_update.callback_query.answer.assert_called()


class TestTelegramExceptions:
    """Tests for custom Telegram exceptions."""

    def test_telegram_bot_error_exists(self):
        """TelegramBotError base exception should exist."""
        from expenses_ai_agent.telegram.exceptions import TelegramBotError

        error = TelegramBotError("Test error")
        assert isinstance(error, Exception)

    def test_invalid_input_error_exists(self):
        """InvalidInputError should exist."""
        from expenses_ai_agent.telegram.exceptions import InvalidInputError

        error = InvalidInputError("Invalid input")
        assert isinstance(error, Exception)

    def test_classification_error_exists(self):
        """ClassificationError should exist."""
        from expenses_ai_agent.telegram.exceptions import ClassificationError

        error = ClassificationError("Classification failed")
        assert isinstance(error, Exception)
