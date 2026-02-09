# Week 3: Tools for the Agent - Classification Service and CLI

Welcome to Week 3! This week you will bring everything together to create the classification pipeline. You will build the prompts that guide the LLM, create a service layer that orchestrates classification, implement database repositories, and add a CLI interface for testing your agent.

## What You're Building This Week

```
+------------------------------------------------------------------+
|                    WEEK 3: CLASSIFICATION PIPELINE               |
+------------------------------------------------------------------+

    CLI Command: expenses-ai-agent classify "Coffee for $5"
                              |
                              v
                    +-------------------+
                    |   Typer CLI       |
                    |   (cli.py)        |
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
                    | DBCategoryRepo    |
                    +-------------------+
                              |
                              v
                    +-------------------+
                    |   Rich Console    |
                    |   Output Table    |
                    +-------------------+
```

## Learning Objectives

By the end of this week, you will:

- Design effective prompts for LLM classification
- Implement a Service layer pattern for business logic
- Create database-backed repositories with SQLModel
- Build a CLI with Typer and Rich for beautiful output
- Understand session management and dependency injection
- Write comprehensive unit tests with mocking


## Week 3 Checklist

### Technical Milestones

- [ ] Create `CLASSIFICATION_PROMPT` system prompt with 12 expense categories
- [ ] Create `USER_PROMPT` template for expense descriptions
- [ ] Implement `ClassificationService` with classify and persist methods
- [ ] Implement `DBCategoryRepo` with SQLModel session management
- [ ] Implement `DBExpenseRepo` with CRUD operations
- [ ] Create Typer CLI with `classify` command
- [ ] Add Rich formatting for output display
- [ ] Pass all provided tests

### Concepts to Master

- [ ] Prompt engineering for classification tasks
- [ ] Service layer pattern (separation of concerns)
- [ ] Session injection vs session ownership in repositories
- [ ] Typer CLI with options and arguments
- [ ] Rich tables and console formatting


## Key Concepts This Week

### 1. Prompt Engineering for Classification

The system prompt defines the 12 expense categories:

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

### 2. Service Layer Pattern

The `ClassificationService` encapsulates the entire classification workflow:

```python
@dataclass
class ClassificationService:
    assistant: Assistant
    category_repo: CategoryRepository | None = None
    expense_repo: ExpenseRepository | None = None

    def classify(
        self,
        expense_description: str,
        persist: bool = False
    ) -> ClassificationResult:
        """Classify an expense and optionally persist to database."""
        messages = self._build_messages(expense_description)
        response = self.assistant.completion(messages)

        if persist:
            self._persist_expense(expense_description, response)

        return ClassificationResult(response=response, persisted=persist)
```

Benefits:
- Single responsibility: classification logic in one place
- Testable: mock the assistant for unit tests
- Flexible: optional persistence via dependency injection

### 3. Database Repositories with Session Management

```python
class DBExpenseRepo(ExpenseRepository):
    def __init__(self, db_url: str, session: Session | None = None):
        self._db_url = db_url
        if session:
            self._session = session
            self._owns_session = False  # External session, don't close it
        else:
            engine = create_engine(db_url)
            self._session = Session(engine)
            self._owns_session = True  # We created it, we close it
```

This pattern supports:
- **Standalone usage**: Repository creates its own session
- **Injected session**: For transactions spanning multiple repos
- **Testing**: Pass a test session with in-memory SQLite

### 4. Typer CLI with Rich Output

```python
import typer
from rich.console import Console
from rich.table import Table

app = typer.Typer()
console = Console()

@app.command()
def classify(
    description: str = typer.Argument(..., help="Expense description"),
    db: bool = typer.Option(False, "--db", help="Persist to database"),
):
    """Classify an expense using AI."""
    service = build_classification_service(persist=db)
    result = service.classify(description, persist=db)

    table = Table(title="Classification Result")
    table.add_column("Field", style="cyan")
    table.add_column("Value", style="green")
    table.add_row("Category", result.response.category)
    table.add_row("Amount", f"{result.response.total_amount}")
    # ... more rows

    console.print(table)
```


