# Looking Ahead: Week 2

Congratulations on completing Week 1! You now have a solid foundation of models and repositories.


## What's Next

In Week 2, you will build the LLM integration layer:

- **Python Protocol** - Define an `Assistant` protocol for LLM providers (OpenAI, Groq)
- **Structured Outputs** - Use Pydantic to parse LLM responses into `ExpenseCategorizationResponse`
- **Tools/Function Calling** - Let the LLM call utility functions for currency conversion and date formatting
- **Type Aliases** - Clean up complex types with `MESSAGES` and `COST` aliases


## How Week 1 Connects to Week 2

The models you built this week become the output of the LLM layer:

```
Week 2: LLM Layer
     |
     v
ExpenseCategorizationResponse (Pydantic model)
     |
     v
Week 1: Storage Layer
Expense + ExpenseCategory (SQLModel entities)
     |
     v
Database
```

Your `Currency` enum will be used in the LLM response. Your `ExpenseCategory` entities will store the classifications. Your repositories will persist the results.


## Prepare for Week 2

Before starting Week 2, make sure you:

1. Have all 26 Week 1 tests passing
2. Understand how abstract base classes define interfaces
3. Have your OpenAI API key ready (add to `.env`)

See you in Week 2!
