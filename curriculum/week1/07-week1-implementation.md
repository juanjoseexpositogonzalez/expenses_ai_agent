# Week 1 Implementation: Data Models and Repositories

This implementation exercise teaches you to build the storage layer for the expense tracking system using Test-Driven Development.


## Learning Goals

By the end of this implementation, you will:

- Implement a `Currency` StrEnum with 10 currency codes
- Create `ExpenseCategory` and `Expense` SQLModel entities
- Build `InMemoryCategoryRepository` and `InMemoryExpenseRepository`
- Define custom exceptions for error handling
- Understand how abstract base classes define interfaces


## What You're Building

**Input:** Python code that models expenses and provides in-memory storage

**Output:** A working storage layer that passes all 26 tests

```python
from decimal import Decimal
from expenses_ai_agent.storage.models import Currency, Expense, ExpenseCategory
from expenses_ai_agent.storage.repo import InMemoryCategoryRepository

# Create and use repositories
repo = InMemoryCategoryRepository()
repo.add(ExpenseCategory.create(name="Food"))
repo.list()  # ["Food"]
```


## What Are Repositories?

Repositories provide a collection-like interface for domain objects. Instead of writing SQL directly, you interact with objects through methods like `add()`, `get()`, and `list()`.

For Week 1, we implement in-memory repositories backed by Python dictionaries. These are perfect for unit testing because they're fast and require no database setup.


## What You're Implementing

### Storage Models (`storage/models.py`)

```python
class Currency(StrEnum):
    """10 currency codes as a StrEnum."""
    # Your implementation

class ExpenseCategory(SQLModel, table=True):
    """Category entity with id, name, and relationship to expenses."""
    # Your implementation

class Expense(SQLModel, table=True):
    """Expense entity with amount, currency, description, date, and category."""
    # Your implementation
```

### Custom Exceptions (`storage/exceptions.py`)

```python
class CategoryNotFoundError(Exception):
    """Raised when a category is not found."""
    # Your implementation

class ExpenseNotFoundError(Exception):
    """Raised when an expense is not found."""
    # Your implementation
```

### Repositories (`storage/repo.py`)

```python
class CategoryRepository(ABC):
    """Abstract base class for category repositories."""
    # Define abstract methods: add, get, list, update, delete

class InMemoryCategoryRepository(CategoryRepository):
    """Dict-backed implementation for testing."""
    # Your implementation

class ExpenseRepository(ABC):
    """Abstract base class for expense repositories."""
    # Define abstract methods: add, get, list, delete, search_by_category

class InMemoryExpenseRepository(ExpenseRepository):
    """Dict-backed implementation for testing."""
    # Your implementation
```


## Test Suite

Copy these tests to your `tests/unit/test_week1.py` file:

