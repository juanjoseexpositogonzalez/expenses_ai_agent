# Week 1 Review: Bridging to Week 2

Before diving into LLM integration, let's review the key concepts from Week 1 that we'll build upon.


## What You Built in Week 1

### Storage Models

```python
from enum import StrEnum
from sqlmodel import SQLModel, Field

class Currency(StrEnum):
    EUR = "EUR"
    USD = "USD"
    # ...

class Expense(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    amount: Decimal
    currency: Currency
    description: str | None = None
```

### Repository Pattern

```python
from abc import ABC, abstractmethod

class ExpenseRepository(ABC):
    @abstractmethod
    def add(self, expense: Expense) -> None: ...

    @abstractmethod
    def get(self, expense_id: int) -> Expense | None: ...
```

### In-Memory Implementation

```python
class InMemoryExpenseRepository(ExpenseRepository):
    def __init__(self):
        self._storage: dict[int, Expense] = {}
```


## How Week 2 Connects

Week 1 gave you the **storage layer**. Week 2 adds the **LLM layer** that produces data for storage:

```
Week 2: LLM Layer
     |
     | produces
     v
ExpenseCategorizationResponse (Pydantic)
     |
     | converts to
     v
Week 1: Storage Layer
Expense + ExpenseCategory (SQLModel)
     |
     | persisted by
     v
Repository -> Database
```


## Key Pattern: Abstraction

Both weeks use abstraction:

| Week 1 | Week 2 |
|--------|--------|
| `ExpenseRepository` (ABC) | `Assistant` (Protocol) |
| Abstracts data storage | Abstracts LLM providers |
| `InMemoryExpenseRepository` | `OpenAIAssistant` |
| `DBExpenseRepository` | `GroqAssistant` |

Same pattern, different purpose.


## Your Currency Enum Returns

The `Currency` enum you built in Week 1 will be used in Week 2's LLM response:

```python
# Week 2: LLM returns structured data using Week 1's enum
class ExpenseCategorizationResponse(BaseModel):
    category: str
    total_amount: Decimal
    currency: Currency  # From Week 1!
    confidence: float
```


## Ready for Week 2?

Make sure you:

- [ ] Have all 26 Week 1 tests passing
- [ ] Understand the Repository pattern
- [ ] Can explain why we use abstract base classes
- [ ] Have your OpenAI API key ready

If anything from Week 1 is unclear, now is the time to review before adding the LLM layer.
