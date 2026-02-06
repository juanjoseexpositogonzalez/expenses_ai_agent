from decimal import Decimal
from unittest.mock import AsyncMock, Mock, patch

import pytest
from telegram import CallbackQuery, Chat, Message, Update, User
from telegram.ext import ConversationHandler, ContextTypes

from expenses_ai_agent.llms.output import ExpenseCategorizationResponse
from expenses_ai_agent.storage.models import Currency
from expenses_ai_agent.telegram.handlers import (
    WAITING_FOR_CONFIRMATION,
    CurrencyHandler,
    ExpenseConversationHandler,
    cancel_command,
    help_command,
    start_command,
)
from expenses_ai_agent.telegram.keyboards import (
    CATEGORY_CALLBACK_PREFIX,
    CURRENCY_CALLBACK_PREFIX,
)


# ------------------------------------------------------------------
# Helpers
# ------------------------------------------------------------------


def _make_update(text: str = "Coffee at Starbucks $5.50") -> Update:
    """Build a minimal mock Update with a text message."""
    user = User(id=123, first_name="Test", is_bot=False)
    chat = Chat(id=456, type="private")
    message = Mock(spec=Message)
    message.text = text
    message.chat = chat
    message.reply_text = AsyncMock()

    update = Mock(spec=Update)
    update.effective_user = user
    update.message = message
    update.callback_query = None
    return update


def _make_callback_update(data: str) -> Update:
    """Build a minimal mock Update with a callback query."""
    user = User(id=123, first_name="Test", is_bot=False)
    query = Mock(spec=CallbackQuery)
    query.data = data
    query.answer = AsyncMock()
    query.edit_message_text = AsyncMock()

    update = Mock(spec=Update)
    update.effective_user = user
    update.callback_query = query
    update.message = None
    return update


def _make_context(**user_data: object) -> Mock:
    ctx = Mock(spec=ContextTypes.DEFAULT_TYPE)
    ctx.user_data = dict(user_data)
    return ctx


def _make_llm_response(
    category: str = "Food & Dining",
) -> ExpenseCategorizationResponse:
    return ExpenseCategorizationResponse(
        category=category,
        total_amount=Decimal("5.50"),
        currency=Currency.USD,
        confidence=0.95,
        cost=Decimal("0.0001"),
        comments="test",
    )


# ------------------------------------------------------------------
# Simple command tests
# ------------------------------------------------------------------


@pytest.mark.asyncio
async def test_start_command() -> None:
    update = _make_update()
    ctx = _make_context()

    await start_command(update, ctx)

    update.message.reply_text.assert_called_once()
    text = update.message.reply_text.call_args[0][0]
    assert "Welcome" in text


@pytest.mark.asyncio
async def test_help_command() -> None:
    update = _make_update()
    ctx = _make_context()

    await help_command(update, ctx)

    update.message.reply_text.assert_called_once()
    text = update.message.reply_text.call_args[0][0]
    assert "Help" in text


@pytest.mark.asyncio
async def test_cancel_command_clears_context() -> None:
    update = _make_update()
    ctx = _make_context(expense_description="test", llm_response="resp")

    result = await cancel_command(update, ctx)

    assert result == ConversationHandler.END
    assert len(ctx.user_data) == 0


# ------------------------------------------------------------------
# handle_expense_text
# ------------------------------------------------------------------


@pytest.mark.asyncio
async def test_handle_expense_text_invalid_input() -> None:
    update = _make_update(text="ab")
    ctx = _make_context()

    handler = ExpenseConversationHandler(
        db_url="sqlite:///:memory:",
        openai_api_key="test-key",
    )
    result = await handler.handle_expense_text(update, ctx)

    assert result == ConversationHandler.END
    update.message.reply_text.assert_called_once()
    text = update.message.reply_text.call_args[0][0]
    assert "Invalid" in text


