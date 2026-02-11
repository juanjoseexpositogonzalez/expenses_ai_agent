# Conversation Handlers

Conversation handlers manage multi-step interactions in Telegram bots. Unlike simple command-response patterns, conversations maintain state across multiple messages, allowing complex workflows like expense entry with confirmation.


## Why Conversation Handlers Exist

Simple bot interactions are stateless:

```
User: /help
Bot: Here's how to use me...
```

But expense tracking needs multiple steps:

```
Step 1: User sends expense text
Step 2: Bot classifies and shows category keyboard
Step 3: User taps category button
Step 4: Bot confirms and saves
```

Each step must know what happened before. `ConversationHandler` from python-telegram-bot provides this state management.


## The python-telegram-bot Library

The `python-telegram-bot` library provides an async-first API for building Telegram bots:

```python
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ConversationHandler,
    ContextTypes,
    filters,
)
```

**Key classes:**
- `Update` - Incoming message or callback from Telegram
- `ContextTypes.DEFAULT_TYPE` - Context with bot data and user data
- `ConversationHandler` - State machine for multi-step flows


## ConversationHandler States

A conversation is a finite state machine:

```
                    WAITING_FOR_EXPENSE
                            |
                            v (user sends text)
                    WAITING_FOR_CATEGORY
                            |
                            v (user taps button)
                    ConversationHandler.END
```

Define states as integer constants:

```python
# Conversation states
WAITING_FOR_EXPENSE = 0
WAITING_FOR_CATEGORY = 1
```


## Building a ConversationHandler

The handler maps states to message handlers:

```python
from telegram.ext import ConversationHandler, CommandHandler, MessageHandler, CallbackQueryHandler, filters

def build(self) -> ConversationHandler:
    """Build the conversation handler."""
    return ConversationHandler(
        entry_points=[
            CommandHandler("start", self.start_command),
            MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_expense_text),
        ],
        states={
            WAITING_FOR_CATEGORY: [
                CallbackQueryHandler(self.handle_category_selection),
            ],
        },
        fallbacks=[
            CommandHandler("cancel", self.cancel_command),
        ],
    )
```

**Components:**
- `entry_points` - How users start the conversation
- `states` - Handlers for each state
- `fallbacks` - Handlers that work in any state (like /cancel)


## Handler Functions

Each handler is an async function that returns the next state:

```python
async def handle_expense_text(
    self,
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> int:
    """Handle incoming expense text."""
    # Preprocess and classify
    result = self._preprocessor.preprocess(update.message.text)

    if not result.is_valid:
        await update.message.reply_text(f"Error: {result.error}")
        return ConversationHandler.END

    classification = self._service.classify(result.text)

    # Store in context for next step
    context.user_data["expense_description"] = result.text
    context.user_data["classification_response"] = classification.response

    # Show keyboard
    keyboard = build_category_confirmation_keyboard(
        suggested_category=classification.response.category,
        all_categories=self._get_categories(),
    )

    await update.message.reply_text(
        f"Classified as {classification.response.category}\n"
        f"Amount: {classification.response.total_amount} {classification.response.currency}",
        reply_markup=keyboard,
    )

    return WAITING_FOR_CATEGORY
```


## Using context.user_data

The context object persists data between handler calls:

```python
# In handle_expense_text (step 1)
context.user_data["expense_description"] = "Coffee $5.50"
context.user_data["classification_response"] = response

# In handle_category_selection (step 2)
description = context.user_data["expense_description"]
response = context.user_data["classification_response"]
```

This is how the bot remembers what the user said when they tap a category button.


## Callback Queries

When users tap inline keyboard buttons, Telegram sends a callback query instead of a message:

```python
async def handle_category_selection(
    self,
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> int:
    """Handle category button tap."""
    query = update.callback_query
    await query.answer()  # Required to stop loading indicator

    # Parse callback data: "cat:Food" -> "Food"
    category_name = query.data.split(":")[1]

    # Get stored data
    description = context.user_data["expense_description"]
    response = context.user_data["classification_response"]

    # Persist with user's category choice
    self._service.persist_with_category(
        expense_description=description,
        category_name=category_name,
        response=response,
    )

    await query.edit_message_text(f"Saved as {category_name}!")

    return ConversationHandler.END
```

**Important:** Always call `query.answer()` to acknowledge the callback.


## Command Handlers

Standard commands like /start and /help:

```python
async def start_command(
    self,
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> int:
    """Handle /start command."""
    await update.message.reply_text(
        "Welcome! Send me an expense like:\n"
        "Coffee at Starbucks $5.50"
    )
    return WAITING_FOR_EXPENSE


async def help_command(
    self,
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    """Handle /help command."""
    await update.message.reply_text(
        "Commands:\n"
        "/start - Start tracking\n"
        "/currency - Set preferred currency\n"
        "/cancel - Cancel current operation"
    )


async def cancel_command(
    self,
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> int:
    """Handle /cancel command."""
    await update.message.reply_text("Operation cancelled.")
    return ConversationHandler.END
```


## Python Comparison: State Management

| Approach | Use Case |
|----------|----------|
| Global variables | Never in async code |
| `context.user_data` | Per-user state in Telegram |
| `context.bot_data` | Shared state across users |
| Database | Persistent state across restarts |


## Error Handling

Wrap handler logic in try/except to show friendly errors:

```python
async def handle_expense_text(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    try:
        # Classification logic...
        return WAITING_FOR_CATEGORY

    except ClassificationError as e:
        await update.message.reply_text(f"Classification failed: {e}")
        return ConversationHandler.END

    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        await update.message.reply_text("An error occurred. Please try again.")
        return ConversationHandler.END
```


## Conversation Handler in Our Bot

The full structure:

```python
class ExpenseConversationHandler:
    """Handles multi-step expense entry conversation."""

    def __init__(self, db_url: str):
        self._preprocessor = InputPreprocessor()
        self._db_url = db_url

    def _build_assistant(self) -> OpenAIAssistant:
        """Build LLM assistant."""
        return OpenAIAssistant()

    def build(self) -> ConversationHandler:
        """Build the ConversationHandler for Application."""
        return ConversationHandler(
            entry_points=[
                CommandHandler("start", start_command),
                MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_expense_text),
            ],
            states={
                WAITING_FOR_CATEGORY: [
                    CallbackQueryHandler(self.handle_category_selection),
                ],
            },
            fallbacks=[
                CommandHandler("cancel", cancel_command),
            ],
        )
```


## Further Reading

- [python-telegram-bot documentation](https://docs.python-telegram-bot.org/)
- [ConversationHandler guide](https://github.com/python-telegram-bot/python-telegram-bot/wiki/Extensions---ConversationHandler)
- [Telegram Bot API](https://core.telegram.org/bots/api)
