# The Repository Pattern

The Repository pattern is a design pattern that abstracts data access behind a clean interface. This lesson explains why we use it and how it benefits our expense tracking system.


## Why the Repository Pattern Exists

Without abstraction, database code spreads throughout your application:

```python
# Scattered database calls - hard to test, hard to change
def classify_expense(description: str):
    conn = sqlite3.connect("expenses.db")
    # ... business logic mixed with database logic
    cursor.execute("INSERT INTO expenses ...")
    conn.commit()
```

Problems with this approach:

- **Testing requires a real database** - Slow and brittle tests
- **Changing databases is painful** - SQLite to PostgreSQL requires finding every query
- **Business logic is polluted** - Hard to understand what the code actually does


## Core Concept

A repository is an abstraction that provides a collection-like interface for accessing domain objects:

```python
from abc import ABC, abstractmethod

class ExpenseRepository(ABC):
    """Abstract interface for expense data access."""

    @abstractmethod
    def add(self, expense: Expense) -> None:
        """Add an expense to the repository."""
        ...

    @abstractmethod
    def get(self, expense_id: int) -> Expense | None:
        """Retrieve an expense by ID."""
        ...

    @abstractmethod
    def list(self) -> list[Expense]:
        """List all expenses."""
        ...

    @abstractmethod
    def delete(self, expense_id: int) -> None:
        """Remove an expense."""
        ...
```

**When to use:** Use the Repository pattern when you want to decouple your domain logic from data access concerns. This is especially valuable when you have complex queries or need to swap storage backends.


## Two Implementation Families

We implement two families of repositories:

### In-Memory Repositories (for testing)

```python
class InMemoryExpenseRepository(ExpenseRepository):
    """Dict-backed repository for fast unit tests."""

    def __init__(self):
        self._storage: dict[int, Expense] = {}
        self._next_id = 1

    def add(self, expense: Expense) -> None:
        expense.id = self._next_id
        self._storage[expense.id] = expense
        self._next_id += 1

    def get(self, expense_id: int) -> Expense | None:
        return self._storage.get(expense_id)
```

### Database Repositories (for production)

```python
class DBExpenseRepository(ExpenseRepository):
    """SQLModel-backed repository for production."""

    def __init__(self, session: Session):
        self._session = session

    def add(self, expense: Expense) -> None:
        self._session.add(expense)
        self._session.commit()
        self._session.refresh(expense)
```


## Benefits in Practice

**Fast unit tests:**

```python
def test_classification_persists_expense():
    # In-memory repo - no database needed
    repo = InMemoryExpenseRepository()
    service = ClassificationService(repo)

    service.classify("Coffee $5")

    assert len(repo.list()) == 1
```

**Easy swapping:**

```python
def create_service(use_db: bool = False):
    if use_db:
        return ClassificationService(DBExpenseRepository())
    return ClassificationService(InMemoryExpenseRepository())
```


## Repository Pattern in Our Project

For the expense tracking system, we define two repositories:

| Repository | Purpose | Key Methods |
|------------|---------|-------------|
| `CategoryRepository` | Manage expense categories | `add`, `get`, `list`, `update`, `delete` |
| `ExpenseRepository` | Manage expenses | `add`, `get`, `list`, `delete`, `search_by_category` |


## Further Reading

- [P of EAA: Repository](https://martinfowler.com/eaaCatalog/repository.html) - Martin Fowler's original pattern description
- [Python ABC documentation](https://docs.python.org/3/library/abc.html) - Abstract base classes in Python