@pytest.mark.asyncio
@patch("expenses_ai_agent.telegram.handlers.DBUserPreferenceRepo")
@patch("expenses_ai_agent.telegram.handlers.Session")
@patch("expenses_ai_agent.telegram.handlers.create_engine")
@patch("expenses_ai_agent.telegram.handlers.OpenAIAssistant")
async def test_handle_expense_text_success(
    mock_assistant_cls: Mock,
    mock_create_engine: Mock,
    mock_session_cls: Mock,
    mock_pref_repo_cls: Mock,
) -> None:
    mock_instance = Mock()
    mock_instance.completion.return_value = _make_llm_response()
    mock_assistant_cls.return_value = mock_instance

    # Mock session context manager
    mock_session = Mock()
    mock_session.__enter__ = Mock(return_value=mock_session)
    mock_session.__exit__ = Mock(return_value=False)
    mock_session_cls.return_value = mock_session

    # Mock user preference repo
    mock_pref_repo = Mock()
    mock_pref_repo.get_by_user_id.return_value = None  # No preference set
    mock_pref_repo_cls.return_value = mock_pref_repo

    # reply_text returns a message that supports .delete()
    processing_msg = Mock()
    processing_msg.delete = AsyncMock()

    update = _make_update("Coffee at Starbucks $5.50")
    # First call returns processing_msg, second is the confirmation
    update.message.reply_text = AsyncMock(side_effect=[processing_msg, None])

    ctx = _make_context()
    handler = ExpenseConversationHandler(
        db_url="sqlite:///:memory:",
        openai_api_key="test-key",
    )

    result = await handler.handle_expense_text(update, ctx)

    assert result == WAITING_FOR_CONFIRMATION
    assert "expense_description" in ctx.user_data
    assert "llm_response" in ctx.user_data
    processing_msg.delete.assert_awaited_once()


@pytest.mark.asyncio
@patch("expenses_ai_agent.telegram.handlers.OpenAIAssistant")
async def test_handle_expense_text_classification_error(
    mock_assistant_cls: Mock,
) -> None:
    mock_instance = Mock()
    mock_instance.completion.side_effect = RuntimeError("LLM down")
    mock_assistant_cls.return_value = mock_instance

    processing_msg = Mock()
    processing_msg.edit_text = AsyncMock()

    update = _make_update("Coffee $5.50")
    update.message.reply_text = AsyncMock(return_value=processing_msg)

    ctx = _make_context()
    handler = ExpenseConversationHandler(
        db_url="sqlite:///:memory:",
        openai_api_key="test-key",
    )

    result = await handler.handle_expense_text(update, ctx)

    assert result == ConversationHandler.END
    processing_msg.edit_text.assert_awaited_once()
    error_text = processing_msg.edit_text.call_args[0][0]
    assert "couldn't classify" in error_text.lower()


# ------------------------------------------------------------------
# handle_category_selection
# ------------------------------------------------------------------


@pytest.mark.asyncio
async def test_handle_category_selection_invalid_callback() -> None:
    update = _make_callback_update(data="invalid:data")
    ctx = _make_context()

    handler = ExpenseConversationHandler(
        db_url="sqlite:///:memory:",
        openai_api_key="test-key",
    )
    result = await handler.handle_category_selection(update, ctx)

    assert result == ConversationHandler.END
    update.callback_query.edit_message_text.assert_awaited_once()


@pytest.mark.asyncio
async def test_handle_category_selection_expired_session() -> None:
    data = f"{CATEGORY_CALLBACK_PREFIX}Food & Dining"
    update = _make_callback_update(data=data)
    ctx = _make_context()  # no stored data

    handler = ExpenseConversationHandler(
        db_url="sqlite:///:memory:",
        openai_api_key="test-key",
    )
    result = await handler.handle_category_selection(update, ctx)

    assert result == ConversationHandler.END
    text = update.callback_query.edit_message_text.call_args[0][0]
    assert "expired" in text.lower()


