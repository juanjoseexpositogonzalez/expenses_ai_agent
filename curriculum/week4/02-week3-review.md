# Week 3 Review: Bridging to Week 4

Before building the Telegram bot, let's review the Week 3 components you will reuse.


## What You Built in Week 3

### ClassificationService

The service layer encapsulates the entire classification pipeline:

```python
from dataclasses import dataclass

@dataclass
class ClassificationResult:
    response: ExpenseCategorizationResponse
    persisted: bool


class ClassificationService:
    def __init__(
        self,
        assistant: Assistant,
        category_repo: CategoryRepository | None = None,
        expense_repo: ExpenseRepository | None = None,
    ):
        self._assistant = assistant
        self._category_repo = category_repo
        self._expense_repo = expense_repo

    def classify(
        self,
        expense_description: str,
        persist: bool = False,
    ) -> ClassificationResult:
        """Classify expense, optionally persist to database."""
        ...

    def persist_with_category(
        self,
        expense_description: str,
        category_name: str,
        response: ExpenseCategorizationResponse,
    ) -> Expense:
        """HITL override: persist with user-selected category."""
        ...
```

### Key Methods for Week 4

| Method | Purpose | Used By |
|--------|---------|---------|
| `classify()` | Get LLM classification | Telegram handler after user sends expense |
| `persist_with_category()` | Store with user's choice | Telegram handler after user taps category |


## How Week 4 Uses Week 3

The Telegram bot wraps ClassificationService with input validation and user interaction:

```
User message: "Coffee $5.50"
        |
        v
+-------------------+
| InputPreprocessor |  <- NEW in Week 4
+-------------------+
        |
        v (if valid)
+-------------------+
| ClassificationService.classify()  <- Week 3
+-------------------+
        |
        v
+-------------------+
| Show keyboard with categories  <- NEW in Week 4
+-------------------+
        |
        v (user taps button)
+-------------------+
| ClassificationService.persist_with_category()  <- Week 3
+-------------------+
        |
        v
+-------------------+
| Confirmation message  <- NEW in Week 4
+-------------------+
```


## The HITL Pattern

Week 3's `persist_with_category()` method enables human-in-the-loop:

```python
# Week 3 implementation
def persist_with_category(
    self,
    expense_description: str,
    category_name: str,
    response: ExpenseCategorizationResponse,
) -> Expense:
    """
    Persist expense with user-selected category (HITL override).

    When user overrides AI suggestion, we:
    1. Use the user's category choice (not AI's)
    2. Set confidence to 1.0 (user confirmed)
    3. Keep other fields from AI response (amount, currency)
    """
    category = self._category_repo.get(category_name)
    expense = Expense(
        amount=response.total_amount,
        currency=response.currency,
        description=expense_description,
        category=category,
        confidence=Decimal("1.0"),  # User confirmed
    )
    self._expense_repo.add(expense)
    return expense
```

This method will be called by the Telegram handler when the user taps a category button.


## New This Week: Input Layer

Week 4 adds input preprocessing before the service:

```
InputPreprocessor
        |
        +-- Validates length (3-500 chars)
        |
        +-- Detects XSS patterns
        |
        +-- Normalizes currency symbols
        |
        +-- Warns about missing amounts
        |
        +-- Returns PreprocessingResult
```


## Prepare for Week 4

Make sure you:

- [ ] Have all 30 Week 3 tests passing
- [ ] Understand ClassificationService.classify() and persist_with_category()
- [ ] Have a Telegram Bot Token (get one from @BotFather)
- [ ] Have python-telegram-bot installed: `pip install python-telegram-bot`

The Telegram bot will reuse your service layer while adding conversational interaction.
