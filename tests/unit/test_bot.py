"""Tests for Telegram bot setup and initialization."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from expenses_ai_agent.telegram.bot import ExpenseTelegramBot


class TestExpenseTelegramBot:
    """Tests for ExpenseTelegramBot class."""

    def test_bot_init(self) -> None:
        """Test bot initialization with required parameters."""
        bot = ExpenseTelegramBot(
            token="test-token",
            db_url="sqlite:///test.db",
            openai_api_key="test-api-key",
            model="gpt-4o",
        )

        assert bot.token == "test-token"
        assert bot.db_url == "sqlite:///test.db"
        assert bot.openai_api_key == "test-api-key"
        assert bot.model == "gpt-4o"
        assert bot.application is None

    def test_bot_init_default_model(self) -> None:
        """Test bot initialization with default model."""
        bot = ExpenseTelegramBot(
            token="test-token",
            db_url="sqlite:///test.db",
            openai_api_key="test-api-key",
        )

        assert bot.model == "gpt-4.1-nano-2025-04-14"

    @patch("expenses_ai_agent.telegram.bot.Application")
    @patch("expenses_ai_agent.telegram.bot.ExpenseConversationHandler")
    @patch("expenses_ai_agent.telegram.bot.CommandHandler")
    def test_bot_setup_registers_handlers(
        self,
        mock_command_handler: MagicMock,
        mock_conversation_handler: MagicMock,
        mock_application_class: MagicMock,
    ) -> None:
        """Test that setup registers all required handlers."""
        mock_app = MagicMock()
        mock_application_class.builder.return_value.token.return_value.build.return_value = (
            mock_app
        )
        mock_conversation_handler.return_value.build.return_value = MagicMock()

        bot = ExpenseTelegramBot(
            token="test-token",
            db_url="sqlite:///test.db",
            openai_api_key="test-api-key",
        )
        result = bot.setup()

        # Verify handlers were added
        # start, help, currency, currency_callback, conversation = 5
        assert mock_app.add_handler.call_count == 5
        assert mock_app.add_error_handler.call_count == 1
        assert result == mock_app

    @patch("expenses_ai_agent.telegram.bot.Application")
    @patch("expenses_ai_agent.telegram.bot.ExpenseConversationHandler")
    @patch("expenses_ai_agent.telegram.bot.CommandHandler")
    def test_bot_run_calls_polling(
        self,
        mock_command_handler: MagicMock,
        mock_conversation_handler: MagicMock,
        mock_application_class: MagicMock,
    ) -> None:
        """Test that run() calls run_polling."""
        mock_app = MagicMock()
        mock_application_class.builder.return_value.token.return_value.build.return_value = (
            mock_app
        )
        mock_conversation_handler.return_value.build.return_value = MagicMock()

        bot = ExpenseTelegramBot(
            token="test-token",
            db_url="sqlite:///test.db",
            openai_api_key="test-api-key",
        )
        bot.run()

        mock_app.run_polling.assert_called_once()

    @patch("expenses_ai_agent.telegram.bot.Application")
    @patch("expenses_ai_agent.telegram.bot.ExpenseConversationHandler")
    @patch("expenses_ai_agent.telegram.bot.CommandHandler")
    def test_bot_run_calls_setup_if_not_done(
        self,
        mock_command_handler: MagicMock,
        mock_conversation_handler: MagicMock,
        mock_application_class: MagicMock,
    ) -> None:
        """Test that run() calls setup() if application is None."""
        mock_app = MagicMock()
        mock_application_class.builder.return_value.token.return_value.build.return_value = (
            mock_app
        )
        mock_conversation_handler.return_value.build.return_value = MagicMock()

        bot = ExpenseTelegramBot(
            token="test-token",
            db_url="sqlite:///test.db",
            openai_api_key="test-api-key",
        )

        # application should be None before run
        assert bot.application is None
        bot.run()
        # run_polling should be called
        mock_app.run_polling.assert_called_once()


class TestBotErrorHandler:
    """Tests for bot error handler."""

    @pytest.mark.asyncio
    async def test_error_handler_logs_error(self) -> None:
        """Test that error handler logs the error."""
        bot = ExpenseTelegramBot(
            token="test-token",
            db_url="sqlite:///test.db",
            openai_api_key="test-api-key",
        )

        # Create mock update without effective_message
        mock_update = MagicMock()
        mock_update.effective_message = None

        mock_context = MagicMock()
        mock_context.error = Exception("Test error")

        # Should not raise, just log
        await bot._error_handler(mock_update, mock_context)

    @pytest.mark.asyncio
    async def test_error_handler_replies_to_user(self) -> None:
        """Test that error handler replies to user when possible."""
        bot = ExpenseTelegramBot(
            token="test-token",
            db_url="sqlite:///test.db",
            openai_api_key="test-api-key",
        )

        # Import Update to use isinstance check
        from telegram import Update

        # Create a proper mock Update
        mock_message = AsyncMock()
        mock_update = MagicMock(spec=Update)
        mock_update.effective_message = mock_message

        mock_context = MagicMock()
        mock_context.error = Exception("Test error")

        await bot._error_handler(mock_update, mock_context)

        mock_message.reply_text.assert_called_once()


class TestMainEntryPoint:
    """Tests for main entry point."""

    @patch("expenses_ai_agent.telegram.bot.ExpenseTelegramBot")
    @patch("expenses_ai_agent.telegram.bot.setup_logging")
    @patch("expenses_ai_agent.telegram.bot.config")
    def test_main_initializes_and_runs_bot(
        self,
        mock_config: MagicMock,
        mock_setup_logging: MagicMock,
        mock_bot_class: MagicMock,
    ) -> None:
        """Test that main() initializes and runs the bot."""
        from expenses_ai_agent.telegram.bot import main

        # Configure mock returns
        mock_config.side_effect = lambda key, **kwargs: {
            "TELEGRAM_BOT_TOKEN": "test-token",
            "DB_URL": "sqlite:///test.db",
            "OPENAI_API_KEY": "test-key",
            "OPENAI_MODEL": "gpt-4o",
        }.get(key, kwargs.get("default", ""))

        mock_bot = MagicMock()
        mock_bot_class.return_value = mock_bot

        main()

        mock_setup_logging.assert_called_once()
        mock_bot_class.assert_called_once()
        mock_bot.run.assert_called_once()