## Project Structure After Week 3

```
expenses_ai_agent/
+-- src/
|   +-- expenses_ai_agent/
|       +-- storage/           # Week 1 + DB repos
|       |   +-- repo.py        # + DBCategoryRepo, DBExpenseRepo
|       +-- llms/              # Week 2
|       +-- tools/             # Week 2
|       +-- utils/             # Week 2
|       +-- prompts/
|       |   +-- __init__.py
|       |   +-- system.py      # CLASSIFICATION_PROMPT
|       |   +-- user.py        # USER_PROMPT
|       +-- services/
|       |   +-- __init__.py
|       |   +-- classification.py  # ClassificationService
|       +-- cli/
|           +-- __init__.py
|           +-- cli.py         # Typer app
+-- tests/
    +-- unit/
        +-- test_week3_prompts.py
        +-- test_week3_service.py
        +-- test_week3_db_repos.py
        +-- test_week3_cli.py
```


## The 12 Expense Categories

Your system must support these categories:

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
| Other | Anything that does not fit above categories |


## Build Guide

### Step 1: Create Prompts (`prompts/`)

**system.py:**
- Define `CLASSIFICATION_PROMPT` constant
- Include all 12 categories with descriptions
- Specify expected output format (JSON)

**user.py:**
- Define `USER_PROMPT` template
- Use `{expense_description}` placeholder

### Step 2: Implement Classification Service (`services/classification.py`)

- Create `ClassificationResult` dataclass
- Create `ClassificationService` class
- Implement `classify()` method
- Implement `persist_with_category()` for HITL overrides
- Handle missing repos gracefully

### Step 3: Implement DB Repositories (`storage/repo.py`)

**DBCategoryRepo:**
- CRUD operations using SQLModel
- Session management (owned vs injected)
- Proper error handling

**DBExpenseRepo:**
- CRUD operations
- Search by category
- Search by date range

### Step 4: Create CLI (`cli/cli.py`)

- Create Typer app
- Add `classify` command with `--db` option
- Use Rich for formatted output
- Handle errors gracefully


## Definition of Done

### Tests to Pass

Copy the test files from `curriculum/week3/tests/` into your `tests/unit/` directory:

- `test_week3_prompts.py` (4 tests)
- `test_week3_service.py` (8 tests)
- `test_week3_db_repos.py` (12 tests)
- `test_week3_cli.py` (6 tests)

### Commands - All Must Succeed

| Command | Expected Result |
|---------|-----------------|
| `pytest tests/unit/test_week3_*.py -v` | All 30 tests pass |
| `ruff format --check .` | No formatting issues |
| `ruff check .` | No linting errors |
| `expenses-ai-agent classify "Coffee $5" --help` | Shows help text |

### You Are Done When

- All 30 tests pass (green)
- No ruff warnings
- CLI command works: `expenses-ai-agent classify "Test expense"`
- You can explain the Service layer pattern


## Common Issues and Solutions

| Issue | Solution |
|-------|----------|
| "No module named expenses_ai_agent" | Run `uv pip install -e ".[dev]"` |
| Session already closed | Check `_owns_session` logic in repos |
| "Table has no column named X" | Call `SQLModel.metadata.create_all(engine)` |
| Rich not formatting | Ensure `Console()` is used, not `print()` |
| Typer command not found | Check `[project.scripts]` in pyproject.toml |


## Looking Ahead

In Week 4, you will add the Telegram bot interface:

- Input preprocessing and validation
- Telegram bot handlers with conversation flow
- Human-in-the-loop category confirmation
- User preference management

Your classification service will be reused by the Telegram bot!

---

**Pro tip**: When testing the CLI, use `--help` on every command to understand the options. Typer generates beautiful help text automatically.