```python
"""
Week 1 - Definition of Done: Data Models and Repositories

Run: pytest tests/unit/test_week1.py -v
All tests must pass to complete Week 1.
"""

from datetime import datetime, timezone
from decimal import Decimal

import pytest


class TestCurrencyEnum:
    """Tests for the Currency enumeration."""

    def test_currency_is_string_enum(self):
        """Currency should be a StrEnum so values work as strings."""
        from expenses_ai_agent.storage.models import Currency

        assert Currency.EUR == "EUR"
        assert Currency.USD == "USD"
        assert str(Currency.EUR) == "EUR"

    def test_currency_has_required_values(self):
        """Currency enum must include at least these 10 common currencies."""
        from expenses_ai_agent.storage.models import Currency

        required_currencies = ["EUR", "USD", "GBP", "JPY", "CHF", "CAD", "AUD", "CNY", "INR", "MXN"]

        for code in required_currencies:
            assert hasattr(Currency, code), f"Currency.{code} is missing"
            assert Currency[code].value == code

    def test_currency_is_iterable(self):
        """Should be able to iterate over all currency values."""
        from expenses_ai_agent.storage.models import Currency

        currencies = list(Currency)
        assert len(currencies) >= 10
        assert all(isinstance(c, Currency) for c in currencies)


class TestExpenseCategory:
    """Tests for the ExpenseCategory model."""

    def test_category_has_required_fields(self):
        """ExpenseCategory must have id and name fields."""
        from expenses_ai_agent.storage.models import ExpenseCategory

        category = ExpenseCategory(name="Food")

        assert hasattr(category, "id")
        assert hasattr(category, "name")
        assert category.name == "Food"
        assert category.id is None

    def test_category_str_representation(self):
        """ExpenseCategory __str__ should return the category name."""
        from expenses_ai_agent.storage.models import ExpenseCategory

        category = ExpenseCategory(name="Transport")
        assert str(category) == "Transport"

    def test_category_create_class_method(self):
        """ExpenseCategory.create() should be a convenient factory method."""
        from expenses_ai_agent.storage.models import ExpenseCategory

        category = ExpenseCategory.create(name="Entertainment")

        assert isinstance(category, ExpenseCategory)
        assert category.name == "Entertainment"

    def test_category_name_is_indexed(self):
        """The name field should be configured for database indexing."""
        from expenses_ai_agent.storage.models import ExpenseCategory

        assert "name" in ExpenseCategory.model_fields


class TestExpense:
    """Tests for the Expense model."""

    def test_expense_has_required_fields(self):
        """Expense must have all required fields for expense tracking."""
        from expenses_ai_agent.storage.models import Currency, Expense

        expense = Expense(
            amount=Decimal("42.50"),
            currency=Currency.EUR,
            description="Lunch at restaurant",
        )

        assert hasattr(expense, "id")
        assert hasattr(expense, "amount")
        assert hasattr(expense, "currency")
        assert hasattr(expense, "description")
        assert hasattr(expense, "date")
        assert hasattr(expense, "category_id")
        assert hasattr(expense, "category")

    def test_expense_amount_is_decimal(self):
        """Amount should use Decimal for financial precision."""
        from expenses_ai_agent.storage.models import Currency, Expense

        expense = Expense(
            amount=Decimal("19.99"),
            currency=Currency.USD,
        )

        assert isinstance(expense.amount, Decimal)
        assert expense.amount == Decimal("19.99")

    def test_expense_currency_default(self):
        """Currency should default to EUR if not specified."""
        from expenses_ai_agent.storage.models import Currency, Expense

        expense = Expense(amount=Decimal("10.00"))

        assert expense.currency == Currency.EUR

    def test_expense_date_defaults_to_now(self):
        """Date should default to current UTC time."""
        from expenses_ai_agent.storage.models import Expense

        before = datetime.now(timezone.utc)
        expense = Expense(amount=Decimal("5.00"))
        after = datetime.now(timezone.utc)

        assert expense.date is not None
        assert before <= expense.date <= after or (after - before).total_seconds() < 2

    def test_expense_str_representation(self):
        """Expense __str__ should provide a readable summary."""
        from expenses_ai_agent.storage.models import Currency, Expense

        expense = Expense(
            amount=Decimal("25.00"),
            currency=Currency.GBP,
            description="Book purchase",
        )

        result = str(expense)
        assert "25" in result
        assert "GBP" in result

    def test_expense_create_class_method(self):
        """Expense.create() should be a convenient factory method."""
        from expenses_ai_agent.storage.models import Currency, Expense, ExpenseCategory

        category = ExpenseCategory(id=1, name="Shopping")

        expense = Expense.create(
            amount=Decimal("99.99"),
            currency=Currency.USD,
            description="New headphones",
            category=category,
        )

        assert isinstance(expense, Expense)
        assert expense.amount == Decimal("99.99")
        assert expense.currency == Currency.USD
        assert expense.description == "New headphones"
        assert expense.category == category

    def test_expense_optional_telegram_user_id(self):
        """Expense should support optional telegram_user_id for multiuser."""
        from expenses_ai_agent.storage.models import Expense

        expense = Expense(
            amount=Decimal("10.00"),
            telegram_user_id=12345,
        )

        assert expense.telegram_user_id == 12345

        expense_no_user = Expense(amount=Decimal("10.00"))
        assert expense_no_user.telegram_user_id is None


class TestStorageExceptions:
    """Tests for custom storage exceptions."""

    def test_category_not_found_error_exists(self):
        """CategoryNotFoundError should be a custom exception."""
        from expenses_ai_agent.storage.exceptions import CategoryNotFoundError

        error = CategoryNotFoundError("Food")
        assert isinstance(error, Exception)
        assert "Food" in str(error)

    def test_expense_not_found_error_exists(self):
        """ExpenseNotFoundError should be a custom exception."""
        from expenses_ai_agent.storage.exceptions import ExpenseNotFoundError

        error = ExpenseNotFoundError(123)
        assert isinstance(error, Exception)
        assert "123" in str(error)


class TestInMemoryCategoryRepository:
    """Tests for the in-memory category repository."""

    @pytest.fixture
    def repo(self):
        """Create a fresh in-memory category repository for each test."""
        from expenses_ai_agent.storage.repo import InMemoryCategoryRepository

        return InMemoryCategoryRepository()

    @pytest.fixture
    def sample_category(self):
        """Create a sample category for testing."""
        from expenses_ai_agent.storage.models import ExpenseCategory

        return ExpenseCategory.create(name="Food")

    def test_add_category(self, repo, sample_category):
        """Should be able to add a category to the repository."""
        repo.add(sample_category)

        result = repo.get("Food")
        assert result is not None
        assert result.name == "Food"

    def test_get_nonexistent_category_returns_none(self, repo):
        """Getting a non-existent category should return None."""
        result = repo.get("NonExistent")
        assert result is None

    def test_list_categories(self, repo):
        """Should list all category names."""
        from expenses_ai_agent.storage.models import ExpenseCategory

        repo.add(ExpenseCategory.create(name="Food"))
        repo.add(ExpenseCategory.create(name="Transport"))
        repo.add(ExpenseCategory.create(name="Entertainment"))

        names = repo.list()

        assert len(names) == 3
        assert "Food" in names
        assert "Transport" in names
        assert "Entertainment" in names

    def test_update_category(self, repo, sample_category):
        """Should be able to update an existing category."""
        repo.add(sample_category)

        sample_category.name = "Groceries"
        repo.update(sample_category)

        assert repo.get("Food") is None
        result = repo.get("Groceries")
        assert result is not None
        assert result.name == "Groceries"

    def test_delete_category(self, repo, sample_category):
        """Should be able to delete a category."""
        repo.add(sample_category)
        repo.delete("Food")

        assert repo.get("Food") is None

    def test_delete_nonexistent_raises(self, repo):
        """Deleting a non-existent category should raise CategoryNotFoundError."""
        from expenses_ai_agent.storage.exceptions import CategoryNotFoundError

        with pytest.raises(CategoryNotFoundError):
            repo.delete("NonExistent")


class TestInMemoryExpenseRepository:
    """Tests for the in-memory expense repository."""

    @pytest.fixture
    def repo(self):
        """Create a fresh in-memory expense repository for each test."""
        from expenses_ai_agent.storage.repo import InMemoryExpenseRepository

        return InMemoryExpenseRepository()

    @pytest.fixture
    def sample_expense(self):
        """Create a sample expense for testing."""
        from expenses_ai_agent.storage.models import Currency, Expense

        return Expense(
            amount=Decimal("42.50"),
            currency=Currency.EUR,
            description="Test expense",
        )

    def test_add_expense_assigns_id(self, repo, sample_expense):
        """Adding an expense should assign an auto-incremented ID."""
        assert sample_expense.id is None

        repo.add(sample_expense)

        assert sample_expense.id is not None
        assert sample_expense.id >= 1

    def test_get_expense_by_id(self, repo, sample_expense):
        """Should retrieve expense by ID."""
        repo.add(sample_expense)

        result = repo.get(sample_expense.id)

        assert result is not None
        assert result.amount == Decimal("42.50")

    def test_get_nonexistent_returns_none(self, repo):
        """Getting a non-existent expense should return None."""
        result = repo.get(999)
        assert result is None

    def test_list_all_expenses(self, repo):
        """Should list all expenses."""
        from expenses_ai_agent.storage.models import Currency, Expense

        repo.add(Expense(amount=Decimal("10.00"), currency=Currency.EUR))
        repo.add(Expense(amount=Decimal("20.00"), currency=Currency.USD))

        expenses = repo.list()

        assert len(expenses) == 2

    def test_delete_expense(self, repo, sample_expense):
        """Should be able to delete an expense."""
        repo.add(sample_expense)
        expense_id = sample_expense.id

        repo.delete(expense_id)

        assert repo.get(expense_id) is None

    def test_delete_nonexistent_raises(self, repo):
        """Deleting a non-existent expense should raise ExpenseNotFoundError."""
        from expenses_ai_agent.storage.exceptions import ExpenseNotFoundError

        with pytest.raises(ExpenseNotFoundError):
            repo.delete(999)

    def test_search_by_category(self, repo):
        """Should be able to search expenses by category."""
        from expenses_ai_agent.storage.models import Currency, Expense, ExpenseCategory

        food = ExpenseCategory(id=1, name="Food")
        transport = ExpenseCategory(id=2, name="Transport")

        repo.add(Expense(amount=Decimal("10.00"), currency=Currency.EUR, category=food))
        repo.add(Expense(amount=Decimal("20.00"), currency=Currency.EUR, category=food))
        repo.add(Expense(amount=Decimal("30.00"), currency=Currency.EUR, category=transport))

        food_expenses = repo.search_by_category(food)

        assert len(food_expenses) == 2
        assert all(e.category.name == "Food" for e in food_expenses)


class TestRepositoryAbstractBase:
    """Tests to verify abstract base classes are properly defined."""

    def test_category_repository_is_abstract(self):
        """CategoryRepository should be an abstract base class."""
        from abc import ABC

        from expenses_ai_agent.storage.repo import CategoryRepository

        assert issubclass(CategoryRepository, ABC)

        with pytest.raises(TypeError):
            CategoryRepository()

    def test_expense_repository_is_abstract(self):
        """ExpenseRepository should be an abstract base class."""
        from abc import ABC

        from expenses_ai_agent.storage.repo import ExpenseRepository

        assert issubclass(ExpenseRepository, ABC)

        with pytest.raises(TypeError):
            ExpenseRepository()

    def test_inmemory_repos_inherit_from_abstract(self):
        """In-memory repositories should implement the abstract base classes."""
        from expenses_ai_agent.storage.repo import (
            CategoryRepository,
            ExpenseRepository,
            InMemoryCategoryRepository,
            InMemoryExpenseRepository,
        )

        assert issubclass(InMemoryCategoryRepository, CategoryRepository)
        assert issubclass(InMemoryExpenseRepository, ExpenseRepository)
```


