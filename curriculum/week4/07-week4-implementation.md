# Week 4 Implementation: Telegram Integration

This implementation exercise teaches you to build the Telegram bot interface with input preprocessing, conversation handlers, inline keyboards, and human-in-the-loop category confirmation.


## Learning Goals

By the end of this implementation, you will:

- Implement InputPreprocessor with validation and XSS protection
- Build inline keyboards for category and currency selection
- Create conversation handlers for multi-step expense entry
- Implement HITL category confirmation with user overrides
- Handle Telegram callbacks and message updates


## What You're Building

**Input:** Telegram message with expense description

**Output:** Classified expense with keyboard confirmation, persisted to database

```
User: Coffee at Starbucks $5.50

Bot: Classified as Food (95% confidence)
     Amount: $5.50 USD

     [>> Food <<] [Transport] [Entertainment]
     [Shopping]   [Health]    [Bills]

User: (taps Food button)

Bot: Saved! Expense recorded as Food.
```


## Project Structure

```
src/expenses_ai_agent/
    services/
        preprocessing.py      # InputPreprocessor, PreprocessingResult
    telegram/
        __init__.py
        bot.py               # ExpenseTelegramBot wrapper
        handlers.py          # ConversationHandler, CurrencyHandler
        keyboards.py         # build_category_confirmation_keyboard, etc.
        exceptions.py        # Custom exceptions
```


## Test Suite

Copy these tests to your `tests/unit/` directory. All three test files must pass.


### Test 1: Input Preprocessing

Create `tests/unit/test_week4_preprocessing.py`:

```python
"""
Week 4 - Definition of Done: Input Preprocessing

Copy this file to your project's tests/unit/ directory.
Run: pytest tests/unit/test_week4_preprocessing.py -v
All tests must pass to complete Week 4's preprocessing milestone.

These tests verify your implementation of:
- InputPreprocessor class
- PreprocessingResult dataclass
- Validation rules (length, XSS, currency normalization)
"""

import pytest


class TestPreprocessingResult:
    """Tests for the PreprocessingResult dataclass."""

    def test_result_has_required_fields(self):
        """PreprocessingResult should have text, is_valid, warnings, error."""
        from expenses_ai_agent.services.preprocessing import PreprocessingResult

        result = PreprocessingResult(
            text="Coffee $5",
            is_valid=True,
            warnings=[],
            error=None,
        )

        assert result.text == "Coffee $5"
        assert result.is_valid is True
        assert result.warnings == []
        assert result.error is None

    def test_result_with_warnings(self):
        """Result can include warnings without failing validation."""
        from expenses_ai_agent.services.preprocessing import PreprocessingResult

        result = PreprocessingResult(
            text="Coffee",
            is_valid=True,
            warnings=["No amount detected"],
        )

        assert result.is_valid is True
        assert len(result.warnings) == 1

    def test_result_with_error(self):
        """Result with error should be invalid."""
        from expenses_ai_agent.services.preprocessing import PreprocessingResult

        result = PreprocessingResult(
            text="ab",
            is_valid=False,
            warnings=[],
            error="Input too short",
        )

        assert result.is_valid is False
        assert result.error is not None


class TestInputPreprocessor:
    """Tests for the InputPreprocessor class."""

    @pytest.fixture
    def preprocessor(self):
        """Create an InputPreprocessor instance."""
        from expenses_ai_agent.services.preprocessing import InputPreprocessor

        return InputPreprocessor()

    def test_valid_input_passes(self, preprocessor):
        """Normal expense description should pass validation."""
        result = preprocessor.preprocess("Coffee at Starbucks $5.50")

        assert result.is_valid is True
        assert result.error is None

    def test_input_too_short_fails(self, preprocessor):
        """Input shorter than minimum length should fail."""
        result = preprocessor.preprocess("ab")

        assert result.is_valid is False
        assert "short" in result.error.lower() or "length" in result.error.lower()

    def test_input_too_long_fails(self, preprocessor):
        """Input longer than maximum length should fail."""
        long_text = "a" * 501
        result = preprocessor.preprocess(long_text)

        assert result.is_valid is False
        assert "long" in result.error.lower() or "length" in result.error.lower()

    def test_xss_script_tag_rejected(self, preprocessor):
        """Input with <script> tag should be rejected."""
        result = preprocessor.preprocess("Coffee <script>alert('xss')</script>")

        assert result.is_valid is False
        assert "xss" in result.error.lower() or "script" in result.error.lower() or "invalid" in result.error.lower()

    def test_xss_javascript_rejected(self, preprocessor):
        """Input with javascript: protocol should be rejected."""
        result = preprocessor.preprocess("Check javascript:void(0)")

        assert result.is_valid is False

    def test_currency_symbol_normalized(self, preprocessor):
        """Currency symbols should be normalized to codes."""
        result = preprocessor.preprocess("Coffee for $5.50")

        # $ should be normalized to USD in some form
        assert result.is_valid is True
        # The normalized text might contain USD or the original $
        # depending on implementation

    def test_euro_symbol_normalized(self, preprocessor):
        """Euro symbol should be normalized."""
        result = preprocessor.preprocess("Lunch for 15 EUR")

        assert result.is_valid is True

    def test_missing_amount_warns(self, preprocessor):
        """Input without numeric amount should produce warning."""
        result = preprocessor.preprocess("Coffee at cafe")

        assert result.is_valid is True  # Still valid, just warn
        # Should have a warning about missing amount
        assert len(result.warnings) > 0 or "amount" in str(result.warnings).lower()

    def test_whitespace_handled(self, preprocessor):
        """Leading/trailing whitespace should be handled."""
        result = preprocessor.preprocess("  Coffee $5  ")

        assert result.is_valid is True
        assert result.text.strip() == result.text or "Coffee" in result.text
```


