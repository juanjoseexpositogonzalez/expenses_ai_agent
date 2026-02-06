class TelegramBotError(Exception):
    """Base exception for Telegram bot errors."""


class InvalidInputError(TelegramBotError):
    """Raised when user input fails preprocessing validation."""


class ClassificationError(TelegramBotError):
    """Raised when LLM classification fails."""


class PersistenceError(TelegramBotError):
    """Raised when database persistence fails."""