## Implementation Strategy

Work through these steps in order. Each step targets specific tests.

### Step 1: Create the Currency Enum

Start with the `Currency` StrEnum in `storage/models.py`:

**Target tests:** `TestCurrencyEnum` (3 tests)

### Step 2: Create Custom Exceptions

Define `CategoryNotFoundError` and `ExpenseNotFoundError` in `storage/exceptions.py`:

**Target tests:** `TestStorageExceptions` (2 tests)

### Step 3: Create ExpenseCategory Model

Build the `ExpenseCategory` SQLModel entity with `id`, `name`, `__str__`, and `create()`:

**Target tests:** `TestExpenseCategory` (4 tests)

### Step 4: Create Expense Model

Build the `Expense` SQLModel entity with all required fields:

**Target tests:** `TestExpense` (7 tests)

### Step 5: Define Abstract Repository Classes

Create `CategoryRepository` and `ExpenseRepository` abstract base classes:

**Target tests:** `TestRepositoryAbstractBase` (3 tests)

### Step 6: Implement InMemoryCategoryRepository

Build the dict-backed category repository:

**Target tests:** `TestInMemoryCategoryRepository` (6 tests)

### Step 7: Implement InMemoryExpenseRepository

Build the dict-backed expense repository with search capability:

**Target tests:** `TestInMemoryExpenseRepository` (7 tests)


