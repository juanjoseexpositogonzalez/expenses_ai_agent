"""Tests for Telegram bot custom exceptions."""

import pytest

from expenses_ai_agent.telegram.exceptions import (
    ClassificationError,
    InvalidInputError,
    PersistenceError,
    TelegramBotError,
)


class TestTelegramExceptions:
    """Tests for Telegram exception hierarchy."""

    def test_telegram_bot_error_is_base_exception(self) -> None:
        """Test that TelegramBotError is the base exception."""
        error = TelegramBotError("test error")
        assert isinstance(error, Exception)
        assert str(error) == "test error"

    def test_invalid_input_error_inherits_from_base(self) -> None:
        """Test that InvalidInputError inherits from TelegramBotError."""
        error = InvalidInputError("invalid input")
        assert isinstance(error, TelegramBotError)
        assert isinstance(error, Exception)

    def test_classification_error_inherits_from_base(self) -> None:
        """Test that ClassificationError inherits from TelegramBotError."""
        error = ClassificationError("classification failed")
        assert isinstance(error, TelegramBotError)

    def test_persistence_error_inherits_from_base(self) -> None:
        """Test that PersistenceError inherits from TelegramBotError."""
        error = PersistenceError("db write failed")
        assert isinstance(error, TelegramBotError)

    def test_exceptions_can_be_caught_by_base_class(self) -> None:
        """Test that all exceptions can be caught by TelegramBotError."""
        exceptions = [
            InvalidInputError("test"),
            ClassificationError("test"),
            PersistenceError("test"),
        ]
        for exc in exceptions:
            with pytest.raises(TelegramBotError):
                raise exc
