# Welcome to Week 1: Scaffolding - Project Setup and Data Models

Welcome to Week 1 of the Expense AI Agent cohort! This week introduces you to the foundational concepts of building an AI-powered expense classification system. You will set up your development environment, understand the project architecture, and implement the core data models that will store expense information.


## What You'll Learn

Week 1 introduces these foundational concepts:

- **Repository Pattern** - Abstract data access for testability and flexibility
- **SQLModel Entities** - Type-safe database models with Pydantic validation
- **StrEnum** - Type-safe string enumerations for currencies and categories
- **Test-Driven Development** - Write code to make tests pass


## The Mental Model Shift

**Traditional database approach:** "Write SQL queries directly wherever you need data"

**Repository pattern approach:** "Abstract data access behind clean interfaces so business logic never knows about the database"

Think of a repository like a librarian. You don't need to know where books are shelved or how the catalog system works. You simply ask the librarian for a book by title, and they handle all the details. Your business logic asks the repository for data, and the repository handles whether that data comes from SQLite, PostgreSQL, or a simple dictionary in memory.


## What Success Looks Like

By the end of this week, your models work like this:

```python
from decimal import Decimal
from expenses_ai_agent.storage.models import Currency, Expense, ExpenseCategory
from expenses_ai_agent.storage.repo import InMemoryCategoryRepository, InMemoryExpenseRepository

# Create repositories
category_repo = InMemoryCategoryRepository()
expense_repo = InMemoryExpenseRepository()

# Add a category
food = ExpenseCategory.create(name="Food")
category_repo.add(food)

# Create and store an expense
expense = Expense.create(
    amount=Decimal("42.50"),
    currency=Currency.EUR,
    description="Lunch at restaurant",
    category=food,
)
expense_repo.add(expense)

# Retrieve and query
all_categories = category_repo.list()  # ["Food"]
food_expenses = expense_repo.search_by_category(food)  # [expense]
```


## The Big Picture: What You're Building

Over six weeks, you will build a complete AI-powered expense tracking system:

```
+-------------------------------------------------------------------------+
|                    EXPENSE AI AGENT ARCHITECTURE                         |
+-------------------------------------------------------------------------+

                              USER INPUT
                                  |
                                  v
                    +-------------------------+
                    |   "Coffee at Starbucks  |
                    |        for $5.50"       |
                    +-------------------------+
                                  |
          +-------------------+---+---+-------------------+
          |                   |       |                   |
          v                   v       v                   v
    +-----------+      +----------+  +--------+    +-----------+
    |    CLI    |      | Telegram |  |  REST  |    | Streamlit |
    |  (Typer)  |      |   Bot    |  |  API   |    | Dashboard |
    +-----------+      +----------+  +--------+    +-----------+
          |                   |           |               |
          +-------------------+-----------+---------------+
                                  |
                                  v
                    +-------------------------+
                    |    Services Layer       |
                    |  (Classification +      |
                    |   Preprocessing)        |
                    +-------------------------+
                                  |
                                  v
                    +-------------------------+
                    |   LLM Assistant Layer   |
                    |  (OpenAI/Groq Protocol) |
                    +-------------------------+
                                  |
                                  v
                    +-------------------------+
                    |   Storage Layer         |
                    |  (Repository Pattern)   |  <-- WEEK 1 FOCUS
                    +-------------------------+
                                  |
                                  v
                    +-------------------------+
                    |       SQLite DB         |
                    |   (SQLModel/SQLAlchemy) |
                    +-------------------------+
                              OUTPUT
```

**Week-by-week progression:**

| Week | Focus | Key Components |
|------|-------|----------------|
| Week 1 | Scaffolding | Project setup, data models, categories, basic storage |
| Week 2 | Assistant Setup | LLM Protocol, OpenAI client, tools, structured outputs |
| Week 3 | Tools for the Agent | Classification service, prompts, CLI, expense persistence |
| Week 4 | Telegram Integration | Bot handlers, preprocessing, human-in-the-loop |
| Week 5 | Web Interface | FastAPI backend, Streamlit frontend, multiuser support |
| Week 6 | Deploy + Docs | Docker, CI/CD, documentation, deployment |

Each week builds on the previous one. By Week 6, you will have a production-ready expense tracking system.


## Why the Repository Pattern Matters

Without the Repository pattern, database logic spreads throughout your code:

```python
# Without Repository Pattern (tight coupling)
def get_expense(expense_id: int):
    conn = sqlite3.connect("expenses.db")
    cursor = conn.execute("SELECT * FROM expenses WHERE id = ?", (expense_id,))
    return cursor.fetchone()
```

With the Repository pattern, data access is abstracted:

```python
# With Repository Pattern (loose coupling)
def get_expense(repo: ExpenseRepository, expense_id: int):
    return repo.get(expense_id)
```

**Why it matters:**

- **Testability**: Use in-memory repos for unit tests, DB repos for integration tests
- **Flexibility**: Switch from SQLite to PostgreSQL without touching business logic
- **Separation of concerns**: Data access logic stays in one place


## Technical Milestones

By the end of Week 1, you'll have:

- [ ] Development environment with Python 3.12+ and UV
- [ ] `Currency` StrEnum with 10 currency codes
- [ ] `ExpenseCategory` SQLModel entity
- [ ] `Expense` SQLModel entity with category relationship
- [ ] `InMemoryCategoryRepository` with CRUD operations
- [ ] `InMemoryExpenseRepository` with search capabilities
- [ ] All 26 tests passing


## Ready?

This week lays the foundation for everything that follows. The models and repositories you build now will be used by the LLM classification system, the Telegram bot, the REST API, and the web dashboard.

Let's start by joining the community and setting up your development environment.
