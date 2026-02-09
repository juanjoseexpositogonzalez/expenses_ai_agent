# Week 2: Assistant Setup - LLM Protocol and Tools

Welcome to Week 2! This week you will build the LLM integration layer that powers the AI classification. You will learn about Python Protocols for type-safe abstractions, implement an OpenAI client with structured outputs, and create utility tools for currency conversion and date formatting.

## What You're Building This Week

Week 2 transforms your data models into an AI-powered system:

```
+------------------------------------------------------------------+
|                    WEEK 2: LLM LAYER                             |
+------------------------------------------------------------------+

    User Input: "Coffee at Starbucks for $5.50"
                              |
                              v
                    +-------------------+
                    |   Messages List   |
                    | [system, user]    |
                    +-------------------+
                              |
                              v
                    +-------------------+
                    |  Assistant        |
                    |  (Protocol)       |
                    +-------------------+
                              |
              +---------------+---------------+
              |                               |
              v                               v
    +-------------------+           +-------------------+
    | OpenAIAssistant   |           | GroqAssistant     |
    | (implementation)  |           | (implementation)  |
    +-------------------+           +-------------------+
              |
              +-- uses tools ----------------+
              |                              |
              v                              v
    +-------------------+           +-------------------+
    | Currency          |           | DateTime          |
    | Conversion Tool   |           | Formatter Tool    |
    +-------------------+           +-------------------+
              |
              v
    +-------------------+
    | ExpenseCategori-  |
    | zationResponse    |
    | (Pydantic model)  |
    +-------------------+
```

## Learning Objectives

By the end of this week, you will:

- Understand Python `Protocol` for structural typing (duck typing with type hints)
- Implement an OpenAI client with function calling (tools)
- Use Pydantic for structured output parsing from LLMs
- Create reusable utility functions for currency and date handling
- Understand type aliases for cleaner code
- Handle API costs with Decimal precision


## Week 2 Checklist

### Technical Milestones

- [ ] Define `Assistant` Protocol in `llms/base.py`
- [ ] Implement `ExpenseCategorizationResponse` Pydantic model
- [ ] Create OpenAI client that satisfies the `Assistant` Protocol
- [ ] Implement currency conversion utility (using ExchangeRate API)
- [ ] Implement date formatter utility with timezone support
- [ ] Define tool schemas following OpenAI function calling format
- [ ] Pass all provided tests

### Concepts to Master

- [ ] Understand difference between Protocol and ABC
- [ ] Know when to use `dataclass` vs `Pydantic BaseModel`
- [ ] Understand type aliases (`MESSAGES`, `COST`)
- [ ] Handle external API calls with proper error handling


## Key Concepts This Week

### 1. Protocol: Structural Typing in Python

Unlike abstract base classes (ABC) that require explicit inheritance, Protocols define interfaces through structure:

```python
from typing import Protocol

class Assistant(Protocol):
    """Any class with these methods satisfies the Protocol."""

    def completion(self, messages: MESSAGES) -> ExpenseCategorizationResponse:
        """Generate a completion from messages."""
        ...

    def calculate_cost(self, prompt_tokens: int, completion_tokens: int) -> Decimal:
        """Calculate the cost of an API call."""
        ...

    def get_available_models(self) -> Sequence[str]:
        """Return list of available model names."""
        ...
```

**Why Protocol over ABC?**
- No inheritance required (duck typing)
- Works with third-party classes you do not control
- Better for dependency injection and testing

### 2. Type Aliases for Cleaner Code

```python
from typing import Dict, List
from decimal import Decimal

# Type alias for chat messages
MESSAGES = List[Dict[str, str]]

# Type alias for cost tracking
COST = Dict[str, List[Decimal]]
```

Usage:
```python
def completion(self, messages: MESSAGES) -> ExpenseCategorizationResponse:
    # messages is List[Dict[str, str]]
    pass
```

### 3. Pydantic for Structured Outputs

```python
from pydantic import BaseModel
from decimal import Decimal
from datetime import datetime

class ExpenseCategorizationResponse(BaseModel):
    category: str
    total_amount: Decimal
    currency: Currency
    confidence: float
    cost: Decimal
    comments: str | None = None
    timestamp: datetime = datetime.now(timezone.utc)
```

Pydantic provides:
- Automatic validation
- JSON serialization
- OpenAI structured output compatibility

### 4. OpenAI Function Calling (Tools)

Tools allow the LLM to call external functions:

```python
tools = [
    {
        "type": "function",
        "function": {
            "name": "convert_currency",
            "description": "Convert an amount from one currency to another",
            "parameters": {
                "type": "object",
                "properties": {
                    "amount": {"type": "number"},
                    "from_currency": {"type": "string"},
                    "to_currency": {"type": "string"},
                },
                "required": ["amount", "from_currency", "to_currency"],
            },
        },
    }
]
```


## Project Structure After Week 2

```
expenses_ai_agent/
+-- src/
|   +-- expenses_ai_agent/
|       +-- storage/           # From Week 1
|       +-- llms/
|       |   +-- __init__.py
|       |   +-- base.py        # Assistant Protocol, type aliases
|       |   +-- openai.py      # OpenAIAssistant implementation
|       |   +-- output.py      # ExpenseCategorizationResponse
|       +-- tools/
|       |   +-- __init__.py
|       |   +-- tools.py       # Tool schemas for function calling
|       +-- utils/
|           +-- __init__.py
|           +-- currency.py    # Currency conversion utility
|           +-- date_formatter.py  # Timezone-aware date formatting
+-- tests/
    +-- unit/
        +-- test_week1_*.py    # From Week 1
        +-- test_week2_llm.py  # (copy from curriculum)
        +-- test_week2_utils.py # (copy from curriculum)
```


## Environment Variables

Add these to your `.env` file:

```bash
OPENAI_API_KEY=sk-...         # Required for OpenAI
EXCHANGE_RATE_API_KEY=...     # Required for currency conversion
GROQ_API_KEY=gsk_...          # Optional, for Groq provider
```


## Build Guide

### Step 1: Create the Output Model (`llms/output.py`)

Build `ExpenseCategorizationResponse` first since other modules depend on it:

- Use Pydantic `BaseModel`
- Include: category, total_amount, currency, confidence, cost, comments, timestamp
- Use `Decimal` for amounts (financial precision)
- Use `Currency` enum from your models

### Step 2: Define the Protocol (`llms/base.py`)

Create the `Assistant` Protocol:

- Define `MESSAGES` type alias
- Define `COST` type alias
- Create `LLMProvider` enum (OPENAI, GROQ)
- Define `Assistant` Protocol with three methods

### Step 3: Implement Utilities

**Currency conversion (`utils/currency.py`):**
- Function `convert_currency(amount, from_currency, to_currency) -> Decimal`
- Use ExchangeRate API (or mock for tests)
- Handle API errors gracefully

**Date formatting (`utils/date_formatter.py`):**
- Function `format_datetime(dt, timezone_str) -> str`
- Support common timezone strings
- Return human-readable format

### Step 4: Define Tool Schemas (`tools/tools.py`)

Create OpenAI-compatible tool definitions:
- `CURRENCY_CONVERSION_TOOL` schema
- `DATETIME_FORMATTER_TOOL` schema
- Follow OpenAI function calling format

### Step 5: Implement OpenAI Client (`llms/openai.py`)

Build `OpenAIAssistant` class:
- Constructor takes model name
- `completion()` calls OpenAI API with structured output
- `calculate_cost()` computes token costs per model
- `get_available_models()` returns supported models
- Handle tool calls within completion


## Definition of Done

### Tests to Pass

Copy the test files from `curriculum/week2/tests/` into your `tests/unit/` directory:

- `test_week2_llm.py` (10 tests)
- `test_week2_utils.py` (8 tests)

### Commands - All Must Succeed

| Command | Expected Result |
|---------|-----------------|
| `pytest tests/unit/test_week2_*.py -v` | All 18 tests pass |
| `ruff format --check .` | No formatting issues |
| `ruff check .` | No linting errors |

### You Are Done When

- All 18 tests pass (green)
- No ruff warnings
- You can explain what a Protocol is and why we use it
- You understand how OpenAI function calling works


## Common Issues and Solutions

| Issue | Solution |
|-------|----------|
| "Protocol is not subscriptable" | Use `from typing import Protocol` (Python 3.8+) |
| OpenAI API key error | Check `.env` file and `python-decouple` config |
| Decimal serialization error | Use `model_config = {"json_encoders": {Decimal: str}}` |
| Tool call not returning | Ensure you handle tool_calls in the response |


## Looking Ahead

In Week 3, you will use your LLM layer to build:

- System and user prompts for classification
- ClassificationService that orchestrates the pipeline
- CLI interface with Typer and Rich
- Database persistence with the DB repositories

Your Protocol-based design means you can easily swap OpenAI for Groq or any other provider!

---

**Remember**: Tests define behavior. When in doubt, read the test assertions carefully - they tell you exactly what your code should do.
