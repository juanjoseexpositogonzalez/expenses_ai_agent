# Looking Ahead: Week 3

Congratulations on completing Week 2! You now have a Protocol-based LLM layer with structured outputs.


## What's Next

In Week 3, you will use your LLM layer to build:

- **System and User Prompts** - Classification instructions for the LLM
- **ClassificationService** - Orchestrates the entire classification pipeline
- **CLI Interface** - Typer commands with Rich formatting
- **Database Repositories** - Persist expenses to SQLite


## How Week 2 Connects to Week 3

Week 2's components become building blocks:

```
Week 3: Service Layer
     |
     +-- ClassificationService
             |
             +-- Uses Assistant Protocol (Week 2)
             |       |
             |       +-- OpenAIAssistant.completion(messages)
             |
             +-- Produces ExpenseCategorizationResponse (Week 2)
             |
             +-- Persists via ExpenseRepository (Week 1)
```


## What the Service Layer Does

The ClassificationService combines all the pieces:

```python
class ClassificationService:
    def __init__(self, assistant: Assistant, expense_repo: ExpenseRepository):
        self._assistant = assistant
        self._expense_repo = expense_repo

    def classify(self, description: str, persist: bool = False) -> ExpenseCategorizationResponse:
        messages = [
            {"role": "system", "content": CLASSIFICATION_PROMPT},
            {"role": "user", "content": description},
        ]
        response = self._assistant.completion(messages)

        if persist:
            expense = Expense(
                amount=response.total_amount,
                currency=response.currency,
                description=description,
            )
            self._expense_repo.add(expense)

        return response
```


## Prepare for Week 3

Before starting Week 3, make sure you:

1. Have all 18 Week 2 tests passing
2. Understand how Protocol-based design enables swapping implementations
3. Can explain how structured outputs work with Pydantic

See you in Week 3!
