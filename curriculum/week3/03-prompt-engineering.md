# Prompt Engineering for Classification

Effective prompts guide the LLM to produce consistent, structured outputs. This lesson covers designing system and user prompts for expense classification.


## Why Prompts Matter

The same LLM produces very different results with different prompts:

**Poor prompt:**
```
"Classify this expense"
```
LLM output: "I think this might be food related, maybe coffee?"

**Good prompt:**
```
"You are an expense classification assistant. Classify into exactly one
of these categories: Food, Transport, Entertainment... Respond with JSON."
```
LLM output: `{"category": "Food", "confidence": 0.95}`


## System Prompt Structure

A good classification system prompt includes:

1. **Role definition** - What the assistant does
2. **Category list** - All valid categories with examples
3. **Extraction instructions** - What to extract
4. **Output format** - How to respond (JSON)

```python
CLASSIFICATION_PROMPT = """You are an expense classification assistant.
Analyze the expense description and classify it into one of these categories:

1. Food - Groceries, restaurants, cafes, snacks
2. Transport - Taxi, bus, train, fuel, parking
3. Entertainment - Movies, concerts, games, streaming
4. Shopping - Clothing, electronics, household items
5. Health - Medicine, doctor visits, gym
6. Bills - Utilities, phone, internet, subscriptions
7. Education - Books, courses, training
8. Travel - Hotels, flights, vacation expenses
9. Services - Haircuts, repairs, professional services
10. Gifts - Presents for others
11. Investments - Stocks, savings, financial products
12. Other - Anything that doesn't fit above

Extract:
- The expense category
- The total amount (numeric value)
- The currency (default EUR if not specified)
- Your confidence level (0.0 to 1.0)

Respond with valid JSON matching the required schema.
"""
```


## User Prompt Template

The user prompt provides the expense description:

```python
USER_PROMPT = "Classify this expense: {expense_description}"
```

Usage:

```python
messages = [
    {"role": "system", "content": CLASSIFICATION_PROMPT},
    {"role": "user", "content": USER_PROMPT.format(
        expense_description="Coffee at Starbucks $5.50"
    )},
]
```


## Best Practices

### Be Specific About Categories

```python
# Good - clear boundaries
"Food - Groceries, restaurants, cafes, snacks (NOT meal delivery fees)"
"Transport - Taxi, bus, train, fuel (NOT food purchased during travel)"

# Bad - ambiguous
"Food - Things you eat"
"Transport - Getting places"
```

### Specify Default Behavior

```python
# Good - clear defaults
"Currency: default EUR if not specified"
"If unsure, use category 'Other' with lower confidence"

# Bad - leaves LLM guessing
"Figure out the currency"
```

### Request Structured Output

```python
# Good - explicit format
"Respond with valid JSON matching the ExpenseCategorizationResponse schema"

# Bad - ambiguous format
"Give me the classification"
```


## Python Comparison

| Traditional code | LLM prompts |
|-----------------|-------------|
| `if/else` logic | Natural language rules |
| Exact matching | Fuzzy understanding |
| Explicit errors | Graceful fallbacks |
| Deterministic | Probabilistic (confidence scores) |


## Prompts in Our Project

We define two constants:

| Prompt | File | Purpose |
|--------|------|---------|
| `CLASSIFICATION_PROMPT` | `prompts/system.py` | Role + categories + rules |
| `USER_PROMPT` | `prompts/user.py` | Template for expense input |


## Further Reading

- [OpenAI Prompt Engineering Guide](https://platform.openai.com/docs/guides/prompt-engineering)
- [Anthropic Prompt Engineering](https://docs.anthropic.com/en/docs/build-with-claude/prompt-engineering)