### Test 2: Telegram Keyboards

Create `tests/unit/test_week4_keyboards.py`:

```python
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
```


### Test 3: Telegram Handlers

Create `tests/unit/test_week4_handlers.py`:

```python
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
```


## Implementation Strategy

Work through these steps in order. Each step targets specific tests.


### Step 1: Create PreprocessingResult and InputPreprocessor

Build `services/preprocessing.py` with validation logic.

**Target tests:** `TestPreprocessingResult`, `TestInputPreprocessor` (12 tests)

**Key requirements:**
- `PreprocessingResult` dataclass with `text`, `is_valid`, `warnings`, `error`
- Length validation (3-500 characters)
- XSS pattern detection (`<script>`, `javascript:`)
- Currency symbol normalization
- Warning for missing amounts


### Step 2: Create Telegram Keyboards

Build `telegram/keyboards.py` with keyboard builders.

**Target tests:** `TestCategoryKeyboard`, `TestCurrencyKeyboard` (7 tests)

**Key requirements:**
- `build_category_confirmation_keyboard(suggested_category, all_categories)`
- `build_currency_selection_keyboard()`
- Highlight suggested category with `>>` and `<<`
- Include callback_data for each button


### Step 3: Create Custom Exceptions

Build `telegram/exceptions.py` with exception hierarchy.

**Target tests:** `TestTelegramExceptions` (3 tests)

**Key requirements:**
- `TelegramBotError` base exception
- `InvalidInputError` for preprocessing failures
- `ClassificationError` for LLM failures


### Step 4: Create Command Handlers

Add `start_command`, `help_command`, `cancel_command` to `telegram/handlers.py`.

**Target tests:** `TestCommandHandlers` (3 tests)

**Key requirements:**
- `start_command` returns welcome message
- `help_command` returns usage instructions
- `cancel_command` returns `ConversationHandler.END`


### Step 5: Create ExpenseConversationHandler

Build the main conversation handler in `telegram/handlers.py`.

**Target tests:** `TestExpenseConversationHandler` (5 tests)

**Key requirements:**
- `__init__(db_url)` to configure database
- `build()` returns `ConversationHandler`
- `handle_expense_text()` preprocesses, classifies, shows keyboard
- `handle_category_selection()` persists with user's choice


### Step 6: Create CurrencyHandler

