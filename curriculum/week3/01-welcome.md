# Welcome to Week 3: Tools for the Agent - Classification Service and CLI

Welcome to Week 3! This week you will bring everything together to create the classification pipeline. You will build the prompts that guide the LLM, create a service layer that orchestrates classification, implement database repositories, and add a CLI interface for testing your agent.


## What You'll Learn

Week 3 introduces these essential patterns:

- **Prompt Engineering** - Design system and user prompts for classification
- **Service Layer Pattern** - Encapsulate business logic in a reusable service
- **Database Repositories** - Persist expenses with SQLModel
- **CLI with Typer** - Build a beautiful command-line interface


## The Mental Model Shift

**Week 2 mindset:** "Define contracts for LLM providers"

**Week 3 mindset:** "Orchestrate the entire classification workflow in a single service"

Think of the ClassificationService like a restaurant kitchen. The chef (service) coordinates between the pantry (prompts), the cooking equipment (LLM), and the storage (database). Customers (CLI, bot, API) just ask for a dish - they don't need to know the internal workflow.


## What Success Looks Like

By the end of this week, your classification pipeline works like this:

```bash
# Classify an expense
expenses-ai-agent classify "Coffee at Starbucks for $5.50"

# Classify and persist to database
expenses-ai-agent classify "Taxi to airport 45 EUR" --db
```

Output:
```
+------------------+----------------------------+
|      Field       |           Value            |
+------------------+----------------------------+
| Category         | Food                       |
| Amount           | 5.50                       |
| Currency         | USD                        |
| Confidence       | 95%                        |
| Persisted        | No                         |
+------------------+----------------------------+
```


## Architecture: Week 3's Place

```
+------------------------------------------------------------------+
|                    WEEK 3: CLASSIFICATION PIPELINE               |
+------------------------------------------------------------------+

    CLI Command: expenses-ai-agent classify "Coffee for $5"
                              |
                              v
                    +-------------------+
                    |   Typer CLI       |
                    +-------------------+
                              |
                              v
                    +-------------------+
                    | Classification-   |
                    | Service           |
                    +-------------------+
                              |
              +---------------+---------------+
              |               |               |
              v               v               v
    +-------------+   +-------------+   +-------------+
    | System      |   | User        |   | Assistant   |
    | Prompt      |   | Prompt      |   | (OpenAI)    |
    +-------------+   +-------------+   +-------------+
                              |
                              v
                    +-------------------+
                    | ExpenseCategori-  |
                    | zationResponse    |
                    +-------------------+
                              |
                              v (optional --db flag)
                    +-------------------+
                    | DBExpenseRepo     |
                    +-------------------+
                              |
                              v
                    +-------------------+
                    |   Rich Console    |
                    |   Output Table    |
                    +-------------------+
```


## The 12 Expense Categories

Your system will classify expenses into these categories:

| Category | Examples |
|----------|----------|
| Food | Groceries, restaurants, cafes, coffee shops |
| Transport | Taxi, Uber, bus, train, fuel, parking |
| Entertainment | Movies, concerts, games, streaming services |
| Shopping | Clothing, electronics, household items |
| Health | Medicine, doctor visits, gym membership |
| Bills | Utilities, phone, internet, subscriptions |
| Education | Books, courses, online learning, training |
| Travel | Hotels, flights, vacation expenses |
| Services | Haircuts, repairs, professional services |
| Gifts | Presents for birthdays, holidays |
| Investments | Stocks, savings, financial products |
| Other | Anything that doesn't fit above categories |


## Technical Milestones

By the end of Week 3, you'll have:

- [ ] `CLASSIFICATION_PROMPT` with 12 expense categories
- [ ] `USER_PROMPT` template for expense descriptions
- [ ] `ClassificationService` with classify and persist methods
- [ ] `DBCategoryRepo` with SQLModel session management
- [ ] `DBExpenseRepo` with CRUD and search operations
- [ ] Typer CLI with `classify` command
- [ ] Rich formatting for beautiful output
- [ ] All 30 tests passing


## Ready?

This week connects all the pieces. The service you build will be reused by the Telegram bot (Week 4), REST API, and web dashboard (Week 5).

Let's start by reviewing the LLM layer from Week 2.
