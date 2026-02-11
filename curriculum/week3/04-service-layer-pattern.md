# The Service Layer Pattern

The Service layer encapsulates business logic, providing a clean interface for multiple consumers (CLI, bot, API). This lesson explains how to design the ClassificationService.


## Why Service Layers Exist

Without a service layer, business logic spreads across the application:

```python
# CLI has classification logic
def cli_classify(description):
    messages = build_messages(description)
    response = assistant.completion(messages)
    expense = create_expense(response)
    repo.add(expense)
    return response

# Bot duplicates the same logic
def bot_classify(description):
    messages = build_messages(description)  # Duplicated!
    response = assistant.completion(messages)  # Duplicated!
    expense = create_expense(response)  # Duplicated!
    repo.add(expense)  # Duplicated!
    return response
```

With a service layer:

```python
# Service encapsulates the logic
class ClassificationService:
    def classify(self, description, persist=False):
        # All logic in one place
        ...

# CLI uses the service
def cli_classify(description):
    return service.classify(description, persist=True)

# Bot uses the same service
def bot_classify(description):
    return service.classify(description, persist=True)
```


## ClassificationService Design

```python
from dataclasses import dataclass

@dataclass
class ClassificationResult:
    """Result of a classification operation."""
    response: ExpenseCategorizationResponse
    persisted: bool


@dataclass
class ClassificationService:
    """Orchestrates expense classification and optional persistence."""

    assistant: Assistant
    category_repo: CategoryRepository | None = None
    expense_repo: ExpenseRepository | None = None

    def classify(
        self,
        expense_description: str,
        persist: bool = False,
    ) -> ClassificationResult:
        """Classify an expense and optionally persist to database."""
        messages = self._build_messages(expense_description)
        response = self.assistant.completion(messages)

        if persist and self.expense_repo:
            self._persist_expense(expense_description, response)

        return ClassificationResult(response=response, persisted=persist)

    def persist_with_category(
        self,
        expense_description: str,
        category_name: str,
        response: ExpenseCategorizationResponse,
    ) -> None:
        """Persist with user-selected category (HITL override)."""
        # For human-in-the-loop: user corrects the classification
        ...
```


## Key Design Decisions

### Optional Repositories

The service works with or without repositories:

```python
# Classification only
service = ClassificationService(assistant=openai_assistant)
result = service.classify("Coffee $5")  # Works!

# Classification with persistence
service = ClassificationService(
    assistant=openai_assistant,
    category_repo=category_repo,
    expense_repo=expense_repo,
)
result = service.classify("Coffee $5", persist=True)  # Works!
```

### ClassificationResult Dataclass

The result carries both the response and persistence status:

```python
result = service.classify("Coffee $5", persist=True)
print(result.response.category)  # "Food"
print(result.persisted)          # True
```

### HITL Support

The `persist_with_category` method supports human-in-the-loop overrides:

```python
# LLM classified as "Food" with low confidence
response = service.classify("Movie snacks").response

# User corrects to "Entertainment"
service.persist_with_category(
    expense_description="Movie snacks",
    category_name="Entertainment",
    response=response,
)
```


## Python Comparison

| Direct calls | Service layer |
|-------------|---------------|
| Logic scattered | Logic centralized |
| Hard to test | Easy to mock |
| Duplication | Single source of truth |
| Tight coupling | Loose coupling |


## Service Layer in Our Project

The ClassificationService is used by:

1. **CLI** - `expenses-ai-agent classify "..."` command
2. **Telegram Bot** - (Week 4) message handlers
3. **REST API** - (Week 5) `/classify` endpoint


## Further Reading

- [P of EAA: Service Layer](https://martinfowler.com/eaaCatalog/serviceLayer.html)
- [Python dataclasses](https://docs.python.org/3/library/dataclasses.html)
