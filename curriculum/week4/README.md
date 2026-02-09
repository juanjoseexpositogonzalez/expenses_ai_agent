# Week 4: Agent Reply - Telegram Integration

Welcome to Week 4! This week you will build a Telegram bot interface that allows users to track expenses through chat messages. You will implement input preprocessing, conversation handlers with human-in-the-loop (HITL) category confirmation, and user preference management.

## What You're Building This Week

```
+------------------------------------------------------------------+
|                    WEEK 4: TELEGRAM BOT                          |
+------------------------------------------------------------------+

    Telegram User: "Coffee at Starbucks $5.50"
                              |
                              v
                    +-------------------+
                    | Telegram Bot API  |
                    +-------------------+
                              |
                              v
                    +-------------------+
                    | InputPreprocessor |
                    | - Validation      |
                    | - XSS detection   |
                    | - Currency norm.  |
                    +-------------------+
                              |
                              v
                    +-------------------+
                    | Classification-   |
                    | Service           |
                    +-------------------+
                              |
                              v
                    +-------------------+
                    | InlineKeyboard    |
                    | [Food] [Other...] |
                    | (HITL Confirm)    |
                    +-------------------+
                              |
                              v (user confirms)
                    +-------------------+
                    | persist_with_     |
                    | category()        |
                    +-------------------+
                              |
                              v
                    +-------------------+
                    | "Saved! Food      |
                    |  $5.50 USD"       |
                    +-------------------+
```

## Learning Objectives

By the end of this week, you will:

- Build a Telegram bot using python-telegram-bot library
- Implement input preprocessing with validation and sanitization
- Create conversation handlers with state management
- Build inline keyboards for user interaction
- Implement human-in-the-loop (HITL) category confirmation
- Manage user preferences (currency settings)
- Handle errors gracefully in async context


## Week 4 Checklist

### Technical Milestones

- [ ] Implement `InputPreprocessor` with validation rules
- [ ] Create `ExpenseTelegramBot` wrapper class
- [ ] Implement conversation handler for expense flow
- [ ] Build inline keyboards for category selection
- [ ] Add `/currency` command for user preferences
- [ ] Implement `UserPreference` model and repository
- [ ] Add comprehensive error handling
- [ ] Pass all provided tests

### Concepts to Master

- [ ] Async/await patterns in Python
- [ ] Telegram Bot API concepts (updates, handlers, callbacks)
- [ ] Conversation state management
- [ ] Input validation and sanitization
- [ ] Human-in-the-loop (HITL) pattern for AI systems


## Key Concepts This Week

### 1. Input Preprocessing

Before sending user input to the LLM, validate and clean it:

```python
@dataclass
class PreprocessingResult:
    text: str
    is_valid: bool
    warnings: list[str]
    error: str | None = None

class InputPreprocessor:
    MIN_LENGTH = 3
    MAX_LENGTH = 500

    XSS_PATTERNS = [
        r"<script",
        r"javascript:",
        r"onerror=",
    ]

    CURRENCY_SYMBOLS = {
        "$": "USD",
        "EUR": "EUR",
        "GBP": "GBP",
        "JPY": "JPY",
    }

    def preprocess(self, text: str) -> PreprocessingResult:
        # 1. Check length
        # 2. Detect XSS patterns
        # 3. Normalize currency symbols
        # 4. Warn if no amount detected
        pass
```

### 2. Telegram Conversation Handlers

Use ConversationHandler for multi-step flows:

```python
from telegram.ext import ConversationHandler, MessageHandler, CallbackQueryHandler

AWAITING_CATEGORY = 1

class ExpenseConversationHandler:
    def build(self) -> ConversationHandler:
        return ConversationHandler(
            entry_points=[
                MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_expense_text)
            ],
            states={
                AWAITING_CATEGORY: [
                    CallbackQueryHandler(self.handle_category_selection)
                ]
            },
            fallbacks=[CommandHandler("cancel", cancel_command)],
        )

    async def handle_expense_text(self, update: Update, context):
        """Classify expense and show category keyboard."""
        # Preprocess -> Classify -> Show keyboard
        pass

    async def handle_category_selection(self, update: Update, context):
        """Handle HITL category confirmation."""
        # User clicked a category button -> persist
        pass
```

### 3. Inline Keyboards for HITL

```python
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

def build_category_confirmation_keyboard(
    suggested_category: str,
    all_categories: list[str]
) -> InlineKeyboardMarkup:
    """Build keyboard with suggested category highlighted."""
    buttons = []
    for cat in all_categories:
        # Highlight suggested category
        text = f">> {cat} <<" if cat == suggested_category else cat
        buttons.append(InlineKeyboardButton(text, callback_data=f"cat:{cat}"))

    # Arrange in rows of 3
    rows = [buttons[i:i+3] for i in range(0, len(buttons), 3)]
    return InlineKeyboardMarkup(rows)
```

### 4. User Preferences

```python
class UserPreference(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    telegram_user_id: int = Field(unique=True, index=True)
    preferred_currency: Currency = Field(default=Currency.EUR)
```

Allows users to set their preferred display currency with `/currency`.


## Project Structure After Week 4