Add currency preference handling to `telegram/handlers.py`.

**Target tests:** `TestCurrencyHandler` (3 tests)

**Key requirements:**
- `currency_command()` shows currency keyboard
- `handle_currency_selection()` saves preference


## Helpful Concepts


### Regex for XSS Detection

```python
import re

XSS_PATTERNS = [
    re.compile(r"<script", re.IGNORECASE),
    re.compile(r"javascript:", re.IGNORECASE),
    re.compile(r"onerror\s*=", re.IGNORECASE),
]

def detect_xss(text: str) -> bool:
    return any(p.search(text) for p in XSS_PATTERNS)
```

[Documentation: re module](https://docs.python.org/3/library/re.html)


### Chunking Lists for Keyboard Rows

```python
def chunk(items: list, size: int) -> list[list]:
    """Split list into chunks."""
    return [items[i : i + size] for i in range(0, len(items), size)]

# Usage
buttons = ["A", "B", "C", "D", "E"]
rows = chunk(buttons, 3)  # [["A", "B", "C"], ["D", "E"]]
```


### Async Function Signatures

```python
from telegram import Update
from telegram.ext import ContextTypes

async def handler(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> int:
    """Handler signature for python-telegram-bot v20+."""
    await update.message.reply_text("Hello!")
    return NEXT_STATE
```


### Mocking Async Functions

```python
from unittest.mock import AsyncMock, MagicMock

# Mock async method
update = MagicMock()
update.message.reply_text = AsyncMock()

# Verify call
update.message.reply_text.assert_called_once()
```


## Validation Checklist

Before moving on, verify:

- [ ] All tests pass: `pytest tests/unit/test_week4_*.py -v`
- [ ] No linting errors: `ruff check src/`
- [ ] Code is formatted: `ruff format .`


## Debugging Tips


### "Module not found: telegram"

Install python-telegram-bot:
```bash
pip install python-telegram-bot
```


### "RuntimeWarning: coroutine was never awaited"

Handler functions must be `async def` and called with `await`:
```python
# Wrong
def handler(update, context):
    update.message.reply_text("Hi")  # Missing await

# Correct
async def handler(update, context):
    await update.message.reply_text("Hi")
```


### "ConversationHandler.END is not defined"

Import from telegram.ext:
```python
from telegram.ext import ConversationHandler

return ConversationHandler.END
```


### "callback_query.answer() was never awaited"

Always await callback query methods:
```python
await query.answer()
await query.edit_message_text("Done!")
```


## Step Hints


### Step 1: Preprocessing Hint

Structure your PreprocessingResult with default values:

```python
@dataclass
class PreprocessingResult:
    text: str
    is_valid: bool
    warnings: list[str] = field(default_factory=list)
    error: str | None = None
```

For XSS detection, use `re.IGNORECASE` to catch variations like `<SCRIPT>`.


### Step 2: Keyboards Hint

Remember to include `callback_data` on every button:

```python
button = InlineKeyboardButton(
    text="Food",
    callback_data="cat:Food",  # This is what handler receives
)
```

Use list slicing to arrange buttons into rows of 3.


### Step 3: Exceptions Hint

Create a hierarchy with a base exception:

```python
class TelegramBotError(Exception):
    """Base exception for Telegram bot."""
    pass

class InvalidInputError(TelegramBotError):
    """Raised when input fails preprocessing."""
    pass
```


### Step 4: Command Handlers Hint

Command handlers are standalone async functions:

```python
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text("Welcome! Send me an expense.")
    return WAITING_FOR_EXPENSE
```

They can be at module level or methods on a class.


### Step 5: Conversation Handler Hint

Store classification response in `context.user_data` for the next step:

```python
# In handle_expense_text
context.user_data["classification_response"] = response

# In handle_category_selection
response = context.user_data["classification_response"]
```


### Step 6: Currency Handler Hint

Parse callback data to get the currency code:

```python
# callback_data = "currency:EUR"
currency_code = query.data.split(":")[1]  # "EUR"
```

---

Your Week 4 Telegram integration is complete when all 33 tests pass.
