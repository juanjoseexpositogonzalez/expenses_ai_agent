# Week 2 Implementation: LLM Layer

This implementation exercise teaches you to build the LLM integration layer using Protocol-based design and structured outputs.


## Learning Goals

By the end of this implementation, you will:

- Define an `Assistant` Protocol for LLM providers
- Create `ExpenseCategorizationResponse` Pydantic model
- Implement `OpenAIAssistant` with structured outputs
- Build currency conversion and date formatting utilities
- Define tool schemas for function calling


## What You're Building

**Input:** Messages to an LLM requesting expense classification

**Output:** Structured response with category, amount, currency, and confidence

```python
from expenses_ai_agent.llms.openai import OpenAIAssistant

assistant = OpenAIAssistant(model="gpt-4o-mini")
response = assistant.completion([
    {"role": "system", "content": "Classify this expense..."},
    {"role": "user", "content": "Coffee at Starbucks $5.50"},
])

print(response.category)     # "Food"
print(response.total_amount) # Decimal("5.50")
print(response.confidence)   # 0.95
```


## What You're Implementing

### Output Model (`llms/output.py`)

```python
class ExpenseCategorizationResponse(BaseModel):
    """Structured response from expense classification."""
    category: str
    total_amount: Decimal
    currency: Currency
    confidence: float
    cost: Decimal
    comments: str | None = None
    timestamp: datetime = Field(default_factory=...)
```

### Protocol and Types (`llms/base.py`)

```python
MESSAGES = list[dict[str, str]]
COST = dict[str, list[Decimal]]

class LLMProvider(StrEnum):
    OPENAI = "openai"
    GROQ = "groq"

class Assistant(Protocol):
    def completion(self, messages: MESSAGES) -> ExpenseCategorizationResponse: ...
    def calculate_cost(self, prompt_tokens: int, completion_tokens: int) -> Decimal: ...
    def get_available_models(self) -> Sequence[str]: ...
```

### Utilities (`utils/currency.py`, `utils/date_formatter.py`)

```python
def convert_currency(amount: Decimal, from_currency: str, to_currency: str) -> Decimal:
    """Convert amount using ExchangeRate API."""
    ...

def format_datetime(dt: datetime, timezone_str: str = "UTC") -> str:
    """Format datetime for display in specified timezone."""
    ...
```

### Tool Schemas (`tools/tools.py`)

```python
CURRENCY_CONVERSION_TOOL = {
    "type": "function",
    "function": {
        "name": "convert_currency",
        "description": "...",
        "parameters": {...}
    }
}

DATETIME_FORMATTER_TOOL = {...}
```


## Test Suite

Copy these tests to your `tests/unit/test_week2.py` file:

```python
"""
Week 2 - Definition of Done: LLM Layer

Run: pytest tests/unit/test_week2.py -v
All tests must pass to complete Week 2.
"""

from datetime import datetime, timezone
from decimal import Decimal
from typing import Protocol
from unittest.mock import MagicMock, patch

import pytest


class TestExpenseCategorizationResponse:
    """Tests for the structured output model."""

    def test_response_has_required_fields(self):
        """Response model must have all required fields."""
        from expenses_ai_agent.llms.output import ExpenseCategorizationResponse
        from expenses_ai_agent.storage.models import Currency

        response = ExpenseCategorizationResponse(
            category="Food",
            total_amount=Decimal("42.50"),
            currency=Currency.EUR,
            confidence=0.95,
            cost=Decimal("0.001"),
        )

        assert response.category == "Food"
        assert response.total_amount == Decimal("42.50")
        assert response.currency == Currency.EUR
        assert response.confidence == 0.95
        assert response.cost == Decimal("0.001")

    def test_response_optional_fields(self):
        """Response should support optional comments."""
        from expenses_ai_agent.llms.output import ExpenseCategorizationResponse
        from expenses_ai_agent.storage.models import Currency

        response = ExpenseCategorizationResponse(
            category="Transport",
            total_amount=Decimal("15.00"),
            currency=Currency.USD,
            confidence=0.8,
            cost=Decimal("0.002"),
            comments="Taxi ride to airport",
        )

        assert response.comments == "Taxi ride to airport"

    def test_response_has_timestamp(self):
        """Response should include a timestamp."""
        from expenses_ai_agent.llms.output import ExpenseCategorizationResponse
        from expenses_ai_agent.storage.models import Currency

        response = ExpenseCategorizationResponse(
            category="Entertainment",
            total_amount=Decimal("10.00"),
            currency=Currency.EUR,
            confidence=0.9,
            cost=Decimal("0.001"),
        )

        assert hasattr(response, "timestamp")
        assert isinstance(response.timestamp, datetime)

    def test_response_is_pydantic_model(self):
        """Response should be a Pydantic BaseModel for validation."""
        from pydantic import BaseModel

        from expenses_ai_agent.llms.output import ExpenseCategorizationResponse

        assert issubclass(ExpenseCategorizationResponse, BaseModel)

    def test_response_json_serialization(self):
        """Response should serialize to JSON."""
        from expenses_ai_agent.llms.output import ExpenseCategorizationResponse
        from expenses_ai_agent.storage.models import Currency

        response = ExpenseCategorizationResponse(
            category="Food",
            total_amount=Decimal("25.00"),
            currency=Currency.GBP,
            confidence=0.85,
            cost=Decimal("0.001"),
        )

        json_str = response.model_dump_json()
        assert "Food" in json_str
        assert "25" in json_str


class TestAssistantProtocol:
    """Tests for the Assistant Protocol definition."""

    def test_assistant_protocol_exists(self):
        """Assistant should be defined as a Protocol."""
        from expenses_ai_agent.llms.base import Assistant

        assert hasattr(Assistant, "__protocol_attrs__") or issubclass(Assistant, Protocol)

    def test_assistant_has_completion_method(self):
        """Assistant Protocol must define completion method."""
        from expenses_ai_agent.llms.base import Assistant

        assert hasattr(Assistant, "completion")

    def test_assistant_has_calculate_cost_method(self):
        """Assistant Protocol must define calculate_cost method."""
        from expenses_ai_agent.llms.base import Assistant

        assert hasattr(Assistant, "calculate_cost")

    def test_assistant_has_get_available_models_method(self):
        """Assistant Protocol must define get_available_models method."""
        from expenses_ai_agent.llms.base import Assistant

        assert hasattr(Assistant, "get_available_models")


class TestLLMProvider:
    """Tests for the LLMProvider enumeration."""

    def test_llm_provider_has_openai(self):
        """LLMProvider should include OPENAI."""
        from expenses_ai_agent.llms.base import LLMProvider

        assert hasattr(LLMProvider, "OPENAI")

    def test_llm_provider_has_groq(self):
        """LLMProvider should include GROQ."""
        from expenses_ai_agent.llms.base import LLMProvider

        assert hasattr(LLMProvider, "GROQ")

    def test_llm_provider_is_str_enum(self):
        """LLMProvider should be a StrEnum for string compatibility."""
        from enum import StrEnum

        from expenses_ai_agent.llms.base import LLMProvider

        assert issubclass(LLMProvider, StrEnum)


class TestTypeAliases:
    """Tests for type alias definitions."""

    def test_messages_type_alias_exists(self):
        """MESSAGES type alias should be defined."""
        from expenses_ai_agent.llms.base import MESSAGES

        sample_messages: MESSAGES = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Hello!"},
        ]
        assert len(sample_messages) == 2

    def test_cost_type_alias_exists(self):
        """COST type alias should be defined."""
        from expenses_ai_agent.llms.base import COST

        sample_cost: COST = {
            "prompt": [Decimal("0.001"), Decimal("0.002")],
            "completion": [Decimal("0.003")],
        }
        assert "prompt" in sample_cost


class TestCurrencyConversion:
    """Tests for the currency conversion utility."""

    def test_convert_currency_function_exists(self):
        """convert_currency function should exist."""
        from expenses_ai_agent.utils.currency import convert_currency

        assert callable(convert_currency)

    def test_convert_currency_returns_decimal(self):
        """Currency conversion should return a Decimal value."""
        from expenses_ai_agent.utils.currency import convert_currency

        with patch("expenses_ai_agent.utils.currency.requests.get") as mock_get:
            mock_response = MagicMock()
            mock_response.json.return_value = {
                "result": "success",
                "conversion_rate": 1.1,
            }
            mock_response.raise_for_status = MagicMock()
            mock_get.return_value = mock_response

            result = convert_currency(Decimal("100"), "EUR", "USD")

            assert isinstance(result, Decimal)

    def test_convert_currency_same_currency(self):
        """Converting to the same currency should return the original amount."""
        from expenses_ai_agent.utils.currency import convert_currency

        result = convert_currency(Decimal("50.00"), "EUR", "EUR")

        assert result == Decimal("50.00")

    def test_convert_currency_applies_rate(self):
        """Conversion should apply the exchange rate correctly."""
        from expenses_ai_agent.utils.currency import convert_currency

        with patch("expenses_ai_agent.utils.currency.requests.get") as mock_get:
            mock_response = MagicMock()
            mock_response.json.return_value = {
                "result": "success",
                "conversion_rate": 1.5,
            }
            mock_response.raise_for_status = MagicMock()
            mock_get.return_value = mock_response

            result = convert_currency(Decimal("100"), "EUR", "USD")

            assert result == Decimal("150")


class TestDateFormatter:
    """Tests for the date formatting utility."""

    def test_format_datetime_function_exists(self):
        """format_datetime function should exist."""
        from expenses_ai_agent.utils.date_formatter import format_datetime

        assert callable(format_datetime)

    def test_format_datetime_returns_string(self):
        """Date formatting should return a string."""
        from expenses_ai_agent.utils.date_formatter import format_datetime

        dt = datetime(2024, 6, 15, 14, 30, 0, tzinfo=timezone.utc)
        result = format_datetime(dt)

        assert isinstance(result, str)

    def test_format_datetime_includes_date_components(self):
        """Formatted datetime should include readable date components."""
        from expenses_ai_agent.utils.date_formatter import format_datetime

        dt = datetime(2024, 6, 15, 14, 30, 0, tzinfo=timezone.utc)
        result = format_datetime(dt)

        assert "2024" in result or "24" in result
        assert "Jun" in result or "06" in result or "6" in result

    def test_format_datetime_with_timezone(self):
        """Should support timezone conversion."""
        from expenses_ai_agent.utils.date_formatter import format_datetime

        dt = datetime(2024, 6, 15, 12, 0, 0, tzinfo=timezone.utc)

        result = format_datetime(dt, timezone_str="Europe/Madrid")

        assert isinstance(result, str)


class TestToolSchemas:
    """Tests for OpenAI-compatible tool schemas."""

    def test_currency_tool_schema_exists(self):
        """Currency conversion tool schema should be defined."""
        from expenses_ai_agent.tools.tools import CURRENCY_CONVERSION_TOOL

        assert isinstance(CURRENCY_CONVERSION_TOOL, dict)

    def test_currency_tool_has_function_type(self):
        """Tool schema should have type: function."""
        from expenses_ai_agent.tools.tools import CURRENCY_CONVERSION_TOOL

        assert CURRENCY_CONVERSION_TOOL.get("type") == "function"

    def test_currency_tool_has_required_structure(self):
        """Tool schema should follow OpenAI function calling format."""
        from expenses_ai_agent.tools.tools import CURRENCY_CONVERSION_TOOL

        assert "function" in CURRENCY_CONVERSION_TOOL
        func = CURRENCY_CONVERSION_TOOL["function"]

        assert "name" in func
        assert "description" in func
        assert "parameters" in func

        params = func["parameters"]
        assert "type" in params
        assert "properties" in params

    def test_datetime_tool_schema_exists(self):
        """Datetime formatter tool schema should be defined."""
        from expenses_ai_agent.tools.tools import DATETIME_FORMATTER_TOOL

        assert isinstance(DATETIME_FORMATTER_TOOL, dict)
        assert DATETIME_FORMATTER_TOOL.get("type") == "function"
```