```
expenses_ai_agent/
+-- src/
|   +-- expenses_ai_agent/
|       +-- storage/
|       |   +-- models.py      # + UserPreference
|       |   +-- repo.py        # + UserPreferenceRepository
|       +-- services/
|       |   +-- preprocessing.py  # InputPreprocessor
|       |   +-- classification.py
|       +-- telegram/
|       |   +-- __init__.py
|       |   +-- bot.py         # ExpenseTelegramBot
|       |   +-- handlers.py    # ConversationHandler, CurrencyHandler
|       |   +-- keyboards.py   # Inline keyboard builders
|       |   +-- exceptions.py  # TelegramBotError, etc.
|       +-- utils/
|           +-- logging_config.py  # Structured logging
+-- tests/
    +-- unit/
        +-- test_week4_preprocessing.py
        +-- test_week4_keyboards.py
        +-- test_week4_handlers.py
    +-- integration/
        +-- test_openai_integration.py
        +-- test_currency_integration.py
```


## Environment Variables

Add to your `.env` file:

```bash
TELEGRAM_BOT_TOKEN=your_bot_token_here
OPENAI_MODEL=gpt-4.1-nano-2025-04-14  # Default model for bot
```


## Preprocessing Rules

| Rule | Behavior |
|------|----------|
| Min length | Reject if < 3 characters |
| Max length | Reject if > 500 characters |
| XSS patterns | Reject `<script>`, `javascript:`, `onerror=` |
| Currency normalization | Convert `$` to `USD`, etc. |
| Missing amount | Warn (but allow) if no number detected |


## Build Guide

### Step 1: Input Preprocessing (`services/preprocessing.py`)

Create `InputPreprocessor` class:
- `preprocess(text: str) -> PreprocessingResult`
- Validation for length, XSS patterns
- Currency symbol normalization
- Amount detection warning

### Step 2: Telegram Exceptions (`telegram/exceptions.py`)

Define custom exceptions:
- `TelegramBotError` (base)
- `InvalidInputError`
- `ClassificationError`
- `PersistenceError`

### Step 3: Keyboards (`telegram/keyboards.py`)

Create keyboard builders:
- `build_category_confirmation_keyboard(suggested, categories)`
- `build_currency_selection_keyboard()`

### Step 4: Handlers (`telegram/handlers.py`)

Implement:
- `start_command`, `help_command`, `cancel_command`
- `CurrencyHandler` for `/currency` command
- `ExpenseConversationHandler` for expense flow

### Step 5: Bot Wrapper (`telegram/bot.py`)

Create `ExpenseTelegramBot` class:
- `__init__(token, db_url)`
- `setup()` - register handlers
- `run()` - start polling

### Step 6: User Preferences

Add to `storage/models.py`:
- `UserPreference` SQLModel

Add to `storage/repo.py`:
- `UserPreferenceRepository` (abstract)
- `InMemoryUserPreferenceRepository`
- `DBUserPreferenceRepo`


## Definition of Done

### Tests to Pass

Copy the test files from `curriculum/week4/tests/` into your `tests/unit/` directory:

- `test_week4_preprocessing.py` (10 tests)
- `test_week4_keyboards.py` (6 tests)
- `test_week4_handlers.py` (12 tests)

### Commands - All Must Succeed

| Command | Expected Result |
|---------|-----------------|
| `pytest tests/unit/test_week4_*.py -v` | All 28 tests pass |
| `ruff format --check .` | No formatting issues |
| `ruff check .` | No linting errors |

### You Are Done When

- All 28 tests pass (green)
- No ruff warnings
- You can run `expenses-telegram-bot` (will fail without valid token, but should start)
- You understand the HITL pattern for AI systems


## Human-in-the-Loop (HITL) Pattern

HITL is crucial for AI systems where confidence matters:

```
+-------+      +------+      +--------+      +-------+
|  User | ---> |  AI  | ---> | Human  | ---> | Store |
| Input |      | Pred.|      | Review |      | Final |
+-------+      +------+      +--------+      +-------+
                  |              |
                  |   Low conf.  |
                  +------>-------+
                      Ask user
                     to confirm
```

In our bot:
1. User sends "Coffee $5"
2. AI predicts "Food" (0.95 confidence)
3. Show keyboard with categories, "Food" highlighted
4. User clicks to confirm or change
5. Persist with final category (confidence=1.0 if overridden)


## Common Issues and Solutions

| Issue | Solution |
|-------|----------|
| "telegram.error.InvalidToken" | Check TELEGRAM_BOT_TOKEN in .env |
| Async test failures | Use `pytest-asyncio` and `@pytest.mark.asyncio` |
| Mock Update object | Create proper mock with `update.effective_user.id` etc. |
| Callback data too long | Telegram limits to 64 bytes; use short codes |
| Session closed in handler | Create new session per request, or use context manager |


## Looking Ahead

In Week 5, you will build the web interface:

- FastAPI REST API with dependency injection
- Streamlit dashboard with Plotly visualizations
- Multiuser support with user ID from headers
- Analytics endpoints for category totals

Your preprocessing and classification services will be reused!

---

**Testing tip**: Use `pytest-asyncio` for testing async handlers. Mock the Update and Context objects carefully - the tests show you exactly how.
