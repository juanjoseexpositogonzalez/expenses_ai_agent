import logging

from decouple import config
from telegram import Update
from telegram.ext import Application, CommandHandler

from expenses_ai_agent.telegram.handlers import (
    ExpenseConversationHandler,
    help_command,
    start_command,
)
from expenses_ai_agent.utils.logging_config import setup_logging

logger = logging.getLogger(__name__)


class ExpenseTelegramBot:
    """Telegram bot for expense tracking with AI classification."""

    def __init__(
        self,
        token: str,
        db_url: str,
        openai_api_key: str,
        model: str = "gpt-4.1-nano-2025-04-14",
    ) -> None:
        self.token = token
        self.db_url = db_url
        self.openai_api_key = openai_api_key
        self.model = model
        self.application: Application | None = None  # type: ignore[type-arg]

    def setup(self) -> Application:  # type: ignore[type-arg]
        """Build and configure the Telegram application."""
        self.application = Application.builder().token(self.token).build()

        # Conversation handler (expense flow with HITL)
        conversation = ExpenseConversationHandler(
            db_url=self.db_url,
            openai_api_key=self.openai_api_key,
            model=self.model,
        ).build()

        self.application.add_handler(CommandHandler("start", start_command))
        self.application.add_handler(CommandHandler("help", help_command))
        self.application.add_handler(conversation)
        self.application.add_error_handler(self._error_handler)

        logger.info("Bot application configured")
        return self.application

    async def _error_handler(self, update: object, context: object) -> None:
        """Log errors and notify the user."""
        logger.error(
            "Update %s caused error: %s", update, getattr(context, "error", "unknown")
        )

        if isinstance(update, Update) and update.effective_message:
            await update.effective_message.reply_text(
                "An error occurred. Please try again or use /cancel."
            )

    def run(self) -> None:
        """Start the bot with long-polling."""
        if self.application is None:
            self.setup()

        assert self.application is not None  # noqa: S101
        logger.info("Starting bot polling...")
        self.application.run_polling(allowed_updates=Update.ALL_TYPES)


def main() -> None:
    """Entry point for the Telegram bot."""
    setup_logging()

    token: str = config("TELEGRAM_BOT_TOKEN")  # type: ignore[assignment]
    db_url: str = config("DB_URL", default="sqlite:///expenses.db")  # type: ignore[assignment]
    openai_api_key: str = config("OPENAI_API_KEY")  # type: ignore[assignment]
    model: str = config("OPENAI_MODEL", default="gpt-4.1-nano-2025-04-14")  # type: ignore[assignment]

    bot = ExpenseTelegramBot(
        token=token,
        db_url=db_url,
        openai_api_key=openai_api_key,
        model=model,
    )
    bot.run()


if __name__ == "__main__":
    main()