## Implementation Strategy

Work through these steps in order. Each step targets specific tests.

### Step 1: Create ExpenseCategorizationResponse

Start with the Pydantic model in `llms/output.py`:

**Target tests:** `TestExpenseCategorizationResponse` (5 tests)

### Step 2: Define Type Aliases and Protocol

Create `llms/base.py` with:
- `MESSAGES` and `COST` type aliases
- `LLMProvider` StrEnum
- `Assistant` Protocol

**Target tests:** `TestAssistantProtocol`, `TestLLMProvider`, `TestTypeAliases` (7 tests)

### Step 3: Implement Currency Conversion

Build `utils/currency.py` with ExchangeRate API integration:

**Target tests:** `TestCurrencyConversion` (4 tests)

### Step 4: Implement Date Formatter

Build `utils/date_formatter.py` with timezone support:

**Target tests:** `TestDateFormatter` (4 tests)

### Step 5: Define Tool Schemas

Create `tools/tools.py` with OpenAI-compatible schemas:

**Target tests:** `TestToolSchemas` (4 tests)


## Helpful Concepts

### Defining a Protocol

```python
from typing import Protocol, Sequence
from decimal import Decimal

class Assistant(Protocol):
    def completion(self, messages: MESSAGES) -> ExpenseCategorizationResponse:
        ...

    def calculate_cost(self, prompt_tokens: int, completion_tokens: int) -> Decimal:
        ...

    def get_available_models(self) -> Sequence[str]:
        ...
```

