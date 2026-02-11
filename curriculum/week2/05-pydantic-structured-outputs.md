# Pydantic for Structured LLM Outputs

Pydantic models define the structure of LLM responses, ensuring type-safe data extraction.


## Why Structured Outputs Matter

Without structured outputs, LLM responses are just text:

```python
response = openai.chat.completions.create(...)
text = response.choices[0].message.content
# "This is a food expense for $5.50 USD"

# Now what? Parse with regex? Hope for the best?
```

With structured outputs, you get validated data:

```python
response = ExpenseCategorizationResponse(
    category="Food",
    total_amount=Decimal("5.50"),
    currency=Currency.USD,
    confidence=0.95,
)

# Type-safe access
print(response.category)      # "Food"
print(response.total_amount)  # Decimal("5.50")
```


## Defining the Response Model

```python
from datetime import datetime, timezone
from decimal import Decimal
from pydantic import BaseModel

from expenses_ai_agent.storage.models import Currency


class ExpenseCategorizationResponse(BaseModel):
    """Structured output from expense classification."""

    category: str
    total_amount: Decimal
    currency: Currency
    confidence: float
    cost: Decimal
    comments: str | None = None
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
```


## Key Features

### Automatic Validation

```python
# Pydantic validates types automatically
response = ExpenseCategorizationResponse(
    category="Food",
    total_amount="5.50",  # String converted to Decimal
    currency="USD",       # String converted to Currency enum
    confidence=0.95,
    cost=Decimal("0.001"),
)
```

### JSON Serialization

```python
# Convert to JSON
json_str = response.model_dump_json()
# {"category": "Food", "total_amount": "5.50", ...}

# Parse from JSON
data = response.model_dump()
# {"category": "Food", "total_amount": Decimal("5.50"), ...}
```

### Default Values

```python
class ExpenseCategorizationResponse(BaseModel):
    # Required fields
    category: str
    total_amount: Decimal

    # Optional with defaults
    comments: str | None = None
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
```


## OpenAI Structured Outputs

OpenAI's API supports structured outputs directly:

```python
from openai import OpenAI

client = OpenAI()

response = client.beta.chat.completions.parse(
    model="gpt-4o-mini",
    messages=messages,
    response_format=ExpenseCategorizationResponse,  # Pydantic model!
)

# response.choices[0].message.parsed is already an ExpenseCategorizationResponse
result = response.choices[0].message.parsed
print(result.category)  # Type-safe access
```


## Python Comparison

| dataclass | Pydantic BaseModel |
|-----------|-------------------|
| No validation | Automatic validation |
| No JSON support | Built-in JSON serialization |
| No coercion | Type coercion ("5.50" -> Decimal) |
| `@dataclass` | `class X(BaseModel)` |


## Handling Decimal Serialization

Decimal values need special handling for JSON:

```python
from pydantic import BaseModel, ConfigDict

class ExpenseCategorizationResponse(BaseModel):
    model_config = ConfigDict(
        json_encoders={Decimal: str}  # Serialize Decimal as string
    )

    total_amount: Decimal
    # JSON output: {"total_amount": "5.50"}
```


## Structured Outputs in Our Project

The `ExpenseCategorizationResponse` is used throughout:

1. **LLM returns it** - OpenAI parses response into this model
2. **Service uses it** - ClassificationService receives structured data
3. **Storage converts it** - Response maps to Expense entity

```python
# LLM Layer
response: ExpenseCategorizationResponse = assistant.completion(messages)

# Service Layer
expense = Expense(
    amount=response.total_amount,
    currency=response.currency,
    description=original_description,
    category=category_repo.get(response.category),
)

# Storage Layer
expense_repo.add(expense)
```


## Further Reading

- [Pydantic Documentation](https://docs.pydantic.dev/)
- [OpenAI Structured Outputs](https://platform.openai.com/docs/guides/structured-outputs)
- [Pydantic Field](https://docs.pydantic.dev/latest/concepts/fields/)
