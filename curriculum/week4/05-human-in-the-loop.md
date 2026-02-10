# Human-in-the-Loop Pattern

Human-in-the-loop (HITL) is a design pattern where AI systems incorporate human judgment at critical decision points. For expense classification, this means the LLM suggests a category, but the user confirms or overrides before saving.


## Why HITL Matters

AI classification has inherent limitations:

```
Input: "Uber to airport"
AI: Transport (99% confidence) - Correct

Input: "Uber Eats dinner"
AI: Transport (85% confidence) - Wrong! Should be Food

Input: "Amazon purchase"
AI: Shopping (70% confidence) - Maybe, could be Books/Electronics

Input: "Payment to John"
AI: Other (45% confidence) - No idea, needs human judgment
```

Without HITL, errors accumulate in the database. With HITL, users catch mistakes before they become permanent.


## The HITL Flow

```
+------------------+
|  User Input      |  "Uber Eats dinner $25"
+------------------+
         |
         v
+------------------+
|  LLM Classifies  |  Transport (85%), $25 USD
+------------------+
         |
         v
+------------------+
|  Show Keyboard   |  [Transport] [>> Food <<] [Shopping]
+------------------+
         |
         v (user taps)
+------------------+
|  Persist with    |  Food, $25 USD, confidence=1.0
|  User's Choice   |
+------------------+
```

The key insight: **AI proposes, human disposes**.


## Confidence-Based UX

Use AI confidence to adjust the UI:

```python
def format_classification_message(response: ExpenseCategorizationResponse) -> str:
    """Format classification with confidence indicator."""
    confidence = response.confidence

    if confidence >= 0.9:
        indicator = "High confidence"
    elif confidence >= 0.7:
        indicator = "Medium confidence"
    else:
        indicator = "Low confidence - please verify"

    return (
        f"Category: {response.category} ({confidence:.0%})\n"
        f"Amount: {response.total_amount} {response.currency}\n"
        f"{indicator}"
    )
```

Low confidence prompts more careful review:

```
High confidence (90%+):
  Category: Food (95%)
  Amount: $5.50 USD

Low confidence (<70%):
  Category: Other (45%)
  Amount: $100.00 USD
  Low confidence - please verify
```


## Highlighting the Suggestion

The keyboard visually emphasizes the AI suggestion:

```python
def build_category_confirmation_keyboard(
    suggested_category: str,
    all_categories: list[str],
) -> InlineKeyboardMarkup:
    """Build keyboard with suggested category highlighted."""
    buttons = []
    for category in all_categories:
        if category == suggested_category:
            # Highlight with arrows
            text = f">> {category} <<"
        else:
            text = category

        buttons.append(
            InlineKeyboardButton(
                text=text,
                callback_data=f"cat:{category}",
            )
        )
    # Arrange in rows of 3
    ...
```

Result:
```
[>> Food <<] [Transport] [Entertainment]
[Shopping]   [Health]    [Bills]
```

The user sees immediately what the AI suggests while having easy access to alternatives.


## Storing User Corrections

When the user selects a category (whether confirming or overriding), we store with confidence=1.0:

```python
def persist_with_category(
    self,
    expense_description: str,
    category_name: str,
    response: ExpenseCategorizationResponse,
) -> Expense:
    """
    Persist expense with user-selected category.

    The user's selection overrides AI classification.
    We set confidence=1.0 because human confirmed.
    """
    category = self._category_repo.get(category_name)

    expense = Expense(
        amount=response.total_amount,
        currency=response.currency,
        description=expense_description,
        category=category,
        confidence=Decimal("1.0"),  # Human verified
    )

    self._expense_repo.add(expense)
    return expense
```

**Why confidence=1.0?**
The stored expense represents what the user confirmed, not what the AI guessed. For analytics and future training, we want to distinguish human-verified entries from pure AI classifications.


## Tracking Corrections

For improving the model, track when users override:

```python
@dataclass
class ClassificationFeedback:
    """Tracks AI classification vs user choice."""

    original_input: str
    ai_category: str
    ai_confidence: float
    user_category: str
    was_override: bool  # True if user_category != ai_category


def record_feedback(response: ExpenseCategorizationResponse, user_choice: str) -> ClassificationFeedback:
    """Record classification feedback for analysis."""
    return ClassificationFeedback(
        original_input=response.comments or "",
        ai_category=response.category,
        ai_confidence=response.confidence,
        user_category=user_choice,
        was_override=(response.category != user_choice),
    )
```

This data can later train better models or tune prompts.


## HITL Design Principles

1. **Always show AI suggestion** - Users should see what the AI thinks
2. **Make correction easy** - One tap to change category
3. **Never force AI decision** - User always has final say
4. **Indicate confidence** - Help users know when to verify
5. **Store human decision** - Persist what user confirmed, not AI guess


## Python Comparison: Validation Patterns

| Pattern | Description | Use Case |
|---------|-------------|----------|
| Pre-validation | Validate before action | Form validation |
| Post-validation | Validate after action | Spell check in editors |
| HITL | Human confirms AI decision | Classification, moderation |

HITL is a special case of post-validation where the AI does the first pass.


## HITL in Our Bot

The conversation flow implements HITL:

```python
async def handle_expense_text(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    # Step 1: AI classifies
    result = self._preprocessor.preprocess(update.message.text)
    classification = self._service.classify(result.text)

    # Store for step 2
    context.user_data["classification_response"] = classification.response

    # Show keyboard with AI suggestion highlighted
    keyboard = build_category_confirmation_keyboard(
        suggested_category=classification.response.category,
        all_categories=self._get_categories(),
    )

    await update.message.reply_text(
        format_classification_message(classification.response),
        reply_markup=keyboard,
    )

    return WAITING_FOR_CATEGORY


async def handle_category_selection(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    # Step 2: Human confirms/overrides
    query = update.callback_query
    await query.answer()

    user_choice = query.data.split(":")[1]
    response = context.user_data["classification_response"]

    # Persist with user's choice (HITL)
    self._service.persist_with_category(
        expense_description=context.user_data["expense_description"],
        category_name=user_choice,
        response=response,
    )

    await query.edit_message_text(f"Saved as {user_choice}!")
    return ConversationHandler.END
```


## Benefits of HITL

| Benefit | Description |
|---------|-------------|
| Accuracy | Human catches AI errors |
| Trust | Users feel in control |
| Data Quality | Corrections improve dataset |
| Compliance | Human oversight for sensitive decisions |
| Edge Cases | AI + Human handles more scenarios |


## Further Reading

- [Human-in-the-Loop Machine Learning](https://www.oreilly.com/library/view/human-in-the-loop-machine/9781617296741/)
- [Active Learning](https://en.wikipedia.org/wiki/Active_learning_(machine_learning))
- [Telegram Bot Best Practices](https://core.telegram.org/bots#keyboards)
