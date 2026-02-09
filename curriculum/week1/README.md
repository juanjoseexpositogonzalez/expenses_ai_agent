# Week 1: Scaffolding - Project Setup and Data Models

Welcome to Week 1 of the Expense AI Agent cohort! This week introduces you to the foundational concepts of building an AI-powered expense classification system. You will set up your development environment, understand the project architecture, and implement the core data models that will store expense information.

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
                    |  (Repository Pattern)   |
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


## Learning Objectives

By the end of this week, you will:

- Set up a complete Python development environment with UV, pytest, and ruff
- Understand the Repository pattern for data access abstraction
- Implement SQLModel entities for expenses and categories
- Create in-memory repositories for testing
- Write comprehensive tests using pytest fixtures and parametrize
- Understand Python's `StrEnum` for type-safe enumerations
- Master the basics of SQLModel relationships


## Week 1 Checklist

### Development Environment Setup

- [ ] Install Python 3.12+ and UV package manager
- [ ] Clone the repository and create your feature branch
- [ ] Install dependencies with `uv pip install -e ".[dev]"`
- [ ] Configure IDE with Python/ruff support
- [ ] Set up `.env` file from `.env.example`

### Technical Milestones

- [ ] Implement `Currency` StrEnum with 10 currency codes
- [ ] Implement `ExpenseCategory` SQLModel with name field
- [ ] Implement `Expense` SQLModel with amount, currency, description, date, category relationship
- [ ] Create `InMemoryCategoryRepository` with CRUD operations
- [ ] Pass all provided tests using TDD approach

### Collaboration & Process

- [ ] Set up Git workflow (branching, commits)
- [ ] Run quality checks: `ruff format --check .` and `ruff check .`
- [ ] Achieve 100% test pass rate for Week 1 tests


## Mental Model: Why These Patterns?

### The Repository Pattern

If you have worked with databases before, you might be used to writing SQL directly. The Repository pattern abstracts data access behind a clean interface:

```python
# Without Repository Pattern (tight coupling)
def get_expense(expense_id: int):
    conn = sqlite3.connect("expenses.db")
    cursor = conn.execute("SELECT * FROM expenses WHERE id = ?", (expense_id,))
    return cursor.fetchone()

# With Repository Pattern (loose coupling)
def get_expense(repo: ExpenseRepository, expense_id: int):
    return repo.get(expense_id)
```

**Why it matters:**
- **Testability**: Swap in-memory repos for unit tests, DB repos for integration
- **Flexibility**: Change from SQLite to PostgreSQL without touching business logic
- **Separation of concerns**: Data access logic stays in one place

### SQLModel: The Best of Both Worlds

SQLModel combines Pydantic (validation) with SQLAlchemy (ORM):

```python
from sqlmodel import Field, SQLModel

class Expense(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    amount: Decimal
    description: str | None = None
```

- Type hints become database columns
- Pydantic validates data automatically
- SQLAlchemy handles database operations


## Project Structure

After Week 1, your project should have this structure:

```
expenses_ai_agent/
+-- src/
|   +-- expenses_ai_agent/
|       +-- __init__.py
|       +-- storage/
|           +-- __init__.py
|           +-- models.py          # Currency, ExpenseCategory, Expense
|           +-- exceptions.py      # CategoryNotFoundError, ExpenseNotFoundError
|           +-- repo.py            # Repository abstract classes + InMemory implementations
+-- tests/
|   +-- unit/
|       +-- test_week1_models.py   # (copy from curriculum)
|       +-- test_week1_repos.py    # (copy from curriculum)
+-- pyproject.toml
+-- .env.example
```


## Key Concepts This Week

### 1. StrEnum for Type-Safe Categories

```python
from enum import StrEnum, verify, UNIQUE

@verify(UNIQUE)
class Currency(StrEnum):
    EUR = "EUR"
    USD = "USD"
    GBP = "GBP"
    # ... more currencies
```

`StrEnum` gives you:
- String values that work in JSON/databases
- Type safety (IDE autocomplete, type checking)
- Iteration (`for c in Currency`)

### 2. SQLModel Relationships

```python
class ExpenseCategory(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(index=True, unique=True)
    expenses: list["Expense"] = Relationship(back_populates="category")

class Expense(SQLModel, table=True):
    category_id: int | None = Field(default=None, foreign_key="expensecategory.id")
    category: ExpenseCategory | None = Relationship(back_populates="expenses")
```

### 3. Abstract Base Classes for Repositories

```python
from abc import ABC, abstractmethod

class CategoryRepository(ABC):
    @abstractmethod
    def add(self, category: ExpenseCategory) -> None: ...

    @abstractmethod
    def get(self, name: str) -> ExpenseCategory | None: ...
```


## Definition of Done

### Tests to Pass

Copy the test files from `curriculum/week1/tests/` into your `tests/unit/` directory:

- `test_week1_models.py` (12 tests)
- `test_week1_repos.py` (14 tests)

### Commands - All Must Succeed

| Command | Expected Result |
|---------|-----------------|
| `pytest tests/unit/test_week1_*.py -v` | All 26 tests pass |
| `ruff format --check .` | No formatting issues |
| `ruff check .` | No linting errors |

### You Are Done When

- All 26 tests pass (green)
- No ruff warnings
- You have NOT looked at the author's implementation
- You can explain what a Repository pattern is and why we use it


## Common Issues and Solutions

| Issue | Solution |
|-------|----------|
| "ModuleNotFoundError: expenses_ai_agent" | Run `uv pip install -e ".[dev]"` to install in editable mode |
| "Table already exists" SQLModel error | Use `sqlite:///:memory:` for tests or delete `expenses.db` |
| Relationship not loading | Add `Relationship(back_populates="...")` on both sides |
| Decimal precision issues | Use `Decimal("10.50")` not `Decimal(10.50)` |


## Looking Ahead

In Week 2, you will build the LLM integration layer:

- Define an `Assistant` Protocol for LLM providers
- Implement the OpenAI client with structured outputs
- Add tools for currency conversion and date formatting
- Create the `ExpenseCategorizationResponse` model

The foundation you build this week (models + repositories) will be used by the classification service in Week 3.

---

**Remember**: The tests are your specification. Run them often, read their assertions carefully, and let them guide your implementation. Happy coding!