## Helpful Concepts

### Abstract Base Classes

```python
from abc import ABC, abstractmethod

class Repository(ABC):
    @abstractmethod
    def add(self, item) -> None:
        """Subclasses must implement this."""
        ...
```

[Documentation: abc module](https://docs.python.org/3/library/abc.html)

### Dict-Based Storage

```python
class InMemoryStorage:
    def __init__(self):
        self._storage: dict[int, Item] = {}
        self._next_id = 1

    def add(self, item: Item) -> None:
        item.id = self._next_id
        self._storage[item.id] = item
        self._next_id += 1
```


## Validation Checklist

Before moving on, verify:

- [ ] All 26 tests pass: `pytest tests/unit/test_week1.py -v`
- [ ] No linting errors: `ruff check src/`
- [ ] Code is formatted: `ruff format .`


## Debugging Tips

### "ModuleNotFoundError: expenses_ai_agent"

Run `uv pip install -e ".[dev]"` to install the package in editable mode.

### "TypeError: Can't instantiate abstract class"

Your repository is missing one or more abstract method implementations. Check that all `@abstractmethod` methods are implemented.

### "Decimal precision issues"

Use `Decimal("10.50")` not `Decimal(10.50)`. The string form ensures exact precision.


## Step Hints


### Step 1: Currency Enum Hint

Use `StrEnum` from the `enum` module. Each currency needs a name and value:

```python
from enum import StrEnum, verify, UNIQUE

@verify(UNIQUE)
class Currency(StrEnum):
    EUR = "EUR"
    # Add 9 more currencies...
```


### Step 3: ExpenseCategory Hint

Your model needs:
- `id: int | None` with `Field(default=None, primary_key=True)`
- `name: str` with `Field(index=True, unique=True)`
- `__str__` method returning the name
- `create()` classmethod as a factory


### Step 4: Expense Hint

Key fields and their defaults:
- `currency` defaults to `Currency.EUR`
- `date` uses `default_factory` for current UTC time
- `category_id` and `category` create the relationship


### Step 6: InMemoryCategoryRepository Hint

Track categories by name in a dict:

```python
def __init__(self):
    self._categories: dict[str, ExpenseCategory] = {}

def add(self, category: ExpenseCategory) -> None:
    self._categories[category.name] = category
```

---

Your Week 1 foundation is complete when all 26 tests pass.
