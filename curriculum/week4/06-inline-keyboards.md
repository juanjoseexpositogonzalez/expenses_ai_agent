# Inline Keyboards

Inline keyboards are buttons that appear directly within messages, allowing users to interact without typing. They are essential for HITL patterns because they make category selection fast and error-free.


## Why Inline Keyboards Exist

Text-based category selection is error-prone:

```
Bot: Select category: Food, Transport, Entertainment, Shopping...
User: food
Bot: Category not found. Did you mean "Food"?
User: Food
Bot: Saved!
```

Inline keyboards eliminate this:

```
Bot: Select category:
     [Food] [Transport] [Entertainment]

User: (taps Food button)

Bot: Saved as Food!
```

One tap, no typos, clear options.


## InlineKeyboardButton and InlineKeyboardMarkup

The building blocks:

```python
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

# Single button
button = InlineKeyboardButton(
    text="Food",           # What user sees
    callback_data="cat:Food",  # What bot receives when tapped
)

# Keyboard with rows of buttons
keyboard = InlineKeyboardMarkup([
    [button1, button2, button3],  # Row 1
    [button4, button5, button6],  # Row 2
])
```

**Important:** `callback_data` is limited to 64 bytes. Use prefixes like `cat:` to identify button types.


## Building the Category Keyboard

The category keyboard shows all 12 categories with the AI suggestion highlighted:

```python
from telegram import InlineKeyboardButton, InlineKeyboardMarkup


def build_category_confirmation_keyboard(
    suggested_category: str,
    all_categories: list[str],
    columns: int = 3,
) -> InlineKeyboardMarkup:
    """
    Build keyboard for category selection.

    Args:
        suggested_category: AI's suggested category (will be highlighted)
        all_categories: All available category names
        columns: Number of buttons per row

    Returns:
        InlineKeyboardMarkup with category buttons
    """
    buttons = []

    for category in all_categories:
        # Highlight the suggested category
        if category == suggested_category:
            text = f">> {category} <<"
        else:
            text = category

        button = InlineKeyboardButton(
            text=text,
            callback_data=f"cat:{category}",
        )
        buttons.append(button)

    # Arrange into rows
    rows = []
    for i in range(0, len(buttons), columns):
        rows.append(buttons[i : i + columns])

    return InlineKeyboardMarkup(rows)
```

Result with `suggested_category="Food"`:

```
[>> Food <<] [Transport]    [Entertainment]
[Shopping]   [Health]       [Bills]
[Education]  [Travel]       [Services]
[Gifts]      [Investments]  [Other]
```


## Building the Currency Keyboard

For user preferences, a currency selection keyboard:

```python
from telegram import InlineKeyboardButton, InlineKeyboardMarkup


def build_currency_selection_keyboard() -> InlineKeyboardMarkup:
    """
    Build keyboard for currency selection.

    Layout: 3 buttons per row for common currencies.
    """
    currencies = [
        ("EUR", "Euro"),
        ("USD", "US Dollar"),
        ("GBP", "British Pound"),
        ("JPY", "Japanese Yen"),
        ("CHF", "Swiss Franc"),
        ("CAD", "Canadian Dollar"),
        ("AUD", "Australian Dollar"),
        ("CNY", "Chinese Yuan"),
        ("INR", "Indian Rupee"),
        ("MXN", "Mexican Peso"),
    ]

    buttons = []
    for code, name in currencies:
        button = InlineKeyboardButton(
            text=f"{code}",
            callback_data=f"currency:{code}",
        )
        buttons.append(button)

    # Arrange: 3-3-3-1 layout
    rows = [
        buttons[0:3],
        buttons[3:6],
        buttons[6:9],
        buttons[9:10],
    ]

    return InlineKeyboardMarkup(rows)
```

Result:

```
[EUR] [USD] [GBP]
[JPY] [CHF] [CAD]
[AUD] [CNY] [INR]
[MXN]
```


## Callback Data Patterns

Use prefixes to identify button types:

```python
# Category selection
callback_data="cat:Food"
callback_data="cat:Transport"

# Currency selection
callback_data="currency:EUR"
callback_data="currency:USD"

# Parsing in handler
def parse_callback(data: str) -> tuple[str, str]:
    """Parse callback data into (type, value)."""
    parts = data.split(":", 1)
    return parts[0], parts[1]

# Usage
type_, value = parse_callback("cat:Food")
# type_ = "cat", value = "Food"
```


