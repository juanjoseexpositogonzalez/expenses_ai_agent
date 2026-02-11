# Week 4 Success Criteria

Use this checklist to verify you've completed all Week 4 requirements.


## Validation Commands

All of these commands must succeed:

| Command | Expected Result |
|---------|-----------------|
| `pytest tests/unit/test_week4_preprocessing.py -v` | All 12 tests pass |
| `pytest tests/unit/test_week4_keyboards.py -v` | All 7 tests pass |
| `pytest tests/unit/test_week4_handlers.py -v` | All 14 tests pass |
| `ruff format --check .` | No formatting issues |
| `ruff check .` | No linting errors |


## Technical Checklist

### Input Preprocessing (`services/preprocessing.py`)

- [ ] `PreprocessingResult` dataclass with `text`, `is_valid`, `warnings`, `error`
- [ ] `InputPreprocessor` class with `preprocess()` method
- [ ] Length validation (3-500 characters)
- [ ] XSS pattern detection (`<script>`, `javascript:`, `onerror=`)
- [ ] Currency symbol normalization
- [ ] Warning for missing numeric amounts
- [ ] Whitespace trimming


### Telegram Keyboards (`telegram/keyboards.py`)

- [ ] `build_category_confirmation_keyboard(suggested_category, all_categories)`
- [ ] Returns `InlineKeyboardMarkup`
- [ ] All categories appear as buttons
- [ ] Suggested category highlighted with `>>` and `<<`
- [ ] `build_currency_selection_keyboard()`
- [ ] Common currencies included (EUR, USD, GBP)
- [ ] All buttons have `callback_data`


### Telegram Exceptions (`telegram/exceptions.py`)

- [ ] `TelegramBotError` base exception
- [ ] `InvalidInputError` for preprocessing failures
- [ ] `ClassificationError` for LLM failures
- [ ] (Optional) `PersistenceError` for database failures


### Telegram Handlers (`telegram/handlers.py`)

- [ ] `start_command()` returns welcome message
- [ ] `help_command()` returns usage instructions
- [ ] `cancel_command()` returns `ConversationHandler.END`
- [ ] `ExpenseConversationHandler` class with `build()` method
- [ ] `handle_expense_text()` preprocesses, classifies, shows keyboard
- [ ] `handle_category_selection()` persists with user's category choice
- [ ] `CurrencyHandler` class for currency preferences
- [ ] `currency_command()` shows currency keyboard
- [ ] `handle_currency_selection()` saves user preference


## Conceptual Understanding

You should be able to answer:

1. **Why preprocess input before LLM calls?**
   - Validates length to avoid wasted API calls
   - Detects XSS patterns for security
   - Normalizes currency for consistency
   - Warns about missing amounts

2. **Why use ConversationHandler?**
   - Manages state across multiple messages
   - Handles multi-step flows (classify -> confirm)
   - Provides entry points, states, and fallbacks

3. **What is Human-in-the-Loop?**
   - AI suggests, human confirms
   - User can override AI classification
   - Persisted with confidence=1.0 (user verified)

4. **Why use inline keyboards?**
   - Eliminates typing errors
   - One tap to select category
   - Visual highlighting of AI suggestion

5. **How does context.user_data work?**
   - Persists data between handler calls
   - Scoped to individual user
   - Stores classification for confirmation step


## You Are Done When

- All 33 tests pass (green)
- No ruff warnings
- You understand the HITL pattern
- You can explain conversation state management


## Common Issues and Solutions

| Issue | Solution |
|-------|----------|
| "Module not found: telegram" | `pip install python-telegram-bot` |
| "coroutine was never awaited" | Add `await` before async calls |
| "callback_data too long" | Keep callback_data under 64 bytes |
| Tests hang on async | Use `@pytest.mark.asyncio` decorator |
| Import errors | Check `__init__.py` exports |
| "ConversationHandler.END undefined" | Import from `telegram.ext` |


## Test Organization

Your test files should be:

```
tests/
    unit/
        test_week4_preprocessing.py    # 12 tests
        test_week4_keyboards.py        # 7 tests
        test_week4_handlers.py         # 14 tests (includes exceptions)
```

Run all Week 4 tests:
```bash
pytest tests/unit/test_week4_*.py -v
```


## Integration Test (Optional)

If you have a Telegram bot token, test the bot manually:

```bash
# Set environment variable
export TELEGRAM_BOT_TOKEN="your-token-here"

# Start the bot
expenses-telegram-bot
```

Then in Telegram:
1. Send `/start` to your bot
2. Send "Coffee at Starbucks $5.50"
3. Verify category keyboard appears
4. Tap a category button
5. Verify confirmation message


## Next Steps

Once all tests pass and you understand the concepts:

1. Review the architecture diagram in `01-welcome.md`
2. Consider edge cases (network errors, API limits)
3. Prepare for Week 5: REST API and Web Dashboard
