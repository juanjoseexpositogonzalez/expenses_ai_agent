# Week 2 Success Criteria

Use this checklist to verify you've completed all Week 2 requirements.


## Validation Commands

All of these commands must succeed:

| Command | Expected Result |
|---------|-----------------|
| `pytest tests/unit/test_week2.py -v` | All 18 tests pass |
| `ruff format --check .` | No formatting issues |
| `ruff check .` | No linting errors |


## Technical Checklist

### Output Model (`llms/output.py`)

- [ ] `ExpenseCategorizationResponse` Pydantic BaseModel
- [ ] Fields: category, total_amount (Decimal), currency (Currency enum), confidence, cost
- [ ] Optional comments field
- [ ] Auto-generated timestamp field
- [ ] JSON serialization works

### Base Definitions (`llms/base.py`)

- [ ] `MESSAGES` type alias (`list[dict[str, str]]`)
- [ ] `COST` type alias (`dict[str, list[Decimal]]`)
- [ ] `LLMProvider` StrEnum with OPENAI, GROQ
- [ ] `Assistant` Protocol with completion, calculate_cost, get_available_models

### Utilities

- [ ] `convert_currency(amount, from_currency, to_currency)` in `utils/currency.py`
- [ ] Returns Decimal
- [ ] Handles same-currency case without API call
- [ ] Uses ExchangeRate API for conversions

- [ ] `format_datetime(dt, timezone_str)` in `utils/date_formatter.py`
- [ ] Returns formatted string
- [ ] Supports timezone conversion

### Tool Schemas (`tools/tools.py`)

- [ ] `CURRENCY_CONVERSION_TOOL` dict following OpenAI format
- [ ] `DATETIME_FORMATTER_TOOL` dict following OpenAI format
- [ ] Both have `type: "function"` and proper structure


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
        +-- test_week1.py      # From Week 1
        +-- test_week2.py      # Week 2 tests
```


## Conceptual Understanding

You should be able to answer these questions:

1. **Why use Protocol instead of ABC for the Assistant?**
   - Structural typing works with third-party classes
   - No inheritance required
   - Better for dependency injection

2. **Why use Pydantic for LLM responses?**
   - Automatic validation
   - JSON serialization
   - OpenAI structured outputs compatibility

3. **What's the purpose of type aliases?**
   - Clean, readable code
   - Define complex types once
   - Self-documenting function signatures

4. **How do function calling tools work?**
   - Define schema in OpenAI format
   - LLM requests tool execution
   - Your code runs the tool
   - Result sent back to LLM


## You Are Done When

- All 18 tests pass (green)
- No ruff warnings
- You can explain what a Protocol is and why we use it
- You understand how OpenAI function calling works


## Common Issues and Solutions

| Issue | Solution |
|-------|----------|
| "Protocol is not subscriptable" | Use `from typing import Protocol` (Python 3.8+) |
| OpenAI API key error | Check `.env` file and `python-decouple` config |
| Decimal serialization error | Use `model_config = ConfigDict(json_encoders={Decimal: str})` |
| Tool call not returning | Ensure you handle tool_calls in the response |