## Handling Callback Queries

When a user taps a button:

```python
async def handle_category_selection(
    self,
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> int:
    """Handle category button tap."""
    query = update.callback_query

    # IMPORTANT: Always answer the callback
    await query.answer()

    # Parse the callback data
    category = query.data.split(":")[1]

    # Process selection...

    # Update the message (removes keyboard)
    await query.edit_message_text(f"Saved as {category}!")

    return ConversationHandler.END
```

**Key points:**
1. `query.answer()` - Stops the loading spinner on the button
2. `query.data` - Contains the `callback_data` from the button
3. `query.edit_message_text()` - Updates the original message


## Keyboard Layout Best Practices

| Principle | Reason |
|-----------|--------|
| 3 buttons per row | Fits most phone screens |
| Highlight suggestion | Reduces cognitive load |
| Short button text | Prevents text overflow |
| Consistent ordering | Builds muscle memory |
| Prefix callback data | Easy routing in handlers |


## Python Comparison: List Chunking

Arranging buttons into rows requires chunking a list:

```python
# Manual chunking
def chunk(items: list, size: int) -> list[list]:
    """Split list into chunks of given size."""
    return [items[i : i + size] for i in range(0, len(items), size)]

# Usage
buttons = ["A", "B", "C", "D", "E", "F", "G"]
rows = chunk(buttons, 3)
# [["A", "B", "C"], ["D", "E", "F"], ["G"]]
```

This pattern is common when building grid layouts.


## Dynamic Keyboards

Sometimes keyboards need to change based on context:

```python
def build_confirmation_keyboard(
    can_edit: bool = True,
    can_delete: bool = True,
) -> InlineKeyboardMarkup:
    """Build keyboard with optional actions."""
    buttons = []

    if can_edit:
        buttons.append(
            InlineKeyboardButton(text="Edit", callback_data="action:edit")
        )

    if can_delete:
        buttons.append(
            InlineKeyboardButton(text="Delete", callback_data="action:delete")
        )

    buttons.append(
        InlineKeyboardButton(text="Cancel", callback_data="action:cancel")
    )

    return InlineKeyboardMarkup([buttons])
```


## Inline Keyboards in Our Bot

The expense flow uses keyboards at two points:

1. **Category Confirmation** - After classification:

```python
keyboard = build_category_confirmation_keyboard(
    suggested_category=response.category,
    all_categories=self._get_categories(),
)

await update.message.reply_text(
    f"Classified as {response.category}",
    reply_markup=keyboard,
)
```

2. **Currency Selection** - For user preferences:

```python
keyboard = build_currency_selection_keyboard()

await update.message.reply_text(
    "Select your preferred currency:",
    reply_markup=keyboard,
)
```


## Testing Keyboards

Keyboards can be tested without Telegram:

```python
def test_keyboard_has_all_categories():
    categories = ["Food", "Transport", "Entertainment"]
    keyboard = build_category_confirmation_keyboard(
        suggested_category="Food",
        all_categories=categories,
    )

    # Flatten all buttons
    all_buttons = [btn for row in keyboard.inline_keyboard for btn in row]

    # Check each category appears
    button_texts = [btn.text for btn in all_buttons]
    for cat in categories:
        assert any(cat in text for text in button_texts)


def test_suggested_category_highlighted():
    keyboard = build_category_confirmation_keyboard(
        suggested_category="Transport",
        all_categories=["Food", "Transport"],
    )

    all_buttons = [btn for row in keyboard.inline_keyboard for btn in row]
    transport_button = [btn for btn in all_buttons if "Transport" in btn.text][0]

    assert ">>" in transport_button.text or "<<" in transport_button.text
```


## Further Reading

- [Telegram Bot API: Inline Keyboards](https://core.telegram.org/bots/api#inlinekeyboardmarkup)
- [python-telegram-bot: Inline Keyboards](https://docs.python-telegram-bot.org/en/stable/telegram.inlinekeyboardmarkup.html)
- [Best Practices for Telegram Keyboards](https://core.telegram.org/bots#keyboards)