[Documentation: typing.Protocol](https://docs.python.org/3/library/typing.html#typing.Protocol)

### ExchangeRate API

```python
import requests
from decouple import config

API_KEY = config("EXCHANGE_RATE_API_KEY")
url = f"https://v6.exchangerate-api.com/v6/{API_KEY}/pair/{from_currency}/{to_currency}"
response = requests.get(url)
data = response.json()
rate = Decimal(str(data["conversion_rate"]))
```

### Timezone Handling

```python
from zoneinfo import ZoneInfo

def format_datetime(dt: datetime, timezone_str: str = "UTC") -> str:
    tz = ZoneInfo(timezone_str)
    local_dt = dt.astimezone(tz)
    return local_dt.strftime("%Y-%m-%d %H:%M %Z")
```


## Environment Variables

Add to your `.env`:

```bash
OPENAI_API_KEY=sk-...
EXCHANGE_RATE_API_KEY=...
```


## Validation Checklist

Before moving on, verify:

- [ ] All 18 tests pass: `pytest tests/unit/test_week2.py -v`
- [ ] No linting errors: `ruff check src/`
- [ ] Code is formatted: `ruff format .`


## Debugging Tips

### "Protocol is not subscriptable"

Use `from typing import Protocol` (not `from typing_extensions`).

### OpenAI API key error

Check your `.env` file and ensure `python-decouple` is configured.

### Decimal serialization error

Add to your Pydantic model:

```python
model_config = ConfigDict(json_encoders={Decimal: str})
```


## Step Hints


### Step 1: ExpenseCategorizationResponse Hint

Your model needs:
- Required: `category`, `total_amount`, `currency`, `confidence`, `cost`
- Optional: `comments` (default None)
- Auto-generated: `timestamp` (use `default_factory`)


### Step 2: Protocol Hint

The Protocol uses `...` for method bodies:

```python
class Assistant(Protocol):
    def completion(self, messages: MESSAGES) -> ExpenseCategorizationResponse:
        ...  # Just ellipsis, no implementation
```


### Step 3: Currency Conversion Hint

Handle the same-currency case first (no API call needed):

```python
def convert_currency(amount: Decimal, from_currency: str, to_currency: str) -> Decimal:
    if from_currency == to_currency:
        return amount
    # ... call API
```


### Step 5: Tool Schema Hint

Follow the OpenAI format exactly:

```python
CURRENCY_CONVERSION_TOOL = {
    "type": "function",
    "function": {
        "name": "convert_currency",
        "description": "...",
        "parameters": {
            "type": "object",
            "properties": {...},
            "required": [...]
        }
    }
}
```

---

Your Week 2 LLM layer is complete when all 18 tests pass.
