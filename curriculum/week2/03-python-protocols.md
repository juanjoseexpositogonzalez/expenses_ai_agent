# Python Protocols: Structural Typing

Protocols define interfaces through structure rather than inheritance. This lesson explains when and why to use them.


## Why Protocols Exist

Abstract Base Classes (ABC) require explicit inheritance:

```python
from abc import ABC, abstractmethod

class Printable(ABC):
    @abstractmethod
    def print(self) -> str: ...

# Must explicitly inherit from Printable
class Document(Printable):
    def print(self) -> str:
        return "Document content"
```

But what if you're using a third-party class you can't modify?

```python
# Third-party library - you can't change this
class ExternalPrinter:
    def print(self) -> str:
        return "External output"

# This fails - ExternalPrinter doesn't inherit Printable
def process(item: Printable) -> None:
    print(item.print())

process(ExternalPrinter())  # Type error!
```

Protocols solve this with structural typing:

```python
from typing import Protocol

class Printable(Protocol):
    def print(self) -> str: ...

# Works! ExternalPrinter has the right structure
process(ExternalPrinter())  # No error - duck typing with type hints
```


## Protocol vs ABC

| Feature | ABC | Protocol |
|---------|-----|----------|
| Inheritance required | Yes | No |
| Typing approach | Nominal | Structural |
| Third-party classes | Can't satisfy | Can satisfy |
| Runtime checks | `isinstance()` works | Need `@runtime_checkable` |
| Best for | Internal code | Interfaces with externals |


## Core Syntax

```python
from typing import Protocol
from decimal import Decimal

class Assistant(Protocol):
    """Any class with these methods satisfies the Protocol."""

    def completion(self, messages: list[dict[str, str]]) -> Response:
        """Generate a completion from messages."""
        ...

    def calculate_cost(self, prompt_tokens: int, completion_tokens: int) -> Decimal:
        """Calculate the cost of an API call."""
        ...
```

Key points:

- Inherit from `Protocol`
- Use `...` (ellipsis) for method bodies
- Type hints define the expected signatures


## Implementing a Protocol

You don't need to explicitly inherit from a Protocol:

```python
# This class satisfies Assistant Protocol - no inheritance needed!
class OpenAIAssistant:
    def completion(self, messages: list[dict[str, str]]) -> Response:
        # Actual implementation
        return self._call_openai(messages)

    def calculate_cost(self, prompt_tokens: int, completion_tokens: int) -> Decimal:
        return Decimal(prompt_tokens * 0.001 + completion_tokens * 0.002)
```

Type checkers recognize that `OpenAIAssistant` satisfies `Assistant` because it has the right methods.


## When to Use Protocol

**Use Protocol when:**

- Integrating with third-party libraries
- Defining interfaces for dependency injection
- You want structural (duck) typing with type hints

**Use ABC when:**

- You control all implementations
- You need `isinstance()` checks without `@runtime_checkable`
- You want to share implementation code via inheritance


## Python Comparison

| Dynamic typing | Protocol |
|---------------|----------|
| `def process(obj):` | `def process(obj: Printable):` |
| No type hints | Full type hints |
| Errors at runtime | Errors at edit time |
| "Duck typing" | "Duck typing with safety" |


## Protocols in Our Project

The `Assistant` Protocol defines the contract for LLM providers:

```python
class Assistant(Protocol):
    def completion(self, messages: MESSAGES) -> ExpenseCategorizationResponse:
        """Generate expense classification from messages."""
        ...

    def calculate_cost(self, prompt_tokens: int, completion_tokens: int) -> Decimal:
        """Calculate API call cost."""
        ...

    def get_available_models(self) -> Sequence[str]:
        """Return list of available model names."""
        ...
```

Both `OpenAIAssistant` and `GroqAssistant` satisfy this Protocol without inheriting from it.


## Further Reading

- [PEP 544 - Protocols: Structural subtyping](https://peps.python.org/pep-0544/)
- [typing.Protocol documentation](https://docs.python.org/3/library/typing.html#typing.Protocol)
- [mypy Protocol documentation](https://mypy.readthedocs.io/en/stable/protocols.html)