@pytest.mark.asyncio
@patch("expenses_ai_agent.telegram.handlers.create_engine")
@patch("expenses_ai_agent.telegram.handlers.Session")
@patch("expenses_ai_agent.telegram.handlers.ClassificationService")
@patch("expenses_ai_agent.telegram.handlers.OpenAIAssistant")
async def test_handle_category_selection_success(
    mock_assistant_cls: Mock,
    mock_service_cls: Mock,
    mock_session_cls: Mock,
    mock_create_engine: Mock,
) -> None:
    llm_response = _make_llm_response("Food & Dining")
    data = f"{CATEGORY_CALLBACK_PREFIX}Food & Dining"
    update = _make_callback_update(data=data)
    ctx = _make_context(
        expense_description="Coffee $5.50",
        llm_response=llm_response,
    )

    # Mock the session context manager
    mock_session = Mock()
    mock_session.__enter__ = Mock(return_value=mock_session)
    mock_session.__exit__ = Mock(return_value=False)
    mock_session_cls.return_value = mock_session

    # Mock the service's persist_with_category to return a result
    from expenses_ai_agent.services.classification import ClassificationResult

    mock_service = Mock()
    mock_service.persist_with_category.return_value = ClassificationResult(
        response=llm_response,
        is_persisted=True,
    )
    mock_service_cls.return_value = mock_service

    mock_assistant_cls.return_value = Mock()

    handler = ExpenseConversationHandler(
        db_url="sqlite:///:memory:",
        openai_api_key="test-key",
    )
    result = await handler.handle_category_selection(update, ctx)

    assert result == ConversationHandler.END
    text = update.callback_query.edit_message_text.call_args[0][0]
    assert "saved" in text.lower()
    assert len(ctx.user_data) == 0  # context cleared


# ------------------------------------------------------------------
# ConversationHandler build
# ------------------------------------------------------------------


def test_build_returns_conversation_handler() -> None:
    handler = ExpenseConversationHandler(
        db_url="sqlite:///:memory:",
        openai_api_key="test-key",
    )
    conv = handler.build()

    assert isinstance(conv, ConversationHandler)


# ------------------------------------------------------------------
# CurrencyHandler tests
# ------------------------------------------------------------------


@pytest.mark.asyncio
@patch("expenses_ai_agent.telegram.handlers.create_engine")
@patch("expenses_ai_agent.telegram.handlers.Session")
@patch("expenses_ai_agent.telegram.handlers.DBUserPreferenceRepo")
async def test_currency_command_shows_keyboard(
    mock_repo_cls: Mock,
    mock_session_cls: Mock,
    mock_create_engine: Mock,
) -> None:
    """Test that /currency command shows currency selection keyboard."""
    mock_session = Mock()
    mock_session.__enter__ = Mock(return_value=mock_session)
    mock_session.__exit__ = Mock(return_value=False)
    mock_session_cls.return_value = mock_session

    mock_repo = Mock()
    mock_repo.get_by_user_id.return_value = None  # No existing preference
    mock_repo_cls.return_value = mock_repo

    update = _make_update()
    ctx = _make_context()

    handler = CurrencyHandler(db_url="sqlite:///:memory:")
    await handler.currency_command(update, ctx)

    update.message.reply_text.assert_called_once()
    call_kwargs = update.message.reply_text.call_args
    assert "currency" in call_kwargs[0][0].lower()
    assert call_kwargs[1]["reply_markup"] is not None


@pytest.mark.asyncio
@patch("expenses_ai_agent.telegram.handlers.create_engine")
@patch("expenses_ai_agent.telegram.handlers.Session")
@patch("expenses_ai_agent.telegram.handlers.DBUserPreferenceRepo")
async def test_currency_command_shows_current_preference(
    mock_repo_cls: Mock,
    mock_session_cls: Mock,
    mock_create_engine: Mock,
) -> None:
    """Test that /currency command shows current preference."""
    mock_session = Mock()
    mock_session.__enter__ = Mock(return_value=mock_session)
    mock_session.__exit__ = Mock(return_value=False)
    mock_session_cls.return_value = mock_session

    # Mock existing preference
    mock_pref = Mock()
    mock_pref.preferred_currency = Currency.GBP
    mock_repo = Mock()
    mock_repo.get_by_user_id.return_value = mock_pref
    mock_repo_cls.return_value = mock_repo

    update = _make_update()
    ctx = _make_context()

    handler = CurrencyHandler(db_url="sqlite:///:memory:")
    await handler.currency_command(update, ctx)

    text = update.message.reply_text.call_args[0][0]
    assert "GBP" in text


