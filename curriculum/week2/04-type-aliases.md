# Type Aliases for Cleaner Code

Type aliases give names to complex types, making code more readable and maintainable.


## Why Type Aliases Exist

Complex type annotations can be hard to read:

```python
def completion(
    self,
    messages: list[dict[str, str]],
    cost_tracker: dict[str, list[Decimal]]
) -> ExpenseCategorizationResponse:
    ...
```

Type aliases improve readability:

```python
MESSAGES = list[dict[str, str]]
COST = dict[str, list[Decimal]]

def completion(
    self,
    messages: MESSAGES,
    cost_tracker: COST
) -> ExpenseCategorizationResponse:
    ...
```


## Defining Type Aliases

In Python 3.9+, use simple assignment:

```python
from decimal import Decimal

# Type alias for chat messages
MESSAGES = list[dict[str, str]]

# Type alias for cost tracking
COST = dict[str, list[Decimal]]
```

For Python 3.12+, you can use the `type` statement:

```python
type MESSAGES = list[dict[str, str]]
type COST = dict[str, list[Decimal]]
```


## Usage in Function Signatures

```python
def completion(self, messages: MESSAGES) -> ExpenseCategorizationResponse:
    # messages is list[dict[str, str]]
    for message in messages:
        role = message["role"]
        content = message["content"]
```

The type checker knows exactly what `messages` contains.


## Benefits

| Without aliases | With aliases |
|----------------|--------------|
| Repeat complex types everywhere | Define once, use everywhere |
| Hard to read signatures | Self-documenting names |
| Error-prone updates | Change in one place |
| `list[dict[str, str]]` | `MESSAGES` |


## Type Aliases in Our Project

We define two aliases in `llms/base.py`:

```python
from decimal import Decimal

# Chat messages format for OpenAI/Groq
MESSAGES = list[dict[str, str]]

# Cost tracking: {"prompt": [0.001, 0.002], "completion": [0.003]}
COST = dict[str, list[Decimal]]
```

These are used throughout the LLM layer:

```python
class Assistant(Protocol):
    def completion(self, messages: MESSAGES) -> ExpenseCategorizationResponse:
        ...

class OpenAIAssistant:
    def __init__(self):
        self._costs: COST = {"prompt": [], "completion": []}

    def completion(self, messages: MESSAGES) -> ExpenseCategorizationResponse:
        ...
```


## Python Comparison

| Approach | Type checking | Readability |
|----------|--------------|-------------|
| No types | None | Hard to understand |
| Inline types | Full | Verbose |
| Type aliases | Full | Clean and clear |


## Best Practices

**Use UPPERCASE for type aliases:**

```python
MESSAGES = list[dict[str, str]]  # Clear it's a type
messages: MESSAGES = []          # Clear it's a variable
```

**Keep aliases close to their usage:**

```python
# In llms/base.py
MESSAGES = list[dict[str, str]]
COST = dict[str, list[Decimal]]

class Assistant(Protocol):
    def completion(self, messages: MESSAGES) -> ...:
        ...
```

**Document complex aliases:**

```python
# Format: [{"role": "system"|"user"|"assistant", "content": "..."}]
MESSAGES = list[dict[str, str]]
```


## Further Reading

- [Python Type Aliases](https://docs.python.org/3/library/typing.html#type-aliases)
- [PEP 613 - Explicit Type Aliases](https://peps.python.org/pep-0613/)
