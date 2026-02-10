# Welcome to Week 2: Assistant Setup - LLM Protocol and Tools

Welcome to Week 2! This week you will build the LLM integration layer that powers the AI classification. You will learn about Python Protocols for type-safe abstractions, implement an OpenAI client with structured outputs, and create utility tools for currency conversion and date formatting.


## What You'll Learn

Week 2 introduces these essential patterns:

- **Python Protocol** - Structural typing for swappable LLM providers
- **Pydantic Structured Outputs** - Type-safe responses from LLMs
- **Type Aliases** - Clean code with `MESSAGES` and `COST` aliases
- **OpenAI Function Calling** - Let the LLM use tools


## The Mental Model Shift

**Week 1 mindset:** "Store and retrieve data through clean interfaces"

**Week 2 mindset:** "Define contracts that any LLM provider can satisfy"

Think of a Protocol like a power outlet specification. Any device that fits the outlet works. Any LLM provider that satisfies the `Assistant` protocol works with our classification system. OpenAI, Groq, Anthropic - all can be plugged in without changing business logic.


## What Success Looks Like

By the end of this week, your LLM layer works like this:

```python
from expenses_ai_agent.llms.openai import OpenAIAssistant
from expenses_ai_agent.llms.base import MESSAGES

# Create an assistant
assistant = OpenAIAssistant(model="gpt-4o-mini")

# Prepare messages
messages: MESSAGES = [
    {"role": "system", "content": "Classify this expense..."},
    {"role": "user", "content": "Coffee at Starbucks $5.50"},
]

# Get structured response
response = assistant.completion(messages)
print(response.category)     # "Food"
print(response.total_amount) # Decimal("5.50")
print(response.currency)     # Currency.USD
print(response.confidence)   # 0.95
```


## Architecture: Week 2's Place

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


## Why Protocol Over ABC?

In Week 1, you used Abstract Base Classes (ABC) for repositories. This week introduces Protocols:

| ABC (Week 1) | Protocol (Week 2) |
|--------------|-------------------|
| Requires explicit inheritance | No inheritance needed |
| `class MyRepo(Repository)` | Just implement the methods |
| Nominal typing | Structural typing (duck typing) |
| Good for internal code | Better for third-party integration |

Protocols are ideal for LLM providers because you might use a third-party client that you don't control. If it has the right methods, it works.


## Technical Milestones

By the end of Week 2, you'll have:

- [ ] `Assistant` Protocol in `llms/base.py`
- [ ] `ExpenseCategorizationResponse` Pydantic model
- [ ] `OpenAIAssistant` class satisfying the Protocol
- [ ] Currency conversion utility (ExchangeRate API)
- [ ] Date formatter utility with timezone support
- [ ] Tool schemas for function calling
- [ ] All 18 tests passing


## Ready?

This week builds the brain of your expense agent. The Protocol-based design means you can easily swap OpenAI for Groq or any other provider.

Let's start by reviewing what you learned in Week 1.