@pytest.mark.asyncio
async def test_currency_command_no_user() -> None:
    """Test that /currency command does nothing when no user."""
    update = _make_update()
    update.effective_user = None
    ctx = _make_context()

    handler = CurrencyHandler(db_url="sqlite:///:memory:")
    await handler.currency_command(update, ctx)

    # Should return early without calling reply_text
    update.message.reply_text.assert_not_called()


@pytest.mark.asyncio
@patch("expenses_ai_agent.telegram.handlers.create_engine")
@patch("expenses_ai_agent.telegram.handlers.Session")
@patch("expenses_ai_agent.telegram.handlers.DBUserPreferenceRepo")
async def test_handle_currency_selection_success(
    mock_repo_cls: Mock,
    mock_session_cls: Mock,
    mock_create_engine: Mock,
) -> None:
    """Test currency selection saves preference."""
    mock_session = Mock()
    mock_session.__enter__ = Mock(return_value=mock_session)
    mock_session.__exit__ = Mock(return_value=False)
    mock_session_cls.return_value = mock_session

    mock_repo = Mock()
    mock_repo_cls.return_value = mock_repo

    data = f"{CURRENCY_CALLBACK_PREFIX}USD"
    update = _make_callback_update(data=data)
    ctx = _make_context()

    handler = CurrencyHandler(db_url="sqlite:///:memory:")
    await handler.handle_currency_selection(update, ctx)

    mock_repo.upsert.assert_called_once_with(123, Currency.USD)
    text = update.callback_query.edit_message_text.call_args[0][0]
    assert "USD" in text
    assert "set to" in text.lower()


@pytest.mark.asyncio
async def test_handle_currency_selection_invalid_callback() -> None:
    """Test that invalid callback is ignored."""
    update = _make_callback_update(data="invalid:data")
    ctx = _make_context()

    handler = CurrencyHandler(db_url="sqlite:///:memory:")
    await handler.handle_currency_selection(update, ctx)

    # Should return early without calling edit_message_text
    update.callback_query.edit_message_text.assert_not_called()


@pytest.mark.asyncio
async def test_handle_currency_selection_invalid_currency() -> None:
    """Test that invalid currency shows error."""
    data = f"{CURRENCY_CALLBACK_PREFIX}INVALID"
    update = _make_callback_update(data=data)
    ctx = _make_context()

    handler = CurrencyHandler(db_url="sqlite:///:memory:")
    await handler.handle_currency_selection(update, ctx)

    text = update.callback_query.edit_message_text.call_args[0][0]
    assert "invalid" in text.lower()


@pytest.mark.asyncio
async def test_handle_currency_selection_no_user() -> None:
    """Test that no user shows error."""
    data = f"{CURRENCY_CALLBACK_PREFIX}USD"
    update = _make_callback_update(data=data)
    update.effective_user = None
    ctx = _make_context()

    handler = CurrencyHandler(db_url="sqlite:///:memory:")
    await handler.handle_currency_selection(update, ctx)

    text = update.callback_query.edit_message_text.call_args[0][0]
    assert "identify user" in text.lower()


# ------------------------------------------------------------------
# Test help/start mention /currency
# ------------------------------------------------------------------


@pytest.mark.asyncio
async def test_help_command_mentions_currency() -> None:
    """Test that help command mentions /currency."""
    update = _make_update()
    ctx = _make_context()

    await help_command(update, ctx)

    text = update.message.reply_text.call_args[0][0]
    assert "/currency" in text


@pytest.mark.asyncio
async def test_start_command_mentions_currency() -> None:
    """Test that start command mentions /currency."""
    update = _make_update()
    ctx = _make_context()

    await start_command(update, ctx)

    text = update.message.reply_text.call_args[0][0]
    assert "/currency" in text
