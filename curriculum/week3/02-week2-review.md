# Week 2 Review: Bridging to Week 3

Before building the classification service, let's review the LLM layer components you'll use.


## What You Built in Week 2

### Assistant Protocol

```python
from typing import Protocol

class Assistant(Protocol):
    def completion(self, messages: MESSAGES) -> ExpenseCategorizationResponse:
        ...

    def calculate_cost(self, prompt_tokens: int, completion_tokens: int) -> Decimal:
        ...
```

### Structured Output

```python
class ExpenseCategorizationResponse(BaseModel):
    category: str
    total_amount: Decimal
    currency: Currency
    confidence: float
    cost: Decimal
    comments: str | None = None
    timestamp: datetime
```

### Type Aliases

```python
MESSAGES = list[dict[str, str]]
COST = dict[str, list[Decimal]]
```


## How Week 3 Uses Week 2

The ClassificationService orchestrates Week 2 components:

```python
from expenses_ai_agent.llms.base import Assistant, MESSAGES
from expenses_ai_agent.llms.output import ExpenseCategorizationResponse

class ClassificationService:
    def __init__(self, assistant: Assistant):
        self._assistant = assistant

    def classify(self, description: str) -> ExpenseCategorizationResponse:
        messages: MESSAGES = [
            {"role": "system", "content": CLASSIFICATION_PROMPT},
            {"role": "user", "content": description},
        ]
        return self._assistant.completion(messages)
```


## New This Week: Prompts

Week 3 adds the prompts that guide the LLM:

```
ClassificationService
        |
        +-- Uses CLASSIFICATION_PROMPT (system)
        |
        +-- Uses USER_PROMPT (user)
        |
        +-- Calls assistant.completion(messages)
        |
        +-- Returns ExpenseCategorizationResponse
```


## Prepare for Week 3

Make sure you:

- [ ] Have all 18 Week 2 tests passing
- [ ] Understand how the Assistant Protocol works
- [ ] Can explain structured outputs with Pydantic

The service layer will tie everything together.
